import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from decimal import Decimal
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from MarketFactProvenanceReference.models import (
    ExplicitMarketFactProvenanceReference,
)
from MarketInstrument.models import ExplicitMarketInstrument
from MarketInstrumentObservation.models import (
    ExplicitMarketInstrumentObservation,
)
from MarketSessionContext.models import (
    ExplicitMarketSessionContext,
)
from MarketSnapshot.models import ExplicitMarketSnapshot
from MarketSnapshot.validation import (
    validate_explicit_market_snapshot,
)


def make_context(
    *,
    session_context_id="session-context-001",
    market_id="market-001",
    venue_id="venue-001",
    session_profile_id="profile-001",
    timezone_id="timezone-001",
    calendar_id="calendar-001",
):
    return ExplicitMarketSessionContext(
        session_context_id,
        market_id,
        venue_id,
        session_profile_id,
        timezone_id,
        calendar_id,
    )


def make_provenance(
    *,
    fact_id="fact-001",
    source_identity="source-001",
    collected_at="collected-at-001",
):
    return ExplicitMarketFactProvenanceReference(
        fact_id,
        source_identity,
        collected_at,
    )


def make_observation(
    *,
    instrument_id="instrument-001",
    session_context=None,
    last_price=None,
    market_status="open",
    provenance=None,
):
    if session_context is None:
        session_context = make_context()
    if last_price is None:
        last_price = Decimal("10.00")
    if provenance is None:
        provenance = make_provenance(
            fact_id=f"fact-for-{instrument_id}"
        )
    return ExplicitMarketInstrumentObservation(
        ExplicitMarketInstrument(instrument_id),
        session_context,
        last_price,
        market_status,
        provenance,
    )


def make_snapshot(**overrides):
    context = overrides.pop(
        "session_context",
        make_context(),
    )
    observations = overrides.pop(
        "instrument_observations",
        None,
    )
    if observations is None and context is not None:
        observations = (
            make_observation(session_context=context),
        )
    values = {
        "market_snapshot_id": "snapshot-001",
        "session_context": context,
        "instrument_observations": observations,
    }
    values.update(overrides)
    return ExplicitMarketSnapshot(**values)


class StringSubclass(str):
    pass


class SnapshotSubclass(ExplicitMarketSnapshot):
    pass


class ContextSubclass(ExplicitMarketSessionContext):
    pass


class TupleSubclass(tuple):
    pass


class ObservationSubclass(
    ExplicitMarketInstrumentObservation
):
    pass


class MarketSnapshotTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(ExplicitMarketSnapshot)
        self.assertEqual(
            [field.name for field in model_fields],
            [
                "market_snapshot_id",
                "session_context",
                "instrument_observations",
            ],
        )
        self.assertEqual(
            get_type_hints(ExplicitMarketSnapshot),
            {
                "market_snapshot_id": str,
                "session_context": (
                    ExplicitMarketSessionContext
                ),
                "instrument_observations": tuple[
                    ExplicitMarketInstrumentObservation,
                    ...,
                ],
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitMarketSnapshot.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitMarketSnapshot.__dict__,
        )

    def test_frozen_hashable_and_structural(self):
        first = make_snapshot()
        same = make_snapshot()
        different = make_snapshot(
            market_snapshot_id="snapshot-002"
        )
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.market_snapshot_id = "replacement"

    def test_exact_snapshot_type_first(self):
        valid = make_snapshot()
        for value in (
            None,
            object(),
            {},
            SnapshotSubclass(
                valid.market_snapshot_id,
                valid.session_context,
                valid.instrument_observations,
            ),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^snapshot must be "
                    "ExplicitMarketSnapshot$",
                ):
                    validate_explicit_market_snapshot(value)

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
                    "^market_snapshot_id must be str$",
                ):
                    validate_explicit_market_snapshot(
                        make_snapshot(
                            market_snapshot_id=value
                        )
                    )
        for value in ("", " ", "\t\n"):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^market_snapshot_id must not be blank$",
                ):
                    validate_explicit_market_snapshot(
                        make_snapshot(
                            market_snapshot_id=value
                        )
                    )

    def test_exact_upstream_and_tuple_types(self):
        valid = make_snapshot()
        cases = (
            (
                make_snapshot(
                    session_context=None,
                    instrument_observations=(
                        valid.instrument_observations
                    ),
                ),
                "session_context must be "
                "ExplicitMarketSessionContext",
            ),
            (
                make_snapshot(
                    session_context=ContextSubclass(
                        "session-context-001",
                        "market-001",
                        "venue-001",
                        "profile-001",
                        "timezone-001",
                        "calendar-001",
                    ),
                    instrument_observations=(),
                ),
                "session_context must be "
                "ExplicitMarketSessionContext",
            ),
            (
                make_snapshot(
                    instrument_observations=[]
                ),
                "instrument_observations must be tuple",
            ),
            (
                make_snapshot(
                    instrument_observations=TupleSubclass()
                ),
                "instrument_observations must be tuple",
            ),
        )
        for snapshot, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    TypeError,
                    f"^{message}$",
                ):
                    validate_explicit_market_snapshot(snapshot)

    def test_empty_and_single_and_multiple_observations(self):
        context = make_context()
        empty = ExplicitMarketSnapshot(
            " snapshot-é ",
            context,
            (),
        )
        self.assertIsNone(
            validate_explicit_market_snapshot(empty)
        )
        self.assertIs(empty.instrument_observations, ())

        single = make_snapshot(
            session_context=context,
            instrument_observations=(
                make_observation(
                    instrument_id="instrument-001",
                    session_context=context,
                ),
            ),
        )
        self.assertIsNone(
            validate_explicit_market_snapshot(single)
        )

        multi = make_snapshot(
            session_context=context,
            instrument_observations=(
                make_observation(
                    instrument_id="instrument-001",
                    session_context=context,
                ),
                make_observation(
                    instrument_id="instrument-002",
                    session_context=context,
                ),
                make_observation(
                    instrument_id="instrument-003",
                    session_context=context,
                ),
            ),
        )
        self.assertIsNone(
            validate_explicit_market_snapshot(multi)
        )

    def test_observation_elements_require_exact_type(self):
        valid = make_observation()
        invalid = (
            None,
            object(),
            ObservationSubclass(
                valid.instrument,
                valid.session_context,
                valid.last_price,
                valid.market_status,
                valid.provenance,
            ),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^instrument_observations must contain "
                    "only ExplicitMarketInstrumentObservation$",
                ):
                    validate_explicit_market_snapshot(
                        make_snapshot(
                            instrument_observations=(value,)
                        )
                    )

    def test_upstream_validators_once_in_declared_order(self):
        context = make_context()
        first = make_observation(
            instrument_id="instrument-002",
            session_context=context,
        )
        second = make_observation(
            instrument_id="instrument-001",
            session_context=context,
        )
        snapshot = make_snapshot(
            session_context=context,
            instrument_observations=(first, second),
        )
        calls = []
        with patch(
            "MarketSnapshot.validation"
            ".validate_explicit_market_session_context",
            side_effect=lambda value: calls.append(
                ("context", value)
            ),
        ) as context_validator, patch(
            "MarketSnapshot.validation"
            ".validate_explicit_market_instrument_observation",
            side_effect=lambda value: calls.append(
                ("observation", value)
            ),
        ) as observation_validator:
            self.assertIsNone(
                validate_explicit_market_snapshot(snapshot)
            )
        context_validator.assert_called_once_with(
            snapshot.session_context
        )
        self.assertEqual(observation_validator.call_count, 2)
        self.assertEqual(
            calls,
            [
                ("context", snapshot.session_context),
                ("observation", first),
                ("observation", second),
            ],
        )

    def test_upstream_exceptions_propagate_unchanged(self):
        snapshot = make_snapshot()
        context_error = ValueError("context failure")
        with patch(
            "MarketSnapshot.validation"
            ".validate_explicit_market_session_context",
            side_effect=context_error,
        ), patch(
            "MarketSnapshot.validation"
            ".validate_explicit_market_instrument_observation",
        ) as observation_validator:
            with self.assertRaises(ValueError) as caught:
                validate_explicit_market_snapshot(snapshot)
        self.assertIs(caught.exception, context_error)
        observation_validator.assert_not_called()

        observation_error = ValueError("observation failure")
        with patch(
            "MarketSnapshot.validation"
            ".validate_explicit_market_instrument_observation",
            side_effect=observation_error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_market_snapshot(snapshot)
        self.assertIs(caught.exception, observation_error)

    def test_session_alignment_uses_exact_stored_field_values(self):
        root = make_context()
        equal_context = make_context()
        snapshot = ExplicitMarketSnapshot(
            "snapshot-001",
            root,
            (
                make_observation(
                    session_context=equal_context
                ),
            ),
        )
        self.assertIsNot(root, equal_context)
        self.assertIsNone(
            validate_explicit_market_snapshot(snapshot)
        )

        alignment_cases = (
            (
                make_context(
                    session_context_id="session-context-002"
                ),
                "session_context_id must match the snapshot "
                "session_context_id",
            ),
            (
                make_context(market_id="market-002"),
                "market_id must match the snapshot "
                "market_id",
            ),
            (
                make_context(venue_id="venue-002"),
                "venue_id must match the snapshot "
                "venue_id",
            ),
            (
                make_context(
                    session_profile_id="profile-002"
                ),
                "session_profile_id must match the snapshot "
                "session_profile_id",
            ),
            (
                make_context(timezone_id="timezone-002"),
                "timezone_id must match the snapshot "
                "timezone_id",
            ),
            (
                make_context(calendar_id="calendar-002"),
                "calendar_id must match the snapshot "
                "calendar_id",
            ),
        )
        for mismatched, message in alignment_cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    ValueError,
                    f"^{message}$",
                ):
                    validate_explicit_market_snapshot(
                        ExplicitMarketSnapshot(
                            "snapshot-001",
                            root,
                            (
                                make_observation(
                                    session_context=mismatched
                                ),
                            ),
                        )
                    )

    def test_duplicate_instrument_ids_are_rejected(self):
        context = make_context()
        first = make_observation(
            instrument_id="instrument-001",
            session_context=context,
        )
        duplicate = make_observation(
            instrument_id="instrument-001",
            session_context=context,
            last_price=Decimal("11.00"),
        )
        self.assertIsNot(first, duplicate)
        with self.assertRaisesRegex(
            ValueError,
            "^instrument_observations must not contain "
            "duplicate instrument_id$",
        ):
            validate_explicit_market_snapshot(
                make_snapshot(
                    session_context=context,
                    instrument_observations=(
                        first,
                        duplicate,
                    ),
                )
            )

    def test_first_bad_observation_fails_first(self):
        context = make_context()
        good = make_observation(
            instrument_id="instrument-001",
            session_context=context,
        )
        bad = make_observation(
            instrument_id="instrument-002",
            session_context=make_context(
                market_id="market-other"
            ),
        )
        later = make_observation(
            instrument_id="instrument-003",
            session_context=make_context(
                venue_id="venue-other"
            ),
        )
        with self.assertRaisesRegex(
            ValueError,
            "^market_id must match the snapshot "
            "market_id$",
        ):
            validate_explicit_market_snapshot(
                make_snapshot(
                    session_context=context,
                    instrument_observations=(
                        good,
                        bad,
                        later,
                    ),
                )
            )

    def test_order_objects_and_values_are_preserved(self):
        snapshot_id = " snapshot-é "
        context = make_context(
            session_context_id=" context-é "
        )
        second = make_observation(
            instrument_id="instrument-002",
            session_context=context,
        )
        first = make_observation(
            instrument_id="instrument-001",
            session_context=context,
        )
        observations = (second, first)
        snapshot = ExplicitMarketSnapshot(
            snapshot_id,
            context,
            observations,
        )

        self.assertIsNone(
            validate_explicit_market_snapshot(snapshot)
        )
        self.assertIs(
            snapshot.market_snapshot_id,
            snapshot_id,
        )
        self.assertIs(snapshot.session_context, context)
        self.assertIs(
            snapshot.instrument_observations,
            observations,
        )
        self.assertIs(
            snapshot.instrument_observations[0],
            second,
        )
        self.assertIs(
            snapshot.instrument_observations[1],
            first,
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
                "MarketInstrumentObservation.models",
                "MarketSessionContext.models",
            },
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "MarketInstrumentObservation.models",
                "MarketInstrumentObservation.validation",
                "MarketSessionContext.models",
                "MarketSessionContext.validation",
                "MarketSnapshot.models",
            },
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitMarketSnapshot"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["validate_explicit_market_snapshot"],
        )
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "ProviderGateway",
            "FactStore",
            "MarketSnapshotProducer",
            "Portfolio",
            "InvestmentResearchOrchestrator",
            "Automation",
            "ohlc",
            "valuation",
            "runtime",
            "persistence",
            "registry",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
