import PortfolioImpactInterpretationPolicy._classification as _private

from PortfolioImpactInterpretationPolicy.models import (
    PortfolioImpactDirection,
    PortfolioImpactInterpretationPolicy,
    PortfolioImpactInterpretationPolicyApplicabilityStatus,
)
from PortfolioImpactInterpretationPolicy.validation import (
    validate_portfolio_impact_interpretation_policy,
)


def classify_portfolio_impact_interpretation_policy_applicability(
    policy: PortfolioImpactInterpretationPolicy,
    direction: PortfolioImpactDirection,
    horizon_id: str,
    rationale: str,
) -> PortfolioImpactInterpretationPolicyApplicabilityStatus:
    validate_portfolio_impact_interpretation_policy(policy)
    if type(direction) is not PortfolioImpactDirection:
        raise TypeError(
            "direction must be PortfolioImpactDirection"
        )
    if type(horizon_id) is not str:
        raise TypeError("horizon_id must be str")
    if horizon_id.strip() == "":
        raise ValueError("horizon_id must not be blank")
    if type(rationale) is not str:
        raise TypeError("rationale must be str")

    return (
        _private
        ._classify_portfolio_impact_interpretation_policy_applicability_unchecked(
            policy,
            direction,
            horizon_id,
            rationale,
        )
    )
