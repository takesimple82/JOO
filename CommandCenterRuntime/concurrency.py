from __future__ import annotations

from datetime import datetime, timezone

from CommandCenterRuntime.integrity import integrity_seal
from CommandCenterRuntime.models import CycleOwnershipLease
from CommandCenterRuntime.vocabularies import (
    FAILURE_EXCLUSIVE_OWNERSHIP_UNPROVABLE,
    FAILURE_OVERLAPPING_CYCLE,
    OWNERSHIP_DENIED,
    OWNERSHIP_HELD,
    OWNERSHIP_UNPROVABLE,
)


def seal_ownership_lease(
    *,
    lease_id: str,
    source_event_id: str,
    holder_id: str,
    status: str,
    acquired_at: datetime,
) -> CycleOwnershipLease:
    if type(acquired_at) is not datetime or acquired_at.tzinfo is not timezone.utc:
        raise ValueError("acquired_at must be UTC")
    if status not in {OWNERSHIP_HELD, OWNERSHIP_DENIED, OWNERSHIP_UNPROVABLE}:
        raise ValueError("invalid ownership status")
    payload = {
        "lease_id": lease_id,
        "source_event_id": source_event_id,
        "holder_id": holder_id,
        "status": status,
        "acquired_at": acquired_at,
    }
    return CycleOwnershipLease(
        lease_id,
        source_event_id,
        holder_id,
        status,
        acquired_at,
        integrity_seal(payload),
    )


class ExclusiveCycleLock:
    """Fail closed if exclusive ownership for same-event cycle is unprovable."""

    def __init__(self) -> None:
        self._held: dict[str, CycleOwnershipLease] = {}

    def try_acquire(
        self,
        *,
        lease_id: str,
        source_event_id: str,
        holder_id: str,
        acquired_at: datetime,
        ownership_provable: bool = True,
    ) -> CycleOwnershipLease:
        if not ownership_provable:
            raise RuntimeError(FAILURE_EXCLUSIVE_OWNERSHIP_UNPROVABLE)
        existing = self._held.get(source_event_id)
        if existing is not None and existing.status == OWNERSHIP_HELD:
            if existing.holder_id != holder_id:
                raise RuntimeError(FAILURE_OVERLAPPING_CYCLE)
            return existing
        lease = seal_ownership_lease(
            lease_id=lease_id,
            source_event_id=source_event_id,
            holder_id=holder_id,
            status=OWNERSHIP_HELD,
            acquired_at=acquired_at,
        )
        self._held[source_event_id] = lease
        return lease

    def release(self, source_event_id: str, holder_id: str) -> None:
        existing = self._held.get(source_event_id)
        if existing is None:
            return
        if existing.holder_id != holder_id:
            raise RuntimeError(FAILURE_OVERLAPPING_CYCLE)
        del self._held[source_event_id]

    def held_for(self, source_event_id: str) -> CycleOwnershipLease | None:
        return self._held.get(source_event_id)
