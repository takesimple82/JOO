from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolio:
    portfolio_id: str
