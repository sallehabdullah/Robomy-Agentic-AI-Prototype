# Perceptible streaming — implementation plan

Follow-on from `STREAMING_STRATEGIES.md` (read its ⚠️ CORRECTION block
first). PR #2 is merged; `/query/stream` is live in production and
returning `text/event-stream`.

## What was discovered

Generation runs at **~83.6 tok/s** (measured: 791 output tokens in 9.46s).
A typical answer here is ~180 tokens, so **~2 seconds of genuinely
streamable text exists** — perceptible, worth showing progressively.

The earlier conclusion that it wasn't worth streaming came from measuring
on a dev machine whose network delivers the response in bursts (71% of one
response arrived in a 0.1s window after ~5.8s of silence, which generation
at 83.6 tok/s cannot produce). That contaminated every local timing
figure, including the claim that LangChain's `with_structured_output()
.stream()` batches instead of streaming incrementally.

**Consequence: we do not currently know whether streaming works in
production.** The code is deployed, but every measurement we have of its
behaviour was taken over a corrupted path. That is the gap this plan
closes, in order, without guessing.

## Guiding principle

Do not build a fix for a cause that has not been isolated. The previous
round of work produced a nearly-shipped raw-SDK rewrite justified entirely
by a finding that turned out to be a measurement artifact. Each phase below
must produce a measurement that selects the next phase.

---

## Phase 0 — Measure production (THIS IS THE ONLY PHASE IMPLEMENTED NOW)

**Goal.** Determine whether the deployed `/query/stream` delivers deltas
progressively over a real network path, or in a single burst.

**Mechanism.** A standalone HTTP client (`measure_stream.py`) that POSTs to
`/query/stream` and timestamps every SSE `data:` frame as it arrives.
Stdlib-only (`urllib`), no repo imports, no model load — so it measures the
network and server exclusively and cannot be contaminated by local
retrieval or LangChain behaviour. Runnable against production or localhost
for comparison.

**Reported metrics.**

| metric | why |
|---|---|
| time to first delta | how long the customer stares at nothing |
| delta span (first→last) | the width of the visible typing window |
| delta count | granularity |
| inter-delta gap percentiles (p50/p90/max) | distinguishes smooth flow from bursts |
| chars per delta | ditto |
| longest silent gap inside the span | the giveaway for buffering |

**Decision rule — this is what selects the next phase:**

- **Span ≥ ~1.0s with p50 gap in roughly the 10–100ms range** → streaming
  works in production. Stop. Go to Phase 3 (polish) only.
- **Span < ~0.3s, i.e. one burst** → buffering is present on this path
  too. Go to Phase 1 to isolate the layer.
- **Span ≥ 1.0s but with one dominant silent gap** → partial buffering,
  likely a flush-boundary issue. Go to Phase 1.

**Cost/risk.** A handful of live API calls (cents). Read-only against
production; no deploy, no repo behaviour change.

**Caveat that must be stated with any result.** Free-tier cold start adds
~30–50s to the first request after idle; the harness warms the instance
first and excludes that request from the measurement. Render's shared CPU
also adds variance, so several runs are needed before trusting a verdict.

---

## Phase 1 — Isolate the buffering layer (conditional)

Only if Phase 0 shows bursts. Three candidate layers, and the fix differs
completely per layer, which is exactly why guessing is not allowed here.

**1A. Model → server (LangChain).** Add temporary server-side logging in
`agent.answer_stream()` recording the wall-clock time each delta is
yielded. Compare against the client arrival times from Phase 0. If the
server-side yields are already bursty, LangChain (or the SDK/network from
Render to Anthropic) is the cause → Phase 2A. If server-side yields are
smooth but client arrival is bursty, the buffering is downstream → 1B.

**1B. Server → proxy.** `X-Accel-Buffering: no` is already set in
`api.py`. If deltas are smooth server-side but bursty at the client, the
next suspects are Render's edge proxy ignoring that header, and response
compression coalescing small chunks. Check response headers for
`content-encoding`; if gzip is being applied to the event stream, that
alone can defeat streaming.

**1C. Browser.** `fetch` + `ReadableStream` in `static/index.html` is not
expected to buffer, but confirm the browser sees the same arrival pattern
`curl` does before touching it.

---

## Phase 2 — Fix, per isolated cause (conditional)

**2A. LangChain is batching → raw SDK streaming.** This is Strategy 2 from
`STREAMING_STRATEGIES.md`, with its full cost re-stated: a hand-rolled
JSON-prefix scanner in the safety path, needing its own test for escaped
quotes and multi-byte characters split across frames, plus a new eval
section (nothing in `eval.py` exercises the streaming path today). Only
worth it against confirmed evidence. `check_prestream()` and the schema
field order are unchanged either way — the invariant does not move.

**2B. Proxy/compression is buffering → transport fixes.** Explicitly
disable compression for `text/event-stream`; consider SSE comment padding
(`: ` + filler) to force early flushes. Cheap, no safety surface.

---

## Phase 3 — The remaining ~6 seconds (independent of all the above)

Even with perfect streaming, `reasoning` must complete before any answer
character is legal to show. That is the invariant, not a defect. The
honest fix is a **code-authored status indicator** ("Searching Adipven's
services…") shown during that window — it streams no model text, so it has
no grounding surface at all, and it addresses the larger share of the wait.
Worth doing regardless of how Phases 0–2 resolve.

Optional, cosmetic, and explicitly *not* latency reduction: client-side
paced reveal of already-gated text. Only sensible if Phase 0 shows real
streaming is unavailable and cannot be fixed.

---

## What is NOT in scope

- Loosening `check()`, widening `RELEVANCE_THRESHOLD`, or trimming
  `reasoning` to win latency. `reasoning` was shortened once before and
  caused a measured regression (the model declined answerable questions).
  Any change there is an accuracy change requiring a live eval, not a
  streaming change.
- Migrating providers. Cohere's `chat_stream` emits citations *after* the
  text they annotate, which inverts our gate ordering and is disqualified.
- Prompt caching. Tested this session: `cache_control` on a 3,239-token
  prefix returned `cache_read_input_tokens=0` on every attempt, across
  streaming/non-streaming and with the legacy beta header. Needs an
  Anthropic console/support answer, not code.
