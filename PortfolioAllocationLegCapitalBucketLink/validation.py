from PortfolioAllocationLegCapitalBucketLink.models import (
    ExplicitPortfolioAllocationLegCapitalBucketLink,
)


def validate_explicit_portfolio_allocation_leg_capital_bucket_link(
    link: ExplicitPortfolioAllocationLegCapitalBucketLink,
) -> None:
    if type(link) is not ExplicitPortfolioAllocationLegCapitalBucketLink:
        raise TypeError(
            "link must be ExplicitPortfolioAllocationLegCapitalBucketLink"
        )
    if type(link.allocation_leg_id) is not str:
        raise TypeError("allocation_leg_id must be str")
    if link.allocation_leg_id.strip() == "":
        raise ValueError("allocation_leg_id must not be blank")
    if type(link.capital_bucket_id) is not str:
        raise TypeError("capital_bucket_id must be str")
    if link.capital_bucket_id.strip() == "":
        raise ValueError("capital_bucket_id must not be blank")
