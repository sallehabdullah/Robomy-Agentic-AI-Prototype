"""
Agent — prompt, chain assembly, and the query pipeline.

On LCEL scope (deliberate, see the README section in the summary):

* The grounded-answer step IS a chain: `prompt | llm.with_structured_output(...)`.
  It is a clean linear transform of one dict into one validated object, which
  is exactly what the pipe operator is for.
* Retrieval-to-context IS composed into that chain as a RunnableLambda, since
  it is also a straight-line transform.
* `answer()` is NOT a chain. It contains conditional control flow (does this
  turn carry a pending clarification?) and a mandatory post-validation gate
  whose whole purpose is to be able to discard the chain's output. Expressing
  that as a runnable would hide the branch and make the guardrail look
  optional. It stays imperative on purpose.

If this grew a real multi-step loop — retrieve, critique, re-retrieve — the
right move would be a state graph, not a longer pipe. It has not grown one.
"""

from __future__ import annotations

import logging
import random
import re
from dataclasses import dataclass
from functools import lru_cache

from pydantic import ValidationError

import config
import grounding
import retrieval as retrieval_mod
from grounding import GroundingVerdict
from schema import AdipvenResponse

log = logging.getLogger(__name__)

# NOTE: langchain_core.prompts is NOT imported at module level. It pulls in
# langchain_core.output_parsers, which pulls in transformers — about 12
# seconds of import time. Everything heavy is imported inside the factories
# below, so importing this module stays cheap and testable.


