"""
Fail-closed grounding enforcement.

This is the one place a response is allowed to be declared safe. The model
is *asked* to stay grounded by the prompt and the schema descriptions; only
this module *enforces* it.

Policy (from the brief): an ungrounded claim about IP protection is a
materially worse outcome than a dead-end response, so every uncertainty
path resolves to silence-plus-redirect, never to a hedged guess.

A grounding failure is any of:

  1. reported `source_ids` not matching the chunk IDs actually retrieved
  2. all retrieved chunks falling below the relevance threshold
  3. retrieval returning nothing at all
  4. the model producing factual content with `source_ids` empty

On any of these the response is replaced wholesale — not patched, not
softened. There is no partial-answer path.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum

import config
from retrieval import RetrievalResult
from schema import AdipvenResponse

log = logging.getLogger(__name__)


class Failure(str, Enum):
    NONE = "none"
    NO_RETRIEVAL = "retrieval_returned_nothing"
    ALL_BELOW_THRESHOLD = "all_chunks_below_relevance_threshold"
    FABRICATED_SOURCE_IDS = "reported_source_ids_not_in_retrieved_set"
    CLAIMS_WITHOUT_SOURCES = "factual_content_with_no_source_ids"
    EMPTY_ANSWER = "claimed_to_answer_but_answer_was_empty"
    PRICING = "pricing_question"
    # Not a defect: the model itself judged the passages insufficient. The
    # response is still replaced, so the wording of a refusal is always the
    # canonical one rather than whatever the model improvised — but keeping
    # it distinct means --debug can tell a correct decline apart from a
    # fabrication.
    MODEL_DECLINED = "model_reported_it_cannot_answer"
    # Also not a defect: a greeting, thanks, or off-topic message that makes
    # no factual claim. Gets a warm steer toward Adipven instead of a contact
    # redirect. Like the others, the reply text is code-authored, so even a
    # mislabelled turn cannot smuggle an ungrounded claim through here.
    CONVERSATIONAL = "conversational_neutral"


@dataclass(frozen=True)
class GroundingVerdict:
    """Why a response was replaced, for logging and --debug output."""

    failure: Failure
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.failure is Failure.NONE


# A response that answers nothing needs no citations. Anything longer than
# this, with no verified sources, is treated as factual content.
_TRIVIAL_ANSWER_CHARS = 40


# Fee vocabulary, matched on word boundaries.
#
# This was originally a list of substrings tested with `t in query`, which
# was badly wrong in both directions. "rate" matched accelerate, corporate,
# operate, cooperate, collaborate, incorporate and separate; "fee" matched
# feedback and coffee. Because the pricing check runs first and replaces the
# response outright, "Can you accelerate my patent filing?" was answered
# with "we don't quote fees" — a nonsense refusal to an answerable question,
# and the exact opposite of the recall-favouring posture everywhere else.
_PRICING_RE = re.compile(
    r"\bhow much\b"
    r"|\b(?:"
    r"price|prices|priced|pricing"
    r"|cost|costs|costly"
    r"|fee|fees"
    r"|charge|charges|chargeable"
    r"|quote|quotes|quotation|quotations"
    r"|rate|rates|tariff|tariffs"
    r"|retainer|upfront"
    r"|invoice|invoices|invoiced|bill|billed|billing"
    r"|expensive|inexpensive|cheap|cheaper|affordable|afford"
    r"|budget|discount|discounts"
    r"|payment|payments"
    r"|estimate|estimates"
    r")\b",
    re.IGNORECASE,
)

# "rate" is a real word outside fee contexts, so word boundaries alone are
# not enough — "what is your success rate?" is not a pricing question. These
# spans are removed before the fee pattern is applied, so a query asking
# about both still matches on the fee half.
_NOT_PRICING_RE = re.compile(
    r"\b(?:success|approval|grant|granting|rejection|refusal|failure|win"
    r"|conversion|exchange|growth|response|renewal|turnover)\s+rates?\b"
    r"|\bat any rate\b"
    r"|\bfirst[- ]rate\b",
    re.IGNORECASE,
)


def _is_pricing(query: str, response: AdipvenResponse) -> bool:
    """Pricing is decided in code, not left to the model's judgement."""
    if response.service_area == "pricing":
        return True
    cleaned = _NOT_PRICING_RE.sub(" ", query)
    return bool(_PRICING_RE.search(cleaned))


