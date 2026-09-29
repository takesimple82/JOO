from __future__ import annotations

import unittest
from decimal import Decimal

from BrokerExecutionCycle.authorization import initial_mutation_authority
from BrokerExecutionCycle.cancel_modify import assert_no_auto_cancel_modify
from BrokerExecutionCycle.mutation_gate import execute_mutation_attempt
from BrokerExecutionCycle.mutation_transport import MockMutationTransport
from BrokerExecutionCycle.open_limit_monitor import (
    OPEN_LIMIT_STATUS_OPEN,
    OPEN_LIMIT_STATUS_UNKNOWN,
    assert_open_limit_never_auto_mutates,
    classify_open_limit_status,
    seal_open_limit_human_attention,
)
from BrokerExecutionCycle.tea_freshness import assert_jit_fresh_facts_permit_exact_execution
from BrokerExecutionCycle.tests.helpers import (
    NOW,
    fresh_cash_fact,
    make_pretrade_bundle,
    sealed_chain,
    verified_account,
    verified_account_allowlist,
)
from BrokerExecutionCycle.translation import translate_order_intent_to_ssam
from BrokerExecutionCycle.vocabularies import (
    FAILURE_BUY_CASH_INSUFFICIENT,
    FAILURE_OPEN_LIMIT_AUTO_POLICY,
    FILL_CLAIM_NONE,
    FILL_CLAIM_PARTIAL,
    FILL_CLAIM_UNKNOWN,
    OPEN_LIMIT_POLICY,
    SIDE_BUY,
)
from BrokerExecutionCycle.authorization import issue_trade_execution_authorization
from BrokerExecutionCycle.intent import seal_limit_order_intent
from BrokerExecutionCycle.pretrade import validate_pretrade
from BrokerExecutionCycle.models import OrderStatusFact
from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.authority_evidence import CANCEL_MODIFY_AUTO_POLICY


class Phase4JitTeaTests(unittest.TestCase):
    def _intent_tea(self):
        _hip, _snap, _prop, approval, artifact = sealed_chain()
        bundle = make_pretrade_bundle(side=SIDE_BUY, cash_amount="50000000")
        validation = validate_pretrade(
            validation_id="v-jit",
            bundle=bundle,
            side=SIDE_BUY,
            approved_notional_krw=Decimal("10000000"),
            validated_at=NOW,
        )
        self.assertTrue(validation.passed)
        intent = seal_limit_order_intent(
            intent_id="intent-jit",
            side=SIDE_BUY,
            portfolio_subject_id="CAND-B",
            bundle=bundle,
            validation=validation,
            artifact=artifact,
            approval=approval,
            sealed_at=NOW,
        )
        tea = issue_trade_execution_authorization(
            authorization_id="tea-jit",
            order_intent=intent,
            artifact=artifact,
            approval=approval,
            authorized_at=NOW,
            principal="human-operator",
        )
        return intent, tea, bundle

    def test_jit_insufficient_fresh_cash_blocks_before_transport(self):
        intent, tea, _bundle = self._intent_tea()
        account = verified_account()
        translation = translate_order_intent_to_ssam(
            translation_id="tr-jit-cash", order_intent=intent, account=account,
        )
        transport = MockMutationTransport()
        with self.assertRaisesRegex(ValueError, FAILURE_BUY_CASH_INSUFFICIENT):
            execute_mutation_attempt(
                attempt_id="att-jit-cash",
                tea=tea,
                order_intent=intent,
                translation=translation,
                account=account,
                account_allowlist=verified_account_allowlist(),
                authority=initial_mutation_authority(tea),
                attempted_at=NOW,
                fresh_orderable_cash=fresh_cash_fact(amount="1"),
                transport=transport,
                durable_pre_send_appender=lambda *_: None,
            )
        self.assertEqual(transport.calls, [])

    def test_jit_exact_cash_permits_mock_submit(self):
        intent, tea, _bundle = self._intent_tea()
        account = verified_account()
        translation = translate_order_intent_to_ssam(
            translation_id="tr-jit-ok", order_intent=intent, account=account,
        )
        needed = intent.limit_price * intent.quantity
        transport = MockMutationTransport()
        execute_mutation_attempt(
            attempt_id="att-jit-ok",
            tea=tea,
            order_intent=intent,
            translation=translation,
            account=account,
            account_allowlist=verified_account_allowlist(),
            authority=initial_mutation_authority(tea),
            attempted_at=NOW,
            fresh_orderable_cash=fresh_cash_fact(amount=format(needed, "f")),
            transport=transport,
            durable_pre_send_appender=lambda *_: None,
        )
        self.assertEqual(len(transport.calls), 1)

    def test_assert_jit_rejects_wrong_broker_field(self):
        intent, tea, bundle = self._intent_tea()
        from dataclasses import replace
        bad = replace(bundle.orderable_cash, broker_field="ordr_psbl_amt")
        # seal won't match replace without reseal — function checks field name first
        with self.assertRaises(ValueError):
            assert_jit_fresh_facts_permit_exact_execution(
                tea=tea,
                order_intent=intent,
                account=verified_account(),
                fresh_orderable_cash=bad,
                fresh_sellable=None,
                refreshed_at=NOW,
            )


