"""Clearly-labelled deterministic demo dataset built from production contracts."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from CommandCenterRuntime.attention import seal_human_attention_item
from CommandCenterRuntime.reporting import build_command_center_report
from CommandCenterRuntime.vocabularies import ATTENTION_DATA_INTEGRITY_FAILURE
from FactStore.models import ExplicitStoredFactRecord
from FactStore.validation.validators import compute_stored_fact_integrity_seal
from InvestmentDecisionVerticalSlice.models import (
    CioActionPosture,
    CioDecisionRecord,
    JournalRecordKind,
)
from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot

from CommandCenterApplication.models import (
    ApplicationDataset,
    JournalArtifact,
    MODE_FIXTURE,
)


FIXTURE_NOW = datetime(2026, 9, 30, 0, 0, tzinfo=timezone.utc)


def _fact(fact_id, collected_at, payload):
    draft = ExplicitStoredFactRecord(
        fact_id,
        "env:" + fact_id,
        "kb_open_api",
        "broker_fact",
        collected_at,
        collected_at,
        "success",
        payload,
        None,
        None,
    )
    return replace(draft, integrity_seal=compute_stored_fact_integrity_seal(draft))


def build_fixture_dataset(*, now: datetime = FIXTURE_NOW) -> ApplicationDataset:
    if type(now) is not datetime or now.tzinfo is not timezone.utc:
        raise ValueError("fixture now must be UTC")
    collected = now - timedelta(minutes=2)
    facts = (
        _fact("fixture-position-005930", collected, {
            "fact_kind": "kb_ssqm2952_position", "raw_fact_id": "fixture-raw-holdings",
            "raw_envelope_id": "fixture-raw-env", "account_selector": "fixture-account",
            "position_class": "현금", "currency_code": "KRW", "raw_currency_code": "   ",
            "provider_symbol": "A005930", "quantity": "10", "raw_quantity": "000000000010",
        }),
        _fact("fixture-position-000660", collected, {
            "fact_kind": "kb_ssqm2952_position", "raw_fact_id": "fixture-raw-holdings",
            "raw_envelope_id": "fixture-raw-env", "account_selector": "fixture-account",
            "position_class": "현금", "currency_code": "KRW", "raw_currency_code": "KRW",
            "provider_symbol": "A000660", "quantity": "4", "raw_quantity": "000000000004",
        }),
        _fact("fixture-value-005930", collected, {
            "fact_kind": "kb_ssqm2952_position_market_value", "raw_fact_id": "fixture-raw-holdings",
            "raw_envelope_id": "fixture-raw-env", "account_selector": "fixture-account",
            "currency_code": "KRW", "broker_field": "val_amt", "amount_presence": "present",
            "amount": "7100000", "raw_amount": "000000000007100000", "position_class": "현금",
            "provider_symbol": "A005930", "quantity": "10", "raw_quantity": "000000000010",
            "quantity_presence": "present", "valuation_method": "broker_val_amt",
        }),
        _fact("fixture-value-000660", collected, {
            "fact_kind": "kb_ssqm2952_position_market_value", "raw_fact_id": "fixture-raw-holdings",
            "raw_envelope_id": "fixture-raw-env", "account_selector": "fixture-account",
            "currency_code": "KRW", "broker_field": "val_amt", "amount_presence": "present",
            "amount": "820000", "raw_amount": "000000000000820000", "position_class": "현금",
            "provider_symbol": "A000660", "quantity": "4", "raw_quantity": "000000000004",
            "quantity_presence": "present", "valuation_method": "broker_val_amt",
        }),
        _fact("fixture-orderable-cash", collected, {
            "fact_kind": "kb_ssqm0004_orderable_cash", "raw_fact_id": "fixture-raw-balances",
            "raw_envelope_id": "fixture-balance-env", "account_selector": "fixture-account",
            "currency_code": "KRW", "broker_field": "ordr_psbl_csh", "amount_presence": "present",
            "amount": "339901", "raw_amount": "000000000339901",
            "authority": "BROKER_ORDERABLE_CASH_CEILING_NOT_DEPLOYABLE",
        }),
        _fact("fixture-account-valuation", collected, {
            "fact_kind": "kb_ssqm2952_broker_reported_account_valuation",
            "raw_fact_id": "fixture-raw-holdings", "raw_envelope_id": "fixture-raw-env",
            "account_selector": "fixture-account", "currency_code": "KRW",
            "broker_field": "nt_asts_val_amt", "amount_presence": "present",
            "amount": "9000000", "raw_amount": "000000000009000000",
            "sizing_authority": "NOT_SIZING_AUTHORITY",
        }),
        _fact("fixture-exclusions", collected, {
            "fact_kind": "kb_ssqm2952_domestic_projection_exclusions",
            "raw_fact_id": "fixture-raw-holdings", "raw_envelope_id": "fixture-raw-env",
            "account_selector": "fixture-account", "record1_observed_count": 3,
            "domestic_projected_count": 2, "excluded_count": 1,
            "exclusion_reason": "EXCLUDED_NON_DOMESTIC",
            "exclusions": [{"row_index": 2, "raw_currency_code": "USD",
                            "position_class": "외화증권", "provider_symbol": "US0378331005",
                            "reason": "EXCLUDED_NON_DOMESTIC"}],
        }),
    )
    snapshot = ExplicitCapitalSnapshot(
        "fixture-capital-snapshot", "fixture-account", "kb_open_api", "KRW", collected,
        timedelta(minutes=5), "fixture-portfolio-snapshot", "fixture-portfolio",
        "fixture-observation", "fixture-raw-balances", "fixture-raw-holdings",
        "fixture-orderable-cash", "fixture-deposit-today", "fixture-deposit-d1",
        "fixture-deposit-d2", "fixture-withdrawable", "fixture-orderable-total",
        "fixture-account-valuation", ("fixture-value-005930", "fixture-value-000660"),
        "NOT_SIZING_AUTHORITY",
    )
    decision = CioDecisionRecord(
        "fixture-cio-decision", "fixture-portfolio-snapshot", "fixture-evidence-bundle",
        "fixture-semantic-output", ("fixture-thesis",), ("fixture-impact",), (), (),
        ("LONG_TERM",), CioActionPosture.NO_ACTION_UNRESOLVED,
        "NO_CHANGE", "No factual change authorizes a new capital action.", None,
        ("DEMO_DATA_ONLY",), ("fixture-orderable-cash",), False,
    )
    attention = seal_human_attention_item(
        attention_id="fixture-attention-live-blocked",
        category=ATTENTION_DATA_INTEGRITY_FAILURE,
        wake_event_id="fixture-wake-authority",
        bound_record_ids=("authority:gnl_ac_no1",),
        subject_ids=(),
        created_at=now,
        detail="Live execution blocked: gnl_ac_no1 authority is not closed.",
    )
    report = build_command_center_report(
        report_id="fixture-report", cycle_id="fixture-cycle", wake_events=(), changes=(),
        attention_items=(attention,), checkpoint=None, created_at=now,
        warnings=("FIXTURE_DATA_NOT_REAL",),
    )
    artifacts = (
        JournalArtifact("fixture-capital-record", JournalRecordKind.CAPITAL_SNAPSHOT.value, now, snapshot),
        JournalArtifact("fixture-cio-record", JournalRecordKind.CIO_DECISION.value, now, decision),
        JournalArtifact("fixture-attention-record", JournalRecordKind.HUMAN_ATTENTION_ITEM.value, now, attention),
        JournalArtifact("fixture-report-record", JournalRecordKind.COMMAND_CENTER_REPORT.value, now, report),
    )
    return ApplicationDataset(
        MODE_FIXTURE,
        "Deterministic fixture — no live KB or broker data",
        now,
        facts,
        artifacts,
        len(artifacts),
        "NO_CHANGE",
    )
