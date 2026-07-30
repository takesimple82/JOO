import unittest
from dataclasses import FrozenInstanceError, fields
from typing import get_type_hints
from unittest.mock import patch

from ExplicitHypothesis.models import ExplicitHypothesis
from ExplicitThesis.models import ExplicitThesis
from HypothesisThesisLink.models import (
    ExplicitHypothesisThesisLink,
)
from HypothesisThesisLink.validation import (
    validate_explicit_hypothesis_thesis_link,
)
from SemanticHypothesisProduction.models import (
    SemanticallyProducedHypothesis,
)
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)


def make_hypothesis(identifier="hypothesis-001"):
    return SemanticallyProducedHypothesis(
        ExplicitHypothesis(identifier, "hypothesis statement")
    )


def make_thesis(identifier="thesis-001"):
    return SemanticallyProducedThesis(
        ExplicitThesis(identifier, "thesis statement")
    )


class LinkSubclass(ExplicitHypothesisThesisLink):
    pass


class HypothesisThesisLinkTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            [
                field.name
                for field in fields(
                    ExplicitHypothesisThesisLink
                )
            ],
            ["hypothesis", "thesis"],
        )
        self.assertEqual(
            get_type_hints(ExplicitHypothesisThesisLink),
            {
                "hypothesis": SemanticallyProducedHypothesis,
                "thesis": SemanticallyProducedThesis,
            },
        )

    def test_frozen_hashable_structural_equality(self):
        hypothesis = make_hypothesis()
        thesis = make_thesis()
        first = ExplicitHypothesisThesisLink(
            hypothesis,
            thesis,
        )
        second = ExplicitHypothesisThesisLink(
            hypothesis,
            thesis,
        )
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        with self.assertRaises(FrozenInstanceError):
            first.thesis = make_thesis()

    def test_success_returns_none(self):
        self.assertIsNone(
            validate_explicit_hypothesis_thesis_link(
                ExplicitHypothesisThesisLink(
                    make_hypothesis(),
                    make_thesis(),
                )
            )
        )

    def test_exact_link_and_endpoint_types(self):
        hypothesis = make_hypothesis()
        thesis = make_thesis()
        with self.assertRaisesRegex(
            TypeError,
            "^link must be ExplicitHypothesisThesisLink$",
        ):
            validate_explicit_hypothesis_thesis_link(
                LinkSubclass(hypothesis, thesis)
            )
        with self.assertRaisesRegex(
            TypeError,
            "^hypothesis must be "
            "SemanticallyProducedHypothesis$",
        ):
            validate_explicit_hypothesis_thesis_link(
                ExplicitHypothesisThesisLink(None, thesis)
            )
        with self.assertRaisesRegex(
            TypeError,
            "^thesis must be SemanticallyProducedThesis$",
        ):
            validate_explicit_hypothesis_thesis_link(
                ExplicitHypothesisThesisLink(
                    hypothesis,
                    None,
                )
            )

    def test_upstream_validation_order_once(self):
        hypothesis = make_hypothesis()
        thesis = make_thesis()
        calls = []
        with patch(
            "HypothesisThesisLink.validation"
            ".validate_semantically_produced_hypothesis",
            side_effect=lambda value: calls.append(
                ("hypothesis", value)
            ),
        ) as hypothesis_validator, patch(
            "HypothesisThesisLink.validation"
            ".validate_semantically_produced_thesis",
            side_effect=lambda value: calls.append(
                ("thesis", value)
            ),
        ) as thesis_validator:
            result = validate_explicit_hypothesis_thesis_link(
                ExplicitHypothesisThesisLink(
                    hypothesis,
                    thesis,
                )
            )
        self.assertIsNone(result)
        self.assertEqual(
            calls,
            [
                ("hypothesis", hypothesis),
                ("thesis", thesis),
            ],
        )
        hypothesis_validator.assert_called_once_with(
            hypothesis
        )
        thesis_validator.assert_called_once_with(thesis)

    def test_first_upstream_failure_stops_thesis(self):
        error = ValueError("hypothesis failure")
        with patch(
            "HypothesisThesisLink.validation"
            ".validate_semantically_produced_hypothesis",
            side_effect=error,
        ), patch(
            "HypothesisThesisLink.validation"
            ".validate_semantically_produced_thesis",
        ) as thesis_validator:
            with self.assertRaises(ValueError) as context:
                validate_explicit_hypothesis_thesis_link(
                    ExplicitHypothesisThesisLink(
                        make_hypothesis(),
                        make_thesis(),
                    )
                )
        self.assertIs(context.exception, error)
        thesis_validator.assert_not_called()

    def test_thesis_exception_identity(self):
        error = TypeError("thesis failure")
        with patch(
            "HypothesisThesisLink.validation"
            ".validate_semantically_produced_thesis",
            side_effect=error,
        ):
            with self.assertRaises(TypeError) as context:
                validate_explicit_hypothesis_thesis_link(
                    ExplicitHypothesisThesisLink(
                        make_hypothesis(),
                        make_thesis(),
                    )
                )
        self.assertIs(context.exception, error)

    def test_many_to_many_duplicates_and_identity(self):
        hypothesis_a = make_hypothesis("hypothesis-a")
        hypothesis_b = make_hypothesis("hypothesis-b")
        thesis_a = make_thesis("thesis-a")
        thesis_b = make_thesis("thesis-b")
        links = (
            ExplicitHypothesisThesisLink(
                hypothesis_a,
                thesis_a,
            ),
            ExplicitHypothesisThesisLink(
                hypothesis_a,
                thesis_b,
            ),
            ExplicitHypothesisThesisLink(
                hypothesis_b,
                thesis_a,
            ),
            ExplicitHypothesisThesisLink(
                hypothesis_a,
                thesis_a,
            ),
        )
        for link in links:
            self.assertIsNone(
                validate_explicit_hypothesis_thesis_link(
                    link
                )
            )
        self.assertEqual(links[0], links[3])
        self.assertIs(links[0].hypothesis, hypothesis_a)
        self.assertIs(links[0].thesis, thesis_a)


if __name__ == "__main__":
    unittest.main()
