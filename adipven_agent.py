"""
This file used to hold the whole agent. It has been split along its real
seams:

    config.py      shared settings (paths, model IDs, thresholds)
    schema.py      Pydantic request/response models
    retrieval.py   Chroma access, relevance filtering, context formatting
    grounding.py   fail-closed enforcement
    agent.py       prompt + LCEL chain + query pipeline
    cli.py         command-line interface

Use `python cli.py` instead.
"""

import sys

if __name__ == "__main__":
    print("adipven_agent.py has moved — use `python cli.py` "
          "(see module docstring).", file=sys.stderr)
    from cli import main

    raise SystemExit(main())
