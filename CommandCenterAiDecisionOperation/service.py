"""Publish truthful REAL research-unavailable state bound to one observation."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from CommandCenterApplication.models import MODE_REAL_READ_ONLY
from CommandCenterApplication.query import load_real_read_only_dataset
from CommandCenterReadOnlyOperation.models import ReadOnlyObservation
from InvestmentDecisionVerticalSlice.models import JournalRecordKind
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal
from ProductionIntegration.journal import ProductionJournal

from CommandCenterAiDecisionOperation.models import (
    AiCioDecisionAttempt,
    ObservationEvidencePackage,
)
from CommandCenterAiDecisionOperation.validation import (
    validate_ai_cio_decision_attempt,
)


_PROVIDER_CONFIGURATION = (
    ("claude", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"),
    ("gemini", "GEMINI_API_KEY", "GEMINI_MODEL"),
    ("grok", "XAI_API_KEY", "XAI_MODEL"),
    ("perplexity", "PERPLEXITY_API_KEY", "PERPLEXITY_MODEL"),
)


def configured_research_providers():
    """Return provider identities only; never inspect or return secret values."""
    return tuple(
        provider for provider, key_name, model_name in _PROVIDER_CONFIGURATION
        if bool(os.getenv(key_name)) and bool(os.getenv(model_name))
    )


def _active_observation(dataset):
    rows = tuple(
        row for row in dataset.artifacts
        if type(row.artifact) is ReadOnlyObservation
        and row.artifact.observation_id == dataset.active_observation_id
    )
    if len(rows) != 1 or rows[0].sequence is None:
        raise ValueError("one journal-ordered active factual observation required")
    return rows[0]


def record_research_unavailable_attempt(
    *, fact_store_path, journal_path, attempt_id, now,
):
    if type(now) is not datetime or now.tzinfo is not timezone.utc:
        raise ValueError("now must be UTC")
    if type(attempt_id) is not str or attempt_id.strip() == "":
        raise ValueError("attempt_id required")
    configured = configured_research_providers()
    if configured:
        raise ValueError(
            "authorized provider configuration detected; use explicit existing "
            "OperationalCioCycle inputs"
        )
    dataset = load_real_read_only_dataset(
        fact_store_path=fact_store_path, journal_path=journal_path, now=now,
    )
    if dataset.mode != MODE_REAL_READ_ONLY or dataset.active_observation_id is None:
        raise ValueError("published REAL factual observation required")
    row = _active_observation(dataset)
    observation = row.artifact
    factual_at = observation.capital_snapshot.collected_at
    age = now - factual_at
    stale = age.total_seconds() < 0 or age > observation.capital_snapshot.freshness_max_age
    package = ObservationEvidencePackage(
        f"evidence-package:{attempt_id}",
        observation.observation_id,
        row.sequence,
        observation.portfolio_snapshot.portfolio_snapshot_id,
        observation.capital_snapshot.capital_snapshot_id,
        observation.application_fact_ids,
        observation.raw_fact_ids,
        "broker_fact",
        factual_at,
        now,
    )
    blockers = (
        ("FACTUAL_OBSERVATION_STALE",)
        if stale else ("AUTHORIZED_RESEARCH_PROVIDER_UNAVAILABLE",)
    )
    attempt = AiCioDecisionAttempt(
        attempt_id,
        MODE_REAL_READ_ONLY,
        package,
        "RESEARCH_UNAVAILABLE",
        "COMMITTEE_UNAVAILABLE",
        "NOT_EVALUATED",
        "BLOCKED",
        "UNAVAILABLE",
        "UNAVAILABLE",
        "NOT_ISSUED",
        blockers,
        now,
        False,
        False,
    )
    validate_ai_cio_decision_attempt(attempt)
    journal = DecisionJournal(journal_path)
    try:
        ProductionJournal(journal).append_artifact(
            JournalRecordKind.AI_CIO_DECISION_ATTEMPT,
            attempt_id,
            attempt,
            now,
            observation.observation_id,
        )
    finally:
        journal.close()
    return attempt
