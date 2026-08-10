"""
Shared configuration for the Adipven agent.

Single source of truth for anything both the offline ingestion pipeline
(ingest_adipven.py) and the runtime agent need to agree on. The embedding
model and persist directory in particular MUST match between the two —
query vectors and document vectors have to come from the same encoder or
similarity search is meaningless.
"""

from pathlib import Path

# --- paths -----------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
MARKDOWN_DIR = PROJECT_ROOT / "adipven_content"
PERSIST_DIR = str(PROJECT_ROOT / "adipven_chroma_db")


# --- embeddings ------------------------------------------------------------
# Local, no API key, no per-call cost. Long-term target is on-device
# inference on a Jetson Orin, so this stays local.
#
# DO NOT change without re-running ingestion. Changing the encoder, OR the
# backend that runs it, invalidates every vector already in PERSIST_DIR —
# query and document vectors must come from the same numbers or cosine
# similarity is comparing apples to noise.
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Which implementation actually runs the model. Both encode the same
# all-MiniLM-L6-v2 weights, so results should be close, but NOT bit
# identical — different runtimes, so re-ingest and re-measure THRESHOLD.md
# after switching.
#
#   "torch" — langchain_huggingface.HuggingFaceEmbeddings. Pulls in torch +
#             sentence-transformers. Measured local RSS after warmup:
#             ~569MB — over Render's 512MB free-tier ceiling.
#   "onnx"  — chromadb's bundled ONNXMiniLM_L6_V2 (onnxruntime + tokenizers,
#             no torch). Adopted specifically to fit the free tier; see
#             THRESHOLD.md for the re-measurement this required.
#
# "torch" is kept as a fallback for local A/B comparison, not because it's
# expected to be used — flip back only if the onnx numbers don't hold up.
EMBED_BACKEND = "onnx"

# Normalised vectors + a cosine collection metric are what make relevance
# scores fall in a usable [0, 1] range. With the defaults (unnormalised
# vectors, L2 metric) LangChain computes 1 - distance/sqrt(2), which goes
# negative on this data — so no threshold in [0, 1] means anything.
#
# Only affects the "torch" backend: chromadb's ONNXMiniLM_L6_V2 normalises
# internally regardless of this flag, so under "onnx" it's a no-op kept
# here for the torch fallback path.
EMBED_NORMALIZE = True
CHROMA_COLLECTION_METADATA = {"hnsw:space": "cosine"}

# all-MiniLM-L6-v2 truncates input at 256 tokens. Text past that point is
# NOT represented in the vector at all. Chunks are therefore built to fit
# under this budget, with headroom for the title prefix we prepend.
EMBED_MAX_TOKENS = 256
CHUNK_TOKEN_BUDGET = 230


# --- generation ------------------------------------------------------------
# Cheapest current-generation model; this is a classification/extraction/
# summarisation workload, which it is well suited to. If grounding
# discipline proves too weak here, escalate to claude-sonnet-5 rather than
# loosening the guardrails.
GENERATION_MODEL = "claude-haiku-4-5-20251001"
GENERATION_TEMPERATURE = 0.0
GENERATION_MAX_TOKENS = 1024


# --- retrieval -------------------------------------------------------------
# k is deliberately larger than the 4 used previously: chunks are now
# smaller (they have to fit the encoder window), so a single answer often
# needs several of them. See RELEVANCE_THRESHOLD — irrelevant results are
# dropped by score, not by rank, so a larger k does not mean more noise.
# Measured, not guessed. Chunks are small (they have to fit the encoder
# window), so a single answer often needs several. On a 10-query recall
# probe, the chunk that actually answers the question sat at rank #11 for
# "does Adipven handle IP licensing?" and #12 for "who is the managing
# director?" — both just outside k=10, which produced confident, correct,
# and completely unnecessary refusals.
#
#   recall@4 = 6/10   recall@10 = 6/10   recall@15 = 8/10   recall@30 = 8/10
#
# 15 captures the gain; beyond that only adds distractors. Raising k does
# not weaken the off-topic gate, which keys on the top-1 raw score.
RETRIEVAL_K = 15

