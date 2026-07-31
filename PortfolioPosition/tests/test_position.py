import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)
from PortfolioPosition.models import (
    ExplicitPortfolioPosition,
)
from PortfolioPosition.validation import (
    validate_explicit_portfolio_position,
)


def make_membership():
    return ExplicitPortfolioMembership(
        "portfolio-001",
        "subject-001",
    )


def make_position(**overrides):
    values = {
        "position_id": "position-001",
        "membership": make_membership(),
    }
    values.update(overrides)
    return ExplicitPortfolioPosition(**values)


class StringSubclass(str):
    pass


class MembershipSubclass(ExplicitPortfolioMembership):
    pass


class PositionSubclass(ExplicitPortfolioPosition):
    pass


class ExplicitPortfolioPositionTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(ExplicitPortfolioPosition)
        self.assertEqual(
            [field.name for field in model_fields],
            ["position_id", "membership"],
        )
        self.assertEqual(
            get_type_hints(ExplicitPortfolioPosition),
            {
                "position_id": str,
                "membership": ExplicitPortfolioMembership,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioPosition.__dict__,
        )

    def test_frozen_hashable_structural_equality(self):
        membership = make_membership()
        first = ExplicitPortfolioPosition(
            "position-001",
            membership,
        )
        same = ExplicitPortfolioPosition(
            "position-001",
            membership,
        )
        different = ExplicitPortfolioPosition(
            "position-002",
            membership,
        )
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.position_id = "replacement"

    def test_exact_position_type(self):
        for value in (
            None,
            object(),
            {},
            PositionSubclass(
                "position-001",
                make_membership(),
            ),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^position must be "
                    "ExplicitPortfolioPosition$",
                ):
                    validate_explicit_portfolio_position(
                        value
                    )

    def test_position_id_contract(self):
        for value in (
            None,
            1,
            b"position",
            StringSubclass("position"),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^position_id must be str$",
                ):
                    validate_explicit_portfolio_position(
                        make_position(position_id=value)
                    )
        for value in ("", " ", "\t\n"):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^position_id must not be blank$",
                ):
                    validate_explicit_portfolio_position(
                        make_position(position_id=value)
                    )

    def test_exact_membership_type(self):
        membership = make_membership()
        subclass = MembershipSubclass(
            membership.portfolio_id,
            membership.portfolio_subject_id,
        )
        for value in (None, object(), subclass):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^membership must be "
                    "ExplicitPortfolioMembership$",
                ):
                    validate_explicit_portfolio_position(
                        make_position(membership=value)
                    )

    def test_validation_order(self):
        cases = (
            (
                make_position(
                    position_id=None,
                    membership=None,
                ),
                TypeError,
                "position_id must be str",
            ),
            (
                make_position(
                    position_id=" ",
                    membership=None,
                ),
                ValueError,
                "position_id must not be blank",
            ),
            (
                make_position(membership=None),
                TypeError,
                "membership must be "
                "ExplicitPortfolioMembership",
            ),
        )
        for position, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_position(
                        position
                    )

    def test_upstream_validator_once_and_exception_identity(self):
        membership = make_membership()
        position = ExplicitPortfolioPosition(
            "position-001",
            membership,
        )
        with patch(
            "PortfolioPosition.validation"
            ".validate_explicit_portfolio_membership",
        ) as validator:
            self.assertIsNone(
                validate_explicit_portfolio_position(
                    position
                )
            )
        validator.assert_called_once_with(membership)
        self.assertIs(
            validator.call_args.args[0],
            membership,
        )

        error = ValueError("membership failure")
        with patch(
            "PortfolioPosition.validation"
            ".validate_explicit_portfolio_membership",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                validate_explicit_portfolio_position(
                    position
                )
        self.assertIs(context.exception, error)

    def test_objects_and_whitespace_are_preserved(self):
        position_id = " position-\u00e9 "
        membership = make_membership()
        position = ExplicitPortfolioPosition(
            position_id,
            membership,
        )
        self.assertIsNone(
            validate_explicit_portfolio_position(position)
        )
        self.assertIs(position.position_id, position_id)
        self.assertIs(position.membership, membership)

    def test_multiple_positions_may_share_membership(self):
        membership = make_membership()
        first = ExplicitPortfolioPosition(
            "position-001",
            membership,
        )
        second = ExplicitPortfolioPosition(
            "position-002",
            membership,
        )
        self.assertIsNone(
            validate_explicit_portfolio_position(first)
        )
        self.assertIsNone(
            validate_explicit_portfolio_position(second)
        )
        self.assertNotEqual(first, second)

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
            {
                "dataclasses",
                "PortfolioMembership.models",
            },
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolioPosition"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["validate_explicit_portfolio_position"],
        )
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "quantity",
            "shares",
            "price",
            "cost_basis",
            "currency",
            "valuation",
            "snapshot",
            "target_weight",
            "allocation",
            "recommendation",
            "execution",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
