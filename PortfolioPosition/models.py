from dataclasses import dataclass

from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)


@dataclass(frozen=True)
class ExplicitPortfolioPosition:
    position_id: str
    membership: ExplicitPortfolioMembership
