from __future__ import annotations

import unittest

from CommandCenterRuntime.checkpoint import checkpoint_answers
from CommandCenterRuntime.idempotency import IdempotencyStore
from CommandCenterRuntime.recovery import recover_command_center
from CommandCenterRuntime.service import (
    CommandCenterCycleRequest,
    run_command_center_cycle,
)
from CommandCenterRuntime.tests.helpers import (
    NOW,
    broker,
    cash,
    detect_broker_order_or_fill,
    detect_capital_cash_change,
    detect_portfolio_membership_change,
    detect_provider_failure,
    membership,
    provider_fail,
    wake_from_detected,
)
from CommandCenterRuntime.vocabularies import (
    STAGE_CAPITAL_SNAPSHOT,
    STAGE_CIO,
    STAGE_RESEARCH,
    STAGE_STATUS_COMPLETED,
)


class CycleAndIdempotencyTests(unittest.TestCase):
    def test_idle_no_change_no_spurious_cio(self):
        prior = membership("m0", ("S1",))
        current = membership("m0b", ("S1",))
        # Same subjects → no change
        change = detect_portfolio_membership_change(prior, current)
        self.assertIsNone(change)

    def test_full_cycle_portfolio_wake_schedules_cio_path(self):
        change = detect_portfolio_membership_change(
            membership("a", ("S1",)), membership("b", ("S1", "S2"))
        )
        wake = wake_from_detected("wake-pf-1", change)
        called = []

        def runner(stage, _wake):
            called.append(stage)
            return (f"id:{stage}",)

        result = run_command_center_cycle(
            CommandCenterCycleRequest(
                cycle_id="cycle-pf-1",
                holder_id="holder-1",
                wake_events=(wake,),
                changes=(change,),
                now=NOW,
            ),
            domain_runner=runner,
        )
        self.assertEqual(result.result_kind, "success")
        self.assertIn(STAGE_RESEARCH, called)
        self.assertIn(STAGE_CIO, called)
        self.assertIsNotNone(result.checkpoint)
        self.assertTrue(result.checkpoint.resume_safe)
        self.assertFalse(result.state.live_mutation_enabled)
        answers = checkpoint_answers(result.checkpoint)
        self.assertIn(STAGE_STATUS_COMPLETED, answers["by_status"])
        self.assertIsNotNone(result.report)
        self.assertTrue(result.report.why_woke)

    def test_capital_only_cycle_no_research_stage_run(self):
        change = detect_capital_cash_change(
            cash("p", "present", "100"), cash("c", "present", "200")
        )
        wake = wake_from_detected("wake-cash-1", change)
        called = []

        def runner(stage, _wake):
            called.append(stage)
            return (f"id:{stage}",)

        result = run_command_center_cycle(
            CommandCenterCycleRequest(
                cycle_id="cycle-cash-1",
                holder_id="holder-1",
                wake_events=(wake,),
                changes=(change,),
                now=NOW,
            ),
            domain_runner=runner,
        )
        self.assertEqual(result.result_kind, "success")
        self.assertIn(STAGE_CAPITAL_SNAPSHOT, called)
        self.assertNotIn(STAGE_RESEARCH, called)
        self.assertNotIn(STAGE_CIO, called)
        self.assertTrue(
            any(a.category == "ALLOCATION_REVISION_REQUIRED" for a in result.attention_items)
        )

    def test_idempotent_same_source_event_no_duplicate_decisions(self):
        change = detect_provider_failure(provider_fail("pf-idem"))
        wake = wake_from_detected("wake-idem-1", change)
        store = IdempotencyStore()
        called = []

        def runner(stage, _wake):
            called.append(stage)
            return (f"id:{stage}",)

        first = run_command_center_cycle(
            CommandCenterCycleRequest(
                cycle_id="cycle-idem-1",
                holder_id="holder-1",
                wake_events=(wake,),
                changes=(change,),
                now=NOW,
            ),
            idempotency_store=store,
            domain_runner=runner,
        )
        self.assertEqual(first.result_kind, "success")
        n = len(called)
        second = run_command_center_cycle(
            CommandCenterCycleRequest(
                cycle_id="cycle-idem-2",
                holder_id="holder-1",
                wake_events=(wake,),
                changes=(change,),
                now=NOW,
            ),
            idempotency_store=store,
            domain_runner=runner,
        )
        self.assertEqual(second.result_kind, "idempotent")
        self.assertEqual(len(called), n)  # no additional domain runs
        self.assertTrue(second.idempotency_hits)

    def test_crash_recover_does_not_enable_live_or_drop_unknown(self):
        change = detect_broker_order_or_fill(
            broker("b-rec", "SUBMISSION_OUTCOME_UNKNOWN")
        )
        wake = wake_from_detected("wake-rec-1", change)
        first = run_command_center_cycle(
            CommandCenterCycleRequest(
                cycle_id="cycle-rec-1",
                holder_id="holder-1",
                wake_events=(wake,),
                changes=(change,),
                now=NOW,
            ),
        )
        recovered = recover_command_center(
            state_id="state-rec",
            checkpoints=(first.checkpoint,),
            attention_items=first.attention_items,
            idempotency_records=(),
        )
        self.assertEqual(recovered.result_kind, "recovered")
        self.assertFalse(recovered.state.live_mutation_enabled)
        self.assertTrue(recovered.state.unresolved_attention_ids)
        with self.assertRaises(RuntimeError):
            recover_command_center(
                state_id="x",
                checkpoints=(),
                attention_items=(),
                live_mutation_enabled=True,
            )

    def test_report_machine_contract_fields(self):
        change = detect_provider_failure(provider_fail("pf-rep"))
        wake = wake_from_detected("wake-rep", change)
        result = run_command_center_cycle(
            CommandCenterCycleRequest(
                cycle_id="cycle-rep",
                holder_id="h",
                wake_events=(wake,),
                changes=(change,),
                now=NOW,
            ),
        )
        report = result.report
        self.assertTrue(report.what_changed)
        self.assertTrue(report.why_woke)
        self.assertIsInstance(report.impacts, tuple)
        self.assertIsInstance(report.human_actions, tuple)
        self.assertIsInstance(report.warnings, tuple)
        self.assertTrue(report.execution_status)
        self.assertTrue(report.integrity_seal)


if __name__ == "__main__":
    unittest.main()
