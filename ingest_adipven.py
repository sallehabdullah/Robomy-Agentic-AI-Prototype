"""
Ingestion — Adipven markdown -> Chroma vector store
====================================================
Offline pipeline. Run once, or re-run whenever content changes. Does NOT
run inside the agent's runtime loop; it produces a persisted vector store
directory that the agent's retriever loads read-only.

Pipeline stages
---------------
1. parse    — split each .md into sections. A section is either a "### "
              subsection, or a "## " section that has body text but no
              "### " children. The latter case is why contact details,
              credentials, testimonials, SLAs and company background were
              previously absent from the store entirely: the old parser
              only emitted "### " sections, so ~32k chars of source text
              (12.8%) was silently dropped.
2. dedupe   — adipven-content-store.md restates most of the other files,
              usually in condensed form. Same-topic sections are collapsed
              to whichever version carries more text.
3. subchunk — the embedding model truncates at 256 tokens, so anything
              longer is only partially represented in its own vector.
              Sections are split on paragraph boundaries to fit, with the
              section title repeated on each part so every chunk stands
              alone when retrieved.
4. embed    — local sentence-transformers encoder; no API key, no cost.

L1 code only. No chat model is involved here — embeddings are a separate,
non-generative model from the one in the agent.

    python ingest_adipven.py
"""

from __future__ import annotations

import argparse
import difflib
import logging
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

from langchain_core.documents import Document

import config

log = logging.getLogger("ingest")


# --- what to read ----------------------------------------------------------

# 00-index.md is a site-crawl manifest: its sections are markdown tables of
# page URLs with almost no prose. They match on service names and carry
# nothing answerable, so they crowd the top-k without contributing.
EXCLUDED_FILES = {"00-index.md"}

# "## Extraction Notes" is internal QA commentary, not customer-facing.
EXCLUDE_H2_CONTAINING = ("extraction notes",)

# Section types dropped from the index entirely. Empty on master; this
# branch excludes case studies to test the agent without them. Filtering by
# type rather than by filename is deliberate: case-study content lives in
# BOTH 03-case-studies.md and adipven-content-store.md's "## Clients & Case
# Studies" block, and the latter's condensed restatements currently lose
# dedupe to the former — excluding only the file would swap long case
# studies for short ones, not remove them. 144 of 243 chunks are case_study.
EXCLUDED_SECTION_TYPES = {"case_study"}

SOURCE_RE = re.compile(r"\*\*Source(?:\(s\))?:\*\*\s*(\S+)")
SOURCE_LINE_RE = re.compile(r"^\*\*Source(?:\(s\))?:\*\*.*$\n?", re.MULTILINE)
DATE_RE = re.compile(r"^\*\*Date:\*\*\s*(.+)$", re.MULTILINE)

# H2 heading (lowercased) -> section type. Prefix match, so
# "People — Staff feature articles (see also ...)" resolves to "people".
SECTION_TYPE_BY_H2 = (
    ("contact & identifying information", "contact"),
    ("services / products", "service"),
    ("pricing & commercial terms", "pricing"),
    ("credentials, certifications & compliance", "credentials"),
    ("process / how it works", "process"),
    ("clients & case studies", "case_study"),
    ("news & announcements", "announcement"),
    ("company background", "background"),
    ("testimonials", "testimonial"),
    ("people", "people"),
)

SECTION_TYPE_BY_FILE = {
    "02-people.md": "people",
    "03-case-studies.md": "case_study",
    "04-company-contact.md": "contact",
}

# Case studies and announcements describe past events. They are legitimate
# content, but a 2017 announcement stating an office address is not a
# statement of the *current* address — and the model cannot tell the
# difference from the text alone. Marking them lets the agent date-qualify
# such claims instead of presenting them as current fact.
HISTORICAL_TYPES = {"case_study", "announcement"}

# Sections that carry current, firm-level fact. Used to break near-ties in
# retrieval ordering so a stale announcement does not outrank the Contacts
# page on a contact question.
AUTHORITATIVE_TYPES = {
    "contact", "credentials", "pricing", "process", "service",
    "people", "background",
}


@dataclass
class Section:
    """One parsed unit of source text, before sub-chunking."""
    title: str
    body: str
    source_file: str
    h2: str
    section_type: str
    source_url: str = ""
    stated_date: str = ""
    is_orphan_h2: bool = False
    merged_from: list[str] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return slugify(self.title)

    @property
    def is_historical(self) -> bool:
        return self.section_type in HISTORICAL_TYPES or bool(self.stated_date)

    @property
    def authority(self) -> int:
        if self.section_type in AUTHORITATIVE_TYPES:
            return 2
        if self.section_type == "provenance":
            return 0
        return 1


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def normalise_title(title: str) -> str:
    """Strip inline extraction annotations before comparing titles.

    Several headings carry a trailing '[CONFLICTING: ...]' or
    '[UNCERTAIN: ...]' note, which changes the slug and would otherwise
    hide a duplicate from the deduper.
    """
    t = re.sub(r"\[(?:CONFLICTING|UNCERTAIN|ILLEGIBLE|TRUNCATED)[^\]]*\]", "", title)
    t = re.sub(r"\((?:title per|no biography)[^)]*\)", "", t, flags=re.I)
    return slugify(t)


