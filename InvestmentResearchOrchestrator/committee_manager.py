from __future__ import annotations

from InvestmentResearchOrchestrator.models.assignment import (
    CommitteeAssignmentPlan,
    CompletenessBuckets,
    StaticRoutingTable,
)
from InvestmentResearchOrchestrator.models.plan import (
    PlannedUnit,
)
from InvestmentResearchOrchestrator.validation.assignment import (
    validate_committee_assignment_plan,
    validate_static_routing_table,
)
from InvestmentResearchOrchestrator.validation.plan import (
    validate_planned_unit,
)


class StaticCommitteeRouter:
    """Static allowlist router (IRO-M1). No adaptive selection."""

    def __init__(self, routing_table: StaticRoutingTable) -> None:
        validate_static_routing_table(routing_table)
        self._routes = {
            task_type: committees
            for task_type, committees in routing_table.routes
        }

    def route(
        self,
        unit: PlannedUnit,
    ) -> CommitteeAssignmentPlan:
        validate_planned_unit(unit)
        if unit.task_type not in self._routes:
            raise ValueError(
                f"unknown task_type not in allowlist: "
                f"{unit.task_type}"
            )
        required = self._routes[unit.task_type]
        plan = CommitteeAssignmentPlan(
            research_id=unit.research_id,
            required_committees=required,
            completeness=CompletenessBuckets(
                required=required,
                completed=(),
                failed=(),
                missing=(),
            ),
        )
        validate_committee_assignment_plan(plan)
        return plan

    def update_completeness(
        self,
        plan: CommitteeAssignmentPlan,
        *,
        completed: tuple[str, ...],
        failed: tuple[str, ...],
        missing: tuple[str, ...],
    ) -> CommitteeAssignmentPlan:
        validate_committee_assignment_plan(plan)
        for name, values in (
            ("completed", completed),
            ("failed", failed),
            ("missing", missing),
        ):
            if type(values) is not tuple:
                raise TypeError(f"{name} must be tuple")
            for index, item in enumerate(values):
                if type(item) is not str or item.strip() == "":
                    raise ValueError(
                        f"{name}[{index}] must be nonblank str"
                    )
        updated = CommitteeAssignmentPlan(
            research_id=plan.research_id,
            required_committees=plan.required_committees,
            completeness=CompletenessBuckets(
                required=plan.required_committees,
                completed=completed,
                failed=failed,
                missing=missing,
            ),
        )
        validate_committee_assignment_plan(updated)
        return updated
