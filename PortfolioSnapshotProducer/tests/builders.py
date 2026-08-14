from __future__ import annotations

from datetime import datetime, timedelta, timezone

from FactStore.models import ExplicitFactAppendRequest
from FactStore.store import FactStore
from ProviderGateway.models import ExplicitProviderPayloadEnvelope

from PortfolioSnapshotProducer.models.types import (
    ExplicitPortfolioFactSelectionCriteria,
    ExplicitPortfolioHoldingFactBinding,
    ExplicitPortfolioSnapshotProductionPolicy,
    ExplicitPortfolioSnapshotProductionRequest,
    ExplicitPortfolioWatchlistMembershipDeclaration,
)
from PortfolioSnapshotProducer.production import (
    PortfolioSnapshotProducer,
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
    return PortfolioSnapshotProducer(store, clock)


def make_payload(**overrides):
    values = {"quantity": "10.00"}
    values.update(overrides)
    return values


def make_envelope(**overrides):
    values = {
        "envelope_id": "envelope-001",
        "provider_id": "kb_open_api",
        "source_class": "broker_fact",
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


def seed_broker_fact(store, **overrides):
    return store.append(make_append_request(**overrides))


def make_binding(**overrides):
    values = {
        "fact_id": "fact-001",
        "position_id": "position-001",
        "portfolio_subject_id": "subject-001",
        "quantity_payload_key": "quantity",
    }
    values.update(overrides)
    return ExplicitPortfolioHoldingFactBinding(**values)


def make_declaration(**overrides):
    values = {"portfolio_subject_id": "watch-subject-001"}
    values.update(overrides)
    return ExplicitPortfolioWatchlistMembershipDeclaration(
        **values
    )


def make_criteria(**overrides):
    values = {
        "required_source_class": "broker_fact",
        "required_source_identity": None,
        "collected_at_start": None,
        "collected_at_end": None,
    }
    values.update(overrides)
    return ExplicitPortfolioFactSelectionCriteria(**values)


def make_policy(**overrides):
    values = {"freshness_max_age": None}
    values.update(overrides)
    return ExplicitPortfolioSnapshotProductionPolicy(**values)


def make_request(**overrides):
    values = {
        "portfolio_snapshot_id": "snapshot-001",
        "observation_context_id": "context-001",
        "portfolio_id": "portfolio-001",
        "holding_fact_bindings": (make_binding(),),
        "watchlist_memberships": (),
        "fact_selection": make_criteria(),
        "production_policy": make_policy(),
    }
    values.update(overrides)
    return ExplicitPortfolioSnapshotProductionRequest(**values)


def make_freshness_policy(max_age=None, **overrides):
    if max_age is None:
        max_age = timedelta(hours=1)
    values = {"freshness_max_age": max_age}
    values.update(overrides)
    return make_policy(**values)
