from __future__ import annotations

from datetime import datetime, timezone

from CommandCenterRuntime.integrity import integrity_seal
from CommandCenterRuntime.models import IdempotencyRecord
from CommandCenterRuntime.vocabularies import (
    FAILURE_DUPLICATE_DECISION,
    IDEMPOTENCY_HIT,
    IDEMPOTENCY_MISS,
)


def make_idempotency_key(source_event_id: str, decision_kind: str) -> str:
    if type(source_event_id) is not str or source_event_id.strip() == "":
        raise ValueError("source_event_id required")
    if type(decision_kind) is not str or decision_kind.strip() == "":
        raise ValueError("decision_kind required")
    return f"{source_event_id}::{decision_kind}"


def seal_idempotency_record(
    *,
    source_event_id: str,
    decision_kind: str,
    produced_record_id: str,
    created_at: datetime,
) -> IdempotencyRecord:
    if type(created_at) is not datetime or created_at.tzinfo is not timezone.utc:
        raise ValueError("created_at must be UTC")
    key = make_idempotency_key(source_event_id, decision_kind)
    payload = {
        "idempotency_key": key,
        "source_event_id": source_event_id,
        "decision_kind": decision_kind,
        "produced_record_id": produced_record_id,
        "created_at": created_at,
    }
    return IdempotencyRecord(
        key,
        source_event_id,
        decision_kind,
        produced_record_id,
        created_at,
        integrity_seal(payload),
    )


class IdempotencyStore:
    """Durable-friendly in-process store; caller may persist records to journal."""

    def __init__(self) -> None:
        self._records: dict[str, IdempotencyRecord] = {}

    def lookup(self, source_event_id: str, decision_kind: str) -> IdempotencyRecord | None:
        return self._records.get(make_idempotency_key(source_event_id, decision_kind))

    def claim_or_hit(
        self,
        *,
        source_event_id: str,
        decision_kind: str,
        produced_record_id: str,
        created_at: datetime,
    ) -> tuple[str, IdempotencyRecord]:
        existing = self.lookup(source_event_id, decision_kind)
        if existing is not None:
            return IDEMPOTENCY_HIT, existing
        record = seal_idempotency_record(
            source_event_id=source_event_id,
            decision_kind=decision_kind,
            produced_record_id=produced_record_id,
            created_at=created_at,
        )
        self._records[record.idempotency_key] = record
        return IDEMPOTENCY_MISS, record

    def assert_not_duplicate(self, source_event_id: str, decision_kind: str) -> None:
        if self.lookup(source_event_id, decision_kind) is not None:
            raise ValueError(FAILURE_DUPLICATE_DECISION)

    def load(self, records: tuple[IdempotencyRecord, ...]) -> None:
        for record in records:
            self._records[record.idempotency_key] = record

    def all_records(self) -> tuple[IdempotencyRecord, ...]:
        return tuple(self._records[k] for k in sorted(self._records))
