from __future__ import annotations

import unittest
from decimal import Decimal

from InvestmentDecisionVerticalSlice.models import (
    CioActionPosture,
    ComparisonStatus,
    JournalAppend,
    JournalRecordKind,
    OpportunityRole,
)
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal

from CapitalAllocationCycle.allocator import allocate_capital
from CapitalAllocationCycle.approval import record_investment_human_approval
from CapitalAllocationCycle.artifact import seal_approved_allocation_artifact
from CapitalAllocationCycle.constraints import derive_action
from CapitalAllocationCycle.hip import build_frozen_hip_v1
from CapitalAllocationCycle.tests.helpers import (
    NOW,
    UTC,
    base_request,
    cio_decision,
    comparison,
    evaluation,
    member,
    position,
    proposed,
    resolved_cash,
    subject,
    universe,
)
from CapitalAllocationCycle.vocabularies import (
    ALLOCATION_ACTION_EXIT,
    ALLOCATION_ACTION_INCREASE,
    ALLOCATION_ACTION_MAINTAIN,
    ALLOCATION_ACTION_REDUCE,
    AMOUNT_PRESENCE_MISSING,
    APPROVAL_DECISION_APPROVED,
    APPROVAL_DECISION_NEEDS_REVISION,
    APPROVAL_DECISION_REJECTED,
    FAILURE_CASH_CONSERVATION_VIOLATION,
    FAILURE_INCREASE_CAPACITY_ZERO,
    FAILURE_MAX_POSITION_EXCEEDED,
    FAILURE_MISSING_ORDERABLE_CASH,
    FAILURE_POSTURE_BLOCKS_INCREASE,
    FAILURE_ROTATION_REQUIRES_EV_SUPERIORITY,
    FAILURE_WATCHLIST_ONLY_INELIGIBLE,
)
from OperationalCioCycle.codec import decode, encode


