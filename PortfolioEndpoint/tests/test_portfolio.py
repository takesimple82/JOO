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

from PortfolioEndpoint.models import ExplicitPortfolio
from PortfolioEndpoint.validation import (
    validate_explicit_portfolio,
)


def make_portfolio(**overrides):
    values = {
        "portfolio_id": "portfolio-001",
    }
    values.update(overrides)
    return ExplicitPortfolio(**values)


class StringSubclass(str):
    pass


class PortfolioSubclass(ExplicitPortfolio):
    pass


class ExplicitPortfolioTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            ExplicitPortfolio.__name__,
            "ExplicitPortfolio",
        )
        self.assertTrue(is_dataclass(ExplicitPortfolio))
        self.assertTrue(
            ExplicitPortfolio.__dataclass_params__.frozen
        )

        model_fields = fields(ExplicitPortfolio)
        self.assertEqual(
            [field.name for field in model_fields],
            ["portfolio_id"],
        )
        self.assertEqual(
            get_type_hints(ExplicitPortfolio),
            {"portfolio_id": str},
        )
        self.assertEqual(len(model_fields), 1)
        self.assertIs(model_fields[0].default, MISSING)
        self.assertIs(
            model_fields[0].default_factory,
            MISSING,
        )
        self.assertNotIn(
            "__post_init__",
            ExplicitPortfolio.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolio.__dict__,
        )
        public_methods = {
            name
            for name, value
            in ExplicitPortfolio.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_model_is_frozen_hashable_and_structural(self):
        first = make_portfolio()
        same = make_portfolio()
        different = make_portfolio(
            portfolio_id="portfolio-002"
        )

        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.portfolio_id = "replacement"

    def test_unknown_constructor_fields_fail_naturally(self):
        for field_name in (
            "name",
            "ticker",
            "subject_id",
            "owner",
        ):
            with self.subTest(field_name=field_name):
                with self.assertRaises(TypeError):
                    ExplicitPortfolio(
                        portfolio_id="portfolio-001",
                        **{field_name: "not-owned"},
                    )

    def test_validator_returns_none_on_success(self):
        self.assertIsNone(
            validate_explicit_portfolio(
                make_portfolio()
            )
        )

    def test_validator_requires_exact_model_type_first(self):
        invalid = (
            None,
            object(),
            {},
            (),
            PortfolioSubclass("portfolio-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^portfolio must be ExplicitPortfolio$",
                ):
                    validate_explicit_portfolio(value)

    def test_portfolio_id_requires_exact_built_in_string(self):
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
                    validate_explicit_portfolio(
                        make_portfolio(
                            portfolio_id=value
                        )
                    )

    def test_portfolio_id_rejects_blank_values(self):
        for value in (
            "",
            " ",
            "\t",
            "\n",
            " \t\n ",
        ):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^portfolio_id must not be blank$",
                ):
                    validate_explicit_portfolio(
                        make_portfolio(
                            portfolio_id=value
                        )
                    )

    def test_identity_is_preserved_without_normalization(self):
        portfolio_id = " portfolio-\u00e9 "
        portfolio = ExplicitPortfolio(portfolio_id)
        model_identity = id(portfolio)

        result = validate_explicit_portfolio(portfolio)

        self.assertIsNone(result)
        self.assertEqual(id(portfolio), model_identity)
        self.assertIs(
            portfolio.portfolio_id,
            portfolio_id,
        )
        self.assertEqual(
            portfolio.portfolio_id,
            " portfolio-\u00e9 ",
        )

    def test_identity_equality_does_not_normalize(self):
        distinct_pairs = (
            ("portfolio", "PORTFOLIO"),
            ("portfolio", " portfolio "),
            ("\u00e9", "e\u0301"),
        )
        for left, right in distinct_pairs:
            with self.subTest(
                left=repr(left),
                right=repr(right),
            ):
                self.assertNotEqual(
                    ExplicitPortfolio(left),
                    ExplicitPortfolio(right),
                )

    def test_duplicate_identity_is_not_checked(self):
        first = ExplicitPortfolio("portfolio-001")
        second = ExplicitPortfolio("portfolio-001")

        self.assertIsNone(
            validate_explicit_portfolio(first)
        )
        self.assertIsNone(
            validate_explicit_portfolio(second)
        )
        self.assertEqual(first, second)

    def test_dependency_and_scope_are_minimal(self):
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
            {"PortfolioEndpoint.models"},
        )

        production_source = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "PortfolioSubject",
            "subject_id",
            "proposition_id",
            "entity_id",
            "portfolio_version",
            "ticker",
            "security",
            "membership",
            "position",
            "holding",
            "watchlist",
            "snapshot",
            "allocation",
            "recommendation",
            "runtime",
            "persistence",
        ):
            self.assertNotIn(
                forbidden,
                production_source,
            )

    def test_public_symbols_are_exact(self):
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
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolio"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["validate_explicit_portfolio"],
        )


if __name__ == "__main__":
    unittest.main()
