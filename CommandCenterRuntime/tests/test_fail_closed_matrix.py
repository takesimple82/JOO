from __future__ import annotations

import unittest

from BrokerExecutionCycle.mutation_transport import LiveMutationTransportDisabled

from CommandCenterRuntime.attention import (
    attention_for_wake,
    dedupe_unresolved,
    refuse_auto_approval,
    refuse_gate_merge,
    sort_attention_safety_first,
)
from CommandCenterRuntime.concurrency import ExclusiveCycleLock
from CommandCenterRuntime.idempotency import IdempotencyStore
from CommandCenterRuntime.observability import structured_event
from CommandCenterRuntime.recovery import assert_retry_safe, recover_command_center
from CommandCenterRuntime.routing import route_wake
from CommandCenterRuntime.service import (
    CommandCenterCycleRequest,
    run_command_center_cycle,
)
from CommandCenterRuntime.stages import assert_no_stage_skip, ordered_required_stages
from CommandCenterRuntime.tests.helpers import (
    NOW,
    approval,
    broker,
    cash,
    detect_approval_transition,
    detect_broker_order_or_fill,
    detect_capital_cash_change,
    detect_portfolio_membership_change,
    detect_provider_failure,
    detect_research_evidence_admission,
    detect_thesis_transition,
    membership,
    provider_fail,
    research,
    seal_wake_event,
    thesis,
    wake_from_detected,
)
from CommandCenterRuntime.vocabularies import (
    ATTENTION_DATA_INTEGRITY_FAILURE,
    ATTENTION_INVESTMENT_APPROVAL_REQUIRED,
    ATTENTION_PROVIDER_FAILURE,
    ATTENTION_SUBMISSION_OUTCOME_UNKNOWN,
    FAILURE_AI_WAKE_WITHOUT_EVIDENCE,
    FAILURE_AUTO_APPROVAL_FORBIDDEN,
    FAILURE_EXCLUSIVE_OWNERSHIP_UNPROVABLE,
    FAILURE_GATE_MERGE_FORBIDDEN,
    FAILURE_LIVE_MUTATION_DISABLED,
    FAILURE_MISSING_NE_ZERO,
    FAILURE_OVERLAPPING_CYCLE,
    FAILURE_RETRY_UNSAFE,
    FAILURE_STAGE_SKIP,
    STAGE_CAPITAL_SNAPSHOT,
    STAGE_CIO,
    STAGE_FACT_REFRESH,
    STAGE_RESEARCH,
    STAGE_STATUS_COMPLETED,
)


