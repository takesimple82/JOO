from __future__ import annotations

import argparse
import uuid
from datetime import datetime, timezone

from CommandCenterAiDecisionOperation.service import (
    record_research_unavailable_attempt,
)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Record an evidence-bound REAL AI CIO attempt state"
    )
    parser.add_argument("--fact-store", required=True)
    parser.add_argument("--journal", required=True)
    parser.add_argument("--attempt-id")
    args = parser.parse_args(argv)
    now = datetime.now(timezone.utc)
    attempt_id = args.attempt_id or (
        "ai-cio-attempt-" + now.strftime("%Y%m%dT%H%M%S%fZ")
        + "-" + uuid.uuid4().hex[:8]
    )
    try:
        result = record_research_unavailable_attempt(
            fact_store_path=args.fact_store,
            journal_path=args.journal,
            attempt_id=attempt_id,
            now=now,
        )
    except Exception as exc:
        print(f"AI CIO attempt failed closed ({type(exc).__name__}).")
        return 1
    print("JOO evidence-bound AI CIO attempt recorded.")
    print(f"Attempt: {result.attempt_id}")
    print(f"Observation: {result.evidence_package.observation_id}")
    print(f"Research: {result.research_state}")
    print(f"Committee: {result.committee_state}")
    print(f"CIO: {result.cio_state}; EV/Allocation: UNAVAILABLE")
    print("Investment approval: NOT ISSUED; execution: LIVE BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
