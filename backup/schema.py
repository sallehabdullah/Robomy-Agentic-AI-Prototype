"""
Structured input / output schema.

Field *descriptions* here are not documentation — they are serialised into
the tool schema sent to the model, so they are a prompt surface in their
own right and are worded as instructions.

Field *order* matters too. Structured-output generation fills fields in
declaration order, so `reasoning` is declared first: it acts as a scratchpad
the model must write before it commits to an `answer`.
"""

from typing import Literal

from pydantic import BaseModel, Field

ServiceArea = Literal[
    "patents",
    "trademarks",
    "industrial_design",
    "copyright",
    "geographical_indications",
    "licensing",
    "enforcement",
    "ip_audit_valuation",
    "training",
    "firm_info",
    "pricing",
    "out_of_scope",
]


class AdipvenQuery(BaseModel):
    """One turn of user input, plus any prior exchange."""

    query: str
    chat_history: list[str] = Field(default_factory=list)


class AdipvenResponse(BaseModel):
    """The model's structured reply.

    Declaration order is load-bearing — see module docstring.
    """

    reasoning: str = Field(
        description=(
            "Think here BEFORE writing the answer. Work through, briefly: "
            "(1) which retrieved chunk IDs, if any, actually address the "
            "question asked — not merely the same topic; "
            "(2) whether any part of the answer you intend to give is not "
            "stated in those chunks, in which case cut it; "
            "(3) whether the question touches cost, fees, quotes or "
            "timelines, which must never be answered; "
            "(4) whether the question is genuinely ambiguous across "
            "different IP rights, or is answerable as asked. "
            "This field is internal and is not shown to the customer."
        )
    )

    # Defaulted deliberately. The model intermittently omits the booleans,
    # which used to raise a ValidationError and take the whole turn down.
    # The defaults are the conservative reading: don't interrogate the
    # customer, and assume contact is warranted.
    needs_clarification: bool = Field(
        default=False,
        description=(
            "True ONLY when the question cannot be answered usefully without "
            "knowing which type of IP right the person means, AND the "
            "retrieved content would differ materially by that answer. "
            "Default to False. If the question is answerable as asked, "
            "answer it. Never set this on a question that is already "
            "specific, and never set it merely to gather more detail."
        )
    )

    clarifying_question: str | None = Field(
        default=None,
        description=(
            "Exactly one short question, asked only when "
            "needs_clarification is True; otherwise null. Offer the "
            "concrete alternatives in plain language rather than legal "
            "terms (e.g. 'the way it works, how it looks, or the brand "
            "name on it'). Never ask more than one thing."
        ),
    )

    # Defaulted for the same reason as the booleans above: the model
    # intermittently omits it, and a dropped turn is worse than an empty
    # one. An empty answer with can_answer=True is caught explicitly by the
    # grounding check, so this default cannot leak a blank reply.
    answer: str = Field(
        default="",
        description=(
            "The customer-facing reply. LEAD WITH THE DIRECT ANSWER in the "
            "first sentence. No preamble, no restating the question, no "
            "opening with general company background unless the question "
            "asked for background. For a 'what services' question, name the "
            "services first and describe the firm only afterwards, if at "
            "all. Every factual claim must be supported by a retrieved "
            "chunk listed in source_ids. Plain declarative prose, no sales "
            "voice. When using a chunk marked HISTORICAL, state the date "
            "rather than presenting it as current fact."
        )
    )

    service_area: ServiceArea = Field(
        default="out_of_scope",
        description="The IP service area the question falls under.",
    )

    can_answer: bool = Field(
        description=(
            "True only if the retrieved chunks actually answer the question "
            "asked. False if they are merely on the same topic, or if "
            "answering would require IP knowledge from outside the "
            "retrieved text."
        )
    )

    source_ids: list[str] = Field(
        default_factory=list,
        description=(
            "The exact chunk IDs, copied verbatim from the [id] labels in "
            "the retrieved content, that support the factual claims in "
            "`answer`. Do not invent, abbreviate or reformat an ID. These "
            "are checked against what was actually retrieved, and an ID "
            "that was not shown to you is treated as a grounding failure. "
            "Empty when can_answer is False."
        ),
    )

    requires_contact: bool = Field(
        default=True,
        description=(
            "True for any cost, fee, quote or timeline question, and true "
            "whenever can_answer is False."
        ),
    )
