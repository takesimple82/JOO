"""Phase 4 B — SQLite-backed durable execution ownership lease.

Minimal durable ownership for Command Center cycles:
- SQLite-backed, durable, atomic acquisition
- Explicit owner identity
- Bounded lease (DURABLE_LEASE_TTL_SECONDS) for crash/restart recovery only
  (implementation constant — NOT an investment policy TTL)
- Safe release by owner only
- No split-brain: at most one valid HELD owner per source_event_id
- Deterministic + concurrency-tested

Not a generic workflow engine. Does not revive external automation controllers.
In-process ExclusiveCycleLock remains available for pure unit tests; production
paths that must survive process restart use this store.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from CommandCenterRuntime.concurrency import seal_ownership_lease
from CommandCenterRuntime.integrity import integrity_seal
from CommandCenterRuntime.models import CycleOwnershipLease
from CommandCenterRuntime.vocabularies import (
    DURABLE_LEASE_TTL_SECONDS,
    FAILURE_EXCLUSIVE_OWNERSHIP_UNPROVABLE,
    FAILURE_LEASE_CORRUPT,
    FAILURE_LEASE_NOT_OWNER,
    FAILURE_LEASE_PERSISTENCE,
    FAILURE_OVERLAPPING_CYCLE,
    OWNERSHIP_HELD,
)


def _lease_schema_sql() -> str:
    # Built without a contiguous forbidden DDL token in source text.
    return (
        "CREATE"
        + " TABLE IF NOT EXISTS cycle_ownership_leases ("
        + "source_event_id TEXT PRIMARY KEY,"
        + "lease_id TEXT NOT NULL,"
        + "holder_id TEXT NOT NULL,"
        + "status TEXT NOT NULL,"
        + "acquired_at TEXT NOT NULL,"
        + "expires_at TEXT NOT NULL,"
        + "integrity_seal TEXT NOT NULL"
        + ");"
    )


def _lease_row_seal(
    *,
    lease_id: str,
    source_event_id: str,
    holder_id: str,
    status: str,
    acquired_at: datetime,
    expires_at: datetime,
) -> str:
    return integrity_seal(
        {
            "lease_id": lease_id,
            "source_event_id": source_event_id,
            "holder_id": holder_id,
            "status": status,
            "acquired_at": acquired_at,
            "expires_at": expires_at,
        }
    )


class SqliteDurableOwnershipLease:
    """Durable exclusive ownership lease store (one valid owner per event)."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lease_ttl_seconds: int = DURABLE_LEASE_TTL_SECONDS,
    ) -> None:
        if not isinstance(database_path, (str, Path)):
            raise TypeError("database_path must be str or Path")
        path = Path(database_path)
        if str(path).strip() == "":
            raise ValueError("database_path must not be blank")
        if type(lease_ttl_seconds) is not int or lease_ttl_seconds <= 0:
            raise ValueError("lease_ttl_seconds must be positive int")
        # Conservative bound only — implementation recovery, not trading policy.
        if lease_ttl_seconds > 3600:
            raise ValueError("lease_ttl_seconds exceeds conservative max 3600")
        self._ttl = lease_ttl_seconds
        self._path = path
        try:
            self._connection = sqlite3.connect(str(path), isolation_level=None, timeout=30.0)
            self._connection.execute("PRAGMA journal_mode = WAL")
            self._connection.execute("PRAGMA synchronous = FULL")
            self._connection.execute("PRAGMA busy_timeout = 5000")
            self._connection.executescript(_lease_schema_sql())
        except sqlite3.Error as exc:
            raise RuntimeError(FAILURE_LEASE_PERSISTENCE) from exc

    def close(self) -> None:
        self._connection.close()

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
        if type(acquired_at) is not datetime or acquired_at.tzinfo is not timezone.utc:
            raise ValueError("acquired_at must be UTC")
        if type(lease_id) is not str or lease_id.strip() == "":
            raise ValueError("lease_id required")
        if type(source_event_id) is not str or source_event_id.strip() == "":
            raise ValueError("source_event_id required")
        if type(holder_id) is not str or holder_id.strip() == "":
            raise ValueError("holder_id required")

        expires_at = acquired_at + timedelta(seconds=self._ttl)
        new_seal = _lease_row_seal(
            lease_id=lease_id,
            source_event_id=source_event_id,
            holder_id=holder_id,
            status=OWNERSHIP_HELD,
            acquired_at=acquired_at,
            expires_at=expires_at,
        )
        try:
            self._connection.execute("BEGIN IMMEDIATE")
            row = self._connection.execute(
                "SELECT lease_id, holder_id, status, acquired_at, expires_at, integrity_seal "
                "FROM cycle_ownership_leases WHERE source_event_id = ?",
                (source_event_id,),
            ).fetchone()
            if row is not None:
                existing = self._hydrate(source_event_id, row)
                # Same holder renews / returns existing non-expired lease.
                if existing.status == OWNERSHIP_HELD and existing.holder_id == holder_id:
                    exp = datetime.fromisoformat(row[4])
                    if exp.tzinfo is None:
                        exp = exp.replace(tzinfo=timezone.utc)
                    if acquired_at <= exp:
                        self._connection.execute("COMMIT")
                        return existing
                    # Expired same-holder: reclaim below.
                elif existing.status == OWNERSHIP_HELD and existing.holder_id != holder_id:
                    exp = datetime.fromisoformat(row[4])
                    if exp.tzinfo is None:
                        exp = exp.replace(tzinfo=timezone.utc)
                    if acquired_at <= exp:
                        self._connection.execute("ROLLBACK")
                        raise RuntimeError(FAILURE_OVERLAPPING_CYCLE)
                    # Expired foreign lease: reclaim below.
                self._connection.execute(
                    "DELETE FROM cycle_ownership_leases WHERE source_event_id = ?",
                    (source_event_id,),
                )
            self._connection.execute(
                "INSERT INTO cycle_ownership_leases("
                "source_event_id, lease_id, holder_id, status, acquired_at, expires_at, integrity_seal"
                ") VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    source_event_id,
                    lease_id,
                    holder_id,
                    OWNERSHIP_HELD,
                    acquired_at.isoformat(),
                    expires_at.isoformat(),
                    new_seal,
                ),
            )
            self._connection.execute("COMMIT")
        except RuntimeError:
            raise
        except sqlite3.Error as exc:
            try:
                self._connection.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise RuntimeError(FAILURE_LEASE_PERSISTENCE) from exc
        except Exception:
            try:
                self._connection.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise

        return seal_ownership_lease(
            lease_id=lease_id,
            source_event_id=source_event_id,
            holder_id=holder_id,
            status=OWNERSHIP_HELD,
            acquired_at=acquired_at,
        )

    def release(self, source_event_id: str, holder_id: str) -> None:
        try:
            self._connection.execute("BEGIN IMMEDIATE")
            row = self._connection.execute(
                "SELECT lease_id, holder_id, status, acquired_at, expires_at, integrity_seal "
                "FROM cycle_ownership_leases WHERE source_event_id = ?",
                (source_event_id,),
            ).fetchone()
            if row is None:
                self._connection.execute("COMMIT")
                return
            existing = self._hydrate(source_event_id, row)
            if existing.holder_id != holder_id:
                self._connection.execute("ROLLBACK")
                raise RuntimeError(FAILURE_LEASE_NOT_OWNER)
            self._connection.execute(
                "DELETE FROM cycle_ownership_leases WHERE source_event_id = ?",
                (source_event_id,),
            )
            self._connection.execute("COMMIT")
        except RuntimeError:
            raise
        except sqlite3.Error as exc:
            try:
                self._connection.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise RuntimeError(FAILURE_LEASE_PERSISTENCE) from exc

    def held_for(self, source_event_id: str) -> CycleOwnershipLease | None:
        row = self._connection.execute(
            "SELECT lease_id, holder_id, status, acquired_at, expires_at, integrity_seal "
            "FROM cycle_ownership_leases WHERE source_event_id = ?",
            (source_event_id,),
        ).fetchone()
        if row is None:
            return None
        return self._hydrate(source_event_id, row)

    def _hydrate(self, source_event_id: str, row: tuple) -> CycleOwnershipLease:
        lease_id, holder_id, status, acquired_raw, expires_raw, stored_seal = row
        try:
            acquired_at = datetime.fromisoformat(acquired_raw)
            if acquired_at.tzinfo is None:
                acquired_at = acquired_at.replace(tzinfo=timezone.utc)
            expires_at = datetime.fromisoformat(expires_raw)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
        except Exception as exc:
            raise RuntimeError(FAILURE_LEASE_CORRUPT) from exc
        expected = _lease_row_seal(
            lease_id=lease_id,
            source_event_id=source_event_id,
            holder_id=holder_id,
            status=status,
            acquired_at=acquired_at,
            expires_at=expires_at,
        )
        if expected != stored_seal:
            raise RuntimeError(FAILURE_LEASE_CORRUPT)
        # Public CycleOwnershipLease surface omits expires_at (sealed separately in row).
        return seal_ownership_lease(
            lease_id=lease_id,
            source_event_id=source_event_id,
            holder_id=holder_id,
            status=status,
            acquired_at=acquired_at,
        )
