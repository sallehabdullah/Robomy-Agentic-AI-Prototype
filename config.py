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
# Local, no API key, no per-call cost — which keeps per-query cost at zero
# and avoids a second vendor dependency. (An earlier version of this
# comment cited an on-device Jetson Orin target; that is NOT the goal. The
# deployment target is a hosted web service.)
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
    # "people" — named practitioners' credentials (education, registrations,
    # languages) are Tier 1 content by CLAUDE.md's priority order, but a bio
    # chunk repeats a title line and a **Source(s):** URL block before the
    # actual credential sentence, so it under-scores case studies that
    # mention the same person in flowing prose. Without this, "who on the
    # team has a chemistry background" retrieved case-study mentions of a
    # person over that person's own bio. See PROJECT_LOG.md 2026-08-13.
    "people",
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
    "pricing", "background", "testimonial",
]

# "people" gets its OWN filtered search rather than sharing the k=5 pool
# above. The store has 8 individual bios; sharing FIRM_DESCRIPTION_TYPES'
# k=5 across 7 other types left people with ~1 slot, which mostly went to
# the same generic chunk. A named person's own bio needs its own budget to
# reliably surface. See PROJECT_LOG.md 2026-08-13.
PEOPLE_SUPPLEMENTARY_K = 16


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

# Conversational reply pools, grouped by category. Used two ways:
#
#   1. The trivial-message fast path (agent._trivial_category) picks
#      randomly from the matching pool for an exact-match greeting/thanks/
#      meta message — no model call, no latency, no cost.
#   2. grounding.refusal_for() falls back to "generic" if the model's own
#      conversational answer is empty or exceeds the length cap. The model's
#      own text is preferred when it's present and reasonable (see Task 2 in
#      the brief this was built against) — these pools are the safety net,
#      not the primary source of conversational replies.
#
# Text constraints (matter for safety, not just tone): no factual claims
# about Adipven beyond the service-area names already in the system prompt
# (those are the firm's own published list, so they're safe); no "we"
# voice — this bot is Adipven's assistant, not Adipven itself; no sales
# language. Kept in code so even the fast path — which never touches the
# model — still varies its phrasing.
CONVERSATIONAL_POOLS: dict[str, list[str]] = {
    "greeting": [
        "Hello! What would you like to know about Adipven's IP services?",
        "Hi there — I can help with questions about patents, trademarks, "
        "industrial design, and more. What's on your mind?",
        "Hey! Ask me anything about Adipven's intellectual property services.",
        "Hello! I'm here for questions on patents, trademarks, copyright, "
        "and the rest of Adipven's IP services.",
        "Hi! Happy to help with questions about Adipven's IP services — "
        "what would you like to know?",
    ],
    "thanks": [
        "You're welcome! Let me know if you have any other questions about "
        "Adipven's services.",
        "Happy to help — feel free to ask anything else about Adipven's IP "
        "services.",
        "Glad I could help! Anything else you'd like to know?",
        "No problem at all — ask away if anything else comes to mind.",
        "You're welcome — happy to help with any other IP questions.",
    ],
    "meta": [
        "I can answer questions about Adipven's services — patents, "
        "trademarks, industrial design, copyright, geographical "
        "indications, licensing, enforcement, IP audit and valuation, and "
        "IP training. What are you interested in?",
        "I answer questions about Adipven's intellectual property "
        "services: patents, trademarks, industrial design, copyright, "
        "geographical indications, licensing, enforcement, IP audit and "
        "valuation, and training. Where would you like to start?",
        "I'm here to help with questions on Adipven's IP services — from "
        "patents and trademarks to enforcement and IP training. What "
        "would you like to know?",
    ],
    # Fallback only: the model's own conversational answer (off-topic
    # remarks, "how are you", anything not an exact greeting/thanks/meta
    # match) is preferred and passed through as-is — see grounding.py. This
    # pool is reached only if that text is missing or too long.
    "generic": [
        "I'm best at answering questions about Adipven's IP services — "
        "patents, trademarks, industrial design, copyright, and more. "
        "What would you like to know?",
        "I can help with questions about Adipven's intellectual property "
        "services. What would you like to ask?",
        "That's outside what I can help with, but I'm happy to answer "
        "questions about Adipven's IP services — patents, trademarks, and "
        "more.",
        "I focus on Adipven's IP services — feel free to ask about "
        "patents, trademarks, industrial design, or enforcement.",
    ],
}

# The model's conversational answer is passed through as-is (see
# grounding.py) rather than replaced — but a greeting reply should be a
# sentence or two. A much longer one suggests the model generated
# substantive content and mislabelled it conversational; that gets swapped
# for a "generic" pool pick instead of shown verbatim.
CONVERSATIONAL_LENGTH_CAP = 300

# A user who sends three consecutive greetings/pleasantries with no
# substantive question in between gets a firmer steer on the third,
# instead of a fourth "what would you like to know?" Tracked client-side —
# currently only cli.py does this; the API is stateless per the brief.
CONVERSATIONAL_ESCALATION = (
    "I'm best at answering specific questions about Adipven's IP services "
    "— for example, you could ask about patent filing, trademark "
    "registration, or enforcement. What would you like to know?"
)

# --- streaming status ------------------------------------------------------
# Shown while the model is working, before any answer text is legal to
# display. Measured in production: time-to-first-answer-character is
# ~15-16s, of which the streamed answer itself occupies only ~1.3s. The
# customer therefore spends roughly 90% of the turn watching nothing, and
# that gap is NOT streamable — `reasoning` is the first schema field and
# must complete before the grounding gate can rule (see
# grounding.check_prestream), and it is internal text that must never be
# shown regardless.
#
# These strings are code-authored and constant. That is the whole point:
# they carry no model output, so they have no grounding surface and cannot
# leak an unverified claim while the gate is still undecided. Do not make
# them dynamic or derive them from the model's output.
#
# Kept generic on purpose — true of every query and promises nothing about
# whether an answer exists.
STATUS_MESSAGES: dict[str, str] = {
    "retrieving": "Searching the Adipven website database…",
    "composing": "Verifying information integrity…",
}

# Whole-message greetings/pleasantries that need no model call at all — the
# agent answers these in code, instantly and at zero API cost. Matching is
# exact on the normalised (lowercased, punctuation-stripped) message, so
# "hi" alone matches but "hi, do you file patents?" does not and still goes
# to the model. Keep these sets conservative for that reason. Anything not
# listed here (including "how are you", off-topic remarks, etc.) still goes
# to the model, which classifies it via the `conversational` field.
TRIVIAL_GREETINGS = frozenset({
    "hi", "hello", "hey", "yo", "hiya", "howdy", "hi there", "hello there",
    "good morning", "good afternoon", "good evening", "greetings",
})
TRIVIAL_THANKS = frozenset({
    "thanks", "thank you", "thankyou", "thanks a lot", "ty", "cheers",
})
TRIVIAL_META = frozenset({
    "what can you do", "what can you help with", "what do you do",
    "help", "who are you",
})

# category -> message set, in priority order. Built once; agent.py looks
# messages up against this rather than three separate membership checks.
TRIVIAL_CATEGORIES: dict[str, frozenset[str]] = {
    "greeting": TRIVIAL_GREETINGS,
    "thanks": TRIVIAL_THANKS,
    "meta": TRIVIAL_META,
}
