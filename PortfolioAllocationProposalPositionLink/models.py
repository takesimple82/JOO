from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolioAllocationProposalPositionLink:
    allocation_proposal_id: str
    position_id: str
