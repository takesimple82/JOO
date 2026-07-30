import ast
import unittest
from dataclasses import FrozenInstanceError, fields
from decimal import Decimal, Inexact, Rounded, localcontext
from pathlib import Path
from typing import Optional, get_type_hints
from unittest.mock import patch

from BaselineCurrentPropositionPair.models import (
    ExplicitBaselineCurrentPropositionPair,
)
from EffectiveContextObservedDate.models import (
    ExplicitEffectiveContextObservedDate,
)
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from ExactCrossContextNumericDelta.calculation import (
    calculate_exact_cross_context_numeric_delta,
)
from ExactCrossContextNumericDelta.models import (
    ExactCrossContextNumericDelta,
    ExactCrossContextNumericDeltaCalculation,
)
from ExactCrossContextNumericDelta.validation import (
    validate_exact_cross_context_numeric_delta,
    validate_exact_cross_context_numeric_delta_calculation,
)
from ExactCrossContextNumericDeltaApplicability.models import (
    ExactCrossContextNumericDeltaApplicabilityStatus,
)
from SemanticPropositionProduction.models import (
    SemanticallyProducedNumericProposition,
)


def make_pair(**overrides):
    values = {
        "baseline_proposition_id": "proposition-baseline",
        "current_proposition_id": "proposition-current",
    }
    values.update(overrides)
    return ExplicitBaselineCurrentPropositionPair(**values)


def make_production(role, **overrides):
    values = {
        "proposition_id": f"proposition-{role}",
        "finding_id": f"finding-{role}",
        "subject_id": "subject-001",
        "predicate_id": "predicate-001",
        "value": (
            Decimal("1")
            if role == "baseline"
            else Decimal("2")
        ),
        "unit_id": "USD",
        "effective_context_id": f"context-{role}",
    }
    values.update(overrides)
    return SemanticallyProducedNumericProposition(
        ExactObservedNumericProposition(**values)
    )


def make_context_date(role):
    return ExplicitEffectiveContextObservedDate(
        effective_context_id=f"context-{role}",
        observed_on=(
            "2026-07-29"
            if role == "baseline"
            else "2026-07-30"
        ),
    )


def calculation_inputs():
    return (
        make_pair(),
        make_production("baseline"),
        make_production("current"),
        make_context_date("baseline"),
        make_context_date("current"),
    )


class DeltaSubclass(ExactCrossContextNumericDelta):
    pass


class CalculationSubclass(
    ExactCrossContextNumericDeltaCalculation
):
    pass


