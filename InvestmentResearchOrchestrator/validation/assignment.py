from __future__ import annotations

from InvestmentResearchOrchestrator.models.assignment import (
    CommitteeAssignmentPlan,
    CompletenessBuckets,
    StaticRoutingTable,
)
from InvestmentResearchOrchestrator.validation.common import (
    require_nonblank_string,
)


def validate_completeness_buckets(
    buckets: CompletenessBuckets,
) -> None:
    if type(buckets) is not CompletenessBuckets:
        raise TypeError(
            "buckets must be CompletenessBuckets"
        )
    for field_name in (
        "required",
        "completed",
        "failed",
        "missing",
    ):
        value = getattr(buckets, field_name)
        if type(value) is not tuple:
            raise TypeError(f"{field_name} must be tuple")
        for index, item in enumerate(value):
            if type(item) is not str:
                raise TypeError(
                    f"{field_name}[{index}] must be str"
                )
            if item.strip() == "":
                raise ValueError(
                    f"{field_name}[{index}] must not be blank"
                )


def validate_committee_assignment_plan(
    plan: CommitteeAssignmentPlan,
) -> None:
    if type(plan) is not CommitteeAssignmentPlan:
        raise TypeError(
            "plan must be CommitteeAssignmentPlan"
        )
    require_nonblank_string("research_id", plan.research_id)
    if type(plan.required_committees) is not tuple:
        raise TypeError("required_committees must be tuple")
    for index, committee_id in enumerate(
        plan.required_committees
    ):
        if type(committee_id) is not str:
            raise TypeError(
                f"required_committees[{index}] must be str"
            )
        if committee_id.strip() == "":
            raise ValueError(
                f"required_committees[{index}] must not be blank"
            )
    validate_completeness_buckets(plan.completeness)


def validate_static_routing_table(
    table: StaticRoutingTable,
) -> None:
    if type(table) is not StaticRoutingTable:
        raise TypeError("table must be StaticRoutingTable")
    if type(table.routes) is not tuple:
        raise TypeError("routes must be tuple")
    seen_task_types = set()
    for index, entry in enumerate(table.routes):
        if type(entry) is not tuple or len(entry) != 2:
            raise TypeError(
                f"routes[{index}] must be "
                "(task_type, committees)"
            )
        task_type, committees = entry
        if type(task_type) is not str:
            raise TypeError(
                f"routes[{index}] task_type must be str"
            )
        if task_type.strip() == "":
            raise ValueError(
                f"routes[{index}] task_type must not be blank"
            )
        if task_type in seen_task_types:
            raise ValueError(
                "routes must not contain duplicate task_type"
            )
        seen_task_types.add(task_type)
        if type(committees) is not tuple:
            raise TypeError(
                f"routes[{index}] committees must be tuple"
            )
        if len(committees) == 0:
            raise ValueError(
                f"routes[{index}] committees must not be empty"
            )
        for c_index, committee_id in enumerate(committees):
            if type(committee_id) is not str:
                raise TypeError(
                    f"routes[{index}] committees[{c_index}] "
                    "must be str"
                )
            if committee_id.strip() == "":
                raise ValueError(
                    f"routes[{index}] committees[{c_index}] "
                    "must not be blank"
                )
