from PortfolioHoldingObservation.models import (
    ExplicitPortfolioHoldingObservation,
)
from PortfolioHoldingObservation.validation import (
    validate_explicit_portfolio_holding_observation,
)
from PortfolioHoldingSnapshot.models import (
    ExplicitPortfolioHoldingSnapshot,
)
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioObservationContext.validation import (
    validate_explicit_portfolio_observation_context,
)


def validate_explicit_portfolio_holding_snapshot(
    snapshot: ExplicitPortfolioHoldingSnapshot,
) -> None:
    if type(snapshot) is not ExplicitPortfolioHoldingSnapshot:
        raise TypeError(
            "snapshot must be "
            "ExplicitPortfolioHoldingSnapshot"
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
    if type(snapshot.holding_observations) is not tuple:
        raise TypeError("holding_observations must be tuple")

    position_ids = set()
    for observation in snapshot.holding_observations:
        if (
            type(observation)
            is not ExplicitPortfolioHoldingObservation
        ):
            raise TypeError(
                "holding_observations must contain only "
                "ExplicitPortfolioHoldingObservation"
            )
        validate_explicit_portfolio_holding_observation(
            observation
        )
        if (
            observation.observation_context.observation_context_id
            != snapshot.observation_context.observation_context_id
        ):
            raise ValueError(
                "observation_context_id must match the snapshot "
                "observation_context_id"
            )
        if (
            observation.observation_context.portfolio_id
            != snapshot.observation_context.portfolio_id
        ):
            raise ValueError(
                "portfolio_id must match the snapshot "
                "portfolio_id"
            )
        position_id = observation.position.position_id
        if position_id in position_ids:
            raise ValueError(
                "holding_observations must not contain "
                "duplicate position_id"
            )
        position_ids.add(position_id)
