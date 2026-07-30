import ExpectedValueAssumptionSetApplicability._classification as _private

from ExpectedValueAssumptionSet.models import (
    ExplicitExpectedValueAssumptionSet,
)
from ExpectedValueAssumptionSet.validation import (
    validate_explicit_expected_value_assumption_set,
)
from ExpectedValueAssumptionSetApplicability.models import (
    ExpectedValueAssumptionSetApplicabilityStatus,
)


def classify_expected_value_assumption_set_applicability(
    assumption_set: ExplicitExpectedValueAssumptionSet,
) -> ExpectedValueAssumptionSetApplicabilityStatus:
    validate_explicit_expected_value_assumption_set(
        assumption_set
    )
    return (
        _private
        ._classify_expected_value_assumption_set_applicability_unchecked(
            assumption_set
        )
    )
