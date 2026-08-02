from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolioCapitalBucket:
    capital_bucket_id: str
    portfolio_id: str
