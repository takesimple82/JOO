import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import get_type_hints

from MarketSessionContext.models import (
    ExplicitMarketSessionContext,
)
from MarketSessionContext.validation import (
    validate_explicit_market_session_context,
)


def make_context(**overrides):
    values = {
        "session_context_id": "session-context-001",
        "market_id": "market-001",
        "venue_id": "venue-001",
        "session_profile_id": "profile-001",
        "timezone_id": "timezone-001",
        "calendar_id": "calendar-001",
    }
    values.update(overrides)
    return ExplicitMarketSessionContext(**values)


class StringSubclass(str):
    pass


class ContextSubclass(ExplicitMarketSessionContext):
    pass


FIELD_NAMES = (
    "session_context_id",
    "market_id",
    "venue_id",
    "session_profile_id",
    "timezone_id",
    "calendar_id",
)


class MarketSessionContextTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(
            ExplicitMarketSessionContext
        )
        self.assertEqual(
            [field.name for field in model_fields],
            list(FIELD_NAMES),
        )
        self.assertEqual(
            get_type_hints(
                ExplicitMarketSessionContext
            ),
            {name: str for name in FIELD_NAMES},
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitMarketSessionContext.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitMarketSessionContext.__dict__,
        )

    def test_frozen_hashable_structural_equality(self):
        first = make_context()
        same = make_context()
        different = make_context(
            session_context_id="session-context-002"
        )
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.market_id = "replacement"

    def test_exact_model_type(self):
        for value in (
            None,
            object(),
            {},
            ContextSubclass(
                "session-context-001",
                "market-001",
                "venue-001",
                "profile-001",
                "timezone-001",
                "calendar-001",
            ),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^context must be "
                    "ExplicitMarketSessionContext$",
                ):
                    validate_explicit_market_session_context(
                        value
                    )

    def test_exact_string_types(self):
        invalid = (
            None,
            1,
            b"identity",
            StringSubclass("identity"),
        )
        for field_name in FIELD_NAMES:
            for value in invalid:
                with self.subTest(
                    field=field_name,
                    value_type=type(value),
                ):
                    with self.assertRaisesRegex(
                        TypeError,
                        f"^{field_name} must be str$",
                    ):
                        validate_explicit_market_session_context(
                            make_context(
                                **{field_name: value}
                            )
                        )

    def test_blank_identifiers_are_rejected(self):
        for field_name in FIELD_NAMES:
            for value in ("", " ", "\t\n"):
                with self.subTest(
                    field=field_name,
                    value=repr(value),
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        f"^{field_name} must not be blank$",
                    ):
                        validate_explicit_market_session_context(
                            make_context(
                                **{field_name: value}
                            )
                        )

    def test_validation_order(self):
        cases = (
            (
                make_context(
                    session_context_id=None,
                    market_id=None,
                ),
                TypeError,
                "session_context_id must be str",
            ),
            (
                make_context(
                    session_context_id=" ",
                    market_id=None,
                ),
                ValueError,
                "session_context_id must not be blank",
            ),
            (
                make_context(market_id=None),
                TypeError,
                "market_id must be str",
            ),
            (
                make_context(market_id=" "),
                ValueError,
                "market_id must not be blank",
            ),
            (
                make_context(venue_id=None),
                TypeError,
                "venue_id must be str",
            ),
            (
                make_context(session_profile_id=None),
                TypeError,
                "session_profile_id must be str",
            ),
            (
                make_context(timezone_id=None),
                TypeError,
                "timezone_id must be str",
            ),
            (
                make_context(calendar_id=None),
                TypeError,
                "calendar_id must be str",
            ),
        )
        for context, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_market_session_context(
                        context
                    )

    def test_success_preserves_identifiers(self):
        values = {
            "session_context_id": " context-\u00e9 ",
            "market_id": " market-e\u0301 ",
            "venue_id": " venue-001 ",
            "session_profile_id": " profile-001 ",
            "timezone_id": " timezone-001 ",
            "calendar_id": " calendar-001 ",
        }
        context = ExplicitMarketSessionContext(**values)
        self.assertIsNone(
            validate_explicit_market_session_context(
                context
            )
        )
        for field_name, value in values.items():
            self.assertIs(
                getattr(context, field_name),
                value,
            )

    def test_duplicate_contexts_are_not_checked(self):
        first = make_context()
        duplicate = make_context()
        for context in (first, duplicate):
            self.assertIsNone(
                validate_explicit_market_session_context(
                    context
                )
            )
        self.assertEqual(first, duplicate)

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
            {"dataclasses"},
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {"MarketSessionContext.models"},
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitMarketSessionContext"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_market_session_context"
            ],
        )
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "MarketEndpoint",
            "MarketVenue",
            "ProviderGateway",
            "FactStore",
            "MarketSnapshotProducer",
            "Portfolio",
            "InvestmentResearchOrchestrator",
            "Automation",
            "KRX",
            "NYSE",
            "Nasdaq",
            "Asia/Seoul",
            "America/New_York",
            "runtime",
            "persistence",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
