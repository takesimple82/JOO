import ast
import unittest
from dataclasses import FrozenInstanceError, fields
from decimal import Decimal, localcontext
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from ExactCrossContextNumericDelta.models import (
    ExactCrossContextNumericDelta,
    ExactCrossContextNumericDeltaCalculation,
)
from ExactCrossContextNumericDeltaApplicability.models import (
    ExactCrossContextNumericDeltaApplicabilityStatus,
)
from ExactCrossContextNumericDeltaDirection.models import (
    ExactCrossContextNumericDeltaDirectionStatus,
)
from ExactNumericDeltaMateriality.classification import (
    classify_exact_numeric_delta_materiality,
)
from ExactNumericDeltaMateriality.models import (
    ExactNumericDeltaMaterialityPolicy,
    ExactNumericDeltaMaterialityStatus,
)
from ExactNumericDeltaMateriality.validation import (
    validate_exact_numeric_delta_materiality_policy,
)


def make_delta(value=Decimal("2"), unit_id="USD"):
    return ExactCrossContextNumericDelta(
        baseline_proposition_id="proposition-baseline",
        current_proposition_id="proposition-current",
        unit_id=unit_id,
        value=value,
    )


def make_policy(
    threshold=Decimal("1"),
    unit_id="USD",
):
    return ExactNumericDeltaMaterialityPolicy(
        unit_id=unit_id,
        threshold=threshold,
    )


class PolicySubclass(ExactNumericDeltaMaterialityPolicy):
    pass


