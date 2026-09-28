from __future__ import annotations

import hashlib
import unittest
from decimal import Decimal
from pathlib import Path

from BrokerExecutionCycle.account_allowlist import (
    require_account_on_allowlist,
    seal_execution_account_allowlist,
)
from BrokerExecutionCycle.authority_evidence import (
    AUTHORITY_CLAIMS,
    KB_EXCEL_PATH,
    KB_EXCEL_SHA256,
    KB_NATIVE_IDEMPOTENCY,
    KB_SAMPLE_ZIP_PATH,
    KB_SAMPLE_ZIP_SHA256,
    PROVENANCE_NONE_DOCUMENTED,
    SSAM_ACCOUNT_BINDING_FIELD,
    SSAM_EXCEL_REQUIRED_INPUT_FIELDS,
    UNKNOWN_MAY_AUTORESUBMIT,
    UNKNOWN_RECOVERY_POLICY,
    assert_phase2_authorities_registered,
)
from BrokerExecutionCycle.cancel_modify import (
    CANCEL_MODIFY_POLICY,
    CANCEL_MODIFY_STATE_UNKNOWN,
    assert_no_auto_cancel_modify,
    draft_cancel_request,
    draft_modify_request,
    map_cancel_modify_terminal_state,
)
from BrokerExecutionCycle.kb_idempotency import (
    assert_no_kb_native_idempotency_claim,
    kb_native_idempotency_status,
)
from BrokerExecutionCycle.mutation_transport import LiveMutationTransportDisabled
from BrokerExecutionCycle.provider_read import normalize_ssqm2341_status
from BrokerExecutionCycle.recovery import assert_unknown_must_not_autoresubmit
from BrokerExecutionCycle.shadow_dry_run import run_read_only_shadow_dry_run
from BrokerExecutionCycle.tests.helpers import (
    NOW,
    load_fixture,
    make_pretrade_bundle,
    sealed_chain,
    unverified_account,
    verified_account,
)
from BrokerExecutionCycle.translation import translate_order_intent_to_ssam
from BrokerExecutionCycle.vocabularies import (
    ACCOUNT_ALLOWLIST_MISMATCH,
    ACCEPTANCE_ACCEPTED,
    FAILURE_LIVE_MUTATION_DISABLED,
    FILL_CLAIM_FULL,
    FILL_CLAIM_NONE,
    FILL_CLAIM_PARTIAL,
    FILL_CLAIM_UNKNOWN,
    RECOVERY_POLICY_QUERY_THEN_HUMAN,
    SIDE_BUY,
    SSAM_FIELD_GNL_AC_NO1,
)


def _status_payload(*, process_flag: str, records: list) -> dict:
    return {
        "dataHeader": {
            "resultCode": "200",
            "resultMessage": "성공",
            "processFlag": process_flag,
            "processMessage": "",
            "processCode": "0000",
            "processTime": "20260623100000000",
        },
        "dataBody": {
            "o_msg": "정상적으로 조회되었습니다." if process_flag == "A" else "err",
            "ordr_no": "0000000000",
            "grid_cnt1": f"{len(records):04d}",
            "Record1": records,
        },
    }