SYSTEM_PROMPT = """\
You are Adipven's information assistant on their website. You answer \
questions from prospective clients about what Adipven does.

Adipven is an intellectual property firm in Malaysia working across Asia: \
patents, trademarks, industrial design, copyright, geographical \
indications, licensing, enforcement, IP audit and valuation, and IP \
training.

## Grounding

Every factual claim about Adipven must come from the retrieved passages \
below. You have no other source. Do not use general knowledge of IP law, \
of Malaysian procedure, or of Adipven, even where you are confident and \
even where it would be helpful.

The retrieved passages being *about the same topic* as the question is not \
the same as their *answering* it. If someone asks how long a Malaysian \
patent lasts and the passages are Malaysian patent case summaries, the \
passages do not answer the question. Say you don't have that information.

Cite the exact chunk IDs you used, copied from the [id] labels. They are \
checked against what was actually retrieved.

Note the field order: you commit to `can_answer` and to `source_ids` \
*before* you write `answer`. Decide what the passages support, list those \
chunk IDs, then write the answer from exactly those chunks and nothing \
else. Do not list an ID you end up not using, and do not write a claim \
that came from a chunk you did not list.

Passages tagged HISTORICAL describe a past event. A 2017 announcement \
giving an office address is evidence of the address in 2017, not of the \
address now. If you use one, say when it was from.

## Never quote fees

Never state, estimate, imply or bracket a price, fee, rate, cost or \
turnaround time — not even a range, not even "it depends". Adipven's \
published material contains no fee information. Cost and timeline \
questions are redirected to the contact channel, always.

## Answer shape

Lead with the direct answer in the first sentence. Do not restate the \
question. Do not open with company background unless background is what \
was asked for. Asked what services Adipven offers, name the services \
first. Plain declarative prose, no sales voice, no "we would be delighted".

## Formatting

Structure the answer so it can be skimmed. When you are enumerating more \
than about three things — service areas, jurisdictions, documents to \
prepare, steps in a process — put each on its own line as a list rather \
than running them together in one paragraph. Number them where order or \
count matters, use hyphens where it does not. Lead in with a short \
sentence, and keep each item to a line or two.

Write lists as plain text. The chat window shows the characters you emit \
exactly as they are, so markdown is not rendered — asterisks, backticks \
and "##" appear on screen as themselves. Use line breaks, "1." and "- ", \
nothing else.

Short answers stay as prose. Two or three items, or one continuous \
explanation, do not need a list. Do not impose structure on an answer that \
reads fine without it.

## Questions with more than one part

One message can carry several requests: two questions, or a question \
alongside something you cannot provide. Take each part on its own merits. \
A part you cannot answer must never suppress a part you can — answering \
what you can is not weakened by declining the rest.

Identify the parts, answer each one the passages support, and decline the \
others explicitly in the same reply so the person can see which is which. \
Set can_answer=true when at least one part is answered, and cite \
source_ids for those parts only. Set requires_contact=true when a declined \
part is something Adipven's team could take up directly.

Do not answer a declined part from general knowledge to make the reply \
tidier, and do not drop a supported claim because another part failed.

## Clarification

You are on a sales-adjacent website. Someone who gets interrogated before \
receiving anything useful leaves. Clarify rarely.

Ask only when the question is genuinely ambiguous across different IP \
rights AND the right answer changes materially depending on which is \
meant. Ask at most one question, and never more than once in a \
conversation. If the question is answerable as asked, answer it.

## Greetings and small talk

Not every message is a question. A greeting ("hi", "hello"), a thanks, a \
question about what you can help with, or a clearly off-topic message \
(recipes, the weather) is conversational: it makes no factual claim and \
needs no sources. Set conversational=true and can_answer=false.

Write a short, warm reply (one or two sentences) that acknowledges what \
the person said and steers toward Adipven's services. Vary your phrasing — \
do not repeat the same greeting formula across turns. Do not push contact \
details at someone who only said hello. Do not make factual claims about \
Adipven beyond naming the service areas listed at the top of this prompt.

Mind the boundary: a real factual question you cannot answer from the \
passages is NOT small talk. "How long does a Malaysian patent last?" is a \
genuine question the passages don't cover — leave conversational=false and \
can_answer=false, so it is handled as "I don't have that; contact Adipven." \
Never label a factual question conversational just to avoid answering it.

## The reasoning field

`reasoning` is a scratchpad, not a document. Notes and fragments, around \
50 words, covering only the checks actually in play. Close it with an \
explicit verdict: which chunk IDs you will cite, and whether you can \
answer. The customer never sees this field, and every word in it is time \
they spend waiting for the answer they do see.

Think as hard as the question needs; just stop writing it down at length. \
Brevity here is about how much you write, never about how much you check — \
a terse note that ends "answerable, cite X" is right, and skipping the \
verdict and defaulting to "can't answer" is the one failure this must not \
produce.

## Output completeness

Emit every field on every reply, including `answer` and `service_area`.
Never leave a field blank and never omit one, even when the field feels
redundant — a reply missing a field is discarded and the customer gets
nothing.

---

### Example — a pricing question

User: How much do you charge to file a trademark in Malaysia?

reasoning: Cost question. No fee data in store. Verdict: no IDs, not \
answerable — refuse + redirect, no estimate or range.
needs_clarification: false
service_area: pricing
can_answer: false
source_ids: []
requires_contact: true
answer: Adipven's published material doesn't include fees or rates, so I \
can't give you a price or an estimate. Please contact Adipven directly and \
the team can help: email info@adipven.com or call +603 2201 4023 / +603 \
2201 4026.

### Example — a genuinely ambiguous protection question

User: I've designed a new bottle cap, how do I stop people copying it?

reasoning: Cap = mechanism (patent) / shape (design) / brand (trademark). \
Answer differs by which. Verdict: genuinely ambiguous, no IDs yet — ask \
one plain-language question.
needs_clarification: true
clarifying_question: Happy to point you the right way — is it the way the \
cap works mechanically, the way it looks, or the brand name on it that you \
want to protect?
service_area: out_of_scope
can_answer: false
source_ids: []
requires_contact: false
answer: Which protection applies depends on which part of the cap you mean.

### Example — an answerable question (do NOT clarify)

User: Can Adipven file a patent for me in Malaysia?

reasoning: 01-services__patents: drafts + files across Asia, plus \
searches. No ambiguity. Verdict: cite 01-services__patents, answerable.
needs_clarification: false
service_area: patents
can_answer: true
source_ids: ["01-services__patents"]
requires_contact: false
answer: Yes. Adipven drafts and files patent applications for both \
domestic and foreign clients throughout Asia, and also conducts novelty, \
infringement and landscape patent searches. Its patent drafters have \
technical backgrounds including chemistry, mechanical engineering, \
electrical and electronic engineering, ICT, biotechnology and \
microbiology.

### Example — two requests, one answerable and one not

User: Give me more specifics on patents. Also, who would you recommend to \
represent me?

reasoning: Two parts. (1) patent specifics — 01-services__patents covers \
it. (2) personal referral — not in passages. Verdict: cite \
01-services__patents, answerable in part — answer 1, decline 2, redirect.
needs_clarification: false
service_area: patents
can_answer: true
source_ids: ["01-services__patents"]
requires_contact: true
answer: On patents, Adipven covers three things:

1. Drafting and filing patent applications for domestic and foreign \
clients across Asia.
2. Novelty, infringement and landscape patent searches.
3. Drafters with technical backgrounds spanning chemistry, mechanical \
engineering, electrical and electronic engineering, ICT, biotechnology and \
microbiology.

On who should represent you — I can't make that recommendation, as \
Adipven's published material doesn't cover individual assignments. The \
team can advise on that directly: email info@adipven.com or call +603 2201 \
4023 / +603 2201 4026.

### Example — a greeting (warm steer, NOT a contact redirect)

User: Hello

reasoning: A greeting, not a question. Conversational; no sources needed.
conversational: true
needs_clarification: false
service_area: out_of_scope
can_answer: false
source_ids: []
requires_contact: false
answer: Hi there! Happy to help with anything about Adipven's IP work — \
patents, trademarks, industrial design, and more. What brings you here?

### Example — small talk that is NOT a greeting (still conversational)

User: How are you?

reasoning: Small talk, not an info request. Conversational; acknowledge + \
steer.
conversational: true
needs_clarification: false
service_area: out_of_scope
can_answer: false
source_ids: []
requires_contact: false
answer: Doing well, thanks for asking! I'm here whenever you have a \
question about Adipven's IP services — patents, trademarks, and the rest.
"""


