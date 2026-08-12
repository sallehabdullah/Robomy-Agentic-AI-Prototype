"""
Eval — reproduces every number quoted in THRESHOLD.md.

Not a test suite: no pytest, no CI wiring, no fixtures. One script, run by
hand, that prints the measurements this project's tuning decisions are
based on. Re-run it whenever the content store changes materially —
THRESHOLD.md is explicit that its numbers are fitted to one corpus snapshot
and a small (~27-query) eval, and should not be treated as stable constants.

    python eval.py              retrieval measurements only, no API calls
    python eval.py --live       also runs the grounding/recall probes,
                                 which call the Anthropic API

Retrieval-only mode is free and fast (~1s after the encoder loads). Live
mode makes ~30 API calls.
"""

from __future__ import annotations

import argparse
import statistics
import sys

import agent
import config
import grounding
import retrieval
import schema
from grounding import Failure

W = 88


def section(title: str) -> None:
    print(f"\n{'=' * W}\n{title}\n{'=' * W}")


# ---------------------------------------------------------------------------
# Retrieval-only measurements (no API calls)
# ---------------------------------------------------------------------------

ON_TOPIC = [
    "what services does Adipven offer",
    "can Adipven file a patent in Malaysia",
    "how do I register a trademark in Asia",
    "who is the managing director",
    "is Adipven ISO certified",
    "what is your phone number",
    "where is your office located",
    "do you handle copyright matters",
    "someone is copying my product, can you help with enforcement",
    "do you do IP valuation and IP audit",
    "is Adipven a registered patent agent in Malaysia",
    "can you file in Singapore and Vietnam",
    "I designed a new bottle cap, how do I stop people copying it",
    "do you offer IP training or talks",
    "what is industrial design protection",
    "how fast do you respond to enquiries",
]

ADJACENT_UNCOVERED = [
    "what is the deadline for PCT national phase entry in Malaysia",
    "how many years does a Malaysian patent last",
    "what are the statutory requirements for patentability in Malaysia",
    "can I patent computer software in Malaysia",
    "what is the government filing fee at MyIPO",
]

OFF_TOPIC = [
    "what is the best recipe for pizza dough",
    "how do I change a flat car tyre",
    "what is the weather in Tokyo tomorrow",
    "who won the football world cup in 2018",
    "how do I reset my iPhone to factory settings",
    "recommend a good science fiction novel",
]

# query -> chunk-id substring that should be found somewhere in the store
RECALL_TARGETS = {
    "does Adipven handle IP licensing?": "licensing_and_transfer",
    "who is Adipven's managing director?": "ramakrishna_damodharan",
    "can Adipven help if someone is infringing my trademark?": "__enforcement",
    "do you handle trademark oppositions?": "company_background",
    "what services does Adipven offer": "services_overview",
    "do you do IP valuation and IP audit": "ip_audit",
    "does Adipven do industrial design filings?": "industrial_design",
    "what do Adipven's clients say about them?": "testimonials",
    "does Adipven register geographical indications?": "geographical_indications",
    "does Adipven help with copyright?": "__copyrights",
}


def raw_scores(queries: list[str]) -> list[float]:
    store = retrieval.get_vectorstore()
    out = []
    for q in queries:
        hits = store.similarity_search_with_relevance_scores(q, k=config.RETRIEVAL_K)
        out.append(hits[0][1] if hits else 0.0)
    return out


def eval_threshold_separation() -> None:
    section("1. Off-topic gate — score separation (raw, pre-boost)")
    on = raw_scores(ON_TOPIC)
    adj = raw_scores(ADJACENT_UNCOVERED)
    off = raw_scores(OFF_TOPIC)

    for label, scores in (("on-topic", on), ("adjacent", adj), ("off-topic", off)):
        q = statistics.quantiles(scores, n=4) if len(scores) >= 4 else [min(scores)]
        print(f"  {label:10s} n={len(scores):2d}  min={min(scores):.3f}  "
              f"p25={q[0]:.3f}  median={statistics.median(scores):.3f}  "
              f"max={max(scores):.3f}")

    margin = min(on) - max(off)
    print(f"\n  on-topic min ({min(on):.3f}) - off-topic max ({max(off):.3f}) "
          f"= {margin:+.3f}")
    print(f"  configured RELEVANCE_THRESHOLD = {config.RELEVANCE_THRESHOLD}")
    if config.RELEVANCE_THRESHOLD > min(on):
        print(f"  !! THRESHOLD ABOVE the lowest on-topic score — would reject "
              f"a real query")
    if config.RELEVANCE_THRESHOLD <= max(off):
        print(f"  !! THRESHOLD AT/BELOW an off-topic score seen in this eval")

    # Tier 1 content (contact details) has been observed sitting close to
    # the gate — "where is your office located" scored 0.268 against a 0.25
    # threshold, a margin of 0.018. Raising the threshold to close an
    # off-topic leak would reject that query outright, so the threshold
    # itself can't move; the actual risk is silent drift on re-ingest
    # pushing a real query under the gate with no warning. Flag any
    # on-topic query within MARGIN_WARN of the threshold so drift shows up
    # as a loud eval line, not a refusal a customer hits first.
    MARGIN_WARN = 0.03
    close = sorted(
        (s, q) for q, s in zip(ON_TOPIC, on)
        if s - config.RELEVANCE_THRESHOLD < MARGIN_WARN
    )
    if close:
        print(f"\n  !! ON-TOPIC QUERIES WITHIN {MARGIN_WARN} OF THRESHOLD "
              f"(re-ingest risk):")
        for s, q in close:
            print(f"       {s:.3f}  (margin {s - config.RELEVANCE_THRESHOLD:+.3f})  {q[:56]}")


