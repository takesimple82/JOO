from dataclasses import dataclass

from PortfolioAllocationProposalPositionLink.models import (
    ExplicitPortfolioAllocationProposalPositionLink,
)


@dataclass(frozen=True)
class ExplicitPortfolioAllocationLeg:
    allocation_leg_id: str
    link: ExplicitPortfolioAllocationProposalPositionLink
