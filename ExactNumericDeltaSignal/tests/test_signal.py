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
from ExactNumericDeltaMateriality.models import (
    ExactNumericDeltaMaterialityPolicy,
    ExactNumericDeltaMaterialityStatus,
)
from ExactNumericDeltaSignal.classification import (
    classify_exact_numeric_delta_signal,
)
from ExactNumericDeltaSignal.models import (
    ExactNumericDeltaSignalClassification,
    ExactNumericDeltaSignalStatus,
)


def make_delta(
    value=Decimal("2"),
    unit_id="USD",
):
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


class ExactNumericDeltaSignalTests(unittest.TestCase):
    def test_exact_status_and_result_model_contracts(self):
        self.assertEqual(
            list(ExactNumericDeltaSignalStatus.__members__),
            [
                "UNIT_MISMATCH",
                "NO_CHANGE",
                "IMMATERIAL_INCREASE",
                "IMMATERIAL_DECREASE",
                "MATERIAL_INCREASE",
                "MATERIAL_DECREASE",
            ],
        )
        self.assertEqual(
            [
                status.value
                for status in ExactNumericDeltaSignalStatus
            ],
            [
                "unit_mismatch",
                "no_change",
                "immaterial_increase",
                "immaterial_decrease",
                "material_increase",
                "material_decrease",
            ],
        )
        self.assertEqual(
            [
                field.name
                for field in fields(
                    ExactNumericDeltaSignalClassification
                )
            ],
            [
                "delta",
                "policy",
                "direction_status",
                "materiality_status",
                "signal_status",
            ],
        )
        self.assertEqual(
            get_type_hints(
                ExactNumericDeltaSignalClassification
            ),
            {
                "delta": ExactCrossContextNumericDelta,
                "policy": ExactNumericDeltaMaterialityPolicy,
                "direction_status": (
                    ExactCrossContextNumericDeltaDirectionStatus
                ),
                "materiality_status": (
                    ExactNumericDeltaMaterialityStatus
                ),
                "signal_status": ExactNumericDeltaSignalStatus,
            },
        )

    def test_result_is_frozen_hashable_and_structural(self):
        first = classify_exact_numeric_delta_signal(
            make_delta(),
            make_policy(),
        )
        second = classify_exact_numeric_delta_signal(
            make_delta(),
            make_policy(),
        )
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        with self.assertRaises(FrozenInstanceError):
            first.signal_status = (
                ExactNumericDeltaSignalStatus.NO_CHANGE
            )

    def test_complete_integrated_signal_mapping(self):
        cases = (
            (
                Decimal("0"),
                Decimal("0"),
                "NO_CHANGE",
                "ZERO",
                "IMMATERIAL",
            ),
            (
                Decimal("1"),
                Decimal("1"),
                "IMMATERIAL_INCREASE",
                "POSITIVE",
                "IMMATERIAL",
            ),
            (
                Decimal("-1"),
                Decimal("1"),
                "IMMATERIAL_DECREASE",
                "NEGATIVE",
                "IMMATERIAL",
            ),
            (
                Decimal("1.01"),
                Decimal("1"),
                "MATERIAL_INCREASE",
                "POSITIVE",
                "MATERIAL",
            ),
            (
                Decimal("-1.01"),
                Decimal("1"),
                "MATERIAL_DECREASE",
                "NEGATIVE",
                "MATERIAL",
            ),
        )
        for (
            value,
            threshold,
            signal_name,
            direction_name,
            materiality_name,
        ) in cases:
            with self.subTest(signal=signal_name):
                result = classify_exact_numeric_delta_signal(
                    make_delta(value),
                    make_policy(threshold),
                )
                self.assertIs(
                    result.signal_status,
                    ExactNumericDeltaSignalStatus
                    .__members__[signal_name],
                )
                self.assertIs(
                    result.direction_status,
                    (
                        ExactCrossContextNumericDeltaDirectionStatus
                        .__members__[direction_name]
                    ),
                )
                self.assertIs(
                    result.materiality_status,
                    (
                        ExactNumericDeltaMaterialityStatus
                        .__members__[materiality_name]
                    ),
                )

    def test_unit_mismatch_preserves_each_direction(self):
        cases = (
            (Decimal("-1"), "NEGATIVE"),
            (Decimal("0"), "ZERO"),
            (Decimal("1"), "POSITIVE"),
        )
        for value, direction_name in cases:
            with self.subTest(direction=direction_name):
                result = classify_exact_numeric_delta_signal(
                    make_delta(value, unit_id="USD"),
                    make_policy(
                        Decimal("0"),
                        unit_id="shares",
                    ),
                )
                self.assertIs(
                    result.signal_status,
                    ExactNumericDeltaSignalStatus.UNIT_MISMATCH,
                )
                self.assertIs(
                    result.materiality_status,
                    (
                        ExactNumericDeltaMaterialityStatus
                        .UNIT_MISMATCH
                    ),
                )
                self.assertIs(
                    result.direction_status,
                    (
                        ExactCrossContextNumericDeltaDirectionStatus
                        .__members__[direction_name]
                    ),
                )

    def test_validation_once_in_delta_then_policy_order(self):
        delta = make_delta()
        policy = make_policy()
        calls = []
        with patch(
            "ExactNumericDeltaSignal.classification"
            ".validate_exact_cross_context_numeric_delta",
            side_effect=lambda value: calls.append(
                ("delta", value)
            ),
        ) as delta_validator, patch(
            "ExactNumericDeltaSignal.classification"
            ".validate_exact_numeric_delta_materiality_policy",
            side_effect=lambda value: calls.append(
                ("policy", value)
            ),
        ) as policy_validator:
            result = classify_exact_numeric_delta_signal(
                delta,
                policy,
            )
        self.assertIs(
            result.signal_status,
            ExactNumericDeltaSignalStatus.MATERIAL_INCREASE,
        )
        self.assertEqual(
            calls,
            [("delta", delta), ("policy", policy)],
        )
        delta_validator.assert_called_once_with(delta)
        policy_validator.assert_called_once_with(policy)

    def test_validation_failure_order_and_exception_identity(self):
        delta_error = TypeError("delta failure")
        with patch(
            "ExactNumericDeltaSignal.classification"
            ".validate_exact_cross_context_numeric_delta",
            side_effect=delta_error,
        ), patch(
            "ExactNumericDeltaSignal.classification"
            ".validate_exact_numeric_delta_materiality_policy",
        ) as policy_validator:
            with self.assertRaises(TypeError) as context:
                classify_exact_numeric_delta_signal(
                    make_delta(),
                    make_policy(),
                )
        self.assertIs(context.exception, delta_error)
        policy_validator.assert_not_called()

        policy_error = ValueError("policy failure")
        with patch(
            "ExactNumericDeltaSignal.classification"
            ".validate_exact_numeric_delta_materiality_policy",
            side_effect=policy_error,
        ):
            with self.assertRaises(ValueError) as context:
                classify_exact_numeric_delta_signal(
                    make_delta(),
                    make_policy(),
                )
        self.assertIs(context.exception, policy_error)

    def test_private_helpers_run_in_order_with_original_inputs(self):
        delta = make_delta()
        policy = make_policy()
        calls = []
        with patch(
            "ExactNumericDeltaSignal.classification"
            "._classify_exact_cross_context_numeric_delta_direction_unchecked",
            side_effect=lambda value: (
                calls.append(("direction", value))
                or ExactCrossContextNumericDeltaDirectionStatus
                .POSITIVE
            ),
        ) as direction, patch(
            "ExactNumericDeltaSignal.classification"
            "._classify_exact_numeric_delta_materiality_unchecked",
            side_effect=lambda first, second: (
                calls.append(("materiality", first, second))
                or ExactNumericDeltaMaterialityStatus.MATERIAL
            ),
        ) as materiality:
            result = classify_exact_numeric_delta_signal(
                delta,
                policy,
            )

        self.assertIs(
            result.signal_status,
            ExactNumericDeltaSignalStatus.MATERIAL_INCREASE,
        )
        self.assertEqual(
            calls,
            [
                ("direction", delta),
                ("materiality", delta, policy),
            ],
        )
        direction.assert_called_once_with(delta)
        materiality.assert_called_once_with(delta, policy)

    def test_original_objects_and_exact_enum_members_preserved(self):
        unit_id = " USD-\u00e9 "
        value = Decimal("-2.000")
        threshold = Decimal("1.000")
        delta = make_delta(value=value, unit_id=unit_id)
        policy = make_policy(
            threshold=threshold,
            unit_id=unit_id,
        )
        result = classify_exact_numeric_delta_signal(
            delta,
            policy,
        )

        self.assertIs(result.delta, delta)
        self.assertIs(result.policy, policy)
        self.assertIs(delta.value, value)
        self.assertIs(policy.threshold, threshold)
        self.assertIs(
            result.direction_status,
            ExactCrossContextNumericDeltaDirectionStatus
            .NEGATIVE,
        )
        self.assertIs(
            result.materiality_status,
            ExactNumericDeltaMaterialityStatus.MATERIAL,
        )
        self.assertIs(
            result.signal_status,
            ExactNumericDeltaSignalStatus.MATERIAL_DECREASE,
        )

    def test_detached_statuses_and_calculation_are_not_inputs(self):
        policy = make_policy()
        invalid_inputs = (
            ExactCrossContextNumericDeltaDirectionStatus.POSITIVE,
            ExactNumericDeltaMaterialityStatus.MATERIAL,
            ExactCrossContextNumericDeltaCalculation(
                applicability_status=(
                    ExactCrossContextNumericDeltaApplicabilityStatus
                    .CALCULABLE
                ),
                delta=make_delta(),
            ),
        )
        for value in invalid_inputs:
            with self.subTest(value=type(value)):
                with self.assertRaises(TypeError):
                    classify_exact_numeric_delta_signal(
                        value,
                        policy,
                    )

    def test_impossible_or_unknown_mapping_raises(self):
        cases = (
            (
                ExactCrossContextNumericDeltaDirectionStatus.ZERO,
                ExactNumericDeltaMaterialityStatus.MATERIAL,
            ),
            (
                object(),
                ExactNumericDeltaMaterialityStatus.IMMATERIAL,
            ),
            (
                ExactCrossContextNumericDeltaDirectionStatus.POSITIVE,
                object(),
            ),
        )
        for direction, materiality in cases:
            with self.subTest(
                direction=direction,
                materiality=materiality,
            ):
                with patch(
                    "ExactNumericDeltaSignal.classification"
                    "._classify_exact_cross_context_numeric_delta_direction_unchecked",
                    return_value=direction,
                ), patch(
                    "ExactNumericDeltaSignal.classification"
                    "._classify_exact_numeric_delta_materiality_unchecked",
                    return_value=materiality,
                ):
                    with self.assertRaisesRegex(
                        RuntimeError,
                        "^unsupported numeric delta signal "
                        "classification$",
                    ):
                        classify_exact_numeric_delta_signal(
                            make_delta(),
                            make_policy(),
                        )

    def test_decimal_context_is_not_changed(self):
        with localcontext() as context:
            context.prec = 1
            context.rounding = "ROUND_DOWN"
            before = context.copy()
            result = classify_exact_numeric_delta_signal(
                make_delta(Decimal("-1E+100")),
                make_policy(Decimal("1")),
            )
            self.assertEqual(context.prec, before.prec)
            self.assertEqual(context.rounding, before.rounding)
            self.assertEqual(context.traps, before.traps)
            self.assertEqual(context.flags, before.flags)
        self.assertIs(
            result.signal_status,
            ExactNumericDeltaSignalStatus.MATERIAL_DECREASE,
        )

    def test_production_dependencies_and_excluded_scope(self):
        root = Path(__file__).resolve().parents[1]
        classification_tree = ast.parse(
            (root / "classification.py").read_text()
        )
        imported_modules = {
            node.module
            for node in ast.walk(classification_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertNotIn(
            "ExactDecimalArithmetic.arithmetic",
            imported_modules,
        )
        source = (root / "classification.py").read_text()
        for forbidden in (
            "subtract",
            "float",
            "Fraction",
            "beneficial",
            "harmful",
            "Hypothesis",
            "Thesis",
            "Portfolio",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
