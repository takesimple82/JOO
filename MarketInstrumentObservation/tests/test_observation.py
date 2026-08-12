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
    MARKET_STATUS_VALUES,
    ExplicitMarketInstrumentObservation,
)
from MarketInstrumentObservation.validation import (
    validate_explicit_market_instrument_observation,
)
from MarketSessionContext.models import (
    ExplicitMarketSessionContext,
)


def make_instrument(
    *,
    instrument_id="instrument-001",
):
    return ExplicitMarketInstrument(instrument_id)


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


def make_observation(**overrides):
    values = {
        "instrument": make_instrument(),
        "session_context": make_context(),
        "last_price": Decimal("10.00"),
        "market_status": "open",
        "provenance": make_provenance(),
    }
    values.update(overrides)
    return ExplicitMarketInstrumentObservation(**values)


class StringSubclass(str):
    pass


class DecimalSubclass(Decimal):
    pass


class ObservationSubclass(
    ExplicitMarketInstrumentObservation
):
    pass


class InstrumentSubclass(ExplicitMarketInstrument):
    pass


class ContextSubclass(ExplicitMarketSessionContext):
    pass


class ProvenanceSubclass(
    ExplicitMarketFactProvenanceReference
):
    pass


class MarketInstrumentObservationTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(
            ExplicitMarketInstrumentObservation
        )
        self.assertEqual(
            [field.name for field in model_fields],
            [
                "instrument",
                "session_context",
                "last_price",
                "market_status",
                "provenance",
            ],
        )
        self.assertEqual(
            get_type_hints(
                ExplicitMarketInstrumentObservation
            ),
            {
                "instrument": ExplicitMarketInstrument,
                "session_context": (
                    ExplicitMarketSessionContext
                ),
                "last_price": Decimal,
                "market_status": str,
                "provenance": (
                    ExplicitMarketFactProvenanceReference
                ),
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitMarketInstrumentObservation.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitMarketInstrumentObservation.__dict__,
        )
        self.assertEqual(
            MARKET_STATUS_VALUES,
            (
                "pre_open",
                "open",
                "post_close",
                "closed",
                "halted",
                "unknown",
            ),
        )

    def test_frozen_hashable_and_structural(self):
        first = make_observation()
        same = make_observation()
        different = make_observation(
            last_price=Decimal("11")
        )
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.last_price = Decimal("12")

    def test_exact_observation_type_first(self):
        for value in (
            None,
            object(),
            {},
            ObservationSubclass(
                make_instrument(),
                make_context(),
                Decimal("1"),
                "open",
                make_provenance(),
            ),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^observation must be "
                    "ExplicitMarketInstrumentObservation$",
                ):
                    validate_explicit_market_instrument_observation(
                        value
                    )

    def test_exact_nested_types(self):
        cases = (
            (
                make_observation(instrument=None),
                "instrument must be ExplicitMarketInstrument",
            ),
            (
                make_observation(
                    instrument=InstrumentSubclass(
                        "instrument-001"
                    )
                ),
                "instrument must be ExplicitMarketInstrument",
            ),
            (
                make_observation(session_context=None),
                "session_context must be "
                "ExplicitMarketSessionContext",
            ),
            (
                make_observation(
                    session_context=ContextSubclass(
                        "session-context-001",
                        "market-001",
                        "venue-001",
                        "profile-001",
                        "timezone-001",
                        "calendar-001",
                    )
                ),
                "session_context must be "
                "ExplicitMarketSessionContext",
            ),
            (
                make_observation(provenance=None),
                "provenance must be "
                "ExplicitMarketFactProvenanceReference",
            ),
            (
                make_observation(
                    provenance=ProvenanceSubclass(
                        "fact-001",
                        "source-001",
                        "collected-at-001",
                    )
                ),
                "provenance must be "
                "ExplicitMarketFactProvenanceReference",
            ),
        )
        for observation, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    TypeError,
                    f"^{message}$",
                ):
                    validate_explicit_market_instrument_observation(
                        observation
                    )

    def test_last_price_requires_exact_finite_decimal(self):
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
                    "^last_price must be Decimal$",
                ):
                    validate_explicit_market_instrument_observation(
                        make_observation(last_price=value)
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
                    "^last_price must be finite$",
                ):
                    validate_explicit_market_instrument_observation(
                        make_observation(last_price=value)
                    )

    def test_last_price_sign_is_not_interpreted(self):
        for value in (
            Decimal("-10"),
            Decimal("-0"),
            Decimal("0"),
            Decimal("10"),
            Decimal("10.00"),
        ):
            with self.subTest(value=str(value)):
                self.assertIsNone(
                    validate_explicit_market_instrument_observation(
                        make_observation(last_price=value)
                    )
                )

    def test_market_status_vocabulary(self):
        for status in MARKET_STATUS_VALUES:
            with self.subTest(status=status):
                self.assertIsNone(
                    validate_explicit_market_instrument_observation(
                        make_observation(
                            market_status=status
                        )
                    )
                )
        for status in (
            "OPEN",
            "Open",
            "preopen",
            "pre-open",
            "after_hours",
            "trading",
            "",
            " ",
            "unknown ",
            " unknown",
        ):
            with self.subTest(status=repr(status)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^market_status must be one of "
                    "MARKET_STATUS_VALUES$",
                ):
                    validate_explicit_market_instrument_observation(
                        make_observation(
                            market_status=status
                        )
                    )

    def test_market_status_requires_exact_str(self):
        for value in (
            None,
            1,
            b"open",
            StringSubclass("open"),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^market_status must be str$",
                ):
                    validate_explicit_market_instrument_observation(
                        make_observation(
                            market_status=value
                        )
                    )

    def test_validation_order(self):
        cases = (
            (
                make_observation(
                    instrument=None,
                    session_context=None,
                    last_price=None,
                    market_status=None,
                    provenance=None,
                ),
                TypeError,
                "instrument must be ExplicitMarketInstrument",
            ),
            (
                make_observation(
                    session_context=None,
                    last_price=None,
                    market_status=None,
                    provenance=None,
                ),
                TypeError,
                "session_context must be "
                "ExplicitMarketSessionContext",
            ),
            (
                make_observation(
                    last_price=None,
                    market_status=None,
                    provenance=None,
                ),
                TypeError,
                "last_price must be Decimal",
            ),
            (
                make_observation(
                    last_price=Decimal("NaN"),
                    market_status=None,
                    provenance=None,
                ),
                ValueError,
                "last_price must be finite",
            ),
            (
                make_observation(
                    market_status=None,
                    provenance=None,
                ),
                TypeError,
                "market_status must be str",
            ),
            (
                make_observation(
                    market_status="not-a-status",
                    provenance=None,
                ),
                ValueError,
                "market_status must be one of "
                "MARKET_STATUS_VALUES",
            ),
            (
                make_observation(provenance=None),
                TypeError,
                "provenance must be "
                "ExplicitMarketFactProvenanceReference",
            ),
        )
        for observation, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_market_instrument_observation(
                        observation
                    )

    def test_upstream_validators_once_in_order(self):
        observation = make_observation()
        calls = []
        with patch(
            "MarketInstrumentObservation.validation"
            ".validate_explicit_market_instrument",
            side_effect=lambda value: calls.append(
                ("instrument", value)
            ),
        ) as instrument_validator, patch(
            "MarketInstrumentObservation.validation"
            ".validate_explicit_market_session_context",
            side_effect=lambda value: calls.append(
                ("context", value)
            ),
        ) as context_validator, patch(
            "MarketInstrumentObservation.validation"
            ".validate_explicit_market_fact_provenance_reference",
            side_effect=lambda value: calls.append(
                ("provenance", value)
            ),
        ) as provenance_validator:
            self.assertIsNone(
                validate_explicit_market_instrument_observation(
                    observation
                )
            )
        instrument_validator.assert_called_once_with(
            observation.instrument
        )
        context_validator.assert_called_once_with(
            observation.session_context
        )
        provenance_validator.assert_called_once_with(
            observation.provenance
        )
        self.assertEqual(
            calls,
            [
                ("instrument", observation.instrument),
                ("context", observation.session_context),
                ("provenance", observation.provenance),
            ],
        )

    def test_upstream_exceptions_propagate_unchanged(self):
        observation = make_observation()
        instrument_error = ValueError("instrument failure")
        with patch(
            "MarketInstrumentObservation.validation"
            ".validate_explicit_market_instrument",
            side_effect=instrument_error,
        ), patch(
            "MarketInstrumentObservation.validation"
            ".validate_explicit_market_session_context",
        ) as context_validator:
            with self.assertRaises(ValueError) as caught:
                validate_explicit_market_instrument_observation(
                    observation
                )
        self.assertIs(caught.exception, instrument_error)
        context_validator.assert_not_called()

        context_error = ValueError("context failure")
        with patch(
            "MarketInstrumentObservation.validation"
            ".validate_explicit_market_session_context",
            side_effect=context_error,
        ), patch(
            "MarketInstrumentObservation.validation"
            ".validate_explicit_market_fact_provenance_reference",
        ) as provenance_validator:
            with self.assertRaises(ValueError) as caught:
                validate_explicit_market_instrument_observation(
                    observation
                )
        self.assertIs(caught.exception, context_error)
        provenance_validator.assert_not_called()

        provenance_error = ValueError("provenance failure")
        with patch(
            "MarketInstrumentObservation.validation"
            ".validate_explicit_market_fact_provenance_reference",
            side_effect=provenance_error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_market_instrument_observation(
                    observation
                )
        self.assertIs(caught.exception, provenance_error)

    def test_objects_and_decimal_representation_are_preserved(self):
        instrument = make_instrument(
            instrument_id=" instrument-\u00e9 "
        )
        session_context = make_context(
            session_context_id=" context-e\u0301 "
        )
        last_price = Decimal("-0.00")
        market_status = "closed"
        provenance = make_provenance(
            fact_id=" fact-001 "
        )
        observation = ExplicitMarketInstrumentObservation(
            instrument,
            session_context,
            last_price,
            market_status,
            provenance,
        )
        self.assertIsNone(
            validate_explicit_market_instrument_observation(
                observation
            )
        )
        self.assertIs(observation.instrument, instrument)
        self.assertIs(
            observation.session_context,
            session_context,
        )
        self.assertIs(observation.last_price, last_price)
        self.assertIs(
            observation.market_status,
            market_status,
        )
        self.assertIs(observation.provenance, provenance)
        self.assertEqual(
            observation.last_price.as_tuple(),
            Decimal("-0.00").as_tuple(),
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
                "MarketFactProvenanceReference.models",
                "MarketInstrument.models",
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
                "decimal",
                "MarketFactProvenanceReference.models",
                "MarketFactProvenanceReference.validation",
                "MarketInstrument.models",
                "MarketInstrument.validation",
                "MarketInstrumentObservation.models",
                "MarketSessionContext.models",
                "MarketSessionContext.validation",
            },
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitMarketInstrumentObservation"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_market_instrument_"
                "observation"
            ],
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
            "bid",
            "ask",
            "volume",
            "turnover",
            "float",
            "runtime",
            "persistence",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
