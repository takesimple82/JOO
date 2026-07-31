import ast
import unittest
from dataclasses import FrozenInstanceError, fields
from decimal import (
    Decimal,
    Inexact,
    InvalidOperation,
    Rounded,
    localcontext,
)
from fractions import Fraction
from pathlib import Path
from typing import Optional, get_type_hints
from unittest.mock import patch

from ExpectedValueAssumptionSet.models import (
    ExplicitExpectedValueAssumptionSet,
    ExplicitExpectedValueOutcomeAssumption,
)
from ExplicitPortfolioImpact.models import (
    ExplicitPortfolioImpact,
)
from ExplicitThesis.models import ExplicitThesis
from ExactExpectedValue.calculation import (
    calculate_exact_expected_value,
)
from ExactExpectedValue.models import (
    ExactExpectedValue,
    ExactExpectedValueCalculation,
)
from ExactExpectedValue.validation import (
    validate_exact_expected_value,
    validate_exact_expected_value_calculation,
)
from ExpectedValueAssumptionSetApplicability.models import (
    ExpectedValueAssumptionSetApplicabilityStatus,
)
import ExpectedValueAssumptionSetApplicability.classification as public_applicability

from PortfolioDomain.models import PortfolioSubject
from PortfolioImpactInterpretationPolicy.models import (
    PortfolioImpactDirection,
    PortfolioImpactInterpretationPolicy,
)
from SemanticExpectedValueAssumptionSetProduction.models import (
    SemanticallyProducedExpectedValueAssumptionSet,
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


def make_outcome(
    outcome_id,
    probability,
    value,
):
    return ExplicitExpectedValueOutcomeAssumption(
        outcome_id,
        f"Outcome {outcome_id}.",
        probability,
        value,
    )


def make_source(outcomes=None):
    if outcomes is None:
        outcomes = (
            make_outcome(
                "outcome-001",
                Decimal("0.25"),
                Decimal("20"),
            ),
            make_outcome(
                "outcome-002",
                Decimal("0.75"),
                Decimal("-4"),
            ),
        )
    return SemanticallyProducedExpectedValueAssumptionSet(
        ExplicitExpectedValueAssumptionSet(
            "assumptions-001",
            make_semantic_impact(),
            "USD",
            outcomes,
        )
    )


def make_semantic_impact():
    thesis = SemanticallyProducedThesis(
        ExplicitThesis(
            "thesis-001",
            "A semantic Thesis.",
        )
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


class ExpectedValueSubclass(ExactExpectedValue):
    pass


class CalculationSubclass(ExactExpectedValueCalculation):
    pass


class SourceSubclass(
    SemanticallyProducedExpectedValueAssumptionSet
):
    pass


class DecimalSubclass(Decimal):
    pass


class ExactExpectedValueTests(unittest.TestCase):
    def test_exact_model_contracts(self):
        self.assertEqual(
            [
                field.name
                for field in fields(ExactExpectedValue)
            ],
            ["source", "value"],
        )
        self.assertEqual(
            get_type_hints(ExactExpectedValue),
            {
                "source": (
                    SemanticallyProducedExpectedValueAssumptionSet
                ),
                "value": Decimal,
            },
        )
        self.assertEqual(
            [
                field.name
                for field in fields(
                    ExactExpectedValueCalculation
                )
            ],
            ["applicability_status", "expected_value"],
        )
        self.assertEqual(
            get_type_hints(ExactExpectedValueCalculation),
            {
                "applicability_status": (
                    ExpectedValueAssumptionSetApplicabilityStatus
                ),
                "expected_value": Optional[
                    ExactExpectedValue
                ],
            },
        )

    def test_models_are_frozen_hashable_and_structural(self):
        source = make_source()
        result = ExactExpectedValue(
            source,
            Decimal("2.00"),
        )
        same = ExactExpectedValue(
            source,
            Decimal("2.0"),
        )
        calculation = ExactExpectedValueCalculation(
            ExpectedValueAssumptionSetApplicabilityStatus
            .APPLICABLE,
            result,
        )
        self.assertEqual(result, same)
        self.assertEqual(hash(result), hash(same))
        self.assertIsInstance(hash(calculation), int)
        with self.assertRaises(FrozenInstanceError):
            result.value = Decimal("3")
        with self.assertRaises(FrozenInstanceError):
            calculation.expected_value = None

    def test_result_validator_success_and_exact_model_type(self):
        result = ExactExpectedValue(
            make_source(),
            Decimal("2"),
        )
        self.assertIsNone(
            validate_exact_expected_value(result)
        )
        with self.assertRaisesRegex(
            TypeError,
            "^expected_value must be ExactExpectedValue$",
        ):
            validate_exact_expected_value(
                ExpectedValueSubclass(
                    result.source,
                    result.value,
                )
            )

    def test_result_validator_exact_source_type(self):
        source = make_source()
        subclass = SourceSubclass(source.assumption_set)
        for value in (None, object(), subclass):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^source must be "
                    "SemanticallyProducedExpectedValueAssumptionSet$",
                ):
                    validate_exact_expected_value(
                        ExactExpectedValue(
                            value,
                            Decimal("1"),
                        )
                    )

    def test_result_validator_decimal_contract(self):
        source = make_source()
        for value in (
            None,
            1,
            1.0,
            Fraction(1, 2),
            DecimalSubclass("1"),
        ):
            with self.subTest(value=value):
                with patch(
                    "ExactExpectedValue.validation"
                    ".validate_semantically_produced_"
                    "expected_value_assumption_set",
                ):
                    with self.assertRaisesRegex(
                        TypeError,
                        "^value must be Decimal$",
                    ):
                        validate_exact_expected_value(
                            ExactExpectedValue(source, value)
                        )
        for value in (
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        ):
            with self.subTest(value=value):
                with patch(
                    "ExactExpectedValue.validation"
                    ".validate_semantically_produced_"
                    "expected_value_assumption_set",
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        "^value must be finite$",
                    ):
                        validate_exact_expected_value(
                            ExactExpectedValue(source, value)
                        )

    def test_source_validator_once_and_exception_identity(self):
        source = make_source()
        result = ExactExpectedValue(
            source,
            Decimal("2"),
        )
        with patch(
            "ExactExpectedValue.validation"
            ".validate_semantically_produced_"
            "expected_value_assumption_set",
        ) as validator:
            self.assertIsNone(
                validate_exact_expected_value(result)
            )
        validator.assert_called_once_with(source)
        self.assertIs(validator.call_args.args[0], source)

        error = ValueError("source failure")
        with patch(
            "ExactExpectedValue.validation"
            ".validate_semantically_produced_"
            "expected_value_assumption_set",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                validate_exact_expected_value(result)
        self.assertIs(context.exception, error)

    def test_calculation_validator_outer_types(self):
        status = (
            ExpectedValueAssumptionSetApplicabilityStatus
            .APPLICABLE
        )
        result = ExactExpectedValue(
            make_source(),
            Decimal("2"),
        )
        with self.assertRaisesRegex(
            TypeError,
            "^calculation must be "
            "ExactExpectedValueCalculation$",
        ):
            validate_exact_expected_value_calculation(
                CalculationSubclass(status, result)
            )
        with self.assertRaisesRegex(
            TypeError,
            "^applicability_status must be "
            "ExpectedValueAssumptionSetApplicabilityStatus$",
        ):
            validate_exact_expected_value_calculation(
                ExactExpectedValueCalculation(None, None)
            )

    def test_calculation_validator_status_result_invariant(self):
        status = ExpectedValueAssumptionSetApplicabilityStatus
        result = ExactExpectedValue(
            make_source(),
            Decimal("2"),
        )
        with patch(
            "ExactExpectedValue.validation"
            ".validate_exact_expected_value",
        ) as validator:
            self.assertIsNone(
                validate_exact_expected_value_calculation(
                    ExactExpectedValueCalculation(
                        status.APPLICABLE,
                        result,
                    )
                )
            )
        validator.assert_called_once_with(result)

        self.assertIsNone(
            validate_exact_expected_value_calculation(
                ExactExpectedValueCalculation(
                    status.PROBABILITY_TOTAL_MISMATCH,
                    None,
                )
            )
        )
        with self.assertRaisesRegex(
            TypeError,
            "^expected_value must be ExactExpectedValue "
            "when applicability_status is APPLICABLE$",
        ):
            validate_exact_expected_value_calculation(
                ExactExpectedValueCalculation(
                    status.APPLICABLE,
                    None,
                )
            )
        with self.assertRaisesRegex(
            ValueError,
            "^expected_value must be None when "
            "applicability_status is "
            "PROBABILITY_TOTAL_MISMATCH$",
        ):
            validate_exact_expected_value_calculation(
                ExactExpectedValueCalculation(
                    status.PROBABILITY_TOTAL_MISMATCH,
                    result,
                )
            )

    def test_calculator_validates_before_classification(self):
        source = make_source()
        calls = []

        def validate(value):
            calls.append(("validate", value))

        def classify(value):
            calls.append(("classify", value))
            return (
                ExpectedValueAssumptionSetApplicabilityStatus
                .PROBABILITY_TOTAL_MISMATCH
            )

        with patch(
            "ExactExpectedValue.calculation"
            ".validate_semantically_produced_"
            "expected_value_assumption_set",
            side_effect=validate,
        ) as validator, patch(
            "ExactExpectedValue.calculation"
            "._private"
            "._classify_expected_value_assumption_set_"
            "applicability_unchecked",
            side_effect=classify,
        ) as classifier:
            calculation = calculate_exact_expected_value(
                source
            )

        validator.assert_called_once_with(source)
        classifier.assert_called_once_with(
            source.assumption_set
        )
        self.assertEqual(
            calls,
            [
                ("validate", source),
                ("classify", source.assumption_set),
            ],
        )
        self.assertIsNone(calculation.expected_value)

    def test_calculator_propagates_source_exception_before_classification(
        self,
    ):
        source = make_source()
        error = ValueError("source failure")
        with patch(
            "ExactExpectedValue.calculation"
            ".validate_semantically_produced_"
            "expected_value_assumption_set",
            side_effect=error,
        ), patch(
            "ExactExpectedValue.calculation"
            "._private"
            "._classify_expected_value_assumption_set_"
            "applicability_unchecked",
        ) as classifier:
            with self.assertRaises(ValueError) as context:
                calculate_exact_expected_value(source)
        self.assertIs(context.exception, error)
        classifier.assert_not_called()

    def test_mismatch_performs_no_arithmetic(self):
        source = make_source()
        with patch(
            "ExactExpectedValue.calculation"
            ".validate_semantically_produced_"
            "expected_value_assumption_set",
        ), patch(
            "ExactExpectedValue.calculation"
            "._private"
            "._classify_expected_value_assumption_set_"
            "applicability_unchecked",
            return_value=(
                ExpectedValueAssumptionSetApplicabilityStatus
                .PROBABILITY_TOTAL_MISMATCH
            ),
        ), patch(
            "ExactExpectedValue.calculation"
            ".multiply_exact_decimal",
        ) as multiply, patch(
            "ExactExpectedValue.calculation"
            ".add_exact_decimal",
        ) as add:
            calculation = calculate_exact_expected_value(
                source
            )
        self.assertIs(
            calculation.applicability_status,
            ExpectedValueAssumptionSetApplicabilityStatus
            .PROBABILITY_TOTAL_MISMATCH,
        )
        self.assertIsNone(calculation.expected_value)
        multiply.assert_not_called()
        add.assert_not_called()

    def test_public_applicability_classifier_is_not_called(self):
        source = make_source()
        with patch(
            "ExpectedValueAssumptionSetApplicability"
            ".classification"
            ".classify_expected_value_assumption_set_applicability",
            side_effect=AssertionError(
                "public classifier must not be called"
            ),
        ), patch(
            "ExactExpectedValue.calculation"
            ".validate_semantically_produced_"
            "expected_value_assumption_set",
        ), patch(
            "ExactExpectedValue.calculation"
            "._private"
            "._classify_expected_value_assumption_set_"
            "applicability_unchecked",
            return_value=(
                ExpectedValueAssumptionSetApplicabilityStatus
                .PROBABILITY_TOTAL_MISMATCH
            ),
        ):
            calculation = calculate_exact_expected_value(
                source
            )
        self.assertIsNone(calculation.expected_value)

    def test_applicable_arithmetic_order_and_identity(self):
        outcomes = (
            make_outcome(
                "outcome-001",
                Decimal("0.2"),
                Decimal("10"),
            ),
            make_outcome(
                "outcome-002",
                Decimal("0.8"),
                Decimal("-1"),
            ),
        )
        source = make_source(outcomes)
        products = (
            Decimal("2.0"),
            Decimal("-0.8"),
        )
        totals = (
            Decimal("2.0"),
            Decimal("1.2"),
        )
        multiply_calls = []
        add_calls = []

        def multiply(left, right):
            multiply_calls.append((left, right))
            return products[len(multiply_calls) - 1]

        def add(left, right):
            add_calls.append((left, right))
            return totals[len(add_calls) - 1]

        with patch(
            "ExactExpectedValue.calculation"
            ".validate_semantically_produced_"
            "expected_value_assumption_set",
        ), patch(
            "ExactExpectedValue.calculation"
            "._private"
            "._classify_expected_value_assumption_set_"
            "applicability_unchecked",
            return_value=(
                ExpectedValueAssumptionSetApplicabilityStatus
                .APPLICABLE
            ),
        ), patch(
            "ExactExpectedValue.calculation"
            ".multiply_exact_decimal",
            side_effect=multiply,
        ) as multiply_mock, patch(
            "ExactExpectedValue.calculation"
            ".add_exact_decimal",
            side_effect=add,
        ) as add_mock:
            calculation = calculate_exact_expected_value(
                source
            )

        self.assertEqual(
            multiply_calls,
            [
                (
                    outcomes[0].probability,
                    outcomes[0].value,
                ),
                (
                    outcomes[1].probability,
                    outcomes[1].value,
                ),
            ],
        )
        self.assertEqual(
            add_calls,
            [
                (Decimal("0"), products[0]),
                (totals[0], products[1]),
            ],
        )
        self.assertEqual(multiply_mock.call_count, 2)
        self.assertEqual(add_mock.call_count, 2)
        self.assertIs(
            calculation.applicability_status,
            ExpectedValueAssumptionSetApplicabilityStatus
            .APPLICABLE,
        )
        self.assertIs(
            calculation.expected_value.source,
            source,
        )
        self.assertIs(
            calculation.expected_value.value,
            totals[-1],
        )

    def test_exact_expected_value_cases(self):
        cases = (
            (
                (
                    ("0.25", "20"),
                    ("0.75", "-4"),
                ),
                Decimal("2.00"),
            ),
            (
                (
                    ("0.5", "-10"),
                    ("0.5", "2"),
                ),
                Decimal("-4.0"),
            ),
            (
                (
                    ("0.5", "4"),
                    ("0.5", "-4"),
                ),
                Decimal("0.0"),
            ),
            (
                (
                    ("0.001", "1E+3"),
                    ("0.999", "0.001"),
                ),
                Decimal("1.000999"),
            ),
        )
        for values, expected in cases:
            with self.subTest(values=values):
                outcomes = tuple(
                    make_outcome(
                        f"outcome-{index}",
                        Decimal(probability),
                        Decimal(value),
                    )
                    for index, (probability, value)
                    in enumerate(values)
                )
                calculation = calculate_exact_expected_value(
                    make_source(outcomes)
                )
                self.assertEqual(
                    calculation.expected_value.value,
                    expected,
                )

    def test_source_graph_is_preserved(self):
        source = make_source()
        assumption_set = source.assumption_set
        outcomes = assumption_set.outcomes
        outcome_objects = tuple(outcomes)
        strings = tuple(
            (
                outcome.outcome_id,
                outcome.statement,
            )
            for outcome in outcomes
        )
        decimals = tuple(
            (
                outcome.probability,
                outcome.value,
            )
            for outcome in outcomes
        )
        calculation = calculate_exact_expected_value(source)
        self.assertIs(
            calculation.expected_value.source,
            source,
        )
        self.assertIs(source.assumption_set, assumption_set)
        self.assertIs(assumption_set.outcomes, outcomes)
        for index, outcome in enumerate(outcomes):
            self.assertIs(outcome, outcome_objects[index])
            self.assertIs(
                outcome.outcome_id,
                strings[index][0],
            )
            self.assertIs(
                outcome.statement,
                strings[index][1],
            )
            self.assertIs(
                outcome.probability,
                decimals[index][0],
            )
            self.assertIs(
                outcome.value,
                decimals[index][1],
            )

    def test_decimal_context_is_unchanged(self):
        outcomes = (
            make_outcome(
                "outcome-001",
                Decimal("0.5"),
                Decimal("9" * 80),
            ),
            make_outcome(
                "outcome-002",
                Decimal("0.5"),
                Decimal("1"),
            ),
        )
        with localcontext() as context:
            context.prec = 1
            context.rounding = "ROUND_DOWN"
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            context.traps[InvalidOperation] = False
            before = context.copy()

            calculation = calculate_exact_expected_value(
                make_source(outcomes)
            )

            self.assertEqual(
                calculation.expected_value.value,
                Decimal("5E+79"),
            )
            self.assertEqual(context.prec, before.prec)
            self.assertEqual(
                context.rounding,
                before.rounding,
            )
            self.assertEqual(context.flags, before.flags)
            self.assertEqual(context.traps, before.traps)

    def test_no_forbidden_arithmetic_constructs(self):
        path = Path(
            "ExactExpectedValue/calculation.py"
        )
        tree = ast.parse(path.read_text())
        forbidden = (
            ast.Mult,
            ast.Add,
        )
        for node in ast.walk(tree):
            self.assertNotIsInstance(node, forbidden)
            if isinstance(node, ast.Call):
                self.assertNotEqual(
                    getattr(node.func, "id", None),
                    "sum",
                )
                self.assertNotEqual(
                    getattr(node.func, "id", None),
                    "float",
                )
                self.assertNotEqual(
                    getattr(node.func, "id", None),
                    "Fraction",
                )

    def test_private_classifier_is_not_publicly_exported(self):
        self.assertFalse(
            hasattr(
                public_applicability,
                "_classify_expected_value_assumption_set_"
                "applicability_unchecked",
            )
        )
