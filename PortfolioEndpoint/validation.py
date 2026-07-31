from PortfolioEndpoint.models import ExplicitPortfolio


def validate_explicit_portfolio(
    portfolio: ExplicitPortfolio,
) -> None:
    if type(portfolio) is not ExplicitPortfolio:
        raise TypeError(
            "portfolio must be ExplicitPortfolio"
        )
    if type(portfolio.portfolio_id) is not str:
        raise TypeError("portfolio_id must be str")
    if portfolio.portfolio_id.strip() == "":
        raise ValueError(
            "portfolio_id must not be blank"
        )
