from __future__ import annotations

from datetime import datetime, timezone

from CommandCenterRuntime.integrity import integrity_seal
from CommandCenterRuntime.models import HumanAttentionItem, WakeEvent
from CommandCenterRuntime.vocabularies import (
    ATTENTION_ALLOCATION_REVISION_REQUIRED,
    ATTENTION_DATA_INTEGRITY_FAILURE,
    ATTENTION_INVESTMENT_APPROVAL_REQUIRED,
    ATTENTION_POLICY_CONFLICT,
    ATTENTION_PRIORITY,
    ATTENTION_PROVIDER_FAILURE,
    ATTENTION_RECONCILIATION_MISMATCH,
    ATTENTION_SUBMISSION_OUTCOME_UNKNOWN,
    ATTENTION_THESIS_INVALIDATED,
    ATTENTION_TRADE_AUTHORIZATION_REQUIRED,
    WAKE_APPROVAL_TRANSITION,
    WAKE_CAPITAL_ORDERABLE_CASH_CHANGED,
    WAKE_POLICY_SUPERSEDED,
    WAKE_PROVIDER_FAILURE,
    WAKE_RECONCILIATION_MISMATCH,
    WAKE_SUBMISSION_OUTCOME_UNKNOWN,
    WAKE_THESIS_TRANSITION,
)


def _priority(category: str) -> int:
    if category not in ATTENTION_PRIORITY:
        raise ValueError(f"unknown attention category: {category}")
    return ATTENTION_PRIORITY[category]


def seal_human_attention_item(
    *,
    attention_id: str,
    category: str,
    wake_event_id: str,
    bound_record_ids: tuple[str, ...],
    subject_ids: tuple[str, ...],
    created_at: datetime,
    detail: str,
    unresolved: bool = True,
) -> HumanAttentionItem:
    if type(created_at) is not datetime or created_at.tzinfo is not timezone.utc:
        raise ValueError("created_at must be UTC")
    if type(bound_record_ids) is not tuple or not bound_record_ids:
        raise ValueError("bound_record_ids required (exact IDs)")
    priority = _priority(category)
    payload = {
        "attention_id": attention_id,
        "category": category,
        "wake_event_id": wake_event_id,
        "bound_record_ids": bound_record_ids,
        "subject_ids": subject_ids,
        "unresolved": unresolved,
        "created_at": created_at,
        "detail": detail,
        "priority": priority,
    }
    return HumanAttentionItem(
        attention_id,
        category,
        wake_event_id,
        bound_record_ids,
        subject_ids,
        unresolved,
        created_at,
        detail,
        priority,
        integrity_seal(payload),
    )


def attention_dedupe_key(item: HumanAttentionItem) -> tuple:
    return (
        item.category,
        item.bound_record_ids,
        item.subject_ids,
        item.unresolved,
    )


def dedupe_unresolved(
    existing: tuple[HumanAttentionItem, ...],
    candidate: HumanAttentionItem,
) -> HumanAttentionItem | None:
    """Return None if identical unresolved item already exists."""
    key = attention_dedupe_key(candidate)
    for item in existing:
        if item.unresolved and attention_dedupe_key(item) == key:
            return None
    return candidate


