from __future__ import annotations

import unittest
from decimal import Decimal

from BrokerExecutionCycle.instrument import (
    holdings_is_cd_to_ssam_is_cd,
    seal_instrument_identity_binding,
)
from BrokerExecutionCycle.pretrade import validate_pretrade
from BrokerExecutionCycle.qty import derive_limit_quantity
from BrokerExecutionCycle.reconciliation import reconcile_acceptance_and_fill
from BrokerExecutionCycle.recovery import plan_submission_unknown_recovery
from BrokerExecutionCycle.acceptance import classify_submission_outcome
from BrokerExecutionCycle.models import (
    BrokerAcceptanceClassification,
    FillFact,
    OrderStatusFact,
)
from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.mutation_transport import MockMutationTransport
from BrokerExecutionCycle.tests.helpers import NOW, make_pretrade_bundle, unverified_account
from BrokerExecutionCycle.vocabularies import (
    ACCEPTANCE_ACCEPTED,
    ACCEPTANCE_UNKNOWN,
    FAILURE_ACCEPTANCE_AS_FILL,
    FAILURE_ACCOUNT_UNVERIFIED,
    FAILURE_INSTRUMENT_UNPROVEN,
    FAILURE_MISSING_TRADE_UNIT,
    FILL_CLAIM_NONE,
    FILL_CLAIM_UNKNOWN,
    RECOVERY_AMBIGUOUS,
    RECOVERY_HUMAN_REQUIRED,
    RECON_INCONCLUSIVE,
    SIDE_BUY,
)


class FailClosedMatrixTests(unittest.TestCase):
    def test_instrument_bridge_a005930(self):
        self.assertEqual(holdings_is_cd_to_ssam_is_cd("A005930"), "005930")
        self.assertIsNone(holdings_is_cd_to_ssam_is_cd("005930"))
        self.assertIsNone(holdings_is_cd_to_ssam_is_cd("B005930"))
        self.assertIsNone(holdings_is_cd_to_ssam_is_cd("A00593"))
        binding = seal_instrument_identity_binding(
            binding_id="x",
            portfolio_subject_id="s",
            holdings_is_cd="ZZZ",
        )
        self.assertFalse(binding.proven)

    def test_unproven_instrument_blocks_pretrade(self):
        bundle = make_pretrade_bundle(holdings_is_cd="NOT_A_CODE")
        result = validate_pretrade(
            validation_id="fc1",
            bundle=bundle,
            side=SIDE_BUY,
            approved_notional_krw=Decimal("10000000"),
            validated_at=NOW,
        )
        self.assertFalse(result.passed)
        self.assertIn(FAILURE_INSTRUMENT_UNPROVEN, [f.code for f in result.findings])

    def test_trade_unit_assumed_one_forbidden(self):
        with self.assertRaisesRegex(ValueError, FAILURE_MISSING_TRADE_UNIT):
            derive_limit_quantity(
                approved_notional=Decimal("1000"),
                limit_price=Decimal("10"),
                trade_quantity_unit=None,
            )

    def test_http200_alone_not_accept(self):
        outcome = classify_submission_outcome(
            classification_id="fc2",
            attempt_id="a",
            response=MockMutationTransport(drop_response=True, http_status=200).submit(
                "/x", {}
            ),
            classified_at=NOW,
        )
        self.assertEqual(outcome.outcome, ACCEPTANCE_UNKNOWN)

    def test_acceptance_is_not_fill(self):
        acceptance = BrokerAcceptanceClassification(
            "c",
            "a",
            ACCEPTANCE_ACCEPTED,
            "A",
            "0040000638",
            200,
            "ok",
            NOW,
            "seal",
        )
        # forge seal properly
        acceptance = BrokerAcceptanceClassification(
            "c",
            "a",
            ACCEPTANCE_ACCEPTED,
            "A",
            "0040000638",
            200,
            "ok",
            NOW,
            integrity_seal(
                {
                    "classification_id": "c",
                    "attempt_id": "a",
                    "outcome": ACCEPTANCE_ACCEPTED,
                    "process_flag": "A",
                    "broker_order_no": "0040000638",
                    "http_status": 200,
                    "raw_message": "ok",
                    "classified_at": NOW,
                }
            ),
        )
        recon = reconcile_acceptance_and_fill(
            result_id="r1",
            attempt_id="a",
            acceptance=acceptance,
            fill=None,
            cash_corroborated=None,
            holdings_corroborated=None,
            reconciled_at=NOW,
        )
        self.assertEqual(recon.status, RECON_INCONCLUSIVE)
        self.assertIn(FAILURE_ACCEPTANCE_AS_FILL, recon.detail)

    def test_unknown_recovery_never_reorders(self):
        acceptance = classify_submission_outcome(
            classification_id="fc3",
            attempt_id="a3",
            response=MockMutationTransport(raise_timeout=True).submit("/x", {}),
            classified_at=NOW,
        )
        self.assertEqual(acceptance.outcome, ACCEPTANCE_UNKNOWN)
        plan = plan_submission_unknown_recovery(
            plan_id="p1",
            acceptance=acceptance,
            status_fact=None,
        )
        self.assertFalse(plan.may_reorder)
        self.assertTrue(plan.requires_human)
        self.assertEqual(plan.recovery_mode, RECOVERY_HUMAN_REQUIRED)

        status = OrderStatusFact(
            "sf",
            None,
            None,
            "B",
            "0000000000",
            FILL_CLAIM_UNKNOWN,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "ambiguous",
            NOW,
            "env",
            integrity_seal(
                {
                    "fact_id": "sf",
                    "query_order_no": None,
                    "query_order_date": None,
                    "process_flag": "B",
                    "broker_order_no": "0000000000",
                    "fill_claim": FILL_CLAIM_UNKNOWN,
                    "filled_qty": None,
                    "filled_amount_krw": None,
                    "ordered_qty": None,
                    "remaining_qty": None,
                    "matched_ordr_no": None,
                    "orgn_ordr_no": None,
                    "raw_ccls_ntc_ccd": None,
                    "raw_crct_cncl_ccd": None,
                    "raw_message": "ambiguous",
                    "collected_at": NOW,
                    "raw_envelope_id": "env",
                }
            ),
        )
        plan2 = plan_submission_unknown_recovery(
            plan_id="p2",
            acceptance=acceptance,
            status_fact=status,
        )
        self.assertFalse(plan2.may_reorder)
        self.assertEqual(plan2.recovery_mode, RECOVERY_AMBIGUOUS)

    def test_account_unverified_mutation_false(self):
        acct = unverified_account()
        self.assertFalse(acct.mutation_eligible)
        self.assertEqual(acct.gnl_ac_no1, "")


if __name__ == "__main__":
    unittest.main()
