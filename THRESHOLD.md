# Retrieval tuning — how the numbers were chosen

Measured against the rebuilt 252-chunk store, cosine metric with normalised
embeddings. Scores are LangChain relevance scores (higher = more relevant).

Final settings: `RETRIEVAL_K = 15`, `RELEVANCE_THRESHOLD = 0.25`,
`SERVICE_CONTENT_BOOST = 0.12`, `SUPPLEMENTARY_K = 5`.

## Prerequisite: the scores had to be made meaningful first

With the original setup (`HuggingFaceEmbeddings` with no normalisation,
Chroma's default L2 metric) LangChain computes relevance as
`1 - distance/sqrt(2)`, which on this data returns **negative** values —
LangChain emits a `UserWarning: Relevance scores must be between 0 and 1`.
No threshold in `[0, 1]` would have meant anything.

Fixed by normalising embeddings and creating the collection with
`hnsw:space=cosine`. Both are in `config.py` and are applied identically by
`ingest_adipven.py` and `retrieval.py` via the shared factory in
`retrieval.get_embeddings()`.

## Measured top-1 score distributions

| Query class | n | min | p25 | median | max |
|---|---|---|---|---|---|
| On-topic (Adipven's content answers it) | 16 | 0.268 | 0.361 | 0.521 | 0.765 |
| Adjacent but **not** covered | 5 | 0.398 | 0.472 | 0.568 | 0.681 |
| Off-topic (nothing to do with IP) | 6 | 0.090 | 0.112 | 0.155 | 0.273 |

## Recall / rejection by threshold

| threshold | on-topic kept | off-topic kept |
|---|---|---|
| 0.20 | 16/16 | 1/6 |
| **0.25** | **16/16** | **1/6** |
| 0.30 | 13/16 | 0/6 |
| 0.40 | 11/16 | 0/6 |

## Why 0.25

The on-topic and off-topic classes **overlap** (on-topic min 0.268 vs
off-topic max 0.273), so no threshold separates them cleanly.

Going to 0.30 buys the last off-topic rejection at the cost of three core
queries returning nothing at all:

- "what is your phone number" (0.288)
- "where is your office located" (0.268)
- "I designed a new bottle cap, how do I stop people copying it" (0.276)

Those score low because the contact chunks are dense label-value blocks
(`**Phone (source: Contacts page):** "+603 …"`) which embed poorly against
a naturally-phrased question — not because they are irrelevant. Inspecting
the full `k=10` for each confirms the correct chunk is retrieved, just with
a low score.

0.25 is therefore the operating point: full recall on on-topic queries,
with the single surviving off-topic case ("recommend a good science fiction
novel", 0.273, which retrieves one staff-bio chunk) left to the grounding
check, which drops any answer the chunks do not support.

The asymmetry is deliberate and matches the fail-closed policy: a false
refusal on a contact question is a guaranteed lost enquiry, while a weak
off-topic chunk still has to survive a downstream check that verifies
reported source IDs and rejects unsupported content.

## What the threshold does NOT defend against

**Adjacent-but-uncovered queries score higher than many genuine on-topic
ones.** Examples, with the top chunk retrieved:

| Query (Adipven's content does not answer this) | score | top chunk |
|---|---|---|
| how many years does a Malaysian patent last | 0.681 | `malaysia_patent_found_to_invalid` |
| statutory requirements for patentability in Malaysia | 0.596 | `malaysia_patent_found_to_invalid` |
| can I patent computer software in Malaysia | 0.568 | `malaysia_how_patent_damages_are_accessed` |
| deadline for PCT national phase entry in Malaysia | 0.545 | `sst_announcements` |

These are semantically about patents, and the store is full of patent
content, so the embedding cannot tell them apart from answerable questions.
**No threshold fixes this** — raising it high enough to reject them would
reject most real queries first.

This is the highest-risk case in the whole system, and the defence is not
retrieval. It is:

1. the `reasoning` field, which forces an explicit per-chunk check of
   whether the retrieved text actually answers the question asked;
2. the grounding check in `grounding.py`, which verifies reported
   `source_ids` against what was really retrieved and fails closed on any
   answer with factual content but no verified support.

## k = 15, and the corpus-imbalance corrections

Separately from the threshold, two measurements drove the rest of the
retrieval config.

**k.** On a 10-query probe checking whether the chunk that actually answers
the question is retrieved at all:

| k | recall |
|---|---|
| 4 | 6/10 |
| 10 | 6/10 |
| **15** | **8/10** |
| 30 | 8/10 |

`k=10` cut off at precisely the wrong point: the licensing service page sat
at rank #11 for "does Adipven handle IP licensing?" and Ramakrishna
Damodharan's profile at #12 for "who is the managing director?". Both
produced confident, correct, entirely unnecessary refusals. Raising k does
not weaken the off-topic gate, which keys on the top-1 raw score.

**Corpus imbalance.** Case studies are 151 of 252 chunks (60%); service
pages are 22. Case studies are long narrative prose and out-score the short
service descriptions on nearly any customer-phrased question. Asked "do you
handle trademark oppositions?", 14 of 15 retrieved chunks were litigation
summaries and the agent refused — while the About Us services list, which
answers it directly, sat far down the ranking.

Two corrections, both applied only *after* the off-topic gate passes:

- a supplementary filtered search (`SUPPLEMENTARY_K=5`) restricted to the
  firm's own descriptions, so they are always candidates rather than only
  re-scored when they happen to appear;
- a `+0.12` score boost on those same section types.

Measured effect on a 16-query answerable set: false refusals went from 3/16
to 0/16, with no change to off-topic rejection (5/6 before and after) and no
grounding leaks (0/12 on the adjacent-uncovered probe).

## Sample size — read these numbers with this caveat attached

Every table above is fitted to **one corpus snapshot and 27 hand-written
queries** (16 on-topic, 6 off-topic, 5 adjacent-uncovered), plus a 16-query
answerable set and a 12-query grounding probe. Each knob is individually
justified by a measurement, but the numbers are precise in a way the
underlying evidence is not. They should not be read as stable constants.

In particular the on-topic and off-topic classes **overlap**: on-topic min
0.268, off-topic max 0.273. 0.25 sits deliberately *below* that seam rather
than inside it — the ordering of those two figures is a property of 22
queries, and could invert on the 23rd. That is the reason for the margin,
and the reason nudging the threshold up to "tighten" things is a bad idea
without re-measuring: the three queries it would kill first are contact
questions.

The practical consequence is about where the safety boundary actually sits.
**Retrieval reduces noise; it is not the guarantee.** The off-topic gate is
load-bearing for genuinely unrelated queries, which do return nothing. But
for the dangerous case — on-topic, plausibly-retrieved, not actually
covered — retrieval offers no protection at all, as the table above shows.
What stands between that case and an ungrounded claim about IP protection
is only:

1. the model's own judgement, recorded in `reasoning`; and
2. `grounding.py`, which verifies reported `source_ids` against what was
   really retrieved and fails closed.

Those two are the safety boundary. Bugs there matter far more than any
number on this page — the pricing gate in `grounding.py` runs before
everything else and replaces the response outright, so a false positive
there silently converts an answerable question into a refusal regardless of
how well retrieval performed.

Re-measure everything here whenever the content store changes materially.

## Embedding backend switch: torch -> onnx (2026-08-10)

The Render free-tier deploy timed out waiting on `/health`. Local RSS
measurement of the torch-backed service (`config.EMBED_BACKEND = "torch"`,
`langchain_huggingface.HuggingFaceEmbeddings`) was ~569MB — over the
512MB ceiling — so the store was rebuilt on `config.EMBED_BACKEND =
"onnx"` (`chromadb.utils.embedding_functions.ONNXMiniLM_L6_V2`, no torch)
to fit the free tier without paying for Starter.

This encoder swap invalidates every existing vector (`ingest_adipven.py`
was re-run in full) and is exactly the kind of change this file's opening
line warns about, so everything above was re-measured against the new
store before trusting it:

| check | torch (previous) | onnx (this store) |
|---|---|---|
| on-topic top-1 score, n=16 | min 0.268, max 0.765 | min 0.268, max 0.765 |
| off-topic top-1 score, n=6 | min 0.090, max 0.273 | min 0.090, max 0.273 |
| recall@k targets, n=10 | 8/10 at k=15 | 8/10 at k=15, identical ranks |
| pricing gate, n=18 | 18/18 | 18/18 |
| grounding discipline (live), n=8 | — | 8/8 refused, 0 leaks |
| false refusals (live), n=8 | — | 0/8 |

Scores matched the torch numbers almost to the decimal — the ONNX export
tracks the original PyTorch weights closely enough that **no retrieval
constant needed retuning** (`RETRIEVAL_K`, `RELEVANCE_THRESHOLD`,
`SERVICE_CONTENT_BOOST`, `SUPPLEMENTARY_K` are all unchanged). This
outcome isn't guaranteed by the model card alone — it's why the re-measure
happened before trusting it, not after.

Reproduce with `python eval.py --live`.

### Memory result

A `pip freeze`-based local measurement was misleading here: `torch` and
`transformers` were still installed in the dev environment (kept for the
`"torch"` fallback branch and earlier work), and `langchain_core`'s
`language_models/base.py` does a module-level
`try: from transformers import GPT2TokenizerFast; except ImportError: ...`
— present locally, it silently imports `transformers` (and `torch`
behind it) the first time `agent.get_chain()` runs, even though nothing
in this codebase calls the function that import exists for
(`get_token_ids()`/`get_num_tokens()` are never used). That produced a
false reading of ~496MB after a few queries.

The real number came from building `requirements.txt` into an isolated
venv containing *only* the pinned packages (confirmed via `pip list` that
torch/transformers/sentence-transformers were genuinely absent) and
running the actual server there:

| | idle (post-warmup) | after 17 queries |
|---|---|---|
| torch backend (polluted local env) | — | ~569MB |
| onnx backend, clean venv | ~257MB | ~312MB (stable, no growth) |

**~312MB against a 512MB ceiling — fits, with roughly 200MB headroom.**
This also caught a real bug: `requirements.txt` still listed
`sentence-transformers` and `langchain-huggingface` after the code switched
to the onnx backend, which would have shipped `torch` to Render regardless
of `config.EMBED_BACKEND`. Fixed — see `requirements.txt`'s own comment.

### What this does not explain

The original Render timeout log showed warmup starting and then nothing
further — no crash, no `ready (N chunks)` line, just silence until Render's
port scanner gave up. That is consistent with an OOM kill, but was never
directly confirmed (no explicit "out of memory" line appeared in what was
pasted), and a slow/throttled network path to whichever host serves the
embedding model on Render's free CPU could produce the identical symptom.
The onnx swap also changes that path: ONNXMiniLM_L6_V2 downloads one
~79MB file over a single HTTPS connection to Chroma's S3 bucket, versus
HuggingFaceEmbeddings's roughly dozen small HEAD requests to the HF Hub
API — plausibly faster and more failure-tolerant on a constrained
instance, but not measured directly against Render's actual network from
here. If the free-tier deploy times out again after this change, that
network-path difference — not memory — is the next thing to check.

