from decimal import Decimal

from ExpectedValueAssumptionSet.models import (
    ExplicitExpectedValueAssumptionSet,
    ExplicitExpectedValueOutcomeAssumption,
)
from SemanticPortfolioImpactProduction.models import (
    SemanticallyProducedPortfolioImpact,
)
from SemanticPortfolioImpactProduction.validation import (
    validate_semantically_produced_portfolio_impact,
)


def validate_explicit_expected_value_outcome_assumption(
    outcome: ExplicitExpectedValueOutcomeAssumption,
) -> None:
    if type(outcome) is not ExplicitExpectedValueOutcomeAssumption:
        raise TypeError(
            "outcome must be "
            "ExplicitExpectedValueOutcomeAssumption"
        )
    if type(outcome.outcome_id) is not str:
        raise TypeError("outcome_id must be str")
    if outcome.outcome_id.strip() == "":
        raise ValueError("outcome_id must not be blank")
    if type(outcome.statement) is not str:
        raise TypeError("statement must be str")
    if outcome.statement.strip() == "":
        raise ValueError("statement must not be blank")
    if type(outcome.probability) is not Decimal:
        raise TypeError("probability must be Decimal")
    if not outcome.probability.is_finite():
        raise ValueError("probability must be finite")
    if outcome.probability < Decimal("0"):
        raise ValueError("probability must be non-negative")
    if outcome.probability > Decimal("1"):
        raise ValueError("probability must not exceed 1")
    if type(outcome.value) is not Decimal:
        raise TypeError("value must be Decimal")
    if not outcome.value.is_finite():
        raise ValueError("value must be finite")


def validate_explicit_expected_value_assumption_set(
    assumption_set: ExplicitExpectedValueAssumptionSet,
) -> None:
    if type(assumption_set) is not ExplicitExpectedValueAssumptionSet:
        raise TypeError(
            "assumption_set must be "
            "ExplicitExpectedValueAssumptionSet"
        )
    if type(assumption_set.assumption_set_id) is not str:
        raise TypeError("assumption_set_id must be str")
    if assumption_set.assumption_set_id.strip() == "":
        raise ValueError(
            "assumption_set_id must not be blank"
        )
    if (
        type(assumption_set.impact)
        is not SemanticallyProducedPortfolioImpact
    ):
        raise TypeError(
            "impact must be "
            "SemanticallyProducedPortfolioImpact"
        )
    validate_semantically_produced_portfolio_impact(
        assumption_set.impact
    )
    if type(assumption_set.unit_id) is not str:
        raise TypeError("unit_id must be str")
    if assumption_set.unit_id.strip() == "":
        raise ValueError("unit_id must not be blank")
    if type(assumption_set.outcomes) is not tuple:
        raise TypeError("outcomes must be tuple")
    if not assumption_set.outcomes:
        raise ValueError("outcomes must not be empty")

    seen_outcome_ids = set()
    for outcome in assumption_set.outcomes:
        validate_explicit_expected_value_outcome_assumption(
            outcome
        )
        if outcome.outcome_id in seen_outcome_ids:
            raise ValueError(
                "outcome_id must not be duplicated"
            )
        seen_outcome_ids.add(outcome.outcome_id)
