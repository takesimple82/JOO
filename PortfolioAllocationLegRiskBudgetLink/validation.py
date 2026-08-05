from PortfolioAllocationLegRiskBudgetLink.models import (
    ExplicitPortfolioAllocationLegRiskBudgetLink,
)


def validate_explicit_portfolio_allocation_leg_risk_budget_link(
    link: ExplicitPortfolioAllocationLegRiskBudgetLink,
) -> None:
    if type(link) is not ExplicitPortfolioAllocationLegRiskBudgetLink:
        raise TypeError(
            "link must be ExplicitPortfolioAllocationLegRiskBudgetLink"
        )
    if type(link.allocation_leg_id) is not str:
        raise TypeError("allocation_leg_id must be str")
    if link.allocation_leg_id.strip() == "":
        raise ValueError("allocation_leg_id must not be blank")
    if type(link.risk_budget_id) is not str:
        raise TypeError("risk_budget_id must be str")
    if link.risk_budget_id.strip() == "":
        raise ValueError("risk_budget_id must not be blank")
