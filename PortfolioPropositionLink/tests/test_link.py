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

from PortfolioPropositionLink.models import (
    ExplicitPropositionPortfolioSubjectLink,
)
from PortfolioPropositionLink.validation import (
    validate_explicit_proposition_portfolio_subject_link,
)


def make_link(
    **overrides,
) -> ExplicitPropositionPortfolioSubjectLink:
    values = {
        "proposition_id": "proposition-001",
        "portfolio_subject_id": "subject-001",
    }
    values.update(overrides)
    return ExplicitPropositionPortfolioSubjectLink(**values)


class StringSubclass(str):
    pass


class LinkSubclass(ExplicitPropositionPortfolioSubjectLink):
    pass


class PortfolioPropositionLinkTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            ExplicitPropositionPortfolioSubjectLink.__name__,
            "ExplicitPropositionPortfolioSubjectLink",
        )
        self.assertTrue(
            is_dataclass(
                ExplicitPropositionPortfolioSubjectLink
            )
        )
        self.assertTrue(
            ExplicitPropositionPortfolioSubjectLink
            .__dataclass_params__.frozen
        )

        model_fields = fields(
            ExplicitPropositionPortfolioSubjectLink
        )

        self.assertEqual(
            [field.name for field in model_fields],
            ["proposition_id", "portfolio_subject_id"],
        )
        self.assertEqual(
            get_type_hints(
                ExplicitPropositionPortfolioSubjectLink
            ),
            {
                "proposition_id": str,
                "portfolio_subject_id": str,
            },
        )
        self.assertEqual(len(model_fields), 2)
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitPropositionPortfolioSubjectLink.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitPropositionPortfolioSubjectLink.__dict__,
        )

        public_methods = {
            name
            for name, value in
            ExplicitPropositionPortfolioSubjectLink
            .__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_model_is_frozen_hashable_and_structurally_equal(self):
        first = make_link()
        same = make_link()
        different_proposition = make_link(
            proposition_id="proposition-002"
        )
        different_subject = make_link(
            portfolio_subject_id="subject-002"
        )

        self.assertEqual(first, same)
        self.assertNotEqual(first, different_proposition)
        self.assertNotEqual(first, different_subject)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)

        with self.assertRaises(FrozenInstanceError):
            first.proposition_id = "replacement"
        with self.assertRaises(FrozenInstanceError):
            first.portfolio_subject_id = "replacement"

    def test_unknown_constructor_field_fails_naturally(self):
        with self.assertRaises(TypeError):
            ExplicitPropositionPortfolioSubjectLink(
                proposition_id="proposition-001",
                portfolio_subject_id="subject-001",
                finding_id="finding-001",
            )

    def test_validator_requires_exact_link_type_first(self):
        invalid = (object(), None, {}, ())

        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^link must be "
                    "ExplicitPropositionPortfolioSubjectLink$",
                ):
                    validate_explicit_proposition_portfolio_subject_link(
                        value
                    )

        with self.assertRaisesRegex(
            TypeError,
            "^link must be "
            "ExplicitPropositionPortfolioSubjectLink$",
        ):
            validate_explicit_proposition_portfolio_subject_link(
                LinkSubclass(
                    "proposition-001",
                    "subject-001",
                )
            )

    def test_proposition_id_requires_exact_built_in_string(self):
        invalid = (
            None,
            1,
            b"proposition-001",
            StringSubclass("proposition-001"),
        )

        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^proposition_id must be str$",
                ):
                    validate_explicit_proposition_portfolio_subject_link(
                        make_link(proposition_id=value)
                    )

    def test_proposition_id_rejects_blank_values(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^proposition_id must not be blank$",
                ):
                    validate_explicit_proposition_portfolio_subject_link(
                        make_link(proposition_id=value)
                    )

    def test_portfolio_subject_id_requires_exact_built_in_string(self):
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
                    "^portfolio_subject_id must be str$",
                ):
                    validate_explicit_proposition_portfolio_subject_link(
                        make_link(portfolio_subject_id=value)
                    )

    def test_portfolio_subject_id_rejects_blank_values(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^portfolio_subject_id must not be blank$",
                ):
                    validate_explicit_proposition_portfolio_subject_link(
                        make_link(portfolio_subject_id=value)
                    )

    def test_validation_order_is_deterministic(self):
        cases = (
            (
                make_link(
                    proposition_id=None,
                    portfolio_subject_id=None,
                ),
                TypeError,
                "proposition_id must be str",
            ),
            (
                make_link(
                    proposition_id=" ",
                    portfolio_subject_id=None,
                ),
                ValueError,
                "proposition_id must not be blank",
            ),
            (
                make_link(portfolio_subject_id=None),
                TypeError,
                "portfolio_subject_id must be str",
            ),
            (
                make_link(portfolio_subject_id=" "),
                ValueError,
                "portfolio_subject_id must not be blank",
            ),
        )

        for link, exception, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    exception,
                    f"^{message}$",
                ):
                    validate_explicit_proposition_portfolio_subject_link(
                        link
                    )

    def test_success_preserves_link_and_field_object_identity(self):
        proposition_id = " proposition-\u00e9 "
        portfolio_subject_id = " subject-e\u0301 "
        link = ExplicitPropositionPortfolioSubjectLink(
            proposition_id,
            portfolio_subject_id,
        )
        original_link_id = id(link)

        result = (
            validate_explicit_proposition_portfolio_subject_link(
                link
            )
        )

        self.assertIsNone(result)
        self.assertEqual(id(link), original_link_id)
        self.assertIs(link.proposition_id, proposition_id)
        self.assertIs(
            link.portfolio_subject_id,
            portfolio_subject_id,
        )

    def test_equality_does_not_normalize_identifiers(self):
        distinct_pairs = (
            ("value", "VALUE"),
            ("value", " value "),
            ("\u00e9", "e\u0301"),
        )

        for left, right in distinct_pairs:
            with self.subTest(left=repr(left), right=repr(right)):
                self.assertNotEqual(
                    make_link(proposition_id=left),
                    make_link(proposition_id=right),
                )
                self.assertNotEqual(
                    make_link(portfolio_subject_id=left),
                    make_link(portfolio_subject_id=right),
                )

    def test_duplicate_and_shared_endpoints_are_not_rejected(self):
        first = make_link()
        duplicate = make_link()
        same_proposition = make_link(
            portfolio_subject_id="subject-002"
        )
        same_subject = make_link(
            proposition_id="proposition-002"
        )

        for link in (
            first,
            duplicate,
            same_proposition,
            same_subject,
        ):
            self.assertIsNone(
                validate_explicit_proposition_portfolio_subject_link(
                    link
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
            "PortfolioPropositionLink.models",
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
                "validate_explicit_proposition_portfolio_subject_link"
            ],
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
