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

from PortfolioDomain.models import PortfolioSubject
from PortfolioDomain.validation import validate_portfolio_subject


def make_subject(**overrides) -> PortfolioSubject:
    values = {
        "subject_id": "subject-001",
        "display_name": "Subject One",
    }
    values.update(overrides)
    return PortfolioSubject(**values)


class StringSubclass(str):
    pass


class PortfolioSubjectSubclass(PortfolioSubject):
    pass


class PortfolioSubjectTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            PortfolioSubject.__name__,
            "PortfolioSubject",
        )
        self.assertTrue(is_dataclass(PortfolioSubject))
        self.assertTrue(
            PortfolioSubject.__dataclass_params__.frozen
        )

        model_fields = fields(PortfolioSubject)

        self.assertEqual(
            [field.name for field in model_fields],
            ["subject_id", "display_name"],
        )
        self.assertEqual(
            get_type_hints(PortfolioSubject),
            {
                "subject_id": str,
                "display_name": str,
            },
        )
        self.assertEqual(len(model_fields), 2)
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            PortfolioSubject.__dict__,
        )
        self.assertNotIn("__slots__", PortfolioSubject.__dict__)

        public_methods = {
            name
            for name, value in PortfolioSubject.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_model_is_frozen_hashable_and_structurally_equal(self):
        first = make_subject()
        same = make_subject()
        different_id = make_subject(subject_id="subject-002")
        different_name = make_subject(display_name="Other")

        self.assertEqual(first, same)
        self.assertNotEqual(first, different_id)
        self.assertNotEqual(first, different_name)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)

        with self.assertRaises(FrozenInstanceError):
            first.subject_id = "replacement"
        with self.assertRaises(FrozenInstanceError):
            first.display_name = "Replacement"

    def test_unknown_constructor_field_fails_naturally(self):
        with self.assertRaises(TypeError):
            PortfolioSubject(
                subject_id="subject-001",
                display_name="Subject One",
                ticker="TICKER",
            )

    def test_validator_requires_exact_model_type_first(self):
        invalid = (object(), None, {}, ())

        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^subject must be PortfolioSubject$",
                ):
                    validate_portfolio_subject(value)

        with self.assertRaisesRegex(
            TypeError,
            "^subject must be PortfolioSubject$",
        ):
            validate_portfolio_subject(
                PortfolioSubjectSubclass(
                    "subject-001",
                    "Subject One",
                )
            )

    def test_subject_id_requires_exact_built_in_string(self):
        invalid = (
            None,
            1,
            b"subject-001",
            StringSubclass("subject-001"),
        )

        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^subject_id must be str$",
                ):
                    validate_portfolio_subject(
                        make_subject(subject_id=value)
                    )

    def test_subject_id_rejects_empty_and_whitespace_only(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^subject_id must not be blank$",
                ):
                    validate_portfolio_subject(
                        make_subject(subject_id=value)
                    )

    def test_display_name_requires_exact_built_in_string(self):
        invalid = (
            None,
            1,
            b"Subject One",
            StringSubclass("Subject One"),
        )

        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^display_name must be str$",
                ):
                    validate_portfolio_subject(
                        make_subject(display_name=value)
                    )

    def test_display_name_rejects_empty_and_whitespace_only(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^display_name must not be blank$",
                ):
                    validate_portfolio_subject(
                        make_subject(display_name=value)
                    )

    def test_validation_order_is_deterministic(self):
        cases = (
            (
                make_subject(
                    subject_id=None,
                    display_name=None,
                ),
                TypeError,
                "subject_id must be str",
            ),
            (
                make_subject(
                    subject_id=" ",
                    display_name=None,
                ),
                ValueError,
                "subject_id must not be blank",
            ),
            (
                make_subject(display_name=None),
                TypeError,
                "display_name must be str",
            ),
            (
                make_subject(display_name=" "),
                ValueError,
                "display_name must not be blank",
            ),
        )

        for subject, exception, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    exception,
                    f"^{message}$",
                ):
                    validate_portfolio_subject(subject)

    def test_success_preserves_model_and_field_object_identity(self):
        subject_id = " subject-\u00e9 "
        display_name = " Subject e\u0301 "
        subject = PortfolioSubject(subject_id, display_name)
        original_subject_id = id(subject)

        result = validate_portfolio_subject(subject)

        self.assertIsNone(result)
        self.assertEqual(id(subject), original_subject_id)
        self.assertIs(subject.subject_id, subject_id)
        self.assertIs(subject.display_name, display_name)
        self.assertEqual(subject.subject_id, " subject-\u00e9 ")
        self.assertEqual(subject.display_name, " Subject e\u0301 ")

    def test_equality_does_not_normalize_fields(self):
        distinct_pairs = (
            ("subject", "SUBJECT"),
            ("subject", " subject "),
            ("\u00e9", "e\u0301"),
        )

        for left, right in distinct_pairs:
            with self.subTest(left=repr(left), right=repr(right)):
                self.assertNotEqual(
                    PortfolioSubject(left, "Display"),
                    PortfolioSubject(right, "Display"),
                )
                self.assertNotEqual(
                    PortfolioSubject("subject", left),
                    PortfolioSubject("subject", right),
                )

    def test_duplicate_subject_id_is_not_checked(self):
        first = PortfolioSubject(
            "subject-001",
            "First Display Name",
        )
        second = PortfolioSubject(
            "subject-001",
            "Second Display Name",
        )

        self.assertIsNone(validate_portfolio_subject(first))
        self.assertIsNone(validate_portfolio_subject(second))
        self.assertNotEqual(first, second)

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
        self.assertIsInstance(model_imports[0], ast.ImportFrom)
        self.assertEqual(model_imports[0].module, "dataclasses")

        validation_imports = [
            node
            for node in ast.walk(validation_tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        self.assertEqual(len(validation_imports), 1)
        self.assertEqual(
            validation_imports[0].module,
            "PortfolioDomain.models",
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
            ["validate_portfolio_subject"],
        )
        self.assertFalse(
            any(
                isinstance(node, (ast.For, ast.While))
                for node in ast.walk(validation_tree)
            )
        )
        self.assertFalse(
            any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr not in {"strip"}
                for node in ast.walk(validation_tree)
            )
        )


if __name__ == "__main__":
    unittest.main()
