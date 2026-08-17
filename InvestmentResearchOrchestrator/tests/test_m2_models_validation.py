from __future__ import annotations

import unittest
from dataclasses import fields
from datetime import datetime, timezone

from InvestmentResearchOrchestrator.models.enums import (
    ContradictionCaseClass,
    ContradictionCaseStatus,
    EscalationMarker,
    EscalationReasonCode,
    IRORunPhase,
    IRORunStatus,
    MemoryDeltaClass,
    NumericPathStatus,
    ReResearchReasonCode,
)
from InvestmentResearchOrchestrator.models.memory import (
    MemoryDelta,
)
from InvestmentResearchOrchestrator.models.re_research import (
    EscalationRecord,
    ReResearchBudget,
    ReResearchRequest,
    ReResearchRequestSet,
)
from InvestmentResearchOrchestrator.models.run import IRORun
from InvestmentResearchOrchestrator.validation.memory import (
    validate_memory_delta,
)
from InvestmentResearchOrchestrator.validation.re_research import (
    validate_escalation_record,
    validate_re_research_budget,
    validate_re_research_request,
    validate_re_research_request_set,
)
from InvestmentResearchOrchestrator.validation.run import (
    validate_iro_run,
)


class M2ModelValidationTests(unittest.TestCase):
    def test_additive_enum_members(self):
        self.assertEqual(
            IRORunPhase.CONTRADICTION_EVALUATED.value,
            "CONTRADICTION_EVALUATED",
        )
        self.assertEqual(
            IRORunStatus.ESCALATED_HUMAN_REVIEW.value,
            "ESCALATED_HUMAN_REVIEW",
        )
        self.assertEqual(
            MemoryDeltaClass.PROVENANCE_CHANGED.value,
            "PROVENANCE_CHANGED",
        )
        self.assertEqual(
            list(ContradictionCaseClass),
            [
                ContradictionCaseClass.NUMERIC_CANDIDATE,
                ContradictionCaseClass.MULTI_COMMITTEE_STATEMENT_CONFLICT,
                ContradictionCaseClass.PRIOR_VS_CURRENT_STATEMENT_CONFLICT,
                ContradictionCaseClass.CONFIDENCE_INSUFFICIENT,
            ],
        )
        self.assertEqual(
            [member.value for member in ReResearchReasonCode],
            [member.value for member in ContradictionCaseClass],
        )
        self.assertEqual(
            list(EscalationMarker),
            [EscalationMarker.WAIT, EscalationMarker.MONITOR],
        )
        self.assertEqual(
            list(EscalationReasonCode),
            [
                EscalationReasonCode.RE_RESEARCH_BUDGET_EXHAUSTED,
                EscalationReasonCode.NON_PROGRESS,
                EscalationReasonCode.UNPLANABLE_REQUESTS,
            ],
        )
        self.assertEqual(
            list(ContradictionCaseStatus),
            [
                ContradictionCaseStatus.UNRESOLVED,
                ContradictionCaseStatus.STRUCTURALLY_CLEARED,
                ContradictionCaseStatus.INELIGIBLE,
            ],
        )
        self.assertEqual(
            list(NumericPathStatus),
            [
                NumericPathStatus.APPLIED,
                NumericPathStatus.NOT_APPLICABLE,
                NumericPathStatus.PARTIAL,
            ],
        )

    def test_iro_run_field_order_unchanged(self):
        self.assertEqual(
            [field.name for field in fields(IRORun)],
            [
                "run_id",
                "portfolio_snapshot_id",
                "prior_baseline_id",
                "phase",
                "status",
                "created_at",
                "updated_at",
            ],
        )

    def test_escalated_terminal_consistency(self):
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        run = IRORun(
            run_id="run-001",
            portfolio_snapshot_id="snap-001",
            prior_baseline_id=None,
            phase=IRORunPhase.ESCALATED_HUMAN_REVIEW,
            status=IRORunStatus.ESCALATED_HUMAN_REVIEW,
            created_at=now,
            updated_at=now,
        )
        validate_iro_run(run)
        bad = IRORun(
            run_id="run-001",
            portfolio_snapshot_id="snap-001",
            prior_baseline_id=None,
            phase=IRORunPhase.ESCALATED_HUMAN_REVIEW,
            status=IRORunStatus.COMPLETED,
            created_at=now,
            updated_at=now,
        )
        with self.assertRaisesRegex(ValueError, "terminal"):
            validate_iro_run(bad)

    def test_memory_new_classes_require_prior_when_specified(self):
        with self.assertRaisesRegex(ValueError, "prior_present"):
            validate_memory_delta(
                MemoryDelta(
                    subject_key="held-a",
                    prior_present=False,
                    delta_class=MemoryDeltaClass.PROVENANCE_CHANGED,
                )
            )
        with self.assertRaisesRegex(ValueError, "prior_present"):
            validate_memory_delta(
                MemoryDelta(
                    subject_key="held-a",
                    prior_present=False,
                    delta_class=(
                        MemoryDeltaClass.MULTI_FINDING_SET_CHANGED
                    ),
                )
            )

    def test_invalid_new_model_types_fail_closed(self):
        with self.assertRaisesRegex(TypeError, "budget"):
            validate_re_research_budget("nope")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "max_attempts"):
            validate_re_research_budget(
                ReResearchBudget(max_attempts=0, remaining=0)
            )
        with self.assertRaisesRegex(ValueError, "request_id"):
            validate_re_research_request(
                ReResearchRequest(
                    request_id="  ",
                    subject_key="held-a",
                    reason_code=(
                        ReResearchReasonCode.NUMERIC_CANDIDATE
                    ),
                    task_type="HOLDING_STRUCTURAL",
                    source_case_ids=("case-1",),
                    priority="P0",
                )
            )
        with self.assertRaisesRegex(ValueError, "source_case_ids"):
            validate_re_research_request(
                ReResearchRequest(
                    request_id="req-1",
                    subject_key="held-a",
                    reason_code=(
                        ReResearchReasonCode.NUMERIC_CANDIDATE
                    ),
                    task_type="HOLDING_STRUCTURAL",
                    source_case_ids=(),
                    priority="P0",
                )
            )
        with self.assertRaisesRegex(TypeError, "attempt"):
            validate_re_research_request_set(
                ReResearchRequestSet(
                    run_id="run-001",
                    attempt="0",  # type: ignore[arg-type]
                    requests=(),
                )
            )
        with self.assertRaisesRegex(TypeError, "record"):
            validate_escalation_record("nope")  # type: ignore[arg-type]
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        validate_escalation_record(
            EscalationRecord(
                run_id="run-001",
                marker=EscalationMarker.WAIT,
                reason_code=(
                    EscalationReasonCode.NON_PROGRESS
                ),
                unresolved_case_ids=("case-1",),
                max_attempts=1,
                remaining=1,
                created_at=now,
            )
        )


if __name__ == "__main__":
    unittest.main()
