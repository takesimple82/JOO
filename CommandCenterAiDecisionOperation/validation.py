"""Fail-closed validation for evidence-bound AI decision attempts."""
from __future__ import annotations

from datetime import datetime, timezone

from CommandCenterAiDecisionOperation.models import (
    AiCioDecisionAttempt,
    ObservationEvidencePackage,
)


def _nonblank(name, value):
    if type(value) is not str or value.strip() == "":
        raise ValueError(f"{name} required")


def _utc(name, value):
    if type(value) is not datetime or value.tzinfo is not timezone.utc:
        raise ValueError(f"{name} must be UTC")


def validate_observation_evidence_package(value):
    if type(value) is not ObservationEvidencePackage:
        raise TypeError("ObservationEvidencePackage required")
    for name in (
        "package_id", "observation_id", "portfolio_snapshot_id",
        "capital_snapshot_id",
    ):
        _nonblank(name, getattr(value, name))
    if type(value.observation_sequence) is not int or value.observation_sequence <= 0:
        raise ValueError("positive observation_sequence required")
    if type(value.fact_ids) is not tuple or not value.fact_ids:
        raise ValueError("factual evidence IDs required")
    if len(set(value.fact_ids)) != len(value.fact_ids):
        raise ValueError("factual evidence IDs must be unique")
    if type(value.raw_fact_ids) is not tuple or len(value.raw_fact_ids) != 2:
        raise ValueError("exact holdings and balances raw evidence required")
    if value.truth_class != "broker_fact":
        raise ValueError("evidence package must remain broker_fact")
    _utc("factual_collected_at", value.factual_collected_at)
    _utc("created_at", value.created_at)
    if value.created_at < value.factual_collected_at:
        raise ValueError("evidence package predates factual collection")


def validate_ai_cio_decision_attempt(value):
    if type(value) is not AiCioDecisionAttempt:
        raise TypeError("AiCioDecisionAttempt required")
    _nonblank("attempt_id", value.attempt_id)
    if value.mode != "REAL_READ_ONLY":
        raise ValueError("REAL_READ_ONLY attempt required")
    validate_observation_evidence_package(value.evidence_package)
    expected = {
        "research_state": "RESEARCH_UNAVAILABLE",
        "committee_state": "COMMITTEE_UNAVAILABLE",
        "contradiction_state": "NOT_EVALUATED",
        "cio_state": "BLOCKED",
        "ev_state": "UNAVAILABLE",
        "allocation_state": "UNAVAILABLE",
        "iha_state": "NOT_ISSUED",
    }
    for name, required in expected.items():
        if getattr(value, name) != required:
            raise ValueError(f"{name} must remain {required}")
    if type(value.blocker_codes) is not tuple or not value.blocker_codes:
        raise ValueError("explicit blocker required")
    for code in value.blocker_codes:
        _nonblank("blocker code", code)
    _utc("created_at", value.created_at)
    if value.created_at != value.evidence_package.created_at:
        raise ValueError("attempt/package timestamp mismatch")
    if value.executable is not False or value.broker_mutation_enabled is not False:
        raise ValueError("AI attempt must not grant execution or broker mutation")
