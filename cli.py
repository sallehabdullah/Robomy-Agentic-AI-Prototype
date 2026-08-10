"""
CLI entry point.

    python cli.py                 interactive
    python cli.py --debug         show reasoning, retrieval scores, verdict
    python cli.py -q "question"   one-shot

`print` is used here and only here — this is the user-facing surface.
Everything else logs.
"""

from __future__ import annotations

import argparse
import logging
import sys

import agent
import config
import retrieval
from retrieval import RetrievalResult, VectorStoreUnavailable
from schema import AdipvenResponse


def _print_debug(result: RetrievalResult, response: AdipvenResponse, verdict) -> None:
    print("\n  ┌─ retrieval " + "─" * 58)
    print(f"  │ {result.considered} candidates, {len(result.chunks)} above "
          f"threshold {config.RELEVANCE_THRESHOLD}, "
          f"{result.dropped_below_threshold} dropped")
    for c in result.chunks:
        tag = "HIST" if c.is_historical else "    "
        boost = "+" if c.section_type in config.BOOSTED_SECTION_TYPES else " "
        print(f"  │  {c.score:.3f}{boost} {tag}  [{c.section_type}] {c.id}")
    if not result.chunks:
        raw = result.best_raw_score
        shown = f"{raw:.3f}" if raw is not None else "n/a"
        print(f"  │  (nothing survived the off-topic gate; best raw score {shown})")

    print("  ├─ reasoning " + "─" * 58)
    for line in response.reasoning.splitlines():
        print(f"  │ {line}")

    print("  ├─ grounding " + "─" * 58)
    status = "PASS" if verdict.ok else f"FAIL — {verdict.failure.value}"
    print(f"  │ {status}")
    if verdict.detail:
        print(f"  │ {verdict.detail}")
    print("  └" + "─" * 70)


def _print_response(response: AdipvenResponse) -> None:
    if response.needs_clarification and response.clarifying_question:
        print(f"\nAgent: {response.clarifying_question}")
    else:
        print(f"\nAgent: {response.answer}")

    bits = [
        f"service_area={response.service_area}",
        f"can_answer={response.can_answer}",
        f"requires_contact={response.requires_contact}",
    ]
    if response.needs_clarification:
        bits.append("needs_clarification=True")
    if response.source_ids:
        bits.append(f"sources={response.source_ids}")
    print(f"  [{', '.join(bits)}]")


def run_once(
    query: str,
    pending,
    debug: bool,
    consecutive_conversational: int = 0,
) -> tuple[AdipvenResponse, int]:
    """Answer one turn, and return the count of consecutive conversational
    turns seen so far (for the caller to pass back in next time).

    Escalation on the 3rd consecutive conversational turn (greeting, thanks,
    small talk, off-topic — see schema.AdipvenResponse.conversational) is
    CLI-only session state, not part of the agent itself: the API is
    stateless, so this can't live in agent.answer() without either adding
    server-side session tracking (out of scope) or pushing the count through
    every HTTP request (awkward for a nice-to-have). Kept here as a
    presentation-layer override — the underlying `response` returned to the
    caller (e.g. for `pending` tracking) is untouched; only what's printed
    changes on escalation.
    """
    response, result, verdict = agent.answer(query, pending)

    display = response
    new_count = 0
    if response.conversational:
        new_count = consecutive_conversational + 1
        if new_count >= 3:
            display = response.model_copy(
                update={"answer": config.CONVERSATIONAL_ESCALATION}
            )
            new_count = 0  # fires again after another 3, not on every turn after

    if debug:
        _print_debug(result, display, verdict)
    _print_response(display)
    return response, new_count


def main() -> int:
    ap = argparse.ArgumentParser(description="Adipven information assistant")
    ap.add_argument("-q", "--query", help="answer one question and exit")
    ap.add_argument("--debug", action="store_true",
                    help="show reasoning, retrieval scores and grounding verdict")
    ap.add_argument("-v", "--verbose", action="store_true", help="log at DEBUG")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )

    # Load the encoder and open the store now rather than on the first
    # question. It is ~30 seconds either way, but here the user is expecting
    # startup cost instead of a stalled-looking prompt.
    # Status goes to stderr so `-q` output stays clean when piped.
    print("Loading retrieval model...", end=" ", flush=True, file=sys.stderr)
    try:
        chunk_count = retrieval.warmup()
    except VectorStoreUnavailable as exc:
        print("failed.", file=sys.stderr)
        print(f"\nCannot start: {exc}", file=sys.stderr)
        return 2
    print(f"ready ({chunk_count} chunks).", file=sys.stderr)

    try:
        if args.query:
            run_once(args.query, None, args.debug)  # single turn, no escalation state
            return 0
    except VectorStoreUnavailable as exc:
        print(f"\nCannot start: {exc}", file=sys.stderr)
        return 2
    except agent.AgentError as exc:
        print(f"\n{exc}", file=sys.stderr)
        return 1

    print("\nAdipven assistant — ask a question, or 'quit' to exit.")
    if args.debug:
        print("(debug mode: reasoning and retrieval shown)")

    # Only a pending clarification is carried forward. Once the follow-up is
    # answered it is cleared, so the agent does not accumulate an unbounded
    # transcript across unrelated questions.
    pending: agent.PendingClarification | None = None

    # See run_once() — CLI-only session state for the conversational-
    # escalation nice-to-have (Task 4). Any substantive turn resets it.
    consecutive_conversational = 0

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if user_input.lower() in ("quit", "exit"):
            return 0
        if not user_input:
            continue

        try:
            response, consecutive_conversational = run_once(
                user_input, pending, args.debug, consecutive_conversational
            )
        except VectorStoreUnavailable as exc:
            print(f"\nRetrieval unavailable: {exc}", file=sys.stderr)
            return 2
        except agent.AgentError as exc:
            print(f"\n{exc}", file=sys.stderr)
            continue

        if response.needs_clarification and response.clarifying_question:
            pending = agent.PendingClarification(
                original_query=user_input,
                clarifying_question=response.clarifying_question,
            )
        else:
            pending = None


if __name__ == "__main__":
    raise SystemExit(main())
