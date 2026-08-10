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


def run_once(query: str, pending, debug: bool) -> AdipvenResponse:
    response, result, verdict = agent.answer(query, pending)
    if debug:
        _print_debug(result, response, verdict)
    _print_response(response)
    return response


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
            run_once(args.query, None, args.debug)
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
            response = run_once(user_input, pending, args.debug)
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