def attention_for_wake(
    *,
    wake: WakeEvent,
    created_at: datetime,
    bound_record_ids: tuple[str, ...] | None = None,
    thesis_state: str | None = None,
) -> HumanAttentionItem | None:
    """Map wake → safety-critical attention. Never invent Human authority."""
    ids = bound_record_ids or (wake.fact_or_evidence_id,)
    aid = f"att:{wake.wake_event_id}"
    wt = wake.wake_type
    if wt == WAKE_SUBMISSION_OUTCOME_UNKNOWN:
        return seal_human_attention_item(
            attention_id=aid,
            category=ATTENTION_SUBMISSION_OUTCOME_UNKNOWN,
            wake_event_id=wake.wake_event_id,
            bound_record_ids=ids,
            subject_ids=wake.subject_ids,
            created_at=created_at,
            detail="submission outcome unknown; no reorder",
        )
    if wt == WAKE_RECONCILIATION_MISMATCH:
        return seal_human_attention_item(
            attention_id=aid,
            category=ATTENTION_RECONCILIATION_MISMATCH,
            wake_event_id=wake.wake_event_id,
            bound_record_ids=ids,
            subject_ids=wake.subject_ids,
            created_at=created_at,
            detail="reconciliation mismatch",
        )
    if wt == WAKE_PROVIDER_FAILURE:
        return seal_human_attention_item(
            attention_id=aid,
            category=ATTENTION_PROVIDER_FAILURE,
            wake_event_id=wake.wake_event_id,
            bound_record_ids=ids,
            subject_ids=wake.subject_ids,
            created_at=created_at,
            detail="provider outage recorded as data",
        )
    if wt == WAKE_POLICY_SUPERSEDED:
        return seal_human_attention_item(
            attention_id=aid,
            category=ATTENTION_POLICY_CONFLICT,
            wake_event_id=wake.wake_event_id,
            bound_record_ids=ids,
            subject_ids=wake.subject_ids,
            created_at=created_at,
            detail="policy supersession invalidates dependents",
        )
    if wt == WAKE_CAPITAL_ORDERABLE_CASH_CHANGED:
        return seal_human_attention_item(
            attention_id=aid,
            category=ATTENTION_ALLOCATION_REVISION_REQUIRED,
            wake_event_id=wake.wake_event_id,
            bound_record_ids=ids,
            subject_ids=wake.subject_ids,
            created_at=created_at,
            detail="capital-only change; allocation may be stale",
        )
    if wt == WAKE_THESIS_TRANSITION and thesis_state == "INVALIDATED":
        return seal_human_attention_item(
            attention_id=aid,
            category=ATTENTION_THESIS_INVALIDATED,
            wake_event_id=wake.wake_event_id,
            bound_record_ids=ids,
            subject_ids=wake.subject_ids,
            created_at=created_at,
            detail="thesis invalidated",
        )
    if wt == WAKE_APPROVAL_TRANSITION:
        # Surface pending gates; never auto-approve.
        # Prefer TEA vs IHA based on fact id prefix convention in bound ids.
        joined = "|".join(ids)
        if "TEA" in joined.upper() or "TRADE" in joined.upper():
            category = ATTENTION_TRADE_AUTHORIZATION_REQUIRED
        else:
            category = ATTENTION_INVESTMENT_APPROVAL_REQUIRED
        return seal_human_attention_item(
            attention_id=aid,
            category=category,
            wake_event_id=wake.wake_event_id,
            bound_record_ids=ids,
            subject_ids=wake.subject_ids,
            created_at=created_at,
            detail="human gate transition; no auto-approval",
        )
    return None


def sort_attention_safety_first(
    items: tuple[HumanAttentionItem, ...],
) -> tuple[HumanAttentionItem, ...]:
    return tuple(sorted(items, key=lambda x: (x.priority, x.created_at.isoformat(), x.attention_id)))


def refuse_auto_approval(*_args, **_kwargs):
    from CommandCenterRuntime.vocabularies import FAILURE_AUTO_APPROVAL_FORBIDDEN

    raise RuntimeError(FAILURE_AUTO_APPROVAL_FORBIDDEN)


def refuse_gate_merge(*_args, **_kwargs):
    from CommandCenterRuntime.vocabularies import FAILURE_GATE_MERGE_FORBIDDEN

    raise RuntimeError(FAILURE_GATE_MERGE_FORBIDDEN)


# Re-export category constants used by tests/callers.
ATTENTION_CATEGORIES = (
    ATTENTION_INVESTMENT_APPROVAL_REQUIRED,
    ATTENTION_TRADE_AUTHORIZATION_REQUIRED,
    ATTENTION_THESIS_INVALIDATED,
    ATTENTION_ALLOCATION_REVISION_REQUIRED,
    ATTENTION_SUBMISSION_OUTCOME_UNKNOWN,
    ATTENTION_RECONCILIATION_MISMATCH,
    ATTENTION_PROVIDER_FAILURE,
    ATTENTION_POLICY_CONFLICT,
    ATTENTION_DATA_INTEGRITY_FAILURE,
)


def open_limit_requires_human_attention(
    *,
    attention_id: str,
    wake_event_id: str,
    bound_record_ids: tuple[str, ...],
    subject_ids: tuple[str, ...],
    created_at: datetime,
    detail: str,
):
    """Escalate open LIMIT to HumanAttention. Never auto cancel/modify."""
    from CommandCenterRuntime.vocabularies import ATTENTION_OPEN_LIMIT_REQUIRES_HUMAN

    return seal_human_attention_item(
        attention_id=attention_id,
        category=ATTENTION_OPEN_LIMIT_REQUIRES_HUMAN,
        wake_event_id=wake_event_id,
        bound_record_ids=bound_record_ids,
        subject_ids=subject_ids,
        created_at=created_at,
        detail=detail,
    )
