"""Production-facing one-cycle, recovery, and mock-only dry-run entrypoints."""
from __future__ import annotations

from dataclasses import replace
from dataclasses import fields, is_dataclass
from datetime import datetime, timezone

from BrokerExecutionCycle.acceptance import classify_submission_outcome
from BrokerExecutionCycle.authorization import initial_mutation_authority
from BrokerExecutionCycle.models import MutationAuthorityState
from BrokerExecutionCycle.mutation_gate import execute_mutation_attempt
from BrokerExecutionCycle.mutation_transport import MockMutationTransport
from BrokerExecutionCycle.provider_read import normalize_ssqm2341_status
from BrokerExecutionCycle.reconciliation import fill_fact_from_status, reconcile_acceptance_and_fill
from BrokerExecutionCycle.recovery import plan_submission_unknown_recovery
from BrokerExecutionCycle.translation import translate_order_intent_to_ssam
from BrokerExecutionCycle.vocabularies import ACCEPTANCE_REJECTED, ACCEPTANCE_UNKNOWN
from CommandCenterRuntime.idempotency import IdempotencyStore
from CommandCenterRuntime.recovery import recover_command_center
from CommandCenterRuntime.reporting import build_command_center_report
from CommandCenterRuntime.service import CommandCenterCycleRequest, run_command_center_cycle
from InvestmentDecisionVerticalSlice.models import JournalRecordKind
from FactStore.models import ExplicitStoredFactRecord
from FactStore.validation.validators import verify_stored_fact_integrity
from CommandCenterRuntime.integrity import integrity_seal as command_center_seal
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal
from ProductionIntegration.journal import ProductionJournal
from ProductionIntegration.models import MockSubmissionResult, ProductionCycleResult
from ProductionIntegration.runner import ProductionJooDomainRunner


def run_one_joo_command_center_cycle(*, request, inputs, journal):
    """Run one externally scheduled cycle; live mutation is structurally absent."""
    if type(request) is not CommandCenterCycleRequest:
        raise TypeError("CommandCenterCycleRequest required")
    if type(journal) is not DecisionJournal:
        raise TypeError("existing DecisionJournal required")
    if type(request.now) is not datetime or request.now.tzinfo is not timezone.utc:
        raise ValueError("production cycle requires explicit UTC now")
    durable = ProductionJournal(journal)
    _verify_wake_sources(request.wake_events, inputs, durable)
    _wakes, _checkpoints, attention, idem = durable.recovery_records()
    store = IdempotencyStore()
    store.load(idem)
    effective = replace(request, prior_attention=attention)
    runner = ProductionJooDomainRunner(
        inputs=inputs, journal=durable,
        source_event_id=request.wake_events[0].wake_event_id,
        now=request.now, wake_events=request.wake_events,
    )
    result = run_command_center_cycle(
        effective, idempotency_store=store, domain_runner=runner,
        enable_live_mutation=False,
    )
    if result.report is not None:
        report = build_command_center_report(
            report_id=result.report.report_id, cycle_id=request.cycle_id,
            wake_events=result.wake_events, changes=request.changes,
            attention_items=result.attention_items, checkpoint=result.checkpoint,
            created_at=result.report.created_at, warnings=result.report.warnings,
            artifact_references=runner.artifact_references,
        )
        result = replace(result, report=report)
    durable.append_command_center(
        result, store.all_records(), request.wake_events[0].wake_event_id, request.now,
    )
    return ProductionCycleResult(result, runner.artifact_references)


def _verify_wake_sources(wake_events, inputs, durable):
    """Every wake must resolve to a durable journal or verified FactStore ID."""
    journal_sources = {
        record_id: artifact
        for _record, artifact in durable.load(JournalRecordKind.COMMAND_CENTER_SOURCE_FACT)
        for record_id in (_record.record_id,)
    }
    stores = []
    for candidate in (
        inputs.source_fact_store,
        None if inputs.operational_cio_kwargs is None else inputs.operational_cio_kwargs.get("first_slice_arguments", {}).get("fact_store"),
        None if inputs.capital_fact_kwargs is None else inputs.capital_fact_kwargs.get("fact_store"),
    ):
        if candidate is not None and candidate not in stores:
            stores.append(candidate)
    for wake in wake_events:
        artifact = journal_sources.get(wake.fact_or_evidence_id)
        if artifact is not None:
            _verify_source_artifact(wake.fact_or_evidence_id, artifact)
            continue
        found = False
        for store in stores:
            try:
                record = store.get_by_fact_id(wake.fact_or_evidence_id)
                store.verify_integrity(record.fact_id)
                durable.append_artifact(
                    JournalRecordKind.COMMAND_CENTER_SOURCE_FACT,
                    record.fact_id, record, wake.observed_at, wake.wake_event_id,
                )
                found = True
                break
            except ValueError:
                continue
        if not found:
            raise ValueError("WAKE_SOURCE_NOT_DURABLE")


