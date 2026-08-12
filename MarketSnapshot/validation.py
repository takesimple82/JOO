from MarketInstrumentObservation.models import (
    ExplicitMarketInstrumentObservation,
)
from MarketInstrumentObservation.validation import (
    validate_explicit_market_instrument_observation,
)
from MarketSessionContext.models import (
    ExplicitMarketSessionContext,
)
from MarketSessionContext.validation import (
    validate_explicit_market_session_context,
)
from MarketSnapshot.models import ExplicitMarketSnapshot


def validate_explicit_market_snapshot(
    snapshot: ExplicitMarketSnapshot,
) -> None:
    if type(snapshot) is not ExplicitMarketSnapshot:
        raise TypeError(
            "snapshot must be ExplicitMarketSnapshot"
        )
    if type(snapshot.market_snapshot_id) is not str:
        raise TypeError(
            "market_snapshot_id must be str"
        )
    if snapshot.market_snapshot_id.strip() == "":
        raise ValueError(
            "market_snapshot_id must not be blank"
        )
    if (
        type(snapshot.session_context)
        is not ExplicitMarketSessionContext
    ):
        raise TypeError(
            "session_context must be "
            "ExplicitMarketSessionContext"
        )
    validate_explicit_market_session_context(
        snapshot.session_context
    )
    if type(snapshot.instrument_observations) is not tuple:
        raise TypeError(
            "instrument_observations must be tuple"
        )

    instrument_ids = set()
    root = snapshot.session_context
    for observation in snapshot.instrument_observations:
        if (
            type(observation)
            is not ExplicitMarketInstrumentObservation
        ):
            raise TypeError(
                "instrument_observations must contain only "
                "ExplicitMarketInstrumentObservation"
            )
        validate_explicit_market_instrument_observation(
            observation
        )
        nested = observation.session_context
        if (
            nested.session_context_id
            != root.session_context_id
        ):
            raise ValueError(
                "session_context_id must match the snapshot "
                "session_context_id"
            )
        if nested.market_id != root.market_id:
            raise ValueError(
                "market_id must match the snapshot "
                "market_id"
            )
        if nested.venue_id != root.venue_id:
            raise ValueError(
                "venue_id must match the snapshot "
                "venue_id"
            )
        if (
            nested.session_profile_id
            != root.session_profile_id
        ):
            raise ValueError(
                "session_profile_id must match the snapshot "
                "session_profile_id"
            )
        if nested.timezone_id != root.timezone_id:
            raise ValueError(
                "timezone_id must match the snapshot "
                "timezone_id"
            )
        if nested.calendar_id != root.calendar_id:
            raise ValueError(
                "calendar_id must match the snapshot "
                "calendar_id"
            )
        instrument_id = observation.instrument.instrument_id
        if instrument_id in instrument_ids:
            raise ValueError(
                "instrument_observations must not contain "
                "duplicate instrument_id"
            )
        instrument_ids.add(instrument_id)
