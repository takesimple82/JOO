from __future__ import annotations

from datetime import datetime, timezone

from CommandCenterRuntime.attention import sort_attention_safety_first
from CommandCenterRuntime.integrity import integrity_seal
from CommandCenterRuntime.models import (
    CommandCenterReport,
    DetectedChange,
    HumanAttentionItem,
    OperationalCheckpoint,
    WakeEvent,
)


def build_command_center_report(
    *,
    report_id: str,
    cycle_id: str,
    wake_events: tuple[WakeEvent, ...],
    changes: tuple[DetectedChange, ...],
    attention_items: tuple[HumanAttentionItem, ...],
    checkpoint: OperationalCheckpoint | None,
    created_at: datetime,
    warnings: tuple[str, ...] = (),
) -> CommandCenterReport:
    if type(created_at) is not datetime or created_at.tzinfo is not timezone.utc:
        raise ValueError("created_at must be UTC")
    what_changed = tuple(f"{c.change_kind}:{c.detail}" for c in changes)
    why_woke = tuple(f"{w.wake_type}:{w.fact_or_evidence_id}" for w in wake_events)
    impacts = ()
    if checkpoint is not None:
        impacts = tuple(
            f"{r.stage}={r.status}" for r in checkpoint.stage_records if r.status != "SKIPPED"
        )
    ordered = sort_attention_safety_first(attention_items)
    human_actions = tuple(
        f"{a.category}:{a.attention_id}" for a in ordered if a.unresolved
    )
    execution_status = "NO_LIVE_MUTATION"
    if checkpoint is not None:
        execution_status = checkpoint.status
    payload = {
        "report_id": report_id,
        "cycle_id": cycle_id,
        "what_changed": what_changed,
        "why_woke": why_woke,
        "impacts": impacts,
        "human_actions": human_actions,
        "execution_status": execution_status,
        "warnings": warnings,
        "created_at": created_at,
    }
    return CommandCenterReport(
        report_id,
        cycle_id,
        what_changed,
        why_woke,
        impacts,
        human_actions,
        execution_status,
        warnings,
        created_at,
        integrity_seal(payload),
    )
