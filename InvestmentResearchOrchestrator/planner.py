from __future__ import annotations

from InvestmentResearchOrchestrator.models.enums import (
    SubjectClass,
)
from InvestmentResearchOrchestrator.models.memory import (
    MemoryDeltaSet,
)
from InvestmentResearchOrchestrator.models.plan import (
    PlannedUnit,
    PlanSkip,
    ResearchPlan,
)
from InvestmentResearchOrchestrator.models.re_research import (
    ReResearchRequestSet,
)
from InvestmentResearchOrchestrator.models.scan import (
    ScanDeltaSet,
)
from InvestmentResearchOrchestrator.validation.memory import (
    validate_memory_delta_set,
)
from InvestmentResearchOrchestrator.validation.plan import (
    validate_research_plan,
)
from InvestmentResearchOrchestrator.validation.re_research import (
    validate_re_research_request_set,
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

    def plan_re_research(
        self,
        request_set: ReResearchRequestSet,
        *,
        memory: MemoryDeltaSet | None = None,
        unresolved_awareness: tuple | None = None,
        scan_context: ScanDeltaSet | None = None,
    ) -> ResearchPlan:
        validate_re_research_request_set(request_set)
        if memory is not None:
            validate_memory_delta_set(memory)
        if unresolved_awareness is not None:
            if type(unresolved_awareness) is not tuple:
                raise TypeError(
                    "unresolved_awareness must be tuple"
                )
        if scan_context is not None:
            validate_scan_delta_set(scan_context)

        in_scope: set[str] | None = None
        if scan_context is not None:
            in_scope = {
                delta.subject_id for delta in scan_context.deltas
            }

        units: list[PlannedUnit] = []
        skips: list[PlanSkip] = []
        known_types = frozenset(_TASK_TYPES.values())

        for index, request in enumerate(request_set.requests):
            if request.task_type not in known_types:
                raise ValueError(
                    "unknown task_type not in allowlist: "
                    f"{request.task_type}"
                )
            if (
                in_scope is not None
                and request.subject_key not in in_scope
            ):
                skips.append(
                    PlanSkip(
                        subject_id=request.subject_key,
                        reason="subject_out_of_scan_scope",
                    )
                )
                continue
            research_id = (
                f"{request_set.run_id}:attempt:"
                f"{request_set.attempt}:unit:{index}:"
                f"{request.subject_key}"
            )
            units.append(
                PlannedUnit(
                    research_id=research_id,
                    subject_id=request.subject_key,
                    task_type=request.task_type,
                    priority=request.priority,
                    title=(
                        f"Re-research for {request.subject_key}"
                    ),
                    objective=(
                        f"Re-research {request.reason_code.value} "
                        f"for subject {request.subject_key}"
                    ),
                )
            )

        plan = ResearchPlan(
            run_id=request_set.run_id,
            units=tuple(units),
            skips=tuple(skips),
        )
        validate_research_plan(plan)
        return plan
