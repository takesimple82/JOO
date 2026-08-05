from PortfolioAllocationLegAssociationConsistencyApplicability.models import (
    PortfolioAllocationLegAssociationConsistencyApplicabilityStatus,
)
from PortfolioAllocationLegCapitalBucketLink.models import (
    ExplicitPortfolioAllocationLegCapitalBucketLink,
)
from PortfolioAllocationLegCapitalBucketLink.validation import (
    validate_explicit_portfolio_allocation_leg_capital_bucket_link,
)
from PortfolioAllocationLegRiskBudgetLink.models import (
    ExplicitPortfolioAllocationLegRiskBudgetLink,
)
from PortfolioAllocationLegRiskBudgetLink.validation import (
    validate_explicit_portfolio_allocation_leg_risk_budget_link,
)
from PortfolioRiskBudget.models import ExplicitPortfolioRiskBudget
from PortfolioRiskBudget.validation import (
    validate_explicit_portfolio_risk_budget,
)


def classify_portfolio_allocation_leg_association_consistency_applicability(
    capital_bucket_link: ExplicitPortfolioAllocationLegCapitalBucketLink,
    risk_budget_link: ExplicitPortfolioAllocationLegRiskBudgetLink,
    risk_budget: ExplicitPortfolioRiskBudget,
) -> PortfolioAllocationLegAssociationConsistencyApplicabilityStatus:
    validate_explicit_portfolio_allocation_leg_capital_bucket_link(
        capital_bucket_link
    )
    validate_explicit_portfolio_allocation_leg_risk_budget_link(
        risk_budget_link
    )
    validate_explicit_portfolio_risk_budget(risk_budget)

    if (
        capital_bucket_link.allocation_leg_id
        != risk_budget_link.allocation_leg_id
    ):
        return (
            PortfolioAllocationLegAssociationConsistencyApplicabilityStatus
            .ALLOCATION_LEG_ENDPOINT_MISMATCH
        )
    if risk_budget_link.risk_budget_id != risk_budget.risk_budget_id:
        return (
            PortfolioAllocationLegAssociationConsistencyApplicabilityStatus
            .RISK_BUDGET_ENDPOINT_MISMATCH
        )
    if capital_bucket_link.capital_bucket_id != risk_budget.capital_bucket_id:
        return (
            PortfolioAllocationLegAssociationConsistencyApplicabilityStatus
            .CAPITAL_BUCKET_ENDPOINT_MISMATCH
        )
    return (
        PortfolioAllocationLegAssociationConsistencyApplicabilityStatus
        .APPLICABLE
    )
