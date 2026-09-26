from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from FactStore.sqlite_storage import SQLiteAppendOnlyFactEngine
from FactStore.store import FactStore

from KbCapitalFactAuthority.service import run_kb_capital_fact_plane
from KbCapitalFactAuthority.tests.helpers import (
    NOW,
    FakeAdapter,
    balances_collect_request,
    balances_payload,
    balances_request,
    identity,
    policy,
    portfolio_binding,
    success_outcome,
)
from KbCapitalFactAuthority.validation import assert_orderable_cash_field


class LeverageSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        path = Path(self.temporary.name) / "facts.sqlite3"
        self.store = FactStore(
            lambda: NOW,
            SQLiteAppendOnlyFactEngine(path),
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_large_mx_and_credit_cannot_inflate_orderable_cash(self):
        outcome = success_outcome(
            "balances-envelope-001",
            "balances-corr-001",
            balances_payload(
                orderable_cash="000000000010000",
                orderable_total="000000009999999",
                extra={
                    "ordr_psbl_sbt": "000000009000000",
                    "mx_ordr_psbl_csh": "000000009999999",
                    "mx_ordr_psbl_amt": "000000009999999",
                    "crdt_ordr_psbl_csh": "000000008888888",
                    "crdt_ordr_psbl_tl_amt": "000000008888888",
                    "fncng_amt": "000000007777777",
                    "do_psbl_sbt": "000000006666666",
                },
            ),
        )
        result = run_kb_capital_fact_plane(
            adapter=FakeAdapter({"balances": outcome}),
            balances_collect_request=balances_collect_request(),
            balances_raw_fact_id="balances-raw-001",
            balances_normalization_request=balances_request(),
            fact_store=self.store,
            snapshot_identity=identity(),
            portfolio_binding=portfolio_binding(),
            policy=policy(),
            now=NOW,
        )
        self.assertEqual(result.result_kind, "success")
        orderable = self.store.get_by_fact_id(
            result.capital_snapshot.orderable_cash_fact_id
        )
        total = self.store.get_by_fact_id(
            result.capital_snapshot.orderable_total_fact_id
        )
        self.assertEqual(orderable.payload["amount"], "10000")
        self.assertEqual(total.payload["amount"], "9999999")
        self.assertNotEqual(
            orderable.payload["amount"], total.payload["amount"]
        )
        self.assertEqual(
            orderable.payload["broker_field"], "ordr_psbl_csh"
        )

    def test_substitute_leverage_fields_rejected_as_orderable_cash(self):
        for field in (
            "mx_ordr_psbl_csh",
            "mx_buy_psbl_amt",
            "crdt_ordr_psbl_csh",
            "ordr_psbl_sbt",
            "fncng_amt",
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    assert_orderable_cash_field(field)


if __name__ == "__main__":
    unittest.main()
