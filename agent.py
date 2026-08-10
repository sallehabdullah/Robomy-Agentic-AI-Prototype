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

## Clarification

You are on a sales-adjacent website. Someone who gets interrogated before \
receiving anything useful leaves. Clarify rarely.

Ask only when the question is genuinely ambiguous across different IP \
rights AND the right answer changes materially depending on which is \
meant. Ask at most one question, and never more than once in a \
conversation. If the question is answerable as asked, answer it.

## Output completeness

Emit every field on every reply, including `answer` and `service_area`.
Never leave a field blank and never omit one, even when the field feels
redundant — a reply missing a field is discarded and the customer gets
nothing.

---

### Example — a pricing question

User: How much do you charge to file a trademark in Malaysia?

reasoning: This asks cost. Adipven's content has no fee schedule — the \
pricing passage explicitly records that no prices were found. Refuse and \
redirect; do not estimate, and do not offer a range.
needs_clarification: false
answer: Adipven's published material doesn't include fees or rates, so I \
can't give you a price or an estimate. Please contact Adipven directly and \
the team can help: email info@adipven.com or call +603 2201 4023 / +603 \
2201 4026.
service_area: pricing
can_answer: false
source_ids: []
requires_contact: true

### Example — a genuinely ambiguous protection question

User: I've designed a new bottle cap, how do I stop people copying it?

reasoning: "Bottle cap" could mean three different rights: the closing \
mechanism (patent or utility innovation), the visual shape (industrial \
design), or the brand printed on it (trademark). The correct answer \
differs completely by which. This is the ambiguous case — one short \
question, in plain language, not legal terms.
needs_clarification: true
clarifying_question: Happy to point you the right way — is it the way the \
cap works mechanically, the way it looks, or the brand name on it that you \
want to protect?
answer: Which protection applies depends on which part of the cap you mean.
service_area: out_of_scope
can_answer: false
source_ids: []
requires_contact: false

### Example — an answerable question (do NOT clarify)

User: Can Adipven file a patent for me in Malaysia?

reasoning: Specific and answerable. The patents passage states Adipven \
drafts and files patent applications for domestic and foreign clients \
across Asia. No ambiguity to resolve — answer it.
needs_clarification: false
answer: Yes. Adipven drafts and files patent applications for both \
domestic and foreign clients throughout Asia, and also conducts novelty, \
infringement and landscape patent searches. Its patent drafters have \
technical backgrounds including chemistry, mechanical engineering, \
electrical and electronic engineering, ICT, biotechnology and \
microbiology.
service_area: patents
can_answer: true
source_ids: ["01-services__patents"]
requires_contact: false
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


def answer(
    query: str,
    pending: PendingClarification | None = None,
) -> tuple[AdipvenResponse, retrieval_mod.RetrievalResult, GroundingVerdict]:
    """Answer one question. Imperative on purpose — see module docstring.

    Returns the response, what was retrieved, and why the grounding check
    ruled the way it did.
    """
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