USER_TEMPLATE = """\
{history_block}Retrieved passages:

{context}

---

Customer question: {query}
"""


@lru_cache(maxsize=1)
def get_llm():
    """Build the chat model. Lazy — importing this module must stay cheap."""
    from dotenv import load_dotenv
    from langchain_anthropic import ChatAnthropic

    load_dotenv()  # ANTHROPIC_API_KEY; never read or logged by this code
    log.debug("initialising %s", config.GENERATION_MODEL)
    return ChatAnthropic(
        model=config.GENERATION_MODEL,
        temperature=config.GENERATION_TEMPERATURE,
        max_tokens=config.GENERATION_MAX_TOKENS,
    )


@dataclass(frozen=True)
class PendingClarification:
    """A clarifying question awaiting the customer's reply.

    Held as structured data rather than transcript strings because the
    original question is needed for two different jobs: rebuilding the
    prompt, and rebuilding the *retrieval query*. A reply like "the shape
    of it, how it looks" retrieves nothing on its own — it has no IP terms
    in it — so searching on the follow-up alone fails closed on a question
    the store can actually answer.
    """

    original_query: str
    clarifying_question: str

    def retrieval_queries(self, reply: str) -> list[str]:
        """Search on both, unioned — not concatenated.

        Concatenating dilutes: the combined embedding of the original
        question and a short reply scored *worse* than either alone
        (0.209 vs 0.276) because the two pull in different directions.
        """
        return [self.original_query, reply, f"{self.original_query} {reply}"]

    def history_block(self) -> str:
        return (
            "Earlier in this conversation:\n"
            f"Customer asked: {self.original_query}\n"
            f"You asked back: {self.clarifying_question}\n\n"
            "The customer is now replying to that clarifying question. "
            "Answer their original request in light of this reply. Do not "
            "ask for clarification again.\n\n"
        )


@lru_cache(maxsize=1)
def get_chain():
    """The grounded-answer chain.

    dict(query, history) -> retrieve -> format -> prompt -> structured output
    """
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_TEMPLATE),
    ])

    structured = get_llm().with_structured_output(AdipvenResponse)

    return (
        RunnablePassthrough.assign(
            context=RunnableLambda(
                lambda x: retrieval_mod.format_context(x["retrieval"])
            ),
            history_block=RunnableLambda(
                lambda x: x["pending"].history_block() if x.get("pending") else ""
            ),
        )
        | prompt
        | structured
    )


class AgentError(RuntimeError):
    """Generation failed for an operational reason the operator must see."""


def _fail_closed(
    result: retrieval_mod.RetrievalResult, detail: str
) -> tuple[AdipvenResponse, retrieval_mod.RetrievalResult, GroundingVerdict]:
    """Produce a refusal for a turn that never yielded a usable response."""
    stub = AdipvenResponse(
        reasoning=detail,
        answer="",
        service_area="out_of_scope",
        can_answer=False,
        source_ids=[],
    )
    verdict = GroundingVerdict(grounding.Failure.CLAIMS_WITHOUT_SOURCES, detail)
    return grounding.refusal_for(verdict, stub), result, verdict


