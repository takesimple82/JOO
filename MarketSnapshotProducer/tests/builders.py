from __future__ import annotations

from datetime import datetime, timedelta, timezone

from FactStore.models import ExplicitFactAppendRequest
from FactStore.store import FactStore
from MarketInstrument.models import ExplicitMarketInstrument
from ProviderGateway.models import ExplicitProviderPayloadEnvelope

from MarketSnapshotProducer.models.types import (
    ExplicitMarketFactSelectionCriteria,
    ExplicitMarketSessionProfile,
    ExplicitMarketSnapshotProductionPolicy,
    ExplicitMarketSnapshotProductionRequest,
    ExplicitMarketSubjectBinding,
)
from MarketSnapshotProducer.production import (
    MarketSnapshotProducer,
)


UTC = timezone.utc
COLLECTED_AT = datetime(2026, 1, 15, 9, 30, tzinfo=UTC)
APPENDED_AT = datetime(2026, 8, 13, 12, 0, tzinfo=UTC)
EVALUATION_TIME = datetime(2026, 8, 13, 12, 30, tzinfo=UTC)


def utc_clock(moment=EVALUATION_TIME):
    def clock():
        return moment

    return clock


def exploding_clock():
    def clock():
        raise AssertionError("clock must not be called")

    return clock


def make_store(**overrides):
    values = {
        "utc_clock": utc_clock(APPENDED_AT),
        "storage_engine": None,
    }
    values.update(overrides)
    return FactStore(
        values["utc_clock"],
        values["storage_engine"],
    )


def make_producer(store=None, clock=None):
    if store is None:
        store = make_store()
    if clock is None:
        clock = utc_clock()
    return MarketSnapshotProducer(store, clock)


def make_instrument(**overrides):
    values = {"instrument_id": "instrument-001"}
    values.update(overrides)
    return ExplicitMarketInstrument(**values)


def make_korea_profile(**overrides):
    values = {
        "session_profile_id": "korea-session-profile",
        "market_id": "korea-market",
        "venue_id": "korea-venue",
        "timezone_id": "korea-timezone",
        "calendar_id": "korea-calendar",
    }
    values.update(overrides)
    return ExplicitMarketSessionProfile(**values)


def make_us_profile(**overrides):
    values = {
        "session_profile_id": "us-session-profile",
        "market_id": "us-market",
        "venue_id": "us-venue",
        "timezone_id": "us-timezone",
        "calendar_id": "us-calendar",
    }
    values.update(overrides)
    return ExplicitMarketSessionProfile(**values)


def make_profile(**overrides):
    return make_korea_profile(**overrides)


def make_payload(**overrides):
    values = {
        "last_price": "10.00",
        "market_status": "open",
    }
    values.update(overrides)
    return values


def make_envelope(**overrides):
    values = {
        "envelope_id": "envelope-001",
        "provider_id": "market-provider-001",
        "source_class": "market_fact",
        "collected_at": COLLECTED_AT,
        "status": "success",
        "payload": make_payload(),
        "error_diagnostics": None,
        "request_correlation_id": "corr-001",
    }
    values.update(overrides)
    return ExplicitProviderPayloadEnvelope(**values)


def make_append_request(**overrides):
    values = {
        "fact_id": "fact-001",
        "envelope": make_envelope(),
        "superseded_fact_id": None,
    }
    values.update(overrides)
    return ExplicitFactAppendRequest(**values)


def seed_market_fact(store, **overrides):
    return store.append(make_append_request(**overrides))


def make_binding(**overrides):
    values = {
        "instrument": make_instrument(),
        "fact_id": "fact-001",
        "last_price_payload_key": "last_price",
        "market_status_payload_key": "market_status",
    }
    values.update(overrides)
    return ExplicitMarketSubjectBinding(**values)


def make_criteria(**overrides):
    values = {
        "required_source_class": "market_fact",
        "required_source_identity": None,
        "collected_at_start": None,
        "collected_at_end": None,
    }
    values.update(overrides)
    return ExplicitMarketFactSelectionCriteria(**values)


def make_policy(**overrides):
    values = {
        "require_all_bound_subjects": True,
        "allow_partial_emission": False,
        "freshness_max_age": None,
    }
    values.update(overrides)
    return ExplicitMarketSnapshotProductionPolicy(**values)


def make_partial_policy(**overrides):
    values = {
        "require_all_bound_subjects": False,
        "allow_partial_emission": True,
        "freshness_max_age": None,
    }
    values.update(overrides)
    return ExplicitMarketSnapshotProductionPolicy(**values)


def make_request(**overrides):
    values = {
        "market_snapshot_id": "snapshot-001",
        "session_context_id": "session-context-001",
        "session_profile": make_profile(),
        "subject_bindings": (make_binding(),),
        "fact_selection": make_criteria(),
        "production_policy": make_policy(),
    }
    values.update(overrides)
    return ExplicitMarketSnapshotProductionRequest(**values)


def make_freshness_policy(max_age=None, **overrides):
    if max_age is None:
        max_age = timedelta(hours=1)
    values = {"freshness_max_age": max_age}
    values.update(overrides)
    return make_policy(**values)
