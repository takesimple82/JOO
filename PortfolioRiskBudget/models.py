from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolioRiskBudget:
    risk_budget_id: str
    capital_bucket_id: str
