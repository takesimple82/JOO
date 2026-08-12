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

from MarketEndpoint.models import ExplicitMarket
from MarketEndpoint.validation import (
    validate_explicit_market,
)


def make_market(**overrides):
    values = {
        "market_id": "market-001",
    }
    values.update(overrides)
    return ExplicitMarket(**values)


class StringSubclass(str):
    pass


class MarketSubclass(ExplicitMarket):
    pass


class ExplicitMarketTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            ExplicitMarket.__name__,
            "ExplicitMarket",
        )
        self.assertTrue(is_dataclass(ExplicitMarket))
        self.assertTrue(
            ExplicitMarket.__dataclass_params__.frozen
        )

        model_fields = fields(ExplicitMarket)
        self.assertEqual(
            [field.name for field in model_fields],
            ["market_id"],
        )
        self.assertEqual(
            get_type_hints(ExplicitMarket),
            {"market_id": str},
        )
        self.assertEqual(len(model_fields), 1)
        self.assertIs(model_fields[0].default, MISSING)
        self.assertIs(
            model_fields[0].default_factory,
            MISSING,
        )
        self.assertNotIn(
            "__post_init__",
            ExplicitMarket.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitMarket.__dict__,
        )
        public_methods = {
            name
            for name, value
            in ExplicitMarket.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_model_is_frozen_hashable_and_structural(self):
        first = make_market()
        same = make_market()
        different = make_market(
            market_id="market-002"
        )

        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.market_id = "replacement"

    def test_unknown_constructor_fields_fail_naturally(self):
        for field_name in (
            "name",
            "ticker",
            "venue_id",
            "exchange",
        ):
            with self.subTest(field_name=field_name):
                with self.assertRaises(TypeError):
                    ExplicitMarket(
                        market_id="market-001",
                        **{field_name: "not-owned"},
                    )

    def test_validator_returns_none_on_success(self):
        self.assertIsNone(
            validate_explicit_market(
                make_market()
            )
        )

    def test_validator_requires_exact_model_type_first(self):
        invalid = (
            None,
            object(),
            {},
            (),
            MarketSubclass("market-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^market must be ExplicitMarket$",
                ):
                    validate_explicit_market(value)

    def test_market_id_requires_exact_built_in_string(self):
        invalid = (
            None,
            1,
            b"market-001",
            StringSubclass("market-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^market_id must be str$",
                ):
                    validate_explicit_market(
                        make_market(
                            market_id=value
                        )
                    )

    def test_market_id_rejects_blank_values(self):
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
                    "^market_id must not be blank$",
                ):
                    validate_explicit_market(
                        make_market(
                            market_id=value
                        )
                    )

    def test_identity_is_preserved_without_normalization(self):
        market_id = " market-\u00e9 "
        market = ExplicitMarket(market_id)
        model_identity = id(market)

        result = validate_explicit_market(market)

        self.assertIsNone(result)
        self.assertEqual(id(market), model_identity)
        self.assertIs(
            market.market_id,
            market_id,
        )
        self.assertEqual(
            market.market_id,
            " market-\u00e9 ",
        )

    def test_identity_equality_does_not_normalize(self):
        distinct_pairs = (
            ("market", "MARKET"),
            ("market", " market "),
            ("\u00e9", "e\u0301"),
        )
        for left, right in distinct_pairs:
            with self.subTest(
                left=repr(left),
                right=repr(right),
            ):
                self.assertNotEqual(
                    ExplicitMarket(left),
                    ExplicitMarket(right),
                )

    def test_duplicate_identity_is_not_checked(self):
        first = ExplicitMarket("market-001")
        second = ExplicitMarket("market-001")

        self.assertIsNone(
            validate_explicit_market(first)
        )
        self.assertIsNone(
            validate_explicit_market(second)
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
            {"MarketEndpoint.models"},
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
            "venue_id",
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
            ["ExplicitMarket"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["validate_explicit_market"],
        )


if __name__ == "__main__":
    unittest.main()
