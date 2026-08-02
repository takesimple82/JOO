from dataclasses import dataclass

from PortfolioHoldingObservation.models import (
    ExplicitPortfolioHoldingObservation,
)
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)


@dataclass(frozen=True)
class ExplicitPortfolioHoldingSnapshot:
    observation_context: ExplicitPortfolioObservationContext
    holding_observations: tuple[
        ExplicitPortfolioHoldingObservation,
        ...,
    ]
