# Streaming strategies — evaluation

Analysis only. No source file was modified to produce this report.

---

> ## ⚠️ CORRECTION (added after the original report)
>
> **Several timing findings below are wrong.** They were corrupted by
> network-level buffering on the development machine, which I mistakenly
> attributed to the model and to LangChain.
>
> **The evidence.** In one instrumented tool-use turn, overall generation
> measured **83.6 tok/s** (791 output tokens in 9.46s) — a normal rate. But
> the bytes arrived like this:
>
> ```
> t=1.70s      0 chars (0%)
> t=7.48s    335 chars (11%)     <- ~5.8s of silence, then...
> t=7.58s   2208 chars (71%)     <- 1,900 chars in 0.1 seconds
> ```
>
> Generation at 83.6 tok/s cannot emit 1,900 characters in 0.1s. Those
> tokens were produced steadily server-side over ~6s and delivered to the
> client in bursts. No proxy env vars are set; the likely cause is local
> TLS inspection or the Windows network stack. Not diagnosed further.
>
> **What this invalidates:**
>
> - The claim that the `answer` field arrives in a ~0.03s / ~0.32s burst
>   (Strategy 1 "Mechanism", Strategy 2 "Time to first character"). That
>   was the local network, not the model.
> - The claim that LangChain's `with_structured_output().stream()` is not
>   genuinely incremental. That finding rested on the same corrupted
>   measurement and is now **unproven** — LangChain may be fine.
> - The recommendation's premise that visible streaming isn't achievable.
>
> **What survives:** the invariant analysis, the field-order safety
> argument, the disqualification of Strategy 3, and the finding that
> `reasoning` occupies the bulk of the turn and cannot be streamed.
>
> **Corrected estimate:** at ~83 tok/s, a typical answer here (~180
> tokens) takes **~2 seconds to generate** — genuinely perceptible
> streaming. Streaming is worth shipping.
>
> **Corrected recommendation:** merge PR #2 as-is and observe it over a
> real network path (Render → browser), which is a different path from the
> one that corrupted these measurements. Do **not** build Strategy 2 (raw
> SDK) until PR #2 has been observed in production — its entire
> justification was the LangChain batching finding, which is now unproven.
>
> The sections below are left unedited for audit purposes. Read them
> against this correction.

---

## Before the analysis: why you don't see streaming right now

Two separate causes, one you asked me to fix and one this report surfaces on
its own.

1. **The streaming code isn't merged.** `master` — what Render deploys — is
   still at `830a6e1`. The streaming implementation (`answer_stream()`,
   `check_prestream()`, `POST /query/stream`) lives only on the open branch
   `stream-answer-tokens` / PR #2. Nothing you're running today calls it.
2. **Even once merged, the current implementation will very likely still
   look like a single burst, not a typewriter.** This is a new finding from
   this session's measurement (see Strategy 1, "Mechanism", below): the
   LangChain wrapper the codebase streams through delivers the `answer`
   field's 604 characters across 87 micro-updates spanning **0.03 seconds**
   in the one case I traced end-to-end. That's below the threshold of human
   perception — indistinguishable from "the whole thing appeared at once,"
   which is exactly what you reported. Merging the open PR fixes cause 1 but
   not cause 2.

That second point is the reason this report doesn't simply recommend
"merge the PR." Strategy 2 below is what actually fixes cause 2, and it
isn't built yet.

---

## The invariant

No character of `answer` may reach the customer unless every grounding gate
that could reject that answer has already been decided. Today that's
achieved by schema field order (`schema.py`): `can_answer` and `source_ids`
are declared, and therefore complete, before `answer`. `check_prestream()`
(`grounding.py:196-235`) reuses `check()` verbatim and only permits
streaming once the two gates that could still be open at that point —
`EMPTY_ANSWER` (impossible once `answer` has started) and
`CLAIMS_WITHOUT_SOURCES` (decidable once `source_ids` is final) — are both
ruled out.

Any strategy that can't preserve this is disqualified outright, not scored
on latency. Strategy 3 below is that case.

## Why these three

**Strategy 1 (current)** is the required baseline. **Strategy 2** is chosen
because it's the direct answer to the mechanism defect found while
re-verifying the baseline for this report: LangChain's
`with_structured_output().stream()` does not deliver truly incremental
partial objects for a field this late in the schema, and the raw Anthropic
SDK — measured in the same session — does. It's the only alternative that
targets the actual symptom you reported, so it earns a full evaluation over
building something new rather than staying with a wrapper. **Strategy 3**
is chosen because it's the obvious next idea for anyone trying to fill the
~7-second dead-air gap before `answer` starts — "if we can't stream the
answer early, stream the reasoning as a live thinking indicator instead" —
and it fails the invariant in a way that isn't fixable by reordering, which
makes it worth ruling out explicitly rather than leaving as a tempting
unexamined option.

