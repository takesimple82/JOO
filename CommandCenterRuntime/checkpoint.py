from __future__ import annotations

from datetime import datetime, timezone

from CommandCenterRuntime.integrity import integrity_seal
from CommandCenterRuntime.models import (
    CommandCenterState,
    OperationalCheckpoint,
    StageExecutionRecord,
)
from CommandCenterRuntime.vocabularies import (
    CHECKPOINT_COMPLETE,
    CHECKPOINT_FAILED,
    CHECKPOINT_PARTIAL,
    CHECKPOINT_RESUME_SAFE,
    STAGE_STATUS_COMPLETED,
    STAGE_STATUS_FAILED,
    STAGE_STATUS_PENDING,
)


def seal_operational_checkpoint(
    *,
    checkpoint_id: str,
    cycle_id: str,
    wake_event_ids: tuple[str, ...],
    stage_records: tuple[StageExecutionRecord, ...],
    attention_ids: tuple[str, ...],
    created_at: datetime,
    detail: str,
) -> OperationalCheckpoint:
    if type(created_at) is not datetime or created_at.tzinfo is not timezone.utc:
        raise ValueError("created_at must be UTC")
    statuses = {r.status for r in stage_records}
    if STAGE_STATUS_FAILED in statuses:
        status = CHECKPOINT_FAILED
        resume_safe = True  # failure is data; resume without discarding
    elif STAGE_STATUS_PENDING in statuses:
        status = CHECKPOINT_PARTIAL
        resume_safe = True
    elif all(r.status == STAGE_STATUS_COMPLETED or r.status == "SKIPPED" for r in stage_records):
        status = CHECKPOINT_COMPLETE
        resume_safe = True
    else:
        status = CHECKPOINT_PARTIAL
        resume_safe = True
    # Annotate resume-safe explicitly in status when partial/failed.
    if resume_safe and status != CHECKPOINT_COMPLETE:
        # Keep primary status; resume_safe flag answers recoverability.
        pass
    payload = {
        "checkpoint_id": checkpoint_id,
        "cycle_id": cycle_id,
        "wake_event_ids": wake_event_ids,
        "stage_records": tuple(
            (
                r.stage,
                r.status,
                r.reason,
                r.domain_record_ids,
                r.started_at,
                r.finished_at,
            )
            for r in stage_records
        ),
        "attention_ids": attention_ids,
        "status": status,
        "resume_safe": resume_safe,
        "created_at": created_at,
        "detail": detail,
    }
    return OperationalCheckpoint(
        checkpoint_id,
        cycle_id,
        wake_event_ids,
        stage_records,
        attention_ids,
        status,
        resume_safe,
        created_at,
        detail,
        integrity_seal(payload),
    )


def rebuild_command_center_state(
    *,
    state_id: str,
    checkpoints: tuple[OperationalCheckpoint, ...],
    unresolved_attention_ids: tuple[str, ...],
    live_mutation_enabled: bool = False,
) -> CommandCenterState:
    """Projection only — DecisionJournal / durable records remain SoT."""
    if live_mutation_enabled:
        raise ValueError("CommandCenterState must default live_mutation_enabled=False")
    latest = checkpoints[-1] if checkpoints else None
    rebuilt_ids = tuple(c.checkpoint_id for c in checkpoints)
    return CommandCenterState(
        state_id,
        None if latest is None else latest.checkpoint_id,
        unresolved_attention_ids,
        () if latest is None else latest.wake_event_ids,
        False,
        rebuilt_ids,
    )


def checkpoint_answers(checkpoint: OperationalCheckpoint) -> dict:
    """Machine answers: what ran/skipped/failed/pending/complete/resume-safe."""
    by_status: dict[str, list[str]] = {}
    for record in checkpoint.stage_records:
        by_status.setdefault(record.status, []).append(record.stage)
    return {
        "status": checkpoint.status,
        "resume_safe": checkpoint.resume_safe,
        "resume_safe_constant": CHECKPOINT_RESUME_SAFE,
        "by_status": {k: tuple(v) for k, v in by_status.items()},
        "wake_event_ids": checkpoint.wake_event_ids,
        "attention_ids": checkpoint.attention_ids,
    }
