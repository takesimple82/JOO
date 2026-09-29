from __future__ import annotations

import tempfile
import threading
import unittest
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from BrokerExecutionCycle.mutation_transport import LiveMutationTransportDisabled, MockMutationTransport
from BrokerExecutionCycle.authorization import initial_mutation_authority
from BrokerExecutionCycle.mutation_gate import execute_mutation_attempt
from BrokerExecutionCycle.translation import translate_order_intent_to_ssam
from BrokerExecutionCycle.service import authorize_trade_execution, run_pretrade_validation, seal_order_intent_from_approval_chain
from BrokerExecutionCycle.tests.helpers import NOW as BROKER_NOW, make_pretrade_bundle, sealed_chain, verified_account, verified_account_allowlist, fresh_cash_fact
from CommandCenterRuntime.integrity import integrity_seal as command_center_seal
from CommandCenterRuntime.models import DetectedChange, PortfolioQuantityFact, ProviderFailureFact
from CommandCenterRuntime.service import CommandCenterCycleRequest
from CommandCenterRuntime.vocabularies import WAKE_PORTFOLIO_QUANTITY_CHANGED, WAKE_PROVIDER_FAILURE
from CommandCenterRuntime.wake import seal_wake_event
from InvestmentDecisionVerticalSlice.models import JournalRecordKind
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal
from CapitalAllocationCycle.hip import build_frozen_hip_v1
from CapitalAllocationCycle.models import PositionCapitalView, ProposedSubjectNotional
from KbCapitalFactAuthority.models import (
    ExplicitCapitalFactBinding, ExplicitCapitalPortfolioBinding,
    ExplicitHoldingsCapitalNormalizationRequest,
    ExplicitPositionMarketValueBinding,
)
from KbCapitalFactAuthority.tests.helpers import (
    FakeAdapter, balances_collect_request, balances_payload, balances_request,
    identity, policy, success_outcome,
)
from KbCapitalFactAuthority.service import run_kb_capital_fact_plane
from OperationalCioCycle.tests.helpers import Fixture, NOW as OCC_NOW
from ProductionIntegration.journal import ProductionJournal
from ProductionIntegration.models import AllocationComposition, PreTradeComposition, ProductionDomainInputs
from ProductionIntegration.runner import ProductionJooDomainRunner
from ProviderGateway.models import ExplicitProviderPayloadEnvelope
from ProductionIntegration.service import (
    recover_joo_command_center_state,
    run_mock_broker_submission_dry_run,
    run_one_joo_command_center_cycle,
)


NOW = BROKER_NOW


def wake(wake_id, kind, fact_id, *, observed_at=NOW):
    return seal_wake_event(
        wake_event_id=wake_id, wake_type=kind, source="verified_fixture",
        fact_or_evidence_id=fact_id, observed_at=observed_at,
        subject_ids=("subject-samsung",), provenance="deterministic",
    )


def provider_failure(fact_id):
    payload = {
        "fact_id": fact_id, "provider_id": "kb_open_api",
        "operation": "READ", "detail": "unavailable", "observed_at": NOW,
    }
    return ProviderFailureFact(
        fact_id, "kb_open_api", "READ", "unavailable", NOW,
        command_center_seal(payload),
    )


def quantity_fact(fact_id, observed_at):
    payload = {
        "fact_id": fact_id, "subject_id": "subject-samsung",
        "quantity": Decimal("10"), "observed_at": observed_at,
    }
    return PortfolioQuantityFact(
        fact_id, "subject-samsung", Decimal("10"), observed_at,
        command_center_seal(payload),
    )


class ProductionIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.journal = DecisionJournal(Path(self.tmp.name) / "journal.sqlite3")

    def tearDown(self):
        self.journal.close()
        self.tmp.cleanup()

    def test_provider_failure_cycle_is_durable_recoverable_and_idempotent(self):
        ProductionJournal(self.journal).append_artifact(
            JournalRecordKind.COMMAND_CENTER_SOURCE_FACT,
            "provider-failure-fact", provider_failure("provider-failure-fact"), NOW, "provider",
        )
        event = wake("wake-provider", WAKE_PROVIDER_FAILURE, "provider-failure-fact")
        request = CommandCenterCycleRequest(
            "command-cycle", "holder", (event,),
            (DetectedChange(WAKE_PROVIDER_FAILURE, None, "provider-failure-fact", (), "outage"),),
            now=NOW,
        )
        first = run_one_joo_command_center_cycle(
            request=request, inputs=ProductionDomainInputs(), journal=self.journal,
        )
        self.assertEqual(first.command_center.result_kind, "success")
        self.assertIn(("wake_source:0", "provider-failure-fact"), first.artifact_references)
        records_before = len(self.journal.list_records())
        duplicate = run_one_joo_command_center_cycle(
            request=replace(request, cycle_id="duplicate-cycle"),
            inputs=ProductionDomainInputs(), journal=self.journal,
        )
        self.assertEqual(duplicate.command_center.result_kind, "idempotent")
        self.assertGreater(len(self.journal.list_records()), records_before)
        recovered = recover_joo_command_center_state(journal=self.journal, state_id="restarted")
        self.assertFalse(recovered.state.live_mutation_enabled)
        self.assertTrue(recovered.idempotency_hits)

    def test_prior_attention_survives_distinct_wake_without_reappend_collision(self):
        durable = ProductionJournal(self.journal)
        durable.append_artifacts((
            (JournalRecordKind.COMMAND_CENTER_SOURCE_FACT, "provider-failure-a", provider_failure("provider-failure-a")),
            (JournalRecordKind.COMMAND_CENTER_SOURCE_FACT, "provider-failure-b", provider_failure("provider-failure-b")),
        ), NOW, "provider")
        first_event = wake("wake-provider-a", WAKE_PROVIDER_FAILURE, "provider-failure-a")
        first_request = CommandCenterCycleRequest(
            "cycle-a", "holder", (first_event,),
            (DetectedChange(WAKE_PROVIDER_FAILURE, None, "provider-failure-a", (), "outage-a"),),
            now=NOW,
        )
        run_one_joo_command_center_cycle(
            request=first_request, inputs=ProductionDomainInputs(), journal=self.journal,
        )
        second_event = wake("wake-provider-b", WAKE_PROVIDER_FAILURE, "provider-failure-b")
        second = run_one_joo_command_center_cycle(
            request=CommandCenterCycleRequest(
                "cycle-b", "holder", (second_event,),
                (DetectedChange(WAKE_PROVIDER_FAILURE, None, "provider-failure-b", (), "outage-b"),),
                now=NOW,
            ),
            inputs=ProductionDomainInputs(), journal=self.journal,
        )
        self.assertEqual(second.command_center.result_kind, "success")
        self.assertEqual(len(second.command_center.attention_items), 2)

    def test_real_block_a_portfolio_path_and_report_lineage(self):
        self.journal.close()
        fixture = Fixture(self.tmp.name)
        self.journal = fixture.journal
        kwargs = dict(
            config=fixture.config, first_slice_arguments=fixture.arguments,
            subjects=fixture.subjects, admissions=fixture.admissions,
            plans=fixture.plans, providers={"grok": fixture.grok},
            journal=fixture.journal, clock=lambda: OCC_NOW,
        )
        event = wake("wake-portfolio", WAKE_PORTFOLIO_QUANTITY_CHANGED, "raw-fact-001", observed_at=OCC_NOW)
        request = CommandCenterCycleRequest(
            "portfolio-command", "holder", (event,),
            (DetectedChange(WAKE_PORTFOLIO_QUANTITY_CHANGED, None, "raw-fact-001", ("subject-samsung",), "quantity"),),
            now=OCC_NOW,
        )
        ProductionJournal(fixture.journal).append_artifact(
            JournalRecordKind.COMMAND_CENTER_SOURCE_FACT,
            "raw-fact-001", quantity_fact("raw-fact-001", OCC_NOW), OCC_NOW, "upstream-change",
        )
        with patch("InvestmentResearchOrchestrator.run_coordinator.utc_now", return_value=OCC_NOW), patch("InvestmentResearchOrchestrator.run_coordinator.datetime") as clock:
            clock.now.return_value = OCC_NOW
            result = run_one_joo_command_center_cycle(
                request=request,
                inputs=ProductionDomainInputs(operational_cio_kwargs=kwargs),
                journal=fixture.journal,
            )
        self.assertEqual(result.command_center.result_kind, "success", result.command_center.failure_codes)
        refs = dict(result.command_center.report.artifact_references)
        self.assertEqual(refs["portfolio_snapshot"], "cycle:completed#portfolio_snapshot=snapshot-001")
        self.assertIn("operational_cio_cycle", refs)
        self.assertTrue(any(key.startswith("exact_ev:") for key in refs))
        self.assertTrue(any(key.startswith("cio_decision:") for key in refs))
        self.assertEqual(len(fixture.kb_http.calls), 2)
        fixture.engine.close()

    def test_unknown_wake_source_rejected_before_provider_or_ai_side_effects(self):
        self.journal.close()
        fixture = Fixture(self.tmp.name)
        self.journal = fixture.journal
        kwargs = dict(
            config=fixture.config, first_slice_arguments=fixture.arguments,
            subjects=fixture.subjects, admissions=fixture.admissions,
            plans=fixture.plans, providers={"grok": fixture.grok},
            journal=fixture.journal, clock=lambda: OCC_NOW,
        )
        event = wake("wake-forged", WAKE_PORTFOLIO_QUANTITY_CHANGED, "nonexistent-fact", observed_at=OCC_NOW)
        with self.assertRaisesRegex(ValueError, "WAKE_SOURCE_NOT_DURABLE"):
            run_one_joo_command_center_cycle(
                request=CommandCenterCycleRequest(
                    "forged-command", "holder", (event,),
                    (DetectedChange(WAKE_PORTFOLIO_QUANTITY_CHANGED, None, "nonexistent-fact", (), "forged"),),
                    now=OCC_NOW,
                ),
                inputs=ProductionDomainInputs(operational_cio_kwargs=kwargs),
                journal=fixture.journal,
            )
        self.assertEqual(fixture.kb_http.calls, [])
        self.assertEqual(fixture.http.calls, [])
        self.assertEqual(fixture.journal.list_records(), ())
        self.assertEqual(fixture.store._engine.list_in_append_order(), ())
        fixture.engine.close()

    def test_real_a_b0_b_capital_path_does_not_repeat_research(self):
        self.journal.close()
        fixture = Fixture(self.tmp.name)
        self.journal = fixture.journal
        occ_kwargs = dict(
            config=fixture.config, first_slice_arguments=fixture.arguments,
            subjects=fixture.subjects, admissions=fixture.admissions,
            plans=fixture.plans, providers={"grok": fixture.grok},
            journal=fixture.journal, clock=lambda: OCC_NOW,
        )
        with patch("InvestmentResearchOrchestrator.run_coordinator.utc_now", return_value=OCC_NOW), patch("InvestmentResearchOrchestrator.run_coordinator.datetime") as clock:
            clock.now.return_value = OCC_NOW
            fixture.run()
        research_calls = len(fixture.http.calls)
        raw = fixture.store.get_by_fact_id("raw-fact-001")
        raw_envelope = ExplicitProviderPayloadEnvelope(
            raw.envelope_id, raw.provider_id, raw.source_class, raw.collected_at,
            raw.status, raw.payload, None, "capital-holdings-correlation",
        )
        mv_binding = ExplicitPositionMarketValueBinding(
            "account-primary", "domestic-stock", "KRW", "005930",
            "position-mv-e", "position-mv-envelope-e", None,
        )
        holdings_request = ExplicitHoldingsCapitalNormalizationRequest(
            "raw-fact-001", "account-primary",
            ExplicitCapitalFactBinding("valuation-e", "valuation-envelope-e", None),
            (mv_binding,),
        )
        capital_kwargs = dict(
            adapter=FakeAdapter((success_outcome(
                "balances-envelope-e", "balances-corr-e", balances_payload(), OCC_NOW,
            ),)),
            balances_collect_request=balances_collect_request("e"),
            balances_raw_fact_id="balances-raw-e",
            balances_normalization_request=balances_request("e"),
            fact_store=fixture.store, snapshot_identity=identity("e"),
            portfolio_binding=ExplicitCapitalPortfolioBinding("snapshot-001", "portfolio-main", "context-001"),
            policy=policy(), now=OCC_NOW,
            holdings_raw_fact_id="raw-fact-001",
            holdings_raw_envelope=raw_envelope,
            holdings_capital_normalization_request=holdings_request,
        )
        # Simulate crash after B0 committed FactStore but before Block E could
        # journal CAPITAL_SNAPSHOT. Restart must rebuild without another READ.
        precrash = run_kb_capital_fact_plane(**capital_kwargs)
        self.assertEqual(precrash.result_kind, "success")

        class NoSecondRead:
            def collect(self, _request):
                raise AssertionError("duplicate capital provider read")

        capital_kwargs["adapter"] = NoSecondRead()
        hip = build_frozen_hip_v1(effective_at=OCC_NOW)
        allocation = AllocationComposition(
            "allocation-e", hip,
            (PositionCapitalView("subject-samsung", "position-mv-e", "present", Decimal("710000"), "KRW"),),
            (ProposedSubjectNotional("leg-e", "subject-samsung", Decimal("710000"), None, None, ()),),
        )
        event = wake("wake-capital", "CAPITAL_ORDERABLE_CASH_CHANGED", "orderable-cash-fact-e", observed_at=OCC_NOW)
        request = CommandCenterCycleRequest(
            "capital-command", "holder", (event,),
            (DetectedChange("CAPITAL_ORDERABLE_CASH_CHANGED", None, "orderable-cash-fact-e", (), "cash"),),
            now=OCC_NOW,
        )
        result = run_one_joo_command_center_cycle(
            request=request,
            inputs=ProductionDomainInputs(
                operational_cio_kwargs=occ_kwargs,
                capital_fact_kwargs=capital_kwargs,
                allocation=allocation,
            ),
            journal=fixture.journal,
        )
        self.assertEqual(result.command_center.result_kind, "partial_failure")
        self.assertEqual(result.command_center.failure_codes, ("INVESTMENT_HUMAN_APPROVAL_REQUIRED",))
        self.assertEqual(len(fixture.http.calls), research_calls)
        proposal = ProductionJournal(fixture.journal).load(
            JournalRecordKind.CAPITAL_ALLOCATION_PROPOSAL, "proposal:allocation-e"
        )
        self.assertEqual(len(proposal), 1)
        fixture.engine.close()

    def _durable_execution_chain(self):
        hip, snapshot, proposal, approval, artifact = sealed_chain()
        bundle = make_pretrade_bundle(account=verified_account(), limit_price="100000", cash_amount="50000000")
        validation = run_pretrade_validation(
            validation_id="pretrade-dry", bundle=bundle, side="BUY",
            approved_notional_krw=proposal.legs[0].proposed_market_value_krw,
            validated_at=NOW,
        )
        intent = seal_order_intent_from_approval_chain(
            intent_id="intent-dry", side="BUY", portfolio_subject_id="CAND-B",
            bundle=bundle, validation=validation, artifact=artifact,
            approval=approval, sealed_at=NOW,
        )
        tea, _ = authorize_trade_execution(
            authorization_id="tea-dry", order_intent=intent,
            artifact=artifact, approval=approval, authorized_at=NOW,
            principal="human-operator",
        )
        durable = ProductionJournal(self.journal)
        durable.append_artifacts((
            (JournalRecordKind.INVESTMENT_HUMAN_APPROVAL, approval.approval_id, approval),
            (JournalRecordKind.SEALED_APPROVED_ALLOCATION, artifact.artifact_id, artifact),
            (JournalRecordKind.PRETRADE_REVALIDATION, validation.validation_id, validation),
            (JournalRecordKind.ORDER_INTENT_SEALED, intent.intent_id, intent),
            (JournalRecordKind.TRADE_EXECUTION_AUTHORIZATION, tea.authorization_id, tea),
        ), NOW, "human-actions")
        return intent, tea, bundle.account

    def test_order_intent_wait_for_tea_uses_explicit_freshness_policy(self):
        hip, snapshot, proposal, approval, artifact = sealed_chain()
        bundle = make_pretrade_bundle(account=verified_account(), limit_price="100000", cash_amount="50000000")
        durable = ProductionJournal(self.journal)
        durable.append_artifacts((
            (JournalRecordKind.INVESTMENT_HUMAN_APPROVAL, approval.approval_id, approval),
            (JournalRecordKind.SEALED_APPROVED_ALLOCATION, artifact.artifact_id, artifact),
        ), NOW, "human")
        pretrade = PreTradeComposition(
            "intent-wait", "BUY", "CAND-B",
            proposal.legs[0].delta_market_value_krw,
            bundle, timedelta(minutes=5),
        )
        inputs = ProductionDomainInputs(
            capital_fact_kwargs={"policy": policy(300)},
            allocation=AllocationComposition("req", hip, (), ()),
            investment_approval=approval, approved_artifact=artifact,
            pretrade=pretrade,
        )

        def runner(at):
            value = ProductionJooDomainRunner(
                inputs=inputs, journal=durable, source_event_id="approval-wake",
                now=at, wake_events=(),
            )
            value._ensure_proposal = lambda: proposal
            value._ensure_capital = lambda: snapshot
            return value

        original = runner(NOW)._ensure_pretrade()
        self.assertEqual(runner(NOW + timedelta(minutes=4))._ensure_pretrade(), original)
        with self.assertRaisesRegex(ValueError, "PRETRADE_STALE"):
            runner(NOW + timedelta(minutes=6))._ensure_pretrade()

    def test_mock_acceptance_pre_send_durability_and_one_shot_restart(self):
        intent, tea, account = self._durable_execution_chain()
        transport = MockMutationTransport()
        result = run_mock_broker_submission_dry_run(
            journal=self.journal, source_event_id="dry-event", order_intent=intent,
            trade_authorization=tea, account=account, attempt_id="attempt-dry",
            account_allowlist=verified_account_allowlist(),
                fresh_orderable_cash=fresh_cash_fact(),
            classification_id="accept-dry", now=NOW, transport=transport,
        )
        self.assertEqual(result.acceptance.outcome, "ACCEPTED")
        records = self.journal.list_records()
        attempt_sequence = next(r.sequence for r in records if r.kind is JournalRecordKind.BROKER_SUBMIT_ATTEMPT)
        acceptance_sequence = next(r.sequence for r in records if r.kind is JournalRecordKind.BROKER_ACCEPTANCE)
        self.assertLess(attempt_sequence, acceptance_sequence)
        self.assertEqual(len(transport.calls), 1)
        with self.assertRaisesRegex(ValueError, "ONE_SHOT"):
            run_mock_broker_submission_dry_run(
                journal=self.journal, source_event_id="retry", order_intent=intent,
                trade_authorization=tea, account=account, attempt_id="attempt-retry",
                account_allowlist=verified_account_allowlist(),
                fresh_orderable_cash=fresh_cash_fact(),
                classification_id="accept-retry", now=NOW,
                transport=MockMutationTransport(),
            )

    def test_unknown_is_latched_and_never_resubmitted(self):
        intent, tea, account = self._durable_execution_chain()
        transport = MockMutationTransport(raise_timeout=True)
        result = run_mock_broker_submission_dry_run(
            journal=self.journal, source_event_id="unknown-event", order_intent=intent,
            trade_authorization=tea, account=account, attempt_id="attempt-unknown",
            account_allowlist=verified_account_allowlist(),
                fresh_orderable_cash=fresh_cash_fact(),
            classification_id="unknown", now=NOW, transport=transport,
        )
        self.assertEqual(result.acceptance.outcome, "SUBMISSION_OUTCOME_UNKNOWN")
        self.assertFalse(result.recovery.may_reorder)
        self.assertTrue(result.recovery.requires_human)
        self.assertEqual(len(transport.calls), 1)

    def test_concurrent_same_tea_persists_once_before_any_submit(self):
        intent, tea, account = self._durable_execution_chain()
        translation = translate_order_intent_to_ssam(
            translation_id="translation-concurrent", order_intent=intent, account=account,
        )
        barrier = threading.Barrier(2)
        transports = (MockMutationTransport(), MockMutationTransport())
        outcomes = []
        outcome_lock = threading.Lock()

        def worker(index):
            journal = DecisionJournal(self.journal.journal_identity)
            durable = ProductionJournal(journal)

            def persist(attempt, state):
                barrier.wait(timeout=5)
                durable.append_artifacts((
                    (JournalRecordKind.BROKER_SUBMIT_ATTEMPT, attempt.attempt_id, attempt),
                    (JournalRecordKind.MUTATION_AUTHORITY_STATE,
                     "mutation-authority:" + tea.authorization_id, state),
                ), NOW, "concurrent-event")

            try:
                execute_mutation_attempt(
                    attempt_id=f"attempt-concurrent-{index}", tea=tea,
                    order_intent=intent, translation=translation, account=account,
                    account_allowlist=verified_account_allowlist(),
                fresh_orderable_cash=fresh_cash_fact(),
                    authority=initial_mutation_authority(tea), attempted_at=NOW,
                    transport=transports[index], durable_pre_send_appender=persist,
                )
                outcome = "submitted"
            except (ValueError, RuntimeError) as exc:
                outcome = f"blocked:{exc}"
            finally:
                journal.close()
            with outcome_lock:
                outcomes.append(outcome)

        threads = tuple(threading.Thread(target=worker, args=(index,)) for index in range(2))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(outcomes.count("submitted"), 1)
        self.assertEqual(sum(len(transport.calls) for transport in transports), 1)
        authority_records = ProductionJournal(self.journal).load(
            JournalRecordKind.MUTATION_AUTHORITY_STATE,
            "mutation-authority:" + tea.authorization_id,
        )
        self.assertEqual(len(authority_records), 1)

    def test_live_transport_and_secret_persistence_are_rejected(self):
        intent, tea, account = self._durable_execution_chain()
        with self.assertRaises(TypeError):
            run_mock_broker_submission_dry_run(
                journal=self.journal, source_event_id="live", order_intent=intent,
                trade_authorization=tea, account=account, attempt_id="attempt-live",
                account_allowlist=verified_account_allowlist(),
                fresh_orderable_cash=fresh_cash_fact(),
                classification_id="live", now=NOW,
                transport=LiveMutationTransportDisabled(),
            )
        for index, key in enumerate((
            "appKey", "appSecret", "access_token", "token", "Authorization",
            "password", "secret", "credential", "api_key", "private-key",
        )):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "credential"):
                ProductionJournal(self.journal).append_artifact(
                    JournalRecordKind.COMMAND_CENTER_REPORT, f"secret-record-{index}",
                    {key: "forbidden"}, NOW, "event",
                )


if __name__ == "__main__":
    unittest.main()
