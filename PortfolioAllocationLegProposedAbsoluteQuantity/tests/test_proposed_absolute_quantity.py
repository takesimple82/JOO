import ast
import inspect
import unittest
import unicodedata
from dataclasses import FrozenInstanceError, MISSING, fields, is_dataclass
from decimal import Decimal, Inexact, getcontext, localcontext
from pathlib import Path
from typing import get_type_hints

from PortfolioAllocationLegProposedAbsoluteQuantity.models import (
    ExplicitPortfolioAllocationLegProposedAbsoluteQuantity,
)
from PortfolioAllocationLegProposedAbsoluteQuantity.validation import (
    validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity,
)


def make_content(**overrides):
    values = {
        "allocation_leg_id": "leg-001",
        "unit_id": "shares",
        "value": Decimal("12.50"),
    }
    values.update(overrides)
    return ExplicitPortfolioAllocationLegProposedAbsoluteQuantity(**values)


class StringSubclass(str):
    pass


class DecimalSubclass(Decimal):
    pass


class ContentSubclass(ExplicitPortfolioAllocationLegProposedAbsoluteQuantity):
    pass


class ProposedAbsoluteQuantityTests(unittest.TestCase):
    def assert_validation_error(self, error_type, message, content):
        with self.assertRaisesRegex(error_type, f"^{message}$"):
            validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity(
                content
            )

    def test_exact_dataclass_contract(self):
        model = ExplicitPortfolioAllocationLegProposedAbsoluteQuantity
        self.assertTrue(is_dataclass(model))
        self.assertTrue(model.__dataclass_params__.frozen)
        model_fields = fields(model)
        self.assertEqual(
            [field.name for field in model_fields],
            ["allocation_leg_id", "unit_id", "value"],
        )
        self.assertEqual(
            get_type_hints(model),
            {"allocation_leg_id": str, "unit_id": str, "value": Decimal},
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn("__slots__", model.__dict__)
        self.assertNotIn("__post_init__", model.__dict__)
        self.assertEqual(
            {
                name
                for name, value in model.__dict__.items()
                if not name.startswith("_") and callable(value)
            },
            set(),
        )
        self.assertEqual(
            {
                name
                for name, value in model.__dict__.items()
                if not name.startswith("_") and isinstance(value, property)
            },
            set(),
        )

    def test_frozen_hashable_structural_equality_and_decimal_equality(self):
        first = make_content()
        duplicate = make_content()
        self.assertEqual(first, duplicate)
        self.assertEqual(hash(first), hash(duplicate))
        self.assertNotEqual(first, make_content(allocation_leg_id="leg-002"))
        self.assertNotEqual(first, make_content(unit_id="contracts"))
        self.assertNotEqual(first, make_content(value=Decimal("12.51")))
        supplied = Decimal("12.500")
        equal_representation = make_content(value=supplied)
        self.assertEqual(first, equal_representation)
        self.assertEqual(hash(first), hash(equal_representation))
        self.assertIs(equal_representation.value, supplied)
        with self.assertRaises(FrozenInstanceError):
            first.value = Decimal("1")

    def test_exact_model_type_is_required_first(self):
        invalid = (
            None,
            object(),
            {},
            [],
            (),
            ContentSubclass("leg-001", "shares", Decimal("1")),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                self.assert_validation_error(
                    TypeError,
                    "content must be ExplicitPortfolioAllocationLegProposedAbsoluteQuantity",
                    value,
                )

    def test_identifiers_require_exact_strings_and_nonblank_values(self):
        for field_name in ("allocation_leg_id", "unit_id"):
            for value in (None, 1, b"id", StringSubclass("id")):
                with self.subTest(field=field_name, value_type=type(value)):
                    self.assert_validation_error(
                        TypeError,
                        f"{field_name} must be str",
                        make_content(**{field_name: value}),
                    )
            for value in ("", " ", "\t", "\n", " \t\n "):
                with self.subTest(field=field_name, value=repr(value)):
                    self.assert_validation_error(
                        ValueError,
                        f"{field_name} must not be blank",
                        make_content(**{field_name: value}),
                    )

    def test_nonblank_identifier_strings_are_accepted_and_preserved(self):
        composed = unicodedata.normalize("NFC", "e\u0301")
        decomposed = unicodedata.normalize("NFD", "\u00e9")
        values = (" id ", "Id", "id", composed, decomposed)
        for value in values:
            for field_name in ("allocation_leg_id", "unit_id"):
                with self.subTest(field=field_name, value=repr(value)):
                    content = make_content(**{field_name: value})
                    self.assertIsNone(
                        validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity(
                            content
                        )
                    )
                    self.assertIs(getattr(content, field_name), value)
        self.assertNotEqual(composed, decomposed)

    def test_value_requires_exact_decimal(self):
        invalid = (None, 1, 1.0, "1", DecimalSubclass("1"))
        for value in invalid:
            with self.subTest(value_type=type(value)):
                self.assert_validation_error(
                    TypeError, "value must be Decimal", make_content(value=value)
                )

    def test_all_finite_decimal_forms_are_accepted(self):
        values = (
            Decimal("12.5"),
            Decimal("-12.5"),
            Decimal("0"),
            Decimal("+0"),
            Decimal("-0"),
            Decimal("1E+1000"),
            Decimal("1.2300"),
        )
        for value in values:
            with self.subTest(value=str(value)):
                content = make_content(value=value)
                before = value.as_tuple()
                self.assertIsNone(
                    validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity(
                        content
                    )
                )
                self.assertIs(content.value, value)
                self.assertEqual(content.value.as_tuple(), before)

    def test_nonfinite_decimals_are_rejected(self):
        for value in (
            Decimal("Infinity"),
            Decimal("-Infinity"),
            Decimal("NaN"),
            Decimal("sNaN"),
        ):
            with self.subTest(value=str(value)):
                self.assert_validation_error(
                    ValueError, "value must be finite", make_content(value=value)
                )

    def test_validation_order_first_failure_transitions(self):
        cases = (
            (make_content(allocation_leg_id=None, unit_id=None, value=None), TypeError, "allocation_leg_id must be str"),
            (make_content(allocation_leg_id=" ", unit_id=None, value=None), ValueError, "allocation_leg_id must not be blank"),
            (make_content(unit_id=None, value=None), TypeError, "unit_id must be str"),
            (make_content(unit_id=" ", value=None), ValueError, "unit_id must not be blank"),
            (make_content(value=None), TypeError, "value must be Decimal"),
            (make_content(value=Decimal("NaN")), ValueError, "value must be finite"),
        )
        for content, error_type, message in cases:
            with self.subTest(message=message):
                self.assert_validation_error(error_type, message, content)

    def test_exact_objects_and_decimal_representation_are_preserved(self):
        allocation_leg_id = " Leg-e\u0301 "
        unit_id = " Unit-\u00e9 "
        value = Decimal("-0.000")
        content = ExplicitPortfolioAllocationLegProposedAbsoluteQuantity(
            allocation_leg_id, unit_id, value
        )
        before = value.as_tuple()
        self.assertIs(content.allocation_leg_id, allocation_leg_id)
        self.assertIs(content.unit_id, unit_id)
        self.assertIs(content.value, value)
        self.assertIsNone(
            validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity(
                content
            )
        )
        self.assertIs(content.allocation_leg_id, allocation_leg_id)
        self.assertIs(content.unit_id, unit_id)
        self.assertIs(content.value, value)
        self.assertEqual(value.as_tuple(), before)
        self.assertTrue(value.is_signed())

    def test_validation_does_not_change_decimal_context(self):
        with localcontext() as context:
            context.prec = 7
            context.rounding = "ROUND_FLOOR"
            context.traps[Inexact] = False
            context.clear_flags()
            before = context.copy()
            self.assertIsNone(
                validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity(
                    make_content(value=Decimal("1E+9999"))
                )
            )
            after = getcontext()
            self.assertEqual(after.prec, before.prec)
            self.assertEqual(after.rounding, before.rounding)
            self.assertEqual(after.traps, before.traps)
            self.assertEqual(after.flags, before.flags)

    def test_duplicates_shared_leg_and_equal_values_validate_independently(self):
        duplicate_one = make_content()
        duplicate_two = make_content()
        same_leg = make_content(unit_id="contracts", value=Decimal("2"))
        distinct_leg = make_content(allocation_leg_id="leg-002")
        zero = make_content(value=Decimal("0"))
        for content in (duplicate_one, duplicate_two, same_leg, distinct_leg, zero):
            self.assertIsNone(
                validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity(
                    content
                )
            )
        self.assertEqual(duplicate_one, duplicate_two)
        self.assertEqual(duplicate_one.allocation_leg_id, same_leg.allocation_leg_id)
        self.assertEqual(duplicate_one.unit_id, distinct_leg.unit_id)
        self.assertEqual(duplicate_one.value, distinct_leg.value)
        self.assertEqual(zero.value, Decimal("0"))

    def test_signature_import_boundary_and_definitions_are_exact(self):
        validator = validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity
        signature = inspect.signature(validator)
        self.assertEqual(list(signature.parameters), ["content"])
        self.assertEqual(signature.parameters["content"].kind, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        self.assertIs(
            signature.parameters["content"].annotation,
            ExplicitPortfolioAllocationLegProposedAbsoluteQuantity,
        )
        self.assertIs(signature.return_annotation, None)
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse((root / "models.py").read_text())
        validation_tree = ast.parse((root / "validation.py").read_text())
        self.assertEqual(
            {node.module for node in ast.walk(model_tree) if isinstance(node, ast.ImportFrom)},
            {"dataclasses", "decimal"},
        )
        self.assertEqual(
            {node.module for node in ast.walk(validation_tree) if isinstance(node, ast.ImportFrom)},
            {"decimal", "PortfolioAllocationLegProposedAbsoluteQuantity.models"},
        )
        self.assertEqual(
            [node.name for node in model_tree.body if isinstance(node, ast.ClassDef)],
            ["ExplicitPortfolioAllocationLegProposedAbsoluteQuantity"],
        )
        self.assertEqual(
            [node.name for node in validation_tree.body if isinstance(node, ast.FunctionDef)],
            ["validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity"],
        )

    def test_production_boundary_and_readme_contract(self):
        root = Path(__file__).resolve().parents[1]
        production = (root / "models.py").read_text() + (root / "validation.py").read_text()
        for forbidden in (
            "PortfolioAllocationLeg.models",
            "PortfolioAllocationLeg.validation",
            "allocation_proposal_id",
            "position_id",
            "recommendation_id",
            "portfolio_id",
            "portfolio_snapshot_id",
            "capital_bucket_id",
            "risk_budget_id",
            "repository",
            "registry",
            "lookup",
            "persistence",
            "runtime",
        ):
            self.assertNotIn(forbidden, production)
        readme = (root / "README.md").read_text()
        normalized = " ".join(readme.split())
        for fragment in (
            "ExplicitPortfolioAllocationLegProposedAbsoluteQuantity",
            "validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity(content: ExplicitPortfolioAllocationLegProposedAbsoluteQuantity) -> None",
            "allocation_leg_id: str`, `unit_id: str`, `value: Decimal",
            "frozen, hashable",
            "first failure wins",
            "content must be ExplicitPortfolioAllocationLegProposedAbsoluteQuantity",
            "value must be finite",
            "object identity",
            "signed zero",
            "surrounding whitespace",
            "foreign-ID-only",
            "standard Decimal equality",
            "one record per Allocation Leg",
            "duplicates are structurally accepted",
            "owns no ordering",
            "zero is explicit content",
            "does not interpret sign",
            "Dependency boundary",
            "Non-responsibilities",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, normalized)


if __name__ == "__main__":
    unittest.main()
