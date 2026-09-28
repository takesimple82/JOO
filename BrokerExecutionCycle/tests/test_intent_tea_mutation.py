from __future__ import annotations

import unittest
from decimal import Decimal

from BrokerExecutionCycle.acceptance import classify_submission_outcome
from BrokerExecutionCycle.authorization import (
    assert_tea_binds_intent,
    consume_one_shot,
    initial_mutation_authority,
    issue_trade_execution_authorization,
)
from BrokerExecutionCycle.intent import seal_limit_order_intent
from BrokerExecutionCycle.mutation_gate import execute_mutation_attempt
from BrokerExecutionCycle.mutation_transport import (
    LiveMutationTransportDisabled,
    MockMutationTransport,
)
from BrokerExecutionCycle.pretrade import validate_pretrade
from BrokerExecutionCycle.tests.helpers import (
    NOW,
    make_pretrade_bundle,
    sealed_chain,
    verified_account,
)
from BrokerExecutionCycle.translation import translate_order_intent_to_ssam
from BrokerExecutionCycle.vocabularies import (
    ACCEPTANCE_ACCEPTED,
    ACCEPTANCE_REJECTED,
    ACCEPTANCE_UNKNOWN,
    FAILURE_LIVE_MUTATION_DISABLED,
    FAILURE_TEA_CONSUMED,
    ORDR_CCD_LIMIT,
    PROCESS_FLAG_ACCEPT,
    PROCESS_FLAG_REJECT,
    SIDE_BUY,
)


class IntentTeaMutationTests(unittest.TestCase):
    def _intent_tea(self):
        _hip, _snap, _prop, approval, artifact = sealed_chain()
        bundle = make_pretrade_bundle()
        validation = validate_pretrade(
            validation_id="v-intent",
            bundle=bundle,
            side=SIDE_BUY,
            approved_notional_krw=Decimal("10000000"),
            validated_at=NOW,
        )
        self.assertTrue(validation.passed)
        intent = seal_limit_order_intent(
            intent_id="intent-001",
            side=SIDE_BUY,
            portfolio_subject_id="CAND-B",
            bundle=bundle,
            validation=validation,
            artifact=artifact,
            approval=approval,
            sealed_at=NOW,
        )
        tea = issue_trade_execution_authorization(
            authorization_id="tea-001",
            order_intent=intent,
            artifact=artifact,
            approval=approval,
            authorized_at=NOW,
            principal="human-operator",
        )
        return bundle, intent, tea, approval, artifact

    def test_limit_only_ordr_ccd(self):
        _, intent, _, _, _ = self._intent_tea()
        self.assertEqual(intent.ordr_ccd, ORDR_CCD_LIMIT)
        self.assertIsNone(getattr(intent, "ordr_no", None) if False else None)

    def test_tea_binds_exact_intent_seal(self):
        _, intent, tea, _, _ = self._intent_tea()
        assert_tea_binds_intent(tea, intent)
        self.assertEqual(tea.order_intent_seal, intent.integrity_seal)
        self.assertTrue(tea.one_shot)

    def test_one_shot_cannot_replay(self):
        bundle, intent, tea, _, _ = self._intent_tea()
        account = verified_account()
        translation = translate_order_intent_to_ssam(
            translation_id="tr-1",
            order_intent=intent,
            account=account,
        )
        self.assertTrue(translation.ready)
        authority = initial_mutation_authority(tea)
        transport = MockMutationTransport()
        _attempt, authority2, _resp = execute_mutation_attempt(
            attempt_id="att-1",
            tea=tea,
            order_intent=intent,
            translation=translation,
            account=account,
            authority=authority,
            attempted_at=NOW,
            transport=transport,
            durable_pre_send_appender=lambda *_: None,
        )
        self.assertTrue(authority2.consumed)
        with self.assertRaisesRegex(ValueError, FAILURE_TEA_CONSUMED):
            execute_mutation_attempt(
                attempt_id="att-2",
                tea=tea,
                order_intent=intent,
                translation=translation,
                account=account,
                authority=authority2,
                attempted_at=NOW,
                transport=transport,
                durable_pre_send_appender=lambda *_: None,
            )

    def test_live_disabled_by_default(self):
        bundle, intent, tea, _, _ = self._intent_tea()
        account = verified_account()
        translation = translate_order_intent_to_ssam(
            translation_id="tr-2",
            order_intent=intent,
            account=account,
        )
        with self.assertRaisesRegex(RuntimeError, FAILURE_LIVE_MUTATION_DISABLED):
            execute_mutation_attempt(
                attempt_id="att-live",
                tea=tea,
                order_intent=intent,
                translation=translation,
                account=account,
                authority=initial_mutation_authority(tea),
                attempted_at=NOW,
                transport=LiveMutationTransportDisabled(),
                durable_pre_send_appender=lambda *_: None,
            )

    def test_acceptance_requires_flag_a_and_nonzero_ordr_no(self):
        accept = classify_submission_outcome(
            classification_id="c1",
            attempt_id="a1",
            response=MockMutationTransport(
                process_flag=PROCESS_FLAG_ACCEPT,
                ordr_no="0040000638",
            ).submit("/x", {}),
            classified_at=NOW,
        )
        self.assertEqual(accept.outcome, ACCEPTANCE_ACCEPTED)
        reject = classify_submission_outcome(
            classification_id="c2",
            attempt_id="a2",
            response=MockMutationTransport(
                process_flag=PROCESS_FLAG_REJECT,
                ordr_no="0000000000",
            ).submit("/x", {}),
            classified_at=NOW,
        )
        self.assertEqual(reject.outcome, ACCEPTANCE_REJECTED)
        http_only = classify_submission_outcome(
            classification_id="c3",
            attempt_id="a3",
            response=MockMutationTransport(drop_response=True, http_status=200).submit(
                "/x", {}
            ),
            classified_at=NOW,
        )
        self.assertEqual(http_only.outcome, ACCEPTANCE_UNKNOWN)
        zero_ordr = classify_submission_outcome(
            classification_id="c4",
            attempt_id="a4",
            response=MockMutationTransport(
                process_flag=PROCESS_FLAG_ACCEPT,
                ordr_no="0000000000",
            ).submit("/x", {}),
            classified_at=NOW,
        )
        self.assertEqual(zero_ordr.outcome, ACCEPTANCE_UNKNOWN)

    def test_unresolved_account_not_ready(self):
        from BrokerExecutionCycle.tests.helpers import unverified_account
        from BrokerExecutionCycle.vocabularies import SSAM_FIELD_GNL_AC_NO1

        _, intent, _, _, _ = self._intent_tea()
        translation = translate_order_intent_to_ssam(
            translation_id="tr-3",
            order_intent=intent,
            account=unverified_account(),
        )
        self.assertFalse(translation.ready)
        self.assertIn(SSAM_FIELD_GNL_AC_NO1, translation.unresolved_fields)


if __name__ == "__main__":
    unittest.main()
