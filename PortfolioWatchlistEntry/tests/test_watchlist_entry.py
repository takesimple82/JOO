import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)
from PortfolioWatchlistEntry.models import (
    ExplicitPortfolioWatchlistEntry,
)
from PortfolioWatchlistEntry.validation import (
    validate_explicit_portfolio_watchlist_entry,
)


def make_membership(**overrides):
    values = {
        "portfolio_id": "portfolio-001",
        "portfolio_subject_id": "subject-001",
    }
    values.update(overrides)
    return ExplicitPortfolioMembership(**values)


def make_entry(**overrides):
    values = {"membership": make_membership()}
    values.update(overrides)
    return ExplicitPortfolioWatchlistEntry(**values)


class EntrySubclass(ExplicitPortfolioWatchlistEntry):
    pass


class MembershipSubclass(ExplicitPortfolioMembership):
    pass


class PortfolioWatchlistEntryTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(
            ExplicitPortfolioWatchlistEntry
        )
        self.assertEqual(
            [field.name for field in model_fields],
            ["membership"],
        )
        self.assertEqual(
            get_type_hints(
                ExplicitPortfolioWatchlistEntry
            ),
            {"membership": ExplicitPortfolioMembership},
        )
        self.assertEqual(len(model_fields), 1)
        self.assertIs(model_fields[0].default, MISSING)
        self.assertIs(
            model_fields[0].default_factory,
            MISSING,
        )
        self.assertNotIn(
            "__post_init__",
            ExplicitPortfolioWatchlistEntry.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioWatchlistEntry.__dict__,
        )

    def test_frozen_hashable_and_structural(self):
        first = make_entry()
        same = make_entry()
        different = make_entry(
            membership=make_membership(
                portfolio_subject_id="subject-002"
            )
        )
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.membership = make_membership()

    def test_exact_entry_type_is_required_first(self):
        for value in (
            None,
            object(),
            {},
            EntrySubclass(make_membership()),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^entry must be "
                    "ExplicitPortfolioWatchlistEntry$",
                ):
                    validate_explicit_portfolio_watchlist_entry(
                        value
                    )

    def test_exact_membership_type_is_required(self):
        invalid = (
            None,
            object(),
            {},
            MembershipSubclass(
                "portfolio-001",
                "subject-001",
            ),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^membership must be "
                    "ExplicitPortfolioMembership$",
                ):
                    validate_explicit_portfolio_watchlist_entry(
                        make_entry(membership=value)
                    )

    def test_upstream_validator_called_exactly_once(self):
        entry = make_entry()
        with patch(
            "PortfolioWatchlistEntry.validation"
            ".validate_explicit_portfolio_membership"
        ) as membership_validator:
            self.assertIsNone(
                validate_explicit_portfolio_watchlist_entry(
                    entry
                )
            )
        membership_validator.assert_called_once_with(
            entry.membership
        )

    def test_upstream_exception_propagates_unchanged(self):
        entry = make_entry()
        upstream_error = ValueError("membership failure")
        with patch(
            "PortfolioWatchlistEntry.validation"
            ".validate_explicit_portfolio_membership",
            side_effect=upstream_error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_portfolio_watchlist_entry(
                    entry
                )
        self.assertIs(caught.exception, upstream_error)

    def test_caller_membership_object_is_preserved(self):
        portfolio_id = " portfolio-é "
        subject_id = " subject-é "
        membership = ExplicitPortfolioMembership(
            portfolio_id,
            subject_id,
        )
        entry = ExplicitPortfolioWatchlistEntry(membership)

        self.assertIsNone(
            validate_explicit_portfolio_watchlist_entry(
                entry
            )
        )
        self.assertIs(entry.membership, membership)
        self.assertIs(
            entry.membership.portfolio_id,
            portfolio_id,
        )
        self.assertIs(
            entry.membership.portfolio_subject_id,
            subject_id,
        )

    def test_duplicates_are_not_detected(self):
        membership = make_membership()
        first = ExplicitPortfolioWatchlistEntry(membership)
        duplicate = ExplicitPortfolioWatchlistEntry(membership)

        self.assertIsNone(
            validate_explicit_portfolio_watchlist_entry(first)
        )
        self.assertIsNone(
            validate_explicit_portfolio_watchlist_entry(
                duplicate
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
            {
                "dataclasses",
                "PortfolioMembership.models",
            },
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "PortfolioMembership.models",
                "PortfolioMembership.validation",
                "PortfolioWatchlistEntry.models",
            },
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolioWatchlistEntry"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_portfolio_"
                "watchlist_entry"
            ],
        )
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "watchlist_entry_id",
            "collection",
            "snapshot",
            "position",
            "holding",
            "quantity",
            "price",
            "priority",
            "ranking",
            "allocation",
            "recommendation",
            "runtime",
            "persistence",
            "registry",
            "automation",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
