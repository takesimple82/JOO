import ast
import unittest
from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from ExactCrossContextNumericDelta.models import (
    ExactCrossContextNumericDelta,
)
from ExactCrossContextNumericDeltaDirection.models import (
    ExactCrossContextNumericDeltaDirectionStatus,
)
from ExactNumericDeltaMateriality.models import (
    ExactNumericDeltaMaterialityPolicy,
    ExactNumericDeltaMaterialityStatus,
)
from ExactNumericDeltaSignal.models import (
    ExactNumericDeltaSignalClassification,
    ExactNumericDeltaSignalStatus,
)
from ExplicitHypothesis.models import ExplicitHypothesis
from NumericSignalHypothesisLink.models import (
    ExplicitNumericSignalHypothesisLink,
)
from NumericSignalHypothesisLink.validation import (
    validate_explicit_numeric_signal_hypothesis_link,
)
from SemanticHypothesisProduction.models import (
    SemanticallyProducedHypothesis,
)


def make_signal(**overrides):
    values = {
        "delta": ExactCrossContextNumericDelta(
            "proposition-baseline",
            "proposition-current",
            "USD",
            Decimal("2"),
        ),
        "policy": ExactNumericDeltaMaterialityPolicy(
            "USD",
            Decimal("1"),
        ),
        "direction_status": (
            ExactCrossContextNumericDeltaDirectionStatus.POSITIVE
        ),
        "materiality_status": (
            ExactNumericDeltaMaterialityStatus.MATERIAL
        ),
        "signal_status": (
            ExactNumericDeltaSignalStatus.MATERIAL_INCREASE
        ),
    }
    values.update(overrides)
    return ExactNumericDeltaSignalClassification(**values)


def make_hypothesis(identifier="hypothesis-001"):
    return SemanticallyProducedHypothesis(
        ExplicitHypothesis(
            identifier,
            "A caller-supplied statement.",
        )
    )


class LinkSubclass(ExplicitNumericSignalHypothesisLink):
    pass


class SignalSubclass(ExactNumericDeltaSignalClassification):
    pass


class HypothesisSubclass(SemanticallyProducedHypothesis):
    pass


class NumericSignalHypothesisLinkTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            [
                field.name
                for field in fields(
                    ExplicitNumericSignalHypothesisLink
                )
            ],
            ["signal", "hypothesis"],
        )
        self.assertEqual(
            get_type_hints(
                ExplicitNumericSignalHypothesisLink
            ),
            {
                "signal": ExactNumericDeltaSignalClassification,
                "hypothesis": SemanticallyProducedHypothesis,
            },
        )

    def test_frozen_hashable_structural_equality(self):
        signal = make_signal()
        hypothesis = make_hypothesis()
        first = ExplicitNumericSignalHypothesisLink(
            signal,
            hypothesis,
        )
        second = ExplicitNumericSignalHypothesisLink(
            signal,
            hypothesis,
        )
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        with self.assertRaises(FrozenInstanceError):
            first.signal = make_signal()

    def test_success_returns_none(self):
        self.assertIsNone(
            validate_explicit_numeric_signal_hypothesis_link(
                ExplicitNumericSignalHypothesisLink(
                    make_signal(),
                    make_hypothesis(),
                )
            )
        )

    def test_exact_link_type(self):
        value = LinkSubclass(
            make_signal(),
            make_hypothesis(),
        )
        with self.assertRaisesRegex(
            TypeError,
            "^link must be "
            "ExplicitNumericSignalHypothesisLink$",
        ):
            validate_explicit_numeric_signal_hypothesis_link(
                value
            )

    def test_exact_signal_type(self):
        signal = make_signal()
        subclass = SignalSubclass(
            signal.delta,
            signal.policy,
            signal.direction_status,
            signal.materiality_status,
            signal.signal_status,
        )
        for value in (None, object(), subclass):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^signal must be "
                    "ExactNumericDeltaSignalClassification$",
                ):
                    validate_explicit_numeric_signal_hypothesis_link(
                        ExplicitNumericSignalHypothesisLink(
                            value,
                            make_hypothesis(),
                        )
                    )

    def test_exact_semantic_hypothesis_type(self):
        hypothesis = make_hypothesis()
        subclass = HypothesisSubclass(
            hypothesis.hypothesis
        )
        for value in (None, object(), subclass):
            with self.subTest(value=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^hypothesis must be "
                    "SemanticallyProducedHypothesis$",
                ):
                    validate_explicit_numeric_signal_hypothesis_link(
                        ExplicitNumericSignalHypothesisLink(
                            make_signal(),
                            value,
                        )
                    )

    def test_upstream_hypothesis_validator_once(self):
        hypothesis = make_hypothesis()
        link = ExplicitNumericSignalHypothesisLink(
            make_signal(),
            hypothesis,
        )
        with patch(
            "NumericSignalHypothesisLink.validation"
            ".validate_semantically_produced_hypothesis",
        ) as validator:
            result = (
                validate_explicit_numeric_signal_hypothesis_link(
                    link
                )
            )
        self.assertIsNone(result)
        validator.assert_called_once_with(hypothesis)
        self.assertIs(
            validator.call_args.args[0],
            hypothesis,
        )

    def test_upstream_exception_identity(self):
        error = ValueError("hypothesis failure")
        with patch(
            "NumericSignalHypothesisLink.validation"
            ".validate_semantically_produced_hypothesis",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                validate_explicit_numeric_signal_hypothesis_link(
                    ExplicitNumericSignalHypothesisLink(
                        make_signal(),
                        make_hypothesis(),
                    )
                )
        self.assertIs(context.exception, error)

    def test_many_to_many_and_duplicates_are_allowed(self):
        signal_a = make_signal()
        signal_b = make_signal(
            signal_status=(
                ExactNumericDeltaSignalStatus.NO_CHANGE
            )
        )
        hypothesis_a = make_hypothesis("hypothesis-a")
        hypothesis_b = make_hypothesis("hypothesis-b")
        links = (
            ExplicitNumericSignalHypothesisLink(
                signal_a,
                hypothesis_a,
            ),
            ExplicitNumericSignalHypothesisLink(
                signal_a,
                hypothesis_b,
            ),
            ExplicitNumericSignalHypothesisLink(
                signal_b,
                hypothesis_a,
            ),
            ExplicitNumericSignalHypothesisLink(
                signal_a,
                hypothesis_a,
            ),
        )
        for link in links:
            self.assertIsNone(
                validate_explicit_numeric_signal_hypothesis_link(
                    link
                )
            )
        self.assertEqual(links[0], links[3])

    def test_link_preserves_complete_objects(self):
        signal = make_signal()
        hypothesis = make_hypothesis()
        link = ExplicitNumericSignalHypothesisLink(
            signal,
            hypothesis,
        )
        validate_explicit_numeric_signal_hypothesis_link(
            link
        )
        self.assertIs(link.signal, signal)
        self.assertIs(link.hypothesis, hypothesis)
        self.assertIs(link.signal.delta, signal.delta)
        self.assertIs(link.signal.policy, signal.policy)

    def test_dependency_direction_and_no_identity_invention(self):
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
        self.assertIn(
            "ExactNumericDeltaSignal.models",
            imported_modules,
        )
        self.assertIn(
            "SemanticHypothesisProduction.models",
            imported_modules,
        )
        for forbidden in (
            "signal_id",
            "link_id",
            "hashlib",
            "registry",
            "lookup",
            "persistence",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
