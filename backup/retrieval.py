"""
Retrieval — Chroma-backed lookup with relevance filtering.

Everything here is L1 code. The model never runs a search; it can only ask
for one, and this module decides what (if anything) comes back.

Two properties the rest of the system depends on:

* `RetrievalResult.chunk_ids` is the ground truth for what the model was
  actually shown. The grounding check intersects the model's self-reported
  `source_ids` against this set — a reported ID that isn't in here is a
  fabrication, not a citation.
* Chunks scoring below `RELEVANCE_THRESHOLD` are dropped before the model
  sees them. `similarity_search` alone always returns k results, so an
  off-topic query would otherwise come back with the k least-bad matches
  and look like successful retrieval.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import config

log = logging.getLogger(__name__)


# The encoder is loaded from a local cache, so Hugging Face's
# "unauthenticated requests to the HF Hub" notice and its weight-loading
# progress bar are pure noise on every run.
#
# This has to happen in two stages. The env vars must be set BEFORE the
# libraries are imported, but the logger levels must be set AFTER — the
# libraries configure their own loggers at import time and will overwrite
# anything set beforehand. Setting the level on the parent logger is not
# enough either, since the child has an explicit level of its own.
_HF_LOGGERS = (
    "huggingface_hub",
    "huggingface_hub.utils._http",
    "transformers",
    "transformers.modeling_utils",
    "sentence_transformers",
    "sentence_transformers.SentenceTransformer",
)


def _quiet_hf_env() -> None:
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def _quiet_hf_loggers() -> None:
    for name in _HF_LOGGERS:
        lg = logging.getLogger(name)
        lg.setLevel(logging.ERROR)
        # huggingface_hub attaches its own handler, so the record would
        # print once from that handler and once more via the root logger.
        lg.propagate = False


class VectorStoreUnavailable(RuntimeError):
    """The persisted Chroma store is missing or unreadable."""


@lru_cache(maxsize=1)
def get_embeddings():
    """Build the embedding function. Cached — loading the model is slow.

    `normalize_embeddings=True` is required for the cosine collection
    metric to behave: without it, Chroma's L2 distances are unbounded and
    LangChain's relevance score can fall outside [0, 1], which makes any
    threshold meaningless (it will also emit a warning to that effect).
    """
    _quiet_hf_env()
    from langchain_huggingface import HuggingFaceEmbeddings
    _quiet_hf_loggers()

    log.debug("loading embedding model %s", config.EMBED_MODEL)
    return HuggingFaceEmbeddings(
        model_name=config.EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": config.EMBED_NORMALIZE},
    )


@lru_cache(maxsize=1)
def get_vectorstore():
    """Open the persisted store read-only. Cached."""
    from langchain_chroma import Chroma

    persist = Path(config.PERSIST_DIR)
    if not persist.exists():
        raise VectorStoreUnavailable(
            f"No vector store at {persist}.\n"
            f"Build it first:  python ingest_adipven.py"
        )
    try:
        store = Chroma(
            persist_directory=config.PERSIST_DIR,
            embedding_function=get_embeddings(),
            collection_metadata=config.CHROMA_COLLECTION_METADATA,
        )
        count = store._collection.count()
    except Exception as exc:  # noqa: BLE001 - surfaced to the user verbatim
        raise VectorStoreUnavailable(
            f"Could not open the vector store at {persist}: {exc}\n"
            f"If it is corrupt, rebuild with:  python ingest_adipven.py"
        ) from exc

    if count == 0:
        raise VectorStoreUnavailable(
            f"Vector store at {persist} is empty. Rebuild with:  "
            f"python ingest_adipven.py"
        )
    log.debug("vector store open: %d chunks", count)
    return store


def warmup() -> int:
    """Load the encoder and open the store up front.

    Both are cached, so calling this at startup moves ~30 seconds of model
    loading off the first question and into a point where the user expects
    to wait. The throwaway embed_query matters: constructing the encoder
    does not fully materialise it, and without this the first real query
    still pays part of the cost.

    Returns the number of chunks in the store.
    """
    store = get_vectorstore()
    get_embeddings().embed_query("warmup")
    return store._collection.count()


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    score: float
    title: str
    section_type: str
    is_historical: bool
    stated_date: str
    authority: int
    source_url: str

    @classmethod
    def from_document(cls, doc, score: float) -> "Chunk":
        m = doc.metadata
        return cls(
            id=m.get("id", "?"),
            text=doc.page_content,
            score=score,
            title=m.get("title", ""),
            section_type=m.get("section_type", "general"),
            is_historical=bool(m.get("is_historical", False)),
            stated_date=m.get("stated_date", "") or "",
            authority=int(m.get("authority", 1)),
            source_url=m.get("source_url", "") or "",
        )


@dataclass
class RetrievalResult:
    query: str
    chunks: list[Chunk] = field(default_factory=list)
    considered: int = 0
    dropped_below_threshold: int = 0
    best_score: float | None = None
    #: best raw (pre-boost) score seen — this is what the off-topic gate uses
    best_raw_score: float | None = None

    @property
    def chunk_ids(self) -> set[str]:
        """The IDs actually shown to the model. Ground truth for grounding."""
        return {c.id for c in self.chunks}

    @property
    def is_empty(self) -> bool:
        return not self.chunks


def retrieve(
    query: str | list[str],
    k: int | None = None,
    threshold: float | None = None,
) -> RetrievalResult:
    """Search the store and drop anything below the relevance threshold.

    `query` may be a list. A clarification reply like "the shape of it, how
    it looks" is too thin to retrieve on alone, and concatenating it onto
    the original question just dilutes both — so the caller passes both and
    the results are unioned on best score per chunk.

    Two stages:

    1. Raw similarity decides whether the query is on-topic at all. If no
       chunk clears the threshold on its raw score, the result is empty and
       the caller fails closed. This is the off-topic gate.
    2. Only once that gate passes, correct for corpus imbalance — case
       studies are 60% of the store and out-score the firm's own service
       pages on customer-phrased questions. Two corrections: a supplementary
       filtered search that guarantees service/contact content is in the
       candidate pool, and a score boost that lifts it above case studies.

    Ordering the stages this way means neither correction can rescue an
    off-topic query: they only run after the query has already proved
    on-topic on raw scores alone.
    """
    k = k if k is not None else config.RETRIEVAL_K
    threshold = threshold if threshold is not None else config.RELEVANCE_THRESHOLD
    queries = [query] if isinstance(query, str) else [q for q in query if q.strip()]
    if not queries:
        return RetrievalResult(query="", considered=0)

    store = get_vectorstore()
    best: dict[str, tuple] = {}
    for q in queries:
        try:
            scored = store.similarity_search_with_relevance_scores(q, k=k)
        except Exception as exc:  # noqa: BLE001
            raise VectorStoreUnavailable(f"Retrieval failed: {exc}") from exc
        for doc, s in scored:
            cid = doc.metadata.get("id", "?")
            if cid not in best or s > best[cid][1]:
                best[cid] = (doc, s)

    scored = list(best.values())
    best_raw = max((s for _, s in scored), default=None)

    # Stage 1 — off-topic gate, on raw scores only.
    if best_raw is None or best_raw < threshold:
        return RetrievalResult(
            query=" | ".join(queries),
            chunks=[],
            considered=len(scored),
            dropped_below_threshold=len(scored),
            best_score=best_raw,
            best_raw_score=best_raw,
        )

    # Stage 2 — the query is on-topic, so correct for corpus imbalance.
    # 2a: make sure the firm's own service/contact descriptions are in the
    # candidate pool at all, not just re-scored once they happen to appear.
    for q in queries:
        try:
            extra = store.similarity_search_with_relevance_scores(
                q,
                k=config.SUPPLEMENTARY_K,
                filter={"section_type": {"$in": config.FIRM_DESCRIPTION_TYPES}},
            )
        except Exception as exc:  # noqa: BLE001 — supplementary only, never fatal
            log.debug("supplementary retrieval skipped: %s", exc)
            break
        for doc, s in extra:
            cid = doc.metadata.get("id", "?")
            if cid not in best or s > best[cid][1]:
                best[cid] = (doc, s)

    scored = list(best.values())

    # 2b: weight the firm's own descriptions above case studies.
    boosted = []
    for doc, s in scored:
        if doc.metadata.get("section_type") in config.BOOSTED_SECTION_TYPES:
            s = min(s + config.SERVICE_CONTENT_BOOST, 1.0)
        boosted.append((doc, s))

    kept = [Chunk.from_document(d, s) for d, s in boosted if s >= threshold]

    # Primary ordering is relevance, bucketed into tie bands. Within a band,
    # authoritative (current, firm-level) chunks sort above historical ones,
    # so a 2017 announcement does not outrank the Contacts page on a contact
    # question by a 0.006 margin.
    #
    # This is presentation order only. Every surviving chunk still reaches
    # the model, and the substantive defence against stale content is the
    # HISTORICAL label applied in format_context() — not this sort.
    band = config.SCORE_TIE_BAND
    kept.sort(key=lambda c: (-round(c.score / band), -c.authority, -c.score))

    result = RetrievalResult(
        query=" | ".join(queries),
        chunks=kept,
        considered=len(scored),
        dropped_below_threshold=len(scored) - len(kept),
        best_score=max((c.score for c in kept), default=best_raw),
        best_raw_score=best_raw,
    )
    log.debug("retrieve(%s): %d considered, %d kept, best_raw=%.3f",
              queries, result.considered, len(kept), best_raw)
    return result


def format_context(result: RetrievalResult) -> str:
    """Render retrieved chunks for the prompt.

    Every chunk is labelled with its ID and provenance. The historical
    marker is applied in code rather than left to the model to infer: a
    2017 announcement reads exactly like current fact otherwise.
    """
    if result.is_empty:
        return "NO RELEVANT CONTENT FOUND."

    blocks = []
    for c in result.chunks:
        tags = [f"section={c.section_type}"]
        if c.is_historical:
            tags.append("HISTORICAL — describes a past event, not necessarily "
                        "current; state the date when using this")
        if c.stated_date:
            tags.append(f"date={c.stated_date}")
        blocks.append(f"[{c.id}] ({'; '.join(tags)})\n{c.text}")
    return "\n\n---\n\n".join(blocks)
