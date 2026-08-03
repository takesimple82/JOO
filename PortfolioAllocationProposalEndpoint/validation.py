from PortfolioAllocationProposalEndpoint.models import (
    ExplicitPortfolioAllocationProposalEndpoint,
)


def validate_explicit_portfolio_allocation_proposal_endpoint(
    endpoint: ExplicitPortfolioAllocationProposalEndpoint,
) -> None:
    if type(endpoint) is not ExplicitPortfolioAllocationProposalEndpoint:
        raise TypeError(
            "endpoint must be "
            "ExplicitPortfolioAllocationProposalEndpoint"
        )
    if type(endpoint.allocation_proposal_id) is not str:
        raise TypeError("allocation_proposal_id must be str")
    if endpoint.allocation_proposal_id.strip() == "":
        raise ValueError("allocation_proposal_id must not be blank")
    if type(endpoint.recommendation_id) is not str:
        raise TypeError("recommendation_id must be str")
    if endpoint.recommendation_id.strip() == "":
        raise ValueError("recommendation_id must not be blank")
