import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import get_type_hints

from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)
from PortfolioMembership.validation import (
    validate_explicit_portfolio_membership,
)


def make_membership(**overrides):
    values = {
        "portfolio_id": "portfolio-001",
        "portfolio_subject_id": "subject-001",
    }
    values.update(overrides)
    return ExplicitPortfolioMembership(**values)


class StringSubclass(str):
    pass


class MembershipSubclass(ExplicitPortfolioMembership):
    pass


class ExplicitPortfolioMembershipTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(ExplicitPortfolioMembership)
        self.assertEqual(
            [field.name for field in model_fields],
            ["portfolio_id", "portfolio_subject_id"],
        )
        self.assertEqual(
            get_type_hints(ExplicitPortfolioMembership),
            {
                "portfolio_id": str,
                "portfolio_subject_id": str,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioMembership.__dict__,
        )

    def test_frozen_hashable_structural_equality(self):
        first = make_membership()
        same = make_membership()
        different = make_membership(
            portfolio_subject_id="subject-002"
        )
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.portfolio_id = "replacement"

    def test_exact_model_type_and_subclass_rejection(self):
        for value in (
            None,
            object(),
            {},
            MembershipSubclass(
                "portfolio-001",
                "subject-001",
            ),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^membership must be "
                    "ExplicitPortfolioMembership$",
                ):
                    validate_explicit_portfolio_membership(
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
                field="portfolio_id",
                value_type=type(value),
            ):
                with self.assertRaisesRegex(
                    TypeError,
                    "^portfolio_id must be str$",
                ):
                    validate_explicit_portfolio_membership(
                        make_membership(
                            portfolio_id=value
                        )
                    )
            with self.subTest(
                field="portfolio_subject_id",
                value_type=type(value),
            ):
                with self.assertRaisesRegex(
                    TypeError,
                    "^portfolio_subject_id must be str$",
                ):
                    validate_explicit_portfolio_membership(
                        make_membership(
                            portfolio_subject_id=value
                        )
                    )

    def test_blank_identifiers_are_rejected(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(
                field="portfolio_id",
                value=repr(value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^portfolio_id must not be blank$",
                ):
                    validate_explicit_portfolio_membership(
                        make_membership(
                            portfolio_id=value
                        )
                    )
            with self.subTest(
                field="portfolio_subject_id",
                value=repr(value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^portfolio_subject_id must not be blank$",
                ):
                    validate_explicit_portfolio_membership(
                        make_membership(
                            portfolio_subject_id=value
                        )
                    )

    def test_validation_order(self):
        cases = (
            (
                make_membership(
                    portfolio_id=None,
                    portfolio_subject_id=None,
                ),
                TypeError,
                "portfolio_id must be str",
            ),
            (
                make_membership(
                    portfolio_id=" ",
                    portfolio_subject_id=None,
                ),
                ValueError,
                "portfolio_id must not be blank",
            ),
            (
                make_membership(
                    portfolio_subject_id=None
                ),
                TypeError,
                "portfolio_subject_id must be str",
            ),
            (
                make_membership(
                    portfolio_subject_id=" "
                ),
                ValueError,
                "portfolio_subject_id must not be blank",
            ),
        )
        for membership, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_membership(
                        membership
                    )

    def test_success_preserves_identity_objects(self):
        portfolio_id = " portfolio-\u00e9 "
        subject_id = " subject-e\u0301 "
        membership = ExplicitPortfolioMembership(
            portfolio_id,
            subject_id,
        )
        self.assertIsNone(
            validate_explicit_portfolio_membership(
                membership
            )
        )
        self.assertIs(
            membership.portfolio_id,
            portfolio_id,
        )
        self.assertIs(
            membership.portfolio_subject_id,
            subject_id,
        )

    def test_duplicates_and_shared_endpoints_are_allowed(self):
        first = make_membership()
        duplicate = make_membership()
        shared_portfolio = make_membership(
            portfolio_subject_id="subject-002"
        )
        for membership in (
            first,
            duplicate,
            shared_portfolio,
        ):
            self.assertIsNone(
                validate_explicit_portfolio_membership(
                    membership
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
            {"PortfolioMembership.models"},
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolioMembership"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_portfolio_membership"
            ],
        )
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "membership_id",
            "position",
            "holding",
            "quantity",
            "price",
            "watchlist",
            "allocation",
            "lifecycle",
            "ticker",
            "runtime",
            "persistence",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
