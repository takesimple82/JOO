from PortfolioAllocationLeg.models import (
    ExplicitPortfolioAllocationLeg,
)
from PortfolioAllocationProposalPositionLink.models import (
    ExplicitPortfolioAllocationProposalPositionLink,
)
from PortfolioAllocationProposalPositionLink.validation import (
    validate_explicit_portfolio_allocation_proposal_position_link,
)


def validate_explicit_portfolio_allocation_leg(
    leg: ExplicitPortfolioAllocationLeg,
) -> None:
    if type(leg) is not ExplicitPortfolioAllocationLeg:
        raise TypeError("leg must be ExplicitPortfolioAllocationLeg")
    if type(leg.allocation_leg_id) is not str:
        raise TypeError("allocation_leg_id must be str")
    if leg.allocation_leg_id.strip() == "":
        raise ValueError("allocation_leg_id must not be blank")
    if type(leg.link) is not ExplicitPortfolioAllocationProposalPositionLink:
        raise TypeError(
            "link must be ExplicitPortfolioAllocationProposalPositionLink"
        )
    validate_explicit_portfolio_allocation_proposal_position_link(leg.link)
