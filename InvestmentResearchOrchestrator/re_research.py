from __future__ import annotations

from InvestmentResearchOrchestrator.models.contradiction import (
    ContradictionEvaluation,
)
from InvestmentResearchOrchestrator.models.enums import (
    IRORunStatus,
)
from InvestmentResearchOrchestrator.models.re_research import (
    ReResearchBudget,
    ReResearchRequestSet,
)
from InvestmentResearchOrchestrator.validation.contradiction import (
    validate_contradiction_evaluation,
)
from InvestmentResearchOrchestrator.validation.re_research import (
    validate_re_research_budget,
    validate_re_research_request_set,
)


def make_re_research_budget(
    *,
    max_attempts: int,
    remaining: int | None = None,
) -> ReResearchBudget:
    if remaining is None:
        remaining = max_attempts
    budget = ReResearchBudget(
        max_attempts=max_attempts,
        remaining=remaining,
    )
    validate_re_research_budget(budget)
    return budget


def consume_re_research_admission(
    budget: ReResearchBudget,
) -> ReResearchBudget:
    validate_re_research_budget(budget)
    if budget.remaining <= 0:
        raise ValueError(
            "no remaining re-research budget"
        )
    updated = ReResearchBudget(
        max_attempts=budget.max_attempts,
        remaining=budget.remaining - 1,
    )
    validate_re_research_budget(updated)
    return updated


def is_exact_non_progress(
    previous_evaluation: ContradictionEvaluation,
    current_evaluation: ContradictionEvaluation,
) -> bool:
    validate_contradiction_evaluation(previous_evaluation)
    validate_contradiction_evaluation(current_evaluation)
    previous_ids = frozenset(previous_evaluation.unresolved)
    current_ids = frozenset(current_evaluation.unresolved)
    previous_reasons = frozenset(
        request.reason_code
        for request in (
            previous_evaluation.re_research_requests.requests
        )
    )
    current_reasons = frozenset(
        request.reason_code
        for request in (
            current_evaluation.re_research_requests.requests
        )
    )
    return (
        previous_ids == current_ids
        and previous_reasons == current_reasons
    )


def should_admit_re_research(
    *,
    request_set: ReResearchRequestSet,
    budget: ReResearchBudget,
    previous_evaluation: ContradictionEvaluation | None,
    current_evaluation: ContradictionEvaluation,
    run_status: IRORunStatus,
) -> bool:
    validate_re_research_request_set(request_set)
    validate_re_research_budget(budget)
    validate_contradiction_evaluation(current_evaluation)
    if previous_evaluation is not None:
        validate_contradiction_evaluation(previous_evaluation)
    if type(run_status) is not IRORunStatus:
        raise TypeError("run_status must be IRORunStatus")
    if run_status is not IRORunStatus.IN_PROGRESS:
        return False
    if len(request_set.requests) == 0:
        return False
    if budget.remaining <= 0:
        return False
    if previous_evaluation is None:
        return True
    if is_exact_non_progress(
        previous_evaluation,
        current_evaluation,
    ):
        return False
    return True
