import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from decimal import Decimal
from pathlib import Path
from typing import get_type_hints

from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from EvidenceProposition.validation import (
    validate_exact_observed_numeric_proposition,
)


IDENTIFIER_FIELDS = (
    "proposition_id",
    "finding_id",
    "subject_id",
    "predicate_id",
    "unit_id",
    "effective_context_id",
)


def make_proposition(
    **overrides,
) -> ExactObservedNumericProposition:
    values = {
        "proposition_id": "proposition-001",
        "finding_id": "finding-001",
        "subject_id": "subject-001",
        "predicate_id": "predicate-001",
        "value": Decimal("123.45"),
        "unit_id": "USD",
        "effective_context_id": "context-001",
    }
    values.update(overrides)
    return ExactObservedNumericProposition(**values)


class StringSubclass(str):
    pass


class PropositionSubclass(ExactObservedNumericProposition):
    pass


class DecimalSubclass(Decimal):
    pass


class EvidencePropositionTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(ExactObservedNumericProposition)

        self.assertEqual(
            [field.name for field in model_fields],
            [
                "proposition_id",
                "finding_id",
                "subject_id",
                "predicate_id",
                "value",
                "unit_id",
                "effective_context_id",
            ],
        )
        self.assertEqual(
            get_type_hints(ExactObservedNumericProposition),
            {
                "proposition_id": str,
                "finding_id": str,
                "subject_id": str,
                "predicate_id": str,
                "value": Decimal,
                "unit_id": str,
                "effective_context_id": str,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)

    def test_model_is_frozen_and_hashable(self):
        proposition = make_proposition()

        with self.assertRaises(FrozenInstanceError):
            proposition.value = Decimal("1")

        self.assertIsInstance(hash(proposition), int)

    def test_model_preserves_exact_supplied_objects(self):
        identifiers = {
            "proposition_id": " proposition-001 ",
            "finding_id": " finding-001 ",
            "subject_id": " subject-001 ",
            "predicate_id": " predicate-001 ",
            "unit_id": " USD millions ",
            "effective_context_id": " context-001 ",
        }
        value = Decimal("1.2300")
        proposition = make_proposition(
            value=value,
            **identifiers,
        )

        for name, supplied in identifiers.items():
            self.assertIs(getattr(proposition, name), supplied)
        self.assertIs(proposition.value, value)
        self.assertEqual(proposition.value.as_tuple().exponent, -4)

    def test_valid_finite_decimal_forms_return_none(self):
        values = (
            Decimal("2"),
            Decimal("2.5"),
            Decimal("-2.5"),
            Decimal("0"),
            Decimal("-0"),
            Decimal("1E+12"),
            Decimal("1.2300"),
        )

        for value in values:
            with self.subTest(value=str(value)):
                proposition = make_proposition(value=value)
                self.assertIsNone(
                    validate_exact_observed_numeric_proposition(
                        proposition
                    )
                )
                self.assertIs(proposition.value, value)

    def test_surrounding_identifier_whitespace_is_preserved(self):
        values = {
            name: f" {name}-value "
            for name in IDENTIFIER_FIELDS
        }
        proposition = make_proposition(**values)

        self.assertIsNone(
            validate_exact_observed_numeric_proposition(proposition)
        )
        for name, supplied in values.items():
            self.assertIs(getattr(proposition, name), supplied)
            self.assertEqual(getattr(proposition, name), supplied)

    def test_decimal_numeric_equality_does_not_normalize_representation(self):
        one_decimal = Decimal("1.0")
        two_decimals = Decimal("1.00")
        first = make_proposition(value=one_decimal)
        second = make_proposition(value=two_decimals)

        self.assertEqual(one_decimal, two_decimals)
        self.assertIsNone(
            validate_exact_observed_numeric_proposition(first)
        )
        self.assertIsNone(
            validate_exact_observed_numeric_proposition(second)
        )
        self.assertIs(first.value, one_decimal)
        self.assertIs(second.value, two_decimals)
        self.assertEqual(first.value.as_tuple().exponent, -1)
        self.assertEqual(second.value.as_tuple().exponent, -2)

    def test_signed_zero_equality_preserves_sign(self):
        positive = Decimal("0")
        negative = Decimal("-0")
        first = make_proposition(value=positive)
        second = make_proposition(value=negative)

        self.assertEqual(positive, negative)
        self.assertIsNone(
            validate_exact_observed_numeric_proposition(first)
        )
        self.assertIsNone(
            validate_exact_observed_numeric_proposition(second)
        )
        self.assertEqual(first.value.as_tuple().sign, 0)
        self.assertEqual(second.value.as_tuple().sign, 1)

    def test_proposition_requires_exact_model_type(self):
        cases = (
            object(),
            PropositionSubclass(
                "proposition-001",
                "finding-001",
                "subject-001",
                "predicate-001",
                Decimal("1"),
                "USD",
                "context-001",
            ),
        )

        for value in cases:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^proposition must be "
                    "ExactObservedNumericProposition$",
                ):
                    validate_exact_observed_numeric_proposition(value)

    def test_identifier_fields_require_exact_string_type(self):
        invalid_values = (None, 1, StringSubclass("value"))

        for field_name in IDENTIFIER_FIELDS:
            for value in invalid_values:
                with self.subTest(
                    field=field_name,
                    value_type=type(value),
                ):
                    with self.assertRaisesRegex(
                        TypeError,
                        f"^{field_name} must be str$",
                    ):
                        validate_exact_observed_numeric_proposition(
                            make_proposition(
                                **{field_name: value}
                            )
                        )

    def test_identifier_fields_reject_blank_values(self):
        for field_name in IDENTIFIER_FIELDS:
            for value in ("", " ", "\t", "\n", "\t\n "):
                with self.subTest(
                    field=field_name,
                    value=repr(value),
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        f"^{field_name} must not be blank$",
                    ):
                        validate_exact_observed_numeric_proposition(
                            make_proposition(
                                **{field_name: value}
                            )
                        )

    def test_value_requires_exact_decimal_type(self):
        invalid_values = (
            1,
            1.0,
            "1.0",
            None,
            DecimalSubclass("1.0"),
        )

        for value in invalid_values:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^value must be Decimal$",
                ):
                    validate_exact_observed_numeric_proposition(
                        make_proposition(value=value)
                    )

    def test_non_finite_decimal_values_are_rejected(self):
        for value in (
            Decimal("NaN"),
            Decimal("sNaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        ):
            with self.subTest(value=str(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^value must be finite$",
                ):
                    validate_exact_observed_numeric_proposition(
                        make_proposition(value=value)
                    )

    def test_validation_stops_at_first_invalid_field(self):
        cases = (
            (
                {
                    "proposition_id": None,
                    "finding_id": None,
                },
                TypeError,
                "proposition_id must be str",
            ),
            (
                {
                    "predicate_id": "",
                    "value": 1,
                    "unit_id": None,
                },
                ValueError,
                "predicate_id must not be blank",
            ),
            (
                {
                    "value": Decimal("NaN"),
                    "unit_id": None,
                },
                ValueError,
                "value must be finite",
            ),
            (
                {
                    "unit_id": "",
                    "effective_context_id": None,
                },
                ValueError,
                "unit_id must not be blank",
            ),
        )

        for overrides, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_exact_observed_numeric_proposition(
                        make_proposition(**overrides)
                    )

    def test_production_import_and_feature_boundaries(self):
        package_root = Path(__file__).resolve().parents[1]
        model_source = (package_root / "models.py").read_text()
        validation_source = (
            package_root / "validation.py"
        ).read_text()

        model_imports = self._import_roots(model_source)
        validation_imports = self._import_roots(
            validation_source
        )
        self.assertEqual(model_imports, {"dataclasses", "decimal"})
        self.assertEqual(
            validation_imports,
            {"decimal", "EvidenceProposition"},
        )

        combined = model_source + validation_source
        forbidden = (
            "ResearchDomain",
            "AIAdapter",
            "ExecutionEngine",
            "provider",
            "compare",
            "compatib",
            "contradict",
            "convert",
            "quantize",
            "normalize",
            "parse",
            "registry",
        )
        for value in forbidden:
            with self.subTest(value=value):
                self.assertNotIn(value, combined)

    @staticmethod
    def _import_roots(source):
        roots = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                roots.update(
                    alias.name.split(".", 1)[0]
                    for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom):
                roots.add(node.module.split(".", 1)[0])
        return roots


if __name__ == "__main__":
    unittest.main()
