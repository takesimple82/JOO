import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

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
from SemanticPortfolioImpactProduction.validation import (
    validate_semantically_produced_portfolio_impact,
)
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)
from ThesisPortfolioSubjectLink.models import (
    ExplicitThesisPortfolioSubjectLink,
)


def make_impact():
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
    return ExplicitPortfolioImpact(
        "impact-001",
        thesis,
        link,
        subject,
        policy,
        PortfolioImpactDirection.BENEFICIAL,
        "long-term",
        "Caller-supplied rationale.",
    )


class ProductionSubclass(SemanticallyProducedPortfolioImpact):
    pass


class ImpactSubclass(ExplicitPortfolioImpact):
    pass


class SemanticPortfolioImpactProductionTests(
    unittest.TestCase
):
    def test_exact_model_contract(self):
        model_fields = fields(
            SemanticallyProducedPortfolioImpact
        )
        self.assertEqual(
            [field.name for field in model_fields],
            ["impact"],
        )
        self.assertEqual(
            get_type_hints(
                SemanticallyProducedPortfolioImpact
            ),
            {"impact": ExplicitPortfolioImpact},
        )
        self.assertIs(model_fields[0].default, MISSING)
        self.assertIs(
            model_fields[0].default_factory,
            MISSING,
        )
        self.assertNotIn(
            "__slots__",
            SemanticallyProducedPortfolioImpact.__dict__,
        )

    def test_frozen_hashable_structural_equality(self):
        impact = make_impact()
        first = SemanticallyProducedPortfolioImpact(impact)
        same = SemanticallyProducedPortfolioImpact(impact)
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        with self.assertRaises(FrozenInstanceError):
            first.impact = make_impact()

    def test_exact_production_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "^production must be "
            "SemanticallyProducedPortfolioImpact$",
        ):
            validate_semantically_produced_portfolio_impact(
                ProductionSubclass(make_impact())
            )

    def test_exact_impact_type(self):
        impact = make_impact()
        subclass = ImpactSubclass(
            **{
                field.name: getattr(impact, field.name)
                for field in fields(ExplicitPortfolioImpact)
            }
        )
        for value in (None, object(), subclass):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^impact must be ExplicitPortfolioImpact$",
                ):
                    validate_semantically_produced_portfolio_impact(
                        SemanticallyProducedPortfolioImpact(
                            value
                        )
                    )

    def test_upstream_validator_called_once_with_original(self):
        impact = make_impact()
        production = SemanticallyProducedPortfolioImpact(
            impact
        )
        with patch(
            "SemanticPortfolioImpactProduction.validation"
            ".validate_explicit_portfolio_impact",
        ) as validator:
            result = (
                validate_semantically_produced_portfolio_impact(
                    production
                )
            )
        self.assertIsNone(result)
        validator.assert_called_once_with(impact)
        self.assertIs(
            validator.call_args.args[0],
            impact,
        )

    def test_upstream_exception_object_propagates_unchanged(self):
        error = ValueError("impact failure")
        with patch(
            "SemanticPortfolioImpactProduction.validation"
            ".validate_explicit_portfolio_impact",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                validate_semantically_produced_portfolio_impact(
                    SemanticallyProducedPortfolioImpact(
                        make_impact()
                    )
                )
        self.assertIs(context.exception, error)

    def test_impact_object_identity_is_preserved(self):
        impact = make_impact()
        production = SemanticallyProducedPortfolioImpact(
            impact
        )
        self.assertIsNone(
            validate_semantically_produced_portfolio_impact(
                production
            )
        )
        self.assertIs(production.impact, impact)

    def test_duplicate_wrappers_are_allowed(self):
        impact = make_impact()
        first = SemanticallyProducedPortfolioImpact(impact)
        duplicate = SemanticallyProducedPortfolioImpact(
            impact
        )
        self.assertIsNone(
            validate_semantically_produced_portfolio_impact(
                first
            )
        )
        self.assertIsNone(
            validate_semantically_produced_portfolio_impact(
                duplicate
            )
        )
        self.assertEqual(first, duplicate)

    def test_production_surface_and_dependency_direction(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (root / "models.py").read_text()
        )
        validation_tree = ast.parse(
            (root / "validation.py").read_text()
        )
        functions = [
            node.name
            for node in validation_tree.body
            if isinstance(node, ast.FunctionDef)
        ]
        self.assertEqual(
            functions,
            [
                "validate_semantically_produced_portfolio_impact"
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
                "ExplicitPortfolioImpact.models",
                "ExplicitPortfolioImpact.validation",
                "SemanticPortfolioImpactProduction.models",
            },
        )


if __name__ == "__main__":
    unittest.main()
