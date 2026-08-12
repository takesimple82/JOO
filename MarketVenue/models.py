from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitMarketVenue:
    venue_id: str
