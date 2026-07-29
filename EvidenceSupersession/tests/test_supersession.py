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

from EvidenceSupersession.models import (
    ExplicitPropositionSupersession,
)
from EvidenceSupersession.validation import (
    validate_explicit_proposition_supersession,
)


def make_relation(**overrides) -> ExplicitPropositionSupersession:
    values = {
        "superseded_proposition_id": "proposition-a",
        "superseding_proposition_id": "proposition-b",
    }
    values.update(overrides)
    return ExplicitPropositionSupersession(**values)


class StringSubclass(str):
    pass


class RelationSubclass(ExplicitPropositionSupersession):
    pass


class EvidenceSupersessionTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            ExplicitPropositionSupersession.__name__,
            "ExplicitPropositionSupersession",
        )
        self.assertTrue(
            is_dataclass(ExplicitPropositionSupersession)
        )
        self.assertTrue(
            ExplicitPropositionSupersession
            .__dataclass_params__.frozen
        )
        model_fields = fields(ExplicitPropositionSupersession)
        self.assertEqual(
            [field.name for field in model_fields],
            [
                "superseded_proposition_id",
                "superseding_proposition_id",
            ],
        )
        self.assertEqual(
            get_type_hints(ExplicitPropositionSupersession),
            {
                "superseded_proposition_id": str,
                "superseding_proposition_id": str,
            },
        )
        self.assertEqual(len(model_fields), 2)
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitPropositionSupersession.__dict__,
        )
        public_methods = {
            name
            for name, value in
            ExplicitPropositionSupersession.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_model_equality_direction_hash_and_immutability(self):
        forward = make_relation()
        same = make_relation()
        reverse = ExplicitPropositionSupersession(
            "proposition-b",
            "proposition-a",
        )

        self.assertEqual(forward, same)
        self.assertNotEqual(forward, reverse)
        self.assertEqual(hash(forward), hash(same))
        self.assertIsInstance(hash(forward), int)
        with self.assertRaises(FrozenInstanceError):
            forward.superseded_proposition_id = "replacement"

    def test_unknown_constructor_field_fails_naturally(self):
        with self.assertRaises(TypeError):
            ExplicitPropositionSupersession(
                superseded_proposition_id="proposition-a",
                superseding_proposition_id="proposition-b",
                relation_id="relation-1",
            )

    def test_relation_requires_exact_type_before_field_access(self):
        invalid = (object(), None, {}, ())
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^relation must be "
                    "ExplicitPropositionSupersession$",
                ):
                    validate_explicit_proposition_supersession(
                        value
                    )

        subclass = RelationSubclass(
            "proposition-a",
            "proposition-b",
        )
        with self.assertRaisesRegex(
            TypeError,
            "^relation must be ExplicitPropositionSupersession$",
        ):
            validate_explicit_proposition_supersession(subclass)

    def test_superseded_identifier_requires_exact_string(self):
        invalid = (1, None, b"value", StringSubclass("value"))
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^superseded_proposition_id must be str$",
                ):
                    validate_explicit_proposition_supersession(
                        make_relation(
                            superseded_proposition_id=value
                        )
                    )

    def test_superseded_identifier_rejects_blank_values(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^superseded_proposition_id "
                    "must not be blank$",
                ):
                    validate_explicit_proposition_supersession(
                        make_relation(
                            superseded_proposition_id=value
                        )
                    )

    def test_superseding_identifier_requires_exact_string(self):
        invalid = (1, None, b"value", StringSubclass("value"))
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^superseding_proposition_id must be str$",
                ):
                    validate_explicit_proposition_supersession(
                        make_relation(
                            superseding_proposition_id=value
                        )
                    )

    def test_superseding_identifier_rejects_blank_values(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^superseding_proposition_id "
                    "must not be blank$",
                ):
                    validate_explicit_proposition_supersession(
                        make_relation(
                            superseding_proposition_id=value
                        )
                    )

    def test_validation_order_is_deterministic(self):
        cases = (
            (
                make_relation(
                    superseded_proposition_id=1,
                    superseding_proposition_id=None,
                ),
                TypeError,
                "superseded_proposition_id must be str",
            ),
            (
                make_relation(
                    superseded_proposition_id=" ",
                    superseding_proposition_id=None,
                ),
                ValueError,
                "superseded_proposition_id must not be blank",
            ),
            (
                make_relation(
                    superseded_proposition_id="valid",
                    superseding_proposition_id=1,
                ),
                TypeError,
                "superseding_proposition_id must be str",
            ),
            (
                make_relation(
                    superseded_proposition_id="valid",
                    superseding_proposition_id=" ",
                ),
                ValueError,
                "superseding_proposition_id must not be blank",
            ),
        )
        for relation, exception, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    exception,
                    f"^{message}$",
                ):
                    validate_explicit_proposition_supersession(
                        relation
                    )

    def test_exact_self_supersession_is_rejected_last(self):
        relation = make_relation(
            superseded_proposition_id="same",
            superseding_proposition_id="same",
        )
        with self.assertRaisesRegex(
            ValueError,
            "^superseding_proposition_id must differ from "
            "superseded_proposition_id$",
        ):
            validate_explicit_proposition_supersession(relation)

    def test_self_comparison_does_not_normalize_identifiers(self):
        valid_pairs = (
            ("value", "VALUE"),
            ("value", " value "),
            ("\u00e9", "e\u0301"),
        )
        for superseded, superseding in valid_pairs:
            with self.subTest(
                superseded=repr(superseded),
                superseding=repr(superseding),
            ):
                self.assertIsNone(
                    validate_explicit_proposition_supersession(
                        ExplicitPropositionSupersession(
                            superseded,
                            superseding,
                        )
                    )
                )

    def test_success_preserves_relation_and_identifier_objects(self):
        superseded = " proposition-\u00e9 "
        superseding = " PROPOSITION-e\u0301 "
        relation = ExplicitPropositionSupersession(
            superseded,
            superseding,
        )
        original_id = id(relation)

        result = validate_explicit_proposition_supersession(
            relation
        )

        self.assertIsNone(result)
        self.assertEqual(id(relation), original_id)
        self.assertIs(
            relation.superseded_proposition_id,
            superseded,
        )
        self.assertIs(
            relation.superseding_proposition_id,
            superseding,
        )
        self.assertEqual(
            relation.superseded_proposition_id,
            " proposition-\u00e9 ",
        )
        self.assertEqual(
            relation.superseding_proposition_id,
            " PROPOSITION-e\u0301 ",
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
            "EvidenceSupersession.models",
        )

        functions = [
            node
            for node in validation_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        self.assertEqual(
            [function.name for function in functions],
            ["validate_explicit_proposition_supersession"],
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

    def test_frozen_packages_have_no_reverse_dependency(self):
        root = Path(__file__).resolve().parents[2].parent
        evidence_packages = (
            "Validation",
            "Provenance",
            "Assessment",
            "Aggregation",
            "Proposition",
            "Comparison",
            "Contradiction",
        )
        frozen_packages = (
            "ResearchDomain",
            *(f"Evidence{name}" for name in evidence_packages),
        )
        for package_name in frozen_packages:
            for source_path in (
                root / package_name
            ).rglob("*.py"):
                tree = ast.parse(source_path.read_text())
                imported_modules = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported_modules.extend(
                            alias.name for alias in node.names
                        )
                    elif isinstance(node, ast.ImportFrom):
                        imported_modules.append(node.module or "")
                self.assertFalse(
                    any(
                        module == "EvidenceSupersession"
                        or module.startswith(
                            "EvidenceSupersession."
                        )
                        for module in imported_modules
                    ),
                    source_path,
                )


if __name__ == "__main__":
    unittest.main()
