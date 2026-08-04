from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolioAllocationLegCapitalBucketLink:
    allocation_leg_id: str
    capital_bucket_id: str
