from PortfolioAllocationProposalPositionLink.models import (
    ExplicitPortfolioAllocationProposalPositionLink,
)


def validate_explicit_portfolio_allocation_proposal_position_link(
    link: ExplicitPortfolioAllocationProposalPositionLink,
) -> None:
    if type(link) is not ExplicitPortfolioAllocationProposalPositionLink:
        raise TypeError(
            "link must be "
            "ExplicitPortfolioAllocationProposalPositionLink"
        )
    if type(link.allocation_proposal_id) is not str:
        raise TypeError("allocation_proposal_id must be str")
    if link.allocation_proposal_id.strip() == "":
        raise ValueError("allocation_proposal_id must not be blank")
    if type(link.position_id) is not str:
        raise TypeError("position_id must be str")
    if link.position_id.strip() == "":
        raise ValueError("position_id must not be blank")
