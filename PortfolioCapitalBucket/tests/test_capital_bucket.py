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

from PortfolioCapitalBucket.models import (
    ExplicitPortfolioCapitalBucket,
)
from PortfolioCapitalBucket.validation import (
    validate_explicit_portfolio_capital_bucket,
)


def make_bucket(**overrides):
    values = {
        "capital_bucket_id": "bucket-001",
        "portfolio_id": "portfolio-001",
    }
    values.update(overrides)
    return ExplicitPortfolioCapitalBucket(**values)


class StringSubclass(str):
    pass


class BucketSubclass(ExplicitPortfolioCapitalBucket):
    pass


class PortfolioCapitalBucketTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertTrue(
            is_dataclass(ExplicitPortfolioCapitalBucket)
        )
        self.assertTrue(
            ExplicitPortfolioCapitalBucket
            .__dataclass_params__.frozen
        )
        model_fields = fields(
            ExplicitPortfolioCapitalBucket
        )
        self.assertEqual(
            [field.name for field in model_fields],
            ["capital_bucket_id", "portfolio_id"],
        )
        self.assertEqual(
            get_type_hints(ExplicitPortfolioCapitalBucket),
            {
                "capital_bucket_id": str,
                "portfolio_id": str,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitPortfolioCapitalBucket.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioCapitalBucket.__dict__,
        )
        public_methods = {
            name
            for name, value
            in ExplicitPortfolioCapitalBucket.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_frozen_hashable_and_structural_equality(self):
        first = make_bucket()
        same = make_bucket()
        different_identity = make_bucket(
            capital_bucket_id="bucket-002"
        )
        different_portfolio = make_bucket(
            portfolio_id="portfolio-002"
        )

        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(first, different_identity)
        self.assertNotEqual(first, different_portfolio)
        with self.assertRaises(FrozenInstanceError):
            first.capital_bucket_id = "replacement"

    def test_exact_bucket_type_is_required_first(self):
        invalid = (
            None,
            object(),
            {},
            (),
            BucketSubclass("bucket-001", "portfolio-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^bucket must be "
                    "ExplicitPortfolioCapitalBucket$",
                ):
                    validate_explicit_portfolio_capital_bucket(
                        value
                    )

    def test_capital_bucket_id_requires_exact_string(self):
        invalid = (
            None,
            1,
            b"bucket-001",
            StringSubclass("bucket-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^capital_bucket_id must be str$",
                ):
                    validate_explicit_portfolio_capital_bucket(
                        make_bucket(capital_bucket_id=value)
                    )

    def test_portfolio_id_requires_exact_string(self):
        invalid = (
            None,
            1,
            b"portfolio-001",
            StringSubclass("portfolio-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^portfolio_id must be str$",
                ):
                    validate_explicit_portfolio_capital_bucket(
                        make_bucket(portfolio_id=value)
                    )

    def test_empty_and_whitespace_only_values_are_rejected(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(
                field="capital_bucket_id",
                value=repr(value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^capital_bucket_id must not be blank$",
                ):
                    validate_explicit_portfolio_capital_bucket(
                        make_bucket(capital_bucket_id=value)
                    )
            with self.subTest(
                field="portfolio_id",
                value=repr(value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^portfolio_id must not be blank$",
                ):
                    validate_explicit_portfolio_capital_bucket(
                        make_bucket(portfolio_id=value)
                    )

    def test_surrounding_whitespace_and_objects_are_preserved(self):
        bucket_id = " bucket-é "
        portfolio_id = " portfolio-é "
        bucket = ExplicitPortfolioCapitalBucket(
            bucket_id,
            portfolio_id,
        )

        self.assertIsNone(
            validate_explicit_portfolio_capital_bucket(
                bucket
            )
        )
        self.assertIs(bucket.capital_bucket_id, bucket_id)
        self.assertIs(bucket.portfolio_id, portfolio_id)
        self.assertEqual(
            bucket.capital_bucket_id,
            " bucket-é ",
        )
        self.assertEqual(
            bucket.portfolio_id,
            " portfolio-é ",
        )

    def test_validation_order(self):
        cases = (
            (
                make_bucket(
                    capital_bucket_id=None,
                    portfolio_id=None,
                ),
                TypeError,
                "capital_bucket_id must be str",
            ),
            (
                make_bucket(
                    capital_bucket_id=" ",
                    portfolio_id=None,
                ),
                ValueError,
                "capital_bucket_id must not be blank",
            ),
            (
                make_bucket(portfolio_id=None),
                TypeError,
                "portfolio_id must be str",
            ),
            (
                make_bucket(portfolio_id=" "),
                ValueError,
                "portfolio_id must not be blank",
            ),
        )
        for bucket, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_capital_bucket(
                        bucket
                    )

    def test_success_returns_none(self):
        self.assertIsNone(
            validate_explicit_portfolio_capital_bucket(
                make_bucket()
            )
        )

    def test_uniqueness_is_not_enforced(self):
        first = make_bucket()
        duplicate = make_bucket()
        shared_portfolio = make_bucket(
            capital_bucket_id="bucket-002"
        )

        for bucket in (first, duplicate, shared_portfolio):
            self.assertIsNone(
                validate_explicit_portfolio_capital_bucket(
                    bucket
                )
            )
        self.assertEqual(first, duplicate)
        self.assertEqual(
            first.portfolio_id,
            shared_portfolio.portfolio_id,
        )

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
            {"PortfolioCapitalBucket.models"},
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolioCapitalBucket"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_portfolio_"
                "capital_bucket"
            ],
        )

    def test_forbidden_responsibilities_absent_from_production(self):
        root = Path(__file__).resolve().parents[1]
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "membership",
            "position",
            "holding",
            "watchlist",
            "snapshot",
            "cash",
            "quantity",
            "currency",
            "price",
            "cost_basis",
            "valuation",
            "profit",
            "loss",
            "percentage",
            "target_weight",
            "concentration",
            "risk_budget",
            "constraint",
            "recommendation",
            "allocation",
            "execution",
            "bucket_name",
            "label",
            "description",
            "category",
            "purpose",
            "taxonomy",
            "observation_context",
            "timestamp",
            "applicability",
            "semantic",
            "calculation",
            "lookup",
            "registry",
            "persistence",
            "migration",
            "runtime",
            "orchestration",
            "automation",
            "approval",
            "override",
            "audit",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
