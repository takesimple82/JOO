import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import get_type_hints

from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioObservationContext.validation import (
    validate_explicit_portfolio_observation_context,
)


def make_context(**overrides):
    values = {
        "observation_context_id": "context-001",
        "portfolio_id": "portfolio-001",
    }
    values.update(overrides)
    return ExplicitPortfolioObservationContext(**values)


class StringSubclass(str):
    pass


class ContextSubclass(
    ExplicitPortfolioObservationContext
):
    pass


class PortfolioObservationContextTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(
            ExplicitPortfolioObservationContext
        )
        self.assertEqual(
            [field.name for field in model_fields],
            [
                "observation_context_id",
                "portfolio_id",
            ],
        )
        self.assertEqual(
            get_type_hints(
                ExplicitPortfolioObservationContext
            ),
            {
                "observation_context_id": str,
                "portfolio_id": str,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioObservationContext.__dict__,
        )

    def test_frozen_hashable_structural_equality(self):
        first = make_context()
        same = make_context()
        different = make_context(
            observation_context_id="context-002"
        )
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.portfolio_id = "replacement"

    def test_exact_model_type(self):
        for value in (
            None,
            object(),
            {},
            ContextSubclass(
                "context-001",
                "portfolio-001",
            ),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^context must be "
                    "ExplicitPortfolioObservationContext$",
                ):
                    validate_explicit_portfolio_observation_context(
                        value
                    )

    def test_exact_string_types(self):
        invalid = (
            None,
            1,
            b"identity",
            StringSubclass("identity"),
        )
        for value in invalid:
            with self.subTest(
                field="observation_context_id",
                value_type=type(value),
            ):
                with self.assertRaisesRegex(
                    TypeError,
                    "^observation_context_id must be str$",
                ):
                    validate_explicit_portfolio_observation_context(
                        make_context(
                            observation_context_id=value
                        )
                    )
            with self.subTest(
                field="portfolio_id",
                value_type=type(value),
            ):
                with self.assertRaisesRegex(
                    TypeError,
                    "^portfolio_id must be str$",
                ):
                    validate_explicit_portfolio_observation_context(
                        make_context(portfolio_id=value)
                    )

    def test_blank_identifiers_are_rejected(self):
        for value in ("", " ", "\t\n"):
            with self.subTest(
                field="observation_context_id",
                value=repr(value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^observation_context_id "
                    "must not be blank$",
                ):
                    validate_explicit_portfolio_observation_context(
                        make_context(
                            observation_context_id=value
                        )
                    )
            with self.subTest(
                field="portfolio_id",
                value=repr(value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^portfolio_id must not be blank$",
                ):
                    validate_explicit_portfolio_observation_context(
                        make_context(portfolio_id=value)
                    )

    def test_validation_order(self):
        cases = (
            (
                make_context(
                    observation_context_id=None,
                    portfolio_id=None,
                ),
                TypeError,
                "observation_context_id must be str",
            ),
            (
                make_context(
                    observation_context_id=" ",
                    portfolio_id=None,
                ),
                ValueError,
                "observation_context_id "
                "must not be blank",
            ),
            (
                make_context(portfolio_id=None),
                TypeError,
                "portfolio_id must be str",
            ),
            (
                make_context(portfolio_id=" "),
                ValueError,
                "portfolio_id must not be blank",
            ),
        )
        for context, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_observation_context(
                        context
                    )

    def test_success_preserves_identifiers(self):
        context_id = " context-\u00e9 "
        portfolio_id = " portfolio-e\u0301 "
        context = ExplicitPortfolioObservationContext(
            context_id,
            portfolio_id,
        )
        self.assertIsNone(
            validate_explicit_portfolio_observation_context(
                context
            )
        )
        self.assertIs(
            context.observation_context_id,
            context_id,
        )
        self.assertIs(context.portfolio_id, portfolio_id)

    def test_duplicate_contexts_are_not_checked(self):
        first = make_context()
        duplicate = make_context()
        for context in (first, duplicate):
            self.assertIsNone(
                validate_explicit_portfolio_observation_context(
                    context
                )
            )
        self.assertEqual(first, duplicate)

    def test_scope_dependencies_and_public_api(self):
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
            {"PortfolioObservationContext.models"},
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolioObservationContext"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_portfolio_"
                "observation_context"
            ],
        )
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "timestamp",
            "observed_on",
            "ResearchSnapshot",
            "portfolio_version",
            "holding",
            "quantity",
            "price",
            "valuation",
            "recommendation",
            "allocation",
            "runtime",
            "persistence",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