---

## Strategy 1 — Current implementation (baseline)

### 1. Mechanism

`agent.answer_stream()` (`agent.py:423-513`) drives
`get_chain().stream(...)`, LangChain's incremental-partial-object interface
over `ChatAnthropic.with_structured_output(AdipvenResponse)`. On each
yielded partial object, once `partial.answer` first becomes non-empty,
`check_prestream()` is called exactly once; if it clears, every subsequent
partial's *new* answer characters are yielded as `{"type": "delta"}` events.
`api.py:199-273` forwards these as SSE lines; `static/index.html` appends
them to a bubble and reconciles with the authoritative `final` event.

**New finding this session, not previously reported:** re-tracing the
per-field arrival timeline (`reasoning` vs `answer`) for "What services does
Adipven offer?" showed `reasoning` arriving as a **single update of 1,713
characters at t=14.91s** (not gradually), and `answer` arriving across **87
updates spanning t=16.24s→16.27s — a 0.03s window** for all 604 characters.
LangChain's partial-object reconstruction is not emitting one delta per
model token here; it appears to batch and only periodically re-parse+emit,
and for a field this late in the object, that batching collapses to
something the user cannot perceive as streaming at all. This is a
LangChain-wrapper behavior, not a property of the underlying model call —
see Strategy 2.

### 2. Invariant

Preserved by construction, and confirmed again this session by direct
inspection: at the first partial where `answer` is non-empty (9 characters:
`"Adipven o"`), `source_ids` already held 3 verified chunk IDs and
`can_answer=True`, and `check_prestream()` returned `may_stream=True`
correctly. `source_ids` and `can_answer` are declared before `answer` in
`schema.py`, so this holds for any query, not just the traced one.

### 3. Time to first customer-visible character

**Measured, this session, single-sample per query (see caveat below):**
first answer character at 11.64s / 3.72s / 6.99s against totals of
12.50s / 3.94s / 7.01s — gains of 0.9s (6.9%), 0.2s (5.4%), and 0.0s (0.3%)
respectively. Bounded below by however long `reasoning` takes for that
query, since `reasoning` is generated first and is not shortened by
streaming.

*Caveat:* these are single API calls per query; Anthropic API latency has
several seconds of run-to-run variance independent of any code change (the
same "services" question measured 16.08s total in one run earlier this
session and 12.50s in another, both blocking, no code changed between
them). Treat the percentages as order-of-magnitude, not precise.

### 4. Total turn latency

Neutral. No additional model calls; same generation.

### 5. Cost per turn

Baseline by definition: 1 API call, `config.GENERATION_MODEL =
"claude-haiku-4-5-20251001"`, `max_tokens=1024`, `temperature=0.0`.

### 6. Accuracy risk

None beyond the schema reorder already shipped on the PR branch, re-verified
fresh this session:

- `eval.py` (non-live): off-topic gate 5/6, recall@k 6/10 at both k=4 and
  k=10, pricing gate 18/18.
- `eval.py --live`: section 6 (grounding discipline on adjacent-uncovered
  queries) 8/8 refused; section 7 (false-refusal rate on answerable
  queries) 0/8; section 8 (forced fabricated-source-id) — `PASS`,
  `verdict=reported_source_ids_not_in_retrieved_set`, `can_answer=False`.