def check(
    query: str,
    response: AdipvenResponse,
    retrieval: RetrievalResult,
) -> GroundingVerdict:
    """Decide whether `response` may be shown to the customer as-is."""
    if _is_pricing(query, response):
        return GroundingVerdict(Failure.PRICING, "query mentions cost/fees")

    # A greeting / thanks / off-topic message makes no factual claim, so it
    # must NOT fall through to the fail-closed retrieval checks below (which
    # would cold-redirect "hello" to the contact page). Handled before them,
    # and only when the model is not also claiming to answer a question.
    if response.conversational and not response.can_answer:
        return GroundingVerdict(
            Failure.CONVERSATIONAL, "greeting / small talk / off-topic"
        )

    # Clarification requests make no factual claims, so they are exempt from
    # the citation rules — but only if a question was actually supplied.
    if response.needs_clarification and response.clarifying_question:
        return GroundingVerdict(Failure.NONE)

    if retrieval.considered == 0:
        return GroundingVerdict(Failure.NO_RETRIEVAL, "retriever returned 0 candidates")

    if retrieval.is_empty:
        best = retrieval.best_score
        best_txt = f"{best:.3f}" if best is not None else "n/a"
        return GroundingVerdict(
            Failure.ALL_BELOW_THRESHOLD,
            f"{retrieval.dropped_below_threshold} candidate(s) all scored below "
            f"{config.RELEVANCE_THRESHOLD}; best was {best_txt}",
        )

    reported = set(response.source_ids)
    actual = retrieval.chunk_ids
    fabricated = reported - actual

    if fabricated:
        return GroundingVerdict(
            Failure.FABRICATED_SOURCE_IDS,
            f"not in retrieved set: {sorted(fabricated)}",
        )

    # A self-reported refusal is taken at face value and always resolves to
    # the canonical redirect, whether or not it cited anything.
    if not response.can_answer:
        return GroundingVerdict(
            Failure.MODEL_DECLINED,
            f"cited {len(reported & actual)} source(s)" if reported else "no sources cited",
        )

    # `answer` is defaulted in the schema so a dropped field cannot take the
    # turn down. That makes an empty answer reachable, so it is rejected
    # here rather than shown to the customer as a blank reply.
    if not response.answer.strip():
        return GroundingVerdict(
            Failure.EMPTY_ANSWER, "can_answer=True but answer was empty"
        )

    verified = reported & actual
    if not verified and len(response.answer.strip()) > _TRIVIAL_ANSWER_CHARS:
        return GroundingVerdict(
            Failure.CLAIMS_WITHOUT_SOURCES,
            f"answer is {len(response.answer)} chars with no verified sources",
        )

    return GroundingVerdict(Failure.NONE)


def conversational_reply(detail: str = "", original_reasoning: str = "") -> AdipvenResponse:
    """A warm, code-authored steer toward Adipven for a non-factual turn.

    Reply text comes from config, never the model, so this path cannot emit
    an ungrounded claim no matter how the turn was classified.
    """
    note = "[conversational/neutral turn: " + (detail or "small talk") + "]"
    if original_reasoning:
        note += f"\n\nModel's original reasoning:\n{original_reasoning}"
    return AdipvenResponse(
        reasoning=note,
        conversational=True,
        needs_clarification=False,
        clarifying_question=None,
        answer=config.CONVERSATIONAL_ANSWER,
        service_area="out_of_scope",
        can_answer=False,
        source_ids=[],
        requires_contact=False,
    )


def refusal_for(verdict: GroundingVerdict, original: AdipvenResponse) -> AdipvenResponse:
    """Build the replacement response for a failed check.

    Constructs a new object rather than mutating the validated one, so the
    model's original output stays intact for debugging.
    """
    if verdict.failure is Failure.CONVERSATIONAL:
        return conversational_reply(verdict.detail, original.reasoning)

    if verdict.failure is Failure.PRICING:
        answer = config.PRICING_ANSWER
        area = "pricing"
    else:
        answer = config.NO_INFO_ANSWER
        area = original.service_area if original.service_area != "pricing" else "out_of_scope"

    return AdipvenResponse(
        reasoning=(
            f"[replaced by grounding check: {verdict.failure.value}"
            + (f" — {verdict.detail}" if verdict.detail else "")
            + f"]\n\nModel's original reasoning:\n{original.reasoning}"
        ),
        needs_clarification=False,
        clarifying_question=None,
        answer=answer,
        service_area=area,
        can_answer=False,
        source_ids=[],
        requires_contact=True,
    )


def enforce(
    query: str,
    response: AdipvenResponse,
    retrieval: RetrievalResult,
) -> tuple[AdipvenResponse, GroundingVerdict]:
    """Single entry point: check, and replace the response if it fails."""
    verdict = check(query, response, retrieval)
    if verdict.ok:
        # Trim citations to the verified subset so downstream consumers
        # never see an ID the retriever did not produce.
        verified = [i for i in response.source_ids if i in retrieval.chunk_ids]
        if verified != response.source_ids:
            response = response.model_copy(update={"source_ids": verified})
        return response, verdict

    log.warning("grounding failure (%s): %s", verdict.failure.value, verdict.detail)
    return refusal_for(verdict, response), verdict
