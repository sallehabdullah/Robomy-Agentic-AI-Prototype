"""
Measure whether /query/stream actually delivers text progressively.

    python measure_stream.py                      # against production
    python measure_stream.py --url http://127.0.0.1:8000
    python measure_stream.py --runs 3             # repeat, Render is noisy

Why this exists as a standalone script rather than a section in eval.py:
eval.py measures *correctness* and imports the agent directly. This
measures *delivery timing* over the wire, so it must not import agent,
retrieval, or langchain at all — otherwise it would be measuring this
machine's model stack instead of the deployed service. Stdlib only, for
the same reason: no client library that might buffer on our behalf.

Background (see STREAMING_STRATEGIES.md, CORRECTION block): an earlier
round of timing work was invalidated because the dev machine's network
delivered responses in bursts — 71% of one response arrived inside a 0.1s
window after ~5.8s of silence, which generation at ~83 tok/s cannot
produce. Every conclusion drawn from local timing was therefore suspect.
This script exists to get a reading over the real path instead.

What the numbers mean:

  span         first delta -> last delta. This is the width of the window
               in which the customer sees text appear. If it collapses to
               near zero, nothing is streaming no matter how many deltas
               were sent.
  p50 gap      typical pause between deltas. Smooth streaming looks like
               tens of milliseconds; one burst looks like ~0.
  max gap      the giveaway. A single large gap inside the span means
               something flushed in chunks rather than continuously.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request

DEFAULT_URL = "https://adipven-assistant-api.onrender.com"

# Deliberately a question the store can answer with citations: only
# grounded, cited answers stream (see grounding.check_prestream) — a
# refusal or a greeting is emitted whole and would measure nothing.
DEFAULT_QUERY = "What services does Adipven offer?"

# Free-tier instances spin down after ~15 min idle and take ~30-50s to
# wake. That wake time would swamp the measurement, so it is paid once
# up front and excluded.
WARMUP_TIMEOUT = 120
STREAM_TIMEOUT = 120


def warm(base: str) -> float | None:
    """Wake a spun-down instance. Returns seconds waited, or None if down."""
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(f"{base}/health", timeout=WARMUP_TIMEOUT) as r:
            r.read()
        return time.perf_counter() - t0
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"  health check failed: {exc}", file=sys.stderr)
        return None


def measure(base: str, query: str) -> dict | None:
    """POST to /query/stream and timestamp every SSE frame on arrival."""
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        f"{base}/query/stream",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            # Ask intermediaries not to buffer or transform the stream.
            # Notably: no Accept-Encoding, so nothing gzips the event
            # stream and coalesces small chunks on the way back.
            "Accept": "text/event-stream",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
        },
    )

    t0 = time.perf_counter()
    deltas: list[tuple[float, int]] = []   # (elapsed, chars)
    first_byte = None
    final_at = None
    buf = ""

    try:
        with urllib.request.urlopen(req, timeout=STREAM_TIMEOUT) as resp:
            # read(1) would be pathologically slow; a small block size
            # keeps arrival resolution fine without busy-waiting.
            while True:
                block = resp.read(64)
                if not block:
                    break
                now = time.perf_counter() - t0
                if first_byte is None:
                    first_byte = now
                buf += block.decode("utf-8", errors="replace")

                while "\n\n" in buf:
                    frame, buf = buf.split("\n\n", 1)
                    line = next(
                        (l for l in frame.split("\n") if l.startswith("data:")), None
                    )
                    if line is None:
                        continue
                    try:
                        ev = json.loads(line[5:].strip())
                    except json.JSONDecodeError:
                        continue
                    if ev.get("type") == "delta":
                        deltas.append((now, len(ev.get("text", ""))))
                    elif ev.get("type") == "final":
                        final_at = now
                    elif ev.get("type") == "error":
                        print(f"  server error event: {ev.get('detail')}",
                              file=sys.stderr)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"  request failed: {exc}", file=sys.stderr)
        return None

    total = time.perf_counter() - t0
    return {
        "first_byte": first_byte,
        "deltas": deltas,
        "final_at": final_at,
        "total": total,
    }


def report(m: dict) -> dict:
    """Print one run. Returns the stats the verdict needs."""
    deltas = m["deltas"]
    fb = m["first_byte"]
    print(f"  first byte      {fb:6.2f}s" if fb else "  first byte      n/a")

    if not deltas:
        print("  deltas          none — answer was emitted whole")
        print("                  (a refusal, greeting, or clarification does "
              "this by design;")
        print("                   if the query was answerable, this is the "
              "burst case)")
        print(f"  total           {m['total']:6.2f}s")
        return {"span": 0.0, "count": 0, "first": fb or 0.0, "max_gap": 0.0}

    first, last = deltas[0][0], deltas[-1][0]
    span = last - first
    chars = sum(n for _, n in deltas)
    gaps = [b[0] - a[0] for a, b in zip(deltas, deltas[1:])]

    print(f"  first delta     {first:6.2f}s   <- customer sees text here")
    print(f"  delta span      {span:6.2f}s   <- width of the typing window")
    print(f"  deltas          {len(deltas):6d}    ({chars} chars, "
          f"{chars / len(deltas):.1f} chars/delta)")

    # Report WHERE the largest gap falls, rather than assuming it is
    # mid-stream. Measured against production over 4 runs it landed at
    # 98.5-99.5% through every time (stdev 0.4 percentage points) — the
    # cost of closing the tool-call JSON and ending the message, not a
    # buffer boundary. An earlier version of this script treated that as
    # "chunked flushing" and mis-diagnosed a stream that was fine.
    # Position is the thing that distinguishes the two, so print it and
    # let the reader judge.
    biggest, at = max((g, i) for i, g in enumerate(gaps))
    chars_before = sum(n for _, n in deltas[:at + 1])
    pct = 100 * chars_before / chars if chars else 0.0

    # What the eye perceives is the number of separate visual updates, not
    # the raw delta count — deltas arriving sub-millisecond apart land in
    # the same rendered frame. This is the metric that actually decides
    # whether it reads as typing.
    BURST_MS = 0.020
    bursts = 1 + sum(1 for g in gaps if g > BURST_MS)
    rate = bursts / span if span > 0 else 0.0

    print(f"  gap p50         {statistics.median(gaps) * 1000:6.1f}ms")
    if len(gaps) >= 10:
        p90 = sorted(gaps)[int(len(gaps) * 0.9)]
        print(f"  gap p90         {p90 * 1000:6.1f}ms")
    print(f"  gap max         {biggest * 1000:6.1f}ms  at {pct:.1f}% through"
          f"  <- >97% means end-of-message overhead, not buffering")
    print(f"  visual updates  {bursts:6d}    ({rate:.1f}/s — "
          f"{'smooth' if rate >= 5 else 'chunky'} to the eye)")
    print(f"  total           {m['total']:6.2f}s")
    return {
        "span": span,
        "count": len(deltas),
        "first": first,
        "max_gap": biggest,
        "rate": rate,
    }


def verdict(runs: list[dict]) -> None:
    """Apply the Phase 0 decision rule from STREAMING_IMPLEMENTATION_PLAN.md.

    Span alone is not sufficient. A span can clear 1s while consisting of
    two bursts separated by one long pause — progressive, but not the
    smooth flow a span figure alone would imply. The dominant-gap ratio
    (largest gap / span) separates those cases, which is the third branch
    of the plan's decision rule.
    """
    print("\n" + "=" * 62)
    streamed = [r for r in runs if r["count"] > 0]
    if not streamed:
        print("VERDICT: no deltas in any run.")
        print("  Either the queries weren't answerable (so the answer was")
        print("  emitted whole by design), or delivery is fully buffered.")
        print("  -> Phase 1: isolate the layer.")
        return

    best = max(r["span"] for r in streamed)
    # Perceived smoothness is the update rate, not the span. ~5/s is about
    # where discrete chunks stop reading as chunks.
    worst_rate = min(r["rate"] for r in streamed)
    slowest_first = max(r["first"] for r in streamed)

    print(f"VERDICT: best delta span {best:.2f}s across {len(streamed)} run(s); "
          f"slowest visual update rate {worst_rate:.1f}/s")

    if best < 0.3:
        print("  Burst delivery — deltas arrive effectively at once, so")
        print("  nothing is perceptibly streaming.")
        print("  -> Phase 1: isolate whether it is LangChain (1A),")
        print("     the proxy (1B), or the browser (1C).")
    elif worst_rate < 5:
        print("  CHUNKY. Text arrives in visibly discrete jumps.")
        print("  -> Phase 1B: check compression / proxy flush boundaries.")
    else:
        print("  Streaming is smooth to the eye — text arrives in small")
        print("  frequent increments, which is what a typewriter effect is.")
        print("  -> No further streaming work is warranted.")

    # The wait before any text appears usually dwarfs the typing window,
    # and no streaming work can shorten it — say so rather than let a
    # green verdict imply the latency problem is solved.
    print(f"\n  NOTE: slowest time-to-first-text was {slowest_first:.1f}s. "
          f"The typing")
    print(f"  window is only {best:.2f}s, so the customer spends the large")
    print("  majority of the turn watching nothing. That gap is `reasoning`")
    print("  generation and is not streamable — see Phase 3.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=DEFAULT_URL, help="base URL of the service")
    ap.add_argument("--query", default=DEFAULT_QUERY)
    ap.add_argument("--runs", type=int, default=2,
                    help="Render's shared CPU is noisy; repeat before judging")
    args = ap.parse_args()
    base = args.url.rstrip("/")

    print(f"target: {base}")
    print(f"query:  {args.query!r}\n")

    print("waking the instance (excluded from measurement)...")
    waited = warm(base)
    if waited is None:
        print("service unreachable — aborting.", file=sys.stderr)
        return 2
    print(f"  ready after {waited:.1f}s"
          + ("  (cold start)" if waited > 5 else "  (already warm)"))

    runs = []
    for i in range(args.runs):
        print(f"\nrun {i + 1}/{args.runs}")
        m = measure(base, args.query)
        if m is None:
            continue
        runs.append(report(m))

    if not runs:
        print("\nno successful runs.", file=sys.stderr)
        return 1
    verdict(runs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
