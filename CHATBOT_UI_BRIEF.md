# Task Brief — Customer-facing chat UI for the Adipven assistant

## Goal

Add a browser-based chat interface that ordinary website visitors can use to
talk to the Adipven assistant. Today the deployed service is a headless JSON
API: `POST /query` works, but the only browsable page is `/docs` (a developer
tool). A prospective client visiting the URL sees either a raw redirect or an
API schema, not a chat window. This task closes that gap.

This is still an experiment: the aim is a working, presentable chat page on the
existing free-tier deployment, not a polished production frontend.

## Current state (what already exists — do not rebuild)

- Backend: FastAPI in `api.py`, deployed on Render free tier at
  `https://adipven-assistant-api.onrender.com`.
- Endpoints:
  - `POST /query` — the one that matters. Request/response contract below.
  - `GET /health` — returns `{"status":"ok"}`; used by Render, not the UI.
  - `GET /docs` — auto-generated Swagger UI (keep for developers).
  - `GET /` — currently redirects to `/docs`. **This is the route the chat
    page will take over.**
- The agent logic (retrieval, grounding, clarification) is done and must not be
  touched. This task is presentation only — a second consumer of `/query`,
  exactly as `api.py` is a second consumer of `agent.answer()` beside `cli.py`.

### The `/query` contract (from `api.py`)

Request:
```json
{ "query": "string",
  "pending": { "original_query": "string",
               "clarifying_question": "string" } | null }
```

Response (`reasoning` is deliberately absent; do not try to surface it):
```json
{ "answer": "string",
  "service_area": "string",
  "can_answer": true,
  "requires_contact": false,
  "needs_clarification": false,
  "clarifying_question": "string | null",
  "source_ids": ["string"],
  "debug": null }
```

## Architecture decision — serve the page from FastAPI itself (same origin)

**Recommended: a single self-contained `index.html` served by the existing
FastAPI app at `/`, same origin as the API.**

Why this over a separately-hosted frontend (Netlify/Vercel/Render static site):

1. **It eliminates CORS entirely.** The page and the API share one origin, so
   the browser makes same-origin requests and `CORSMiddleware` never comes into
   play. A separately-hosted frontend would be CORS-blocked until its exact
   origin is added to `ALLOWED_ORIGINS` in `api.py` (which today lists only
   localhost, with a `TODO` for the real frontend origin). That is a real,
   easy-to-forget trap; same-origin sidesteps it.
2. **One deploy, one URL.** No second host, no second pipeline. Matches the
   free-tier, single-service footprint.
3. **Proportionate.** This is an experiment. No build step, no framework, no
   bundler.

Trade-off accepted: the page can't be cached on a CDN independently of the API,
and frontend redeploys ride along with backend deploys. For this project that
is fine.

Only revisit this if a separate, richer frontend is later wanted — in which
case the CORS step becomes mandatory and belongs in its own task.

### Concrete shape

- Add `frontend/index.html` — a single file containing inline CSS and vanilla
  JS. No CDN dependencies (so it works even under a strict CSP and offline
  during dev). No React/Vue/build tooling.
- In `api.py`:
  - Replace the `GET /` redirect-to-`/docs` with a route that returns the chat
    page (`FileResponse("frontend/index.html")`).
  - Keep `/docs`, `/health`, `/query` exactly as they are.
  - If assets are ever split out of the single file, mount them under a
    dedicated path (`app.mount("/assets", StaticFiles(...))`) — but do **not**
    mount `StaticFiles` at `/`, as that shadows the API routes. The single-file
    approach avoids this entirely.

## Task 1 — the chat page

A minimal, mobile-friendly chat layout:

- A scrollable message list (user messages right-aligned, assistant left).
- A text input + send button, fixed at the bottom.
- A short header with the firm name and a one-line disclaimer (see Task 4).

Behaviour on send:

1. Append the user's message to the list.
2. Disable the input/button and show a "typing…" indicator (see Task 3 —
   responses are slow on free tier).
3. `POST /query` with the body described below.
4. On success, append the assistant's `answer` and re-enable input.

## Task 2 — the clarification loop (stateless, client-carried)

This is the one non-obvious bit. HTTP is stateless and the server holds **no**
session — the clarification round-trip is carried by the client echoing a
`pending` object back, exactly as `cli.py` does in memory. Implement precisely:

```
let pending = null;   // module-scoped

async function send(userText) {
  const body = { query: userText, pending: pending };
  const res  = await postJSON("/query", body);

  if (res.needs_clarification && res.clarifying_question) {
    // show the clarifying question as the assistant's reply
    render(res.clarifying_question);
    // next turn: the ORIGINAL question + the reply the user is about to type
    pending = { original_query: userText,
                clarifying_question: res.clarifying_question };
  } else {
    render(res.answer);
    pending = null;   // clear once a real answer (or refusal) comes back
  }
}
```

Notes:
- `pending.original_query` is the question that triggered the clarification, not
  the reply. The reply becomes the next `query`. Getting this backwards breaks
  retrieval (the server searches on both).
