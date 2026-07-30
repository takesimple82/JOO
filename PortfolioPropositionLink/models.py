from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPropositionPortfolioSubjectLink:
    proposition_id: str
    portfolio_subject_id: str