class Phase4OpenLimitTests(unittest.TestCase):
    def _status(self, *, fill_claim, remaining, ordered="5", filled="0", order_no="0040000638"):
        payload = {
            "fact_id": "st-1",
            "query_order_no": order_no,
            "query_order_date": "20260623",
            "process_flag": "A",
            "broker_order_no": order_no,
            "fill_claim": fill_claim,
            "filled_qty": Decimal(filled),
            "filled_amount_krw": None,
            "ordered_qty": Decimal(ordered),
            "remaining_qty": Decimal(remaining) if remaining is not None else None,
            "matched_ordr_no": order_no,
            "orgn_ordr_no": None,
            "raw_ccls_ntc_ccd": None,
            "raw_crct_cncl_ccd": None,
            "raw_message": None,
            "collected_at": NOW,
            "raw_envelope_id": "env-st-1",
        }
        return OrderStatusFact(
            payload["fact_id"],
            payload["query_order_no"],
            payload["query_order_date"],
            payload["process_flag"],
            payload["broker_order_no"],
            payload["fill_claim"],
            payload["filled_qty"],
            payload["filled_amount_krw"],
            payload["ordered_qty"],
            payload["remaining_qty"],
            payload["matched_ordr_no"],
            payload["orgn_ordr_no"],
            payload["raw_ccls_ntc_ccd"],
            payload["raw_crct_cncl_ccd"],
            payload["raw_message"],
            payload["collected_at"],
            payload["raw_envelope_id"],
            integrity_seal(payload),
        )

    def test_open_limit_escalates_to_human_attention(self):
        status = self._status(fill_claim=FILL_CLAIM_NONE, remaining="5")
        self.assertEqual(classify_open_limit_status(status), OPEN_LIMIT_STATUS_OPEN)
        signal = seal_open_limit_human_attention(
            signal_id="sig-open-1",
            account_binding_id="acct-bind-001",
            status_fact=status,
            observed_at=NOW,
        )
        self.assertEqual(signal.auto_policy, CANCEL_MODIFY_AUTO_POLICY)
        self.assertEqual(signal.open_limit_policy, OPEN_LIMIT_POLICY)
        self.assertIn("human must decide", signal.why_human_needed)
        self.assertEqual(signal.broker_order_no, "0040000638")
        self.assertEqual(signal.remaining_qty, Decimal("5"))

    def test_unknown_open_limit_escalates(self):
        status = self._status(fill_claim=FILL_CLAIM_UNKNOWN, remaining=None)
        self.assertEqual(classify_open_limit_status(status), OPEN_LIMIT_STATUS_UNKNOWN)
        signal = seal_open_limit_human_attention(
            signal_id="sig-unk-1",
            account_binding_id="acct-bind-001",
            status_fact=status,
            observed_at=NOW,
        )
        self.assertIn("UNKNOWN", signal.why_human_needed)

    def test_open_limit_never_auto_mutates(self):
        with self.assertRaisesRegex(RuntimeError, "CANCEL_MODIFY_NO_AUTO_POLICY"):
            assert_open_limit_never_auto_mutates()
        with self.assertRaisesRegex(RuntimeError, "CANCEL_MODIFY_NO_AUTO_POLICY"):
            assert_no_auto_cancel_modify()


if __name__ == "__main__":
    unittest.main()