class ExactNumericDeltaMaterialityTests(unittest.TestCase):
    def test_exact_policy_and_enum_contracts(self):
        self.assertEqual(
            [
                field.name
                for field in fields(
                    ExactNumericDeltaMaterialityPolicy
                )
            ],
            ["unit_id", "threshold"],
        )
        self.assertEqual(
            get_type_hints(
                ExactNumericDeltaMaterialityPolicy
            ),
            {
                "unit_id": str,
                "threshold": Decimal,
            },
        )
        self.assertEqual(
            list(
                ExactNumericDeltaMaterialityStatus.__members__
            ),
            ["UNIT_MISMATCH", "IMMATERIAL", "MATERIAL"],
        )
        self.assertEqual(
            [
                status.value
                for status in
                ExactNumericDeltaMaterialityStatus
            ],
            ["unit_mismatch", "immaterial", "material"],
        )

    def test_policy_is_frozen_hashable_and_structural(self):
        first = make_policy(Decimal("1.0"))
        second = make_policy(Decimal("1.00"))
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        with self.assertRaises(FrozenInstanceError):
            first.threshold = Decimal("2")

    def test_policy_validator_success_and_exact_model_type(self):
        self.assertIsNone(
            validate_exact_numeric_delta_materiality_policy(
                make_policy()
            )
        )
        with self.assertRaisesRegex(
            TypeError,
            "^policy must be ExactNumericDeltaMaterialityPolicy$",
        ):
            validate_exact_numeric_delta_materiality_policy(
                PolicySubclass("USD", Decimal("1"))
            )

    def test_policy_validation_order_and_messages(self):
        cases = (
            (
                make_policy(unit_id=None, threshold=None),
                TypeError,
                "unit_id must be str",
            ),
            (
                make_policy(unit_id=" ", threshold=None),
                ValueError,
                "unit_id must not be blank",
            ),
            (
                make_policy(threshold=None),
                TypeError,
                "threshold must be Decimal",
            ),
            (
                make_policy(threshold=Decimal("NaN")),
                ValueError,
                "threshold must be finite",
            ),
            (
                make_policy(threshold=Decimal("-0.01")),
                ValueError,
                "threshold must be non-negative",
            ),
        )
        for policy, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_exact_numeric_delta_materiality_policy(
                        policy
                    )

    def test_positive_and_negative_zero_thresholds_are_valid(self):
        for threshold in (
            Decimal("0"),
            Decimal("-0"),
            Decimal("0.000"),
            Decimal("-0E+100"),
        ):
            with self.subTest(threshold=threshold):
                self.assertIsNone(
                    validate_exact_numeric_delta_materiality_policy(
                        make_policy(threshold)
                    )
                )

    def test_validation_once_in_delta_then_policy_order(self):
        delta = make_delta()
        policy = make_policy()
        calls = []
        with patch(
            "ExactNumericDeltaMateriality.classification"
            ".validate_exact_cross_context_numeric_delta",
            side_effect=lambda value: calls.append(
                ("delta", value)
            ),
        ) as delta_validator, patch(
            "ExactNumericDeltaMateriality.classification"
            ".validate_exact_numeric_delta_materiality_policy",
            side_effect=lambda value: calls.append(
                ("policy", value)
            ),
        ) as policy_validator:
            result = classify_exact_numeric_delta_materiality(
                delta,
                policy,
            )
        self.assertIs(
            result,
            ExactNumericDeltaMaterialityStatus.MATERIAL,
        )
        self.assertEqual(
            calls,
            [("delta", delta), ("policy", policy)],
        )
        delta_validator.assert_called_once_with(delta)
        policy_validator.assert_called_once_with(policy)

    def test_first_validation_failure_stops_policy_validation(self):
        error = TypeError("delta failure")
        with patch(
            "ExactNumericDeltaMateriality.classification"
            ".validate_exact_cross_context_numeric_delta",
            side_effect=error,
        ), patch(
            "ExactNumericDeltaMateriality.classification"
            ".validate_exact_numeric_delta_materiality_policy",
        ) as policy_validator:
            with self.assertRaises(TypeError) as context:
                classify_exact_numeric_delta_materiality(
                    make_delta(),
                    make_policy(),
                )
        self.assertIs(context.exception, error)
        policy_validator.assert_not_called()

    def test_policy_failure_propagates_unchanged(self):
        error = ValueError("policy failure")
        with patch(
            "ExactNumericDeltaMateriality.classification"
            ".validate_exact_numeric_delta_materiality_policy",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                classify_exact_numeric_delta_materiality(
                    make_delta(),
                    make_policy(),
                )
        self.assertIs(context.exception, error)

    def test_unit_mismatch_precedes_magnitude(self):
        self.assertIs(
            classify_exact_numeric_delta_materiality(
                make_delta(
                    value=Decimal("1E+100"),
                    unit_id="USD",
                ),
                make_policy(
                    threshold=Decimal("0"),
                    unit_id="shares",
                ),
            ),
            ExactNumericDeltaMaterialityStatus.UNIT_MISMATCH,
        )

    def test_strict_threshold_and_equality_contract(self):
        cases = (
            (Decimal("1.01"), Decimal("1"), "MATERIAL"),
            (Decimal("1"), Decimal("1"), "IMMATERIAL"),
            (Decimal("0.99"), Decimal("1"), "IMMATERIAL"),
            (Decimal("-1.01"), Decimal("1"), "MATERIAL"),
            (Decimal("-1"), Decimal("1"), "IMMATERIAL"),
            (Decimal("-0.99"), Decimal("1"), "IMMATERIAL"),
        )
        for value, threshold, expected_name in cases:
            with self.subTest(
                value=value,
                threshold=threshold,
            ):
                self.assertIs(
                    classify_exact_numeric_delta_materiality(
                        make_delta(value),
                        make_policy(threshold),
                    ),
                    (
                        ExactNumericDeltaMaterialityStatus
                        .__members__[expected_name]
                    ),
                )

    def test_zero_threshold_contract(self):
        cases = (
            (Decimal("0"), "IMMATERIAL"),
            (Decimal("-0"), "IMMATERIAL"),
            (Decimal("0.0001"), "MATERIAL"),
            (Decimal("-0.0001"), "MATERIAL"),
        )
        for value, expected_name in cases:
            with self.subTest(value=value):
                self.assertIs(
                    classify_exact_numeric_delta_materiality(
                        make_delta(value),
                        make_policy(Decimal("0")),
                    ),
                    (
                        ExactNumericDeltaMaterialityStatus
                        .__members__[expected_name]
                    ),
                )

    def test_equal_magnitudes_have_equal_materiality(self):
        for magnitude in (
            Decimal("0"),
            Decimal("1"),
            Decimal("2"),
        ):
            with self.subTest(magnitude=magnitude):
                positive = (
                    classify_exact_numeric_delta_materiality(
                        make_delta(magnitude),
                        make_policy(Decimal("1")),
                    )
                )
                negative = (
                    classify_exact_numeric_delta_materiality(
                        make_delta(-magnitude),
                        make_policy(Decimal("1")),
                    )
                )
                self.assertIs(positive, negative)

    def test_context_inputs_and_field_objects_are_preserved(self):
        unit_id = " USD-\u00e9 "
        threshold = Decimal("1.000")
        value = Decimal("-2.000")
        delta = make_delta(value=value, unit_id=unit_id)
        policy = make_policy(
            threshold=threshold,
            unit_id=unit_id,
        )
        identities = (id(delta), id(policy))
        with localcontext() as context:
            context.prec = 1
            context.rounding = "ROUND_DOWN"
            before = context.copy()
            result = classify_exact_numeric_delta_materiality(
                delta,
                policy,
            )
            self.assertEqual(context.prec, before.prec)
            self.assertEqual(context.rounding, before.rounding)
            self.assertEqual(context.traps, before.traps)
            self.assertEqual(context.flags, before.flags)

        self.assertIs(
            result,
            ExactNumericDeltaMaterialityStatus.MATERIAL,
        )
        self.assertEqual(
            (id(delta), id(policy)),
            identities,
        )
        self.assertIs(delta.unit_id, unit_id)
        self.assertIs(policy.unit_id, unit_id)
        self.assertIs(delta.value, value)
        self.assertIs(policy.threshold, threshold)

    def test_direction_and_calculation_are_not_inputs(self):
        with self.assertRaises(TypeError):
            classify_exact_numeric_delta_materiality(
                (
                    ExactCrossContextNumericDeltaDirectionStatus
                    .POSITIVE
                ),
                make_policy(),
            )
        calculation = ExactCrossContextNumericDeltaCalculation(
            applicability_status=(
                ExactCrossContextNumericDeltaApplicabilityStatus
                .CALCULABLE
            ),
            delta=make_delta(),
        )
        with self.assertRaises(TypeError):
            classify_exact_numeric_delta_materiality(
                calculation,
                make_policy(),
            )

    def test_production_dependencies_and_excluded_scope(self):
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
                "ExactNumericDeltaMateriality.models",
                "ExactNumericDeltaMateriality.validation",
            },
        )
        source = (root / "classification.py").read_text()
        for forbidden in (
            "subtract",
            "float",
            "Fraction",
            "tolerance",
            "Signal",
            "Direction",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
