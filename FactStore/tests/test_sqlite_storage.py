from __future__ import annotations

import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from FactStore.sqlite_storage import SQLiteAppendOnlyFactEngine
from FactStore.sqlite_storage import _SCHEMA
from FactStore.store import FactStore
from FactStore.tests.builders import (
    make_broker_envelope,
    make_broker_request,
)


UTC = timezone.utc


def clock():
    return datetime(2026, 9, 22, 1, 0, tzinfo=UTC)


class SQLiteStorageTests(unittest.TestCase):
    def test_restart_replay_and_supersession(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "facts.sqlite3"
            engine = SQLiteAppendOnlyFactEngine(path)
            store = FactStore(clock, engine)
            first = store.append(make_broker_request())
            second = store.append(
                make_broker_request(
                    fact_id="broker-fact-002",
                    envelope=make_broker_envelope(
                        envelope_id="broker-envelope-002"
                    ),
                    superseded_fact_id=first.fact_id,
                )
            )
            engine.close()
            reopened_engine = SQLiteAppendOnlyFactEngine(path)
            reopened = FactStore(clock, reopened_engine)
            self.assertEqual(
                reopened.get_by_fact_id(first.fact_id), first
            )
            self.assertEqual(
                reopened.get_successor(first.fact_id), second
            )
            self.assertEqual(
                reopened.get_predecessor(second.fact_id), first
            )
            self.assertIsNone(reopened.verify_integrity(second.fact_id))
            reopened_engine.close()

    def test_batch_is_atomic_on_duplicate(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "facts.sqlite3"
            engine = SQLiteAppendOnlyFactEngine(path)
            store = FactStore(clock, engine)
            first = make_broker_request(
                fact_id="one",
                envelope=make_broker_envelope(envelope_id="env-one"),
            )
            duplicate = make_broker_request(
                fact_id="two",
                envelope=make_broker_envelope(envelope_id="env-one"),
            )
            with self.assertRaisesRegex(
                ValueError, "^envelope_id already accepted$"
            ):
                store.append_batch((first, duplicate))
            self.assertEqual(store.list_by_source_class("broker_fact"), ())
            engine.close()

    def test_update_and_delete_are_database_guarded(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "facts.sqlite3"
            engine = SQLiteAppendOnlyFactEngine(path)
            store = FactStore(clock, engine)
            store.append(make_broker_request())
            connection = sqlite3.connect(str(path))
            for statement in (
                "UPDATE fact_records SET status='failure'",
                "DELETE FROM fact_records",
            ):
                with self.subTest(statement=statement):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(statement)
            connection.close()
            engine.close()

    def test_corruption_fails_closed_on_restart(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "facts.sqlite3"
            engine = SQLiteAppendOnlyFactEngine(path)
            FactStore(clock, engine).append(make_broker_request())
            engine.close()
            connection = sqlite3.connect(str(path))
            connection.execute("DROP TRIGGER fact_records_no_update")
            connection.execute(
                "UPDATE fact_records SET payload_json='{}'"
            )
            connection.commit()
            connection.close()
            with self.assertRaisesRegex(
                ValueError,
                "^durable fact record integrity verification failed$",
            ):
                SQLiteAppendOnlyFactEngine(path)

    def test_schema_guard_removal_fails_closed_while_open(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "facts.sqlite3"
            engine = SQLiteAppendOnlyFactEngine(path)
            connection = sqlite3.connect(str(path))
            connection.execute("DROP TRIGGER fact_records_no_delete")
            connection.commit()
            connection.close()
            with self.assertRaisesRegex(
                ValueError, "^durable append-only guards mismatch$"
            ):
                engine.list_in_append_order()
            engine.close()

    def test_same_name_altered_guards_fail_on_restart(self):
        for trigger_name, event in (
            ("fact_records_no_update", "UPDATE"),
            ("fact_records_no_delete", "DELETE"),
        ):
            with self.subTest(trigger_name=trigger_name):
                with tempfile.TemporaryDirectory() as temporary:
                    path = Path(temporary) / "facts.sqlite3"
                    engine = SQLiteAppendOnlyFactEngine(path)
                    engine.close()
                    connection = sqlite3.connect(str(path))
                    connection.execute(f"DROP TRIGGER {trigger_name}")
                    connection.execute(
                        f"""
                        CREATE TRIGGER {trigger_name}
                        BEFORE {event} ON fact_records
                        BEGIN
                            SELECT 1;
                        END
                        """
                    )
                    connection.commit()
                    connection.close()
                    with self.assertRaisesRegex(
                        ValueError,
                        "^durable append-only guards mismatch$",
                    ):
                        SQLiteAppendOnlyFactEngine(path)

    def test_altered_declared_column_type_fails_on_restart(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "facts.sqlite3"
            connection = sqlite3.connect(str(path))
            connection.executescript(
                _SCHEMA.replace(
                    "fact_id TEXT NOT NULL UNIQUE",
                    "fact_id BLOB NOT NULL UNIQUE",
                    1,
                )
            )
            connection.close()
            with self.assertRaisesRegex(
                ValueError,
                "^durable fact table schema mismatch$",
            ):
                SQLiteAppendOnlyFactEngine(path)


if __name__ == "__main__":
    unittest.main()
