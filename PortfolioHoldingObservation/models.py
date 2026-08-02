from dataclasses import dataclass
from decimal import Decimal

from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioPosition.models import ExplicitPortfolioPosition


@dataclass(frozen=True)
class ExplicitPortfolioHoldingObservation:
    position: ExplicitPortfolioPosition
    observation_context: ExplicitPortfolioObservationContext
    quantity: Decimal
