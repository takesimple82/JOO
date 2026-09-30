from __future__ import annotations

import argparse
import uuid
from datetime import datetime, timezone
from pathlib import Path

from ProviderGateway.auth.kb_openapi_runtime import (
    KbOpenApiRuntimeReady,
    compose_kb_openapi_live_runtime,
)
from ProviderGateway.models import ExplicitBrokerParameterProfile

from CommandCenterReadOnlyOperation.configuration import (
    load_read_only_operation_config,
)
from CommandCenterReadOnlyOperation.http import kb_read_only_http_post
from CommandCenterReadOnlyOperation.service import (
    run_real_read_only_observation,
)


def _default_state_path(name):
    return Path.home() / ".joo" / "command_center" / name


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Produce one verified KB read-only Command Center observation"
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--fact-store", default=str(_default_state_path("facts.sqlite3")))
    parser.add_argument("--journal", default=str(_default_state_path("decision.sqlite3")))
    parser.add_argument("--observation-id")
    args = parser.parse_args(argv)
    now = datetime.now(timezone.utc)
    observation_id = args.observation_id or (
        "kb-readonly-" + now.strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:8]
    )
    try:
        config = load_read_only_operation_config(args.config)
        profile = ExplicitBrokerParameterProfile(
            "joo-command-center-readonly",
            config.account_selector,
            ("holdings", "balances"),
        )
        runtime = compose_kb_openapi_live_runtime(
            kb_read_only_http_post,
            lambda: datetime.now(timezone.utc),
            profile,
        )
        if type(runtime) is not KbOpenApiRuntimeReady:
            raise ValueError("KB read-only runtime unavailable")
        result = run_real_read_only_observation(
            adapter=runtime.adapter,
            binding=runtime.binding,
            config=config,
            fact_store_path=args.fact_store,
            journal_path=args.journal,
            observation_id=observation_id,
            now=now,
        )
    except Exception as exc:
        print(f"Observation failed closed ({type(exc).__name__}).")
        return 1
    observation = result.observation
    print("JOO real read-only observation accepted.")
    print(f"Observation: {observation.observation_id}")
    print(f"Observed at: {observation.created_at.isoformat()}")
    print(f"Change: {observation.change_class}")
    print(f"Published factual records: {len(observation.application_fact_ids)}")
    print("Execution: LIVE BLOCKED; mutation calls: 0")
    print(f"FactStore: {result.fact_store_path}")
    print(f"DecisionJournal: {result.journal_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
