import ast
import unittest
from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from ExplicitHypothesis.models import ExplicitHypothesis
from SemanticHypothesisProduction.models import (
    SemanticallyProducedHypothesis,
)
from SemanticHypothesisProduction.validation import (
    validate_semantically_produced_hypothesis,
)


def make_hypothesis(**overrides):
    values = {
        "hypothesis_id": "hypothesis-001",
        "statement": "A caller-supplied statement.",
    }
    values.update(overrides)
    return ExplicitHypothesis(**values)


class ProductionSubclass(SemanticallyProducedHypothesis):
    pass


class HypothesisSubclass(ExplicitHypothesis):
    pass


class SemanticHypothesisProductionTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            [
                field.name
                for field in fields(
                    SemanticallyProducedHypothesis
                )
            ],
            ["hypothesis"],
        )
        self.assertEqual(
            get_type_hints(
                SemanticallyProducedHypothesis
            ),
            {"hypothesis": ExplicitHypothesis},
        )

    def test_frozen_hashable_structural_equality(self):
        hypothesis = make_hypothesis()
        first = SemanticallyProducedHypothesis(hypothesis)
        second = SemanticallyProducedHypothesis(hypothesis)
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        with self.assertRaises(FrozenInstanceError):
            first.hypothesis = make_hypothesis()

    def test_success_returns_none(self):
        self.assertIsNone(
            validate_semantically_produced_hypothesis(
                SemanticallyProducedHypothesis(
                    make_hypothesis()
                )
            )
        )

    def test_exact_wrapper_type_and_subclass_rejection(self):
        hypothesis = make_hypothesis()
        for value in (
            None,
            hypothesis,
            ProductionSubclass(hypothesis),
        ):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^production must be "
                    "SemanticallyProducedHypothesis$",
                ):
                    validate_semantically_produced_hypothesis(
                        value
                    )

    def test_exact_hypothesis_type_and_subclass_rejection(self):
        subclass = HypothesisSubclass(
            "hypothesis-001",
            "statement",
        )
        for value in (None, object(), subclass):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^hypothesis must be ExplicitHypothesis$",
                ):
                    validate_semantically_produced_hypothesis(
                        SemanticallyProducedHypothesis(value)
                    )

    def test_upstream_validator_called_once_with_original(self):
        hypothesis = make_hypothesis()
        production = SemanticallyProducedHypothesis(
            hypothesis
        )
        with patch(
            "SemanticHypothesisProduction.validation"
            ".validate_explicit_hypothesis",
        ) as validator:
            result = validate_semantically_produced_hypothesis(
                production
            )
        self.assertIsNone(result)
        validator.assert_called_once_with(hypothesis)
        self.assertIs(
            validator.call_args.args[0],
            hypothesis,
        )

    def test_upstream_exception_propagates_unchanged(self):
        error = ValueError("hypothesis failure")
        with patch(
            "SemanticHypothesisProduction.validation"
            ".validate_explicit_hypothesis",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                validate_semantically_produced_hypothesis(
                    SemanticallyProducedHypothesis(
                        make_hypothesis()
                    )
                )
        self.assertIs(context.exception, error)

    def test_wrong_field_stops_before_upstream_validation(self):
        with patch(
            "SemanticHypothesisProduction.validation"
            ".validate_explicit_hypothesis",
        ) as validator:
            with self.assertRaises(TypeError):
                validate_semantically_produced_hypothesis(
                    SemanticallyProducedHypothesis(None)
                )
        validator.assert_not_called()

    def test_object_and_field_identity_preserved(self):
        hypothesis_id = " hypothesis-\u00e9 "
        statement = " statement-e\u0301 "
        hypothesis = ExplicitHypothesis(
            hypothesis_id,
            statement,
        )
        production = SemanticallyProducedHypothesis(
            hypothesis
        )

        validate_semantically_produced_hypothesis(
            production
        )

        self.assertIs(production.hypothesis, hypothesis)
        self.assertIs(
            hypothesis.hypothesis_id,
            hypothesis_id,
        )
        self.assertIs(hypothesis.statement, statement)

    def test_attestation_does_not_add_semantic_proof(self):
        production = SemanticallyProducedHypothesis(
            make_hypothesis(
                statement="not proven testable or true"
            )
        )
        self.assertIsNone(
            validate_semantically_produced_hypothesis(
                production
            )
        )

    def test_dependency_direction_and_excluded_scope(self):
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
            {
                "dataclasses",
                "ExplicitHypothesis.models",
            },
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "ExplicitHypothesis.models",
                "ExplicitHypothesis.validation",
                "SemanticHypothesisProduction.models",
            },
        )
        source = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "Signal",
            "producer_id",
            "provenance",
            "confidence",
            "probability",
            "Thesis",
            "Portfolio",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
