import ast
import inspect
import unittest
import unicodedata
from dataclasses import FrozenInstanceError, MISSING, fields, is_dataclass
from pathlib import Path
from typing import get_type_hints

from PortfolioAllocationLegCapitalBucketLink.models import (
    ExplicitPortfolioAllocationLegCapitalBucketLink,
)
from PortfolioAllocationLegCapitalBucketLink.validation import (
    validate_explicit_portfolio_allocation_leg_capital_bucket_link,
)


def make_link(**overrides):
    values = {
        "allocation_leg_id": "leg-001",
        "capital_bucket_id": "bucket-001",
    }
    values.update(overrides)
    return ExplicitPortfolioAllocationLegCapitalBucketLink(**values)


class StringSubclass(str):
    pass


class LinkSubclass(ExplicitPortfolioAllocationLegCapitalBucketLink):
    pass


class PortfolioAllocationLegCapitalBucketLinkTests(unittest.TestCase):
    def assert_validation_error(self, error_type, message, link):
        with self.assertRaisesRegex(error_type, f"^{message}$"):
            validate_explicit_portfolio_allocation_leg_capital_bucket_link(link)

    def test_exact_frozen_dataclass_contract(self):
        model = ExplicitPortfolioAllocationLegCapitalBucketLink
        self.assertTrue(is_dataclass(model))
        self.assertTrue(model.__dataclass_params__.frozen)
        model_fields = fields(model)
        self.assertEqual(
            [field.name for field in model_fields],
            ["allocation_leg_id", "capital_bucket_id"],
        )
        self.assertEqual(
            get_type_hints(model),
            {"allocation_leg_id": str, "capital_bucket_id": str},
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn("__slots__", model.__dict__)
        self.assertNotIn("__post_init__", model.__dict__)
        self.assertEqual(
            {
                name
                for name, item in model.__dict__.items()
                if not name.startswith("_") and callable(item)
            },
            set(),
        )
        self.assertEqual(
            {
                name
                for name, item in model.__dict__.items()
                if not name.startswith("_") and isinstance(item, property)
            },
            set(),
        )

    def test_immutable_hashable_and_structurally_equal(self):
        first = make_link()
        duplicate = make_link()
        self.assertEqual(first, duplicate)
        self.assertEqual(hash(first), hash(duplicate))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(first, make_link(allocation_leg_id="leg-002"))
        self.assertNotEqual(first, make_link(capital_bucket_id="bucket-002"))
        with self.assertRaises(FrozenInstanceError):
            first.allocation_leg_id = "leg-002"
        with self.assertRaises(FrozenInstanceError):
            first.capital_bucket_id = "bucket-002"

    def test_exact_model_type_is_required_first(self):
        invalid = (
            None,
            object(),
            {},
            [],
            (),
            LinkSubclass("leg-001", "bucket-001"),
        )
        for item in invalid:
            with self.subTest(item_type=type(item)):
                self.assert_validation_error(
                    TypeError,
                    "link must be ExplicitPortfolioAllocationLegCapitalBucketLink",
                    item,
                )

    def test_identifiers_require_exact_builtin_strings(self):
        for field_name in ("allocation_leg_id", "capital_bucket_id"):
            for item in (None, 1, b"id", StringSubclass("id")):
                with self.subTest(field=field_name, item_type=type(item)):
                    self.assert_validation_error(
                        TypeError,
                        f"{field_name} must be str",
                        make_link(**{field_name: item}),
                    )

    def test_identifiers_reject_empty_and_whitespace_only_strings(self):
        for field_name in ("allocation_leg_id", "capital_bucket_id"):
            for item in ("", " ", "\t", "\n", " \t\n "):
                with self.subTest(field=field_name, item=repr(item)):
                    self.assert_validation_error(
                        ValueError,
                        f"{field_name} must not be blank",
                        make_link(**{field_name: item}),
                    )

    def test_validation_order_and_first_failure(self):
        cases = (
            (
                make_link(allocation_leg_id=None, capital_bucket_id=None),
                TypeError,
                "allocation_leg_id must be str",
            ),
            (
                make_link(allocation_leg_id=" ", capital_bucket_id=None),
                ValueError,
                "allocation_leg_id must not be blank",
            ),
            (
                make_link(capital_bucket_id=None),
                TypeError,
                "capital_bucket_id must be str",
            ),
            (
                make_link(capital_bucket_id=" "),
                ValueError,
                "capital_bucket_id must not be blank",
            ),
        )
        for link, error_type, message in cases:
            with self.subTest(message=message):
                self.assert_validation_error(error_type, message, link)

    def test_exact_strings_whitespace_case_and_unicode_are_preserved(self):
        composed = unicodedata.normalize("NFC", "e\u0301")
        decomposed = unicodedata.normalize("NFD", "\u00e9")
        allocation_leg_id = " Leg-" + decomposed + " "
        capital_bucket_id = " Bucket-" + composed + " "
        link = ExplicitPortfolioAllocationLegCapitalBucketLink(
            allocation_leg_id,
            capital_bucket_id,
        )
        self.assertIs(link.allocation_leg_id, allocation_leg_id)
        self.assertIs(link.capital_bucket_id, capital_bucket_id)
        self.assertIsNone(
            validate_explicit_portfolio_allocation_leg_capital_bucket_link(link)
        )
        self.assertIs(link.allocation_leg_id, allocation_leg_id)
        self.assertIs(link.capital_bucket_id, capital_bucket_id)
        self.assertEqual(link.allocation_leg_id, " Leg-e\u0301 ")
        self.assertEqual(link.capital_bucket_id, " Bucket-\u00e9 ")
        self.assertNotEqual(composed, decomposed)
        self.assertNotEqual(make_link(allocation_leg_id="leg"), make_link(allocation_leg_id="LEG"))

    def test_duplicates_and_many_at_either_endpoint_are_accepted(self):
        duplicate_one = make_link()
        duplicate_two = make_link()
        same_leg = make_link(capital_bucket_id="bucket-002")
        same_bucket = make_link(allocation_leg_id="leg-002")
        for link in (duplicate_one, duplicate_two, same_leg, same_bucket):
            self.assertIsNone(
                validate_explicit_portfolio_allocation_leg_capital_bucket_link(link)
            )
        self.assertEqual(duplicate_one, duplicate_two)
        self.assertIsNot(duplicate_one, duplicate_two)
        self.assertEqual(duplicate_one.allocation_leg_id, same_leg.allocation_leg_id)
        self.assertEqual(duplicate_one.capital_bucket_id, same_bucket.capital_bucket_id)

    def test_optionality_is_absence_of_a_record_only(self):
        self.assert_validation_error(
            TypeError,
            "link must be ExplicitPortfolioAllocationLegCapitalBucketLink",
            None,
        )
        self.assert_validation_error(
            ValueError,
            "allocation_leg_id must not be blank",
            make_link(allocation_leg_id=""),
        )
        self.assert_validation_error(
            ValueError,
            "capital_bucket_id must not be blank",
            make_link(capital_bucket_id=""),
        )
        with self.assertRaises(TypeError):
            ExplicitPortfolioAllocationLegCapitalBucketLink()

    def test_signature_import_allowlists_and_definitions_are_exact(self):
        validator = validate_explicit_portfolio_allocation_leg_capital_bucket_link
        signature = inspect.signature(validator)
        self.assertEqual(list(signature.parameters), ["link"])
        self.assertEqual(
            signature.parameters["link"].kind,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
        self.assertIs(
            signature.parameters["link"].annotation,
            ExplicitPortfolioAllocationLegCapitalBucketLink,
        )
        self.assertIs(signature.return_annotation, None)

        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse((root / "models.py").read_text())
        validation_tree = ast.parse((root / "validation.py").read_text())
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
            {"PortfolioAllocationLegCapitalBucketLink.models"},
        )
        self.assertEqual(
            [node.name for node in model_tree.body if isinstance(node, ast.ClassDef)],
            ["ExplicitPortfolioAllocationLegCapitalBucketLink"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["validate_explicit_portfolio_allocation_leg_capital_bucket_link"],
        )

    def test_forbidden_fields_and_responsibilities_are_absent(self):
        root = Path(__file__).resolve().parents[1]
        production = (root / "models.py").read_text() + (root / "validation.py").read_text()
        for forbidden in (
            "PortfolioAllocationLeg.models",
            "PortfolioCapitalBucket.models",
            "PortfolioRiskBudget",
            "allocation_proposal_id",
            "position_id",
            "recommendation_id",
            "portfolio_id",
            "portfolio_snapshot_id",
            "risk_budget_id",
            "unit_id",
            "quantity",
            "amount",
            "currency",
            "weight",
            "ratio",
            "percentage",
            "repository",
            "registry",
            "resolver",
            "lookup",
            "runtime",
            "orchestration",
            "collection",
            "ordering",
            "uniqueness",
        ):
            self.assertNotIn(forbidden, production)

    def test_readme_covers_contract_without_contradiction(self):
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
        normalized = " ".join(readme.split())
        required = (
            "PortfolioAllocationLegCapitalBucketLink",
            "ExplicitPortfolioAllocationLegCapitalBucketLink",
            "validate_explicit_portfolio_allocation_leg_capital_bucket_link(link: ExplicitPortfolioAllocationLegCapitalBucketLink) -> None",
            "allocation_leg_id: str`, then `capital_bucket_id: str",
            "frozen, hashable",
            "first failure wins",
            "link must be ExplicitPortfolioAllocationLegCapitalBucketLink",
            "allocation_leg_id must not be blank",
            "capital_bucket_id must not be blank",
            "exact built-in `str`",
            "object identity",
            "surrounding whitespace",
            "standard frozen-dataclass structural equality",
            "independent exact duplicates are structurally accepted",
            "optional per Leg",
            "absence of a link record",
            "Dependency and import boundary",
            "no endpoint lookup or existence proof",
            "Denormalization prohibitions",
            "Risk Budget association remains deferred",
            "constraint architecture remains deferred",
            "Non-responsibilities",
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, normalized)

        contradictory = (
            "proves endpoint existence",
            "validates both endpoints",
            "enforces one Bucket per Leg",
            "selects a primary Bucket",
            "reserves capital",
        )
        for fragment in contradictory:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, normalized)


if __name__ == "__main__":
    unittest.main()
