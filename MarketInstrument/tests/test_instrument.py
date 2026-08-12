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

from MarketInstrument.models import ExplicitMarketInstrument
from MarketInstrument.validation import (
    validate_explicit_market_instrument,
)


def make_instrument(**overrides):
    values = {
        "instrument_id": "instrument-001",
    }
    values.update(overrides)
    return ExplicitMarketInstrument(**values)


class StringSubclass(str):
    pass


class InstrumentSubclass(ExplicitMarketInstrument):
    pass


class ExplicitMarketInstrumentTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            ExplicitMarketInstrument.__name__,
            "ExplicitMarketInstrument",
        )
        self.assertTrue(
            is_dataclass(ExplicitMarketInstrument)
        )
        self.assertTrue(
            ExplicitMarketInstrument
            .__dataclass_params__.frozen
        )

        model_fields = fields(ExplicitMarketInstrument)
        self.assertEqual(
            [field.name for field in model_fields],
            ["instrument_id"],
        )
        self.assertEqual(
            get_type_hints(ExplicitMarketInstrument),
            {"instrument_id": str},
        )
        self.assertEqual(len(model_fields), 1)
        self.assertIs(model_fields[0].default, MISSING)
        self.assertIs(
            model_fields[0].default_factory,
            MISSING,
        )
        self.assertNotIn(
            "__post_init__",
            ExplicitMarketInstrument.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitMarketInstrument.__dict__,
        )
        public_methods = {
            name
            for name, value
            in ExplicitMarketInstrument.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_model_is_frozen_hashable_and_structural(self):
        first = make_instrument()
        same = make_instrument()
        different = make_instrument(
            instrument_id="instrument-002"
        )

        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.instrument_id = "replacement"

    def test_unknown_constructor_fields_fail_naturally(self):
        for field_name in (
            "ticker",
            "isin",
            "cusip",
            "display_name",
            "currency",
        ):
            with self.subTest(field_name=field_name):
                with self.assertRaises(TypeError):
                    ExplicitMarketInstrument(
                        instrument_id="instrument-001",
                        **{field_name: "not-owned"},
                    )

    def test_validator_returns_none_on_success(self):
        self.assertIsNone(
            validate_explicit_market_instrument(
                make_instrument()
            )
        )

    def test_validator_requires_exact_model_type_first(self):
        invalid = (
            None,
            object(),
            {},
            (),
            InstrumentSubclass("instrument-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^instrument must be "
                    "ExplicitMarketInstrument$",
                ):
                    validate_explicit_market_instrument(value)

    def test_instrument_id_requires_exact_built_in_string(self):
        invalid = (
            None,
            1,
            b"instrument-001",
            StringSubclass("instrument-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^instrument_id must be str$",
                ):
                    validate_explicit_market_instrument(
                        make_instrument(
                            instrument_id=value
                        )
                    )

    def test_instrument_id_rejects_blank_values(self):
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
                    "^instrument_id must not be blank$",
                ):
                    validate_explicit_market_instrument(
                        make_instrument(
                            instrument_id=value
                        )
                    )

    def test_identity_is_preserved_without_normalization(self):
        instrument_id = " instrument-\u00e9 "
        instrument = ExplicitMarketInstrument(
            instrument_id
        )
        model_identity = id(instrument)

        result = validate_explicit_market_instrument(
            instrument
        )

        self.assertIsNone(result)
        self.assertEqual(id(instrument), model_identity)
        self.assertIs(
            instrument.instrument_id,
            instrument_id,
        )
        self.assertEqual(
            instrument.instrument_id,
            " instrument-\u00e9 ",
        )

    def test_identity_equality_does_not_normalize(self):
        distinct_pairs = (
            ("instrument", "INSTRUMENT"),
            ("instrument", " instrument "),
            ("\u00e9", "e\u0301"),
        )
        for left, right in distinct_pairs:
            with self.subTest(
                left=repr(left),
                right=repr(right),
            ):
                self.assertNotEqual(
                    ExplicitMarketInstrument(left),
                    ExplicitMarketInstrument(right),
                )

    def test_duplicate_identity_is_not_checked(self):
        first = ExplicitMarketInstrument("instrument-001")
        second = ExplicitMarketInstrument("instrument-001")

        self.assertIsNone(
            validate_explicit_market_instrument(first)
        )
        self.assertIsNone(
            validate_explicit_market_instrument(second)
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
            {"MarketInstrument.models"},
        )

        production_source = (
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
            "ticker",
            "isin",
            "cusip",
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
            ["ExplicitMarketInstrument"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["validate_explicit_market_instrument"],
        )


if __name__ == "__main__":
    unittest.main()