class Phase2EvidenceTests(unittest.TestCase):
    def test_authorities_a_through_g_registered(self):
        assert_phase2_authorities_registered()
        self.assertEqual({c.authority_id for c in AUTHORITY_CLAIMS}, set("ABCDEFG"))

    def test_official_artifacts_hashes(self):
        excel = Path(KB_EXCEL_PATH)
        sample = Path(KB_SAMPLE_ZIP_PATH)
        self.assertTrue(excel.is_file())
        self.assertTrue(sample.is_file())
        self.assertEqual(
            hashlib.sha256(excel.read_bytes()).hexdigest(), KB_EXCEL_SHA256
        )
        self.assertEqual(
            hashlib.sha256(sample.read_bytes()).hexdigest(), KB_SAMPLE_ZIP_SHA256
        )

    def test_account_field_is_sample_observed_gnl_ac_no1(self):
        self.assertEqual(SSAM_ACCOUNT_BINDING_FIELD, "gnl_ac_no1")
        self.assertEqual(SSAM_FIELD_GNL_AC_NO1, "gnl_ac_no1")
        self.assertIn("mkt_tm_clsf", SSAM_EXCEL_REQUIRED_INPUT_FIELDS)
        self.assertNotIn("gnl_ac_no1", SSAM_EXCEL_REQUIRED_INPUT_FIELDS)

    def test_kb_native_idempotency_none(self):
        status = kb_native_idempotency_status()
        self.assertEqual(status["status"], PROVENANCE_NONE_DOCUMENTED)
        self.assertEqual(KB_NATIVE_IDEMPOTENCY, PROVENANCE_NONE_DOCUMENTED)
        assert_no_kb_native_idempotency_claim(None)
        with self.assertRaises(ValueError):
            assert_no_kb_native_idempotency_claim("KB native idempotency key exists")


class Phase2FillSemanticsTests(unittest.TestCase):
    def test_official_sample_remains_unknown(self):
        payload = load_fixture("SSQM2341.json")["output"]
        status = normalize_ssqm2341_status(
            fact_id="st-sample",
            payload=payload,
            query_order_no="0040000638",
            query_order_date="20260623",
            collected_at=NOW,
            raw_envelope_id="e",
        )
        self.assertEqual(status.fill_claim, FILL_CLAIM_UNKNOWN)

    def test_http200_alone_never_fill(self):
        payload = _status_payload(process_flag="B", records=[])
        status = normalize_ssqm2341_status(
            fact_id="st-http",
            payload=payload,
            query_order_no="0040000638",
            query_order_date="20260623",
            collected_at=NOW,
            raw_envelope_id="e",
        )
        self.assertEqual(status.fill_claim, FILL_CLAIM_UNKNOWN)

    def test_excel_qty_none_partial_full(self):
        cases = [
            ("5", "0", "5", FILL_CLAIM_NONE),
            ("5", "2", "3", FILL_CLAIM_PARTIAL),
            ("5", "5", "0", FILL_CLAIM_FULL),
            ("5", "2", "2", FILL_CLAIM_UNKNOWN),  # inconsistent
        ]
        for ordered, filled, remaining, expected in cases:
            with self.subTest(ordered=ordered, filled=filled, remaining=remaining):
                payload = _status_payload(
                    process_flag="A",
                    records=[
                        {
                            "ordr_no": "0040000638",
                            "orgn_ordr_no": "0000000000",
                            "ordr_q": ordered,
                            "tl_ccls_q": filled,
                            "nccls_q": remaining,
                            "ccls_ntc_ccd": "X",  # undocumented enum → raw only
                            "crct_cncl_ccd": "",
                        }
                    ],
                )
                status = normalize_ssqm2341_status(
                    fact_id="st-qty",
                    payload=payload,
                    query_order_no="0040000638",
                    query_order_date="20260623",
                    collected_at=NOW,
                    raw_envelope_id="e",
                )
                self.assertEqual(status.fill_claim, expected)
                if expected != FILL_CLAIM_UNKNOWN:
                    self.assertEqual(status.ordered_qty, Decimal(ordered))
                    self.assertEqual(status.filled_qty, Decimal(filled))
                    self.assertEqual(status.remaining_qty, Decimal(remaining))
                    self.assertEqual(status.matched_ordr_no, "0040000638")


