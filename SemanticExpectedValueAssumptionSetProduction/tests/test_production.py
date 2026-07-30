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
from ExplicitPortfolioImpact.models import (
    ExplicitPortfolioImpact,
)
from ExplicitThesis.models import ExplicitThesis
from PortfolioDomain.models import PortfolioSubject
from PortfolioImpactInterpretationPolicy.models import (
    PortfolioImpactDirection,
    PortfolioImpactInterpretationPolicy,
)
from SemanticExpectedValueAssumptionSetProduction.models import (
    SemanticallyProducedExpectedValueAssumptionSet,
)
from SemanticExpectedValueAssumptionSetProduction.validation import (
    validate_semantically_produced_expected_value_assumption_set,
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


def make_assumption_set():
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
    impact = SemanticallyProducedPortfolioImpact(
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
    return ExplicitExpectedValueAssumptionSet(
        "assumptions-001",
        impact,
        "USD",
        (
            ExplicitExpectedValueOutcomeAssumption(
                "outcome-001",
                "An outcome.",
                Decimal("1"),
                Decimal("10"),
            ),
        ),
    )


class ProductionSubclass(
    SemanticallyProducedExpectedValueAssumptionSet
):
    pass


class AssumptionSetSubclass(ExplicitExpectedValueAssumptionSet):
    pass


class SemanticExpectedValueAssumptionSetProductionTests(
    unittest.TestCase
):
    def test_exact_model_contract(self):
        model_fields = fields(
            SemanticallyProducedExpectedValueAssumptionSet
        )
        self.assertEqual(
            [field.name for field in model_fields],
            ["assumption_set"],
        )
        self.assertEqual(
            get_type_hints(
                SemanticallyProducedExpectedValueAssumptionSet
            ),
            {
                "assumption_set": (
                    ExplicitExpectedValueAssumptionSet
                )
            },
        )
        self.assertIs(model_fields[0].default, MISSING)
        self.assertIs(
            model_fields[0].default_factory,
            MISSING,
        )
        self.assertNotIn(
            "__slots__",
            SemanticallyProducedExpectedValueAssumptionSet
            .__dict__,
        )

    def test_frozen_hashable_structural_equality(self):
        assumption_set = make_assumption_set()
        first = (
            SemanticallyProducedExpectedValueAssumptionSet(
                assumption_set
            )
        )
        same = (
            SemanticallyProducedExpectedValueAssumptionSet(
                assumption_set
            )
        )
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        with self.assertRaises(FrozenInstanceError):
            first.assumption_set = make_assumption_set()

    def test_exact_production_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "^production must be "
            "SemanticallyProducedExpectedValueAssumptionSet$",
        ):
            validate_semantically_produced_expected_value_assumption_set(
                ProductionSubclass(make_assumption_set())
            )

    def test_exact_assumption_set_type(self):
        assumption_set = make_assumption_set()
        subclass = AssumptionSetSubclass(
            assumption_set.assumption_set_id,
            assumption_set.impact,
            assumption_set.unit_id,
            assumption_set.outcomes,
        )
        for value in (None, object(), subclass):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^assumption_set must be "
                    "ExplicitExpectedValueAssumptionSet$",
                ):
                    validate_semantically_produced_expected_value_assumption_set(
                        SemanticallyProducedExpectedValueAssumptionSet(
                            value
                        )
                    )

    def test_upstream_validator_called_once_with_original(self):
        assumption_set = make_assumption_set()
        production = (
            SemanticallyProducedExpectedValueAssumptionSet(
                assumption_set
            )
        )
        with patch(
            "SemanticExpectedValueAssumptionSetProduction"
            ".validation"
            ".validate_explicit_expected_value_assumption_set",
        ) as validator:
            result = (
                validate_semantically_produced_expected_value_assumption_set(
                    production
                )
            )
        self.assertIsNone(result)
        validator.assert_called_once_with(assumption_set)
        self.assertIs(
            validator.call_args.args[0],
            assumption_set,
        )

    def test_upstream_exception_object_propagates_unchanged(self):
        error = ValueError("assumption failure")
        with patch(
            "SemanticExpectedValueAssumptionSetProduction"
            ".validation"
            ".validate_explicit_expected_value_assumption_set",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                validate_semantically_produced_expected_value_assumption_set(
                    SemanticallyProducedExpectedValueAssumptionSet(
                        make_assumption_set()
                    )
                )
        self.assertIs(context.exception, error)

    def test_object_identity_and_duplicates_are_preserved(self):
        assumption_set = make_assumption_set()
        first = (
            SemanticallyProducedExpectedValueAssumptionSet(
                assumption_set
            )
        )
        duplicate = (
            SemanticallyProducedExpectedValueAssumptionSet(
                assumption_set
            )
        )
        self.assertIsNone(
            validate_semantically_produced_expected_value_assumption_set(
                first
            )
        )
        self.assertIsNone(
            validate_semantically_produced_expected_value_assumption_set(
                duplicate
            )
        )
        self.assertIs(first.assumption_set, assumption_set)
        self.assertIs(
            duplicate.assumption_set,
            assumption_set,
        )
        self.assertEqual(first, duplicate)

    def test_probability_total_is_not_attested(self):
        assumption_set = make_assumption_set()
        incomplete = ExplicitExpectedValueAssumptionSet(
            assumption_set.assumption_set_id,
            assumption_set.impact,
            assumption_set.unit_id,
            (
                ExplicitExpectedValueOutcomeAssumption(
                    "outcome-001",
                    "An outcome.",
                    Decimal("0.2"),
                    Decimal("10"),
                ),
            ),
        )
        self.assertIsNone(
            validate_semantically_produced_expected_value_assumption_set(
                SemanticallyProducedExpectedValueAssumptionSet(
                    incomplete
                )
            )
        )

    def test_production_surface_and_dependency_direction(self):
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
                "validate_semantically_produced_expected_value_assumption_set"
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
                "ExpectedValueAssumptionSet.models",
                "ExpectedValueAssumptionSet.validation",
                "SemanticExpectedValueAssumptionSetProduction.models",
            },
        )


if __name__ == "__main__":
    unittest.main()
