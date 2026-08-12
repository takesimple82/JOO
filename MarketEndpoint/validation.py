from MarketEndpoint.models import ExplicitMarket


def validate_explicit_market(
    market: ExplicitMarket,
) -> None:
    if type(market) is not ExplicitMarket:
        raise TypeError(
            "market must be ExplicitMarket"
        )
    if type(market.market_id) is not str:
        raise TypeError("market_id must be str")
    if market.market_id.strip() == "":
        raise ValueError(
            "market_id must not be blank"
        )
