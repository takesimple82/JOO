from PortfolioRiskBudget.models import (
    ExplicitPortfolioRiskBudget,
)


def validate_explicit_portfolio_risk_budget(
    risk_budget: ExplicitPortfolioRiskBudget,
) -> None:
    if type(risk_budget) is not ExplicitPortfolioRiskBudget:
        raise TypeError(
            "risk_budget must be ExplicitPortfolioRiskBudget"
        )
    if type(risk_budget.risk_budget_id) is not str:
        raise TypeError("risk_budget_id must be str")
    if risk_budget.risk_budget_id.strip() == "":
        raise ValueError("risk_budget_id must not be blank")
    if type(risk_budget.capital_bucket_id) is not str:
        raise TypeError("capital_bucket_id must be str")
    if risk_budget.capital_bucket_id.strip() == "":
        raise ValueError(
            "capital_bucket_id must not be blank"
        )
