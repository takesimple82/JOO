from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolioRecommendationImpactLink:
    recommendation_id: str
    impact_id: str
