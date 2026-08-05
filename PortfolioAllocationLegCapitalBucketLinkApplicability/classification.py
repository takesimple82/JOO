from PortfolioAllocationLeg.models import ExplicitPortfolioAllocationLeg
from PortfolioAllocationLeg.validation import (
    validate_explicit_portfolio_allocation_leg,
)
from PortfolioAllocationLegCapitalBucketLink.models import (
    ExplicitPortfolioAllocationLegCapitalBucketLink,
)
from PortfolioAllocationLegCapitalBucketLink.validation import (
    validate_explicit_portfolio_allocation_leg_capital_bucket_link,
)
from PortfolioAllocationLegCapitalBucketLinkApplicability.models import (
    PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus,
)
from PortfolioCapitalBucket.models import ExplicitPortfolioCapitalBucket
from PortfolioCapitalBucket.validation import (
    validate_explicit_portfolio_capital_bucket,
)
from PortfolioPosition.models import ExplicitPortfolioPosition
from PortfolioPosition.validation import (
    validate_explicit_portfolio_position,
)


def classify_portfolio_allocation_leg_capital_bucket_link_applicability(
    capital_bucket_link: ExplicitPortfolioAllocationLegCapitalBucketLink,
    leg: ExplicitPortfolioAllocationLeg,
    capital_bucket: ExplicitPortfolioCapitalBucket,
    position: ExplicitPortfolioPosition,
) -> PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus:
    validate_explicit_portfolio_allocation_leg_capital_bucket_link(
        capital_bucket_link
    )
    validate_explicit_portfolio_allocation_leg(leg)
    validate_explicit_portfolio_capital_bucket(capital_bucket)
    validate_explicit_portfolio_position(position)

    if capital_bucket_link.allocation_leg_id != leg.allocation_leg_id:
        return (
            PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus
            .ALLOCATION_LEG_ENDPOINT_MISMATCH
        )
    if capital_bucket_link.capital_bucket_id != capital_bucket.capital_bucket_id:
        return (
            PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus
            .CAPITAL_BUCKET_ENDPOINT_MISMATCH
        )
    if leg.link.position_id != position.position_id:
        return (
            PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus
            .POSITION_ENDPOINT_MISMATCH
        )
    if capital_bucket.portfolio_id != position.membership.portfolio_id:
        return (
            PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus
            .PORTFOLIO_ENDPOINT_MISMATCH
        )
    return PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus.APPLICABLE
