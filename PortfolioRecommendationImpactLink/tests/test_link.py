import ast
import unittest
from dataclasses import (
    FrozenInstanceError,
    MISSING,
    fields,
    is_dataclass,
)
from pathlib import Path
from typing import get_type_hints

from PortfolioRecommendationImpactLink.models import (
    ExplicitPortfolioRecommendationImpactLink,
)
from PortfolioRecommendationImpactLink.validation import (
    validate_explicit_portfolio_recommendation_impact_link,
)


def make_link(**overrides):
    values = {
        "recommendation_id": "recommendation-001",
        "impact_id": "impact-001",
    }
    values.update(overrides)
    return ExplicitPortfolioRecommendationImpactLink(**values)


class StringSubclass(str):
    pass


class LinkSubclass(ExplicitPortfolioRecommendationImpactLink):
    pass


class PortfolioRecommendationImpactLinkTests(unittest.TestCase):
    def test_successful_model_construction(self):
        link = ExplicitPortfolioRecommendationImpactLink(
            "recommendation-001",
            "impact-001",
        )
        self.assertEqual(
            link.recommendation_id,
            "recommendation-001",
        )
        self.assertEqual(link.impact_id, "impact-001")

    def test_exact_model_contract(self):
        self.assertTrue(
            is_dataclass(
                ExplicitPortfolioRecommendationImpactLink
            )
        )
        self.assertTrue(
            ExplicitPortfolioRecommendationImpactLink
            .__dataclass_params__.frozen
        )
        model_fields = fields(
            ExplicitPortfolioRecommendationImpactLink
        )
        self.assertEqual(
            [field.name for field in model_fields],
            ["recommendation_id", "impact_id"],
        )
        self.assertEqual(
            get_type_hints(
                ExplicitPortfolioRecommendationImpactLink
            ),
            {
                "recommendation_id": str,
                "impact_id": str,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitPortfolioRecommendationImpactLink.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioRecommendationImpactLink.__dict__,
        )
        public_methods = {
            name
            for name, value
            in ExplicitPortfolioRecommendationImpactLink
            .__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_frozen_hashable_and_structural_equality(self):
        first = make_link()
        same = make_link()
        different_recommendation = make_link(
            recommendation_id="recommendation-002"
        )
        different_impact = make_link(
            impact_id="impact-002"
        )

        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(first, different_recommendation)
        self.assertNotEqual(first, different_impact)
        with self.assertRaises(FrozenInstanceError):
            first.recommendation_id = "replacement"

    def test_unknown_and_redundant_fields_fail_naturally(self):
        forbidden_fields = (
            "link_id",
            "portfolio_snapshot_id",
            "portfolio_id",
            "thesis_id",
            "assumption_set_id",
            "proposition_id",
            "finding_id",
        )
        for field_name in forbidden_fields:
            with self.subTest(field_name=field_name):
                with self.assertRaises(TypeError):
                    ExplicitPortfolioRecommendationImpactLink(
                        recommendation_id="recommendation-001",
                        impact_id="impact-001",
                        **{field_name: "not-owned"},
                    )

    def test_exact_model_type_is_required_first(self):
        invalid = (
            None,
            object(),
            {},
            (),
            LinkSubclass(
                "recommendation-001",
                "impact-001",
            ),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^link must be "
                    "ExplicitPortfolioRecommendationImpactLink$",
                ):
                    validate_explicit_portfolio_recommendation_impact_link(
                        value
                    )

    def test_recommendation_id_requires_exact_string(self):
        invalid = (
            None,
            1,
            b"recommendation-001",
            StringSubclass("recommendation-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^recommendation_id must be str$",
                ):
                    validate_explicit_portfolio_recommendation_impact_link(
                        make_link(recommendation_id=value)
                    )

    def test_impact_id_requires_exact_string(self):
        invalid = (
            None,
            1,
            b"impact-001",
            StringSubclass("impact-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^impact_id must be str$",
                ):
                    validate_explicit_portfolio_recommendation_impact_link(
                        make_link(impact_id=value)
                    )

    def test_blank_and_whitespace_only_values_are_rejected(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(
                field="recommendation_id",
                value=repr(value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^recommendation_id must not be blank$",
                ):
                    validate_explicit_portfolio_recommendation_impact_link(
                        make_link(recommendation_id=value)
                    )
            with self.subTest(
                field="impact_id",
                value=repr(value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^impact_id must not be blank$",
                ):
                    validate_explicit_portfolio_recommendation_impact_link(
                        make_link(impact_id=value)
                    )

    def test_surrounding_whitespace_and_objects_are_preserved(self):
        recommendation_id = " recommendation-é "
        impact_id = " impact-é "
        link = ExplicitPortfolioRecommendationImpactLink(
            recommendation_id,
            impact_id,
        )

        self.assertIsNone(
            validate_explicit_portfolio_recommendation_impact_link(
                link
            )
        )
        self.assertIs(link.recommendation_id, recommendation_id)
        self.assertIs(link.impact_id, impact_id)
        self.assertEqual(
            link.recommendation_id,
            " recommendation-é ",
        )
        self.assertEqual(link.impact_id, " impact-é ")

    def test_validation_order(self):
        cases = (
            (
                make_link(
                    recommendation_id=None,
                    impact_id=None,
                ),
                TypeError,
                "recommendation_id must be str",
            ),
            (
                make_link(
                    recommendation_id=" ",
                    impact_id=None,
                ),
                ValueError,
                "recommendation_id must not be blank",
            ),
            (
                make_link(impact_id=None),
                TypeError,
                "impact_id must be str",
            ),
            (
                make_link(impact_id=" "),
                ValueError,
                "impact_id must not be blank",
            ),
        )
        for link, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_recommendation_impact_link(
                        link
                    )

    def test_success_returns_none(self):
        self.assertIsNone(
            validate_explicit_portfolio_recommendation_impact_link(
                make_link()
            )
        )

    def test_multiplicity_and_duplicate_pairs_are_allowed(self):
        first = make_link()
        duplicate = make_link()
        shared_recommendation = make_link(
            impact_id="impact-002"
        )
        shared_impact = make_link(
            recommendation_id="recommendation-002"
        )

        for link in (
            first,
            duplicate,
            shared_recommendation,
            shared_impact,
        ):
            self.assertIsNone(
                validate_explicit_portfolio_recommendation_impact_link(
                    link
                )
            )
        self.assertEqual(first, duplicate)
        self.assertEqual(
            first.recommendation_id,
            shared_recommendation.recommendation_id,
        )
        self.assertEqual(
            first.impact_id,
            shared_impact.impact_id,
        )

    def test_identifier_representation_is_not_normalized(self):
        self.assertNotEqual(
            make_link(recommendation_id="value"),
            make_link(recommendation_id="VALUE"),
        )
        self.assertNotEqual(
            make_link(impact_id="é"),
            make_link(impact_id="é"),
        )

    def test_dependency_scope_and_public_api_are_exact(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (root / "models.py").read_text()
        )
        validation_tree = ast.parse(
            (root / "validation.py").read_text()
        )
        model_imports = [
            node
            for node in ast.walk(model_tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        self.assertEqual(len(model_imports), 1)
        self.assertIsInstance(model_imports[0], ast.ImportFrom)
        self.assertEqual(model_imports[0].module, "dataclasses")

        validation_imports = [
            node
            for node in ast.walk(validation_tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        self.assertEqual(len(validation_imports), 1)
        self.assertEqual(
            validation_imports[0].module,
            "PortfolioRecommendationImpactLink.models",
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolioRecommendationImpactLink"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_portfolio_"
                "recommendation_impact_link"
            ],
        )
        self.assertFalse(
            any(
                isinstance(node, (ast.For, ast.While))
                for node in ast.walk(validation_tree)
            )
        )

    def test_forbidden_behavior_absent_from_production(self):
        root = Path(__file__).resolve().parents[1]
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "link_id",
            "portfolio_snapshot_id",
            "portfolio_id",
            "thesis_id",
            "assumption_set_id",
            "proposition_id",
            "finding_id",
            "lookup",
            "registry",
            "repository",
            "resolver",
            "applicability",
            "uniqueness",
            "ranking",
            "completeness",
            "causal",
            "support",
            "semantic",
            "allocation",
            "constraint",
            "approval",
            "audit",
            "persistence",
            "migration",
            "runtime",
            "orchestration",
            "automation",
            "scheduling",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
