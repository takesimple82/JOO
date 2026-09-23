import sqlite3, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
from InvestmentDecisionVerticalSlice.models import JournalAppend, JournalRecordKind
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal

NOW=datetime(2026,9,22,tzinfo=timezone.utc)

class JournalTests(unittest.TestCase):
    def test_atomic_append_restart_and_chain(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"d.sqlite"; j=DecisionJournal(p)
            records=j.append_batch((JournalAppend("a",JournalRecordKind.RESEARCH_EVIDENCE_BUNDLE,NOW,{"x":1}),JournalAppend("b",JournalRecordKind.SEMANTIC_PRODUCTION,NOW,{"x":2})))
            self.assertEqual(records[1].previous_seal,records[0].integrity_seal); j.close()
            reopened=DecisionJournal(p); self.assertEqual(len(reopened.list_records()),2); reopened.close()

    def test_update_delete_guards(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"d.sqlite"; j=DecisionJournal(p); j.append_batch((JournalAppend("a",JournalRecordKind.CIO_DECISION,NOW,{}),))
            c=sqlite3.connect(str(p))
            for sql in ("UPDATE decision_records SET payload_json='{}'","DELETE FROM decision_records"):
                with self.assertRaises(sqlite3.IntegrityError): c.execute(sql)
            c.close(); j.close()

    def test_integrity_corruption_and_guard_replacement_fail(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"d.sqlite"; j=DecisionJournal(p); j.append_batch((JournalAppend("a",JournalRecordKind.EXACT_EV_RESULT,NOW,{"x":1}),)); j.close()
            c=sqlite3.connect(str(p)); c.execute("DROP TRIGGER decision_records_no_update"); c.execute("CREATE TRIGGER decision_records_no_update BEFORE UPDATE ON decision_records BEGIN SELECT 1; END"); c.commit(); c.close()
            with self.assertRaisesRegex(ValueError,"mutation guards"): DecisionJournal(p)

    def test_duplicate_batch_rolls_back(self):
        with tempfile.TemporaryDirectory() as d:
            j=DecisionJournal(Path(d)/"d.sqlite")
            with self.assertRaises(ValueError): j.append_batch((JournalAppend("a",JournalRecordKind.CIO_DECISION,NOW,{}),JournalAppend("a",JournalRecordKind.CIO_DECISION,NOW,{})))
            self.assertEqual(j.list_records(),()); j.close()

if __name__ == "__main__": unittest.main()
