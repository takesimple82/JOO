from PortfolioImpactInterpretationPolicy.models import (
    PortfolioImpactDirection,
    PortfolioImpactInterpretationPolicy,
)


def validate_portfolio_impact_interpretation_policy(
    policy: PortfolioImpactInterpretationPolicy,
) -> None:
    if type(policy) is not PortfolioImpactInterpretationPolicy:
        raise TypeError(
            "policy must be PortfolioImpactInterpretationPolicy"
        )
    if type(policy.policy_id) is not str:
        raise TypeError("policy_id must be str")
    if policy.policy_id.strip() == "":
        raise ValueError("policy_id must not be blank")
    if type(policy.policy_version) is not str:
        raise TypeError("policy_version must be str")
    if policy.policy_version.strip() == "":
        raise ValueError("policy_version must not be blank")

    if type(policy.allowed_directions) is not tuple:
        raise TypeError("allowed_directions must be tuple")
    if not policy.allowed_directions:
        raise ValueError(
            "allowed_directions must not be empty"
        )
    seen_directions = set()
    for direction in policy.allowed_directions:
        if type(direction) is not PortfolioImpactDirection:
            raise TypeError(
                "allowed_directions must contain only "
                "PortfolioImpactDirection"
            )
        if direction in seen_directions:
            raise ValueError(
                "allowed_directions must not contain duplicates"
            )
        seen_directions.add(direction)

    if type(policy.allowed_horizon_ids) is not tuple:
        raise TypeError("allowed_horizon_ids must be tuple")
    if not policy.allowed_horizon_ids:
        raise ValueError(
            "allowed_horizon_ids must not be empty"
        )
    seen_horizon_ids = set()
    for horizon_id in policy.allowed_horizon_ids:
        if type(horizon_id) is not str:
            raise TypeError(
                "allowed_horizon_ids must contain only str"
            )
        if horizon_id.strip() == "":
            raise ValueError(
                "allowed_horizon_ids must not contain blank values"
            )
        if horizon_id in seen_horizon_ids:
            raise ValueError(
                "allowed_horizon_ids must not contain duplicates"
            )
        seen_horizon_ids.add(horizon_id)

    if type(policy.rationale_required) is not bool:
        raise TypeError("rationale_required must be bool")
