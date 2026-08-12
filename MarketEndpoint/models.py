from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitMarket:
    market_id: str
