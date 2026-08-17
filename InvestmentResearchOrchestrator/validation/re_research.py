from __future__ import annotations

from InvestmentResearchOrchestrator.models.enums import (
    EscalationMarker,
    EscalationReasonCode,
    ReResearchReasonCode,
)
from InvestmentResearchOrchestrator.models.re_research import (
    EscalationRecord,
    ReResearchBudget,
    ReResearchRequest,
    ReResearchRequestSet,
)
from InvestmentResearchOrchestrator.validation.common import (
    require_datetime,
    require_enum,
    require_int,
    require_nonblank_string,
    require_tuple_of,
)

_PRIORITIES = frozenset({"P0", "P1", "P2"})


def validate_re_research_budget(
    budget: ReResearchBudget,
) -> None:
    if type(budget) is not ReResearchBudget:
        raise TypeError("budget must be ReResearchBudget")
    require_int("max_attempts", budget.max_attempts)
    if budget.max_attempts <= 0:
        raise ValueError("max_attempts must be > 0")
    require_int("remaining", budget.remaining)
    if budget.remaining < 0:
        raise ValueError("remaining must be >= 0")
    if budget.remaining > budget.max_attempts:
        raise ValueError(
            "remaining must be <= max_attempts"
        )


def validate_re_research_request(
    request: ReResearchRequest,
) -> None:
    if type(request) is not ReResearchRequest:
        raise TypeError(
            "request must be ReResearchRequest"
        )
    require_nonblank_string("request_id", request.request_id)
    require_nonblank_string(
        "subject_key",
        request.subject_key,
    )
    require_enum(
        "reason_code",
        request.reason_code,
        ReResearchReasonCode,
    )
    require_nonblank_string("task_type", request.task_type)
    require_tuple_of(
        "source_case_ids",
        request.source_case_ids,
        str,
    )
    if len(request.source_case_ids) == 0:
        raise ValueError(
            "source_case_ids must not be empty"
        )
    for index, case_id in enumerate(request.source_case_ids):
        require_nonblank_string(
            f"source_case_ids[{index}]",
            case_id,
        )
    require_nonblank_string("priority", request.priority)
    if request.priority not in _PRIORITIES:
        raise ValueError("priority must be P0, P1, or P2")


def validate_re_research_request_set(
    request_set: ReResearchRequestSet,
) -> None:
    if type(request_set) is not ReResearchRequestSet:
        raise TypeError(
            "request_set must be ReResearchRequestSet"
        )
    require_nonblank_string("run_id", request_set.run_id)
    require_int("attempt", request_set.attempt)
    if request_set.attempt < 0:
        raise ValueError("attempt must be >= 0")
    require_tuple_of(
        "requests",
        request_set.requests,
        ReResearchRequest,
    )
    for request in request_set.requests:
        validate_re_research_request(request)


def validate_escalation_record(
    record: EscalationRecord,
) -> None:
    if type(record) is not EscalationRecord:
        raise TypeError(
            "record must be EscalationRecord"
        )
    require_nonblank_string("run_id", record.run_id)
    require_enum("marker", record.marker, EscalationMarker)
    require_enum(
        "reason_code",
        record.reason_code,
        EscalationReasonCode,
    )
    require_tuple_of(
        "unresolved_case_ids",
        record.unresolved_case_ids,
        str,
    )
    for index, case_id in enumerate(record.unresolved_case_ids):
        require_nonblank_string(
            f"unresolved_case_ids[{index}]",
            case_id,
        )
    require_int("max_attempts", record.max_attempts)
    if record.max_attempts <= 0:
        raise ValueError("max_attempts must be > 0")
    require_int("remaining", record.remaining)
    if record.remaining < 0:
        raise ValueError("remaining must be >= 0")
    if record.remaining > record.max_attempts:
        raise ValueError(
            "remaining must be <= max_attempts"
        )
    require_datetime("created_at", record.created_at)
