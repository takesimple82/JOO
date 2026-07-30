from PortfolioImpactInterpretationPolicy.models import (
    PortfolioImpactDirection,
    PortfolioImpactInterpretationPolicy,
    PortfolioImpactInterpretationPolicyApplicabilityStatus,
)


def _classify_portfolio_impact_interpretation_policy_applicability_unchecked(
    policy: PortfolioImpactInterpretationPolicy,
    direction: PortfolioImpactDirection,
    horizon_id: str,
    rationale: str,
) -> PortfolioImpactInterpretationPolicyApplicabilityStatus:
    if direction not in policy.allowed_directions:
        return (
            PortfolioImpactInterpretationPolicyApplicabilityStatus
            .DIRECTION_NOT_ALLOWED
        )
    if horizon_id not in policy.allowed_horizon_ids:
        return (
            PortfolioImpactInterpretationPolicyApplicabilityStatus
            .HORIZON_NOT_ALLOWED
        )
    if policy.rationale_required and rationale.strip() == "":
        return (
            PortfolioImpactInterpretationPolicyApplicabilityStatus
            .RATIONALE_REQUIRED
        )
    return (
        PortfolioImpactInterpretationPolicyApplicabilityStatus
        .APPLICABLE
    )
