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

from MarketVenue.models import ExplicitMarketVenue
from MarketVenue.validation import (
    validate_explicit_market_venue,
)


def make_venue(**overrides):
    values = {
        "venue_id": "venue-001",
    }
    values.update(overrides)
    return ExplicitMarketVenue(**values)


class StringSubclass(str):
    pass


class VenueSubclass(ExplicitMarketVenue):
    pass


class ExplicitMarketVenueTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            ExplicitMarketVenue.__name__,
            "ExplicitMarketVenue",
        )
        self.assertTrue(is_dataclass(ExplicitMarketVenue))
        self.assertTrue(
            ExplicitMarketVenue.__dataclass_params__.frozen
        )

        model_fields = fields(ExplicitMarketVenue)
        self.assertEqual(
            [field.name for field in model_fields],
            ["venue_id"],
        )
        self.assertEqual(
            get_type_hints(ExplicitMarketVenue),
            {"venue_id": str},
        )
        self.assertEqual(len(model_fields), 1)
        self.assertIs(model_fields[0].default, MISSING)
        self.assertIs(
            model_fields[0].default_factory,
            MISSING,
        )
        self.assertNotIn(
            "__post_init__",
            ExplicitMarketVenue.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitMarketVenue.__dict__,
        )
        public_methods = {
            name
            for name, value
            in ExplicitMarketVenue.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_model_is_frozen_hashable_and_structural(self):
        first = make_venue()
        same = make_venue()
        different = make_venue(venue_id="venue-002")

        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.venue_id = "replacement"

    def test_unknown_constructor_fields_fail_naturally(self):
        for field_name in (
            "name",
            "market_id",
            "exchange",
            "mic",
        ):
            with self.subTest(field_name=field_name):
                with self.assertRaises(TypeError):
                    ExplicitMarketVenue(
                        venue_id="venue-001",
                        **{field_name: "not-owned"},
                    )

    def test_validator_returns_none_on_success(self):
        self.assertIsNone(
            validate_explicit_market_venue(
                make_venue()
            )
        )

    def test_validator_requires_exact_model_type_first(self):
        invalid = (
            None,
            object(),
            {},
            (),
            VenueSubclass("venue-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^venue must be ExplicitMarketVenue$",
                ):
                    validate_explicit_market_venue(value)

    def test_venue_id_requires_exact_built_in_string(self):
        invalid = (
            None,
            1,
            b"venue-001",
            StringSubclass("venue-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^venue_id must be str$",
                ):
                    validate_explicit_market_venue(
                        make_venue(venue_id=value)
                    )

    def test_venue_id_rejects_blank_values(self):
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
                    "^venue_id must not be blank$",
                ):
                    validate_explicit_market_venue(
                        make_venue(venue_id=value)
                    )

    def test_identity_is_preserved_without_normalization(self):
        venue_id = " venue-\u00e9 "
        venue = ExplicitMarketVenue(venue_id)
        model_identity = id(venue)

        result = validate_explicit_market_venue(venue)

        self.assertIsNone(result)
        self.assertEqual(id(venue), model_identity)
        self.assertIs(venue.venue_id, venue_id)
        self.assertEqual(
            venue.venue_id,
            " venue-\u00e9 ",
        )

    def test_identity_equality_does_not_normalize(self):
        distinct_pairs = (
            ("venue", "VENUE"),
            ("venue", " venue "),
            ("\u00e9", "e\u0301"),
        )
        for left, right in distinct_pairs:
            with self.subTest(
                left=repr(left),
                right=repr(right),
            ):
                self.assertNotEqual(
                    ExplicitMarketVenue(left),
                    ExplicitMarketVenue(right),
                )

    def test_duplicate_identity_is_not_checked(self):
        first = ExplicitMarketVenue("venue-001")
        second = ExplicitMarketVenue("venue-001")

        self.assertIsNone(
            validate_explicit_market_venue(first)
        )
        self.assertIsNone(
            validate_explicit_market_venue(second)
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
            {"MarketVenue.models"},
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
            "market_id",
            "instrument_id",
            "ticker",
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
            ["ExplicitMarketVenue"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["validate_explicit_market_venue"],
        )


if __name__ == "__main__":
    unittest.main()
