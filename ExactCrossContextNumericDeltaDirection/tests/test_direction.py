import ast
import unittest
from decimal import Decimal, getcontext, localcontext
from pathlib import Path
from unittest.mock import patch

from ExactCrossContextNumericDelta.models import (
    ExactCrossContextNumericDelta,
    ExactCrossContextNumericDeltaCalculation,
)
from ExactCrossContextNumericDeltaApplicability.models import (
    ExactCrossContextNumericDeltaApplicabilityStatus,
)
from ExactCrossContextNumericDeltaDirection.classification import (
    classify_exact_cross_context_numeric_delta_direction,
)
from ExactCrossContextNumericDeltaDirection.models import (
    ExactCrossContextNumericDeltaDirectionStatus,
)


def make_delta(value):
    return ExactCrossContextNumericDelta(
        baseline_proposition_id="proposition-baseline",
        current_proposition_id="proposition-current",
        unit_id="USD",
        value=value,
    )


class ExactCrossContextNumericDeltaDirectionTests(
    unittest.TestCase
):
    def test_exact_enum_contract(self):
        self.assertEqual(
            list(
                ExactCrossContextNumericDeltaDirectionStatus
                .__members__
            ),
            ["NEGATIVE", "ZERO", "POSITIVE"],
        )
        self.assertEqual(
            [
                status.value
                for status in
                ExactCrossContextNumericDeltaDirectionStatus
            ],
            ["negative", "zero", "positive"],
        )

    def test_negative_values(self):
        for value in (
            Decimal("-1"),
            Decimal("-0.0001"),
            Decimal("-1E+100"),
        ):
            with self.subTest(value=value):
                self.assertIs(
                    classify_exact_cross_context_numeric_delta_direction(
                        make_delta(value)
                    ),
                    (
                        ExactCrossContextNumericDeltaDirectionStatus
                        .NEGATIVE
                    ),
                )

    def test_positive_and_negative_zero_are_zero(self):
        for value in (
            Decimal("0"),
            Decimal("-0"),
            Decimal("0.000"),
            Decimal("-0E+100"),
        ):
            with self.subTest(value=value):
                self.assertIs(
                    classify_exact_cross_context_numeric_delta_direction(
                        make_delta(value)
                    ),
                    (
                        ExactCrossContextNumericDeltaDirectionStatus
                        .ZERO
                    ),
                )

    def test_positive_values(self):
        for value in (
            Decimal("1"),
            Decimal("0.0001"),
            Decimal("1E+100"),
        ):
            with self.subTest(value=value):
                self.assertIs(
                    classify_exact_cross_context_numeric_delta_direction(
                        make_delta(value)
                    ),
                    (
                        ExactCrossContextNumericDeltaDirectionStatus
                        .POSITIVE
                    ),
                )

    def test_validator_called_once_with_original_delta(self):
        delta = make_delta(Decimal("-1"))
        with patch(
            "ExactCrossContextNumericDeltaDirection"
            ".classification"
            ".validate_exact_cross_context_numeric_delta",
        ) as validator:
            result = (
                classify_exact_cross_context_numeric_delta_direction(
                    delta
                )
            )
        self.assertIs(
            result,
            ExactCrossContextNumericDeltaDirectionStatus.NEGATIVE,
        )
        validator.assert_called_once_with(delta)
        self.assertIs(validator.call_args.args[0], delta)

    def test_validator_exception_propagates_unchanged(self):
        error = TypeError("delta failure")
        with patch(
            "ExactCrossContextNumericDeltaDirection"
            ".classification"
            ".validate_exact_cross_context_numeric_delta",
            side_effect=error,
        ):
            with self.assertRaises(TypeError) as context:
                classify_exact_cross_context_numeric_delta_direction(
                    make_delta(Decimal("1"))
                )
        self.assertIs(context.exception, error)

    def test_calculation_wrapper_is_not_an_accepted_input(self):
        calculation = ExactCrossContextNumericDeltaCalculation(
            applicability_status=(
                ExactCrossContextNumericDeltaApplicabilityStatus
                .CALCULABLE
            ),
            delta=make_delta(Decimal("1")),
        )
        with self.assertRaisesRegex(
            TypeError,
            "^delta must be ExactCrossContextNumericDelta$",
        ):
            classify_exact_cross_context_numeric_delta_direction(
                calculation
            )

    def test_inputs_and_value_identity_are_preserved(self):
        value = Decimal("-1.2300")
        delta = make_delta(value)
        delta_id = id(delta)
        value_tuple = value.as_tuple()

        result = (
            classify_exact_cross_context_numeric_delta_direction(
                delta
            )
        )

        self.assertIs(
            result,
            ExactCrossContextNumericDeltaDirectionStatus.NEGATIVE,
        )
        self.assertEqual(id(delta), delta_id)
        self.assertIs(delta.value, value)
        self.assertEqual(value.as_tuple(), value_tuple)

    def test_decimal_context_is_not_changed(self):
        with localcontext() as context:
            context.prec = 1
            context.rounding = "ROUND_DOWN"
            before = context.copy()
            classify_exact_cross_context_numeric_delta_direction(
                make_delta(Decimal("-1E+100"))
            )
            self.assertEqual(context.prec, before.prec)
            self.assertEqual(context.rounding, before.rounding)
            self.assertEqual(context.traps, before.traps)
            self.assertEqual(context.flags, before.flags)
        self.assertIsNotNone(getcontext())

    def test_production_dependencies_and_no_arithmetic(self):
        root = Path(__file__).resolve().parents[1]
        classification_tree = ast.parse(
            (root / "classification.py").read_text()
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(classification_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "ExactCrossContextNumericDelta.models",
                "ExactCrossContextNumericDelta.validation",
                (
                    "ExactCrossContextNumericDeltaDirection"
                    ".models"
                ),
            },
        )
        source = (root / "classification.py").read_text()
        for forbidden in (
            "subtract",
            "float",
            "Fraction",
            "tolerance",
            "material",
            "applicability",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
