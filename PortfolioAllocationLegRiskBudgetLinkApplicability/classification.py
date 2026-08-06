from PortfolioAllocationLeg.models import ExplicitPortfolioAllocationLeg
from PortfolioAllocationLeg.validation import (
    validate_explicit_portfolio_allocation_leg,
)
from PortfolioAllocationLegRiskBudgetLink.models import (
    ExplicitPortfolioAllocationLegRiskBudgetLink,
)
from PortfolioAllocationLegRiskBudgetLink.validation import (
    validate_explicit_portfolio_allocation_leg_risk_budget_link,
)
from PortfolioAllocationLegRiskBudgetLinkApplicability.models import (
    PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus,
)
from PortfolioCapitalBucket.models import ExplicitPortfolioCapitalBucket
from PortfolioCapitalBucket.validation import (
    validate_explicit_portfolio_capital_bucket,
)
from PortfolioPosition.models import ExplicitPortfolioPosition
from PortfolioPosition.validation import (
    validate_explicit_portfolio_position,
)
from PortfolioRiskBudget.models import ExplicitPortfolioRiskBudget
from PortfolioRiskBudget.validation import (
    validate_explicit_portfolio_risk_budget,
)


def classify_portfolio_allocation_leg_risk_budget_link_applicability(
    risk_budget_link: ExplicitPortfolioAllocationLegRiskBudgetLink,
    leg: ExplicitPortfolioAllocationLeg,
    risk_budget: ExplicitPortfolioRiskBudget,
    capital_bucket: ExplicitPortfolioCapitalBucket,
    position: ExplicitPortfolioPosition,
) -> PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus:
    validate_explicit_portfolio_allocation_leg_risk_budget_link(
        risk_budget_link
    )
    validate_explicit_portfolio_allocation_leg(leg)
    validate_explicit_portfolio_risk_budget(risk_budget)
    validate_explicit_portfolio_capital_bucket(capital_bucket)
    validate_explicit_portfolio_position(position)

    if risk_budget_link.allocation_leg_id != leg.allocation_leg_id:
        return (
            PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus
            .ALLOCATION_LEG_ENDPOINT_MISMATCH
        )
    if risk_budget_link.risk_budget_id != risk_budget.risk_budget_id:
        return (
            PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus
            .RISK_BUDGET_ENDPOINT_MISMATCH
        )
    if risk_budget.capital_bucket_id != capital_bucket.capital_bucket_id:
        return (
            PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus
            .CAPITAL_BUCKET_ENDPOINT_MISMATCH
        )
    if leg.link.position_id != position.position_id:
        return (
            PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus
            .POSITION_ENDPOINT_MISMATCH
        )
    if capital_bucket.portfolio_id != position.membership.portfolio_id:
        return (
            PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus
            .PORTFOLIO_ENDPOINT_MISMATCH
        )
    return PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus.APPLICABLE
