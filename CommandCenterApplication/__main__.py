from __future__ import annotations

import argparse
from datetime import datetime, timezone

from CommandCenterApplication.fixture import build_fixture_dataset
from CommandCenterApplication.models import MODE_FIXTURE, MODE_REAL_READ_ONLY
from CommandCenterApplication.projection import build_command_center_view
from CommandCenterApplication.query import load_real_read_only_dataset
from CommandCenterApplication.server import serve


def main():
    parser = argparse.ArgumentParser(description="JOO Personal AI CIO Command Center")
    parser.add_argument("--mode", choices=(MODE_FIXTURE, MODE_REAL_READ_ONLY), default=MODE_FIXTURE)
    parser.add_argument("--fact-store")
    parser.add_argument("--journal")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    if args.mode == MODE_REAL_READ_ONLY:
        if not args.fact_store or not args.journal:
            parser.error("REAL_READ_ONLY requires --fact-store and --journal")
        dataset = load_real_read_only_dataset(
            fact_store_path=args.fact_store, journal_path=args.journal, now=now
        )
    else:
        dataset = build_fixture_dataset(now=now)
    view = build_command_center_view(dataset)
    print(f"JOO Command Center: http://{args.host}:{args.port} [{view.mode_label}]")
    if args.mode == MODE_REAL_READ_ONLY:
        print(f"FactStore (read-only): {args.fact_store}")
        print(f"DecisionJournal (read-only): {args.journal}")
    print(f"Factual freshness: {view.system_health.factual_freshness}")
    print("Execution: LIVE BLOCKED (gnl_ac_no1 authority not closed)")
    serve(view=view, host=args.host, port=args.port)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nJOO Command Center stopped.")
