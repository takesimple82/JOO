from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolioRecommendationAssumptionSetLink:
    recommendation_id: str
    assumption_set_id: str
