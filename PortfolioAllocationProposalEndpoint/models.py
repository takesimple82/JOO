from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolioAllocationProposalEndpoint:
    allocation_proposal_id: str
    recommendation_id: str