def section_type_for(h2: str, source_file: str) -> str:
    h2l = h2.strip().lower()
    for prefix, kind in SECTION_TYPE_BY_H2:
        if h2l.startswith(prefix):
            return kind
    if not h2l:
        return "provenance"
    return SECTION_TYPE_BY_FILE.get(source_file, "general")


def _excluded_h2(h2: str) -> bool:
    return any(x in h2.strip().lower() for x in EXCLUDE_H2_CONTAINING)


# --- stage 1: parse --------------------------------------------------------

def parse_file(path: Path) -> list[Section]:
    """Split one markdown file into sections.

    Emits a section for every '### ' subsection, and additionally for any
    '## ' section that has body text of its own but no '### ' children
    (e.g. '## Contact & Identifying Information'). Text before the first
    '## ' is emitted as a 'provenance' section.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: list[Section] = []

    h2 = ""
    h3: str | None = None
    buf: list[str] = []
    h2_had_child = False

    def make(title: str, is_orphan: bool) -> None:
        body = "\n".join(buf).strip()
        if not body or _excluded_h2(h2):
            return
        m = SOURCE_RE.search(body)
        d = DATE_RE.search(body)
        # The **Source(s):** line is provenance boilerplate (one or two
        # URLs), already captured above into metadata.source_url — leaving
        # it in the embedded text just dilutes the chunk's vector with
        # tokens that carry no retrievable meaning. Matters most on short
        # bio-style sections, where it can be a fifth of the chunk's
        # content. See PROJECT_LOG.md 2026-08-13.
        body = SOURCE_LINE_RE.sub("", body).strip()
        sections.append(Section(
            title=title,
            body=body,
            source_file=path.name,
            h2=h2,
            section_type=section_type_for(h2, path.name),
            source_url=m.group(1).rstrip(";") if m else "",
            stated_date=d.group(1).strip() if d else "",
            is_orphan_h2=is_orphan,
        ))

    def flush() -> None:
        if h3 is not None:
            make(h3, is_orphan=False)
        else:
            # body sitting directly under a '## ' (or the file preamble)
            title = h2 if h2 else f"{path.stem} — document provenance"
            make(title, is_orphan=True)

    for line in lines:
        if line.startswith("### "):
            flush()
            h3 = line[4:].strip()
            h2_had_child = True
            buf = []
        elif line.startswith("## "):
            flush()
            h2 = line[3:].strip()
            h3 = None
            h2_had_child = False
            buf = []
        elif line.startswith("# "):
            flush()
            h2 = ""
            h3 = None
            buf = []
        else:
            buf.append(line)
    flush()
    return sections


# --- stage 2: dedupe -------------------------------------------------------

# Section types where the two extractions are complementary rather than
# nested: 04-company-contact.md and adipven-content-store.md were extracted
# from overlapping page sets independently, so each caught firm-level facts
# the other missed (founding date, "team of nine practitioners", the
# Utara/Utama address conflict). For these, unique paragraphs from the
# shorter version are carried across instead of discarded.
#
# Case studies and announcements are excluded: there the content store holds
# a condensed restatement of the same article, so a union would just append
# a summary of text already present.
UNION_ON_MERGE = {
    "contact", "credentials", "background", "pricing",
    "process", "service", "people", "testimonial",
}

# Paragraph similarity above which a paragraph counts as already present.
PARA_DUP_RATIO = 0.75


def _norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _union_bodies(kept: str, other: str, other_file: str) -> str:
    """Append paragraphs from `other` that `kept` does not already contain."""
    kept_paras = [_norm_ws(p) for p in re.split(r"\n\s*\n", kept) if p.strip()]
    extra: list[str] = []

    for para in re.split(r"\n\s*\n", other):
        para = para.strip()
        if not para:
            continue
        pn = _norm_ws(para)
        if any(pn in k or k in pn for k in kept_paras):
            continue
        best = max((difflib.SequenceMatcher(None, pn, k).ratio()
                    for k in kept_paras), default=0.0)
        if best < PARA_DUP_RATIO:
            extra.append(para)

    if not extra:
        return kept
    return (f"{kept}\n\nAdditional detail from a second extraction of the same "
            f"pages ({other_file}):\n\n" + "\n\n".join(extra))


def _same_topic(a: str, b: str) -> bool:
    """Do two normalised titles refer to the same topic?

    Exact match catches most of it. Prefix match catches singular/plural
    drift ('sst_announcement' vs 'sst_announcements') and one file
    appending a gloss to the heading. The ratio check catches source-side
    typos between the two extractions, e.g. 'damages_are_accessed_by_court'
    vs 'damages_are_assessed_by_court'.
    """
    if a == b:
        return True
    if a.startswith(b) or b.startswith(a):
        return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.85


def dedupe_sections(sections: list[Section]) -> list[Section]:
    """Collapse same-topic sections that appear in more than one file.

    Keeps whichever version carries more text — in practice this favours
    03-case-studies.md over the content store's condensed summaries, and
    01-services.md over its near-identical service copy.
    """
    kept: list[Section] = []
    dropped = 0

    # longest first so the survivor is chosen deterministically
    for sec in sorted(sections, key=lambda s: (-len(s.body), s.source_file, s.title)):
        norm = normalise_title(sec.title)
        match = None
        for k in kept:
            # only dedupe across files, and only within the same section type
            if k.source_file == sec.source_file:
                continue
            if k.section_type != sec.section_type:
                continue
            if _same_topic(norm, normalise_title(k.title)):
                match = k
                break
        if match is None:
            kept.append(sec)
            continue

        match.merged_from.append(f"{sec.source_file}::{sec.slug}")
        dropped += 1
        before = len(match.body)
        if match.section_type in UNION_ON_MERGE:
            match.body = _union_bodies(match.body, sec.body, sec.source_file)
        gained = len(match.body) - before
        log.debug("dedupe: %s::%s -> %s::%s (%d vs %d chars, +%d carried across)",
                  sec.source_file, sec.slug, match.source_file, match.slug,
                  len(sec.body), before, gained)

    log.info("dedupe: %d sections -> %d (%d duplicates collapsed)",
             len(sections), len(kept), dropped)
    return kept


# --- stage 3: sub-chunk ----------------------------------------------------

_tokenizer = None


def _token_len(text: str) -> int:
    """Token count under whichever tokenizer config.EMBED_BACKEND actually
    uses at query/embed time — this is an offline, one-time ingestion step,
    so pulling in `transformers` here costs nothing at runtime regardless
    of backend; it's not on the Render deploy's import path.

    Matching tokenizers matters less than it might look: both the ONNX and
    torch paths enable truncation at 256 rather than raising, so a
    mismatch would only make a chunk a few tokens tighter or looser than
    intended, never a hard failure. Kept consistent anyway since it's easy.
    """
    global _tokenizer
    if _tokenizer is None:
        if config.EMBED_BACKEND == "onnx":
            import retrieval
            emb = retrieval.get_embeddings()
            # The tokenizer is a lazy cached_property that reads
            # tokenizer.json from the on-disk model download, but only
            # __call__ triggers that download — accessing .tokenizer
            # directly, before anything has been embedded, hits a
            # FileNotFoundError. One throwaway call forces it first.
            emb.embed_query("warmup")
            _tokenizer = emb._fn.tokenizer
        else:
            from transformers import AutoTokenizer
            _tokenizer = AutoTokenizer.from_pretrained(config.EMBED_MODEL)
    if config.EMBED_BACKEND == "onnx":
        # tokenizers.Tokenizer.encode; padding is enabled on this instance
        # (see retrieval._OnnxMiniLMEmbeddings), so raw .ids includes pad —
        # attention_mask marks the real (non-pad) tokens.
        enc = _tokenizer.encode(text)
        return int(sum(enc.attention_mask))
    return len(_tokenizer.encode(text, add_special_tokens=True))


def _split_paragraph(para: str, budget: int) -> list[str]:
    """Last resort: split a single over-long paragraph on sentence ends."""
    sentences = re.split(r"(?<=[.!?])\s+", para)
    out, cur = [], ""
    for s in sentences:
        cand = f"{cur} {s}".strip()
        if cur and _token_len(cand) > budget:
            out.append(cur)
            cur = s
        else:
            cur = cand
    if cur:
        out.append(cur)
    return out


def subchunk(sec: Section, budget: int) -> list[str]:
    """Split a section body into parts that fit the encoder window.

    Splits only on paragraph boundaries where possible, so a fact and its
    qualifier stay together. The title is prepended to every part by the
    caller, and counts against the budget here.
    """
    title_cost = _token_len(sec.title) + 4
    room = max(budget - title_cost, 64)

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", sec.body) if p.strip()]
    parts: list[str] = []
    cur = ""

    for para in paragraphs:
        if _token_len(para) > room:
            if cur:
                parts.append(cur)
                cur = ""
            parts.extend(_split_paragraph(para, room))
            continue
        cand = f"{cur}\n\n{para}".strip()
        if cur and _token_len(cand) > room:
            parts.append(cur)
            cur = para
        else:
            cur = cand
    if cur:
        parts.append(cur)
    return parts or [sec.body]


def sections_to_documents(sections: list[Section]) -> list[Document]:
    docs: list[Document] = []
    for sec in sections:
        parts = subchunk(sec, config.CHUNK_TOKEN_BUDGET)
        multi = len(parts) > 1
        for i, part in enumerate(parts, start=1):
            base = f"{Path(sec.source_file).stem}__{sec.slug}"
            chunk_id = f"{base}__p{i}" if multi else base
            docs.append(Document(
                page_content=f"{sec.title}\n\n{part}",
                metadata={
                    "id": chunk_id,
                    "title": sec.title,
                    "source_file": sec.source_file,
                    "source_url": sec.source_url,
                    "section": sec.h2,
                    "section_type": sec.section_type,
                    "is_historical": sec.is_historical,
                    "stated_date": sec.stated_date,
                    "authority": sec.authority,
                    "part": i,
                    "part_count": len(parts),
                    "merged_from": ",".join(sec.merged_from),
                },
            ))
    return docs


# --- driver ----------------------------------------------------------------

def build_documents() -> list[Document]:
    if not config.MARKDOWN_DIR.exists():
        raise SystemExit(f"Content folder not found: {config.MARKDOWN_DIR}")

    sections: list[Section] = []
    for path in sorted(config.MARKDOWN_DIR.glob("*.md")):
        if path.name in EXCLUDED_FILES:
            log.info("  %-28s skipped (excluded)", path.name)
            continue
        file_sections = parse_file(path)
        orphans = sum(1 for s in file_sections if s.is_orphan_h2)
        log.info("  %-28s %3d sections (%d recovered from '##'-only text)",
                 path.name, len(file_sections), orphans)
        sections.extend(file_sections)

    if not sections:
        raise SystemExit("No sections parsed — check the markdown structure.")

    # Before dedupe, not after: dedupe only ever matches within a section
    # type, so dropping a whole type here cannot change any other type's
    # merge outcome. Doing it afterwards would let the long versions absorb
    # the short ones first and then discard the merged result.
    if EXCLUDED_SECTION_TYPES:
        before = len(sections)
        sections = [s for s in sections if s.section_type not in EXCLUDED_SECTION_TYPES]
        log.info("excluded %d sections of type %s", before - len(sections),
                 ", ".join(sorted(EXCLUDED_SECTION_TYPES)))
        if not sections:
            raise SystemExit("Every section was excluded — check EXCLUDED_SECTION_TYPES.")

    sections = dedupe_sections(sections)
    docs = sections_to_documents(sections)

    ids = [d.metadata["id"] for d in docs]
    if len(set(ids)) != len(ids):
        dupes = {i for i in ids if ids.count(i) > 1}
        raise SystemExit(f"Duplicate chunk IDs generated: {sorted(dupes)}")

    return docs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="parse and report, but do not touch the vector store")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
        stream=sys.stdout,
    )

    log.info("Parsing %s", config.MARKDOWN_DIR)
    docs = build_documents()

    over = [d for d in docs if _token_len(d.page_content) > config.EMBED_MAX_TOKENS]
    log.info("Built %d chunks; %d exceed the %d-token embedding window",
             len(docs), len(over), config.EMBED_MAX_TOKENS)
    for d in over[:5]:
        log.warning("  oversized: %s (%d tok)", d.metadata["id"],
                    _token_len(d.page_content))

    by_type: dict[str, int] = {}
    for d in docs:
        by_type[d.metadata["section_type"]] = by_type.get(d.metadata["section_type"], 0) + 1
    log.info("Chunks by section type: %s",
             ", ".join(f"{k}={v}" for k, v in sorted(by_type.items())))

    if args.dry_run:
        log.info("Dry run — vector store untouched.")
        return

    from langchain_chroma import Chroma

    import retrieval  # shared embedding factory — must match the runtime side

    persist = Path(config.PERSIST_DIR)
    if persist.exists():
        log.info("Removing existing store at %s", persist)
        shutil.rmtree(persist)

    log.info("Embedding with %s (normalised=%s, metric=%s) ...",
             config.EMBED_MODEL, config.EMBED_NORMALIZE,
             config.CHROMA_COLLECTION_METADATA["hnsw:space"])
    Chroma.from_documents(
        documents=docs,
        embedding=retrieval.get_embeddings(),
        persist_directory=config.PERSIST_DIR,
        collection_metadata=config.CHROMA_COLLECTION_METADATA,
    )
    log.info("Persisted %d chunks to %s", len(docs), config.PERSIST_DIR)


if __name__ == "__main__":
    main()