# Chunks scoring below this are discarded before the model ever sees them.
# Chosen empirically — see THRESHOLD.md for the full measurement.
#
#   off-topic queries  top-1 score: 0.090 - 0.273  (n=6)
#   on-topic  queries  top-1 score: 0.268 - 0.765  (n=16)
#
# The two classes overlap slightly, so no threshold separates them cleanly.
# 0.25 keeps 16/16 on-topic queries and rejects 5/6 off-topic ones. The
# alternative, 0.30, rejects 6/6 off-topic but also silently kills three
# core queries ("what is your phone number", "where is your office",
# "how do I stop people copying my design") — contact chunks are short
# label-value blocks and score low against natural questions.
#
# Recall is favoured deliberately: a false refusal on a contact question is
# a guaranteed lost enquiry, whereas a marginal off-topic chunk still has to
# get past the grounding check, which drops any answer the chunks don't
# support. The threshold is the defence against off-topic queries; it is
# NOT a defence against on-topic-but-uncovered ones (see THRESHOLD.md).
RELEVANCE_THRESHOLD = 0.25

# Scores within this band count as tied, and authoritative (current,
# firm-level) chunks sort above historical ones inside a band. Without it,
# a 2017 announcement outranks the Contacts page on "what is your phone
# number" by 0.006.
SCORE_TIE_BAND = 0.05

# The store is 60% case studies (151 of 252 chunks) and only 22 service
# chunks. Case studies are long narrative prose and out-score the short
# service-page descriptions on almost any customer-phrased question — ask
# "how do I protect the shape of my product" and you get litigation
# summaries, not the industrial design page. CLAUDE.md ranks service and
# contact content Tier 1 and case studies Tier 3; raw similarity inverts
# that.
#
# This boost is applied ONLY after the query has already cleared the
# relevance threshold on its raw scores (see retrieve()). An off-topic
# query never reaches this stage, so the boost cannot pull service content
# into an otherwise-empty result.
SERVICE_CONTENT_BOOST = 0.12
BOOSTED_SECTION_TYPES = frozenset({
    "service", "contact", "credentials", "process", "pricing",
    # "background" carries the About Us service list, the response-time
    # commitments, and the geographic coverage statement — Tier 1/2 content
    # by CLAUDE.md's priority order, typed "background" only because of
    # which H2 it sits under. Without it, "do you handle trademark
    # oppositions?" returned 14 case studies and refused, even though the
    # About Us list answers it directly.
    "background",
})

# Boosting only re-scores what the main search already returned, so it
# cannot rescue a chunk that never made the top-k at all. For queries about
# a topic the case studies also cover, all 15 slots can go to litigation
# summaries: "do you handle trademark oppositions?" returned 14 case studies
# and refused, while the About Us list answering it sat far down the ranking.
#
# So a second, filtered search runs alongside the main one, restricted to
# the firm's own descriptions. It guarantees they are always candidates.
# Like the boost, it runs only AFTER the off-topic gate has passed.
SUPPLEMENTARY_K = 5
FIRM_DESCRIPTION_TYPES = [
    "service", "contact", "credentials", "process",
    "pricing", "background", "people", "testimonial",
]


# --- fail-closed redirect --------------------------------------------------
# Used whenever the agent must refuse. Kept in config rather than generated
# by the model so that a refusal can never itself be an ungrounded claim.
#
# SOURCE: adipven_content/04-company-contact.md, "Contact & Identifying
# Information" (Contacts page values, treated there as authoritative over
# the conflicting info@adipven.edu.my found in Home-page boilerplate).
# If the source document changes, update this constant to match.
CONTACT_EMAIL = "info@adipven.com"
CONTACT_PHONE = "+603 2201 4023 / +603 2201 4026"

CONTACT_REDIRECT = (
    f"Please contact Adipven directly and the team can help: "
    f"email {CONTACT_EMAIL} or call {CONTACT_PHONE}."
)

NO_INFO_ANSWER = (
    "I don't have that information on hand. " + CONTACT_REDIRECT
)

PRICING_ANSWER = (
    "Adipven's published material doesn't include fees, rates, or cost "
    "estimates, so I can't quote or estimate a price. " + CONTACT_REDIRECT
)
