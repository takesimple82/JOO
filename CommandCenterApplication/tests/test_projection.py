from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import timedelta

from CommandCenterApplication.fixture import build_fixture_dataset
from CommandCenterApplication.presentation import public_json
from CommandCenterApplication.projection import build_command_center_view


class CommandCenterProjectionTests(unittest.TestCase):
    def setUp(self):
        self.dataset = build_fixture_dataset()
        self.view = build_command_center_view(self.dataset)

    def test_fixture_is_explicit_and_execution_is_fail_closed(self):
        self.assertEqual(self.view.mode, "FIXTURE")
        self.assertIn("NOT REAL DATA", self.view.mode_label)
        self.assertEqual(self.view.execution.state, "LIVE_BLOCKED")
        self.assertEqual(self.view.execution.mutation_mode, "LIVE_DISABLED")
        self.assertFalse(self.view.execution.live_enabled)
        self.assertEqual(self.view.investment_approval.state, "NOT_ISSUED")

    def test_broker_valuation_not_quantity_times_price_drives_weights(self):
        self.assertEqual(self.view.portfolio_value_krw, "7920000")
        self.assertEqual(
            [(x.security, x.market_value_krw, x.valuation_authority) for x in self.view.positions],
            [
                ("A000660", "820000", "SSQM2952.Record1[].val_amt"),
                ("A005930", "7100000", "SSQM2952.Record1[].val_amt"),
            ],
        )
        self.assertEqual([x.weight_percent for x in self.view.positions], ["10.35", "89.65"])

    def test_authoritative_cash_and_non_sizing_account_value_remain_separate(self):
        self.assertEqual(self.view.capital.orderable_cash_krw, "339901")
        self.assertEqual(self.view.capital.available_allocation_capacity_krw, "339901")
        self.assertEqual(self.view.capital.broker_account_valuation_krw, "9000000")
        self.assertEqual(
            self.view.capital.broker_account_valuation_authority,
            "NOT_SIZING_AUTHORITY",
        )

    def test_foreign_position_is_an_explicit_exclusion(self):
        self.assertEqual(self.view.position_count, 2)
        self.assertEqual(len(self.view.foreign_exclusions), 1)
        self.assertEqual(self.view.foreign_exclusions[0].provider_symbol, "US0378331005")
        self.assertEqual(self.view.foreign_exclusions[0].reason, "EXCLUDED_NON_DOMESTIC")

    def test_no_change_non_executable_and_attention_are_visible(self):
        self.assertEqual(self.view.change.classification, "NO_CHANGE")
        self.assertEqual(self.view.cio.state, "BLOCKED")
        self.assertEqual(self.view.cio.posture, "NO_ACTION_UNRESOLVED")
        self.assertEqual(self.view.cio.decision_timestamp, self.dataset.generated_at.isoformat())
        self.assertEqual(len(self.view.attention), 1)
        self.assertEqual(self.view.attention[0].state, "UNRESOLVED")

    def test_stale_snapshot_degrades_health(self):
        dataset = replace(
            self.dataset,
            generated_at=self.dataset.generated_at + timedelta(minutes=10),
        )
        view = build_command_center_view(dataset)
        self.assertEqual(view.system_health.factual_freshness, "STALE")
        self.assertEqual(view.system_health.state, "ATTENTION")

    def test_missing_position_valuation_fails_closed_without_inventing_value(self):
        facts = tuple(x for x in self.dataset.facts if x.fact_id != "fixture-value-000660")
        view = build_command_center_view(replace(self.dataset, facts=facts))
        self.assertIsNone(view.portfolio_value_krw)
        self.assertIsNone(view.capital.deployed_capital_krw)
        sk = next(x for x in view.positions if x.security == "A000660")
        self.assertIsNone(sk.market_value_krw)
        self.assertIsNone(sk.weight_percent)

    def test_non_factual_truth_class_is_rejected(self):
        bad = replace(self.dataset.facts[0], source_class="research_ai")
        with self.assertRaisesRegex(ValueError, "non-factual"):
            build_command_center_view(replace(self.dataset, facts=(bad,) + self.dataset.facts[1:]))

    def test_presentation_redacts_secret_and_full_account_number(self):
        attention = self.dataset.artifacts[2].artifact
        unsafe = replace(attention, detail="appsecret=hidden account 12345678901")
        artifacts = self.dataset.artifacts[:2] + (
            replace(self.dataset.artifacts[2], artifact=unsafe),
        ) + self.dataset.artifacts[3:]
        payload = public_json(build_command_center_view(replace(self.dataset, artifacts=artifacts)))
        self.assertNotIn(b"hidden", payload)
        self.assertNotIn(b"12345678901", payload)
        self.assertIn("••••8901".encode(), payload)
        self.assertIn(b'"max_position_krw":"100000000"', payload)
        self.assertIn(b'"provider_symbol":"US0378331005"', payload)


if __name__ == "__main__":
    unittest.main()
