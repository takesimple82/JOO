from __future__ import annotations

from InvestmentResearchOrchestrator.models.enums import (
    SubjectClass,
)
from InvestmentResearchOrchestrator.models.plan import (
    PlannedUnit,
    PlanSkip,
    ResearchPlan,
)
from InvestmentResearchOrchestrator.models.scan import (
    ScanDeltaSet,
)
from InvestmentResearchOrchestrator.validation.plan import (
    validate_research_plan,
)
from InvestmentResearchOrchestrator.validation.scan import (
    validate_scan_delta_set,
)

HOLDING_TASK_TYPE = "HOLDING_STRUCTURAL"
WATCHLIST_TASK_TYPE = "WATCHLIST_STRUCTURAL"

_TASK_TYPES = {
    SubjectClass.HOLDING: HOLDING_TASK_TYPE,
    SubjectClass.WATCHLIST: WATCHLIST_TASK_TYPE,
}
_PRIORITIES = {
    SubjectClass.HOLDING: "P0",
    SubjectClass.WATCHLIST: "P1",
}


class ResearchPlanner:
    """Convert structural scan deltas into ordered planned units."""

    def plan(self, delta_set: ScanDeltaSet) -> ResearchPlan:
        validate_scan_delta_set(delta_set)
        units: list[PlannedUnit] = []
        skips: list[PlanSkip] = []

        if len(delta_set.deltas) == 0:
            skips.append(
                PlanSkip(
                    subject_id="*",
                    reason="empty_scan_no_material_delta",
                )
            )
            plan = ResearchPlan(
                run_id=delta_set.run_id,
                units=(),
                skips=tuple(skips),
            )
            validate_research_plan(plan)
            return plan

        for index, delta in enumerate(delta_set.deltas):
            subject_class = delta.subject_class
            if subject_class not in _TASK_TYPES:
                skips.append(
                    PlanSkip(
                        subject_id=delta.subject_id,
                        reason="unknown_subject_class",
                    )
                )
                continue
            task_type = _TASK_TYPES[subject_class]
            priority = _PRIORITIES[subject_class]
            research_id = (
                f"{delta_set.run_id}:unit:{index}:"
                f"{delta.subject_id}"
            )
            units.append(
                PlannedUnit(
                    research_id=research_id,
                    subject_id=delta.subject_id,
                    task_type=task_type,
                    priority=priority,
                    title=(
                        f"Structural research for "
                        f"{delta.subject_id}"
                    ),
                    objective=(
                        f"Investigate structural portfolio "
                        f"change {delta.change_class.value} "
                        f"for subject {delta.subject_id}"
                    ),
                )
            )

        plan = ResearchPlan(
            run_id=delta_set.run_id,
            units=tuple(units),
            skips=tuple(skips),
        )
        validate_research_plan(plan)
        return plan
