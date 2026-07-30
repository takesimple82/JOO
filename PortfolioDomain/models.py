from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioSubject:
    subject_id: str
    display_name: str
