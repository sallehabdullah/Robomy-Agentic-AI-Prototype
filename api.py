"""
HTTP API — a second consumer of agent.answer(), beside cli.py.

Nothing about the agent, retrieval, or grounding changes here. This module
only does three jobs: load the model once at startup, translate HTTP <->
the existing (query, pending) -> (response, result, verdict) contract, and
keep `reasoning` off the wire unless a server-side debug flag is set.

Run locally:

    uvicorn api:app --port 8000

Render runs (see render.yaml):

    uvicorn api:app --host 0.0.0.0 --port $PORT
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import agent
import retrieval
from retrieval import VectorStoreUnavailable

log = logging.getLogger("api")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

# Off by default. Set DEBUG_API=1 in the environment to include `reasoning`
# and the grounding verdict in responses. Never flip this on for a public
# deployment — reasoning is explicitly marked internal in schema.py.
DEBUG_API = os.environ.get("DEBUG_API", "").lower() in ("1", "true", "yes")

# CORS: allow local dev origins only. This is a deliberate default, not an
# oversight — allow_origins=["*"] is NOT shipped here. Add the real frontend
# origin below when it exists.
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",   # Vite default
    "http://127.0.0.1:5173",
    # TODO: add the deployed frontend origin once it exists, e.g.
    # "https://adipven-frontend.example.com"
]

_startup_error: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the encoder and open the store once, before serving any request.

    If this fails, the process must not come up looking healthy — better to
    fail the deploy loudly than to start and 500 on every /query call. We
    store the error and let /health report 503 rather than raising here,
    because raising inside lifespan crashes uvicorn with a traceback that
    doesn't reach Render's log summary as cleanly as a clear log line does.
    """
    global _startup_error
    log.info("startup: loading retrieval model...")
    try:
        count = retrieval.warmup()
        log.info("startup: ready (%d chunks in store)", count)
    except VectorStoreUnavailable as exc:
        _startup_error = str(exc)
        log.error("startup FAILED — vector store unavailable: %s", exc)
    yield
    log.info("shutdown")


