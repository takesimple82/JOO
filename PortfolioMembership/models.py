from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolioMembership:
    portfolio_id: str
    portfolio_subject_id: str
