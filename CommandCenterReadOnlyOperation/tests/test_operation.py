from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from CommandCenterApplication.projection import build_command_center_view
from CommandCenterApplication.presentation import public_json
from CommandCenterApplication.query import load_real_read_only_dataset
from CommandCenterReadOnlyOperation.configuration import (
    load_read_only_operation_config,
)
from CommandCenterReadOnlyOperation.http import kb_read_only_http_post
from CommandCenterReadOnlyOperation.models import (
    DomesticPositionBinding,
    ReadOnlyOperationConfig,
)
from CommandCenterReadOnlyOperation.service import (
    run_real_read_only_observation,
)
from ProviderGateway.models import (
    ExplicitBrokerAdapterBinding,
    ExplicitBrokerParameterProfile,
    ExplicitCollectOutcome,
    ExplicitProviderFailureSignal,
    ExplicitProviderPayloadEnvelope,
)


NOW = datetime(2026, 9, 30, 1, 0, tzinfo=timezone.utc)


def holdings_payload(*, currency="   ", foreign=False, quantity="10"):
    rows = [{
        "clsf": "현금", "crncy_cd": currency, "is_cd": "A005930",
        "hld_q": quantity, "now_prc": "999999999", "val_amt": "7100000",
    }]
    if foreign:
        rows.append({
            "clsf": "외화증권", "crncy_cd": "USD", "is_cd": "US0378331005",
            "hld_q": "2", "now_prc": "100", "val_amt": "200",
        })
    return {
        "dataHeader": {"processFlag": "A", "processCode": "0011"},
        "dataBody": {"nt_asts_val_amt": "9000000", "Record1": rows},
    }


def balances_payload():
    return {
        "dataHeader": {"processFlag": "A", "processCode": "0011"},
        "dataBody": {
            "ordr_psbl_csh": "339901", "ordr_psbl_amt": "999999999",
            "do_psbl_csh": "111", "tdy_tfnd_amt": "1",
            "ndy_tfnd": "2", "nxt2_dy_tfnd": "3",
        },
    }


class FakeReadAdapter:
    def __init__(
        self, now, *, holdings=None, balances=None, fail_kind=None,
        foreign=False, collected_at=None,
    ):
        self.now = now if collected_at is None else collected_at
        self.holdings = holdings or holdings_payload(foreign=foreign)
        self.balances = balances or balances_payload()
        self.fail_kind = fail_kind
        self.calls = []

    def collect(self, request):
        self.calls.append(request.request_kind)
        if request.request_kind == self.fail_kind:
            return ExplicitCollectOutcome(
                "failure", None,
                ExplicitProviderFailureSignal(
                    "kb_open_api", self.now, "AUTH_FAILURE", None,
                    request.request_correlation_id,
                ),
            )
        payload = self.holdings if request.request_kind == "holdings" else self.balances
        return ExplicitCollectOutcome(
            "success",
            ExplicitProviderPayloadEnvelope(
                request.envelope_id, "kb_open_api", "broker_fact", self.now,
                "success", payload, None, request.request_correlation_id,
            ),
            None,
        )


def config():
    return ReadOnlyOperationConfig(
        "kb-primary-readonly", "personal-portfolio", 300,
        (DomesticPositionBinding(
            "현금", "A005930", "position-samsung", "subject-samsung",
        ),),
    )


def binding():
    return ExplicitBrokerAdapterBinding(
        "kb_open_api", "kb_open_api",
        ExplicitBrokerParameterProfile(
            "readonly-profile", "kb-primary-readonly", ("holdings", "balances"),
        ),
    )


