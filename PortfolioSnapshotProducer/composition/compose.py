from __future__ import annotations

from decimal import Decimal, InvalidOperation

from PortfolioHoldingObservation.models import (
    ExplicitPortfolioHoldingObservation,
)
from PortfolioHoldingSnapshot.models import (
    ExplicitPortfolioHoldingSnapshot,
)
from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioPosition.models import ExplicitPortfolioPosition
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioWatchlistEntry.models import (
    ExplicitPortfolioWatchlistEntry,
)


def project_bound_quantity(
    payload: object,
    quantity_payload_key: str,
) -> Decimal | None:
    if type(payload) is not dict:
        return None
    if quantity_payload_key not in payload:
        return None
    return _project_quantity_value(payload[quantity_payload_key])


def _project_quantity_value(value: object) -> Decimal | None:
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


def build_explicit_portfolio_observation_context(
    observation_context_id: str,
    portfolio_id: str,
) -> ExplicitPortfolioObservationContext:
    return ExplicitPortfolioObservationContext(
        observation_context_id,
        portfolio_id,
    )


def build_explicit_portfolio_membership(
    portfolio_id: str,
    portfolio_subject_id: str,
) -> ExplicitPortfolioMembership:
    return ExplicitPortfolioMembership(
        portfolio_id,
        portfolio_subject_id,
    )


def build_explicit_portfolio_position(
    position_id: str,
    membership: ExplicitPortfolioMembership,
) -> ExplicitPortfolioPosition:
    return ExplicitPortfolioPosition(position_id, membership)


def build_explicit_portfolio_holding_observation(
    position: ExplicitPortfolioPosition,
    observation_context: ExplicitPortfolioObservationContext,
    quantity: Decimal,
) -> ExplicitPortfolioHoldingObservation:
    return ExplicitPortfolioHoldingObservation(
        position,
        observation_context,
        quantity,
    )


def build_explicit_portfolio_holding_snapshot(
    observation_context: ExplicitPortfolioObservationContext,
    holding_observations: tuple[
        ExplicitPortfolioHoldingObservation,
        ...,
    ],
) -> ExplicitPortfolioHoldingSnapshot:
    return ExplicitPortfolioHoldingSnapshot(
        observation_context,
        holding_observations,
    )


def build_explicit_portfolio_watchlist_entry(
    membership: ExplicitPortfolioMembership,
) -> ExplicitPortfolioWatchlistEntry:
    return ExplicitPortfolioWatchlistEntry(membership)


def build_explicit_portfolio_snapshot(
    portfolio_snapshot_id: str,
    observation_context: ExplicitPortfolioObservationContext,
    holding_snapshot: ExplicitPortfolioHoldingSnapshot,
    watchlist_entries: tuple[
        ExplicitPortfolioWatchlistEntry,
        ...,
    ],
) -> ExplicitPortfolioSnapshot:
    return ExplicitPortfolioSnapshot(
        portfolio_snapshot_id,
        observation_context,
        holding_snapshot,
        watchlist_entries,
    )
