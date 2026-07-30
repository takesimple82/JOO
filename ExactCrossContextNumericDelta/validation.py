from decimal import Decimal

from ExactCrossContextNumericDelta.models import (
    ExactCrossContextNumericDelta,
    ExactCrossContextNumericDeltaCalculation,
)
from ExactCrossContextNumericDeltaApplicability.models import (
    ExactCrossContextNumericDeltaApplicabilityStatus,
)


def validate_exact_cross_context_numeric_delta(
    delta: ExactCrossContextNumericDelta,
) -> None:
    if type(delta) is not ExactCrossContextNumericDelta:
        raise TypeError(
            "delta must be ExactCrossContextNumericDelta"
        )
    _validate_identifier(
        "baseline_proposition_id",
        delta.baseline_proposition_id,
    )
    _validate_identifier(
        "current_proposition_id",
        delta.current_proposition_id,
    )
    _validate_identifier("unit_id", delta.unit_id)
    if type(delta.value) is not Decimal:
        raise TypeError("value must be Decimal")
    if not delta.value.is_finite():
        raise ValueError("value must be finite")


def validate_exact_cross_context_numeric_delta_calculation(
    calculation: ExactCrossContextNumericDeltaCalculation,
) -> None:
    if type(calculation) is not ExactCrossContextNumericDeltaCalculation:
        raise TypeError(
            "calculation must be "
            "ExactCrossContextNumericDeltaCalculation"
        )
    if (
        type(calculation.applicability_status)
        is not ExactCrossContextNumericDeltaApplicabilityStatus
    ):
        raise TypeError(
            "applicability_status must be "
            "ExactCrossContextNumericDeltaApplicabilityStatus"
        )

    if (
        calculation.applicability_status
        is ExactCrossContextNumericDeltaApplicabilityStatus.CALCULABLE
    ):
        if type(calculation.delta) is not ExactCrossContextNumericDelta:
            raise TypeError(
                "delta must be ExactCrossContextNumericDelta "
                "when applicability_status is CALCULABLE"
            )
        validate_exact_cross_context_numeric_delta(
            calculation.delta
        )
        return

    if calculation.delta is not None:
        raise ValueError(
            "delta must be None when applicability_status "
            "is not CALCULABLE"
        )


def _validate_identifier(name: str, value: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{name} must be str")
    if value.strip() == "":
        raise ValueError(f"{name} must not be blank")