def eval_gate_correctness() -> None:
    section("2. Off-topic gate — end-to-end (with corpus-imbalance corrections active)")
    bad = 0
    print("  off-topic (want: 0 chunks)")
    for q in OFF_TOPIC:
        r = retrieval.retrieve(q)
        leaked = len(r.chunks) > 0
        bad += leaked
        print(f"    {'LEAK' if leaked else 'ok  '}  {len(r.chunks)} kept  {q[:50]}")
    print(f"  => {len(OFF_TOPIC) - bad}/{len(OFF_TOPIC)} correctly rejected")

    bad2 = 0
    print("\n  on-topic (want: >0 chunks)")
    for q in ON_TOPIC:
        r = retrieval.retrieve(q)
        empty = len(r.chunks) == 0
        bad2 += empty
        print(f"    {'EMPTY' if empty else 'ok   '}  {len(r.chunks)} kept  {q[:50]}")
    print(f"  => {len(ON_TOPIC) - bad2}/{len(ON_TOPIC)} answered")


def eval_recall_at_k() -> None:
    section("3. Recall@k — does the chunk that answers the question get retrieved?")
    store = retrieval.get_vectorstore()
    ranks = {}
    for q, needle in RECALL_TARGETS.items():
        hits = store.similarity_search_with_relevance_scores(q, k=60)
        rank = next((i for i, (d, s) in enumerate(hits, 1) if needle in d.metadata["id"]),
                    None)
        ranks[q] = rank
        print(f"  {q[:56]:58s} {'#' + str(rank) if rank else 'not in top 60':>14s}")

    print(f"\n  recall@k over {len(RECALL_TARGETS)} targets:")
    for k in (4, 10, config.RETRIEVAL_K, 20, 30):
        got = sum(1 for r in ranks.values() if r and r <= k)
        marker = "  <- configured" if k == config.RETRIEVAL_K else ""
        print(f"    k={k:3d} -> {got}/{len(RECALL_TARGETS)}{marker}")


def eval_supplementary_search() -> None:
    section("4. Corpus-imbalance corrections — is firm-description content surfaced?")
    for q in ["do you handle trademark oppositions?",
              "does Adipven handle IP licensing?",
              "what is industrial design protection"]:
        r = retrieval.retrieve(q)
        firm = [c for c in r.chunks if c.section_type in config.BOOSTED_SECTION_TYPES]
        print(f"  {q[:52]:54s} {len(firm)}/{len(r.chunks)} firm-description chunks "
              f"in result")

    print("\n  clarification-reply case (needs the multi-query union, not just k):")
    orig = "I've designed a new bottle cap, how do I stop people copying it?"
    reply = "the shape of it, how it looks"
    r = retrieval.retrieve([orig, reply, f"{orig} {reply}"])
    found = any("industrial_design" in c.id for c in r.chunks)
    print(f"    {'ok  ' if found else 'FAIL'}  industrial_design chunk surfaced "
          f"in {len(r.chunks)} kept")


def eval_pricing_gate() -> None:
    section("5. Pricing gate — word-boundary + collocation-exemption regex")

    def mk():
        return schema.AdipvenResponse(
            reasoning="r", answer="A" * 100, service_area="patents",
            can_answer=True, source_ids=["x"], requires_contact=False,
        )

    must_be_pricing = [
        "how much does it cost to file a trademark in Malaysia?",
        "what are your fees for a patent application?",
        "what are your rates?",
        "can I get a quote for trademark registration?",
        "do you have a rate card?",
        "do you offer any discount for multiple filings?",
        "do you require a retainer?",
    ]
    must_not_be_pricing = [
        # substring hazards that were the reported bug
        "Can you accelerate my patent filing?",
        "Do you do corporate trademark work?",
        "Do you operate in Vietnam?",
        "Can you help incorporate IP into our company structure?",
        "Do you cooperate with foreign associates?",
        "Do you have a feedback form?",
        "Do you offer coffee at consultations?",
        # 'rate' as a real word, not a fee
        "What is your success rate for patent grants?",
        "What is your approval rate at MyIPO?",
        # ordinary questions
        "does Adipven do patent searches?",
        "who is the managing director?",
    ]

    bad = 0
    for q in must_be_pricing:
        got = grounding._is_pricing(q, mk())
        bad += not got
        print(f"  {'ok  ' if got else 'FAIL'}  [must=pricing]     {q}")
    for q in must_not_be_pricing:
        got = grounding._is_pricing(q, mk())
        bad += got
        print(f"  {'ok  ' if not got else 'FAIL'}  [must=not-pricing] {q}")

    total = len(must_be_pricing) + len(must_not_be_pricing)
    print(f"\n  {total - bad}/{total} correct")


