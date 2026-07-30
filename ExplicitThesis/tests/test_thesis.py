import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import get_type_hints

from ExplicitThesis.models import ExplicitThesis
from ExplicitThesis.validation import validate_explicit_thesis


class ThesisSubclass(ExplicitThesis):
    pass


class StringSubclass(str):
    pass


def make_thesis(**overrides):
    values = {
        "thesis_id": "thesis-001",
        "statement": "A caller-supplied thesis statement.",
    }
    values.update(overrides)
    return ExplicitThesis(**values)


class ExplicitThesisTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(ExplicitThesis)
        self.assertEqual(
            [field.name for field in model_fields],
            ["thesis_id", "statement"],
        )
        self.assertEqual(
            get_type_hints(ExplicitThesis),
            {"thesis_id": str, "statement": str},
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertFalse(hasattr(ExplicitThesis, "__slots__"))

    def test_frozen_hashable_structural_equality(self):
        first = make_thesis()
        second = make_thesis()
        different = make_thesis(thesis_id="thesis-002")
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.statement = "replacement"

    def test_success_returns_none(self):
        self.assertIsNone(
            validate_explicit_thesis(make_thesis())
        )

    def test_exact_model_type(self):
        for value in (
            None,
            object(),
            ThesisSubclass("thesis-001", "statement"),
        ):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^thesis must be ExplicitThesis$",
                ):
                    validate_explicit_thesis(value)

    def test_thesis_id_exact_string_and_nonblank(self):
        for value in (
            None,
            1,
            StringSubclass("thesis-001"),
        ):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^thesis_id must be str$",
                ):
                    validate_explicit_thesis(
                        make_thesis(thesis_id=value)
                    )
        for value in ("", " ", "\t\n"):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^thesis_id must not be blank$",
                ):
                    validate_explicit_thesis(
                        make_thesis(thesis_id=value)
                    )

    def test_statement_exact_string_and_nonblank(self):
        for value in (
            None,
            1,
            StringSubclass("statement"),
        ):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^statement must be str$",
                ):
                    validate_explicit_thesis(
                        make_thesis(statement=value)
                    )
        for value in ("", " ", "\t\n"):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^statement must not be blank$",
                ):
                    validate_explicit_thesis(
                        make_thesis(statement=value)
                    )

    def test_validation_order(self):
        cases = (
            (
                make_thesis(thesis_id=None, statement=None),
                TypeError,
                "thesis_id must be str",
            ),
            (
                make_thesis(thesis_id=" ", statement=None),
                ValueError,
                "thesis_id must not be blank",
            ),
            (
                make_thesis(statement=None),
                TypeError,
                "statement must be str",
            ),
            (
                make_thesis(statement=" "),
                ValueError,
                "statement must not be blank",
            ),
        )
        for thesis, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_thesis(thesis)

    def test_identity_and_representation_preserved(self):
        thesis_id = " thesis-\u00e9 "
        statement = " statement-e\u0301 "
        thesis = ExplicitThesis(thesis_id, statement)
        validate_explicit_thesis(thesis)
        self.assertIs(thesis.thesis_id, thesis_id)
        self.assertIs(thesis.statement, statement)

    def test_nonblank_text_is_not_semantically_certified(self):
        for statement in (
            "not necessarily evidence-supported",
            "not necessarily portfolio relevant",
            "not necessarily an investment proposition",
        ):
            self.assertIsNone(
                validate_explicit_thesis(
                    make_thesis(statement=statement)
                )
            )

    def test_dependency_direction_and_scope(self):
        root = Path(__file__).resolve().parents[1]
        source = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            imported_modules,
            {"dataclasses", "ExplicitThesis.models"},
        )
        for forbidden in (
            "Signal",
            "Hypothesis",
            "Portfolio",
            "BUY",
            "HOLD",
            "SELL",
            "confidence",
            "conviction",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
