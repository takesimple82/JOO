from PortfolioRecommendationAssumptionSetLink.models import (
    ExplicitPortfolioRecommendationAssumptionSetLink,
)


def validate_explicit_portfolio_recommendation_assumption_set_link(
    link: ExplicitPortfolioRecommendationAssumptionSetLink,
) -> None:
    if type(link) is not ExplicitPortfolioRecommendationAssumptionSetLink:
        raise TypeError(
            "link must be "
            "ExplicitPortfolioRecommendationAssumptionSetLink"
        )
    if type(link.recommendation_id) is not str:
        raise TypeError("recommendation_id must be str")
    if link.recommendation_id.strip() == "":
        raise ValueError("recommendation_id must not be blank")
    if type(link.assumption_set_id) is not str:
        raise TypeError("assumption_set_id must be str")
    if link.assumption_set_id.strip() == "":
        raise ValueError("assumption_set_id must not be blank")
