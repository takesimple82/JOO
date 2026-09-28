from __future__ import annotations

import tempfile
import unittest
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from FactStore.models import ExplicitFactAppendRequest
from FactStore.sqlite_storage import SQLiteAppendOnlyFactEngine
from FactStore.store import FactStore
from ProviderGateway.models import ExplicitProviderPayloadEnvelope

from KbCapitalFactAuthority.models import ExplicitCapitalPortfolioBinding
from KbCapitalFactAuthority.normalization import (
    normalize_ssqm0004_balances,
    normalize_ssqm2952_capital_facts,
)
from KbCapitalFactAuthority.service import run_kb_capital_fact_plane
from KbCapitalFactAuthority.tests.helpers import (
    COLLECTED,
    NOW,
    UTC,
    FakeAdapter,
    balances_collect_request,
    balances_payload,
    balances_request,
    failure_outcome,
    holdings_capital_request,
    holdings_payload,
    identity,
    policy,
    portfolio_binding,
    success_outcome,
)
from KbCapitalFactAuthority.validation import (
    assert_orderable_cash_field,
    validate_orderable_cash_semantic_safety,
)
from KbCapitalFactAuthority.vocabularies import (
    AMOUNT_PRESENCE_MISSING,
    AMOUNT_PRESENCE_PRESENT,
    BROKER_FIELD_ORDERABLE_CASH,
    FACT_KIND_ORDERABLE_CASH,
    SIZING_AUTHORITY_NONE,
)


class CapitalFactPlaneTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        path = Path(self.temporary.name) / "facts.sqlite3"
        self.store = FactStore(
            lambda: NOW,
            SQLiteAppendOnlyFactEngine(path),
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_orderable_cash_from_ordr_psbl_csh_only(self):
        outcome = success_outcome(
            "balances-envelope-001",
            "balances-corr-001",
            balances_payload(orderable_cash="000000000339901"),
        )
        adapter = FakeAdapter({"balances": outcome})
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
        )
        self.assertEqual(result.result_kind, "success")
        snapshot = result.capital_snapshot
        self.assertIsNotNone(snapshot)
        orderable = self.store.get_by_fact_id(snapshot.orderable_cash_fact_id)
        self.assertEqual(
            orderable.payload["fact_kind"], FACT_KIND_ORDERABLE_CASH
        )
        self.assertEqual(
            orderable.payload["broker_field"], BROKER_FIELD_ORDERABLE_CASH
        )
        self.assertEqual(orderable.payload["amount"], "339901")
        self.assertEqual(
            orderable.payload["raw_amount"], "000000000339901"
        )
        self.assertEqual(
            orderable.payload["amount_presence"], AMOUNT_PRESENCE_PRESENT
        )

    def test_deposit_orderable_withdrawable_settlement_remain_distinct(self):
        outcome = success_outcome(
            "balances-envelope-001",
            "balances-corr-001",
            balances_payload(
                orderable_cash="000000000100000",
                orderable_total="000000000200000",
                withdrawable="000000000050000",
                deposit_today="000000000300000",
                deposit_d1="000000000400000",
                deposit_d2="000000000500000",
            ),
        )
        result = run_kb_capital_fact_plane(
            adapter=FakeAdapter({"balances": outcome}),
            balances_collect_request=balances_collect_request(),
            balances_raw_fact_id="balances-raw-001",
            balances_normalization_request=balances_request(),
            fact_store=self.store,
            snapshot_identity=identity(),
            portfolio_binding=ExplicitCapitalPortfolioBinding(
                None, None, None
            ),
            policy=policy(),
            now=NOW,
        )
        snapshot = result.capital_snapshot
        ids = [
            snapshot.orderable_cash_fact_id,
            snapshot.orderable_total_fact_id,
            snapshot.withdrawable_cash_fact_id,
            snapshot.deposit_today_fact_id,
            snapshot.deposit_d1_fact_id,
            snapshot.deposit_d2_fact_id,
        ]
        self.assertEqual(len(ids), len(set(ids)))
        amounts = [
            self.store.get_by_fact_id(fact_id).payload["amount"]
            for fact_id in ids
        ]
        self.assertEqual(
            amounts,
            ["100000", "200000", "50000", "300000", "400000", "500000"],
        )

    def test_missing_deposit_is_not_zero(self):
        payload = balances_payload()
        del payload["dataBody"]["ndy_tfnd"]
        outcome = success_outcome(
            "balances-envelope-001",
            "balances-corr-001",
            payload,
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
        d1 = self.store.get_by_fact_id(
            result.capital_snapshot.deposit_d1_fact_id
        )
        self.assertEqual(d1.payload["amount_presence"], AMOUNT_PRESENCE_MISSING)
        self.assertIsNone(d1.payload["amount"])
        self.assertNotEqual(d1.payload["amount"], "0")

    def test_legitimate_zero_orderable_cash_is_present_zero(self):
        outcome = success_outcome(
            "balances-envelope-001",
            "balances-corr-001",
            balances_payload(orderable_cash="000000000000000"),
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
        orderable = self.store.get_by_fact_id(
            result.capital_snapshot.orderable_cash_fact_id
        )
        self.assertEqual(
            orderable.payload["amount_presence"], AMOUNT_PRESENCE_PRESENT
        )
        self.assertEqual(orderable.payload["amount"], "0")
        self.assertEqual(Decimal(orderable.payload["amount"]), Decimal(0))

    def test_position_mv_uses_val_amt_and_preserves_unsettled_zero_qty(self):
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
            holdings_payload(quantity="000000000000000", val_amt="000000000000426500"),
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
        result = run_kb_capital_fact_plane(
            adapter=FakeAdapter({"balances": balances}),
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
        mv_id = result.capital_snapshot.position_market_value_fact_ids[0]
        mv = self.store.get_by_fact_id(mv_id)
        self.assertEqual(mv.payload["amount"], "426500")
        self.assertEqual(mv.payload["quantity"], "0")
        self.assertEqual(mv.payload["valuation_method"], "broker_val_amt")
        self.assertNotIn("computed_from_quantity_price", mv.payload)
        valuation = self.store.get_by_fact_id(
            result.capital_snapshot.broker_reported_account_valuation_fact_id
        )
        self.assertEqual(
            valuation.payload["sizing_authority"], SIZING_AUTHORITY_NONE
        )

    def test_never_invent_position_mv_from_qty_times_price(self):
        raw = ExplicitProviderPayloadEnvelope(
            "holdings-envelope-001",
            "kb_open_api",
            "broker_fact",
            COLLECTED,
            "success",
            holdings_payload(
                quantity="000000000002",
                val_amt="000000000000100000",
                now_prc="00000000090000",
            ),
            None,
            "holdings-corr-001",
        )
        record = self.store.append(
            ExplicitFactAppendRequest("holdings-raw-001", raw, None)
        )
        normalized = normalize_ssqm2952_capital_facts(
            raw_record=record,
            raw_envelope=raw,
            request=holdings_capital_request(),
        )
        mv = [
            fact
            for fact in normalized.facts
            if fact.fact_kind
            == "kb_ssqm2952_position_market_value"
        ][0]
        self.assertEqual(mv.amount.canonical_text, "100000")
        invented = Decimal("2") * Decimal("90000")
        self.assertNotEqual(Decimal(mv.amount.canonical_text), invented)

    def test_raw_persists_when_normalization_fails(self):
        payload = balances_payload()
        payload["dataBody"]["ordr_psbl_csh"] = "not-a-decimal"
        outcome = success_outcome(
            "balances-envelope-001",
            "balances-corr-001",
            payload,
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
        self.assertEqual(result.result_kind, "failure")
        self.assertEqual(
            result.failure_code, "BALANCES_NORMALIZATION_FAILED"
        )
        raw = self.store.get_by_fact_id("balances-raw-001")
        self.assertEqual(raw.payload["dataBody"]["ordr_psbl_csh"], "not-a-decimal")
        self.assertEqual(result.canonical_fact_ids, ())

    def test_provider_unavailable_fail_closed(self):
        result = run_kb_capital_fact_plane(
            adapter=FakeAdapter({"balances": failure_outcome()}),
            balances_collect_request=balances_collect_request(),
            balances_raw_fact_id="balances-raw-001",
            balances_normalization_request=balances_request(),
            fact_store=self.store,
            snapshot_identity=identity(),
            portfolio_binding=portfolio_binding(),
            policy=policy(),
            now=NOW,
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertEqual(result.failure_code, "PROVIDER_UNAVAILABLE")

    def test_stale_facts_fail_closed(self):
        outcome = success_outcome(
            "balances-envelope-001",
            "balances-corr-001",
            balances_payload(),
        )
        result = run_kb_capital_fact_plane(
            adapter=FakeAdapter({"balances": outcome}),
            balances_collect_request=balances_collect_request(),
            balances_raw_fact_id="balances-raw-001",
            balances_normalization_request=balances_request(),
            fact_store=self.store,
            snapshot_identity=identity(),
            portfolio_binding=portfolio_binding(),
            policy=policy(seconds=60),
            now=COLLECTED + timedelta(seconds=120),
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertEqual(
            result.failure_code, "STALE_OR_MISSING_FRESHNESS"
        )
        self.store.get_by_fact_id("balances-raw-001")

    def test_official_fixed_width_blank_currency_maps_to_krw(self):
        # Capital/Portfolio semantic consistency: whitespace-only String(3)
        # blank is domestic KRW candidate; raw broker payload stays untouched.
        raw = ExplicitProviderPayloadEnvelope(
            "holdings-envelope-001",
            "kb_open_api",
            "broker_fact",
            COLLECTED,
            "success",
            holdings_payload(currency="   "),
            None,
            "holdings-corr-001",
        )
        record = self.store.append(
            ExplicitFactAppendRequest("holdings-raw-001", raw, None)
        )
        result = normalize_ssqm2952_capital_facts(
            raw_record=record,
            raw_envelope=raw,
            request=holdings_capital_request(),
        )
        self.assertEqual(
            record.payload["dataBody"]["Record1"][0]["crncy_cd"],
            "   ",
        )
        mv = [
            fact
            for fact in result.facts
            if fact.fact_kind == "kb_ssqm2952_position_market_value"
        ][0]
        self.assertEqual(
            mv.append_request.envelope.payload["currency_code"],
            "KRW",
        )

    def test_usd_row_excluded_with_durable_provenance(self):
        from KbCapitalFactAuthority.models import (
            ExplicitCapitalFactBinding,
            ExplicitHoldingsCapitalNormalizationRequest,
        )

        raw = ExplicitProviderPayloadEnvelope(
            "holdings-envelope-001",
            "kb_open_api",
            "broker_fact",
            COLLECTED,
            "success",
            holdings_payload(currency="USD", clsf="외화증권", symbol="AAPL"),
            None,
            "holdings-corr-001",
        )
        record = self.store.append(
            ExplicitFactAppendRequest("holdings-raw-001", raw, None)
        )
        request = ExplicitHoldingsCapitalNormalizationRequest(
            "holdings-raw-001",
            "account-primary",
            ExplicitCapitalFactBinding("av-f", "av-e", None),
            (),
            "excl-f",
            "excl-e",
        )
        result = normalize_ssqm2952_capital_facts(
            raw_record=record,
            raw_envelope=raw,
            request=request,
        )
        self.assertEqual(len(result.exclusions), 1)
        self.assertEqual(result.exclusions[0].reason, "EXCLUDED_NON_DOMESTIC")
        self.assertEqual(result.exclusions[0].raw_currency_code, "USD")
        self.assertIsNotNone(result.exclusion_provenance_append_request)
        mv = [
            fact
            for fact in result.facts
            if fact.fact_kind == "kb_ssqm2952_position_market_value"
        ]
        self.assertEqual(mv, [])
        excl = self.store.append(result.exclusion_provenance_append_request)
        self.assertEqual(excl.payload["excluded_count"], 1)
        self.assertEqual(excl.payload["domestic_projected_count"], 0)
        self.assertEqual(
            record.payload["dataBody"]["Record1"][0]["crncy_cd"], "USD"
        )

    def test_semantic_safety_rejects_substitute_fields(self):
        for field in (
            "tdy_tfnd_amt",
            "do_psbl_csh",
            "ordr_psbl_amt",
            "mx_ordr_psbl_csh",
            "crdt_ordr_psbl_csh",
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    assert_orderable_cash_field(field)

    def test_orderable_cash_must_match_raw_ordr_psbl_csh(self):
        from KbCapitalFactAuthority.models import ExplicitExactAmount

        amount = ExplicitExactAmount(
            AMOUNT_PRESENCE_PRESENT,
            "1",
            "1",
        )
        with self.assertRaises(ValueError):
            validate_orderable_cash_semantic_safety(
                broker_field="ordr_psbl_csh",
                raw_body={"ordr_psbl_csh": "2"},
                amount=amount,
            )

    def test_no_float_in_amounts(self):
        outcome = success_outcome(
            "balances-envelope-001",
            "balances-corr-001",
            balances_payload(orderable_cash="000000000339901"),
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
        orderable = self.store.get_by_fact_id(
            result.capital_snapshot.orderable_cash_fact_id
        )
        self.assertIsInstance(orderable.payload["amount"], str)
        self.assertNotIsInstance(orderable.payload["amount"], float)

    def test_capital_snapshot_does_not_mutate_portfolio_snapshot(self):
        outcome = success_outcome(
            "balances-envelope-001",
            "balances-corr-001",
            balances_payload(),
        )
        binding = portfolio_binding()
        result = run_kb_capital_fact_plane(
            adapter=FakeAdapter({"balances": outcome}),
            balances_collect_request=balances_collect_request(),
            balances_raw_fact_id="balances-raw-001",
            balances_normalization_request=balances_request(),
            fact_store=self.store,
            snapshot_identity=identity(),
            portfolio_binding=binding,
            policy=policy(),
            now=NOW,
        )
        self.assertEqual(
            result.capital_snapshot.portfolio_snapshot_id,
            binding.portfolio_snapshot_id,
        )
        self.assertEqual(
            result.capital_snapshot.sizing_authority,
            SIZING_AUTHORITY_NONE,
        )

    def test_withdrawable_is_not_orderable_cash_ceiling(self):
        outcome = success_outcome(
            "balances-envelope-001",
            "balances-corr-001",
            balances_payload(
                orderable_cash="000000000100000",
                withdrawable="000000000999999",
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
        orderable = self.store.get_by_fact_id(
            result.capital_snapshot.orderable_cash_fact_id
        )
        withdrawable = self.store.get_by_fact_id(
            result.capital_snapshot.withdrawable_cash_fact_id
        )
        self.assertEqual(orderable.payload["amount"], "100000")
        self.assertEqual(withdrawable.payload["amount"], "999999")
        self.assertEqual(
            withdrawable.payload["authority"],
            "WITHDRAWABLE_NOT_ALLOCATION_CEILING",
        )


class NormalizationUnitTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        path = Path(self.temporary.name) / "facts.sqlite3"
        self.store = FactStore(
            lambda: NOW,
            SQLiteAppendOnlyFactEngine(path),
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_balances_normalization_rejects_float_raw(self):
        payload = balances_payload()
        payload["dataBody"]["ordr_psbl_csh"] = 339901.0
        raw = ExplicitProviderPayloadEnvelope(
            "balances-envelope-001",
            "kb_open_api",
            "broker_fact",
            COLLECTED,
            "success",
            payload,
            None,
            "balances-corr-001",
        )
        record = self.store.append(
            ExplicitFactAppendRequest("balances-raw-001", raw, None)
        )
        with self.assertRaises(TypeError):
            normalize_ssqm0004_balances(
                raw_record=record,
                raw_envelope=raw,
                request=balances_request(),
            )


if __name__ == "__main__":
    unittest.main()
