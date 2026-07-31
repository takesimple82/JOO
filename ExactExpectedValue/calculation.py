from decimal import Decimal

import ExpectedValueAssumptionSetApplicability._classification as _private

from ExactDecimalArithmetic.arithmetic import (
    add_exact_decimal,
    multiply_exact_decimal,
)
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


def calculate_exact_expected_value(
    source: SemanticallyProducedExpectedValueAssumptionSet,
) -> ExactExpectedValueCalculation:
    validate_semantically_produced_expected_value_assumption_set(
        source
    )
    applicability_status = (
        _private
        ._classify_expected_value_assumption_set_applicability_unchecked(
            source.assumption_set
        )
    )
    if (
        applicability_status
        is ExpectedValueAssumptionSetApplicabilityStatus
        .PROBABILITY_TOTAL_MISMATCH
    ):
        return ExactExpectedValueCalculation(
            applicability_status=applicability_status,
            expected_value=None,
        )

    accumulator = Decimal("0")
    for outcome in source.assumption_set.outcomes:
        product = multiply_exact_decimal(
            outcome.probability,
            outcome.value,
        )
        accumulator = add_exact_decimal(
            accumulator,
            product,
        )

    expected_value = ExactExpectedValue(
        source=source,
        value=accumulator,
    )
    return ExactExpectedValueCalculation(
        applicability_status=applicability_status,
        expected_value=expected_value,
    )
