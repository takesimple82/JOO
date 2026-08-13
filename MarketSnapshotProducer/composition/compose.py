from __future__ import annotations

from decimal import Decimal, InvalidOperation

from MarketEndpoint.models import ExplicitMarket
from MarketFactProvenanceReference.models import (
    ExplicitMarketFactProvenanceReference,
)
from MarketInstrument.models import ExplicitMarketInstrument
from MarketInstrumentObservation.models import (
    MARKET_STATUS_VALUES,
    ExplicitMarketInstrumentObservation,
)
from MarketSessionContext.models import (
    ExplicitMarketSessionContext,
)
from MarketSnapshot.models import ExplicitMarketSnapshot
from MarketVenue.models import ExplicitMarketVenue

from FactStore.models import ExplicitStoredFactRecord

from MarketSnapshotProducer.models.types import (
    ExplicitMarketSessionProfile,
)


def project_bound_payload(
    payload: object,
    last_price_payload_key: str,
    market_status_payload_key: str,
) -> tuple[Decimal, str] | None:
    if type(payload) is not dict:
        return None
    if last_price_payload_key not in payload:
        return None
    last_price = _project_last_price(
        payload[last_price_payload_key]
    )
    if last_price is None:
        return None
    if market_status_payload_key not in payload:
        return None
    market_status = payload[market_status_payload_key]
    if type(market_status) is not str:
        return None
    if market_status not in MARKET_STATUS_VALUES:
        return None
    return (last_price, market_status)


def _project_last_price(value: object) -> Decimal | None:
    if type(value) is Decimal:
        if not value.is_finite():
            return None
        return value
    if type(value) is str:
        try:
            projected = Decimal(value)
        except (InvalidOperation, ValueError):
            return None
        if not projected.is_finite():
            return None
        return projected
    return None


def build_explicit_market(market_id: str) -> ExplicitMarket:
    return ExplicitMarket(market_id)


def build_explicit_market_venue(
    venue_id: str,
) -> ExplicitMarketVenue:
    return ExplicitMarketVenue(venue_id)


def build_explicit_market_session_context(
    session_context_id: str,
    profile: ExplicitMarketSessionProfile,
) -> ExplicitMarketSessionContext:
    return ExplicitMarketSessionContext(
        session_context_id,
        profile.market_id,
        profile.venue_id,
        profile.session_profile_id,
        profile.timezone_id,
        profile.calendar_id,
    )


def build_explicit_market_fact_provenance_reference(
    record: ExplicitStoredFactRecord,
) -> ExplicitMarketFactProvenanceReference:
    return ExplicitMarketFactProvenanceReference(
        record.fact_id,
        record.provider_id,
        record.collected_at.isoformat(),
    )


def build_explicit_market_instrument_observation(
    instrument: ExplicitMarketInstrument,
    session_context: ExplicitMarketSessionContext,
    last_price: Decimal,
    market_status: str,
    provenance: ExplicitMarketFactProvenanceReference,
) -> ExplicitMarketInstrumentObservation:
    return ExplicitMarketInstrumentObservation(
        instrument,
        session_context,
        last_price,
        market_status,
        provenance,
    )


def build_explicit_market_snapshot(
    market_snapshot_id: str,
    session_context: ExplicitMarketSessionContext,
    instrument_observations: tuple[
        ExplicitMarketInstrumentObservation,
        ...,
    ],
) -> ExplicitMarketSnapshot:
    return ExplicitMarketSnapshot(
        market_snapshot_id,
        session_context,
        instrument_observations,
    )
