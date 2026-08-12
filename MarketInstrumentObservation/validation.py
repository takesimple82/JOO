from decimal import Decimal

from MarketFactProvenanceReference.models import (
    ExplicitMarketFactProvenanceReference,
)
from MarketFactProvenanceReference.validation import (
    validate_explicit_market_fact_provenance_reference,
)
from MarketInstrument.models import ExplicitMarketInstrument
from MarketInstrument.validation import (
    validate_explicit_market_instrument,
)
from MarketInstrumentObservation.models import (
    MARKET_STATUS_VALUES,
    ExplicitMarketInstrumentObservation,
)
from MarketSessionContext.models import (
    ExplicitMarketSessionContext,
)
from MarketSessionContext.validation import (
    validate_explicit_market_session_context,
)


def validate_explicit_market_instrument_observation(
    observation: ExplicitMarketInstrumentObservation,
) -> None:
    if (
        type(observation)
        is not ExplicitMarketInstrumentObservation
    ):
        raise TypeError(
            "observation must be "
            "ExplicitMarketInstrumentObservation"
        )
    if (
        type(observation.instrument)
        is not ExplicitMarketInstrument
    ):
        raise TypeError(
            "instrument must be ExplicitMarketInstrument"
        )
    validate_explicit_market_instrument(
        observation.instrument
    )
    if (
        type(observation.session_context)
        is not ExplicitMarketSessionContext
    ):
        raise TypeError(
            "session_context must be "
            "ExplicitMarketSessionContext"
        )
    validate_explicit_market_session_context(
        observation.session_context
    )
    if type(observation.last_price) is not Decimal:
        raise TypeError("last_price must be Decimal")
    if not observation.last_price.is_finite():
        raise ValueError("last_price must be finite")
    if type(observation.market_status) is not str:
        raise TypeError("market_status must be str")
    if observation.market_status not in MARKET_STATUS_VALUES:
        raise ValueError(
            "market_status must be one of "
            "MARKET_STATUS_VALUES"
        )
    if (
        type(observation.provenance)
        is not ExplicitMarketFactProvenanceReference
    ):
        raise TypeError(
            "provenance must be "
            "ExplicitMarketFactProvenanceReference"
        )
    validate_explicit_market_fact_provenance_reference(
        observation.provenance
    )