app = FastAPI(
    title="Adipven Assistant API",
    description="Grounded Q&A over Adipven's IP-services content store.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- request / response models ---------------------------------------------

class PendingIn(BaseModel):
    original_query: str
    clarifying_question: str


class QueryIn(BaseModel):
    query: str = Field(..., min_length=1)
    pending: PendingIn | None = None


class QueryOut(BaseModel):
    """Customer-facing subset of AdipvenResponse. No `reasoning` field."""

    answer: str
    service_area: str
    can_answer: bool
    requires_contact: bool
    needs_clarification: bool
    clarifying_question: str | None
    source_ids: list[str]
    # Populated only when DEBUG_API is set; None otherwise.
    debug: dict | None = None


# --- routes ------------------------------------------------------------------

@app.get("/health")
def health():
    """Render's health check. Must not trigger a model call.

    Reports the outcome of the startup warmup — a store that failed to
    load at startup is not going to start working later, so this stays 503
    for the life of the process rather than retrying on every poll.
    """
    if _startup_error is not None:
        raise HTTPException(
            status_code=503,
            detail="vector store unavailable at startup",
        )
    return {"status": "ok"}


@app.post("/query", response_model=QueryOut)
def query(body: QueryIn):
    if _startup_error is not None:
        # Startup never completed; every request would fail identically.
        raise HTTPException(
            status_code=503,
            detail="service did not start correctly (vector store unavailable)",
        )

    pending = (
        agent.PendingClarification(
            original_query=body.pending.original_query,
            clarifying_question=body.pending.clarifying_question,
        )
        if body.pending
        else None
    )

    try:
        response, result, verdict = agent.answer(body.query, pending)
    except VectorStoreUnavailable as exc:
        log.error("retrieval unavailable mid-request: %s", exc)
        raise HTTPException(status_code=503, detail="retrieval unavailable") from exc
    except agent.AgentError as exc:
        # Operational failure (bad key, network, rate limit). Log the detail
        # server-side; never put exception text or key material on the wire.
        log.error("agent call failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="the assistant is temporarily unavailable",
        ) from exc

    out = _to_out(response, result, verdict)
    return out


def _to_out(response, result, verdict) -> QueryOut:
    """Project the internal response onto the customer-facing wire model."""
    out = QueryOut(
        answer=response.answer,
        service_area=response.service_area,
        can_answer=response.can_answer,
        requires_contact=response.requires_contact,
        needs_clarification=response.needs_clarification,
        clarifying_question=response.clarifying_question,
        source_ids=response.source_ids,
    )
    if DEBUG_API:
        out.debug = {
            "reasoning": response.reasoning,
            "grounding_verdict": verdict.failure.value,
            "grounding_detail": verdict.detail,
            "chunks_retrieved": len(result.chunks),
            "chunks_considered": result.considered,
        }
    return out


@app.post("/query/stream")
def query_stream(body: QueryIn):
    """Server-sent events form of /query.

    Same contract, same grounding guarantees — see agent.answer_stream().
    Emits, one JSON object per SSE `data:` line:

        {"type": "delta",  "text": "..."}       answer fragment, append it
        {"type": "final",  ...QueryOut...,
                           "streamed": bool}    authoritative; render this
        {"type": "error",  "detail": "..."}     terminal

    `final` always arrives unless `error` does. Its `answer` is the
    authoritative text: a client should render it in place of whatever it
    accumulated from deltas, which makes the deltas a pure optimisation and
    keeps the grounding gate — not the network — the thing that decides
    what the customer ends up reading.

    Errors cannot use HTTP status codes once the body has started, so they
    are in-band. The status line is still 200 for a stream that fails
    mid-flight; clients must check for the `error` event, and must also
    treat a stream that ends without `final` as a failure.
    """
    if _startup_error is not None:
        raise HTTPException(
            status_code=503,
            detail="service did not start correctly (vector store unavailable)",
        )

    pending = (
        agent.PendingClarification(
            original_query=body.pending.original_query,
            clarifying_question=body.pending.clarifying_question,
        )
        if body.pending
        else None
    )

    def events():
        def sse(payload: dict) -> str:
            return f"data: {json.dumps(payload)}\n\n"

        try:
            for ev in agent.answer_stream(body.query, pending):
                if ev["type"] == "delta":
                    yield sse(ev)
                    continue
                out = _to_out(ev["response"], ev["retrieval"], ev["verdict"])
                yield sse({
                    "type": "final",
                    "streamed": ev["streamed"],
                    **out.model_dump(),
                })
        except VectorStoreUnavailable as exc:
            log.error("retrieval unavailable mid-request: %s", exc)
            yield sse({"type": "error", "detail": "retrieval unavailable"})
        except agent.AgentError as exc:
            # Same policy as /query: log the detail, put nothing on the wire.
            log.error("agent call failed: %s", exc)
            yield sse({
                "type": "error",
                "detail": "the assistant is temporarily unavailable",
            })

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # Render fronts the service with a proxy that will otherwise
            # buffer the whole body and defeat the point of streaming.
            "X-Accel-Buffering": "no",
        },
    )


# --- static chat frontend ---------------------------------------------------
# Mounted LAST and deliberately at "/": Starlette checks routes in
# registration order, so the explicit routes above (/health, /query, plus
# FastAPI's own /docs, /openapi.json) still win on an exact match. Anything
# that isn't one of those — starting with "/" itself — falls through to this
# mount, which serves static/index.html (html=True makes "/" resolve to it).
#
# Same-origin: the page's own fetch("/query") calls never touch CORS, since
# they're calling the same host that served the page. ALLOWED_ORIGINS above
# is still what a *different* origin (a separately hosted frontend) would
# need to be added to.
_STATIC_DIR = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="static")
