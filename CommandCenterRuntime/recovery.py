from __future__ import annotations

from CommandCenterRuntime.checkpoint import rebuild_command_center_state
from CommandCenterRuntime.models import (
    CommandCenterCycleResult,
    HumanAttentionItem,
    IdempotencyRecord,
    OperationalCheckpoint,
    WakeEvent,
)
from CommandCenterRuntime.vocabularies import (
    FAILURE_LIVE_MUTATION_DISABLED,
    FAILURE_RETRY_UNSAFE,
)


UNSAFE_RETRY_KINDS = frozenset({
    "BROKER_MUTATION_AFTER_POSSIBLE_SEND",
    "HUMAN_APPROVAL_CREATION",
    "TEA_CREATION",
    "ORDER_INTENT_RECREATE",
})


def assert_retry_safe(decision_kind: str) -> None:
    if decision_kind in UNSAFE_RETRY_KINDS:
        raise RuntimeError(FAILURE_RETRY_UNSAFE)


def recover_command_center(
    *,
    state_id: str,
    checkpoints: tuple[OperationalCheckpoint, ...],
    attention_items: tuple[HumanAttentionItem, ...],
    idempotency_records: tuple[IdempotencyRecord, ...] = (),
    wake_events: tuple[WakeEvent, ...] = (),
    live_mutation_enabled: bool = False,
) -> CommandCenterCycleResult:
    """Host-agnostic recover entry. Never re-mutate; never recreate Human authority.

    Reads durable checkpoints/attention/idempotency and rebuilds projection.
    Does not discard UNKNOWN/recon attention. Does not enable live SSAM.
    """
    del wake_events  # available for callers; recover does not invent wakes
    if live_mutation_enabled:
        raise RuntimeError(FAILURE_LIVE_MUTATION_DISABLED)

    unresolved = tuple(
        a.attention_id for a in attention_items if a.unresolved
    )
    # Preserve UNKNOWN / recon / integrity failures — never discard.
    preserved_categories = {
        "SUBMISSION_OUTCOME_UNKNOWN",
        "RECONCILIATION_MISMATCH",
        "DATA_INTEGRITY_FAILURE",
    }
    for item in attention_items:
        if item.category in preserved_categories and not item.unresolved:
            # Caller may mark resolved only with explicit human action elsewhere.
            pass

    state = rebuild_command_center_state(
        state_id=state_id,
        checkpoints=checkpoints,
        unresolved_attention_ids=unresolved,
        live_mutation_enabled=False,
    )
    latest = checkpoints[-1] if checkpoints else None
    # Idempotency records are loaded by caller store; recover only validates seals.
    for record in idempotency_records:
        if type(record.idempotency_key) is not str or not record.idempotency_key:
            raise ValueError("corrupt idempotency record")

    return CommandCenterCycleResult(
        "recovered",
        (),
        (),
        latest,
        attention_items,
        None,
        state,
        tuple(r.idempotency_key for r in idempotency_records),
    )
