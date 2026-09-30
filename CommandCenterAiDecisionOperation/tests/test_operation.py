from __future__ import annotations

import os
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from CommandCenterAiDecisionOperation.models import AiCioDecisionAttempt
from CommandCenterAiDecisionOperation.service import record_research_unavailable_attempt
from CommandCenterApplication.fixture import build_fixture_dataset
from CommandCenterApplication.presentation import public_json
from CommandCenterApplication.projection import build_command_center_view
from CommandCenterApplication.query import load_real_read_only_dataset
from CommandCenterReadOnlyOperation.service import run_real_read_only_observation
from CommandCenterReadOnlyOperation.tests.test_operation import NOW, FakeReadAdapter, binding, config
from InvestmentDecisionVerticalSlice.models import JournalRecordKind
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal
from ProductionIntegration.journal import ProductionJournal


class AiDecisionOperationTests(unittest.TestCase):
    def stores(self, directory):
        facts = Path(directory) / "facts.sqlite3"
        journal = Path(directory) / "journal.sqlite3"
        result = run_real_read_only_observation(
            adapter=FakeReadAdapter(NOW), binding=binding(), config=config(),
            fact_store_path=facts, journal_path=journal,
            observation_id="observation-real", now=NOW,
        )
        return facts, journal, result.observation

    def test_real_unavailable_attempt_is_evidence_bound_and_non_authorizing(self):
        with tempfile.TemporaryDirectory() as directory:
            facts, journal, observation = self.stores(directory)
            attempt = record_research_unavailable_attempt(
                fact_store_path=facts, journal_path=journal,
                attempt_id="attempt-real", now=NOW + timedelta(minutes=1),
            )
            view = build_command_center_view(load_real_read_only_dataset(
                fact_store_path=facts, journal_path=journal,
                now=NOW + timedelta(minutes=1),
            ))
        self.assertEqual(attempt.evidence_package.observation_id, observation.observation_id)
        self.assertEqual(attempt.evidence_package.fact_ids, observation.application_fact_ids)
        self.assertEqual(attempt.evidence_package.raw_fact_ids, observation.raw_fact_ids)
        self.assertEqual(attempt.evidence_package.truth_class, "broker_fact")
        self.assertEqual(view.ai_pipeline.research_state, "RESEARCH_UNAVAILABLE")
        self.assertEqual(view.ai_pipeline.committee_state, "COMMITTEE_UNAVAILABLE")
        self.assertEqual(view.cio.state, "BLOCKED")
        self.assertEqual(view.expected_values, ())
        self.assertEqual(view.allocation.state, "UNAVAILABLE")
        self.assertEqual(view.investment_approval.state, "NOT_ISSUED")
        self.assertFalse(view.execution.live_enabled)
        self.assertFalse(attempt.executable)
        self.assertFalse(attempt.broker_mutation_enabled)

    def test_restart_reconstructs_exact_attempt_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            facts, journal, _observation = self.stores(directory)
            first = record_research_unavailable_attempt(
                fact_store_path=facts, journal_path=journal,
                attempt_id="attempt-restart", now=NOW + timedelta(minutes=1),
            )
            second = record_research_unavailable_attempt(
                fact_store_path=facts, journal_path=journal,
                attempt_id="attempt-restart", now=NOW + timedelta(minutes=1),
            )
            dataset = load_real_read_only_dataset(
                fact_store_path=facts, journal_path=journal,
                now=NOW + timedelta(minutes=1),
            )
        attempts = tuple(
            row.artifact for row in dataset.artifacts
            if type(row.artifact) is AiCioDecisionAttempt
        )
        self.assertEqual(first, second)
        self.assertEqual(attempts, (first,))

    def test_stale_facts_block_before_research(self):
        with tempfile.TemporaryDirectory() as directory:
            facts, journal, _observation = self.stores(directory)
            attempt = record_research_unavailable_attempt(
                fact_store_path=facts, journal_path=journal,
                attempt_id="attempt-stale", now=NOW + timedelta(minutes=6),
            )
        self.assertEqual(attempt.blocker_codes, ("FACTUAL_OBSERVATION_STALE",))
        self.assertEqual(attempt.cio_state, "BLOCKED")
        self.assertEqual(attempt.ev_state, "UNAVAILABLE")
        self.assertEqual(attempt.allocation_state, "UNAVAILABLE")

    def test_no_observation_fails_without_fabricating_attempt(self):
        from FactStore.sqlite_storage import SQLiteAppendOnlyFactEngine

        with tempfile.TemporaryDirectory() as directory:
            facts = Path(directory) / "facts.sqlite3"
            journal = Path(directory) / "journal.sqlite3"
            SQLiteAppendOnlyFactEngine(facts).close()
            DecisionJournal(journal).close()
            with self.assertRaisesRegex(ValueError, "factual observation"):
                record_research_unavailable_attempt(
                    fact_store_path=facts, journal_path=journal,
                    attempt_id="attempt-none", now=NOW,
                )
            decision = DecisionJournal(journal)
            self.assertEqual(decision.list_records(), ())
            decision.close()

    def test_configured_provider_cannot_be_downgraded_to_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            facts, journal, _observation = self.stores(directory)
            before = Path(journal).read_bytes()
            with patch.dict(os.environ, {
                "XAI_API_KEY": "test-secret-never-persisted",
                "XAI_MODEL": "configured-model",
            }, clear=False):
                with self.assertRaisesRegex(ValueError, "OperationalCioCycle"):
                    record_research_unavailable_attempt(
                        fact_store_path=facts, journal_path=journal,
                        attempt_id="attempt-provider", now=NOW,
                    )
            self.assertEqual(Path(journal).read_bytes(), before)

    def test_wrong_observation_cio_cannot_appear_current(self):
        with tempfile.TemporaryDirectory() as directory:
            facts, journal_path, _observation = self.stores(directory)
            fixture_decision = next(
                row.artifact for row in build_fixture_dataset().artifacts
                if row.kind == JournalRecordKind.CIO_DECISION.value
            )
            journal = DecisionJournal(journal_path)
            ProductionJournal(journal).append_artifact(
                JournalRecordKind.CIO_DECISION, "foreign-observation-cio",
                fixture_decision, NOW + timedelta(seconds=1), "foreign-observation",
            )
            journal.close()
            view = build_command_center_view(load_real_read_only_dataset(
                fact_store_path=facts, journal_path=journal_path,
                now=NOW + timedelta(seconds=1),
            ))
        self.assertEqual(view.cio.state, "UNAVAILABLE")
        self.assertEqual(view.expected_values, ())
        self.assertEqual(view.allocation.state, "UNAVAILABLE")

    def test_public_json_redacts_account_and_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            facts, journal, _observation = self.stores(directory)
            record_research_unavailable_attempt(
                fact_store_path=facts, journal_path=journal,
                attempt_id="attempt-redaction", now=NOW + timedelta(minutes=1),
            )
            payload = public_json(build_command_center_view(
                load_real_read_only_dataset(
                    fact_store_path=facts, journal_path=journal,
                    now=NOW + timedelta(minutes=1),
                )
            ))
        self.assertNotIn(b"kb-primary-readonly", payload)
        for marker in (b"api_key", b"appSecret", b"Authorization", b"Bearer"):
            self.assertNotIn(marker, payload)


if __name__ == "__main__":
    unittest.main()
