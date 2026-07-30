from ExactCrossContextNumericDelta.models import (
    ExactCrossContextNumericDelta,
)
from ExactCrossContextNumericDelta.validation import (
    validate_exact_cross_context_numeric_delta,
)
from ExactCrossContextNumericDeltaDirection.models import (
    ExactCrossContextNumericDeltaDirectionStatus,
)


def classify_exact_cross_context_numeric_delta_direction(
    delta: ExactCrossContextNumericDelta,
) -> ExactCrossContextNumericDeltaDirectionStatus:
    validate_exact_cross_context_numeric_delta(delta)

    return (
        _classify_exact_cross_context_numeric_delta_direction_unchecked(
            delta
        )
    )


def _classify_exact_cross_context_numeric_delta_direction_unchecked(
    delta: ExactCrossContextNumericDelta,
) -> ExactCrossContextNumericDeltaDirectionStatus:
    if delta.value.is_zero():
        return ExactCrossContextNumericDeltaDirectionStatus.ZERO
    if delta.value.is_signed():
        return ExactCrossContextNumericDeltaDirectionStatus.NEGATIVE
    return ExactCrossContextNumericDeltaDirectionStatus.POSITIVE
