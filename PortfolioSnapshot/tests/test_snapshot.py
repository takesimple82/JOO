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
from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioPosition.models import ExplicitPortfolioPosition
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioSnapshot.validation import (
    validate_explicit_portfolio_snapshot,
)
from PortfolioWatchlistEntry.models import (
    ExplicitPortfolioWatchlistEntry,
)


MISSING_OVERRIDE = object()


def make_context(
    *,
    observation_context_id="context-001",
    portfolio_id="portfolio-001",
):
    return ExplicitPortfolioObservationContext(
        observation_context_id,
        portfolio_id,
    )


def make_holding_snapshot(context):
    membership = ExplicitPortfolioMembership(
        context.portfolio_id,
        "subject-held",
    )
    position = ExplicitPortfolioPosition(
        "position-001",
        membership,
    )
    observation = ExplicitPortfolioHoldingObservation(
        position,
        context,
        Decimal("10.00"),
    )
    return ExplicitPortfolioHoldingSnapshot(
        context,
        (observation,),
    )


def make_watchlist_entry(
    *,
    portfolio_id="portfolio-001",
    portfolio_subject_id="subject-watchlisted",
):
    return ExplicitPortfolioWatchlistEntry(
        ExplicitPortfolioMembership(
            portfolio_id,
            portfolio_subject_id,
        )
    )


def make_snapshot(**overrides):
    context = overrides.pop(
        "observation_context",
        make_context(),
    )
    holding_snapshot = overrides.pop(
        "holding_snapshot",
        MISSING_OVERRIDE,
    )
    if (
        holding_snapshot is MISSING_OVERRIDE
        and context is not None
    ):
        holding_snapshot = make_holding_snapshot(context)
    values = {
        "portfolio_snapshot_id": "snapshot-001",
        "observation_context": context,
        "holding_snapshot": holding_snapshot,
        "watchlist_entries": (
            make_watchlist_entry(
                portfolio_id=context.portfolio_id
            ),
        ) if context is not None else (),
    }
    values.update(overrides)
    return ExplicitPortfolioSnapshot(**values)


class StringSubclass(str):
    pass


class SnapshotSubclass(ExplicitPortfolioSnapshot):
    pass


class ContextSubclass(ExplicitPortfolioObservationContext):
    pass


class HoldingSnapshotSubclass(ExplicitPortfolioHoldingSnapshot):
    pass


class TupleSubclass(tuple):
    pass


class WatchlistEntrySubclass(ExplicitPortfolioWatchlistEntry):
    pass


class PortfolioSnapshotTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(ExplicitPortfolioSnapshot)
        self.assertEqual(
            [field.name for field in model_fields],
            [
                "portfolio_snapshot_id",
                "observation_context",
                "holding_snapshot",
                "watchlist_entries",
            ],
        )
        self.assertEqual(
            get_type_hints(ExplicitPortfolioSnapshot),
            {
                "portfolio_snapshot_id": str,
                "observation_context": (
                    ExplicitPortfolioObservationContext
                ),
                "holding_snapshot": (
                    ExplicitPortfolioHoldingSnapshot
                ),
                "watchlist_entries": tuple[
                    ExplicitPortfolioWatchlistEntry,
                    ...,
                ],
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitPortfolioSnapshot.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioSnapshot.__dict__,
        )

    def test_frozen_hashable_and_structural(self):
        first = make_snapshot()
        same = make_snapshot()
        different = make_snapshot(
            portfolio_snapshot_id="snapshot-002"
        )
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.portfolio_snapshot_id = "replacement"

    def test_exact_snapshot_type_first(self):
        valid = make_snapshot()
        for value in (
            None,
            object(),
            {},
            SnapshotSubclass(
                valid.portfolio_snapshot_id,
                valid.observation_context,
                valid.holding_snapshot,
                valid.watchlist_entries,
            ),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^snapshot must be "
                    "ExplicitPortfolioSnapshot$",
                ):
                    validate_explicit_portfolio_snapshot(value)

    def test_snapshot_id_requires_exact_nonblank_string(self):
        for value in (
            None,
            1,
            b"snapshot-001",
            StringSubclass("snapshot-001"),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^portfolio_snapshot_id must be str$",
                ):
                    validate_explicit_portfolio_snapshot(
                        make_snapshot(
                            portfolio_snapshot_id=value
                        )
                    )
        for value in ("", " ", "\t\n"):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^portfolio_snapshot_id must not be blank$",
                ):
                    validate_explicit_portfolio_snapshot(
                        make_snapshot(
                            portfolio_snapshot_id=value
                        )
                    )

    def test_exact_upstream_and_tuple_types(self):
        valid = make_snapshot()
        cases = (
            (
                make_snapshot(
                    observation_context=None,
                    holding_snapshot=valid.holding_snapshot,
                ),
                "observation_context must be "
                "ExplicitPortfolioObservationContext",
            ),
            (
                make_snapshot(
                    observation_context=ContextSubclass(
                        "context-001",
                        "portfolio-001",
                    )
                ),
                "observation_context must be "
                "ExplicitPortfolioObservationContext",
            ),
            (
                make_snapshot(holding_snapshot=None),
                "holding_snapshot must be "
                "ExplicitPortfolioHoldingSnapshot",
            ),
            (
                make_snapshot(
                    holding_snapshot=HoldingSnapshotSubclass(
                        valid.observation_context,
                        (),
                    )
                ),
                "holding_snapshot must be "
                "ExplicitPortfolioHoldingSnapshot",
            ),
            (
                make_snapshot(watchlist_entries=[]),
                "watchlist_entries must be tuple",
            ),
            (
                make_snapshot(
                    watchlist_entries=TupleSubclass()
                ),
                "watchlist_entries must be tuple",
            ),
        )
        for snapshot, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    TypeError,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_snapshot(snapshot)

    def test_empty_collections_and_partial_state_are_valid(self):
        context = make_context()
        holding_snapshot = ExplicitPortfolioHoldingSnapshot(
            context,
            (),
        )
        watchlist_entries = ()
        snapshot = ExplicitPortfolioSnapshot(
            " snapshot-é ",
            context,
            holding_snapshot,
            watchlist_entries,
        )

        self.assertIsNone(
            validate_explicit_portfolio_snapshot(snapshot)
        )
        self.assertIs(
            snapshot.watchlist_entries,
            watchlist_entries,
        )

    def test_watchlist_elements_require_exact_type(self):
        valid = make_watchlist_entry()
        invalid = (
            None,
            object(),
            WatchlistEntrySubclass(valid.membership),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^watchlist_entries must contain only "
                    "ExplicitPortfolioWatchlistEntry$",
                ):
                    validate_explicit_portfolio_snapshot(
                        make_snapshot(
                            watchlist_entries=(value,)
                        )
                    )

    def test_upstream_validators_once_in_declared_order(self):
        snapshot = make_snapshot(
            watchlist_entries=(
                make_watchlist_entry(
                    portfolio_subject_id="subject-002"
                ),
                make_watchlist_entry(
                    portfolio_subject_id="subject-001"
                ),
            )
        )
        calls = []
        with patch(
            "PortfolioSnapshot.validation"
            ".validate_explicit_portfolio_observation_context",
            side_effect=lambda value: calls.append(
                ("context", value)
            ),
        ) as context_validator, patch(
            "PortfolioSnapshot.validation"
            ".validate_explicit_portfolio_holding_snapshot",
            side_effect=lambda value: calls.append(
                ("holding", value)
            ),
        ) as holding_validator, patch(
            "PortfolioSnapshot.validation"
            ".validate_explicit_portfolio_watchlist_entry",
            side_effect=lambda value: calls.append(
                ("watchlist", value)
            ),
        ) as watchlist_validator:
            self.assertIsNone(
                validate_explicit_portfolio_snapshot(snapshot)
            )
        context_validator.assert_called_once_with(
            snapshot.observation_context
        )
        holding_validator.assert_called_once_with(
            snapshot.holding_snapshot
        )
        self.assertEqual(watchlist_validator.call_count, 2)
        self.assertEqual(
            calls,
            [
                ("context", snapshot.observation_context),
                ("holding", snapshot.holding_snapshot),
                ("watchlist", snapshot.watchlist_entries[0]),
                ("watchlist", snapshot.watchlist_entries[1]),
            ],
        )

    def test_upstream_exceptions_propagate_unchanged(self):
        snapshot = make_snapshot()
        context_error = ValueError("context failure")
        with patch(
            "PortfolioSnapshot.validation"
            ".validate_explicit_portfolio_observation_context",
            side_effect=context_error,
        ), patch(
            "PortfolioSnapshot.validation"
            ".validate_explicit_portfolio_holding_snapshot",
        ) as holding_validator:
            with self.assertRaises(ValueError) as caught:
                validate_explicit_portfolio_snapshot(snapshot)
        self.assertIs(caught.exception, context_error)
        holding_validator.assert_not_called()

        holding_error = ValueError("holding failure")
        with patch(
            "PortfolioSnapshot.validation"
            ".validate_explicit_portfolio_holding_snapshot",
            side_effect=holding_error,
        ), patch(
            "PortfolioSnapshot.validation"
            ".validate_explicit_portfolio_watchlist_entry",
        ) as watchlist_validator:
            with self.assertRaises(ValueError) as caught:
                validate_explicit_portfolio_snapshot(snapshot)
        self.assertIs(caught.exception, holding_error)
        watchlist_validator.assert_not_called()

        watchlist_error = ValueError("watchlist failure")
        with patch(
            "PortfolioSnapshot.validation"
            ".validate_explicit_portfolio_watchlist_entry",
            side_effect=watchlist_error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_portfolio_snapshot(snapshot)
        self.assertIs(caught.exception, watchlist_error)

    def test_holding_context_alignment_uses_exact_values(self):
        root = make_context()
        equal_context = make_context()
        snapshot = ExplicitPortfolioSnapshot(
            "snapshot-001",
            root,
            make_holding_snapshot(equal_context),
            (),
        )
        self.assertIsNot(root, equal_context)
        self.assertIsNone(
            validate_explicit_portfolio_snapshot(snapshot)
        )

        mismatched_context_id = make_context(
            observation_context_id="context-002"
        )
        with self.assertRaisesRegex(
            ValueError,
            "^holding_snapshot observation_context_id "
            "must match observation_context "
            "observation_context_id$",
        ):
            validate_explicit_portfolio_snapshot(
                ExplicitPortfolioSnapshot(
                    "snapshot-001",
                    root,
                    make_holding_snapshot(
                        mismatched_context_id
                    ),
                    (),
                )
            )

        mismatched_portfolio = make_context(
            portfolio_id="portfolio-002"
        )
        with self.assertRaisesRegex(
            ValueError,
            "^holding_snapshot portfolio_id must match "
            "observation_context portfolio_id$",
        ):
            validate_explicit_portfolio_snapshot(
                ExplicitPortfolioSnapshot(
                    "snapshot-001",
                    root,
                    make_holding_snapshot(
                        mismatched_portfolio
                    ),
                    (),
                )
            )

    def test_watchlist_portfolio_alignment_is_exact(self):
        with self.assertRaisesRegex(
            ValueError,
            "^watchlist entry portfolio_id must match "
            "observation_context portfolio_id$",
        ):
            validate_explicit_portfolio_snapshot(
                make_snapshot(
                    watchlist_entries=(
                        make_watchlist_entry(
                            portfolio_id="portfolio-002"
                        ),
                    )
                )
            )

    def test_duplicate_watchlist_memberships_are_rejected(self):
        first = make_watchlist_entry()
        duplicate = make_watchlist_entry()
        self.assertIsNot(first, duplicate)
        with self.assertRaisesRegex(
            ValueError,
            "^watchlist_entries must not contain "
            "duplicate memberships$",
        ):
            validate_explicit_portfolio_snapshot(
                make_snapshot(
                    watchlist_entries=(first, duplicate)
                )
            )

    def test_order_objects_and_values_are_preserved(self):
        snapshot_id = " snapshot-é "
        context = make_context(
            observation_context_id=" context-é "
        )
        holding_snapshot = make_holding_snapshot(context)
        second = make_watchlist_entry(
            portfolio_subject_id="subject-002"
        )
        first = make_watchlist_entry(
            portfolio_subject_id="subject-001"
        )
        entries = (second, first)
        snapshot = ExplicitPortfolioSnapshot(
            snapshot_id,
            context,
            holding_snapshot,
            entries,
        )

        self.assertIsNone(
            validate_explicit_portfolio_snapshot(snapshot)
        )
        self.assertIs(
            snapshot.portfolio_snapshot_id,
            snapshot_id,
        )
        self.assertIs(snapshot.observation_context, context)
        self.assertIs(
            snapshot.holding_snapshot,
            holding_snapshot,
        )
        self.assertIs(snapshot.watchlist_entries, entries)
        self.assertIs(snapshot.watchlist_entries[0], second)
        self.assertIs(snapshot.watchlist_entries[1], first)

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
                "PortfolioHoldingSnapshot.models",
                "PortfolioObservationContext.models",
                "PortfolioWatchlistEntry.models",
            },
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "PortfolioHoldingSnapshot.models",
                "PortfolioHoldingSnapshot.validation",
                "PortfolioObservationContext.models",
                "PortfolioObservationContext.validation",
                "PortfolioSnapshot.models",
                "PortfolioWatchlistEntry.models",
                "PortfolioWatchlistEntry.validation",
            },
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolioSnapshot"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["validate_explicit_portfolio_snapshot"],
        )
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "cash",
            "price",
            "cost_basis",
            "currency",
            "valuation",
            "profit",
            "loss",
            "capital_bucket",
            "risk_budget",
            "target_weight",
            "recommendation",
            "allocation",
            "constraint",
            "runtime",
            "persistence",
            "registry",
            "automation",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
