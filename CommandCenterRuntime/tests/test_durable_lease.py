from __future__ import annotations

import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from CommandCenterRuntime.durable_lease import SqliteDurableOwnershipLease
from CommandCenterRuntime.vocabularies import (
    DURABLE_LEASE_TTL_SECONDS,
    FAILURE_LEASE_CORRUPT,
    FAILURE_LEASE_NOT_OWNER,
    FAILURE_OVERLAPPING_CYCLE,
    OWNERSHIP_HELD,
)


NOW = datetime(2026, 6, 23, 10, 0, 0, tzinfo=timezone.utc)


class DurableLeaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "leases.sqlite3"
        self.store = SqliteDurableOwnershipLease(self.path, lease_ttl_seconds=60)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_ttl_constant_is_implementation_bound(self):
        self.assertEqual(DURABLE_LEASE_TTL_SECONDS, 300)
        self.assertLessEqual(DURABLE_LEASE_TTL_SECONDS, 3600)

    def test_single_owner_acquire_release(self):
        lease = self.store.try_acquire(
            lease_id="l1", source_event_id="e1", holder_id="h1", acquired_at=NOW,
        )
        self.assertEqual(lease.status, OWNERSHIP_HELD)
        self.assertEqual(self.store.held_for("e1").holder_id, "h1")
        self.store.release("e1", "h1")
        self.assertIsNone(self.store.held_for("e1"))

    def test_two_holders_simultaneous_only_one_wins(self):
        barrier = threading.Barrier(2)
        outcomes = []
        lock = threading.Lock()

        def worker(holder):
            store = SqliteDurableOwnershipLease(self.path, lease_ttl_seconds=60)
            barrier.wait(timeout=5)
            try:
                store.try_acquire(
                    lease_id=f"l-{holder}",
                    source_event_id="same-event",
                    holder_id=holder,
                    acquired_at=NOW,
                )
                result = "acquired"
            except RuntimeError as exc:
                result = f"blocked:{exc}"
            finally:
                store.close()
            with lock:
                outcomes.append(result)

        threads = [threading.Thread(target=worker, args=(h,)) for h in ("h1", "h2")]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)
        self.assertEqual(outcomes.count("acquired"), 1)
        self.assertEqual(sum(1 for o in outcomes if o.startswith("blocked:")), 1)

    def test_non_owner_release_rejected(self):
        self.store.try_acquire(
            lease_id="l1", source_event_id="e1", holder_id="h1", acquired_at=NOW,
        )
        with self.assertRaisesRegex(RuntimeError, FAILURE_LEASE_NOT_OWNER):
            self.store.release("e1", "h2")

    def test_expired_lease_recoverable_by_new_owner(self):
        self.store.try_acquire(
            lease_id="l1", source_event_id="e1", holder_id="h1", acquired_at=NOW,
        )
        later = NOW + timedelta(seconds=120)
        lease = self.store.try_acquire(
            lease_id="l2", source_event_id="e1", holder_id="h2", acquired_at=later,
        )
        self.assertEqual(lease.holder_id, "h2")

    def test_restart_sees_persisted_lease(self):
        self.store.try_acquire(
            lease_id="l1", source_event_id="e1", holder_id="h1", acquired_at=NOW,
        )
        self.store.close()
        reopened = SqliteDurableOwnershipLease(self.path, lease_ttl_seconds=60)
        held = reopened.held_for("e1")
        self.assertIsNotNone(held)
        self.assertEqual(held.holder_id, "h1")
        with self.assertRaisesRegex(RuntimeError, FAILURE_OVERLAPPING_CYCLE):
            reopened.try_acquire(
                lease_id="l2", source_event_id="e1", holder_id="h2", acquired_at=NOW,
            )
        reopened.close()
        self.store = SqliteDurableOwnershipLease(self.path, lease_ttl_seconds=60)

    def test_corrupted_lease_fail_closed(self):
        self.store.try_acquire(
            lease_id="l1", source_event_id="e1", holder_id="h1", acquired_at=NOW,
        )
        import sqlite3
        conn = sqlite3.connect(str(self.path))
        conn.execute(
            "UPDATE cycle_ownership_leases SET integrity_seal = ? WHERE source_event_id = ?",
            ("deadbeef", "e1"),
        )
        conn.commit()
        conn.close()
        with self.assertRaisesRegex(RuntimeError, FAILURE_LEASE_CORRUPT):
            self.store.held_for("e1")


if __name__ == "__main__":
    unittest.main()
