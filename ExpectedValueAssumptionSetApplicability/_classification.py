from decimal import Decimal

from ExactDecimalArithmetic.arithmetic import (
    add_exact_decimal,
)
from ExpectedValueAssumptionSet.models import (
    ExplicitExpectedValueAssumptionSet,
)
from ExpectedValueAssumptionSetApplicability.models import (
    ExpectedValueAssumptionSetApplicabilityStatus,
)


def _classify_expected_value_assumption_set_applicability_unchecked(
    assumption_set: ExplicitExpectedValueAssumptionSet,
) -> ExpectedValueAssumptionSetApplicabilityStatus:
    total = Decimal("0")
    for outcome in assumption_set.outcomes:
        total = add_exact_decimal(
            total,
            outcome.probability,
        )

    if total != Decimal("1"):
        return (
            ExpectedValueAssumptionSetApplicabilityStatus
            .PROBABILITY_TOTAL_MISMATCH
        )
    return (
        ExpectedValueAssumptionSetApplicabilityStatus
        .APPLICABLE
    )
