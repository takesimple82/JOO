from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolioObservationContext:
    observation_context_id: str
    portfolio_id: str