class ExactCrossContextNumericDeltaTests(unittest.TestCase):
    def test_exact_model_contracts(self):
        self.assertEqual(
            [
                field.name
                for field in fields(
                    ExactCrossContextNumericDelta
                )
            ],
            [
                "baseline_proposition_id",
                "current_proposition_id",
                "unit_id",
                "value",
            ],
        )
        self.assertEqual(
            get_type_hints(ExactCrossContextNumericDelta),
            {
                "baseline_proposition_id": str,
                "current_proposition_id": str,
                "unit_id": str,
                "value": Decimal,
            },
        )
        self.assertEqual(
            [
                field.name
                for field in fields(
                    ExactCrossContextNumericDeltaCalculation
                )
            ],
            ["applicability_status", "delta"],
        )
        self.assertEqual(
            get_type_hints(
                ExactCrossContextNumericDeltaCalculation
            ),
            {
                "applicability_status": (
                    ExactCrossContextNumericDeltaApplicabilityStatus
                ),
                "delta": Optional[
                    ExactCrossContextNumericDelta
                ],
            },
        )

    def test_models_are_frozen_hashable_and_structural(self):
        delta = ExactCrossContextNumericDelta(
            "baseline",
            "current",
            "USD",
            Decimal("1.00"),
        )
        same = ExactCrossContextNumericDelta(
            "baseline",
            "current",
            "USD",
            Decimal("1.0"),
        )
        calculation = ExactCrossContextNumericDeltaCalculation(
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CALCULABLE,
            delta,
        )
        self.assertEqual(delta, same)
        self.assertEqual(hash(delta), hash(same))
        self.assertIsInstance(hash(calculation), int)
        with self.assertRaises(FrozenInstanceError):
            delta.value = Decimal("2")
        with self.assertRaises(FrozenInstanceError):
            calculation.delta = None

    def test_delta_validator_success_and_exact_type(self):
        delta = ExactCrossContextNumericDelta(
            "baseline",
            "current",
            "USD",
            Decimal("1"),
        )
        self.assertIsNone(
            validate_exact_cross_context_numeric_delta(delta)
        )
        with self.assertRaisesRegex(
            TypeError,
            "^delta must be ExactCrossContextNumericDelta$",
        ):
            validate_exact_cross_context_numeric_delta(
                DeltaSubclass(
                    "baseline",
                    "current",
                    "USD",
                    Decimal("1"),
                )
            )

    def test_delta_validator_field_order_and_contract(self):
        cases = (
            (
                ExactCrossContextNumericDelta(
                    None,
                    None,
                    None,
                    None,
                ),
                TypeError,
                "baseline_proposition_id must be str",
            ),
            (
                ExactCrossContextNumericDelta(
                    " ",
                    None,
                    None,
                    None,
                ),
                ValueError,
                "baseline_proposition_id must not be blank",
            ),
            (
                ExactCrossContextNumericDelta(
                    "baseline",
                    None,
                    None,
                    None,
                ),
                TypeError,
                "current_proposition_id must be str",
            ),
            (
                ExactCrossContextNumericDelta(
                    "baseline",
                    "current",
                    None,
                    None,
                ),
                TypeError,
                "unit_id must be str",
            ),
            (
                ExactCrossContextNumericDelta(
                    "baseline",
                    "current",
                    "USD",
                    None,
                ),
                TypeError,
                "value must be Decimal",
            ),
            (
                ExactCrossContextNumericDelta(
                    "baseline",
                    "current",
                    "USD",
                    Decimal("NaN"),
                ),
                ValueError,
                "value must be finite",
            ),
        )
        for delta, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_exact_cross_context_numeric_delta(
                        delta
                    )

    def test_calculation_validator_enforces_delta_invariant(self):
        status_type = (
            ExactCrossContextNumericDeltaApplicabilityStatus
        )
        delta = ExactCrossContextNumericDelta(
            "baseline",
            "current",
            "USD",
            Decimal("1"),
        )
        self.assertIsNone(
            validate_exact_cross_context_numeric_delta_calculation(
                ExactCrossContextNumericDeltaCalculation(
                    status_type.CALCULABLE,
                    delta,
                )
            )
        )
        self.assertIsNone(
            validate_exact_cross_context_numeric_delta_calculation(
                ExactCrossContextNumericDeltaCalculation(
                    status_type.SAME_DATE,
                    None,
                )
            )
        )
        with self.assertRaisesRegex(
            TypeError,
            "^delta must be ExactCrossContextNumericDelta "
            "when applicability_status is CALCULABLE$",
        ):
            validate_exact_cross_context_numeric_delta_calculation(
                ExactCrossContextNumericDeltaCalculation(
                    status_type.CALCULABLE,
                    None,
                )
            )
        with self.assertRaisesRegex(
            ValueError,
            "^delta must be None when applicability_status "
            "is not CALCULABLE$",
        ):
            validate_exact_cross_context_numeric_delta_calculation(
                ExactCrossContextNumericDeltaCalculation(
                    status_type.SAME_DATE,
                    delta,
                )
            )

    def test_calculation_validator_exact_outer_types(self):
        delta = ExactCrossContextNumericDelta(
            "baseline",
            "current",
            "USD",
            Decimal("1"),
        )
        status = (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CALCULABLE
        )
        with self.assertRaisesRegex(
            TypeError,
            "^calculation must be "
            "ExactCrossContextNumericDeltaCalculation$",
        ):
            validate_exact_cross_context_numeric_delta_calculation(
                CalculationSubclass(status, delta)
            )
        with self.assertRaisesRegex(
            TypeError,
            "^applicability_status must be "
            "ExactCrossContextNumericDeltaApplicabilityStatus$",
        ):
            validate_exact_cross_context_numeric_delta_calculation(
                ExactCrossContextNumericDeltaCalculation(
                    None,
                    None,
                )
            )

    def test_public_applicability_called_once_with_originals(self):
        inputs = calculation_inputs()
        with patch(
            "ExactCrossContextNumericDelta.calculation"
            ".classify_exact_cross_context_numeric_delta_applicability",
            return_value=(
                ExactCrossContextNumericDeltaApplicabilityStatus
                .CALCULABLE
            ),
        ) as classifier:
            result = calculate_exact_cross_context_numeric_delta(
                *inputs
            )
        self.assertIsNotNone(result.delta)
        classifier.assert_called_once_with(*inputs)
        for actual, expected in zip(
            classifier.call_args.args,
            inputs,
        ):
            self.assertIs(actual, expected)

    def test_upstream_exception_propagates_unchanged(self):
        error = ValueError("applicability failure")
        with patch(
            "ExactCrossContextNumericDelta.calculation"
            ".classify_exact_cross_context_numeric_delta_applicability",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                calculate_exact_cross_context_numeric_delta(
                    *calculation_inputs()
                )
        self.assertIs(context.exception, error)

    def test_each_noncalculable_status_returns_none_without_arithmetic(
        self,
    ):
        statuses = [
            status
            for status in
            ExactCrossContextNumericDeltaApplicabilityStatus
            if (
                status
                is not
                ExactCrossContextNumericDeltaApplicabilityStatus
                .CALCULABLE
            )
        ]
        for status in statuses:
            with self.subTest(status=status):
                with patch(
                    "ExactCrossContextNumericDelta.calculation"
                    ".classify_exact_cross_context_numeric_delta_applicability",
                    return_value=status,
                ), patch(
                    "ExactCrossContextNumericDelta.calculation"
                    ".subtract_exact_decimal",
                ) as subtract:
                    result = (
                        calculate_exact_cross_context_numeric_delta(
                            *calculation_inputs()
                        )
                    )
                self.assertIs(
                    result.applicability_status,
                    status,
                )
                self.assertIsNone(result.delta)
                subtract.assert_not_called()

    def test_calculable_uses_current_minus_baseline_once(self):
        inputs = calculation_inputs()
        baseline = inputs[1]
        current = inputs[2]
        arithmetic_result = Decimal("123.4500")
        with patch(
            "ExactCrossContextNumericDelta.calculation"
            ".subtract_exact_decimal",
            return_value=arithmetic_result,
        ) as subtract:
            result = calculate_exact_cross_context_numeric_delta(
                *inputs
            )

        subtract.assert_called_once_with(
            current.proposition.value,
            baseline.proposition.value,
        )
        self.assertIs(
            result.applicability_status,
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CALCULABLE,
        )
        self.assertIs(result.delta.value, arithmetic_result)

    def test_integrated_exact_arithmetic_ignores_active_context(self):
        inputs = list(calculation_inputs())
        inputs[1] = make_production(
            "baseline",
            value=Decimal("1"),
        )
        inputs[2] = make_production(
            "current",
            value=Decimal("1e40"),
        )
        with localcontext() as context:
            context.prec = 1
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            result = calculate_exact_cross_context_numeric_delta(
                *inputs
            )

        self.assertEqual(
            result.delta.value,
            Decimal(
                "9999999999999999999999999999999999999999"
            ),
        )

    def test_endpoint_unit_and_value_object_identity(self):
        baseline_id = " baseline-\u00e9 "
        current_id = " current-e\u0301 "
        unit_id = " USD "
        pair = make_pair(
            baseline_proposition_id=baseline_id,
            current_proposition_id=current_id,
        )
        baseline = make_production(
            "baseline",
            proposition_id=baseline_id,
            unit_id=unit_id,
        )
        current = make_production(
            "current",
            proposition_id=current_id,
            unit_id=unit_id,
        )
        arithmetic_result = Decimal("1.00")
        with patch(
            "ExactCrossContextNumericDelta.calculation"
            ".subtract_exact_decimal",
            return_value=arithmetic_result,
        ):
            result = calculate_exact_cross_context_numeric_delta(
                pair,
                baseline,
                current,
                make_context_date("baseline"),
                make_context_date("current"),
            )

        self.assertIs(
            result.delta.baseline_proposition_id,
            baseline_id,
        )
        self.assertIs(
            result.delta.current_proposition_id,
            current_id,
        )
        self.assertIs(result.delta.unit_id, unit_id)
        self.assertIs(result.delta.value, arithmetic_result)

    def test_production_dependencies_and_excluded_responsibilities(
        self,
    ):
        root = Path(__file__).resolve().parents[1]
        calculation_tree = ast.parse(
            (root / "calculation.py").read_text()
        )
        imported_modules = {
            node.module
            for node in ast.walk(calculation_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertIn(
            "ExactDecimalArithmetic.arithmetic",
            imported_modules,
        )
        self.assertIn(
            (
                "ExactCrossContextNumericDeltaApplicability"
                ".classification"
            ),
            imported_modules,
        )
        source = (root / "calculation.py").read_text()
        for forbidden in (
            "float(",
            "Fraction",
            "materiality",
            "Signal",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
