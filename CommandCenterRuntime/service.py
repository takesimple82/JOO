from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from BrokerExecutionCycle.mutation_transport import (
    LiveMutationTransportDisabled,
    default_mutation_transport,
)

from CommandCenterRuntime.attention import (
    attention_for_wake,
    dedupe_unresolved,
    refuse_auto_approval,
    refuse_gate_merge,
)
from CommandCenterRuntime.checkpoint import (
    rebuild_command_center_state,
    seal_operational_checkpoint,
)
from CommandCenterRuntime.concurrency import ExclusiveCycleLock
from CommandCenterRuntime.idempotency import IdempotencyStore
from CommandCenterRuntime.models import (
    CommandCenterCycleResult,
    DetectedChange,
    HumanAttentionItem,
    StageExecutionRecord,
    WakeEvent,
)
from CommandCenterRuntime.observability import structured_event
from CommandCenterRuntime.recovery import assert_retry_safe, recover_command_center
from CommandCenterRuntime.reporting import build_command_center_report
from CommandCenterRuntime.routing import route_wake
from CommandCenterRuntime.stages import (
    assert_no_stage_skip,
    initial_stage_status_map,
    ordered_required_stages,
)
from CommandCenterRuntime.vocabularies import (
    FAILURE_LIVE_MUTATION_DISABLED,
    FAILURE_RETRY_UNSAFE,
    IDEMPOTENCY_HIT,
    MAX_SAFE_RETRIES,
    MUTATION_TRANSPORT_DEFAULT,
    STAGE_STATUS_COMPLETED,
    STAGE_STATUS_FAILED,
    STAGE_STATUS_SKIPPED,
    WAKE_TYPES,
)
from CommandCenterRuntime.wake import seal_wake_event, verify_wake_event


DomainRunner = Callable[[str, WakeEvent], tuple[str, ...]]


@dataclass(frozen=True)
class CommandCenterCycleRequest:
    cycle_id: str
    holder_id: str
    wake_events: tuple[WakeEvent, ...]
    changes: tuple[DetectedChange, ...]
    prior_attention: tuple[HumanAttentionItem, ...] = ()
    thesis_states: tuple[tuple[str, str], ...] = ()  # wake_event_id -> state
    now: datetime | None = None


