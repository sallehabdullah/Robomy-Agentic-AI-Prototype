# Project Log — Adipven Assistant

Running chronological record of decisions and why they were made. Git history has the what; this file has the why, including the paths that were tried and rejected. Append to this file going forward rather than starting a new one — each entry should be one dated block, newest at the bottom, and should stay even after later entries supersede its conclusion (correct forward, don't delete backward — see the 2026-08-13 entries for the pattern).

---

## 2026-08-10 — Initial build

**What:** FastAPI wrapper + Render deployment artifacts, ONNX embedding backend, customer-facing chat UI, conversational-turn handling, brand restyle.

**Decisions:**
- **Deployment target is Render (hosted web service), not an edge device.** An earlier brief had named a Jetson Orin as the eventual on-device target; that requirement was dropped. The Jetson reference was removed from code comments (`33d5916`) so future reasoning about model size / local-vs-cloud inference doesn't get anchored to a target that no longer applies. This is now stated as a hard rule in `CLAUDE.md`.
- **Embedding backend switched to ONNX** (`0c93b7b`) specifically to fit Render's free tier — the `torch` backend is a documented but dead path (`EMBED_BACKEND = "onnx"` in `config.py`), kept as a switch rather than deleted.
- **Greetings/small talk handled conversationally instead of cold-redirecting** (`b70e154`, `830a6e1`) — a "hi" used to get the same "I don't have that; contact Adipven" redirect as a genuine unanswerable question. Fixed by adding a `conversational` field to the schema and a dedicated grounding path (`Failure.CONVERSATIONAL`) that carries the model's own varied reply instead of a static redirect, since a greeting makes no factual claim and needs no citation.

---

## 2026-08-11 — Token streaming

**What:** Answer text streamed to the client instead of returned as one block after full generation (`b2237ca`, merged as PR #2).

**Decision — the core safety constraint that shapes everything downstream:** streaming is gated so that no character of the answer can reach the customer until every grounding gate that could reject it has already been decided. This is why the response schema declares fields in a specific order — `reasoning` first, then `can_answer`/`source_ids`, `answer` last — because structured-output generation fills fields in declaration order, so by the time `answer` starts arriving, everything the grounding check needs to run is already final. See `schema.py`'s module docstring and `grounding.check_prestream()`.

**Rejected/deferred:** streaming `reasoning` itself was not done — the scratchpad is explicitly internal and never shown to the customer, so streaming it would leak the model's uncommitted internal deliberation before the grounding verdict is final.

---

## 2026-08-11/12 — Status indicator during the pre-answer wait

**What:** `4553a69` — a status message shown during the wait before streaming starts (the model still has to finish `reasoning` and commit to `can_answer` before any answer text can safely stream, so there's unavoidable dead air first).

**Finding:** initial smoothness measurement was measuring the wrong thing — raw gap size between tokens isn't what a user perceives as stuttering. Corrected in `c4ad5d3` ("Measure perceived smoothness, not raw gap size").

**Finding, `3b784ab`:** a chunking pattern initially suspected to be caused by buffering (a proxy or the local network holding tokens back) was, after a post-deploy production reading, actually CPU jitter — not a buffering bug. Notable because an earlier session had previously misattributed a similar symptom to local network buffering when it was actually the measurement instrument being wrong; this time the distinction was confirmed correctly. `measure_stream.py` is deliberately stdlib-only, importing nothing from the repo, specifically so the measurement tool itself can't be the thing under test.

**2026-08-12 — copy change:** status indicator text reworded for consumer appeal (`2ea93ff`, merged as PR #4) — "Searching the Adipven website database.." and "Verifying information integrity..", replacing more technical-sounding original copy.

---

## 2026-08-12 — Retrieval threshold warning + multi-part questions + formatting

**`81fd532` — Warn when an on-topic query's raw score sits near `RELEVANCE_THRESHOLD`.** Added to `eval.py` as a margin-warning check (`MARGIN_WARN`) in `eval_threshold_separation()`, so a query that passes the threshold only barely gets flagged in eval output even though it isn't currently failing — an early-warning signal for threshold drift, not a behavior change.

**`5e55ba1` — Multi-part questions answered partially instead of declined wholesale.** Previously, a message like "Give me more specifics on patents. Also, who would you recommend to represent me?" risked the whole reply being declined because one part (a referral) is unanswerable from the content store. Fixed in prompt/schema only, no `grounding.py` changes: `can_answer` is now true if at least one part is supported, and the model is instructed to answer the answerable part and decline the rest explicitly inside the same `answer` text. No grounding-gate change was needed because a compound reply is still one answer with one citation set — the existing fail-closed logic doesn't care how many sub-questions are inside `answer`.

**Same commit — readability formatting.** The UI renders `answer` as plain text (`textContent` + `white-space: pre-wrap` in `static/index.html`, never `innerHTML`), so an enumeration of more than ~3 items needed to break onto separate lines as a plain-text numbered/hyphen list rather than running into one paragraph — markdown syntax (`**bold**`, `#` headers) would display literally rather than render, so the schema's `answer` field description explicitly says "plain text" list formatting only.

**Retrieval-strategy latency evaluation (not committed as code — a judgment call recorded here):**
- *"Faster model mix"* (small model for planning/reasoning, large model only for the final answer) — evaluated against the actual architecture and set aside: the current design is a single structured-output call where `reasoning` and `answer` come from the same generation, not a separate planning step: splitting them would add a second model round-trip, which very likely costs more latency than it saves, and introduces a second consistency surface between what the "planner" decided and what the "writer" is allowed to say.
- *"Parallelize tool calls"* — also set aside: there's no fan-out of multiple retrieval calls per turn currently; retrieval is a single fast call (0.13–0.15s locally, full path including the supplementary filtered search), so there's nothing to parallelize in the current architecture. The dominant latency cost is model generation time for `reasoning`, not I/O.
- **Deployment tier, measured directly, found to be a bigger factor than either strategy above:** a direct comparison of an identical non-streaming query showed local ~4.8s vs. production (Render free tier) ~10.5–21.7s. This corrected an earlier-session conclusion that had said deployment tier was *not* a dominant latency factor.

---

## 2026-08-13 — Concise chain-of-thought, quality pass, anatomy report

**`37fb25e` — Cut `reasoning` length ~44% with concise, verdict-anchored scratchpad notes.** Applied Concise/Chain-of-Draft prompting (arXiv 2502.18600) to the `reasoning` field across `schema.py` and `agent.py`'s system prompt and few-shot examples: telegraphic notes instead of prose, since `reasoning` is internal-only and every word in it is time the customer spends waiting.

**Regression found and fixed, same day, before this landed:** the first pass (reasoning capped under 40 words, "skip a check rather than writing it out to dismiss it," no requirement to state a conclusion) caused "What services does Adipven offer?" — the single most important query in the store — to intermittently false-refuse (`model_reported_it_cannot_answer: no sources cited`), reproduced at ~25% (1 in 4 runs). Root cause: brevity had started eating the actual decision, not just the explanation of it. **Fix:** required the reasoning to close with an explicit verdict — which chunk IDs will be cited, and answerable yes/no — on all three prompt surfaces (schema field description, a new system-prompt section, and all six few-shot examples). Verified via a 9-run probe (0/9 false refusals) and a full `eval.py --live` battery (all clean), while still holding a 44% length reduction (1,071 → 604 mean chars) and reasoning's share of total output dropping from 69.9% to 57.9%.

**Rule this produced, now written into the schema description itself:** brevity in `reasoning` is about how much gets written down, never about how much gets checked — a terse note that ends "answerable, cite X" is correct; skipping the verdict and defaulting to "can't answer" is the one failure this must never produce.

**`ec94600` — Correct timing claims the concise-CoT change invalidated.** Two code comments in `agent.py` and one paragraph in `STREAMING_STRATEGIES.md` had stated timing splits (e.g. "~7s of ~16s is reasoning," "~0.08s retrieval") that were true before the reasoning-length cut and became stale the moment it landed. Self-caught during a quality-check pass, not user-reported — corrected rather than left, since a stale measurement stated as fact reads as more authoritative than no claim at all. `STREAMING_STRATEGIES.md` was appended-to rather than rewritten, so the original report's reasoning stays visible alongside the correction.

**Also in the quality pass:** removed a stray 0-byte file (`0`) at the repo root — an accidental shell-redirect artifact, not intentional state. AST-syntax-checked all 9 `.py` files; no functional bugs found. Noted but deliberately left alone: `backup/` isn't in `.gitignore` (clutters `git status` but isn't broken), and the `torch` embedding backend is documented dead code, not an oversight.

**Anatomy report published** (teaching document, not part of the running codebase): `https://claude.ai/code/artifact/19a5a64d-ccc5-46c3-a3b2-62660df47039` — covers all 12 project files, each as problem → code → why it generalizes, aimed at someone without deep coding background learning agentic-AI patterns from this codebase specifically. Not a substitute for this log: it explains the current shape of the code, not the sequence of decisions that got it there.

**Production status as of this entry:** the concise-CoT change (`37fb25e`, `ec94600`) is committed and pushed to `master`, which auto-deploys on Render — but no post-deploy production measurement has been run yet to confirm the ~44% reasoning reduction is actually reflected in live latency. That's the natural next check.

---

---

## 2026-08-13 (later) — Correction: concise-CoT was not actually pushed yet

The previous entry stated the concise-CoT change (`37fb25e`, `ec94600`) was "committed and pushed to `master`" — that was wrong. Both commits existed only locally; `origin/master` was 2 commits behind. Pushed now (`git push origin master`, `5e55ba1..b47a8ec`), bundled with the project-log/UI-brief/chroma_db commit made earlier today. Render auto-deploy should pick this up from the push.

---

## 2026-08-13 (later still) — Fixed: "who on the team can help" false refusal

**Reported:** a customer asked who on the team could help with an Applied Chemistry patent query. The agent named no one and redirected to the contact channel, even though Ramakrishna Damodharan's stated education (Applied Chemistry degree, per `02-people.md`) was in the store. When the customer pasted his bio back into the chat, the agent immediately cited him correctly — proving the underlying fact was answerable and the miss was upstream of the model's judgement.

**Diagnosis, retrieval-only (no model call, isolates cause from grounding.py's behavior):** ran `retrieve()` against the exact customer phrasing. All 15 returned chunks; zero were his. Three compounding causes, each measured directly:

1. `people` was absent from `BOOSTED_SECTION_TYPES` (`config.py`) — bios got no corpus-imbalance correction, unlike service/contact/background content, so they lost to case studies mentioning the same person in passing.
2. `people` shared `SUPPLEMENTARY_K=5` across all 8 `FIRM_DESCRIPTION_TYPES`, leaving it roughly one guaranteed candidate slot against 8 named practitioners' bios.
3. The bio chunk itself was diluted: a title-line repeat, a `**Source(s):** <url>` boilerplate line, and a 370-char registration-number list ahead of the one-sentence education fact that actually answered the question.

**Fix, in order (retrieval before policy — a prompt change is untestable until the model can see the chunk, and risks the model naming someone without evidence if it lands first):**

- Added `people` to `BOOSTED_SECTION_TYPES`.
- Split `people` out into its own filtered supplementary search, `PEOPLE_SUPPLEMENTARY_K=16` — the smallest value that reliably surfaced the target chunk on a 6-query labelled credential-match probe (8 caught 4/6, 16 caught 6/6). See THRESHOLD.md's "People-retrieval fix and re-ingest" section for the full before/after regression table.
- Stripped `**Source(s):**` lines from embedded chunk text in `ingest_adipven.py` (kept in metadata) — re-ingest required regardless once chunk boundaries move; measured in isolation as *not* the thing that fixed the reported query, kept anyway as a correct simplification.
- Re-ingested (252 → 243 chunks).

That alone fixed the reported query end-to-end, live, with zero prompt change — cites Rama, states his credential, frames it as "could help" without asserting assignment.

**Second, independent defect found while testing an adjacent phrasing:** "who would you recommend I reach out to ... for a biomedical technology query" still refused — but retrieval *did* surface a correctly-credentialed person (Dr Kumutha Priya, "Degree in Biomedical Science" per `02-people.md`) well above threshold. This was a policy gap, not retrieval: the model's own reasoning showed it treating "who should represent me" (a real, deliberate refusal category — the firm doesn't publish staffing/assignment decisions, see the existing few-shot in `agent.py`) as covering "who can help" (a credential-match question the store does answer) as well. Fixed by adding a `agent.py` system-prompt section that names the distinction explicitly (credential match vs. assignment/referral) plus one contrasting few-shot pinned to the exact reported query. Verified live: the reported case now answers correctly, the pre-existing assignment-decline few-shot still declines correctly, and a "recommend...reach out to" phrasing for a matter the store doesn't cover by name still correctly declines — that boundary case is a defensible reading of genuinely ambiguous phrasing, not a bug, and was left alone.

**Regression, full `eval.py --live`:** 8/8 adjacent-uncovered refused, 0/8 false refusals, forced-fabrication test still fails closed, 18/18 pricing gate, all pre-existing on/off-topic gate results unchanged. One side effect noted, not fixed: the pre-existing off-topic leak on "recommend a good science fiction novel" (raw score already above threshold before this change — see THRESHOLD.md's "Why 0.25") now surfaces 3 people chunks instead of 1, since bios generally score better post-boost. Judged acceptable: the leak itself predates this change, and any answer built from it still has to clear `grounding.py`.

**`grounding.py` was not touched** — every gate in this incident behaved correctly given its inputs; the defect was upstream (what the gate was given to check) in both the retrieval and policy findings above.

**Pushed:** committed as `8e4097e` and pushed to `master` the same day (superseding the "not yet deployed" note this entry originally had here) — Render auto-deploy should pick it up.

**Anatomy of a Grounded Agent report updated to match:** the teaching artifact (`https://claude.ai/code/artifact/19a5a64d-ccc5-46c3-a3b2-62660df47039`) was revised in place rather than left describing pre-fix behavior. New material was integrated into its existing sections, not appended as a changelog: `retrieval.py`'s section gained "The same bug, one layer deeper" (the corpus-imbalance correction existed but hadn't reached `people`, and why a shared supplementary budget quietly starves whichever category has the most named entities); `ingest_adipven.py`'s section gained the `Source(s):` boilerplate-dilution fix, including the honest note that it alone didn't resolve the reported case; `agent.py`'s section gained "Two questions that look alike, and aren't" covering the credential-match vs. assignment distinction; and the closing lessons list gained: diagnose retrieval before touching the prompt, since a refusal can come from either layer and the two look identical from the customer's side.

---

## 2026-08-13 (branch) — `experiment/exclude-case-studies`: index built without case studies

**Branch, not master.** `master` keeps case studies; this branch exists to test the agent without them and can be returned from by checkout. `abc21ae`.

**What:** `EXCLUDED_SECTION_TYPES = {"case_study"}` in `ingest_adipven.py`, filtered in `build_documents()` after parse and before dedupe. 243 → 99 chunks.

Filtered by section type, not filename. `adipven-content-store.md` carries its own `## Clients & Case Studies` block whose condensed restatements currently *lose* dedupe to the longer 03- versions — excluding only `03-case-studies.md` would have promoted the summaries, not removed the content. Filtering before dedupe matters because `dedupe_sections` only ever matches within a section type, so dropping one type cannot disturb another's merges: confirmed, every non-case-study count is byte-identical to the baseline census (announcement=6, background=15, contact=6, credentials=6, people=34, pricing=3, process=1, provenance=5, service=21, testimonial=2). Announcements deliberately kept — single variable, and it keeps the HISTORICAL path in `agent.py`/`schema.py` exercised by real chunks. `config.py`'s three imbalance corrections were left exactly as they are, since whether they still earn their keep is a question *for* this test, not an input to it.

**Retrieval precision improved substantially.** recall@15 went 8/10 → **10/10** (recall@10: 6/10 → 8/10). Every one of the four documented "case studies drowned the answer" failures inverted: "do you handle trademark oppositions?" moved from rank #31 to **#3**, "can Adipven help if someone is infringing my trademark?" #41 → #13, "who is the managing director?" #13 → #10, "what services does Adipven offer" #9 → #6. Firm-description share of results rose from 21/35 to 28/30 on the oppositions query. All live gates unchanged and clean: 8/8 adjacent-uncovered refused, 0/8 false refusals, forced fabrication still fails closed, 18/18 pricing.

**But the off-topic gate got worse, not better — and this is the finding that matters.** On-topic/off-topic score separation widened in the wrong direction: −0.009 → **−0.032**. Two on-topic queries now fall below `RELEVANCE_THRESHOLD = 0.25` and are hard-rejected with 0 chunks, i.e. the customer gets the fail-closed redirect:

- "how do I protect the shape of my product" — raw max **0.181** (was above threshold), top hit `01-services__patents`
- "I designed a new bottle cap, how do I stop people copying it?" — raw max **0.244**, top hit `01-services__copyrights`

Both are industrial-design questions, and `01-services__industrial_design` is still in the store and still scores 0.520 on the direct phrasing "what is industrial design protection". The chunk did not get worse; the *bridge to it* disappeared. This also takes down `eval_supplementary_search`'s clarification-reply case (`industrial_design` surfaced in 0 kept, was 14) — that check depends on the same query clearing the gate first.

**What this actually shows:** the case studies were doing a second job nobody had credited them with. `config.py:120-131` frames them purely as noise — long litigation prose that out-scores short service copy. That framing is correct about *ranking*, and removing them fixes ranking exactly as predicted. What it misses is that the same narrative prose was also the only text in the store written in a customer's own vocabulary. A layperson describing their problem ("the shape of my product", "a bottle cap", "stop people copying it") matched a litigation summary far more readily than the terse service-page entry, and once that match cleared the threshold, the boost and supplementary searches could pull the correct service chunk up behind it. Remove the case studies and those queries no longer clear the gate at all — and the boost never runs, because it is applied only *after* the raw threshold passes (`config.py:128-131`).

**No single threshold fixes it.** The off-topic leak "recommend a good science fiction novel" scores **0.279** raw — higher than either failing on-topic query. Admitting the bottle-cap query means admitting the sci-fi query. The bands genuinely overlap; this is not a tuning oversight.

**Not touched, deliberately:** `RELEVANCE_THRESHOLD`, `SERVICE_CONTENT_BOOST`, `BOOSTED_SECTION_TYPES`, `SUPPLEMENTARY_K`, `PEOPLE_SUPPLEMENTARY_K`, `grounding.py`, `agent.py`, `schema.py`, `retrieval.py`. Re-tuning inside the same change would have confounded the experiment.

**Open decision this branch hands back:** shipping it as-is trades better ranking on questions that already worked for hard refusals on lay-phrased design questions — a bad trade on its face, since a wrong-but-present answer is recoverable in conversation and a refusal is not. The options worth measuring next, in rough order of appeal: (a) keep case studies out but add customer-vocabulary phrasing to the service chunks themselves, so the bridge is in Tier 1 content rather than Tier 3; (b) keep case studies in the index but demote them harder at rank time; (c) lower the threshold and accept a wider off-topic leak, relying on `grounding.py` to fail closed — weakest, since `THRESHOLD.md`'s "Why 0.25" already documents the sci-fi leak as the reason not to go lower.

**Side note, unrelated to the change:** merely *running* `eval.py` dirties the committed `adipven_chroma_db/` (sqlite + HNSW files rewrite on read), so `git status` shows modifications after any eval run. Restore with `git checkout -- adipven_chroma_db`.

## Open items / things not yet resolved

- **Deploy confirmation for the concise-CoT change:** now actually pushed to `master` (see correction above) — Render auto-deploy should be picking it up, but not yet verified against production with `measure_stream.py`.
- **`backup/` directory not gitignored** — cosmetic, not urgent.
- **`torch` embedding backend** — confirmed dead code, kept intentionally as a documented switch; revisit only if there's a reason to actually support it again.
- **`PEOPLE_SUPPLEMENTARY_K=16`** is fit to a 6-query probe (see THRESHOLD.md) — worth re-measuring if the People page content changes materially (new practitioner added, a bio rewritten).
- **Deploy confirmation for the people-retrieval fix (`8e4097e`):** pushed to `master`, same as above — not yet verified against production.
