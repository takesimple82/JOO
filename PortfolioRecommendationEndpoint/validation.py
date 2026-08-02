from PortfolioRecommendationEndpoint.models import (
    ExplicitPortfolioRecommendationEndpoint,
)


def validate_explicit_portfolio_recommendation_endpoint(
    endpoint: ExplicitPortfolioRecommendationEndpoint,
) -> None:
    if type(endpoint) is not ExplicitPortfolioRecommendationEndpoint:
        raise TypeError(
            "endpoint must be "
            "ExplicitPortfolioRecommendationEndpoint"
        )
    if type(endpoint.recommendation_id) is not str:
        raise TypeError("recommendation_id must be str")
    if endpoint.recommendation_id.strip() == "":
        raise ValueError(
            "recommendation_id must not be blank"
        )
    if type(endpoint.portfolio_snapshot_id) is not str:
        raise TypeError("portfolio_snapshot_id must be str")
    if endpoint.portfolio_snapshot_id.strip() == "":
        raise ValueError(
            "portfolio_snapshot_id must not be blank"
        )
