import ast
import unittest
from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from SemanticPropositionProduction.models import (
    SemanticallyProducedNumericProposition,
)
from SemanticPropositionProduction.validation import (
    validate_semantically_produced_numeric_proposition,
)


def make_proposition(**overrides):
    values = {
        "proposition_id": "proposition-001",
        "finding_id": "finding-001",
        "subject_id": "subject-001",
        "predicate_id": "predicate-001",
        "value": Decimal("1.00"),
        "unit_id": "USD",
        "effective_context_id": "context-001",
    }
    values.update(overrides)
    return ExactObservedNumericProposition(**values)


class ProductionSubclass(SemanticallyProducedNumericProposition):
    pass


class PropositionSubclass(ExactObservedNumericProposition):
    pass


class SemanticPropositionProductionTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(
            SemanticallyProducedNumericProposition
        )
        self.assertEqual(
            [field.name for field in model_fields],
            ["proposition"],
        )
        self.assertEqual(
            get_type_hints(
                SemanticallyProducedNumericProposition
            ),
            {
                "proposition": ExactObservedNumericProposition,
            },
        )
        self.assertTrue(
            all(
                field.default is field.default_factory
                for field in model_fields
            )
        )
        self.assertFalse(
            hasattr(
                SemanticallyProducedNumericProposition,
                "__slots__",
            )
        )

    def test_frozen_hashable_structural_equality(self):
        proposition = make_proposition()
        first = SemanticallyProducedNumericProposition(
            proposition
        )
        second = SemanticallyProducedNumericProposition(
            proposition
        )
        different = SemanticallyProducedNumericProposition(
            make_proposition(proposition_id="other")
        )

        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.proposition = different.proposition

    def test_validator_success_returns_none(self):
        self.assertIsNone(
            validate_semantically_produced_numeric_proposition(
                SemanticallyProducedNumericProposition(
                    make_proposition()
                )
            )
        )

    def test_exact_production_type_and_subclass_rejection(self):
        proposition = make_proposition()
        for value in (
            None,
            object(),
            proposition,
            ProductionSubclass(proposition),
        ):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^production must be "
                    "SemanticallyProducedNumericProposition$",
                ):
                    validate_semantically_produced_numeric_proposition(
                        value
                    )

    def test_exact_proposition_type_and_subclass_rejection(self):
        base = make_proposition()
        subclass = PropositionSubclass(
            base.proposition_id,
            base.finding_id,
            base.subject_id,
            base.predicate_id,
            base.value,
            base.unit_id,
            base.effective_context_id,
        )
        for value in (None, object(), subclass):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^proposition must be "
                    "ExactObservedNumericProposition$",
                ):
                    validate_semantically_produced_numeric_proposition(
                        SemanticallyProducedNumericProposition(
                            value
                        )
                    )

    def test_upstream_validator_called_once_with_original(self):
        proposition = make_proposition()
        production = SemanticallyProducedNumericProposition(
            proposition
        )
        with patch(
            "SemanticPropositionProduction.validation"
            ".validate_exact_observed_numeric_proposition",
        ) as validator:
            result = (
                validate_semantically_produced_numeric_proposition(
                    production
                )
            )

        self.assertIsNone(result)
        validator.assert_called_once_with(proposition)
        self.assertIs(
            validator.call_args.args[0],
            proposition,
        )

    def test_upstream_exception_propagates_unchanged(self):
        error = ValueError("upstream failure")
        with patch(
            "SemanticPropositionProduction.validation"
            ".validate_exact_observed_numeric_proposition",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                validate_semantically_produced_numeric_proposition(
                    SemanticallyProducedNumericProposition(
                        make_proposition()
                    )
                )
        self.assertIs(context.exception, error)

    def test_wrong_field_type_stops_before_upstream_validation(self):
        with patch(
            "SemanticPropositionProduction.validation"
            ".validate_exact_observed_numeric_proposition",
        ) as validator:
            with self.assertRaises(TypeError):
                validate_semantically_produced_numeric_proposition(
                    SemanticallyProducedNumericProposition(None)
                )
        validator.assert_not_called()

    def test_proposition_and_field_object_identity_preserved(self):
        proposition_id = " proposition-\u00e9 "
        finding_id = " finding-e\u0301 "
        subject_id = " subject-\u00e9 "
        predicate_id = " predicate-e\u0301 "
        value = Decimal("1.2300")
        unit_id = " USD "
        context_id = " context-\u00e9 "
        proposition = ExactObservedNumericProposition(
            proposition_id,
            finding_id,
            subject_id,
            predicate_id,
            value,
            unit_id,
            context_id,
        )
        production = SemanticallyProducedNumericProposition(
            proposition
        )

        validate_semantically_produced_numeric_proposition(
            production
        )

        self.assertIs(production.proposition, proposition)
        self.assertIs(proposition.proposition_id, proposition_id)
        self.assertIs(proposition.finding_id, finding_id)
        self.assertIs(proposition.subject_id, subject_id)
        self.assertIs(proposition.predicate_id, predicate_id)
        self.assertIs(proposition.value, value)
        self.assertIs(proposition.unit_id, unit_id)
        self.assertIs(
            proposition.effective_context_id,
            context_id,
        )

    def test_duplicate_wrappers_are_allowed(self):
        proposition = make_proposition()
        first = SemanticallyProducedNumericProposition(
            proposition
        )
        second = SemanticallyProducedNumericProposition(
            proposition
        )

        self.assertIsNone(
            validate_semantically_produced_numeric_proposition(
                first
            )
        )
        self.assertIsNone(
            validate_semantically_produced_numeric_proposition(
                second
            )
        )
        self.assertEqual(first, second)
        self.assertIs(first.proposition, second.proposition)

    def test_production_structure_and_dependency_direction(self):
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
                "EvidenceProposition.models",
            },
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "EvidenceProposition.models",
                "EvidenceProposition.validation",
                "SemanticPropositionProduction.models",
            },
        )
        repository_root = root.parent
        for path in (
            repository_root / "EvidenceProposition"
        ).glob("*.py"):
            self.assertNotIn(
                "SemanticPropositionProduction",
                path.read_text(),
            )


if __name__ == "__main__":
    unittest.main()
