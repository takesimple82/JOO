from dataclasses import dataclass

from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)


@dataclass(frozen=True)
class ExplicitPortfolioWatchlistEntry:
    membership: ExplicitPortfolioMembership
