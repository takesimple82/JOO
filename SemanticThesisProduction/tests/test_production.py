import unittest
from dataclasses import FrozenInstanceError, fields
from typing import get_type_hints
from unittest.mock import patch

from ExplicitThesis.models import ExplicitThesis
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)
from SemanticThesisProduction.validation import (
    validate_semantically_produced_thesis,
)


def make_thesis():
    return ExplicitThesis(
        "thesis-001",
        "A caller-supplied thesis statement.",
    )


class ProductionSubclass(SemanticallyProducedThesis):
    pass


class ThesisSubclass(ExplicitThesis):
    pass


class SemanticThesisProductionTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            [
                field.name
                for field in fields(
                    SemanticallyProducedThesis
                )
            ],
            ["thesis"],
        )
        self.assertEqual(
            get_type_hints(SemanticallyProducedThesis),
            {"thesis": ExplicitThesis},
        )

    def test_frozen_hashable_structural_equality(self):
        thesis = make_thesis()
        first = SemanticallyProducedThesis(thesis)
        second = SemanticallyProducedThesis(thesis)
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        with self.assertRaises(FrozenInstanceError):
            first.thesis = make_thesis()

    def test_success_returns_none(self):
        self.assertIsNone(
            validate_semantically_produced_thesis(
                SemanticallyProducedThesis(make_thesis())
            )
        )

    def test_exact_wrapper_type(self):
        thesis = make_thesis()
        for value in (
            None,
            thesis,
            ProductionSubclass(thesis),
        ):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^production must be "
                    "SemanticallyProducedThesis$",
                ):
                    validate_semantically_produced_thesis(
                        value
                    )

    def test_exact_thesis_type(self):
        subclass = ThesisSubclass(
            "thesis-001",
            "statement",
        )
        for value in (None, object(), subclass):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^thesis must be ExplicitThesis$",
                ):
                    validate_semantically_produced_thesis(
                        SemanticallyProducedThesis(value)
                    )

    def test_upstream_validator_once_and_original(self):
        thesis = make_thesis()
        production = SemanticallyProducedThesis(thesis)
        with patch(
            "SemanticThesisProduction.validation"
            ".validate_explicit_thesis",
        ) as validator:
            result = validate_semantically_produced_thesis(
                production
            )
        self.assertIsNone(result)
        validator.assert_called_once_with(thesis)
        self.assertIs(
            validator.call_args.args[0],
            thesis,
        )

    def test_upstream_exception_identity(self):
        error = ValueError("thesis failure")
        with patch(
            "SemanticThesisProduction.validation"
            ".validate_explicit_thesis",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                validate_semantically_produced_thesis(
                    SemanticallyProducedThesis(
                        make_thesis()
                    )
                )
        self.assertIs(context.exception, error)

    def test_object_and_field_identity_preserved(self):
        thesis_id = " thesis-\u00e9 "
        statement = " statement-e\u0301 "
        thesis = ExplicitThesis(thesis_id, statement)
        production = SemanticallyProducedThesis(thesis)
        validate_semantically_produced_thesis(production)
        self.assertIs(production.thesis, thesis)
        self.assertIs(thesis.thesis_id, thesis_id)
        self.assertIs(thesis.statement, statement)

    def test_attestation_does_not_prove_semantics(self):
        self.assertIsNone(
            validate_semantically_produced_thesis(
                SemanticallyProducedThesis(
                    ExplicitThesis(
                        "thesis-001",
                        "not proven investment-valid",
                    )
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
