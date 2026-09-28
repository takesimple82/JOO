from __future__ import annotations

import unittest
from decimal import Decimal

from BrokerExecutionCycle.provider_read import (
    normalize_ivu10140_quote,
    normalize_orderable_cash,
    normalize_sellable_quantity,
    normalize_ssqm2341_status,
)
from BrokerExecutionCycle.service import run_broker_execution_cycle
from BrokerExecutionCycle.mutation_transport import MockMutationTransport
from BrokerExecutionCycle.tests.helpers import (
    NOW,
    load_fixture,
    make_pretrade_bundle,
    sealed_chain,
    verified_account,
    verified_account_allowlist,
)
from BrokerExecutionCycle.vocabularies import (
    ACCEPTANCE_ACCEPTED,
    FILL_CLAIM_UNKNOWN,
    SIDE_BUY,
)
from ProviderGateway.models.vocabularies import BROKER_REQUEST_KIND_VALUES


class ProviderReadNormalizationTests(unittest.TestCase):
    def test_ivu10140_trade_unit(self):
        payload = {"dataHeader": load_fixture("IVU10140.json")["output"]["dataHeader"],
                   "dataBody": load_fixture("IVU10140.json")["output"]["dataBody"]}
        quote = normalize_ivu10140_quote(
            fact_id="q",
            payload=payload,
            instrument_ssam_is_cd="005930",
            collected_at=NOW,
            raw_envelope_id="e",
        )
        self.assertEqual(quote.trade_quantity_unit, Decimal("1"))
        self.assertGreater(quote.now_price, Decimal("0"))

    def test_ssqm0004_cash(self):
        payload = load_fixture("SSQM0004.json")["output"]
        cash = normalize_orderable_cash(
            fact_id="c",
            payload=payload,
            collected_at=NOW,
            raw_envelope_id="e",
        )
        self.assertEqual(cash.amount_krw, Decimal("339901"))

    def test_ssqm1801_sellable(self):
        payload = load_fixture("SSQM1801.json")["output"]
        sell = normalize_sellable_quantity(
            fact_id="s",
            payload=payload,
            instrument_ssam_is_cd="005930",
            collected_at=NOW,
            raw_envelope_id="e",
        )
        self.assertEqual(sell.sellable_qty, Decimal("1"))

    def test_ssqm2341_insufficient_fill_unknown(self):
        payload = load_fixture("SSQM2341.json")["output"]
        status = normalize_ssqm2341_status(
            fact_id="st",
            payload=payload,
            query_order_no=None,
            query_order_date="20260623",
            collected_at=NOW,
            raw_envelope_id="e",
        )
        self.assertEqual(status.fill_claim, FILL_CLAIM_UNKNOWN)

    def test_gateway_request_kinds_include_block_c_reads(self):
        for kind in (
            "quote",
            "order_status",
            "sell_orderability",
            "cash_orderability",
            "holdings",
            "balances",
        ):
            self.assertIn(kind, BROKER_REQUEST_KIND_VALUES)


class ServiceCycleTests(unittest.TestCase):
    def test_full_mock_cycle_accept(self):
        _hip, _snap, _prop, approval, artifact = sealed_chain()
        bundle = make_pretrade_bundle()
        result = run_broker_execution_cycle(
            intent_id="intent-svc-1",
            authorization_id="tea-svc-1",
            attempt_id="att-svc-1",
            classification_id="cls-svc-1",
            side=SIDE_BUY,
            portfolio_subject_id="CAND-B",
            approved_notional_krw=Decimal("10000000"),
            bundle=bundle,
            artifact=artifact,
            approval=approval,
            account=verified_account(),
            account_allowlist=verified_account_allowlist(),
            now=NOW,
            principal="human-operator",
            transport=MockMutationTransport(),
            durable_pre_send_appender=lambda *_: None,
        )
        self.assertEqual(result.result_kind, "success")
        self.assertIsNotNone(result.order_intent)
        self.assertIsNotNone(result.tea)
        self.assertIsNotNone(result.attempt)
        self.assertEqual(result.acceptance.outcome, ACCEPTANCE_ACCEPTED)
        self.assertTrue(result.attempt.durable_pre_send)


if __name__ == "__main__":
    unittest.main()
