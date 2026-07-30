from decimal import Decimal

from ExactNumericDeltaMateriality.models import (
    ExactNumericDeltaMaterialityPolicy,
)


def validate_exact_numeric_delta_materiality_policy(
    policy: ExactNumericDeltaMaterialityPolicy,
) -> None:
    if type(policy) is not ExactNumericDeltaMaterialityPolicy:
        raise TypeError(
            "policy must be ExactNumericDeltaMaterialityPolicy"
        )
    if type(policy.unit_id) is not str:
        raise TypeError("unit_id must be str")
    if policy.unit_id.strip() == "":
        raise ValueError("unit_id must not be blank")
    if type(policy.threshold) is not Decimal:
        raise TypeError("threshold must be Decimal")
    if not policy.threshold.is_finite():
        raise ValueError("threshold must be finite")
    if (
        policy.threshold.is_signed()
        and not policy.threshold.is_zero()
    ):
        raise ValueError("threshold must be non-negative")
