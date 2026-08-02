from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolioRecommendationEndpoint:
    recommendation_id: str
    portfolio_snapshot_id: str
