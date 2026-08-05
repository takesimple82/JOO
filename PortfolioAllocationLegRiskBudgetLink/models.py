from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPortfolioAllocationLegRiskBudgetLink:
    allocation_leg_id: str
    risk_budget_id: str