class AllocationSuiteTests(unittest.TestCase):
    """Focused Block B suite covering frozen HIP/constraint contract items."""

    # --- HIP / deployable authority ---
    def test_01_deployable_equals_orderable_cash(self):
        result = allocate_capital(base_request(cash=resolved_cash("339901")))
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(
            result.proposal.funding.deployable_orderable_cash_krw,
            Decimal("339901"),
        )

    def test_02_explicit_reserve_zero_subtracted(self):
        result = allocate_capital(base_request())
        self.assertEqual(result.proposal.funding.explicit_reserve_krw, Decimal("0"))
        self.assertEqual(
            result.proposal.funding.deployable_after_reserve_krw,
            result.proposal.funding.deployable_orderable_cash_krw,
        )

    def test_03_missing_orderable_cash_fail_closed(self):
        result = allocate_capital(
            base_request(
                cash=resolved_cash(presence=AMOUNT_PRESENCE_MISSING),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "20000000"),),
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIn(FAILURE_MISSING_ORDERABLE_CASH, result.failure_codes)

    def test_04_present_zero_orderable_is_not_missing(self):
        result = allocate_capital(
            base_request(
                cash=resolved_cash("0"),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "20000000"),),
                decisions=(cio_decision(posture=CioActionPosture.MAINTAIN),),
                comparisons=(),
                evaluations=(),
            )
        )
        # MAINTAIN preserve succeeds with zero cash when no increase.
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(
            result.proposal.funding.deployable_orderable_cash_krw,
            Decimal("0"),
        )

    def test_05_cap_snapshot_sizing_authority_preserved(self):
        request = base_request()
        self.assertEqual(
            request.capital_snapshot.sizing_authority,
            "NOT_SIZING_AUTHORITY",
        )
        result = allocate_capital(request)
        self.assertEqual(result.result_kind, "success")

    def test_06_valuation_fact_not_used_as_deployable(self):
        request = base_request(cash=resolved_cash("1000"))
        # Valuation fact id exists but deployable must track orderable cash only.
        self.assertNotEqual(
            request.capital_snapshot.broker_reported_account_valuation_fact_id,
            request.capital_snapshot.orderable_cash_fact_id,
        )
        result = allocate_capital(
            base_request(
                cash=resolved_cash("1000"),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "20000000"),),
                decisions=(cio_decision(posture=CioActionPosture.MAINTAIN),),
                comparisons=(),
                evaluations=(),
            )
        )
        self.assertEqual(
            result.proposal.funding.deployable_orderable_cash_krw,
            Decimal("1000"),
        )

    # --- Actions ---
    def test_07_derive_increase(self):
        self.assertEqual(derive_action(Decimal("1"), Decimal("2")), ALLOCATION_ACTION_INCREASE)

    def test_08_derive_maintain(self):
        self.assertEqual(derive_action(Decimal("5"), Decimal("5")), ALLOCATION_ACTION_MAINTAIN)

    def test_09_derive_reduce(self):
        self.assertEqual(derive_action(Decimal("5"), Decimal("3")), ALLOCATION_ACTION_REDUCE)

    def test_10_derive_exit(self):
        self.assertEqual(derive_action(Decimal("5"), Decimal("0")), ALLOCATION_ACTION_EXIT)

    # --- CIO posture admission ---
    def test_11_maintain_blocks_increase(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        result = allocate_capital(
            base_request(
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.MAINTAIN,
                        comparison_ids=("cmp-001",),
                    ),
                ),
                evaluations=(left,),
                comparisons=(
                    comparison("cmp-001", left, left, ComparisonStatus.EQUAL),
                ),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "30000000"),),
                positions=(position("HOLD-A", "20000000"),),
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIn(FAILURE_POSTURE_BLOCKS_INCREASE, result.failure_codes)

    def test_12_maintain_allows_preserve(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        result = allocate_capital(
            base_request(
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.MAINTAIN,
                        comparison_ids=("cmp-001",),
                    ),
                ),
                evaluations=(left,),
                comparisons=(
                    comparison("cmp-001", left, left, ComparisonStatus.EQUAL),
                ),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "20000000"),),
                positions=(position("HOLD-A", "20000000"),),
            )
        )
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(result.proposal.legs[0].action, ALLOCATION_ACTION_MAINTAIN)

    def test_13_consider_rotation_with_ev_superiority(self):
        result = allocate_capital(base_request())
        self.assertEqual(result.result_kind, "success")
        actions = {leg.portfolio_subject_id: leg.action for leg in result.proposal.legs}
        self.assertEqual(actions["HOLD-A"], ALLOCATION_ACTION_REDUCE)
        self.assertEqual(actions["CAND-B"], ALLOCATION_ACTION_INCREASE)

    def test_14_consider_rotation_without_ev_superiority_fails(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        right = evaluation("opp-cand", "CAND-B", OpportunityRole.CANDIDATE)
        result = allocate_capital(
            base_request(
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.CONSIDER_ROTATION,
                        comparison_ids=("cmp-001",),
                        superior=None,
                    ),
                ),
                evaluations=(left, right),
                comparisons=(
                    comparison("cmp-001", left, right, ComparisonStatus.EQUAL),
                ),
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIn(FAILURE_ROTATION_REQUIRES_EV_SUPERIORITY, result.failure_codes)

    def test_15_invalidate_blocks_increase(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        result = allocate_capital(
            base_request(
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.INVALIDATE_THESIS,
                        comparison_ids=("cmp-001",),
                    ),
                ),
                evaluations=(left,),
                comparisons=(
                    comparison("cmp-001", left, left, ComparisonStatus.EQUAL),
                ),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "30000000"),),
                positions=(position("HOLD-A", "20000000"),),
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIn(FAILURE_POSTURE_BLOCKS_INCREASE, result.failure_codes)

    def test_16_invalidate_allows_reduce(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        result = allocate_capital(
            base_request(
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.INVALIDATE_THESIS,
                        comparison_ids=("cmp-001",),
                    ),
                ),
                evaluations=(left,),
                comparisons=(
                    comparison("cmp-001", left, left, ComparisonStatus.EQUAL),
                ),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "5000000"),),
                positions=(position("HOLD-A", "20000000"),),
            )
        )
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(result.proposal.legs[0].action, ALLOCATION_ACTION_REDUCE)

    def test_17_invalidate_allows_exit(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        result = allocate_capital(
            base_request(
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.INVALIDATE_THESIS,
                        comparison_ids=("cmp-001",),
                    ),
                ),
                evaluations=(left,),
                comparisons=(
                    comparison("cmp-001", left, left, ComparisonStatus.EQUAL),
                ),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "0"),),
                positions=(position("HOLD-A", "20000000"),),
            )
        )
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(result.proposal.legs[0].action, ALLOCATION_ACTION_EXIT)

    def test_18_unresolved_blocks_increase(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        result = allocate_capital(
            base_request(
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.NO_ACTION_UNRESOLVED,
                        comparison_ids=("cmp-001",),
                        unresolved=("STALE_EVIDENCE",),
                    ),
                ),
                evaluations=(left,),
                comparisons=(
                    comparison("cmp-001", left, left, ComparisonStatus.UNRESOLVED),
                ),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "30000000"),),
                positions=(position("HOLD-A", "20000000"),),
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIn(FAILURE_POSTURE_BLOCKS_INCREASE, result.failure_codes)

    def test_19_research_more_blocks_increase(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        result = allocate_capital(
            base_request(
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.RESEARCH_MORE,
                        comparison_ids=("cmp-001",),
                    ),
                ),
                evaluations=(left,),
                comparisons=(
                    comparison("cmp-001", left, left, ComparisonStatus.EQUAL),
                ),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "30000000"),),
                positions=(position("HOLD-A", "20000000"),),
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIn(FAILURE_POSTURE_BLOCKS_INCREASE, result.failure_codes)

    # --- Universe / eligibility ---
    def test_20_watchlist_only_rejected(self):
        result = allocate_capital(
            base_request(
                proposed_notionals=(proposed("leg-w", "WATCH-C", "1000000"),),
                positions=(position("WATCH-C", "0"),),
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.CONSIDER_ROTATION,
                        superior="opp-cand",
                        comparison_ids=("cmp-001",),
                    ),
                ),
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIn(FAILURE_WATCHLIST_ONLY_INELIGIBLE, result.failure_codes)

    def test_21_holding_eligible(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        result = allocate_capital(
            base_request(
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.MAINTAIN,
                        comparison_ids=("cmp-001",),
                    ),
                ),
                evaluations=(left,),
                comparisons=(
                    comparison("cmp-001", left, left, ComparisonStatus.EQUAL),
                ),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "20000000"),),
                positions=(position("HOLD-A", "20000000"),),
            )
        )
        self.assertEqual(result.result_kind, "success")

    # --- Max position MV hard cap ---
    def test_22_max_position_hard_cap_blocks_overshoot(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        right = evaluation("opp-cand", "CAND-B", OpportunityRole.CANDIDATE)
        result = allocate_capital(
            base_request(
                cash=resolved_cash("200000000"),
                positions=(position("HOLD-A", "90000000"), position("CAND-B", "0")),
                proposed_notionals=(
                    proposed("leg-a", "HOLD-A", "90000000"),
                    proposed(
                        "leg-b",
                        "CAND-B",
                        "110000000",
                        funding=(),
                    ),
                ),
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.CONSIDER_ROTATION,
                        comparison_ids=("cmp-001",),
                        superior="opp-cand",
                    ),
                ),
                evaluations=(left, right),
                comparisons=(
                    comparison(
                        "cmp-001",
                        left,
                        right,
                        ComparisonStatus.RIGHT_SUPERIOR,
                    ),
                ),
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertTrue(
            FAILURE_MAX_POSITION_EXCEEDED in result.failure_codes
            or FAILURE_INCREASE_CAPACITY_ZERO in result.failure_codes
        )

    def test_23_already_at_cap_increase_capacity_zero(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        result = allocate_capital(
            base_request(
                cash=resolved_cash("50000000"),
                positions=(position("HOLD-A", "100000000"),),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "110000000"),),
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.CONSIDER_ROTATION,
                        comparison_ids=("cmp-001",),
                        superior="opp-hold",
                    ),
                ),
                evaluations=(left,),
                comparisons=(
                    comparison("cmp-001", left, left, ComparisonStatus.EQUAL),
                ),
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIn(FAILURE_INCREASE_CAPACITY_ZERO, result.failure_codes)

    def test_24_reduction_allowed_when_above_cap(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        result = allocate_capital(
            base_request(
                positions=(position("HOLD-A", "150000000"),),
                proposed_notionals=(proposed("leg-a", "HOLD-A", "80000000"),),
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.INVALIDATE_THESIS,
                        comparison_ids=("cmp-001",),
                    ),
                ),
                evaluations=(left,),
                comparisons=(
                    comparison("cmp-001", left, left, ComparisonStatus.EQUAL),
                ),
            )
        )
        self.assertEqual(result.result_kind, "success")

    # --- Capital conservation / rotation ---
    def test_25_rotation_proceeds_fund_increase(self):
        result = allocate_capital(base_request())
        self.assertEqual(result.result_kind, "success")
        cand = [leg for leg in result.proposal.legs if leg.portfolio_subject_id == "CAND-B"][0]
        self.assertEqual(cand.rotation_funding_krw, Decimal("10000000"))
        self.assertEqual(cand.cash_funding_krw, Decimal("0"))

    def test_26_cash_funded_increase_within_deployable(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        right = evaluation("opp-cand", "CAND-B", OpportunityRole.CANDIDATE)
        result = allocate_capital(
            base_request(
                cash=resolved_cash("15000000"),
                positions=(position("HOLD-A", "20000000"), position("CAND-B", "0")),
                proposed_notionals=(
                    proposed("leg-a", "HOLD-A", "20000000"),
                    proposed("leg-b", "CAND-B", "10000000"),
                ),
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.CONSIDER_ROTATION,
                        comparison_ids=("cmp-001",),
                        superior="opp-cand",
                    ),
                ),
                evaluations=(left, right),
                comparisons=(
                    comparison(
                        "cmp-001",
                        left,
                        right,
                        ComparisonStatus.RIGHT_SUPERIOR,
                    ),
                ),
            )
        )
        self.assertEqual(result.result_kind, "success")
        cand = [leg for leg in result.proposal.legs if leg.portfolio_subject_id == "CAND-B"][0]
        self.assertEqual(cand.cash_funding_krw, Decimal("10000000"))

    def test_27_cash_conservation_violation(self):
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        right = evaluation("opp-cand", "CAND-B", OpportunityRole.CANDIDATE)
        result = allocate_capital(
            base_request(
                cash=resolved_cash("1000"),
                positions=(position("HOLD-A", "20000000"), position("CAND-B", "0")),
                proposed_notionals=(
                    proposed("leg-a", "HOLD-A", "20000000"),
                    proposed("leg-b", "CAND-B", "5000000"),
                ),
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.CONSIDER_ROTATION,
                        comparison_ids=("cmp-001",),
                        superior="opp-cand",
                    ),
                ),
                evaluations=(left, right),
                comparisons=(
                    comparison(
                        "cmp-001",
                        left,
                        right,
                        ComparisonStatus.RIGHT_SUPERIOR,
                    ),
                ),
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIn(FAILURE_CASH_CONSERVATION_VIOLATION, result.failure_codes)

    def test_28_funding_provenance_auditable(self):
        result = allocate_capital(base_request())
        funding = result.proposal.funding
        self.assertEqual(funding.rotation_proceeds_krw, Decimal("10000000"))
        self.assertEqual(funding.rotation_funded_increases_krw, Decimal("10000000"))
        self.assertEqual(funding.cash_funded_increases_krw, Decimal("0"))

    def test_29_proposal_non_executable(self):
        result = allocate_capital(base_request())
        self.assertIs(result.proposal.executable, False)
        for leg in result.proposal.legs:
            self.assertIs(leg.executable, False)

    def test_30_krw_notional_not_order_payload(self):
        result = allocate_capital(base_request())
        encoded = encode(result.proposal)
        blob = str(encoded)
        self.assertNotIn("ordr_", blob)
        self.assertNotIn("SSAM", blob)
        self.assertNotIn("place_order", blob)

    # --- Structural bucket/risk ---
    def test_31_structural_bucket_and_risk_ids_accepted(self):
        result = allocate_capital(
            base_request(
                proposed_notionals=(
                    proposed("leg-hold", "HOLD-A", "10000000", bucket="bucket-1"),
                    proposed(
                        "leg-cand",
                        "CAND-B",
                        "10000000",
                        bucket="bucket-1",
                        risk="risk-1",
                        funding=("HOLD-A",),
                    ),
                )
            )
        )
        self.assertEqual(result.result_kind, "success")

    def test_32_risk_without_bucket_rejected(self):
        with self.assertRaises(ValueError):
            allocate_capital(
                base_request(
                    proposed_notionals=(
                        proposed(
                            "leg-cand",
                            "CAND-B",
                            "10000000",
                            risk="risk-1",
                            funding=("HOLD-A",),
                        ),
                    )
                )
            )

    # --- Approval / artifact ---
    def test_33_approval_binds_seals(self):
        request = base_request()
        result = allocate_capital(request)
        approval = record_investment_human_approval(
            approval_id="apr-001",
            decision=APPROVAL_DECISION_APPROVED,
            proposal=result.proposal,
            hip=request.hip,
            capital_snapshot=request.capital_snapshot,
            principal="YOUNG WO JUN",
            decided_at=NOW,
            rationale="approve rotation",
        )
        self.assertEqual(approval.proposal_integrity_seal, result.proposal.integrity_seal)
        self.assertEqual(approval.hip_integrity_seal, request.hip.integrity_seal)
        self.assertEqual(
            approval.capital_snapshot_id,
            request.capital_snapshot.capital_snapshot_id,
        )

    def test_34_reject_and_needs_revision(self):
        request = base_request()
        result = allocate_capital(request)
        rejected = record_investment_human_approval(
            approval_id="apr-002",
            decision=APPROVAL_DECISION_REJECTED,
            proposal=result.proposal,
            hip=request.hip,
            capital_snapshot=request.capital_snapshot,
            principal="YOUNG WO JUN",
            decided_at=NOW,
            rationale="reject",
        )
        self.assertEqual(rejected.decision, APPROVAL_DECISION_REJECTED)
        needs = record_investment_human_approval(
            approval_id="apr-003",
            decision=APPROVAL_DECISION_NEEDS_REVISION,
            proposal=result.proposal,
            hip=request.hip,
            capital_snapshot=request.capital_snapshot,
            principal="YOUNG WO JUN",
            decided_at=NOW,
            rationale="revise sizes",
        )
        self.assertEqual(needs.decision, APPROVAL_DECISION_NEEDS_REVISION)

    def test_35_artifact_requires_approved(self):
        request = base_request()
        result = allocate_capital(request)
        rejected = record_investment_human_approval(
            approval_id="apr-004",
            decision=APPROVAL_DECISION_REJECTED,
            proposal=result.proposal,
            hip=request.hip,
            capital_snapshot=request.capital_snapshot,
            principal="YOUNG WO JUN",
            decided_at=NOW,
            rationale="no",
        )
        with self.assertRaises(ValueError):
            seal_approved_allocation_artifact(
                artifact_id="art-001",
                approval=rejected,
                proposal=result.proposal,
                hip=request.hip,
                capital_snapshot=request.capital_snapshot,
                sealed_at=NOW,
            )

    def test_36_artifact_has_no_order_payload(self):
        request = base_request()
        result = allocate_capital(request)
        approval = record_investment_human_approval(
            approval_id="apr-005",
            decision=APPROVAL_DECISION_APPROVED,
            proposal=result.proposal,
            hip=request.hip,
            capital_snapshot=request.capital_snapshot,
            principal="YOUNG WO JUN",
            decided_at=NOW,
            rationale="ok",
        )
        artifact = seal_approved_allocation_artifact(
            artifact_id="art-002",
            approval=approval,
            proposal=result.proposal,
            hip=request.hip,
            capital_snapshot=request.capital_snapshot,
            sealed_at=NOW,
        )
        self.assertTrue(artifact.integrity_seal)
        for leg in artifact.legs:
            self.assertIs(leg.executable, False)

    def test_37_approval_hip_seal_mismatch_fails(self):
        request = base_request()
        result = allocate_capital(request)
        other = build_frozen_hip_v1(effective_at=NOW.replace(year=2025))
        with self.assertRaises(ValueError):
            record_investment_human_approval(
                approval_id="apr-006",
                decision=APPROVAL_DECISION_APPROVED,
                proposal=result.proposal,
                hip=other,
                capital_snapshot=request.capital_snapshot,
                principal="YOUNG WO JUN",
                decided_at=NOW,
                rationale="bad hip",
            )

    # --- Journal kinds / codec ---
    def test_38_journal_kinds_exist(self):
        for kind in (
            JournalRecordKind.HUMAN_INVESTMENT_POLICY,
            JournalRecordKind.CAPITAL_ALLOCATION_PROPOSAL,
            JournalRecordKind.INVESTMENT_HUMAN_APPROVAL,
            JournalRecordKind.SEALED_APPROVED_ALLOCATION,
        ):
            self.assertIsInstance(kind.value, str)

    def test_39_codec_roundtrip_proposal(self):
        result = allocate_capital(base_request())
        encoded = encode(result.proposal)
        decoded = decode(encoded)
        self.assertEqual(decoded, result.proposal)

    def test_40_codec_roundtrip_hip(self):
        hip = build_frozen_hip_v1()
        self.assertEqual(decode(encode(hip)), hip)

    def test_41_journal_append_block_b_kinds(self):
        import tempfile
        from pathlib import Path
        request = base_request()
        result = allocate_capital(request)
        with tempfile.TemporaryDirectory() as tmp:
            journal = DecisionJournal(Path(tmp) / "d.sqlite")
            batch = (
                JournalAppend(
                    "hip-1",
                    JournalRecordKind.HUMAN_INVESTMENT_POLICY,
                    NOW,
                    encode(request.hip),
                ),
                JournalAppend(
                    "prop-1",
                    JournalRecordKind.CAPITAL_ALLOCATION_PROPOSAL,
                    NOW,
                    encode(result.proposal),
                ),
            )
            stored = journal.append_batch(batch)
            self.assertEqual(len(stored), 2)
            self.assertEqual(
                stored[0].kind,
                JournalRecordKind.HUMAN_INVESTMENT_POLICY,
            )
            journal.close()

    # --- Exact decimal / immutability ---
    def test_42_no_float_in_funding(self):
        result = allocate_capital(base_request())
        for value in (
            result.proposal.funding.deployable_orderable_cash_krw,
            result.proposal.funding.cash_funded_increases_krw,
            result.proposal.funding.rotation_funded_increases_krw,
        ):
            self.assertIs(type(value), Decimal)

    def test_43_deterministic_seal_stable(self):
        a = allocate_capital(base_request())
        b = allocate_capital(base_request())
        self.assertEqual(a.proposal.integrity_seal, b.proposal.integrity_seal)

    def test_44_consider_rotation_is_not_auto_sell_without_proposal(self):
        # CIO CONSIDER_ROTATION alone without proposed reduce does not invent sells.
        left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
        right = evaluation("opp-cand", "CAND-B", OpportunityRole.CANDIDATE)
        result = allocate_capital(
            base_request(
                proposed_notionals=(
                    proposed("leg-a", "HOLD-A", "20000000"),
                    proposed("leg-b", "CAND-B", "0"),
                ),
                decisions=(
                    cio_decision(
                        posture=CioActionPosture.CONSIDER_ROTATION,
                        comparison_ids=("cmp-001",),
                        superior="opp-cand",
                    ),
                ),
                evaluations=(left, right),
                comparisons=(
                    comparison(
                        "cmp-001",
                        left,
                        right,
                        ComparisonStatus.RIGHT_SUPERIOR,
                    ),
                ),
            )
        )
        self.assertEqual(result.result_kind, "success")
        actions = {leg.portfolio_subject_id: leg.action for leg in result.proposal.legs}
        self.assertEqual(actions["HOLD-A"], ALLOCATION_ACTION_MAINTAIN)

    def test_45_duplicate_leg_rejected(self):
        with self.assertRaises(ValueError):
            allocate_capital(
                base_request(
                    proposed_notionals=(
                        proposed("leg-a", "HOLD-A", "20000000"),
                        proposed("leg-a", "CAND-B", "10000000"),
                    )
                )
            )

    def test_46_negative_notional_rejected(self):
        with self.assertRaises(ValueError):
            allocate_capital(
                base_request(
                    proposed_notionals=(
                        proposed("leg-a", "HOLD-A", "-1"),
                    )
                )
            )

    def test_47_profit_realization_deferred_not_hardcoded(self):
        hip = build_frozen_hip_v1()
        self.assertEqual(hip.profit_realization_mode, "DEFER")
        # No hardcoded +50% policy value exists on HIP.
        self.assertFalse(hasattr(hip, "profit_take_ratio"))


if __name__ == "__main__":
    unittest.main()
