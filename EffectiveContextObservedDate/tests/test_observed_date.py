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

from EffectiveContextObservedDate.models import (
    ExplicitEffectiveContextObservedDate,
)
from EffectiveContextObservedDate.validation import (
    validate_explicit_effective_context_observed_date,
)


def make_context_date(
    **overrides,
) -> ExplicitEffectiveContextObservedDate:
    values = {
        "effective_context_id": "context-001",
        "observed_on": "2026-07-30",
    }
    values.update(overrides)
    return ExplicitEffectiveContextObservedDate(**values)


class StringSubclass(str):
    pass


class ContextDateSubclass(
    ExplicitEffectiveContextObservedDate
):
    pass


class EffectiveContextObservedDateTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            ExplicitEffectiveContextObservedDate.__name__,
            "ExplicitEffectiveContextObservedDate",
        )
        self.assertTrue(
            is_dataclass(ExplicitEffectiveContextObservedDate)
        )
        self.assertTrue(
            ExplicitEffectiveContextObservedDate
            .__dataclass_params__.frozen
        )

        model_fields = fields(
            ExplicitEffectiveContextObservedDate
        )

        self.assertEqual(
            [field.name for field in model_fields],
            ["effective_context_id", "observed_on"],
        )
        self.assertEqual(
            get_type_hints(
                ExplicitEffectiveContextObservedDate
            ),
            {
                "effective_context_id": str,
                "observed_on": str,
            },
        )
        self.assertEqual(len(model_fields), 2)
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitEffectiveContextObservedDate.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitEffectiveContextObservedDate.__dict__,
        )

        public_methods = {
            name
            for name, value in
            ExplicitEffectiveContextObservedDate
            .__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_model_is_frozen_hashable_and_structurally_equal(self):
        first = make_context_date()
        same = make_context_date()
        different_context = make_context_date(
            effective_context_id="context-002"
        )
        different_date = make_context_date(
            observed_on="2026-07-31"
        )

        self.assertEqual(first, same)
        self.assertNotEqual(first, different_context)
        self.assertNotEqual(first, different_date)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)

        with self.assertRaises(FrozenInstanceError):
            first.effective_context_id = "replacement"
        with self.assertRaises(FrozenInstanceError):
            first.observed_on = "2026-08-01"

    def test_unknown_constructor_field_fails_naturally(self):
        with self.assertRaises(TypeError):
            ExplicitEffectiveContextObservedDate(
                effective_context_id="context-001",
                observed_on="2026-07-30",
                proposition_id="proposition-001",
            )

    def test_validator_requires_exact_model_type_first(self):
        invalid = (object(), None, {}, ())

        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^context_date must be "
                    "ExplicitEffectiveContextObservedDate$",
                ):
                    validate_explicit_effective_context_observed_date(
                        value
                    )

        with self.assertRaisesRegex(
            TypeError,
            "^context_date must be "
            "ExplicitEffectiveContextObservedDate$",
        ):
            validate_explicit_effective_context_observed_date(
                ContextDateSubclass(
                    "context-001",
                    "2026-07-30",
                )
            )

    def test_context_id_requires_exact_built_in_string(self):
        invalid = (
            None,
            1,
            b"context-001",
            StringSubclass("context-001"),
        )

        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^effective_context_id must be str$",
                ):
                    validate_explicit_effective_context_observed_date(
                        make_context_date(
                            effective_context_id=value
                        )
                    )

    def test_context_id_rejects_blank_values(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^effective_context_id must not be blank$",
                ):
                    validate_explicit_effective_context_observed_date(
                        make_context_date(
                            effective_context_id=value
                        )
                    )

    def test_observed_on_requires_exact_built_in_string(self):
        invalid = (
            None,
            20260730,
            b"2026-07-30",
            StringSubclass("2026-07-30"),
        )

        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^observed_on must be str$",
                ):
                    validate_explicit_effective_context_observed_date(
                        make_context_date(observed_on=value)
                    )

    def test_valid_strict_calendar_dates(self):
        for value in (
            "2024-02-29",
            "2026-01-01",
            "2026-12-31",
            "0001-01-01",
            "9999-12-31",
        ):
            with self.subTest(value=value):
                context_date = make_context_date(
                    observed_on=value
                )
                self.assertIsNone(
                    validate_explicit_effective_context_observed_date(
                        context_date
                    )
                )

    def test_invalid_date_formats_and_calendar_dates(self):
        invalid = (
            "",
            " ",
            "2026-7-30",
            "2026-07-3",
            "2026/07/30",
            " 2026-07-30",
            "2026-07-30 ",
            "２０２６-０７-３０",
            "2026-02-29",
            "2024-02-30",
            "2026-04-31",
            "0000-01-01",
            "10000-01-01",
        )

        for value in invalid:
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^observed_on must be a valid "
                    "YYYY-MM-DD date$",
                ):
                    validate_explicit_effective_context_observed_date(
                        make_context_date(observed_on=value)
                    )

    def test_validation_order_is_deterministic(self):
        cases = (
            (
                make_context_date(
                    effective_context_id=None,
                    observed_on=None,
                ),
                TypeError,
                "effective_context_id must be str",
            ),
            (
                make_context_date(
                    effective_context_id=" ",
                    observed_on=None,
                ),
                ValueError,
                "effective_context_id must not be blank",
            ),
            (
                make_context_date(observed_on=None),
                TypeError,
                "observed_on must be str",
            ),
            (
                make_context_date(observed_on="invalid"),
                ValueError,
                "observed_on must be a valid YYYY-MM-DD date",
            ),
        )

        for context_date, exception, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    exception,
                    f"^{message}$",
                ):
                    validate_explicit_effective_context_observed_date(
                        context_date
                    )

    def test_success_preserves_model_and_field_objects(self):
        effective_context_id = " context-\u00e9 "
        observed_on = "2026-07-30"
        context_date = ExplicitEffectiveContextObservedDate(
            effective_context_id,
            observed_on,
        )
        original_model_id = id(context_date)

        result = (
            validate_explicit_effective_context_observed_date(
                context_date
            )
        )

        self.assertIsNone(result)
        self.assertEqual(id(context_date), original_model_id)
        self.assertIs(
            context_date.effective_context_id,
            effective_context_id,
        )
        self.assertIs(context_date.observed_on, observed_on)

    def test_duplicate_and_conflicting_associations_are_not_checked(self):
        first = make_context_date()
        duplicate = make_context_date()
        conflicting = make_context_date(
            observed_on="2026-07-31"
        )

        for context_date in (
            first,
            duplicate,
            conflicting,
        ):
            self.assertIsNone(
                validate_explicit_effective_context_observed_date(
                    context_date
                )
            )

    def test_structural_scope_and_production_imports(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (root / "models.py").read_text()
        )
        validation_tree = ast.parse(
            (root / "validation.py").read_text()
        )

        model_imports = [
            node
            for node in ast.walk(model_tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        self.assertEqual(len(model_imports), 1)
        self.assertEqual(model_imports[0].module, "dataclasses")

        imported_modules = {
            node.module
            for node in ast.walk(validation_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            imported_modules,
            {
                "datetime",
                "EffectiveContextObservedDate.models",
            },
        )
        direct_imports = [
            node
            for node in ast.walk(validation_tree)
            if isinstance(node, ast.Import)
        ]
        self.assertEqual(
            [alias.name for node in direct_imports for alias in node.names],
            ["re"],
        )

        functions = [
            node
            for node in validation_tree.body
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            )
        ]
        self.assertEqual(
            [function.name for function in functions],
            [
                "validate_explicit_effective_context_observed_date",
                "_is_strict_date",
            ],
        )


if __name__ == "__main__":
    unittest.main()
