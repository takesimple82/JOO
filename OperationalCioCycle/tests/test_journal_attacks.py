import copy
import sqlite3
import tempfile
import threading
import unittest
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from InvestmentDecisionVerticalSlice.models import JournalAppend, JournalRecordKind
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal, UPDATE_TRIGGER_SQL
from OperationalCioCycle.service import replay_cycle
from OperationalCioCycle.codec import decode, encode
from OperationalCioCycle.tests.helpers import Fixture, NOW


class JournalAttacks(unittest.TestCase):
    def test_concurrent_writers_bind_tail_inside_write_transaction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.sqlite3"
            journal = DecisionJournal(path)
            journal.close()
            barrier = threading.Barrier(2)
            def write(prefix):
                j = DecisionJournal(path)
                try:
                    j._connection.set_trace_callback(lambda sql: barrier.wait(timeout=3) if sql == "BEGIN IMMEDIATE" else None)
                    return j.append_batch((JournalAppend(prefix, JournalRecordKind.CIO_DECISION, NOW, {"id": prefix}),))
                finally:
                    j.close()
            with ThreadPoolExecutor(max_workers=2) as pool:
                jobs = [pool.submit(write, x) for x in ("a", "b")]
                self.assertTrue(all(len(job.result(timeout=10)) == 1 for job in jobs))
            j = DecisionJournal(path)
            self.assertEqual(len(j.list_records()), 2)
            j.close()

    def test_sql_failure_after_first_insert_rolls_back_whole_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            j = DecisionJournal(Path(tmp) / "journal.sqlite3")
            original = j._connection
            class FailSecondInsert:
                count = 0
                def execute(self, sql, *args):
                    if sql.startswith("INSERT"):
                        self.count += 1
                        if self.count == 2:
                            raise sqlite3.OperationalError("disk failure")
                    return original.execute(sql, *args)
                @property
                def in_transaction(self):
                    return original.in_transaction
            j._connection = FailSecondInsert()
            with self.assertRaises(sqlite3.OperationalError):
                j.append_batch(tuple(JournalAppend(x, JournalRecordKind.CIO_DECISION, NOW, {}) for x in ("a", "b")))
            j._connection = original
            self.assertEqual(j.list_records(), ())
            self.assertFalse(original.in_transaction)
            j.close()

    def test_replay_rejects_sealed_but_semantically_forged_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(tmp)
            try:
                f.run()
                payload = copy.deepcopy(f.journal.list_records()[0].payload)
                payload["result"]["fields"]["decisions"]["tuple"][0]["fields"]["executable"] = True
                other = DecisionJournal(Path(tmp) / "forged.sqlite3")
                inputs = list(decode(payload["inputs"]))
                inputs[0] = replace(inputs[0], journal_id=other.journal_identity)
                payload["inputs"] = encode(tuple(inputs))
                other.append_batch((JournalAppend("cycle:completed", JournalRecordKind.OPERATIONAL_CIO_CYCLE, NOW, payload),))
                with self.assertRaisesRegex(ValueError, "replay mismatch"):
                    replay_cycle(other, "cycle", other.journal_identity)
                other.close()
            finally:
                f.close()

    def test_corruption_detected_after_original_guards_restored(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Fixture(tmp)
            try:
                f.run()
                connection = sqlite3.connect(str(Path(tmp) / "decisions.sqlite3"))
                connection.execute("DROP TRIGGER decision_records_no_update")
                connection.execute("UPDATE decision_records SET payload_json='{}'")
                connection.execute(UPDATE_TRIGGER_SQL)
                connection.commit()
                connection.close()
                with self.assertRaisesRegex(ValueError, "integrity chain"):
                    replay_cycle(f.journal, "cycle", f.config.journal_id)
            finally:
                f.close()
