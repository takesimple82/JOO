from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)
from PortfolioMembership.validation import (
    validate_explicit_portfolio_membership,
)
from PortfolioWatchlistEntry.models import (
    ExplicitPortfolioWatchlistEntry,
)


def validate_explicit_portfolio_watchlist_entry(
    entry: ExplicitPortfolioWatchlistEntry,
) -> None:
    if type(entry) is not ExplicitPortfolioWatchlistEntry:
        raise TypeError(
            "entry must be ExplicitPortfolioWatchlistEntry"
        )
    if type(entry.membership) is not ExplicitPortfolioMembership:
        raise TypeError(
            "membership must be "
            "ExplicitPortfolioMembership"
        )
    validate_explicit_portfolio_membership(entry.membership)
