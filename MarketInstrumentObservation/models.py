from dataclasses import dataclass
from decimal import Decimal

from MarketFactProvenanceReference.models import (
    ExplicitMarketFactProvenanceReference,
)
from MarketInstrument.models import ExplicitMarketInstrument
from MarketSessionContext.models import (
    ExplicitMarketSessionContext,
)

MARKET_STATUS_VALUES: tuple[str, ...] = (
    "pre_open",
    "open",
    "post_close",
    "closed",
    "halted",
    "unknown",
)


@dataclass(frozen=True)
class ExplicitMarketInstrumentObservation:
    instrument: ExplicitMarketInstrument
    session_context: ExplicitMarketSessionContext
    last_price: Decimal
    market_status: str
    provenance: ExplicitMarketFactProvenanceReference
