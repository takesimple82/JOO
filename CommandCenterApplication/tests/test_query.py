from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from CommandCenterApplication.fixture import FIXTURE_NOW, build_fixture_dataset
from CommandCenterApplication.query import load_real_read_only_dataset
from FactStore.sqlite_storage import SQLiteAppendOnlyFactEngine
from InvestmentDecisionVerticalSlice.models import JournalRecordKind
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal
from ProductionIntegration.journal import ProductionJournal


class RealReadOnlyQueryTests(unittest.TestCase):
    def test_existing_stores_are_verified_and_not_modified(self):
        fixture = build_fixture_dataset()
        with tempfile.TemporaryDirectory() as directory:
            facts_path = Path(directory) / "facts.sqlite3"
            journal_path = Path(directory) / "journal.sqlite3"
            facts = SQLiteAppendOnlyFactEngine(facts_path)
            facts.append_batch(fixture.facts)
            facts.close()
            journal = DecisionJournal(journal_path)
            production = ProductionJournal(journal)
            for row in fixture.artifacts:
                production.append_artifact(
                    kind=JournalRecordKind(row.kind),
                    record_id=row.record_id,
                    artifact=row.artifact,
                    created_at=row.created_at,
                    source_event_id=row.record_id,
                )
            journal.close()
            before = (facts_path.read_bytes(), journal_path.read_bytes())
            dataset = load_real_read_only_dataset(
                fact_store_path=facts_path,
                journal_path=journal_path,
                now=FIXTURE_NOW,
            )
            after = (facts_path.read_bytes(), journal_path.read_bytes())
        self.assertEqual(before, after)
        self.assertEqual(dataset.mode, "REAL_READ_ONLY")
        self.assertEqual(len(dataset.facts), len(fixture.facts))
        self.assertEqual(dataset.journal_record_count, len(fixture.artifacts))

    def test_nonexistent_store_fails_closed_without_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.sqlite3"
            with self.assertRaisesRegex(ValueError, "must already exist"):
                load_real_read_only_dataset(
                    fact_store_path=missing,
                    journal_path=missing,
                    now=FIXTURE_NOW,
                )
            self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
