from PortfolioHoldingSnapshot.models import (
    ExplicitPortfolioHoldingSnapshot,
)
from PortfolioHoldingSnapshot.validation import (
    validate_explicit_portfolio_holding_snapshot,
)
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioObservationContext.validation import (
    validate_explicit_portfolio_observation_context,
)
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioWatchlistEntry.models import (
    ExplicitPortfolioWatchlistEntry,
)
from PortfolioWatchlistEntry.validation import (
    validate_explicit_portfolio_watchlist_entry,
)


def validate_explicit_portfolio_snapshot(
    snapshot: ExplicitPortfolioSnapshot,
) -> None:
    if type(snapshot) is not ExplicitPortfolioSnapshot:
        raise TypeError(
            "snapshot must be ExplicitPortfolioSnapshot"
        )
    if type(snapshot.portfolio_snapshot_id) is not str:
        raise TypeError("portfolio_snapshot_id must be str")
    if snapshot.portfolio_snapshot_id.strip() == "":
        raise ValueError(
            "portfolio_snapshot_id must not be blank"
        )
    if (
        type(snapshot.observation_context)
        is not ExplicitPortfolioObservationContext
    ):
        raise TypeError(
            "observation_context must be "
            "ExplicitPortfolioObservationContext"
        )
    validate_explicit_portfolio_observation_context(
        snapshot.observation_context
    )
    if (
        type(snapshot.holding_snapshot)
        is not ExplicitPortfolioHoldingSnapshot
    ):
        raise TypeError(
            "holding_snapshot must be "
            "ExplicitPortfolioHoldingSnapshot"
        )
    validate_explicit_portfolio_holding_snapshot(
        snapshot.holding_snapshot
    )
    if (
        snapshot.holding_snapshot.observation_context
        .observation_context_id
        != snapshot.observation_context.observation_context_id
    ):
        raise ValueError(
            "holding_snapshot observation_context_id must match "
            "observation_context observation_context_id"
        )
    if (
        snapshot.holding_snapshot.observation_context.portfolio_id
        != snapshot.observation_context.portfolio_id
    ):
        raise ValueError(
            "holding_snapshot portfolio_id must match "
            "observation_context portfolio_id"
        )
    if type(snapshot.watchlist_entries) is not tuple:
        raise TypeError("watchlist_entries must be tuple")

    memberships = set()
    for entry in snapshot.watchlist_entries:
        if type(entry) is not ExplicitPortfolioWatchlistEntry:
            raise TypeError(
                "watchlist_entries must contain only "
                "ExplicitPortfolioWatchlistEntry"
            )
        validate_explicit_portfolio_watchlist_entry(entry)
        if (
            entry.membership.portfolio_id
            != snapshot.observation_context.portfolio_id
        ):
            raise ValueError(
                "watchlist entry portfolio_id must match "
                "observation_context portfolio_id"
            )
        membership = (
            entry.membership.portfolio_id,
            entry.membership.portfolio_subject_id,
        )
        if membership in memberships:
            raise ValueError(
                "watchlist_entries must not contain "
                "duplicate memberships"
            )
        memberships.add(membership)