def _trivial_category(query: str) -> str | None:
    """Whole-message greeting/pleasantry that needs no model call at all.

    Exact match on the normalised message only, so "hi" short-circuits but
    "hi, do you file patents?" does not — that still goes to the model.
    Returns the category name (a key into config.CONVERSATIONAL_POOLS) so
    the fast path can vary its reply instead of returning the same string
    every time, or None if the message isn't an exact trivial match.
    """
    normalised = " ".join(re.sub(r"[^\w\s]", " ", query).lower().split())
    for category, messages in config.TRIVIAL_CATEGORIES.items():
        if normalised in messages:
            return category
    return None


def answer(
    query: str,
    pending: PendingClarification | None = None,
) -> tuple[AdipvenResponse, retrieval_mod.RetrievalResult, GroundingVerdict]:
    """Answer one question. Imperative on purpose — see module docstring.

    Returns the response, what was retrieved, and why the grounding check
    ruled the way it did.
    """
    # Fast path: a bare greeting or thanks (and no clarification in flight)
    # is answered in code — no retrieval, no API call. This is both the fix
    # for "hello" cold-redirecting to contact, and the biggest latency win
    # available here: an instant, free reply instead of a ~10-26s round trip.
    #
    # Category-based, not a single fixed string: three different exact
    # greetings ("hi", "hello", "hey") each get a random pick from the
    # matching pool, so the fast path doesn't repeat itself even though it
    # never touches the model. See config.CONVERSATIONAL_POOLS.
    category = _trivial_category(query) if pending is None else None
    if category is not None:
        text = random.choice(config.CONVERSATIONAL_POOLS[category])
        verdict = GroundingVerdict(
            grounding.Failure.CONVERSATIONAL,
            f"trivial {category} (no model call)",
        )
        empty = retrieval_mod.RetrievalResult(query=query, considered=0)
        return grounding.conversational_reply(text, verdict.detail), empty, verdict

    # Retrieval is unconditional: this agent has exactly one job and every
    # question needs the store. The old code let the model decide whether to
    # search, which spent a round trip to reach a foregone conclusion.
    #
    # When answering a clarification reply, search on the original question
    # combined with the reply — the reply alone is usually too thin to match.
    search = pending.retrieval_queries(query) if pending else query
    result = retrieval_mod.retrieve(search)

    try:
        response: AdipvenResponse = get_chain().invoke({
            "query": query,
            "pending": pending,
            "retrieval": result,
        })
    except ValidationError as exc:
        # A malformed structured response is an uncertainty path like any
        # other, and the policy says those resolve to silence-plus-redirect
        # rather than to an error the customer sees.
        log.warning("model returned an unparseable response: %s", exc)
        return _fail_closed(result, f"response failed schema validation: {exc}")
    except Exception as exc:  # noqa: BLE001
        # Operational failures (bad key, network, rate limit) are the
        # operator's problem, not the customer's — surface them loudly.
        raise AgentError(
            f"The language model call failed: {exc}\n"
            "Check ANTHROPIC_API_KEY is set in .env and that the network is up."
        ) from exc

    # Nothing above this line is trusted. The gate is the only thing that
    # can declare a response safe to show.
    checked, verdict = grounding.enforce(query, response, result)
    return checked, result, verdict


# --- streaming ---------------------------------------------------------------
#
# answer() above stays the canonical path: cli.py and eval.py use it, and it
# is the reference the streaming path is checked against. answer_stream()
# below produces the *same* final result — it only emits the answer text
# earlier, and only when doing so cannot be retracted.
#
# The safety argument, in one line: `answer` is the last field in the schema,
# so by the time its first character exists every grounding-gate input is
# final, and grounding.check_prestream() has already ruled. Nothing is
# emitted before that ruling.
#
# Measured on this content store: `reasoning` takes the bulk of generation
# (~7s of ~16s locally), so the customer still waits for the model to think.
# Streaming removes the answer-writing wait, not the reasoning wait.


