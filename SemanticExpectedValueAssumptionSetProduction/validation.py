from ExpectedValueAssumptionSet.models import (
    ExplicitExpectedValueAssumptionSet,
)
from ExpectedValueAssumptionSet.validation import (
    validate_explicit_expected_value_assumption_set,
)
from SemanticExpectedValueAssumptionSetProduction.models import (
    SemanticallyProducedExpectedValueAssumptionSet,
)


def validate_semantically_produced_expected_value_assumption_set(
    production: SemanticallyProducedExpectedValueAssumptionSet,
) -> None:
    if (
        type(production)
        is not SemanticallyProducedExpectedValueAssumptionSet
    ):
        raise TypeError(
            "production must be "
            "SemanticallyProducedExpectedValueAssumptionSet"
        )
    if (
        type(production.assumption_set)
        is not ExplicitExpectedValueAssumptionSet
    ):
        raise TypeError(
            "assumption_set must be "
            "ExplicitExpectedValueAssumptionSet"
        )
    validate_explicit_expected_value_assumption_set(
        production.assumption_set
    )
