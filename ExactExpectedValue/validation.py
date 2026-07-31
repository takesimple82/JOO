from decimal import Decimal

from ExactExpectedValue.models import (
    ExactExpectedValue,
    ExactExpectedValueCalculation,
)
from ExpectedValueAssumptionSetApplicability.models import (
    ExpectedValueAssumptionSetApplicabilityStatus,
)
from SemanticExpectedValueAssumptionSetProduction.models import (
    SemanticallyProducedExpectedValueAssumptionSet,
)
from SemanticExpectedValueAssumptionSetProduction.validation import (
    validate_semantically_produced_expected_value_assumption_set,
)


def validate_exact_expected_value(
    expected_value: ExactExpectedValue,
) -> None:
    if type(expected_value) is not ExactExpectedValue:
        raise TypeError(
            "expected_value must be ExactExpectedValue"
        )
    if (
        type(expected_value.source)
        is not SemanticallyProducedExpectedValueAssumptionSet
    ):
        raise TypeError(
            "source must be "
            "SemanticallyProducedExpectedValueAssumptionSet"
        )
    validate_semantically_produced_expected_value_assumption_set(
        expected_value.source
    )
    if type(expected_value.value) is not Decimal:
        raise TypeError("value must be Decimal")
    if not expected_value.value.is_finite():
        raise ValueError("value must be finite")


def validate_exact_expected_value_calculation(
    calculation: ExactExpectedValueCalculation,
) -> None:
    if type(calculation) is not ExactExpectedValueCalculation:
        raise TypeError(
            "calculation must be "
            "ExactExpectedValueCalculation"
        )
    if (
        type(calculation.applicability_status)
        is not ExpectedValueAssumptionSetApplicabilityStatus
    ):
        raise TypeError(
            "applicability_status must be "
            "ExpectedValueAssumptionSetApplicabilityStatus"
        )

    if (
        calculation.applicability_status
        is ExpectedValueAssumptionSetApplicabilityStatus.APPLICABLE
    ):
        if type(calculation.expected_value) is not ExactExpectedValue:
            raise TypeError(
                "expected_value must be ExactExpectedValue "
                "when applicability_status is APPLICABLE"
            )
        validate_exact_expected_value(
            calculation.expected_value
        )
        return

    if calculation.expected_value is not None:
        raise ValueError(
            "expected_value must be None when "
            "applicability_status is "
            "PROBABILITY_TOTAL_MISMATCH"
        )
