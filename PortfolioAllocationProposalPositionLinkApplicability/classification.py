from PortfolioAllocationProposalEndpoint.models import (
    ExplicitPortfolioAllocationProposalEndpoint,
)
from PortfolioAllocationProposalEndpoint.validation import (
    validate_explicit_portfolio_allocation_proposal_endpoint,
)
from PortfolioAllocationProposalPositionLink.models import (
    ExplicitPortfolioAllocationProposalPositionLink,
)
from PortfolioAllocationProposalPositionLink.validation import (
    validate_explicit_portfolio_allocation_proposal_position_link,
)
from PortfolioAllocationProposalPositionLinkApplicability.models import (
    PortfolioAllocationProposalPositionLinkApplicabilityStatus,
)
from PortfolioPosition.models import ExplicitPortfolioPosition
from PortfolioPosition.validation import (
    validate_explicit_portfolio_position,
)
from PortfolioRecommendationEndpoint.models import (
    ExplicitPortfolioRecommendationEndpoint,
)
from PortfolioRecommendationEndpoint.validation import (
    validate_explicit_portfolio_recommendation_endpoint,
)
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioSnapshot.validation import (
    validate_explicit_portfolio_snapshot,
)


def classify_portfolio_allocation_proposal_position_link_applicability(
    link: ExplicitPortfolioAllocationProposalPositionLink,
    proposal: ExplicitPortfolioAllocationProposalEndpoint,
    recommendation: ExplicitPortfolioRecommendationEndpoint,
    snapshot: ExplicitPortfolioSnapshot,
    position: ExplicitPortfolioPosition,
) -> PortfolioAllocationProposalPositionLinkApplicabilityStatus:
    validate_explicit_portfolio_allocation_proposal_position_link(link)
    validate_explicit_portfolio_allocation_proposal_endpoint(proposal)
    validate_explicit_portfolio_recommendation_endpoint(recommendation)
    validate_explicit_portfolio_snapshot(snapshot)
    validate_explicit_portfolio_position(position)

    if link.allocation_proposal_id != proposal.allocation_proposal_id:
        return (
            PortfolioAllocationProposalPositionLinkApplicabilityStatus
            .ALLOCATION_PROPOSAL_ENDPOINT_MISMATCH
        )
    if link.position_id != position.position_id:
        return (
            PortfolioAllocationProposalPositionLinkApplicabilityStatus
            .POSITION_ENDPOINT_MISMATCH
        )
    if proposal.recommendation_id != recommendation.recommendation_id:
        return (
            PortfolioAllocationProposalPositionLinkApplicabilityStatus
            .RECOMMENDATION_ENDPOINT_MISMATCH
        )
    if (
        recommendation.portfolio_snapshot_id
        != snapshot.portfolio_snapshot_id
    ):
        return (
            PortfolioAllocationProposalPositionLinkApplicabilityStatus
            .PORTFOLIO_SNAPSHOT_ENDPOINT_MISMATCH
        )
    if (
        position.membership.portfolio_id
        != snapshot.observation_context.portfolio_id
    ):
        return (
            PortfolioAllocationProposalPositionLinkApplicabilityStatus
            .PORTFOLIO_ENDPOINT_MISMATCH
        )
    return (
        PortfolioAllocationProposalPositionLinkApplicabilityStatus
        .APPLICABLE
    )
