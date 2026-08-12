from MarketSessionContext.models import (
    ExplicitMarketSessionContext,
)


def validate_explicit_market_session_context(
    context: ExplicitMarketSessionContext,
) -> None:
    if type(context) is not ExplicitMarketSessionContext:
        raise TypeError(
            "context must be "
            "ExplicitMarketSessionContext"
        )
    if type(context.session_context_id) is not str:
        raise TypeError(
            "session_context_id must be str"
        )
    if context.session_context_id.strip() == "":
        raise ValueError(
            "session_context_id must not be blank"
        )
    if type(context.market_id) is not str:
        raise TypeError("market_id must be str")
    if context.market_id.strip() == "":
        raise ValueError(
            "market_id must not be blank"
        )
    if type(context.venue_id) is not str:
        raise TypeError("venue_id must be str")
    if context.venue_id.strip() == "":
        raise ValueError(
            "venue_id must not be blank"
        )
    if type(context.session_profile_id) is not str:
        raise TypeError(
            "session_profile_id must be str"
        )
    if context.session_profile_id.strip() == "":
        raise ValueError(
            "session_profile_id must not be blank"
        )
    if type(context.timezone_id) is not str:
        raise TypeError("timezone_id must be str")
    if context.timezone_id.strip() == "":
        raise ValueError(
            "timezone_id must not be blank"
        )
    if type(context.calendar_id) is not str:
        raise TypeError("calendar_id must be str")
    if context.calendar_id.strip() == "":
        raise ValueError(
            "calendar_id must not be blank"
        )
