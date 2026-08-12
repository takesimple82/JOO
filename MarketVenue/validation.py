from MarketVenue.models import ExplicitMarketVenue


def validate_explicit_market_venue(
    venue: ExplicitMarketVenue,
) -> None:
    if type(venue) is not ExplicitMarketVenue:
        raise TypeError(
            "venue must be ExplicitMarketVenue"
        )
    if type(venue.venue_id) is not str:
        raise TypeError("venue_id must be str")
    if venue.venue_id.strip() == "":
        raise ValueError(
            "venue_id must not be blank"
        )
