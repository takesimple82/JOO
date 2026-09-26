from __future__ import annotations

from CommandCenterRuntime.models import StagePlanEntry
from CommandCenterRuntime.vocabularies import (
    FAILURE_STAGE_SKIP,
    STAGE_ORDER,
    STAGE_PREDECESSORS,
    STAGE_STATUS_BLOCKED,
    STAGE_STATUS_COMPLETED,
    STAGE_STATUS_PENDING,
    STAGE_STATUS_SKIPPED,
)


def ordered_required_stages(
    plan: tuple[StagePlanEntry, ...],
) -> tuple[str, ...]:
    required = {e.stage for e in plan if e.required}
    unknown = required - set(STAGE_ORDER)
    if unknown:
        raise ValueError(f"unknown stages: {sorted(unknown)}")
    return tuple(s for s in STAGE_ORDER if s in required)


def assert_no_stage_skip(
    *,
    stage: str,
    required_stages: tuple[str, ...],
    completed_or_skipped: dict[str, str],
) -> None:
    """Fail closed if a required predecessor is missing."""
    if stage not in required_stages:
        return
    for pred in STAGE_PREDECESSORS.get(stage, ()):
        if pred not in required_stages:
            continue
        status = completed_or_skipped.get(pred)
        if status not in {STAGE_STATUS_COMPLETED, STAGE_STATUS_SKIPPED}:
            raise ValueError(f"{FAILURE_STAGE_SKIP}:{stage}:missing:{pred}")


def initial_stage_status_map(
    required_stages: tuple[str, ...],
) -> dict[str, str]:
    return {
        stage: (
            STAGE_STATUS_PENDING
            if stage in required_stages
            else STAGE_STATUS_SKIPPED
        )
        for stage in STAGE_ORDER
    }


def mark_blocked(status_map: dict[str, str], stage: str) -> None:
    status_map[stage] = STAGE_STATUS_BLOCKED