A regression in the reorder specifically would show up as a drop in section
7 (the model declining answerable questions because it now has to commit to
`can_answer` before writing the answer) or section 6 (the model answering
something it shouldn't). Neither moved.

### 7. Code surface

`schema.py`, `grounding.py` (`check_prestream`), `agent.py`
(`answer_stream`, `_final`), `api.py` (`/query/stream`), `static/index.html`
— all on the open PR. `answer()` and `answer_stream()` are guaranteed to
agree because `_final()` (`agent.py:516-539`) runs the same
`grounding.enforce()` call the blocking path uses, and logs `CRITICAL` if a
streamed answer's final verdict ever disagrees with what `check_prestream()`
promised. That log line fired 0 times across every test in this session and
the prior one.

---

## Strategy 2 — Raw Anthropic SDK streaming, bypassing LangChain's wrapper

### 1. Mechanism

Replace `get_chain().stream()` with a direct call to
`client.messages.stream(...)` (the raw Anthropic SDK, already used for
measurement in this session's probes) using the same tool schema
(`AdipvenResponse.model_json_schema()`). Accumulate the raw
`input_json_delta.partial_json` text into a buffer and track, with a small
hand-rolled JSON-prefix scanner, the moment the `answer` key's string value
opens — at which point every earlier field (including `source_ids` and
`can_answer`) is provably closed and parseable, so `check_prestream()` can
run on a partially-deserialized dict instead of a LangChain partial object.
From that point, forward each new fragment of the `answer` string value as
it streams in, rather than waiting for LangChain's periodic re-parse. On
stream completion, parse the full accumulated JSON with
`AdipvenResponse.model_validate_json()` for the authoritative object —
identical to what `check()`/`grounding.enforce()` consume today, so no
downstream logic changes.

### 2. Invariant

Preserved, by the same rule as Strategy 1 — same schema, same field order,
same "only stream once the fields before `answer` are closed" logic. The
difference is entirely in how the partial state is derived (a hand-rolled
JSON-prefix scan vs. LangChain's object reconstruction), which introduces a
**new, currently-untested correctness risk of its own**: the scanner has to
correctly find the boundary of `answer`'s JSON string value without being
fooled by an escaped quote (`\"`) inside the answer text, or a chunk
boundary that splits a multi-byte UTF-8 character or an escape sequence
across two SSE frames. Getting this wrong could emit the wrong field's text,
or emit corrupted characters that never appear in the final validated
object. LangChain's parser handles this today; a replacement would need to
prove it does too, before it could be trusted the way `check_prestream()`
is trusted now.

### 3. Time to first customer-visible character

**Not improved over Strategy 1 — same generation, same order.** The model
still writes `reasoning` before `answer` regardless of which client parses
the byte stream; this session's raw-SDK measurements of when the `"answer":`
key first appears in the JSON buffer are 11.64s / 3.72s / 6.99s for the same
three queries — effectively identical to Strategy 1's numbers, because
they're measuring the same underlying generation.

**Where this strategy actually helps — estimated, not measured:** once
`answer` starts, Strategy 1 delivers it as a ~30ms burst; Strategy 2 would
deliver it at whatever cadence the raw API actually emits those tokens.
This session measured the *whole* raw response (reasoning + all fields +
answer, 2,702 JSON characters) spanning 7.03 seconds across 403 events. If
`answer` (604 of those 2,702 characters, ≈22%) is emitted at a broadly
similar rate, a proportional estimate is roughly **1–2 seconds of
genuinely visible token-by-token typing** — but this is an extrapolation
from the whole-response rate, not a direct measurement of the `answer`
span specifically. See "falsifying measurement" at the end of this report.

### 4. Total turn latency

Neutral to very slightly worse — a small constant client-side overhead for
maintaining a custom streaming JSON scanner, negligible next to ~10–16s of
model latency.

### 5. Cost per turn

Unchanged from baseline: 1 API call, same model, same tokens. This is a
client-side parsing change only.

### 6. Accuracy risk

None to the grounding decision itself — `check()` is untouched, and
`check_prestream()`'s logic is reused unchanged, just applied to a
differently-sourced partial state. The risk is entirely in the new parser's
correctness (see "Invariant" above), and today **nothing in `eval.py`
would catch it**, because every section of `eval.py` calls
`agent.answer()` — the blocking path — never the streaming path or its
parser. A new live section would be needed: assemble the streamed answer
character-by-character for a sample of queries and assert byte-for-byte
equality against `response.answer` from the same turn, plus a specific
adversarial case (a question whose grounded answer legitimately contains a
double-quote or non-ASCII character) to exercise the escaping edge case
directly.

### 7. Code surface

`agent.py` only, in principle — a new streaming primitive alongside (or
replacing) `get_chain()`. `grounding.py`, `schema.py`, `api.py`, and
`static/index.html` are unaffected; the SSE wire contract is unchanged, so
the client needs no changes. `answer()` would stay on the LangChain path
(unaffected), so `answer()`/`answer_stream()` divergence risk is contained
entirely to the new code path and would need `_final()`'s
CRITICAL-on-mismatch defence re-verified against it from scratch — the
existing 0-CRITICAL track record does not transfer, since it was recorded
against LangChain's parser, not this one.

---

## Strategy 3 — Stream the `reasoning` field live as a "thinking…" indicator (DISQUALIFIED)

### 1. Mechanism

Instead of (or in addition to) streaming `answer`, forward the model's
`reasoning` text to the client as it's generated — via either delivery
mechanism above — rendered as a live "thinking" UI element, so the ~7-second
dead-air gap before `answer` starts has visible content instead of a static
typing indicator.

### 2. Invariant — disqualified, not traded off

`reasoning` is declared first in the schema specifically *because* it is
the model's scratchpad for deciding the very things the gate exists to
check: whether the question is pricing, whether it's conversational,
which chunks actually answer it, whether `can_answer` should be true. At
the moment any character of `reasoning` exists, **none** of those fields
have been decided yet — that's not a timing quirk fixable by reordering,
it's what "first field" means. There is no position in the schema
`reasoning` could occupy that would let it be gated before being shown,
because gating it requires the fields it exists to reason about, and those
fields don't exist until after it's fully written.

This isn't hypothetical: `grounding.refusal_for()` and
`conversational_reply()` (`grounding.py:238-311`) already treat `reasoning`
as sensitive enough to keep server-side even after a turn is *refused* —
the refusal object's internal notes field embeds
`"Model's original reasoning:\n{original.reasoning}"` precisely because
that reasoning is expected to sometimes contain the model's rejected,
uncited train of thought (e.g. "the passages might cover this, but chunk
X is only tangentially related, so I'll decline"). Streaming it live means
a customer sometimes reads the model entertaining an answer it's about to
retract, or reading intermediate uncertainty about a question the gate
later rules `PRICING` or `CLAIMS_WITHOUT_SOURCES`.

Per the brief: not scored on latency, total latency, cost, or code surface.
It's excluded on invariant grounds alone.

---

## Recommendation

**Merge PR #2 (Strategy 1) — it's correct and regression-free — but don't
expect it to look like streaming.** Then decide separately whether the
~1–2s typing effect Strategy 2 might buy is worth building and testing a
new safety-adjacent JSON parser for. Given the measured numbers, I'd lean
against it: the real dead time is the ~7s of `reasoning`, which neither
strategy touches, and Strategy 2's benefit is confined to a window this
report estimates, not measured, at 1–2 seconds. The better-leverage,
zero-risk move for that dead time is a **code-authored status indicator**
("Searching Adipven's services…") shown while `reasoning` is being
generated and swapped for the answer bubble once `check_prestream()`
clears — it streams no model text at all, so it carries none of Strategy
2's or Strategy 3's risk, and it directly addresses the 7-second gap that
both strategies evaluated here leave untouched. That's a UX change, not a
streaming strategy, so it's out of scope for this report's 7-axis
evaluation — noted here only because it dominates both evaluated
alternatives on effort-to-perceived-benefit.

**The one measurement that would falsify this recommendation:** directly
instrument the raw-SDK path to record inter-delta timestamps *within* the
`answer` value's byte range specifically (not the whole-response rate used
above), for a representative sample of queries. If that span turns out to
be on the order of Strategy 1's measured 30ms — i.e., the model writes the
600-odd answer characters in a tight burst regardless of which client
parses the stream, rather than the ~1-2s the whole-response rate suggests —
then Strategy 2 provides no real benefit over Strategy 1 either, and the
right call becomes "skip both, ship only the status indicator."

---

## Status update — the `reasoning` dead time was addressable after all

This report treats the "~7s of `reasoning`" as fixed background that no
streaming strategy can touch. That framing was right about *streaming* and
wrong about the dead time being immovable, so it is worth recording what
changed rather than leaving the conclusion to read as final.

`reasoning` was measured at ~70% of generated output (3,214 chars vs 1,384
for `answer`, three queries). It was then cut to telegraphic notes with an
explicit closing verdict — concise chain-of-thought, per Chain of Draft
(arXiv 2502.18600) — bringing it to ~58% of output, a 44% reduction in mean
length, with no eval regression.

So the dead time this report identifies as dominant is a *prompt* variable,
not a floor. Both this report's conclusions still hold as written — the
status indicator was the right call, and Strategy 2's premise was
separately falsified — but "the real dead time is the ~7s of `reasoning`"
should be read as "…which is itself tunable", not as a constant.

The remaining large factor is the deployment tier: the same query measured
4.8s locally and 10.5–21.7s on Render's free instance, for identical work.
That is larger than anything in this report's scope.
