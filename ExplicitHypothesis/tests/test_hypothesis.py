import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import get_type_hints

from ExplicitHypothesis.models import ExplicitHypothesis
from ExplicitHypothesis.validation import (
    validate_explicit_hypothesis,
)


class HypothesisSubclass(ExplicitHypothesis):
    pass


class StringSubclass(str):
    pass


def make_hypothesis(**overrides):
    values = {
        "hypothesis_id": "hypothesis-001",
        "statement": "A caller-supplied statement.",
    }
    values.update(overrides)
    return ExplicitHypothesis(**values)


class ExplicitHypothesisTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(ExplicitHypothesis)
        self.assertEqual(
            [field.name for field in model_fields],
            ["hypothesis_id", "statement"],
        )
        self.assertEqual(
            get_type_hints(ExplicitHypothesis),
            {
                "hypothesis_id": str,
                "statement": str,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertFalse(
            hasattr(ExplicitHypothesis, "__slots__")
        )

    def test_frozen_hashable_structural_equality(self):
        first = make_hypothesis()
        second = make_hypothesis()
        different = make_hypothesis(
            hypothesis_id="hypothesis-002"
        )

        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.statement = "replacement"

    def test_validator_success_returns_none(self):
        self.assertIsNone(
            validate_explicit_hypothesis(
                make_hypothesis()
            )
        )

    def test_exact_model_type_and_subclass_rejection(self):
        for value in (
            None,
            object(),
            {
                "hypothesis_id": "hypothesis-001",
                "statement": "statement",
            },
            HypothesisSubclass(
                "hypothesis-001",
                "statement",
            ),
        ):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^hypothesis must be ExplicitHypothesis$",
                ):
                    validate_explicit_hypothesis(value)

    def test_hypothesis_id_requires_exact_built_in_string(self):
        for value in (
            None,
            1,
            StringSubclass("hypothesis-001"),
        ):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^hypothesis_id must be str$",
                ):
                    validate_explicit_hypothesis(
                        make_hypothesis(hypothesis_id=value)
                    )

    def test_hypothesis_id_rejects_blank_values(self):
        for value in ("", " ", "\t\n"):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^hypothesis_id must not be blank$",
                ):
                    validate_explicit_hypothesis(
                        make_hypothesis(hypothesis_id=value)
                    )

    def test_statement_requires_exact_built_in_string(self):
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
                    validate_explicit_hypothesis(
                        make_hypothesis(statement=value)
                    )

    def test_statement_rejects_blank_values(self):
        for value in ("", " ", "\t\n"):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^statement must not be blank$",
                ):
                    validate_explicit_hypothesis(
                        make_hypothesis(statement=value)
                    )

    def test_validation_stops_in_exact_field_order(self):
        cases = (
            (
                make_hypothesis(
                    hypothesis_id=None,
                    statement=None,
                ),
                TypeError,
                "hypothesis_id must be str",
            ),
            (
                make_hypothesis(
                    hypothesis_id=" ",
                    statement=None,
                ),
                ValueError,
                "hypothesis_id must not be blank",
            ),
            (
                make_hypothesis(statement=None),
                TypeError,
                "statement must be str",
            ),
            (
                make_hypothesis(statement=" "),
                ValueError,
                "statement must not be blank",
            ),
        )
        for hypothesis, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_hypothesis(
                        hypothesis
                    )

    def test_surrounding_whitespace_and_unicode_preserved(self):
        hypothesis_id = " hypothesis-\u00e9 "
        statement = " statement-e\u0301 "
        hypothesis = ExplicitHypothesis(
            hypothesis_id,
            statement,
        )

        validate_explicit_hypothesis(hypothesis)

        self.assertIs(
            hypothesis.hypothesis_id,
            hypothesis_id,
        )
        self.assertIs(hypothesis.statement, statement)
        self.assertEqual(
            hypothesis.hypothesis_id,
            " hypothesis-\u00e9 ",
        )
        self.assertEqual(
            hypothesis.statement,
            " statement-e\u0301 ",
        )

    def test_nonblank_text_does_not_gain_semantic_validation(self):
        values = (
            "not necessarily testable",
            "not necessarily explanatory",
            "not necessarily causal",
            "not necessarily predictive",
            "not necessarily evidence-supported",
        )
        for statement in values:
            with self.subTest(statement=statement):
                self.assertIsNone(
                    validate_explicit_hypothesis(
                        make_hypothesis(
                            statement=statement
                        )
                    )
                )

    def test_structural_scope_and_dependency_direction(self):
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
            {"ExplicitHypothesis.models"},
        )
        production_source = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "Signal",
            "finding_id",
            "proposition_id",
            "subject_id",
            "predicate_id",
            "effective_context_id",
            "confidence",
            "probability",
            "Thesis",
            "Portfolio",
        ):
            self.assertNotIn(
                forbidden,
                production_source,
            )


if __name__ == "__main__":
    unittest.main()
