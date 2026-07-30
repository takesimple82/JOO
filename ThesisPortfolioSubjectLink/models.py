from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitThesisPortfolioSubjectLink:
    thesis_id: str
    portfolio_subject_id: str
