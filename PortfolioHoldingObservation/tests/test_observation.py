import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from decimal import Decimal
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from PortfolioHoldingObservation.models import (
    ExplicitPortfolioHoldingObservation,
)
from PortfolioHoldingObservation.validation import (
    validate_explicit_portfolio_holding_observation,
)
from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioPosition.models import ExplicitPortfolioPosition


def make_position(
    *,
    position_id="position-001",
    portfolio_id="portfolio-001",
    portfolio_subject_id="subject-001",
):
    return ExplicitPortfolioPosition(
        position_id,
        ExplicitPortfolioMembership(
            portfolio_id,
            portfolio_subject_id,
        ),
    )


def make_context(
    *,
    observation_context_id="context-001",
    portfolio_id="portfolio-001",
):
    return ExplicitPortfolioObservationContext(
        observation_context_id,
        portfolio_id,
    )


def make_observation(**overrides):
    values = {
        "position": make_position(),
        "observation_context": make_context(),
        "quantity": Decimal("10.00"),
    }
    values.update(overrides)
    return ExplicitPortfolioHoldingObservation(**values)


class DecimalSubclass(Decimal):
    pass


class ObservationSubclass(ExplicitPortfolioHoldingObservation):
    pass


class PortfolioHoldingObservationTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(
            ExplicitPortfolioHoldingObservation
        )
        self.assertEqual(
            [field.name for field in model_fields],
            [
                "position",
                "observation_context",
                "quantity",
            ],
        )
        self.assertEqual(
            get_type_hints(
                ExplicitPortfolioHoldingObservation
            ),
            {
                "position": ExplicitPortfolioPosition,
                "observation_context": (
                    ExplicitPortfolioObservationContext
                ),
                "quantity": Decimal,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioHoldingObservation.__dict__,
        )

    def test_frozen_hashable_and_structural(self):
        first = make_observation()
        same = make_observation()
        different = make_observation(
            quantity=Decimal("11")
        )
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.quantity = Decimal("12")

    def test_exact_observation_type_first(self):
        for value in (
            None,
            object(),
            {},
            ObservationSubclass(
                make_position(),
                make_context(),
                Decimal("1"),
            ),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^observation must be "
                    "ExplicitPortfolioHoldingObservation$",
                ):
                    validate_explicit_portfolio_holding_observation(
                        value
                    )

    def test_exact_position_and_context_types(self):
        cases = (
            (
                make_observation(position=None),
                "position must be ExplicitPortfolioPosition",
            ),
            (
                make_observation(
                    observation_context=None
                ),
                "observation_context must be "
                "ExplicitPortfolioObservationContext",
            ),
        )
        for observation, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    TypeError,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_holding_observation(
                        observation
                    )

    def test_quantity_requires_exact_finite_decimal(self):
        for value in (
            None,
            1,
            1.0,
            "1",
            DecimalSubclass("1"),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^quantity must be Decimal$",
                ):
                    validate_explicit_portfolio_holding_observation(
                        make_observation(quantity=value)
                    )
        for value in (
            Decimal("NaN"),
            Decimal("sNaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        ):
            with self.subTest(value=str(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^quantity must be finite$",
                ):
                    validate_explicit_portfolio_holding_observation(
                        make_observation(quantity=value)
                    )

    def test_validation_order(self):
        cases = (
            (
                make_observation(
                    position=None,
                    observation_context=None,
                    quantity=None,
                ),
                "position must be ExplicitPortfolioPosition",
            ),
            (
                make_observation(
                    observation_context=None,
                    quantity=None,
                ),
                "observation_context must be "
                "ExplicitPortfolioObservationContext",
            ),
            (
                make_observation(quantity=None),
                "quantity must be Decimal",
            ),
        )
        for observation, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    TypeError,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_holding_observation(
                        observation
                    )

    def test_upstream_validators_once_in_order(self):
        observation = make_observation()
        calls = []
        with patch(
            "PortfolioHoldingObservation.validation"
            ".validate_explicit_portfolio_position",
            side_effect=lambda value: calls.append(
                ("position", value)
            ),
        ) as position_validator, patch(
            "PortfolioHoldingObservation.validation"
            ".validate_explicit_portfolio_observation_context",
            side_effect=lambda value: calls.append(
                ("context", value)
            ),
        ) as context_validator:
            self.assertIsNone(
                validate_explicit_portfolio_holding_observation(
                    observation
                )
            )
        position_validator.assert_called_once_with(
            observation.position
        )
        context_validator.assert_called_once_with(
            observation.observation_context
        )
        self.assertEqual(
            calls,
            [
                ("position", observation.position),
                (
                    "context",
                    observation.observation_context,
                ),
            ],
        )

    def test_upstream_exceptions_propagate_unchanged(self):
        observation = make_observation()
        position_error = ValueError("position failure")
        with patch(
            "PortfolioHoldingObservation.validation"
            ".validate_explicit_portfolio_position",
            side_effect=position_error,
        ), patch(
            "PortfolioHoldingObservation.validation"
            ".validate_explicit_portfolio_observation_context",
        ) as context_validator:
            with self.assertRaises(ValueError) as context:
                validate_explicit_portfolio_holding_observation(
                    observation
                )
        self.assertIs(context.exception, position_error)
        context_validator.assert_not_called()

        context_error = ValueError("context failure")
        with patch(
            "PortfolioHoldingObservation.validation"
            ".validate_explicit_portfolio_observation_context",
            side_effect=context_error,
        ):
            with self.assertRaises(ValueError) as context:
                validate_explicit_portfolio_holding_observation(
                    observation
                )
        self.assertIs(context.exception, context_error)

    def test_objects_and_decimal_representation_are_preserved(self):
        position = make_position(
            position_id=" position-\u00e9 "
        )
        observation_context = make_context(
            observation_context_id=" context-e\u0301 "
        )
        quantity = Decimal("-0.00")
        observation = ExplicitPortfolioHoldingObservation(
            position,
            observation_context,
            quantity,
        )
        self.assertIsNone(
            validate_explicit_portfolio_holding_observation(
                observation
            )
        )
        self.assertIs(observation.position, position)
        self.assertIs(
            observation.observation_context,
            observation_context,
        )
        self.assertIs(observation.quantity, quantity)
        self.assertEqual(
            observation.quantity.as_tuple(),
            Decimal("-0.00").as_tuple(),
        )

    def test_quantity_sign_is_not_interpreted(self):
        for value in (
            Decimal("-10"),
            Decimal("-0"),
            Decimal("0"),
            Decimal("10"),
        ):
            with self.subTest(value=str(value)):
                self.assertIsNone(
                    validate_explicit_portfolio_holding_observation(
                        make_observation(quantity=value)
                    )
                )

    def test_matching_portfolio_ids_succeed(self):
        observation = make_observation(
            position=make_position(
                portfolio_id="portfolio-shared"
            ),
            observation_context=make_context(
                portfolio_id="portfolio-shared"
            ),
        )
        self.assertIsNone(
            validate_explicit_portfolio_holding_observation(
                observation
            )
        )

    def test_mismatched_portfolio_ids_fail(self):
        observation = make_observation(
            position=make_position(
                portfolio_id="portfolio-left"
            ),
            observation_context=make_context(
                portfolio_id="portfolio-right"
            ),
        )
        with self.assertRaisesRegex(
            ValueError,
            "^position portfolio_id must match "
            "observation_context portfolio_id$",
        ):
            validate_explicit_portfolio_holding_observation(
                observation
            )

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
                "decimal",
                "PortfolioObservationContext.models",
                "PortfolioPosition.models",
            },
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolioHoldingObservation"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_portfolio_"
                "holding_observation"
            ],
        )
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "timestamp",
            "observed_on",
            "price",
            "cost_basis",
            "currency",
            "valuation",
            "profit",
            "loss",
            "snapshot",
            "watchlist",
            "allocation",
            "recommendation",
            "runtime",
            "persistence",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