class RealReadOnlyOperationTests(unittest.TestCase):
    def execute(self, directory, suffix, now=NOW, **adapter_kwargs):
        adapter = FakeReadAdapter(now, **adapter_kwargs)
        result = run_real_read_only_observation(
            adapter=adapter, binding=binding(), config=config(),
            fact_store_path=Path(directory) / "facts.sqlite3",
            journal_path=Path(directory) / "journal.sqlite3",
            observation_id="observation-" + suffix, now=now,
        )
        return adapter, result

    def test_real_observation_reaches_read_only_application_with_authorities(self):
        with tempfile.TemporaryDirectory() as directory:
            adapter, result = self.execute(directory, "one", foreign=True)
            dataset = load_real_read_only_dataset(
                fact_store_path=Path(directory) / "facts.sqlite3",
                journal_path=Path(directory) / "journal.sqlite3", now=NOW,
            )
            view = build_command_center_view(dataset)
        self.assertEqual(adapter.calls, ["holdings", "balances"])
        self.assertEqual(result.observation.change_class, "BASELINE_ABSENT")
        self.assertEqual(view.mode, "REAL_READ_ONLY")
        self.assertEqual(view.positions[0].quantity, "10")
        self.assertEqual(view.positions[0].market_value_krw, "7100000")
        self.assertEqual(view.portfolio_value_krw, "7100000")
        self.assertEqual(view.capital.orderable_cash_krw, "339901")
        self.assertEqual(view.capital.broker_account_valuation_authority, "NOT_SIZING_AUTHORITY")
        self.assertEqual(len(view.foreign_exclusions), 1)
        self.assertEqual(view.change.classification, "BASELINE_ABSENT")
        self.assertEqual(view.cio.state, "UNAVAILABLE")
        self.assertEqual(view.expected_values, ())
        self.assertEqual(view.execution.state, "LIVE_BLOCKED")
        self.assertFalse(view.execution.live_enabled)
        self.assertEqual(view.system_health.decision_journal_state, "VERIFIED")
        payload = public_json(view)
        self.assertNotIn(b"kb-primary-readonly", payload)
        self.assertNotIn(b"appSecret", payload)

    def test_second_identical_observation_is_no_change_and_supersedes_facts(self):
        with tempfile.TemporaryDirectory() as directory:
            self.execute(directory, "one")
            _adapter, second = self.execute(
                directory, "two", now=NOW + timedelta(minutes=1)
            )
            dataset = load_real_read_only_dataset(
                fact_store_path=Path(directory) / "facts.sqlite3",
                journal_path=Path(directory) / "journal.sqlite3",
                now=NOW + timedelta(minutes=1),
            )
        self.assertEqual(second.observation.change_class, "NO_CHANGE")
        self.assertEqual(dataset.change_class, "NO_CHANGE")
        self.assertTrue(all(x.fact_id.startswith(("fact-position:observation-two", "fact:observation-two", "fact-position-value:observation-two")) for x in dataset.facts))

    def test_exact_observation_retry_is_durable_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            _adapter, first = self.execute(directory, "same")
            _adapter, second = self.execute(directory, "same")
        self.assertEqual(second.appended_fact_count, 0)
        self.assertEqual(second.observation, first.observation)

    def test_partially_published_facts_never_replace_valid_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            _adapter, first = self.execute(directory, "published")
            facts_path = Path(directory) / "facts.sqlite3"
            main_journal = Path(directory) / "journal.sqlite3"
            side_journal = Path(directory) / "interrupted-journal.sqlite3"
            run_real_read_only_observation(
                adapter=FakeReadAdapter(NOW + timedelta(minutes=1)),
                binding=binding(), config=config(), fact_store_path=facts_path,
                journal_path=side_journal,
                observation_id="observation-unpublished",
                now=NOW + timedelta(minutes=1),
            )
            dataset = load_real_read_only_dataset(
                fact_store_path=facts_path, journal_path=main_journal,
                now=NOW + timedelta(minutes=1),
            )
        self.assertEqual(dataset.active_observation_id, "observation-published")
        self.assertEqual(
            tuple(x.fact_id for x in dataset.facts),
            first.observation.application_fact_ids,
        )
        self.assertNotIn("observation-unpublished", repr(dataset.facts))

    def test_partially_published_facts_without_observation_remain_unavailable(self):
        from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal

        with tempfile.TemporaryDirectory() as directory:
            facts_path = Path(directory) / "facts.sqlite3"
            side_journal = Path(directory) / "interrupted-journal.sqlite3"
            empty_journal = Path(directory) / "journal.sqlite3"
            run_real_read_only_observation(
                adapter=FakeReadAdapter(NOW), binding=binding(), config=config(),
                fact_store_path=facts_path, journal_path=side_journal,
                observation_id="observation-unpublished", now=NOW,
            )
            DecisionJournal(empty_journal).close()
            dataset = load_real_read_only_dataset(
                fact_store_path=facts_path, journal_path=empty_journal, now=NOW,
            )
            view = build_command_center_view(dataset)
        self.assertIsNone(dataset.active_observation_id)
        self.assertEqual(dataset.facts, ())
        self.assertEqual(view.position_count, 0)
        self.assertIsNone(view.portfolio_value_krw)

    def test_latest_journal_sequence_wins_equal_or_skewed_timestamps(self):
        from InvestmentDecisionVerticalSlice.models import JournalRecordKind
        from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal
        from ProductionIntegration.journal import ProductionJournal

        for created_at in (NOW, NOW - timedelta(minutes=1)):
            with self.subTest(created_at=created_at), tempfile.TemporaryDirectory() as directory:
                _adapter, first = self.execute(directory, "first")
                journal_path = Path(directory) / "journal.sqlite3"
                journal = DecisionJournal(journal_path)
                later = replace(
                    first.observation,
                    observation_id="observation-later-sequence",
                    created_at=created_at,
                    change_class="NO_CHANGE",
                )
                ProductionJournal(journal).append_artifact(
                    JournalRecordKind.READ_ONLY_OBSERVATION,
                    later.observation_id,
                    later,
                    created_at,
                    later.observation_id,
                )
                journal.close()
                dataset = load_real_read_only_dataset(
                    fact_store_path=Path(directory) / "facts.sqlite3",
                    journal_path=journal_path,
                    now=NOW,
                )
            self.assertEqual(
                dataset.active_observation_id, "observation-later-sequence"
            )
            self.assertEqual(dataset.change_class, "NO_CHANGE")

    def test_blank_currency_requires_explicit_domestic_binding(self):
        bad_config = replace(config(), domestic_bindings=())
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "verified domestic binding required"):
                run_real_read_only_observation(
                    adapter=FakeReadAdapter(NOW), binding=binding(), config=bad_config,
                    fact_store_path=Path(directory) / "facts.sqlite3",
                    journal_path=Path(directory) / "journal.sqlite3",
                    observation_id="observation-bad", now=NOW,
                )
            self.assertFalse((Path(directory) / "facts.sqlite3").exists())

    def test_auth_failure_creates_no_false_store_state(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "AUTH_FAILURE"):
                self.execute(directory, "auth", fail_kind="holdings")
            self.assertFalse((Path(directory) / "facts.sqlite3").exists())
            self.assertFalse((Path(directory) / "journal.sqlite3").exists())

    def test_malformed_or_stale_data_fails_closed(self):
        malformed = {"dataHeader": {"processFlag": "A"}, "dataBody": {}}
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "Record1"):
                self.execute(directory, "malformed", holdings=malformed)
        with tempfile.TemporaryDirectory() as directory:
            old = NOW - timedelta(minutes=6)
            with self.assertRaisesRegex(ValueError, "PortfolioSnapshot"):
                self.execute(directory, "stale", collected_at=old)

    def test_missing_and_corrupt_application_stores_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.sqlite3"
            with self.assertRaisesRegex(ValueError, "must already exist"):
                load_real_read_only_dataset(
                    fact_store_path=missing, journal_path=missing, now=NOW,
                )
            facts = Path(directory) / "facts.sqlite3"
            journal = Path(directory) / "journal.sqlite3"
            facts.write_bytes(b"not sqlite")
            journal.write_bytes(b"not sqlite")
            with self.assertRaises(Exception):
                load_real_read_only_dataset(
                    fact_store_path=facts, journal_path=journal, now=NOW,
                )

    def test_empty_verified_stores_degrade_truthfully(self):
        from FactStore.sqlite_storage import SQLiteAppendOnlyFactEngine
        from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal

        with tempfile.TemporaryDirectory() as directory:
            facts = Path(directory) / "facts.sqlite3"
            journal = Path(directory) / "journal.sqlite3"
            SQLiteAppendOnlyFactEngine(facts).close()
            DecisionJournal(journal).close()
            view = build_command_center_view(load_real_read_only_dataset(
                fact_store_path=facts, journal_path=journal, now=NOW,
            ))
        self.assertEqual(view.position_count, 0)
        self.assertEqual(view.system_health.factual_freshness, "UNAVAILABLE")
        self.assertEqual(view.system_health.fact_store_state, "EMPTY")
        self.assertEqual(view.system_health.decision_journal_state, "VERIFIED_EMPTY")
        self.assertEqual(view.execution.state, "LIVE_BLOCKED")

    def test_foreign_only_observation_stays_outside_domestic_portfolio(self):
        foreign_only = holdings_payload(foreign=True)["dataBody"]["Record1"][1:]
        payload = holdings_payload()
        payload["dataBody"]["Record1"] = foreign_only
        with tempfile.TemporaryDirectory() as directory:
            _adapter, _result = self.execute(
                directory, "foreign-only", holdings=payload,
            )
            view = build_command_center_view(load_real_read_only_dataset(
                fact_store_path=Path(directory) / "facts.sqlite3",
                journal_path=Path(directory) / "journal.sqlite3", now=NOW,
            ))
        self.assertEqual(view.position_count, 0)
        self.assertEqual(len(view.foreign_exclusions), 1)
        self.assertIsNone(view.portfolio_value_krw)

    def test_http_boundary_rejects_every_mutation_and_public_path(self):
        for url in (
            "https://developer.kbsec.com:32484/api/v1/ssam1802",
            "https://developer.kbsec.com:32484/api/v1/ssam1805",
            "https://developer.kbsec.com:32484/api/v1/ssam1806",
            "http://developer.kbsec.com:32484/api/v1/ssqm2952",
            "https://example.com/api/v1/ssqm2952",
        ):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, "not allowed"):
                kb_read_only_http_post(url, {}, b"{}", 1)

    def test_config_rejects_secret_keys_and_full_account_identifiers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            payload = {
                "schema_version": 1, "account_selector": "12345678901",
                "portfolio_id": "personal", "freshness_max_age_seconds": 300,
                "domestic_bindings": [],
            }
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, "account identifier"):
                load_read_only_operation_config(path)
            payload["account_selector"] = "primary"
            payload["appSecret"] = "forbidden"
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, "schema mismatch"):
                load_read_only_operation_config(path)


if __name__ == "__main__":
    unittest.main()
