from ExactCrossContextNumericDelta.models import (
    ExactCrossContextNumericDelta,
)
from ExactCrossContextNumericDelta.validation import (
    validate_exact_cross_context_numeric_delta,
)
from ExactNumericDeltaMateriality.models import (
    ExactNumericDeltaMaterialityPolicy,
    ExactNumericDeltaMaterialityStatus,
)
from ExactNumericDeltaMateriality.validation import (
    validate_exact_numeric_delta_materiality_policy,
)


def classify_exact_numeric_delta_materiality(
    delta: ExactCrossContextNumericDelta,
    policy: ExactNumericDeltaMaterialityPolicy,
) -> ExactNumericDeltaMaterialityStatus:
    validate_exact_cross_context_numeric_delta(delta)
    validate_exact_numeric_delta_materiality_policy(policy)

    if delta.unit_id != policy.unit_id:
        return ExactNumericDeltaMaterialityStatus.UNIT_MISMATCH

    magnitude = delta.value.copy_abs()
    if magnitude > policy.threshold:
        return ExactNumericDeltaMaterialityStatus.MATERIAL
    return ExactNumericDeltaMaterialityStatus.IMMATERIAL
