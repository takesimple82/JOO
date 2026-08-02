from PortfolioRecommendationImpactLink.models import (
    ExplicitPortfolioRecommendationImpactLink,
)


def validate_explicit_portfolio_recommendation_impact_link(
    link: ExplicitPortfolioRecommendationImpactLink,
) -> None:
    if type(link) is not ExplicitPortfolioRecommendationImpactLink:
        raise TypeError(
            "link must be "
            "ExplicitPortfolioRecommendationImpactLink"
        )
    if type(link.recommendation_id) is not str:
        raise TypeError("recommendation_id must be str")
    if link.recommendation_id.strip() == "":
        raise ValueError(
            "recommendation_id must not be blank"
        )
    if type(link.impact_id) is not str:
        raise TypeError("impact_id must be str")
    if link.impact_id.strip() == "":
        raise ValueError("impact_id must not be blank")
