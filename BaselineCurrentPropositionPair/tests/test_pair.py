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

from BaselineCurrentPropositionPair.models import (
    ExplicitBaselineCurrentPropositionPair,
)
from BaselineCurrentPropositionPair.validation import (
    validate_explicit_baseline_current_proposition_pair,
)


def make_pair(
    **overrides,
) -> ExplicitBaselineCurrentPropositionPair:
    values = {
        "baseline_proposition_id": "proposition-baseline",
        "current_proposition_id": "proposition-current",
    }
    values.update(overrides)
    return ExplicitBaselineCurrentPropositionPair(**values)


class StringSubclass(str):
    pass


class PairSubclass(ExplicitBaselineCurrentPropositionPair):
    pass


class BaselineCurrentPropositionPairTests(
    unittest.TestCase
):
    def test_exact_model_contract(self):
        self.assertEqual(
            ExplicitBaselineCurrentPropositionPair.__name__,
            "ExplicitBaselineCurrentPropositionPair",
        )
        self.assertTrue(
            is_dataclass(
                ExplicitBaselineCurrentPropositionPair
            )
        )
        self.assertTrue(
            ExplicitBaselineCurrentPropositionPair
            .__dataclass_params__.frozen
        )

        model_fields = fields(
            ExplicitBaselineCurrentPropositionPair
        )

        self.assertEqual(
            [field.name for field in model_fields],
            [
                "baseline_proposition_id",
                "current_proposition_id",
            ],
        )
        self.assertEqual(
            get_type_hints(
                ExplicitBaselineCurrentPropositionPair
            ),
            {
                "baseline_proposition_id": str,
                "current_proposition_id": str,
            },
        )
        self.assertEqual(len(model_fields), 2)
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitBaselineCurrentPropositionPair.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitBaselineCurrentPropositionPair.__dict__,
        )

        public_methods = {
            name
            for name, value in
            ExplicitBaselineCurrentPropositionPair
            .__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_model_is_frozen_hashable_and_directional(self):
        forward = make_pair()
        same = make_pair()
        reverse = ExplicitBaselineCurrentPropositionPair(
            "proposition-current",
            "proposition-baseline",
        )

        self.assertEqual(forward, same)
        self.assertNotEqual(forward, reverse)
        self.assertEqual(hash(forward), hash(same))
        self.assertIsInstance(hash(forward), int)

        with self.assertRaises(FrozenInstanceError):
            forward.baseline_proposition_id = "replacement"
        with self.assertRaises(FrozenInstanceError):
            forward.current_proposition_id = "replacement"

    def test_unknown_constructor_field_fails_naturally(self):
        with self.assertRaises(TypeError):
            ExplicitBaselineCurrentPropositionPair(
                baseline_proposition_id="proposition-baseline",
                current_proposition_id="proposition-current",
                pair_id="pair-001",
            )

    def test_validator_requires_exact_pair_type_first(self):
        invalid = (object(), None, {}, ())

        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^pair must be "
                    "ExplicitBaselineCurrentPropositionPair$",
                ):
                    validate_explicit_baseline_current_proposition_pair(
                        value
                    )

        with self.assertRaisesRegex(
            TypeError,
            "^pair must be "
            "ExplicitBaselineCurrentPropositionPair$",
        ):
            validate_explicit_baseline_current_proposition_pair(
                PairSubclass(
                    "proposition-baseline",
                    "proposition-current",
                )
            )

    def test_baseline_id_requires_exact_built_in_string(self):
        invalid = (
            None,
            1,
            b"proposition-baseline",
            StringSubclass("proposition-baseline"),
        )

        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^baseline_proposition_id must be str$",
                ):
                    validate_explicit_baseline_current_proposition_pair(
                        make_pair(
                            baseline_proposition_id=value
                        )
                    )

    def test_baseline_id_rejects_blank_values(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^baseline_proposition_id must not be blank$",
                ):
                    validate_explicit_baseline_current_proposition_pair(
                        make_pair(
                            baseline_proposition_id=value
                        )
                    )

    def test_current_id_requires_exact_built_in_string(self):
        invalid = (
            None,
            1,
            b"proposition-current",
            StringSubclass("proposition-current"),
        )

        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^current_proposition_id must be str$",
                ):
                    validate_explicit_baseline_current_proposition_pair(
                        make_pair(
                            current_proposition_id=value
                        )
                    )

    def test_current_id_rejects_blank_values(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^current_proposition_id must not be blank$",
                ):
                    validate_explicit_baseline_current_proposition_pair(
                        make_pair(
                            current_proposition_id=value
                        )
                    )

    def test_validation_order_is_deterministic(self):
        cases = (
            (
                make_pair(
                    baseline_proposition_id=None,
                    current_proposition_id=None,
                ),
                TypeError,
                "baseline_proposition_id must be str",
            ),
            (
                make_pair(
                    baseline_proposition_id=" ",
                    current_proposition_id=None,
                ),
                ValueError,
                "baseline_proposition_id must not be blank",
            ),
            (
                make_pair(current_proposition_id=None),
                TypeError,
                "current_proposition_id must be str",
            ),
            (
                make_pair(current_proposition_id=" "),
                ValueError,
                "current_proposition_id must not be blank",
            ),
        )

        for pair, exception, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    exception,
                    f"^{message}$",
                ):
                    validate_explicit_baseline_current_proposition_pair(
                        pair
                    )

    def test_same_proposition_id_is_rejected_last(self):
        pair = make_pair(
            baseline_proposition_id="same-proposition",
            current_proposition_id="same-proposition",
        )

        with self.assertRaisesRegex(
            ValueError,
            "^current_proposition_id must differ from "
            "baseline_proposition_id$",
        ):
            validate_explicit_baseline_current_proposition_pair(
                pair
            )

    def test_role_conflict_uses_exact_identifier_equality(self):
        distinct_pairs = (
            ("value", "VALUE"),
            ("value", " value "),
            ("\u00e9", "e\u0301"),
        )

        for baseline_id, current_id in distinct_pairs:
            with self.subTest(
                baseline_id=repr(baseline_id),
                current_id=repr(current_id),
            ):
                self.assertIsNone(
                    validate_explicit_baseline_current_proposition_pair(
                        ExplicitBaselineCurrentPropositionPair(
                            baseline_id,
                            current_id,
                        )
                    )
                )

    def test_success_preserves_pair_and_field_objects(self):
        baseline_id = " baseline-\u00e9 "
        current_id = " current-e\u0301 "
        pair = ExplicitBaselineCurrentPropositionPair(
            baseline_id,
            current_id,
        )
        original_pair_id = id(pair)

        result = (
            validate_explicit_baseline_current_proposition_pair(
                pair
            )
        )

        self.assertIsNone(result)
        self.assertEqual(id(pair), original_pair_id)
        self.assertIs(
            pair.baseline_proposition_id,
            baseline_id,
        )
        self.assertIs(
            pair.current_proposition_id,
            current_id,
        )

    def test_duplicate_pairs_and_shared_endpoints_are_allowed(self):
        pairs = (
            make_pair(),
            make_pair(),
            make_pair(
                current_proposition_id="proposition-other"
            ),
            make_pair(
                baseline_proposition_id="proposition-other"
            ),
        )

        for pair in pairs:
            self.assertIsNone(
                validate_explicit_baseline_current_proposition_pair(
                    pair
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

        validation_imports = [
            node
            for node in ast.walk(validation_tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        self.assertEqual(len(validation_imports), 1)
        self.assertEqual(
            validation_imports[0].module,
            "BaselineCurrentPropositionPair.models",
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
                "validate_explicit_baseline_current_proposition_pair"
            ],
        )
        self.assertFalse(
            any(
                isinstance(node, (ast.For, ast.While))
                for node in ast.walk(validation_tree)
            )
        )


if __name__ == "__main__":
    unittest.main()