class Phase2CancelModifyTests(unittest.TestCase):
    def test_no_auto_policy(self):
        self.assertEqual(CANCEL_MODIFY_POLICY, "DEFERRED_NO_AUTO_POLICY")
        with self.assertRaises(RuntimeError):
            assert_no_auto_cancel_modify()

    def test_modify_cancel_drafts(self):
        mod = draft_modify_request(
            ssam_is_cd="005930",
            orgn_ordr_no="0040000638",
            limit_price=Decimal("370000"),
            quantity=Decimal("5"),
            crct_clsf="2",
        )
        self.assertTrue(mod.ready)
        self.assertEqual(mod.api_path, "/api/v1/ssam1805")
        cancel = draft_cancel_request(
            ssam_is_cd="005930",
            orgn_ordr_no="0040000638",
            crct_clsf="2",
        )
        self.assertTrue(cancel.ready)
        self.assertEqual(cancel.api_path, "/api/v1/ssam1806")
        self.assertEqual(
            map_cancel_modify_terminal_state(
                remaining_qty=Decimal("0"),
                fill_claim=FILL_CLAIM_FULL,
                raw_crct_cncl_ccd="??",
            ),
            CANCEL_MODIFY_STATE_UNKNOWN,
        )


class Phase2AllowlistAndShadowTests(unittest.TestCase):
    def test_allowlist_fail_closed(self):
        allow = seal_execution_account_allowlist(
            allowlist_id="al-1",
            allowed_gnl_ac_no1=("400277078",),
        )
        require_account_on_allowlist(verified_account(), allow)
        with self.assertRaises(ValueError) as ctx:
            require_account_on_allowlist(unverified_account(), allow)
        self.assertIn("ACCOUNT", str(ctx.exception))
        other = seal_execution_account_allowlist(
            allowlist_id="al-2",
            allowed_gnl_ac_no1=("999999999",),
        )
        with self.assertRaises(ValueError) as ctx2:
            require_account_on_allowlist(verified_account(), other)
        self.assertEqual(str(ctx2.exception), ACCOUNT_ALLOWLIST_MISMATCH)

    def test_shadow_dry_run_hits_live_disabled_no_real_submit(self):
        self.assertEqual(UNKNOWN_RECOVERY_POLICY, RECOVERY_POLICY_QUERY_THEN_HUMAN)
        self.assertFalse(UNKNOWN_MAY_AUTORESUBMIT)
        assert_unknown_must_not_autoresubmit(may_reorder=False, may_autoresubmit=False)
        with self.assertRaises(RuntimeError):
            assert_unknown_must_not_autoresubmit(may_reorder=True, may_autoresubmit=False)

        _hip, _snap, _prop, approval, artifact = sealed_chain()
        bundle = make_pretrade_bundle()
        allow = seal_execution_account_allowlist(
            allowlist_id="al-shadow",
            allowed_gnl_ac_no1=("400277078",),
        )
        result = run_read_only_shadow_dry_run(
            intent_id="intent-shadow-1",
            authorization_id="tea-shadow-1",
            classification_id="cls-shadow-1",
            recon_id="recon-shadow-1",
            side=SIDE_BUY,
            portfolio_subject_id="CAND-B",
            approved_notional_krw=Decimal("10000000"),
            bundle=bundle,
            artifact=artifact,
            approval=approval,
            account=verified_account(),
            allowlist=allow,
            now=NOW,
            principal="human-operator",
        )
        self.assertFalse(result.real_mutation_submitted)
        self.assertEqual(result.live_boundary_error, FAILURE_LIVE_MUTATION_DISABLED)
        self.assertEqual(result.transport_mode_at_boundary, "LIVE_DISABLED")
        self.assertTrue(result.translation.ready)
        self.assertEqual(
            result.translation.data_body[SSAM_FIELD_GNL_AC_NO1], "400277078"
        )
        for field in SSAM_EXCEL_REQUIRED_INPUT_FIELDS:
            self.assertIn(field, result.translation.data_body)
            self.assertNotEqual(result.translation.data_body[field], "")
        self.assertEqual(result.shadow_acceptance.outcome, ACCEPTANCE_ACCEPTED)
        # Live transport still disabled independently.
        with self.assertRaises(RuntimeError):
            LiveMutationTransportDisabled().submit("/api/v1/ssam1802", {})


if __name__ == "__main__":
    unittest.main()
