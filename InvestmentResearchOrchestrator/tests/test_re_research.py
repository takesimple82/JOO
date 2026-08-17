from __future__ import annotations

import unittest

from InvestmentResearchOrchestrator.models.contradiction import (
    ContradictionCase,
    ContradictionEvaluation,
    ContradictionEvidenceRef,
)
from InvestmentResearchOrchestrator.models.enums import (
    ContradictionCaseClass,
    ContradictionCaseStatus,
    IRORunStatus,
    NumericPathStatus,
    ReResearchReasonCode,
)
from InvestmentResearchOrchestrator.models.re_research import (
    ReResearchBudget,
    ReResearchRequest,
    ReResearchRequestSet,
)
from InvestmentResearchOrchestrator.re_research import (
    consume_re_research_admission,
    is_exact_non_progress,
    make_re_research_budget,
    should_admit_re_research,
)


def _case(case_id="run-001:case:held-a:MULTI_COMMITTEE_STATEMENT_CONFLICT"):
    return ContradictionCase(
        case_id=case_id,
        subject_key="held-a",
        case_class=(
            ContradictionCaseClass.MULTI_COMMITTEE_STATEMENT_CONFLICT
        ),
        status=ContradictionCaseStatus.UNRESOLVED,
        evidence_refs=(
            ContradictionEvidenceRef(
                research_id="r1",
                committee_id="c1",
                store_identity=None,
                prompt_hash=None,
            ),
        ),
        domain_status=None,
        notes_code=None,
    )


def _request(case_id):
    return ReResearchRequest(
        request_id="run-001:request:held-a:MULTI_COMMITTEE_STATEMENT_CONFLICT",
        subject_key="held-a",
        reason_code=(
            ReResearchReasonCode.MULTI_COMMITTEE_STATEMENT_CONFLICT
        ),
        task_type="HOLDING_STRUCTURAL",
        source_case_ids=(case_id,),
        priority="P0",
    )


def _evaluation(*, attempt, case_id):
    request = _request(case_id)
    return ContradictionEvaluation(
        run_id="run-001",
        attempt=attempt,
        cases=(_case(case_id),),
        unresolved=(case_id,),
        re_research_requests=ReResearchRequestSet(
            run_id="run-001",
            attempt=attempt,
            requests=(request,),
        ),
        numeric_path_status=NumericPathStatus.NOT_APPLICABLE,
    )


class ReResearchHelperTests(unittest.TestCase):
    def test_initial_budget_does_not_consume_until_admission(self):
        budget = make_re_research_budget(max_attempts=2)
        self.assertEqual(budget.max_attempts, 2)
        self.assertEqual(budget.remaining, 2)

    def test_admission_consumes_exactly_one(self):
        budget = make_re_research_budget(max_attempts=2)
        consumed = consume_re_research_admission(budget)
        self.assertEqual(consumed.remaining, 1)
        self.assertEqual(budget.remaining, 2)

    def test_exact_non_progress(self):
        case_id = (
            "run-001:case:held-a:"
            "MULTI_COMMITTEE_STATEMENT_CONFLICT"
        )
        previous = _evaluation(attempt=0, case_id=case_id)
        current = _evaluation(attempt=1, case_id=case_id)
        self.assertTrue(
            is_exact_non_progress(previous, current)
        )

    def test_first_admission_after_attempt_zero(self):
        case_id = (
            "run-001:case:held-a:"
            "MULTI_COMMITTEE_STATEMENT_CONFLICT"
        )
        current = _evaluation(attempt=0, case_id=case_id)
        self.assertTrue(
            should_admit_re_research(
                request_set=current.re_research_requests,
                budget=make_re_research_budget(max_attempts=1),
                previous_evaluation=None,
                current_evaluation=current,
                run_status=IRORunStatus.IN_PROGRESS,
            )
        )

    def test_non_progress_is_not_admitted(self):
        case_id = (
            "run-001:case:held-a:"
            "MULTI_COMMITTEE_STATEMENT_CONFLICT"
        )
        previous = _evaluation(attempt=0, case_id=case_id)
        current = _evaluation(attempt=1, case_id=case_id)
        self.assertFalse(
            should_admit_re_research(
                request_set=current.re_research_requests,
                budget=make_re_research_budget(max_attempts=2),
                previous_evaluation=previous,
                current_evaluation=current,
                run_status=IRORunStatus.IN_PROGRESS,
            )
        )

    def test_invalid_budget_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "max_attempts"):
            make_re_research_budget(max_attempts=0)
        with self.assertRaisesRegex(TypeError, "budget"):
            consume_re_research_admission("nope")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "remaining"):
            make_re_research_budget(
                max_attempts=1,
                remaining=2,
            )


if __name__ == "__main__":
    unittest.main()