- Only one clarification is ever pending at a time; a non-clarification response
  clears it. This matches the server, which never asks twice in a row.
- Known limitation (acceptable, just document it): if the user ignores the
  clarifying question and types an unrelated new question, it's treated as the
  reply for that one turn. The CLI has the same behaviour.

## Task 3 — free-tier latency is a first-class UX problem

Measured against the live deployment: normal responses take **~10–26 seconds**
on the free tier's shared CPU, and after 15 minutes idle the instance spins down
and the **first** request pays an additional **~30–50s cold-wake** on top. The
UI must not look broken during this.

- Persistent typing indicator while awaiting a response; keep the send button
  disabled so double-submits can't happen.
- Set a generous client timeout (≥ 60s). On timeout, show a friendly retry
  message, not a stack trace.
- Optional but recommended: fire a `GET /health` on page load to start waking
  the instance while the user reads the header — turns some cold-start latency
  into background time.
- Optional: after ~8s with no response, swap the indicator text to something
  like "still working — the assistant can take a moment" so long waits feel
  intentional rather than hung.

The backend returns a single structured object (not a token stream), so
true answer-streaming is **not** available without backend changes. Do not
promise a streaming/typewriter effect that reflects real progress; a static
"typing…" indicator is honest. (A cosmetic typewriter reveal of the finished
answer is fine, but note it's cosmetic.)

## Task 4 — safety and presentation (this is a law firm's public surface)

- **Disclaimer, always visible:** e.g. "Automated information assistant — not
  legal advice. For advice on your situation, contact Adipven." The agent is
  already built to fail closed and redirect rather than guess; the UI should set
  the same expectation up front.
- **Do not render `source_ids` to end users.** They are internal chunk IDs like
  `03-case-studies__adipven_is_expanding__p2` — meaningless and slightly
  alarming to a customer. If any provenance is shown at all, show a generic line
  like "Based on Adipven's published materials." Keep the raw IDs out of the DOM.
- **`requires_contact` / contact details:** when `requires_contact` is true, the
  `answer` text already contains the contact email and phone (pricing and
  can't-answer paths both redirect there). Rendering `answer` is enough; a nice
  touch is to linkify emails as `mailto:` and phone numbers as `tel:`. Don't
  fabricate or hardcode contact details in the frontend — let them come from the
  API response so there's one source of truth.
- **Keep `DEBUG_API` off in production** (already the default). The `debug` field
  will be `null`; never build UI that depends on it, and never enable it on the
  public deployment.

## Task 5 — abuse / cost exposure (flag, decide before going truly public)

The `/query` endpoint calls the Anthropic API on every request, which costs
money. A fully public, unauthenticated URL means anyone can drive that spend.
For an experiment shared with a few people this is tolerable; before wider
exposure, consider one of:

- a lightweight per-IP rate limit (e.g. a small in-process limiter),
- a shared access code checked server-side,
- or at minimum, awareness plus an Anthropic spend cap on the account.

This is out of scope to *implement* here, but the plan should not pretend the
risk doesn't exist. Decide consciously.

## Verification

Local first (`uvicorn api:app --port 8000`, open `http://localhost:8000/`):

- The chat page loads at `/`; `/docs`, `/health`, `/query` still work.
- A services question returns an answer that leads with services.
- A pricing question ("how much to file a trademark?") shows the refusal +
  contact redirect; no fabricated numbers.
- The ambiguous "bottle cap" question shows the clarifying question; typing a
  reply ("the shape of it") returns an industrial-design answer — i.e. the
  `pending` round-trip works end to end in the browser.
- An off-topic question shows the safe "I don't have that" redirect.
- No `source_ids` and no `reasoning` appear anywhere in the rendered page
  (check the DOM, not just the visible text).
- Confirm `cli.py` still runs (the `/` route change must not affect it).

Then on Render:

- Deploy, open the public URL in a real browser (and on a phone).
- Confirm the page renders and a real question round-trips.
- Note the cold-start delay on the first request after an idle period, so the
  loading UX is validated against real latency, not just local speed.

## Non-goals (do not do these unless separately asked)

- No React / Vue / Svelte / build tooling. Single static HTML file.
- No separate frontend host (keep it same-origin on FastAPI).
- No auth system, user accounts, or persisted chat history.
- No websockets or server-sent events; the API is request/response.
- No changes to `agent.py`, `grounding.py`, `retrieval.py`, `schema.py`, or the
  vector store. Presentation layer only.
- No new backend framework, Docker, or test-suite scaffold.

## Open decisions for the requester

1. **Branding:** any colours, logo, or firm styling to match adipven.com, or is
   a clean neutral look fine for now?
2. **Where it lives:** confirm same-origin on the existing service (recommended)
   vs. a separate frontend host (adds the CORS step).
3. **Access control:** leave it fully open for now (Task 5), or gate it behind a
   simple access code before sharing the URL?
