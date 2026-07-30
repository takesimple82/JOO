import ast
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from ExpectedValueAssumptionSet.models import (
    ExplicitExpectedValueAssumptionSet,
    ExplicitExpectedValueOutcomeAssumption,
)
from ExpectedValueAssumptionSetApplicability.classification import (
    classify_expected_value_assumption_set_applicability,
)
from ExpectedValueAssumptionSetApplicability.models import (
    ExpectedValueAssumptionSetApplicabilityStatus,
)


def make_outcome(identifier, probability):
    return ExplicitExpectedValueOutcomeAssumption(
        identifier,
        f"Outcome {identifier}.",
        probability,
        Decimal("1"),
    )


def make_set(probabilities):
    return ExplicitExpectedValueAssumptionSet(
        "assumptions-001",
        None,
        "USD",
        tuple(
            make_outcome(
                f"outcome-{index}",
                probability,
            )
            for index, probability in enumerate(probabilities)
        ),
    )


class ExpectedValueAssumptionSetApplicabilityTests(
    unittest.TestCase
):
    def test_exact_status_contract(self):
        self.assertEqual(
            [
                status.value
                for status in
                ExpectedValueAssumptionSetApplicabilityStatus
            ],
            [
                "probability_total_mismatch",
                "applicable",
            ],
        )

    def test_exact_total_is_applicable(self):
        cases = (
            (Decimal("1"),),
            (Decimal("0.5"), Decimal("0.5")),
            (
                Decimal("0.10"),
                Decimal("0.20"),
                Decimal("0.700"),
            ),
            (Decimal("-0"), Decimal("1.000")),
        )
        for probabilities in cases:
            with self.subTest(probabilities=probabilities):
                with patch(
                    "ExpectedValueAssumptionSetApplicability"
                    ".classification"
                    ".validate_explicit_expected_value_assumption_set",
                ):
                    self.assertIs(
                        classify_expected_value_assumption_set_applicability(
                            make_set(probabilities)
                        ),
                        ExpectedValueAssumptionSetApplicabilityStatus
                        .APPLICABLE,
                    )

    def test_non_unit_total_is_mismatch(self):
        for probabilities in (
            (Decimal("0.9"),),
            (Decimal("0.8"), Decimal("0.3")),
            (Decimal("0"),),
        ):
            with self.subTest(probabilities=probabilities):
                with patch(
                    "ExpectedValueAssumptionSetApplicability"
                    ".classification"
                    ".validate_explicit_expected_value_assumption_set",
                ):
                    self.assertIs(
                        classify_expected_value_assumption_set_applicability(
                            make_set(probabilities)
                        ),
                        ExpectedValueAssumptionSetApplicabilityStatus
                        .PROBABILITY_TOTAL_MISMATCH,
                    )

    def test_upstream_validator_once_and_exception_identity(self):
        assumption_set = make_set((Decimal("1"),))
        with patch(
            "ExpectedValueAssumptionSetApplicability"
            ".classification"
            ".validate_explicit_expected_value_assumption_set",
        ) as validator:
            result = (
                classify_expected_value_assumption_set_applicability(
                    assumption_set
                )
            )
        self.assertIs(
            result,
            ExpectedValueAssumptionSetApplicabilityStatus
            .APPLICABLE,
        )
        validator.assert_called_once_with(assumption_set)

        error = ValueError("assumption failure")
        with patch(
            "ExpectedValueAssumptionSetApplicability"
            ".classification"
            ".validate_explicit_expected_value_assumption_set",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                classify_expected_value_assumption_set_applicability(
                    assumption_set
                )
        self.assertIs(context.exception, error)

    def test_probabilities_added_in_caller_order(self):
        probabilities = (
            Decimal("0.2"),
            Decimal("0.3"),
            Decimal("0.5"),
        )
        assumption_set = make_set(probabilities)
        calls = []
        totals = (
            Decimal("0.2"),
            Decimal("0.5"),
            Decimal("1"),
        )

        def add(augend, addend):
            calls.append((augend, addend))
            return totals[len(calls) - 1]

        with patch(
            "ExpectedValueAssumptionSetApplicability"
            ".classification"
            ".validate_explicit_expected_value_assumption_set",
        ), patch(
            "ExpectedValueAssumptionSetApplicability"
            "._classification.add_exact_decimal",
            side_effect=add,
        ) as arithmetic:
            classify_expected_value_assumption_set_applicability(
                assumption_set
            )

        self.assertEqual(
            [call[1] for call in calls],
            list(probabilities),
        )
        self.assertEqual(arithmetic.call_count, 3)

    def test_inputs_and_probability_objects_are_preserved(self):
        first_probability = Decimal("0.400")
        second_probability = Decimal("0.600")
        assumption_set = make_set(
            (first_probability, second_probability)
        )
        outcomes = assumption_set.outcomes
        with patch(
            "ExpectedValueAssumptionSetApplicability"
            ".classification"
            ".validate_explicit_expected_value_assumption_set",
        ):
            result = (
                classify_expected_value_assumption_set_applicability(
                    assumption_set
                )
            )
        self.assertIs(
            result,
            ExpectedValueAssumptionSetApplicabilityStatus
            .APPLICABLE,
        )
        self.assertIs(assumption_set.outcomes, outcomes)
        self.assertIs(
            assumption_set.outcomes[0].probability,
            first_probability,
        )
        self.assertIs(
            assumption_set.outcomes[1].probability,
            second_probability,
        )

    def test_public_classifier_delegates_to_private_helper(self):
        assumption_set = make_set((Decimal("1"),))
        with patch(
            "ExpectedValueAssumptionSetApplicability"
            ".classification"
            ".validate_explicit_expected_value_assumption_set",
        ), patch(
            "ExpectedValueAssumptionSetApplicability"
            ".classification"
            "._private"
            "._classify_expected_value_assumption_set_applicability_unchecked",
            return_value=(
                ExpectedValueAssumptionSetApplicabilityStatus
                .APPLICABLE
            ),
        ) as classifier:
            result = (
                classify_expected_value_assumption_set_applicability(
                    assumption_set
                )
            )
        self.assertIs(
            result,
            ExpectedValueAssumptionSetApplicabilityStatus
            .APPLICABLE,
        )
        classifier.assert_called_once_with(assumption_set)

    def test_production_has_no_builtin_sum_or_decimal_addition(self):
        root = Path(__file__).resolve().parents[1]
        private_tree = ast.parse(
            (root / "_classification.py").read_text()
        )
        calls = [
            node
            for node in ast.walk(private_tree)
            if isinstance(node, ast.Call)
        ]
        self.assertFalse(
            any(
                isinstance(call.func, ast.Name)
                and call.func.id == "sum"
                for call in calls
            )
        )
        additions = [
            node
            for node in ast.walk(private_tree)
            if isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.Add)
        ]
        self.assertEqual(additions, [])
        imported_modules = {
            node.module
            for node in ast.walk(private_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            imported_modules,
            {
                "decimal",
                "ExactDecimalArithmetic.arithmetic",
                "ExpectedValueAssumptionSet.models",
                "ExpectedValueAssumptionSetApplicability.models",
            },
        )


if __name__ == "__main__":
    unittest.main()
