import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from decimal import Decimal
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from ExpectedValueAssumptionSet.models import (
    ExplicitExpectedValueAssumptionSet,
    ExplicitExpectedValueOutcomeAssumption,
)
from ExpectedValueAssumptionSet.validation import (
    validate_explicit_expected_value_assumption_set,
    validate_explicit_expected_value_outcome_assumption,
)
from ExplicitPortfolioImpact.models import (
    ExplicitPortfolioImpact,
)
from ExplicitThesis.models import ExplicitThesis
from PortfolioDomain.models import PortfolioSubject
from PortfolioImpactInterpretationPolicy.models import (
    PortfolioImpactDirection,
    PortfolioImpactInterpretationPolicy,
)
from SemanticPortfolioImpactProduction.models import (
    SemanticallyProducedPortfolioImpact,
)
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)
from ThesisPortfolioSubjectLink.models import (
    ExplicitThesisPortfolioSubjectLink,
)


def make_semantic_impact():
    thesis = SemanticallyProducedThesis(
        ExplicitThesis("thesis-001", "A semantic Thesis.")
    )
    link = ExplicitThesisPortfolioSubjectLink(
        "thesis-001",
        "subject-001",
    )
    subject = PortfolioSubject(
        "subject-001",
        "Subject One",
    )
    policy = PortfolioImpactInterpretationPolicy(
        "policy-001",
        "version-001",
        (PortfolioImpactDirection.BENEFICIAL,),
        ("long-term",),
        True,
    )
    return SemanticallyProducedPortfolioImpact(
        ExplicitPortfolioImpact(
            "impact-001",
            thesis,
            link,
            subject,
            policy,
            PortfolioImpactDirection.BENEFICIAL,
            "long-term",
            "Rationale.",
        )
    )


def make_outcome(**overrides):
    values = {
        "outcome_id": "outcome-001",
        "statement": "An explicit outcome assumption.",
        "probability": Decimal("0.5"),
        "value": Decimal("10"),
    }
    values.update(overrides)
    return ExplicitExpectedValueOutcomeAssumption(**values)


def make_set(**overrides):
    values = {
        "assumption_set_id": "assumptions-001",
        "impact": make_semantic_impact(),
        "unit_id": "USD",
        "outcomes": (
            make_outcome(),
            make_outcome(
                outcome_id="outcome-002",
                probability=Decimal("0.5"),
                value=Decimal("-4"),
            ),
        ),
    }
    values.update(overrides)
    return ExplicitExpectedValueAssumptionSet(**values)


class StringSubclass(str):
    pass


class TupleSubclass(tuple):
    pass


class OutcomeSubclass(ExplicitExpectedValueOutcomeAssumption):
    pass


class AssumptionSetSubclass(ExplicitExpectedValueAssumptionSet):
    pass


