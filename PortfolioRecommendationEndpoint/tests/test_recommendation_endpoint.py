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

from PortfolioRecommendationEndpoint.models import (
    ExplicitPortfolioRecommendationEndpoint,
)
from PortfolioRecommendationEndpoint.validation import (
    validate_explicit_portfolio_recommendation_endpoint,
)


def make_endpoint(**overrides):
    values = {
        "recommendation_id": "recommendation-001",
        "portfolio_snapshot_id": "snapshot-001",
    }
    values.update(overrides)
    return ExplicitPortfolioRecommendationEndpoint(**values)


class StringSubclass(str):
    pass


class EndpointSubclass(ExplicitPortfolioRecommendationEndpoint):
    pass


class PortfolioRecommendationEndpointTests(unittest.TestCase):
    def test_successful_model_construction(self):
        endpoint = ExplicitPortfolioRecommendationEndpoint(
            "recommendation-001",
            "snapshot-001",
        )
        self.assertEqual(
            endpoint.recommendation_id,
            "recommendation-001",
        )
        self.assertEqual(
            endpoint.portfolio_snapshot_id,
            "snapshot-001",
        )

    def test_exact_model_contract(self):
        self.assertTrue(
            is_dataclass(
                ExplicitPortfolioRecommendationEndpoint
            )
        )
        self.assertTrue(
            ExplicitPortfolioRecommendationEndpoint
            .__dataclass_params__.frozen
        )
        model_fields = fields(
            ExplicitPortfolioRecommendationEndpoint
        )
        self.assertEqual(
            [field.name for field in model_fields],
            ["recommendation_id", "portfolio_snapshot_id"],
        )
        self.assertEqual(
            get_type_hints(
                ExplicitPortfolioRecommendationEndpoint
            ),
            {
                "recommendation_id": str,
                "portfolio_snapshot_id": str,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitPortfolioRecommendationEndpoint.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioRecommendationEndpoint.__dict__,
        )
        public_methods = {
            name
            for name, value
            in ExplicitPortfolioRecommendationEndpoint
            .__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_frozen_hashable_and_structural_equality(self):
        first = make_endpoint()
        same = make_endpoint()
        different_identity = make_endpoint(
            recommendation_id="recommendation-002"
        )
        different_snapshot = make_endpoint(
            portfolio_snapshot_id="snapshot-002"
        )

        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(first, different_identity)
        self.assertNotEqual(first, different_snapshot)
        with self.assertRaises(FrozenInstanceError):
            first.recommendation_id = "replacement"

    def test_exact_model_type_is_required_first(self):
        invalid = (
            None,
            object(),
            {},
            (),
            EndpointSubclass(
                "recommendation-001",
                "snapshot-001",
            ),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^endpoint must be "
                    "ExplicitPortfolioRecommendationEndpoint$",
                ):
                    validate_explicit_portfolio_recommendation_endpoint(
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
                    validate_explicit_portfolio_recommendation_endpoint(
                        make_endpoint(recommendation_id=value)
                    )

    def test_portfolio_snapshot_id_requires_exact_string(self):
        invalid = (
            None,
            1,
            b"snapshot-001",
            StringSubclass("snapshot-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^portfolio_snapshot_id must be str$",
                ):
                    validate_explicit_portfolio_recommendation_endpoint(
                        make_endpoint(
                            portfolio_snapshot_id=value
                        )
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
                    validate_explicit_portfolio_recommendation_endpoint(
                        make_endpoint(recommendation_id=value)
                    )
            with self.subTest(
                field="portfolio_snapshot_id",
                value=repr(value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^portfolio_snapshot_id must not be blank$",
                ):
                    validate_explicit_portfolio_recommendation_endpoint(
                        make_endpoint(
                            portfolio_snapshot_id=value
                        )
                    )

    def test_surrounding_whitespace_and_objects_are_preserved(self):
        recommendation_id = " recommendation-é "
        portfolio_snapshot_id = " snapshot-é "
        endpoint = ExplicitPortfolioRecommendationEndpoint(
            recommendation_id,
            portfolio_snapshot_id,
        )

        self.assertIsNone(
            validate_explicit_portfolio_recommendation_endpoint(
                endpoint
            )
        )
        self.assertIs(
            endpoint.recommendation_id,
            recommendation_id,
        )
        self.assertIs(
            endpoint.portfolio_snapshot_id,
            portfolio_snapshot_id,
        )
        self.assertEqual(
            endpoint.recommendation_id,
            " recommendation-é ",
        )
        self.assertEqual(
            endpoint.portfolio_snapshot_id,
            " snapshot-é ",
        )

    def test_validation_order(self):
        cases = (
            (
                make_endpoint(
                    recommendation_id=None,
                    portfolio_snapshot_id=None,
                ),
                TypeError,
                "recommendation_id must be str",
            ),
            (
                make_endpoint(
                    recommendation_id=" ",
                    portfolio_snapshot_id=None,
                ),
                ValueError,
                "recommendation_id must not be blank",
            ),
            (
                make_endpoint(portfolio_snapshot_id=None),
                TypeError,
                "portfolio_snapshot_id must be str",
            ),
            (
                make_endpoint(portfolio_snapshot_id=" "),
                ValueError,
                "portfolio_snapshot_id must not be blank",
            ),
        )
        for endpoint, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_recommendation_endpoint(
                        endpoint
                    )

    def test_success_returns_none(self):
        self.assertIsNone(
            validate_explicit_portfolio_recommendation_endpoint(
                make_endpoint()
            )
        )

    def test_multiple_recommendations_share_snapshot(self):
        first = make_endpoint(
            recommendation_id="recommendation-001"
        )
        second = make_endpoint(
            recommendation_id="recommendation-002"
        )

        self.assertIsNone(
            validate_explicit_portfolio_recommendation_endpoint(
                first
            )
        )
        self.assertIsNone(
            validate_explicit_portfolio_recommendation_endpoint(
                second
            )
        )
        self.assertNotEqual(first, second)
        self.assertEqual(
            first.portfolio_snapshot_id,
            second.portfolio_snapshot_id,
        )

    def test_uniqueness_and_existence_are_not_enforced(self):
        first = make_endpoint()
        duplicate = make_endpoint()
        for endpoint in (first, duplicate):
            self.assertIsNone(
                validate_explicit_portfolio_recommendation_endpoint(
                    endpoint
                )
            )
        self.assertEqual(first, duplicate)

    def test_dependency_scope_and_public_api_are_exact(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (root / "models.py").read_text()
        )
        validation_tree = ast.parse(
            (root / "validation.py").read_text()
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(model_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {"dataclasses"},
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {"PortfolioRecommendationEndpoint.models"},
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolioRecommendationEndpoint"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_portfolio_"
                "recommendation_endpoint"
            ],
        )

    def test_forbidden_responsibilities_absent_from_production(self):
        root = Path(__file__).resolve().parents[1]
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "ExplicitPortfolioSnapshot",
            "portfolio_id",
            "action",
            "direction",
            "BUY",
            "HOLD",
            "SELL",
            "trade_instruction",
            "target",
            "subject",
            "instrument",
            "position",
            "membership",
            "capital_bucket",
            "risk_budget",
            "rationale",
            "confidence",
            "priority",
            "ranking",
            "conviction",
            "urgency",
            "materiality",
            "PortfolioImpact",
            "ExpectedValue",
            "evidence",
            "thesis",
            "hypothesis",
            "signal",
            "allocation",
            "capital_movement",
            "quantity",
            "amount",
            "currency",
            "unit",
            "percentage",
            "target_weight",
            "cash_routing",
            "limit",
            "threshold",
            "constraint",
            "policy",
            "breach",
            "approval",
            "rejection",
            "override",
            "execution",
            "audit",
            "timestamp",
            "label",
            "description",
            "category",
            "taxonomy",
            "lookup",
            "registry",
            "repository",
            "resolver",
            "mapping",
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
