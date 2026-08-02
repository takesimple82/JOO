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
from PortfolioHoldingSnapshot.models import (
    ExplicitPortfolioHoldingSnapshot,
)
from PortfolioHoldingSnapshot.validation import (
    validate_explicit_portfolio_holding_snapshot,
)
from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioPosition.models import ExplicitPortfolioPosition


def make_context(
    *,
    observation_context_id="context-001",
    portfolio_id="portfolio-001",
):
    return ExplicitPortfolioObservationContext(
        observation_context_id,
        portfolio_id,
    )


def make_observation(
    context,
    *,
    position_id="position-001",
    portfolio_subject_id="subject-001",
    quantity=Decimal("10.00"),
):
    position = ExplicitPortfolioPosition(
        position_id,
        ExplicitPortfolioMembership(
            context.portfolio_id,
            portfolio_subject_id,
        ),
    )
    return ExplicitPortfolioHoldingObservation(
        position,
        context,
        quantity,
    )


def make_snapshot(**overrides):
    context = overrides.pop(
        "observation_context",
        make_context(),
    )
    observations = overrides.pop(
        "holding_observations",
        None,
    )
    if observations is None and context is not None:
        observations = (make_observation(context),)
    values = {
        "observation_context": context,
        "holding_observations": observations,
    }
    values.update(overrides)
    return ExplicitPortfolioHoldingSnapshot(**values)


class SnapshotSubclass(ExplicitPortfolioHoldingSnapshot):
    pass


class TupleSubclass(tuple):
    pass


class ObservationSubclass(ExplicitPortfolioHoldingObservation):
    pass


class PortfolioHoldingSnapshotTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(
            ExplicitPortfolioHoldingSnapshot
        )
        self.assertEqual(
            [field.name for field in model_fields],
            ["observation_context", "holding_observations"],
        )
        self.assertEqual(
            get_type_hints(ExplicitPortfolioHoldingSnapshot),
            {
                "observation_context": (
                    ExplicitPortfolioObservationContext
                ),
                "holding_observations": tuple[
                    ExplicitPortfolioHoldingObservation,
                    ...,
                ],
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitPortfolioHoldingSnapshot.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioHoldingSnapshot.__dict__,
        )

    def test_frozen_hashable_and_structural(self):
        first = make_snapshot()
        same = make_snapshot()
        different = make_snapshot(
            holding_observations=(),
        )
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.holding_observations = ()

    def test_exact_snapshot_type_first(self):
        context = make_context()
        for value in (
            None,
            object(),
            {},
            SnapshotSubclass(context, ()),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^snapshot must be "
                    "ExplicitPortfolioHoldingSnapshot$",
                ):
                    validate_explicit_portfolio_holding_snapshot(
                        value
                    )

    def test_exact_context_and_tuple_types(self):
        cases = (
            (
                make_snapshot(
                    observation_context=None,
                    holding_observations=(),
                ),
                "observation_context must be "
                "ExplicitPortfolioObservationContext",
            ),
            (
                make_snapshot(holding_observations=[]),
                "holding_observations must be tuple",
            ),
            (
                make_snapshot(
                    holding_observations=TupleSubclass()
                ),
                "holding_observations must be tuple",
            ),
        )
        for snapshot, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    TypeError,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_holding_snapshot(
                        snapshot
                    )

    def test_empty_tuple_is_valid(self):
        observations = ()
        snapshot = make_snapshot(
            holding_observations=observations
        )
        self.assertIsNone(
            validate_explicit_portfolio_holding_snapshot(
                snapshot
            )
        )
        self.assertIs(snapshot.holding_observations, observations)

    def test_elements_require_exact_observation_type(self):
        context = make_context()
        valid = make_observation(context)
        invalid_values = (
            None,
            object(),
            ObservationSubclass(
                valid.position,
                context,
                valid.quantity,
            ),
        )
        for value in invalid_values:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^holding_observations must contain only "
                    "ExplicitPortfolioHoldingObservation$",
                ):
                    validate_explicit_portfolio_holding_snapshot(
                        ExplicitPortfolioHoldingSnapshot(
                            context,
                            (value,),
                        )
                    )

    def test_caller_order_and_object_identity_are_preserved(self):
        context = make_context()
        first = make_observation(
            context,
            position_id="position-002",
            quantity=Decimal("2.00"),
        )
        second = make_observation(
            context,
            position_id="position-001",
            quantity=Decimal("1.000"),
        )
        observations = (first, second)
        snapshot = ExplicitPortfolioHoldingSnapshot(
            context,
            observations,
        )

        self.assertIsNone(
            validate_explicit_portfolio_holding_snapshot(
                snapshot
            )
        )
        self.assertIs(snapshot.observation_context, context)
        self.assertIs(
            snapshot.holding_observations,
            observations,
        )
        self.assertIs(snapshot.holding_observations[0], first)
        self.assertIs(snapshot.holding_observations[1], second)
        self.assertEqual(
            [
                observation.position.position_id
                for observation in snapshot.holding_observations
            ],
            ["position-002", "position-001"],
        )
        self.assertIs(first.quantity, observations[0].quantity)
        self.assertEqual(
            second.quantity.as_tuple(),
            Decimal("1.000").as_tuple(),
        )

    def test_upstream_validators_once_in_caller_order(self):
        context = make_context()
        first = make_observation(
            context,
            position_id="position-002",
        )
        second = make_observation(
            context,
            position_id="position-001",
        )
        snapshot = ExplicitPortfolioHoldingSnapshot(
            context,
            (first, second),
        )
        calls = []
        with patch(
            "PortfolioHoldingSnapshot.validation"
            ".validate_explicit_portfolio_observation_context",
            side_effect=lambda value: calls.append(
                ("context", value)
            ),
        ) as context_validator, patch(
            "PortfolioHoldingSnapshot.validation"
            ".validate_explicit_portfolio_holding_observation",
            side_effect=lambda value: calls.append(
                ("observation", value)
            ),
        ) as observation_validator:
            self.assertIsNone(
                validate_explicit_portfolio_holding_snapshot(
                    snapshot
                )
            )
        context_validator.assert_called_once_with(context)
        self.assertEqual(
            observation_validator.call_count,
            2,
        )
        self.assertEqual(
            calls,
            [
                ("context", context),
                ("observation", first),
                ("observation", second),
            ],
        )

    def test_upstream_exceptions_propagate_unchanged(self):
        snapshot = make_snapshot()
        context_error = ValueError("context failure")
        with patch(
            "PortfolioHoldingSnapshot.validation"
            ".validate_explicit_portfolio_observation_context",
            side_effect=context_error,
        ), patch(
            "PortfolioHoldingSnapshot.validation"
            ".validate_explicit_portfolio_holding_observation",
        ) as observation_validator:
            with self.assertRaises(ValueError) as caught:
                validate_explicit_portfolio_holding_snapshot(
                    snapshot
                )
        self.assertIs(caught.exception, context_error)
        observation_validator.assert_not_called()

        observation_error = ValueError("observation failure")
        with patch(
            "PortfolioHoldingSnapshot.validation"
            ".validate_explicit_portfolio_holding_observation",
            side_effect=observation_error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_portfolio_holding_snapshot(
                    snapshot
                )
        self.assertIs(caught.exception, observation_error)

    def test_same_context_object_succeeds(self):
        context = make_context()
        observation = make_observation(context)
        snapshot = ExplicitPortfolioHoldingSnapshot(
            context,
            (observation,),
        )

        self.assertIsNone(
            validate_explicit_portfolio_holding_snapshot(
                snapshot
            )
        )
        self.assertIs(snapshot.observation_context, context)
        self.assertIs(
            observation.observation_context,
            context,
        )

    def test_distinct_equal_context_object_succeeds_unchanged(self):
        root = make_context()
        element_context = make_context()
        observation = make_observation(element_context)
        snapshot = ExplicitPortfolioHoldingSnapshot(
            root,
            (observation,),
        )

        self.assertEqual(root, element_context)
        self.assertIsNot(root, element_context)
        self.assertIsNone(
            validate_explicit_portfolio_holding_snapshot(
                snapshot
            )
        )
        self.assertIs(snapshot.observation_context, root)
        self.assertIs(
            observation.observation_context,
            element_context,
        )
        self.assertIsNot(
            observation.observation_context,
            snapshot.observation_context,
        )

    def test_mismatched_observation_context_id_fails(self):
        root = make_context(
            observation_context_id="context-root"
        )
        element_context = make_context(
            observation_context_id="context-element"
        )
        observation = make_observation(element_context)
        with self.assertRaisesRegex(
            ValueError,
            "^observation_context_id must match the snapshot "
            "observation_context_id$",
        ):
            validate_explicit_portfolio_holding_snapshot(
                ExplicitPortfolioHoldingSnapshot(
                    root,
                    (observation,),
                )
            )

    def test_mismatched_portfolio_id_fails(self):
        root = make_context(portfolio_id="portfolio-root")
        element_context = make_context(
            portfolio_id="portfolio-element"
        )
        observation = make_observation(element_context)
        with self.assertRaisesRegex(
            ValueError,
            "^portfolio_id must match the snapshot "
            "portfolio_id$",
        ):
            validate_explicit_portfolio_holding_snapshot(
                ExplicitPortfolioHoldingSnapshot(
                    root,
                    (observation,),
                )
            )

    def test_duplicate_position_id_is_rejected(self):
        context = make_context()
        first = make_observation(
            context,
            position_id="position-001",
            portfolio_subject_id="subject-001",
        )
        duplicate = make_observation(
            context,
            position_id="position-001",
            portfolio_subject_id="subject-002",
        )
        with self.assertRaisesRegex(
            ValueError,
            "^holding_observations must not contain "
            "duplicate position_id$",
        ):
            validate_explicit_portfolio_holding_snapshot(
                ExplicitPortfolioHoldingSnapshot(
                    context,
                    (first, duplicate),
                )
            )

    def test_partial_snapshot_is_valid(self):
        context = make_context()
        single = make_observation(
            context,
            position_id="position-009",
        )
        self.assertIsNone(
            validate_explicit_portfolio_holding_snapshot(
                ExplicitPortfolioHoldingSnapshot(
                    context,
                    (single,),
                )
            )
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
                "PortfolioHoldingObservation.models",
                "PortfolioObservationContext.models",
            },
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "PortfolioHoldingObservation.models",
                "PortfolioHoldingObservation.validation",
                "PortfolioHoldingSnapshot.models",
                "PortfolioObservationContext.models",
                "PortfolioObservationContext.validation",
            },
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolioHoldingSnapshot"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["validate_explicit_portfolio_holding_snapshot"],
        )
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "snapshot_id",
            "price",
            "cost_basis",
            "currency",
            "valuation",
            "profit",
            "loss",
            "watchlist",
            "PortfolioSnapshot",
            "allocation",
            "runtime",
            "persistence",
            "registry",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