class ExpectedValueAssumptionSetTests(unittest.TestCase):
    def test_exact_model_contracts(self):
        outcome_fields = fields(
            ExplicitExpectedValueOutcomeAssumption
        )
        set_fields = fields(ExplicitExpectedValueAssumptionSet)
        self.assertEqual(
            [field.name for field in outcome_fields],
            ["outcome_id", "statement", "probability", "value"],
        )
        self.assertEqual(
            [field.name for field in set_fields],
            [
                "assumption_set_id",
                "impact",
                "unit_id",
                "outcomes",
            ],
        )
        self.assertEqual(
            get_type_hints(
                ExplicitExpectedValueOutcomeAssumption
            ),
            {
                "outcome_id": str,
                "statement": str,
                "probability": Decimal,
                "value": Decimal,
            },
        )
        self.assertEqual(
            get_type_hints(ExplicitExpectedValueAssumptionSet),
            {
                "assumption_set_id": str,
                "impact": SemanticallyProducedPortfolioImpact,
                "unit_id": str,
                "outcomes": tuple[
                    ExplicitExpectedValueOutcomeAssumption,
                    ...,
                ],
            },
        )
        for field in (*outcome_fields, *set_fields):
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)

    def test_models_are_frozen_hashable_and_structural(self):
        outcome = make_outcome()
        same_outcome = make_outcome()
        assumption_set = make_set()
        same_set = make_set()
        self.assertEqual(outcome, same_outcome)
        self.assertEqual(hash(outcome), hash(same_outcome))
        self.assertEqual(assumption_set, same_set)
        self.assertEqual(hash(assumption_set), hash(same_set))
        with self.assertRaises(FrozenInstanceError):
            outcome.outcome_id = "replacement"
        with self.assertRaises(FrozenInstanceError):
            assumption_set.unit_id = "replacement"

    def test_exact_outcome_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "^outcome must be "
            "ExplicitExpectedValueOutcomeAssumption$",
        ):
            validate_explicit_expected_value_outcome_assumption(
                OutcomeSubclass(
                    "outcome",
                    "statement",
                    Decimal("0.5"),
                    Decimal("1"),
                )
            )

    def test_outcome_string_validation_order(self):
        cases = (
            (
                make_outcome(outcome_id=None, statement=None),
                TypeError,
                "outcome_id must be str",
            ),
            (
                make_outcome(outcome_id=" ", statement=None),
                ValueError,
                "outcome_id must not be blank",
            ),
            (
                make_outcome(statement=None),
                TypeError,
                "statement must be str",
            ),
            (
                make_outcome(statement=" "),
                ValueError,
                "statement must not be blank",
            ),
            (
                make_outcome(
                    outcome_id=StringSubclass("outcome")
                ),
                TypeError,
                "outcome_id must be str",
            ),
            (
                make_outcome(
                    statement=StringSubclass("statement")
                ),
                TypeError,
                "statement must be str",
            ),
        )
        for outcome, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_expected_value_outcome_assumption(
                        outcome
                    )

    def test_probability_validation_order_and_bounds(self):
        cases = (
            (
                None,
                TypeError,
                "probability must be Decimal",
            ),
            (
                Decimal("NaN"),
                ValueError,
                "probability must be finite",
            ),
            (
                Decimal("-0.0001"),
                ValueError,
                "probability must be non-negative",
            ),
            (
                Decimal("1.0001"),
                ValueError,
                "probability must not exceed 1",
            ),
        )
        for value, error_type, message in cases:
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_expected_value_outcome_assumption(
                        make_outcome(probability=value)
                    )

    def test_probability_inclusive_bounds(self):
        for value in (
            Decimal("0"),
            Decimal("-0"),
            Decimal("1"),
            Decimal("1.000"),
        ):
            with self.subTest(value=value):
                self.assertIsNone(
                    validate_explicit_expected_value_outcome_assumption(
                        make_outcome(probability=value)
                    )
                )

    def test_value_requires_exact_finite_decimal(self):
        cases = (
            (
                None,
                TypeError,
                "value must be Decimal",
            ),
            (
                Decimal("Infinity"),
                ValueError,
                "value must be finite",
            ),
            (
                Decimal("NaN"),
                ValueError,
                "value must be finite",
            ),
        )
        for value, error_type, message in cases:
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_expected_value_outcome_assumption(
                        make_outcome(value=value)
                    )
        for value in (
            Decimal("-10"),
            Decimal("-0"),
            Decimal("0"),
            Decimal("10"),
        ):
            self.assertIsNone(
                validate_explicit_expected_value_outcome_assumption(
                    make_outcome(value=value)
                )
            )

    def test_exact_assumption_set_type_and_fields(self):
        valid = make_set()
        subclass = AssumptionSetSubclass(
            valid.assumption_set_id,
            valid.impact,
            valid.unit_id,
            valid.outcomes,
        )
        with self.assertRaisesRegex(
            TypeError,
            "^assumption_set must be "
            "ExplicitExpectedValueAssumptionSet$",
        ):
            validate_explicit_expected_value_assumption_set(
                subclass
            )
        cases = (
            (
                make_set(assumption_set_id=None),
                TypeError,
                "assumption_set_id must be str",
            ),
            (
                make_set(assumption_set_id=" "),
                ValueError,
                "assumption_set_id must not be blank",
            ),
            (
                make_set(impact=None),
                TypeError,
                "impact must be "
                "SemanticallyProducedPortfolioImpact",
            ),
            (
                make_set(unit_id=None),
                TypeError,
                "unit_id must be str",
            ),
            (
                make_set(unit_id=" "),
                ValueError,
                "unit_id must not be blank",
            ),
        )
        for assumption_set, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_expected_value_assumption_set(
                        assumption_set
                    )

    def test_outcomes_require_exact_nonempty_tuple(self):
        invalid = (
            None,
            [],
            set(),
            (item for item in ()),
            TupleSubclass((make_outcome(),)),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^outcomes must be tuple$",
                ):
                    validate_explicit_expected_value_assumption_set(
                        make_set(outcomes=value)
                    )
        with self.assertRaisesRegex(
            ValueError,
            "^outcomes must not be empty$",
        ):
            validate_explicit_expected_value_assumption_set(
                make_set(outcomes=())
            )

    def test_impact_and_outcomes_validated_once_in_order(self):
        impact = make_semantic_impact()
        first = make_outcome(outcome_id="first")
        second = make_outcome(outcome_id="second")
        assumption_set = make_set(
            impact=impact,
            outcomes=(first, second),
        )
        calls = []
        with patch(
            "ExpectedValueAssumptionSet.validation"
            ".validate_semantically_produced_portfolio_impact",
            side_effect=lambda value: calls.append(
                ("impact", value)
            ),
        ) as impact_validator, patch(
            "ExpectedValueAssumptionSet.validation"
            ".validate_explicit_expected_value_outcome_assumption",
            side_effect=lambda value: calls.append(
                ("outcome", value)
            ),
        ) as outcome_validator:
            result = (
                validate_explicit_expected_value_assumption_set(
                    assumption_set
                )
            )
        self.assertIsNone(result)
        self.assertEqual(
            calls,
            [
                ("impact", impact),
                ("outcome", first),
                ("outcome", second),
            ],
        )
        impact_validator.assert_called_once_with(impact)
        self.assertEqual(outcome_validator.call_count, 2)

    def test_upstream_exception_propagates_unchanged(self):
        error = ValueError("impact failure")
        with patch(
            "ExpectedValueAssumptionSet.validation"
            ".validate_semantically_produced_portfolio_impact",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                validate_explicit_expected_value_assumption_set(
                    make_set()
                )
        self.assertIs(context.exception, error)

    def test_duplicate_rejected_after_duplicate_is_validated(self):
        first = make_outcome(outcome_id="duplicate")
        duplicate = make_outcome(outcome_id="duplicate")
        later = make_outcome(outcome_id="later")
        calls = []
        with patch(
            "ExpectedValueAssumptionSet.validation"
            ".validate_explicit_expected_value_outcome_assumption",
            side_effect=lambda value: calls.append(value),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "^outcome_id must not be duplicated$",
            ):
                validate_explicit_expected_value_assumption_set(
                    make_set(
                        outcomes=(first, duplicate, later)
                    )
                )
        self.assertEqual(calls, [first, duplicate])

    def test_probability_total_is_not_checked(self):
        for probabilities in (
            (Decimal("0.2"), Decimal("0.3")),
            (Decimal("0.8"), Decimal("0.8")),
        ):
            outcomes = tuple(
                make_outcome(
                    outcome_id=f"outcome-{index}",
                    probability=probability,
                )
                for index, probability in enumerate(
                    probabilities
                )
            )
            self.assertIsNone(
                validate_explicit_expected_value_assumption_set(
                    make_set(outcomes=outcomes)
                )
            )

    def test_identity_and_order_preservation(self):
        assumption_set_id = " assumptions-\u00e9 "
        unit_id = " unit-e\u0301 "
        outcome_id = " outcome-\u00e9 "
        statement = " statement-e\u0301 "
        probability = Decimal("0.2500")
        value = Decimal("-12.50")
        outcome = ExplicitExpectedValueOutcomeAssumption(
            outcome_id,
            statement,
            probability,
            value,
        )
        outcomes = (outcome,)
        impact = make_semantic_impact()
        assumption_set = ExplicitExpectedValueAssumptionSet(
            assumption_set_id,
            impact,
            unit_id,
            outcomes,
        )
        self.assertIsNone(
            validate_explicit_expected_value_assumption_set(
                assumption_set
            )
        )
        self.assertIs(
            assumption_set.assumption_set_id,
            assumption_set_id,
        )
        self.assertIs(assumption_set.impact, impact)
        self.assertIs(assumption_set.unit_id, unit_id)
        self.assertIs(assumption_set.outcomes, outcomes)
        self.assertIs(assumption_set.outcomes[0], outcome)
        self.assertIs(outcome.outcome_id, outcome_id)
        self.assertIs(outcome.statement, statement)
        self.assertIs(outcome.probability, probability)
        self.assertIs(outcome.value, value)

    def test_dependency_direction_and_public_surface(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (root / "models.py").read_text()
        )
        validation_tree = ast.parse(
            (root / "validation.py").read_text()
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_expected_value_outcome_assumption",
                "validate_explicit_expected_value_assumption_set",
            ],
        )
        imported_modules = {
            node.module
            for tree in (model_tree, validation_tree)
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            imported_modules,
            {
                "dataclasses",
                "decimal",
                "ExpectedValueAssumptionSet.models",
                "SemanticPortfolioImpactProduction.models",
                "SemanticPortfolioImpactProduction.validation",
            },
        )


if __name__ == "__main__":
    unittest.main()
