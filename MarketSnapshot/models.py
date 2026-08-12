from dataclasses import dataclass

from MarketInstrumentObservation.models import (
    ExplicitMarketInstrumentObservation,
)
from MarketSessionContext.models import (
    ExplicitMarketSessionContext,
)


@dataclass(frozen=True)
class ExplicitMarketSnapshot:
    market_snapshot_id: str
    session_context: ExplicitMarketSessionContext
    instrument_observations: tuple[
        ExplicitMarketInstrumentObservation,
        ...,
    ]
