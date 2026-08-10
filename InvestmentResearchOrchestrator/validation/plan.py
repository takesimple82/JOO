from __future__ import annotations

from InvestmentResearchOrchestrator.models.plan import (
    PlannedUnit,
    PlanSkip,
    ResearchPlan,
)
from InvestmentResearchOrchestrator.validation.common import (
    require_nonblank_string,
    require_string,
    require_tuple_of,
)

_PRIORITIES = frozenset({"P0", "P1", "P2"})


def validate_planned_unit(unit: PlannedUnit) -> None:
    if type(unit) is not PlannedUnit:
        raise TypeError("unit must be PlannedUnit")
    require_nonblank_string("research_id", unit.research_id)
    require_nonblank_string("subject_id", unit.subject_id)
    require_nonblank_string("task_type", unit.task_type)
    require_string("priority", unit.priority)
    if unit.priority not in _PRIORITIES:
        raise ValueError("priority must be P0, P1, or P2")
    require_nonblank_string("title", unit.title)
    require_nonblank_string("objective", unit.objective)


def validate_plan_skip(skip: PlanSkip) -> None:
    if type(skip) is not PlanSkip:
        raise TypeError("skip must be PlanSkip")
    require_nonblank_string("subject_id", skip.subject_id)
    require_nonblank_string("reason", skip.reason)


def validate_research_plan(plan: ResearchPlan) -> None:
    if type(plan) is not ResearchPlan:
        raise TypeError("plan must be ResearchPlan")
    require_nonblank_string("run_id", plan.run_id)
    require_tuple_of("units", plan.units, PlannedUnit)
    require_tuple_of("skips", plan.skips, PlanSkip)
    for unit in plan.units:
        validate_planned_unit(unit)
    for skip in plan.skips:
        validate_plan_skip(skip)
