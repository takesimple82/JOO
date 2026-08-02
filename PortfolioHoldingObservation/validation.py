from decimal import Decimal

from PortfolioHoldingObservation.models import (
    ExplicitPortfolioHoldingObservation,
)
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioObservationContext.validation import (
    validate_explicit_portfolio_observation_context,
)
from PortfolioPosition.models import ExplicitPortfolioPosition
from PortfolioPosition.validation import (
    validate_explicit_portfolio_position,
)


def validate_explicit_portfolio_holding_observation(
    observation: ExplicitPortfolioHoldingObservation,
) -> None:
    if type(observation) is not ExplicitPortfolioHoldingObservation:
        raise TypeError(
            "observation must be "
            "ExplicitPortfolioHoldingObservation"
        )
    if type(observation.position) is not ExplicitPortfolioPosition:
        raise TypeError(
            "position must be ExplicitPortfolioPosition"
        )
    validate_explicit_portfolio_position(observation.position)
    if (
        type(observation.observation_context)
        is not ExplicitPortfolioObservationContext
    ):
        raise TypeError(
            "observation_context must be "
            "ExplicitPortfolioObservationContext"
        )
    validate_explicit_portfolio_observation_context(
        observation.observation_context
    )
    if (
        observation.position.membership.portfolio_id
        != observation.observation_context.portfolio_id
    ):
        raise ValueError(
            "position portfolio_id must match "
            "observation_context portfolio_id"
        )
    if type(observation.quantity) is not Decimal:
        raise TypeError("quantity must be Decimal")
    if not observation.quantity.is_finite():
        raise ValueError("quantity must be finite")