def _verify_source_artifact(expected_id, artifact):
    if type(artifact) is ExplicitStoredFactRecord:
        if artifact.fact_id != expected_id:
            raise ValueError("WAKE_SOURCE_IDENTITY_MISMATCH")
        verify_stored_fact_integrity(artifact)
        return
    if not is_dataclass(artifact) or not hasattr(artifact, "integrity_seal"):
        raise ValueError("WAKE_SOURCE_TYPE_NOT_AUTHORITATIVE")
    identity = getattr(artifact, "fact_id", None)
    if identity != expected_id:
        raise ValueError("WAKE_SOURCE_IDENTITY_MISMATCH")
    payload = {
        field.name: getattr(artifact, field.name)
        for field in fields(artifact)
        if field.name != "integrity_seal"
    }
    if command_center_seal(payload) != artifact.integrity_seal:
        raise ValueError("WAKE_SOURCE_INTEGRITY_MISMATCH")


def recover_joo_command_center_state(*, journal, state_id):
    """Rebuild only from integrity-checked durable records; performs no I/O work."""
    durable = ProductionJournal(journal)
    wakes, checkpoints, attention, idem = durable.recovery_records()
    return recover_command_center(
        state_id=state_id, checkpoints=checkpoints,
        attention_items=attention, idempotency_records=idem,
        wake_events=wakes, live_mutation_enabled=False,
    )


def run_mock_broker_submission_dry_run(
    *, journal, source_event_id, order_intent, trade_authorization, account,
    attempt_id, classification_id, now, transport,
    status_payload=None, cash_corroborated=None, holdings_corroborated=None,
):
    """Explicit test/dry-run seam. Accepts MockMutationTransport exactly."""
    if type(transport) is not MockMutationTransport:
        raise TypeError("exact MockMutationTransport required")
    durable = ProductionJournal(journal)
    if not durable.contains_exact(
        JournalRecordKind.ORDER_INTENT_SEALED, order_intent.intent_id, order_intent
    ):
        raise ValueError("ORDER_INTENT_NOT_DURABLE")
    if not durable.contains_exact(
        JournalRecordKind.TRADE_EXECUTION_AUTHORIZATION,
        trade_authorization.authorization_id, trade_authorization,
    ):
        raise ValueError("TRADE_EXECUTION_AUTHORIZATION_NOT_DURABLE")
    authority_record_id = "mutation-authority:" + trade_authorization.authorization_id
    consumed = durable.load(JournalRecordKind.MUTATION_AUTHORITY_STATE, authority_record_id)
    if consumed:
        raise ValueError("TEA_ONE_SHOT_CONSUMED")
    translation = translate_order_intent_to_ssam(
        translation_id="translation:" + order_intent.intent_id,
        order_intent=order_intent, account=account,
    )
    authority = initial_mutation_authority(trade_authorization)

    def persist_before_send(attempt, state):
        durable.append_artifacts((
            (JournalRecordKind.BROKER_SUBMIT_ATTEMPT, attempt.attempt_id, attempt),
            (JournalRecordKind.MUTATION_AUTHORITY_STATE, authority_record_id, state),
        ), now, source_event_id)

    attempt, authority, response = execute_mutation_attempt(
        attempt_id=attempt_id, tea=trade_authorization,
        order_intent=order_intent, translation=translation, account=account,
        authority=authority, attempted_at=now, transport=transport,
        durable_pre_send_appender=persist_before_send,
    )
    acceptance = classify_submission_outcome(
        classification_id=classification_id, attempt_id=attempt_id,
        response=response, classified_at=now,
    )
    acceptance_kind = (
        JournalRecordKind.BROKER_REJECTION if acceptance.outcome == ACCEPTANCE_REJECTED
        else JournalRecordKind.SUBMISSION_OUTCOME_UNKNOWN if acceptance.outcome == ACCEPTANCE_UNKNOWN
        else JournalRecordKind.BROKER_ACCEPTANCE
    )
    durable.append_artifact(acceptance_kind, acceptance.classification_id, acceptance, now, source_event_id)
    status = fill = recovery = None
    if status_payload is not None:
        status = normalize_ssqm2341_status(
            fact_id="status:" + attempt_id, payload=status_payload,
            query_order_no=acceptance.broker_order_no, query_order_date=None,
            collected_at=now, raw_envelope_id="read-envelope:" + attempt_id,
        )
        fill = fill_fact_from_status(fact_id="fill:" + attempt_id, status=status, observed_at=now)
        durable.append_artifacts((
            (JournalRecordKind.ORDER_STATUS_FACT, status.fact_id, status),
            (JournalRecordKind.FILL_FACT, fill.fact_id, fill),
        ), now, source_event_id)
    if acceptance.outcome == ACCEPTANCE_UNKNOWN:
        recovery = plan_submission_unknown_recovery(
            plan_id="recovery:" + attempt_id, acceptance=acceptance, status_fact=status,
        )
        durable.append_artifact(
            JournalRecordKind.SUBMISSION_OUTCOME_UNKNOWN,
            recovery.plan_id, recovery, now, source_event_id,
        )
    reconciliation = reconcile_acceptance_and_fill(
        result_id="recon:" + attempt_id, attempt_id=attempt_id,
        acceptance=acceptance, fill=fill,
        cash_corroborated=cash_corroborated,
        holdings_corroborated=holdings_corroborated,
        reconciled_at=now,
    )
    durable.append_artifact(
        JournalRecordKind.RECONCILIATION_RESULT,
        reconciliation.result_id, reconciliation, now, source_event_id,
    )
    return MockSubmissionResult(attempt, authority, acceptance, recovery, fill, reconciliation)
