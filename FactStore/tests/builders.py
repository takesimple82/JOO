from __future__ import annotations

from datetime import datetime, timezone

from ProviderGateway.models import (
    ExplicitErrorDiagnostics,
    ExplicitProviderFailureSignal,
    ExplicitProviderHealthSnapshot,
    ExplicitProviderPayloadEnvelope,
)

from FactStore.models.types import (
    ExplicitFactAppendRequest,
    ExplicitStoredFactRecord,
)
from FactStore.store import FactStore
from FactStore.validation.validators import (
    compute_stored_fact_integrity_seal,
)


UTC = timezone.utc
COLLECTED_AT = datetime(2026, 1, 15, 9, 30, tzinfo=UTC)
APPENDED_AT = datetime(2026, 8, 13, 12, 0, tzinfo=UTC)


def utc_clock(moment=APPENDED_AT):
    def clock():
        return moment

    return clock


def make_store(**overrides):
    values = {
        "utc_clock": utc_clock(),
        "storage_engine": None,
    }
    values.update(overrides)
    return FactStore(
        values["utc_clock"],
        values["storage_engine"],
    )


def make_diagnostics(**overrides):
    values = {
        "failure_class": "PROVIDER_ERROR",
        "detail": "provider reported an error",
    }
    values.update(overrides)
    return ExplicitErrorDiagnostics(**values)


def make_envelope(**overrides):
    values = {
        "envelope_id": "envelope-001",
        "provider_id": "market-provider-001",
        "source_class": "market_fact",
        "collected_at": COLLECTED_AT,
        "status": "success",
        "payload": {"last": "10.00", "venue": "opaque-venue"},
        "error_diagnostics": None,
        "request_correlation_id": "corr-001",
    }
    values.update(overrides)
    return ExplicitProviderPayloadEnvelope(**values)


def make_broker_envelope(**overrides):
    values = {
        "envelope_id": "broker-envelope-001",
        "provider_id": "kb_open_api",
        "source_class": "broker_fact",
        "payload": {"holding": "opaque-broker-body"},
    }
    values.update(overrides)
    return make_envelope(**values)


def make_korea_market_envelope(**overrides):
    values = {
        "envelope_id": "korea-envelope-001",
        "payload": {
            "last": "100",
            "venue": "korea-market-capable",
            "timezone": "korea-timezone",
            "calendar": "korea-calendar",
        },
    }
    values.update(overrides)
    return make_envelope(**values)


def make_us_market_envelope(**overrides):
    values = {
        "envelope_id": "us-envelope-001",
        "payload": {
            "last": "10.00",
            "venue": "us-market-capable",
            "timezone": "us-timezone",
            "calendar": "us-calendar",
        },
    }
    values.update(overrides)
    return make_envelope(**values)


def make_health(**overrides):
    values = {
        "provider_id": "market-provider-001",
        "observed_at": COLLECTED_AT,
        "availability": "available",
        "detail": None,
    }
    values.update(overrides)
    return ExplicitProviderHealthSnapshot(**values)


def make_failure(**overrides):
    values = {
        "provider_id": "market-provider-001",
        "observed_at": COLLECTED_AT,
        "failure_class": "TRANSPORT_FAILURE",
        "detail": None,
        "request_correlation_id": "corr-001",
    }
    values.update(overrides)
    return ExplicitProviderFailureSignal(**values)


def make_request(**overrides):
    values = {
        "fact_id": "fact-001",
        "envelope": make_envelope(),
        "superseded_fact_id": None,
    }
    values.update(overrides)
    return ExplicitFactAppendRequest(**values)


def make_broker_request(**overrides):
    values = {
        "fact_id": "broker-fact-001",
        "envelope": make_broker_envelope(),
        "superseded_fact_id": None,
    }
    values.update(overrides)
    return ExplicitFactAppendRequest(**values)


def make_stored_record(**overrides):
    values = {
        "fact_id": "fact-001",
        "envelope_id": "envelope-001",
        "provider_id": "market-provider-001",
        "source_class": "market_fact",
        "collected_at": COLLECTED_AT,
        "appended_at": APPENDED_AT,
        "status": "success",
        "payload": {"last": "10.00", "venue": "opaque-venue"},
        "superseded_fact_id": None,
        "integrity_seal": None,
    }
    seal_supplied = "integrity_seal" in overrides
    values.update(overrides)
    draft = ExplicitStoredFactRecord(**values)
    if seal_supplied:
        return draft
    return ExplicitStoredFactRecord(
        draft.fact_id,
        draft.envelope_id,
        draft.provider_id,
        draft.source_class,
        draft.collected_at,
        draft.appended_at,
        draft.status,
        draft.payload,
        draft.superseded_fact_id,
        compute_stored_fact_integrity_seal(draft),
    )