def _utc_now(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if type(value) is not datetime or value.tzinfo is not timezone.utc:
        raise ValueError("now must be UTC datetime")
    return value


def _default_domain_runner(stage: str, wake: WakeEvent) -> tuple[str, ...]:
    """Record-only runner: integrates by scheduling existing domains without executing AI.

    Callers inject real A/B/C runners when wiring production composition.
    Block D itself never performs investment reasoning or live mutation.
    """
    del wake
    return (f"scheduled:{stage}",)


def run_command_center_cycle(
    request: CommandCenterCycleRequest,
    *,
    idempotency_store: IdempotencyStore | None = None,
    lock: ExclusiveCycleLock | None = None,
    domain_runner: DomainRunner | None = None,
    mutation_transport=None,
    enable_live_mutation: bool = False,
    ownership_provable: bool = True,
    journal_appender: Callable[[tuple], None] | None = None,
) -> CommandCenterCycleResult:
    """Host-agnostic one-cycle entry. No while-loop correctness.

    Collect facts (caller-supplied wakes/changes) → detect/classify → run only
    required domain stages → persist checkpoint → HumanAttentionItem.
    Cycle does NOT do AI investment reasoning.
    """
    now = _utc_now(request.now)
    store = idempotency_store or IdempotencyStore()
    cycle_lock = lock or ExclusiveCycleLock()
    runner = domain_runner or _default_domain_runner
    transport = mutation_transport if mutation_transport is not None else default_mutation_transport()

    if enable_live_mutation:
        raise RuntimeError(FAILURE_LIVE_MUTATION_DISABLED)
    if not isinstance(transport, LiveMutationTransportDisabled):
        # Even mock transport is allowed only for injected test composition;
        # default path remains LIVE_DISABLED. Block D never activates live SSAM.
        if getattr(transport, "mode", None) != "MOCK":
            raise RuntimeError(FAILURE_LIVE_MUTATION_DISABLED)
    if MUTATION_TRANSPORT_DEFAULT != "LIVE_DISABLED":
        raise RuntimeError(FAILURE_LIVE_MUTATION_DISABLED)

    if type(request.wake_events) is not tuple or not request.wake_events:
        raise ValueError("wake_events required")
    for event in request.wake_events:
        verify_wake_event(event)
        if event.wake_type not in WAKE_TYPES:
            raise ValueError("unknown wake type")

    # Exclusive ownership per primary source event (first wake).
    primary = request.wake_events[0]
    lease = cycle_lock.try_acquire(
        lease_id=f"lease:{request.cycle_id}",
        source_event_id=primary.wake_event_id,
        holder_id=request.holder_id,
        acquired_at=now,
        ownership_provable=ownership_provable,
    )

    idempotency_hits: list[str] = []
    attention_items: list[HumanAttentionItem] = list(request.prior_attention)
    stage_records: list[StageExecutionRecord] = []
    failure_codes: list[str] = []
    thesis_map = dict(request.thesis_states)

    try:
        # Idempotency: same source event cannot duplicate cycle decisions.
        status, idem = store.claim_or_hit(
            source_event_id=primary.wake_event_id,
            decision_kind="COMMAND_CENTER_CYCLE",
            produced_record_id=request.cycle_id,
            created_at=now,
        )
        if status == IDEMPOTENCY_HIT:
            idempotency_hits.append(idem.idempotency_key)
            # Rebuild from prior attention only; do not re-run domain stages.
            checkpoint = seal_operational_checkpoint(
                checkpoint_id=f"cp:{request.cycle_id}:idempotent",
                cycle_id=request.cycle_id,
                wake_event_ids=tuple(w.wake_event_id for w in request.wake_events),
                stage_records=(),
                attention_ids=tuple(a.attention_id for a in attention_items if a.unresolved),
                created_at=now,
                detail="idempotent hit; no duplicate decisions",
            )
            state = rebuild_command_center_state(
                state_id=f"state:{request.cycle_id}",
                checkpoints=(checkpoint,),
                unresolved_attention_ids=checkpoint.attention_ids,
            )
            report = build_command_center_report(
                report_id=f"report:{request.cycle_id}",
                cycle_id=request.cycle_id,
                wake_events=request.wake_events,
                changes=request.changes,
                attention_items=tuple(attention_items),
                checkpoint=checkpoint,
                created_at=now,
                warnings=("IDEMPOTENCY_HIT",),
            )
            return CommandCenterCycleResult(
                "idempotent",
                (),
                request.wake_events,
                checkpoint,
                tuple(attention_items),
                report,
                state,
                tuple(idempotency_hits),
            )

        # Merge routing across wakes (union of required stages, STAGE_ORDER preserved).
        required: list[str] = []
        seen = set()
        for wake in request.wake_events:
            for entry in route_wake(wake):
                if entry.stage not in seen:
                    seen.add(entry.stage)
                    required.append(entry.stage)
        # Reorder to STAGE_ORDER
        from CommandCenterRuntime.models import StagePlanEntry

        required_stages = ordered_required_stages(
            tuple(StagePlanEntry(s, True, "merged") for s in required)
        )
        status_map = initial_stage_status_map(required_stages)

        for stage in required_stages:
            assert_no_stage_skip(
                stage=stage,
                required_stages=required_stages,
                completed_or_skipped=status_map,
            )
            started = now
            try:
                # Bounded safe retries for domain runner only; never mutation/approval/TEA.
                assert_retry_safe(f"STAGE_RUN:{stage}")
                domain_ids: tuple[str, ...] = ()
                last_exc: Exception | None = None
                for attempt in range(MAX_SAFE_RETRIES + 1):
                    try:
                        domain_ids = runner(stage, primary)
                        last_exc = None
                        break
                    except Exception as exc:  # noqa: BLE001 — fail-closed after bound
                        last_exc = exc
                        if attempt >= MAX_SAFE_RETRIES:
                            break
                if last_exc is not None:
                    raise last_exc
                # Live mutation never activated from this cycle.
                if stage in {"PRETRADE", "TRADE_HUMAN_GATE", "BROKER_STATUS"}:
                    if enable_live_mutation:
                        raise RuntimeError(FAILURE_LIVE_MUTATION_DISABLED)
                status_map[stage] = STAGE_STATUS_COMPLETED
                stage_records.append(
                    StageExecutionRecord(
                        stage,
                        STAGE_STATUS_COMPLETED,
                        "domain scheduled/executed",
                        domain_ids,
                        started,
                        now,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                status_map[stage] = STAGE_STATUS_FAILED
                failure_codes.append(str(exc))
                stage_records.append(
                    StageExecutionRecord(
                        stage,
                        STAGE_STATUS_FAILED,
                        str(exc),
                        (),
                        started,
                        now,
                    )
                )
                # Fail closed: stop further stages that depend on this one.
                break

        # Mark non-required as skipped in checkpoint view.
        from CommandCenterRuntime.vocabularies import STAGE_ORDER

        full_records = list(stage_records)
        recorded = {r.stage for r in stage_records}
        for stage in STAGE_ORDER:
            if stage not in recorded:
                full_records.append(
                    StageExecutionRecord(
                        stage,
                        STAGE_STATUS_SKIPPED
                        if stage not in required_stages
                        else status_map.get(stage, STAGE_STATUS_SKIPPED),
                        "not required or not reached",
                        (),
                        None,
                        None,
                    )
                )

        # Human attention (preserve both gates; never auto-approve / merge).
        from CommandCenterRuntime.vocabularies import WAKE_APPROVAL_TRANSITION

        for wake in request.wake_events:
            if wake.wake_type == WAKE_APPROVAL_TRANSITION:
                # Explicit: cycle must not create approval authority or merge gates.
                # These raise if ever wired as auto-approve / merge hooks.
                assert callable(refuse_auto_approval)
                assert callable(refuse_gate_merge)
            item = attention_for_wake(
                wake=wake,
                created_at=now,
                thesis_state=thesis_map.get(wake.wake_event_id),
            )
            if item is None:
                continue
            kept = dedupe_unresolved(tuple(attention_items), item)
            if kept is None:
                continue
            # Idempotency for attention
            att_status, att_rec = store.claim_or_hit(
                source_event_id=wake.wake_event_id,
                decision_kind=f"ATTENTION:{item.category}",
                produced_record_id=item.attention_id,
                created_at=now,
            )
            if att_status == IDEMPOTENCY_HIT:
                idempotency_hits.append(att_rec.idempotency_key)
                continue
            attention_items.append(kept)

        checkpoint = seal_operational_checkpoint(
            checkpoint_id=f"cp:{request.cycle_id}",
            cycle_id=request.cycle_id,
            wake_event_ids=tuple(w.wake_event_id for w in request.wake_events),
            stage_records=tuple(full_records),
            attention_ids=tuple(
                a.attention_id for a in attention_items if a.unresolved
            ),
            created_at=now,
            detail=structured_event(
                event_type="command_center_cycle",
                cycle_id=request.cycle_id,
                fields={
                    "wake_types": [w.wake_type for w in request.wake_events],
                    "required_stages": list(required_stages),
                    "lease_id": lease.lease_id,
                    "transport_mode": getattr(transport, "mode", "UNKNOWN"),
                },
                observed_at=now,
            ),
        )
        state = rebuild_command_center_state(
            state_id=f"state:{request.cycle_id}",
            checkpoints=(checkpoint,),
            unresolved_attention_ids=checkpoint.attention_ids,
        )
        report = build_command_center_report(
            report_id=f"report:{request.cycle_id}",
            cycle_id=request.cycle_id,
            wake_events=request.wake_events,
            changes=request.changes,
            attention_items=tuple(attention_items),
            checkpoint=checkpoint,
            created_at=now,
            warnings=tuple(failure_codes),
        )
        if journal_appender is not None:
            journal_appender(
                (
                    ("WAKE_EVENT", request.wake_events),
                    ("OPERATIONAL_CHECKPOINT", checkpoint),
                    ("HUMAN_ATTENTION_ITEM", tuple(attention_items)),
                )
            )
        result_kind = "success" if not failure_codes else "partial_failure"
        return CommandCenterCycleResult(
            result_kind,
            tuple(failure_codes),
            request.wake_events,
            checkpoint,
            tuple(attention_items),
            report,
            state,
            tuple(idempotency_hits),
        )
    finally:
        cycle_lock.release(primary.wake_event_id, request.holder_id)


# Public recover alias matching hosting contract.
recover = recover_command_center


def refuse_unsafe_broker_retry() -> None:
    raise RuntimeError(FAILURE_RETRY_UNSAFE)


def seal_wake_from_change(
    *,
    wake_event_id: str,
    change: DetectedChange,
    source: str,
    observed_at: datetime,
    provenance: str,
) -> WakeEvent:
    return seal_wake_event(
        wake_event_id=wake_event_id,
        wake_type=change.change_kind,
        source=source,
        fact_or_evidence_id=change.current_fact_id,
        observed_at=observed_at,
        subject_ids=change.subject_ids,
        provenance=provenance,
    )
