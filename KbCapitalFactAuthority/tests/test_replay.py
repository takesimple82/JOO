from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from FactStore.models import ExplicitFactAppendRequest
from FactStore.sqlite_storage import SQLiteAppendOnlyFactEngine
from FactStore.store import FactStore
from ProviderGateway.models import ExplicitProviderPayloadEnvelope

from KbCapitalFactAuthority.replay import replay_capital_snapshot_from_store
from KbCapitalFactAuthority.service import run_kb_capital_fact_plane
from KbCapitalFactAuthority.tests.helpers import (
    COLLECTED,
    NOW,
    FakeAdapter,
    balances_collect_request,
    balances_payload,
    balances_request,
    holdings_capital_request,
    holdings_payload,
    identity,
    policy,
    portfolio_binding,
    success_outcome,
)


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        path = Path(self.temporary.name) / "facts.sqlite3"
        self.store = FactStore(
            lambda: NOW,
            SQLiteAppendOnlyFactEngine(path),
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_replay_capital_snapshot_without_kb_or_ai(self):
        balances = success_outcome(
            "balances-envelope-001",
            "balances-corr-001",
            balances_payload(),
        )
        holdings_raw = ExplicitProviderPayloadEnvelope(
            "holdings-envelope-001",
            "kb_open_api",
            "broker_fact",
            COLLECTED,
            "success",
            holdings_payload(),
            None,
            "holdings-corr-001",
        )
        self.store.append(
            ExplicitFactAppendRequest(
                "holdings-raw-001",
                holdings_raw,
                None,
            )
        )
        adapter = FakeAdapter({"balances": balances})
        result = run_kb_capital_fact_plane(
            adapter=adapter,
            balances_collect_request=balances_collect_request(),
            balances_raw_fact_id="balances-raw-001",
            balances_normalization_request=balances_request(),
            fact_store=self.store,
            snapshot_identity=identity(),
            portfolio_binding=portfolio_binding(),
            policy=policy(),
            now=NOW,
            holdings_raw_fact_id="holdings-raw-001",
            holdings_raw_envelope=holdings_raw,
            holdings_capital_normalization_request=holdings_capital_request(),
        )
        self.assertEqual(result.result_kind, "success")
        calls_before = len(adapter.calls)
        replayed = replay_capital_snapshot_from_store(
            fact_store=self.store,
            snapshot=result.capital_snapshot,
        )
        self.assertEqual(len(adapter.calls), calls_before)
        self.assertEqual(
            replayed.capital_snapshot_id,
            result.capital_snapshot.capital_snapshot_id,
        )
        self.assertEqual(
            replayed.orderable_cash_fact_id,
            result.capital_snapshot.orderable_cash_fact_id,
        )
        orderable = self.store.get_by_fact_id(
            replayed.orderable_cash_fact_id
        )
        self.assertEqual(orderable.payload["amount"], "339901")


if __name__ == "__main__":
    unittest.main()