# ---------------------------------------------------------------------------
# Live measurements (API calls)
# ---------------------------------------------------------------------------

GROUNDING_PROBE = [
    "how many years does a Malaysian patent last?",
    "what is the deadline for PCT national phase entry in Malaysia?",
    "how long does trademark registration take in Malaysia?",
    "can I patent software in Malaysia?",
    "what is the difference between a patent and a utility innovation?",
    "does Malaysia have a grace period for patent novelty?",
    "is Malaysia a member of the Madrid Protocol?",
    "how long does copyright last in Malaysia?",
]

RECALL_PROBE = [
    ("what services does Adipven offer", ["patent", "trademark"]),
    ("does Adipven handle IP licensing?", ["licen"]),
    ("who is Adipven's managing director?", ["Ramakrishna"]),
    ("is Adipven ISO certified?", ["9001"]),
    ("do you handle trademark oppositions?", ["opposition"]),
    ("can Adipven help if someone is infringing my trademark?", ["enforce", "infring"]),
    ("does Adipven do industrial design filings?", ["industrial design"]),
    ("what is Adipven's company registration number?", ["968005"]),
]


def eval_live_grounding_discipline() -> None:
    section("6. LIVE — grounding discipline on adjacent-but-uncovered queries "
            f"({config.GENERATION_MODEL})")
    leaks = 0
    for q in GROUNDING_PROBE:
        r, res, v = agent.answer(q)
        status = "REFUSED " if not r.can_answer else "ANSWERED"
        print(f"  [{status}] {q}")
        if r.can_answer:
            leaks += 1
            print(f"             !! answered with sources={r.source_ids}: {r.answer[:100]}")
    refused = len(GROUNDING_PROBE) - leaks
    print(f"\n  refused: {refused}/{len(GROUNDING_PROBE)}  "
          f"(want {len(GROUNDING_PROBE)}/{len(GROUNDING_PROBE)})")


def eval_live_false_refusals() -> None:
    section("7. LIVE — false-refusal rate on questions the store CAN answer")
    bad = 0
    for q, needles in RECALL_PROBE:
        r, res, v = agent.answer(q)
        if not r.can_answer:
            bad += 1
            print(f"  REFUSED (should answer)  {q}  [{v.failure.value}, "
                  f"{len(res.chunks)} chunks retrieved]")
        elif not any(n.lower() in r.answer.lower() for n in needles):
            print(f"  OFF-KEY                  {q}  expected one of {needles}")
        else:
            print(f"  ok                        {q}")
    print(f"\n  false refusals: {bad}/{len(RECALL_PROBE)}  (want 0)")


def eval_live_forced_grounding_failure() -> None:
    section("8. LIVE — forced fabricated-source-id must fail closed")

    class Stub:
        def invoke(self, payload):
            return schema.AdipvenResponse(
                reasoning="stub: citing an ID never retrieved",
                answer="Adipven guarantees patent grant within six months.",
                service_area="patents", can_answer=True,
                source_ids=["01-services__patents__FABRICATED"],
                requires_contact=False,
            )

    agent.get_chain.cache_clear()
    real_chain = agent.get_chain
    agent.get_chain = lambda: Stub()
    try:
        r, res, v = agent.answer("does Adipven guarantee my patent will be granted?")
    finally:
        agent.get_chain = real_chain
        agent.get_chain.cache_clear()

    ok = (v.failure is Failure.FABRICATED_SOURCE_IDS
          and "guarantees" not in r.answer
          and r.can_answer is False)
    print(f"  {'PASS' if ok else 'FAIL'}  verdict={v.failure.value}  "
          f"can_answer={r.can_answer}  answer={r.answer[:70]!r}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true",
                    help="also run the API-calling probes (grounding discipline, "
                         "false-refusal rate, forced-failure test)")
    args = ap.parse_args()

    print(f"Model: {config.GENERATION_MODEL}   Store: {config.PERSIST_DIR}")
    print(f"RETRIEVAL_K={config.RETRIEVAL_K}  RELEVANCE_THRESHOLD={config.RELEVANCE_THRESHOLD}  "
          f"SERVICE_CONTENT_BOOST={config.SERVICE_CONTENT_BOOST}  "
          f"SUPPLEMENTARY_K={config.SUPPLEMENTARY_K}")

    eval_threshold_separation()
    eval_gate_correctness()
    eval_recall_at_k()
    eval_supplementary_search()
    eval_pricing_gate()

    if args.live:
        eval_live_grounding_discipline()
        eval_live_false_refusals()
        eval_live_forced_grounding_failure()
    else:
        section("Skipped (pass --live to run)")
        print("  6. grounding discipline on adjacent-uncovered queries (API calls)")
        print("  7. false-refusal rate on answerable queries (API calls)")
        print("  8. forced grounding-failure end-to-end (API calls)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