def answer_stream(query: str, pending: PendingClarification | None = None):
    """Generator form of answer(). Yields, in order:

        {"type": "status", "stage": str}
            Progress marker for the pre-answer wait. `stage` is a key into
            config.STATUS_MESSAGES; the text is code-authored and constant,
            never model output, so this event carries no grounding surface.
            Purely presentational — a consumer may ignore it entirely.

        {"type": "delta", "text": str}
            A fragment of the customer-facing answer that has already
            passed the grounding gate. Append it verbatim.

        {"type": "final", "response": AdipvenResponse,
         "retrieval": RetrievalResult, "verdict": GroundingVerdict,
         "streamed": bool}
            Exactly once, last. `response` is authoritative and equals what
            answer() would have returned. `streamed` says whether any delta
            was emitted, so a consumer can tell "append finished" from
            "nothing was streamed, render this now".

    Deltas are an optimisation, never the source of truth: a consumer that
    ignores them entirely and renders only `final` is still correct.
    """
    # Same fast path as answer(). No model call, so nothing to stream — the
    # reply is already complete before the first byte would have gone out.
    category = _trivial_category(query) if pending is None else None
    if category is not None:
        text = random.choice(config.CONVERSATIONAL_POOLS[category])
        verdict = GroundingVerdict(
            grounding.Failure.CONVERSATIONAL,
            f"trivial {category} (no model call)",
        )
        empty = retrieval_mod.RetrievalResult(query=query, considered=0)
        yield {
            "type": "final",
            "response": grounding.conversational_reply(text, verdict.detail),
            "retrieval": empty,
            "verdict": verdict,
            "streamed": False,
        }
        return

    # Status events bracket the two phases the customer would otherwise
    # experience as undifferentiated dead air. Emitted before the work they
    # describe, so each one reaches the client while that phase is running.
    yield {"type": "status", "stage": "retrieving"}

    search = pending.retrieval_queries(query) if pending else query
    result = retrieval_mod.retrieve(search)

    # Retrieval is fast (~0.08s locally); essentially the whole wait is the
    # model generating `reasoning` before it may write `answer`.
    yield {"type": "status", "stage": "composing"}

    latest: AdipvenResponse | None = None
    gated = False        # has check_prestream run for this turn?
    may_stream = False   # ...and did it clear the answer for streaming?
    sent = 0             # characters already emitted

    try:
        for partial in get_chain().stream({
            "query": query,
            "pending": pending,
            "retrieval": result,
        }):
            latest = partial

            if not gated:
                # Wait for the first character of `answer`. Its existence is
                # the signal that every earlier field — including source_ids
                # and can_answer — has finished parsing.
                if not partial.answer:
                    continue
                _, may_stream = grounding.check_prestream(query, partial, result)
                gated = True

            if may_stream and len(partial.answer) > sent:
                yield {"type": "delta", "text": partial.answer[sent:]}
                sent = len(partial.answer)

    except ValidationError as exc:
        log.warning("model returned an unparseable response: %s", exc)
        response, res, verdict = _fail_closed(
            result, f"response failed schema validation: {exc}"
        )
        yield _final(response, res, verdict, streamed=sent > 0, query=query)
        return
    except Exception as exc:  # noqa: BLE001
        raise AgentError(
            f"The language model call failed: {exc}\n"
            "Check ANTHROPIC_API_KEY is set in .env and that the network is up."
        ) from exc

    if latest is None:
        # The stream produced nothing at all. Treat it like any other
        # uncertainty path rather than returning an empty turn.
        response, res, verdict = _fail_closed(result, "stream yielded no output")
        yield _final(response, res, verdict, streamed=False, query=query)
        return

    # The full gate runs on the completed response regardless of what was
    # streamed. This is the same call answer() makes, so the two paths cannot
    # disagree about the final result.
    checked, verdict = grounding.enforce(query, latest, result)
    yield _final(checked, result, verdict, streamed=sent > 0, query=query)


def _final(response, result, verdict, *, streamed: bool, query: str) -> dict:
    """Build the terminal event, and refuse to let the two paths diverge.

    If text was streamed, check_prestream() promised the gate would pass.
    Should that promise ever be broken, the customer has already seen text
    the gate later rejected — the exact failure this design exists to
    prevent. It cannot be un-sent, so it is logged at CRITICAL and the
    authoritative `response` in this event still carries the refusal, which
    a conforming consumer renders in place of the streamed text.
    """
    if streamed and not verdict.ok:
        log.critical(
            "STREAMED TEXT FAILED THE FINAL GATE (%s: %s) for query %r — "
            "check_prestream() and check() disagreed; this is a bug in the "
            "streaming gate, not a model failure",
            verdict.failure.value, verdict.detail, query,
        )
    return {
        "type": "final",
        "response": response,
        "retrieval": result,
        "verdict": verdict,
        "streamed": streamed,
    }
