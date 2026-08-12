from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitMarketSessionContext:
    session_context_id: str
    market_id: str
    venue_id: str
    session_profile_id: str
    timezone_id: str
    calendar_id: str