class FailClosedMatrixTests(unittest.TestCase):
    def test_ai_cannot_invent_wake_without_evidence(self):
        with self.assertRaisesRegex(ValueError, FAILURE_AI_WAKE_WITHOUT_EVIDENCE):
            seal_wake_event(
                wake_event_id="bad",
                wake_type="PROVIDER_FAILURE",
                source="AI",
                fact_or_evidence_id="f1",
                observed_at=NOW,
                subject_ids=(),
                provenance="model-said-so",
            )
        with self.assertRaisesRegex(ValueError, FAILURE_AI_WAKE_WITHOUT_EVIDENCE):
            seal_wake_event(
                wake_event_id="bad2",
                wake_type="PROVIDER_FAILURE",
                source="FactStore",
                fact_or_evidence_id="AI_INVENTED_1",
                observed_at=NOW,
                subject_ids=(),
                provenance="p",
            )

    def test_missing_capital_not_coerced_to_zero(self):
        with self.assertRaisesRegex(ValueError, FAILURE_MISSING_NE_ZERO):
            detect_capital_cash_change(None, cash("c1", "present", None))
        missing = cash("c2", "missing", None)
        change = detect_capital_cash_change(None, missing)
        self.assertIsNotNone(change)
        # present zero is distinct and allowed
        zero = cash("c3", "present", "0")
        self.assertIsNotNone(detect_capital_cash_change(missing, zero))

    def test_capital_only_does_not_auto_research(self):
        change = detect_capital_cash_change(
            cash("p", "present", "1000"), cash("c", "present", "2000")
        )
        wake = wake_from_detected("w-cash", change)
        stages = {e.stage for e in route_wake(wake)}
        self.assertIn(STAGE_CAPITAL_SNAPSHOT, stages)
        self.assertNotIn(STAGE_RESEARCH, stages)
        self.assertNotIn(STAGE_CIO, stages)

    def test_portfolio_change_escalates_to_cio(self):
        change = detect_portfolio_membership_change(
            membership("a", ("S1",)), membership("b", ("S1", "S2"))
        )
        wake = wake_from_detected("w-pf", change)
        stages = {e.stage for e in route_wake(wake)}
        self.assertIn(STAGE_RESEARCH, stages)
        self.assertIn(STAGE_CIO, stages)

    def test_stage_skip_forbidden(self):
        from CommandCenterRuntime.vocabularies import STAGE_EXPECTED_VALUE

        required = (STAGE_FACT_REFRESH, STAGE_EXPECTED_VALUE, STAGE_CIO)
        with self.assertRaisesRegex(ValueError, FAILURE_STAGE_SKIP):
            assert_no_stage_skip(
                stage=STAGE_CIO,
                required_stages=required,
                completed_or_skipped={STAGE_FACT_REFRESH: STAGE_STATUS_COMPLETED},
            )

    def test_both_gates_never_merged_or_auto_approved(self):
        with self.assertRaisesRegex(RuntimeError, FAILURE_AUTO_APPROVAL_FORBIDDEN):
            refuse_auto_approval()
        with self.assertRaisesRegex(RuntimeError, FAILURE_GATE_MERGE_FORBIDDEN):
            refuse_gate_merge()
        iha = detect_approval_transition(
            approval("a1", "INVESTMENT_HUMAN_APPROVAL", "PENDING")
        )
        tea = detect_approval_transition(
            approval("a2", "TRADE_EXECUTION_AUTHORIZATION", "PENDING")
        )
        self.assertNotEqual(iha.detail, tea.detail)

    def test_live_mutation_cannot_enable_from_cycle(self):
        change = detect_provider_failure(provider_fail("pf1"))
        wake = wake_from_detected("w-pfail", change)
        with self.assertRaisesRegex(RuntimeError, FAILURE_LIVE_MUTATION_DISABLED):
            run_command_center_cycle(
                CommandCenterCycleRequest(
                    cycle_id="c1",
                    holder_id="h1",
                    wake_events=(wake,),
                    changes=(change,),
                    now=NOW,
                ),
                enable_live_mutation=True,
            )
        self.assertIsInstance(LiveMutationTransportDisabled(), LiveMutationTransportDisabled)

    def test_unsafe_retries_forbidden(self):
        with self.assertRaisesRegex(RuntimeError, FAILURE_RETRY_UNSAFE):
            assert_retry_safe("BROKER_MUTATION_AFTER_POSSIBLE_SEND")
        with self.assertRaisesRegex(RuntimeError, FAILURE_RETRY_UNSAFE):
            assert_retry_safe("HUMAN_APPROVAL_CREATION")
        with self.assertRaisesRegex(RuntimeError, FAILURE_RETRY_UNSAFE):
            assert_retry_safe("TEA_CREATION")

    def test_exclusive_ownership_fail_closed(self):
        lock = ExclusiveCycleLock()
        lock.try_acquire(
            lease_id="l1",
            source_event_id="e1",
            holder_id="h1",
            acquired_at=NOW,
        )
        with self.assertRaisesRegex(RuntimeError, FAILURE_OVERLAPPING_CYCLE):
            lock.try_acquire(
                lease_id="l2",
                source_event_id="e1",
                holder_id="h2",
                acquired_at=NOW,
            )
        with self.assertRaisesRegex(RuntimeError, FAILURE_EXCLUSIVE_OWNERSHIP_UNPROVABLE):
            ExclusiveCycleLock().try_acquire(
                lease_id="l3",
                source_event_id="e2",
                holder_id="h1",
                acquired_at=NOW,
                ownership_provable=False,
            )

    def test_provider_outage_is_data_and_attention(self):
        change = detect_provider_failure(provider_fail("pf2"))
        wake = wake_from_detected("w-outage", change)
        item = attention_for_wake(wake=wake, created_at=NOW)
        self.assertIsNotNone(item)
        self.assertEqual(item.category, ATTENTION_PROVIDER_FAILURE)

    def test_unknown_and_recon_attention_preserved_on_recover(self):
        change = detect_broker_order_or_fill(
            broker("b1", "SUBMISSION_OUTCOME_UNKNOWN")
        )
        wake = wake_from_detected("w-unk", change)
        item = attention_for_wake(wake=wake, created_at=NOW)
        self.assertEqual(item.category, ATTENTION_SUBMISSION_OUTCOME_UNKNOWN)
        result = recover_command_center(
            state_id="s1",
            checkpoints=(),
            attention_items=(item,),
        )
        self.assertEqual(result.result_kind, "recovered")
        self.assertIn(item.attention_id, result.state.unresolved_attention_ids)

    def test_attention_dedupe_identical_unresolved(self):
        change = detect_provider_failure(provider_fail("pf3"))
        wake = wake_from_detected("w-d", change)
        a = attention_for_wake(wake=wake, created_at=NOW)
        b = attention_for_wake(wake=wake, created_at=NOW)
        self.assertIsNone(dedupe_unresolved((a,), b))

    def test_safety_priority_not_investment_ranking(self):
        from CommandCenterRuntime.attention import seal_human_attention_item

        low = seal_human_attention_item(
            attention_id="a-low",
            category=ATTENTION_INVESTMENT_APPROVAL_REQUIRED,
            wake_event_id="w",
            bound_record_ids=("x",),
            subject_ids=(),
            created_at=NOW,
            detail="invest",
        )
        high = seal_human_attention_item(
            attention_id="a-high",
            category=ATTENTION_DATA_INTEGRITY_FAILURE,
            wake_event_id="w",
            bound_record_ids=("y",),
            subject_ids=(),
            created_at=NOW,
            detail="integrity",
        )
        ordered = sort_attention_safety_first((low, high))
        self.assertEqual(ordered[0].attention_id, "a-high")

    def test_observability_redacts_secrets(self):
        line = structured_event(
            event_type="t",
            cycle_id="c",
            fields={"token": "sekrit", "ok": 1, "gnl_ac_no1": "acc"},
            observed_at=NOW,
        )
        self.assertIn("***REDACTED***", line)
        self.assertNotIn("sekrit", line)
        self.assertNotIn('"acc"', line)

    def test_research_truth_class_not_broker_fact(self):
        ok = detect_research_evidence_admission(research("r1", "e1", ("S1",)))
        self.assertEqual(ok.change_kind, "RESEARCH_EVIDENCE_ADMITTED")
        from dataclasses import replace

        bad = research("r2", "e2", ("S1",))
        forged = replace(bad, truth_class="broker_fact")
        with self.assertRaisesRegex(ValueError, "broker_fact"):
            detect_research_evidence_admission(forged)

    def test_thesis_invalidated_attention(self):
        change = detect_thesis_transition(thesis("th1", "INVALIDATED"))
        wake = wake_from_detected("w-th", change)
        item = attention_for_wake(
            wake=wake, created_at=NOW, thesis_state="INVALIDATED"
        )
        self.assertEqual(item.category, "THESIS_INVALIDATED")

    def test_ordered_required_stages_stable(self):
        change = detect_portfolio_membership_change(
            None, membership("m1", ("S1",))
        )
        wake = wake_from_detected("w-o", change)
        plan = route_wake(wake)
        ordered = ordered_required_stages(plan)
        self.assertEqual(ordered[0], STAGE_FACT_REFRESH)
        self.assertIn(STAGE_CIO, ordered)


if __name__ == "__main__":
    unittest.main()
