from dataclasses import dataclass

from PortfolioHoldingSnapshot.models import (
    ExplicitPortfolioHoldingSnapshot,
)
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioWatchlistEntry.models import (
    ExplicitPortfolioWatchlistEntry,
)


@dataclass(frozen=True)
class ExplicitPortfolioSnapshot:
    portfolio_snapshot_id: str
    observation_context: ExplicitPortfolioObservationContext
    holding_snapshot: ExplicitPortfolioHoldingSnapshot
    watchlist_entries: tuple[
        ExplicitPortfolioWatchlistEntry,
        ...,
    ]
