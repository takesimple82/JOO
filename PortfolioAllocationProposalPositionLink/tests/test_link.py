import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields, is_dataclass
from pathlib import Path
from typing import get_type_hints

from PortfolioAllocationProposalPositionLink.models import (
    ExplicitPortfolioAllocationProposalPositionLink,
)
from PortfolioAllocationProposalPositionLink.validation import (
    validate_explicit_portfolio_allocation_proposal_position_link,
)


def make_link(**overrides):
    values = {
        "allocation_proposal_id": "proposal-001",
        "position_id": "position-001",
    }
    values.update(overrides)
    return ExplicitPortfolioAllocationProposalPositionLink(**values)


class StringSubclass(str):
    pass


class LinkSubclass(ExplicitPortfolioAllocationProposalPositionLink):
    pass


class PortfolioAllocationProposalPositionLinkTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model = ExplicitPortfolioAllocationProposalPositionLink
        self.assertTrue(is_dataclass(model))
        self.assertTrue(model.__dataclass_params__.frozen)
        model_fields = fields(model)
        self.assertEqual(
            [field.name for field in model_fields],
            ["allocation_proposal_id", "position_id"],
        )
        self.assertEqual(
            get_type_hints(model),
            {"allocation_proposal_id": str, "position_id": str},
        )
        self.assertEqual(len(model_fields), 2)
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn("__slots__", model.__dict__)
        self.assertNotIn("__post_init__", model.__dict__)
        public_methods = {
            name
            for name, value in model.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_frozen_hashable_and_structural_equality(self):
        first = make_link()
        duplicate = make_link()
        self.assertEqual(first, duplicate)
        self.assertEqual(hash(first), hash(duplicate))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(
            first, make_link(allocation_proposal_id="proposal-002")
        )
        self.assertNotEqual(first, make_link(position_id="position-002"))
        with self.assertRaises(FrozenInstanceError):
            first.allocation_proposal_id = "replacement"
        with self.assertRaises(FrozenInstanceError):
            first.position_id = "replacement"

    def test_no_link_id_or_extra_constructor_fields(self):
        self.assertNotIn(
            "link_id",
            [
                field.name
                for field in fields(
                    ExplicitPortfolioAllocationProposalPositionLink
                )
            ],
        )
        with self.assertRaises(TypeError):
            ExplicitPortfolioAllocationProposalPositionLink(
                allocation_proposal_id="proposal-001",
                position_id="position-001",
                link_id="link-001",
            )

    def test_exact_model_type_is_required_first(self):
        invalid = (
            None,
            object(),
            {},
            (),
            LinkSubclass("proposal-001", "position-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^link must be "
                    "ExplicitPortfolioAllocationProposalPositionLink$",
                ):
                    validate_explicit_portfolio_allocation_proposal_position_link(
                        value
                    )

    def test_allocation_proposal_id_requires_exact_builtin_string(self):
        invalid = (None, 1, b"proposal-001", StringSubclass("proposal-001"))
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^allocation_proposal_id must be str$",
                ):
                    validate_explicit_portfolio_allocation_proposal_position_link(
                        make_link(allocation_proposal_id=value)
                    )

    def test_allocation_proposal_id_rejects_blank_strings(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^allocation_proposal_id must not be blank$",
                ):
                    validate_explicit_portfolio_allocation_proposal_position_link(
                        make_link(allocation_proposal_id=value)
                    )

    def test_position_id_requires_exact_builtin_string(self):
        invalid = (None, 1, b"position-001", StringSubclass("position-001"))
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^position_id must be str$",
                ):
                    validate_explicit_portfolio_allocation_proposal_position_link(
                        make_link(position_id=value)
                    )

    def test_position_id_rejects_blank_strings(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^position_id must not be blank$",
                ):
                    validate_explicit_portfolio_allocation_proposal_position_link(
                        make_link(position_id=value)
                    )

    def test_validation_order(self):
        cases = (
            (
                make_link(allocation_proposal_id=None, position_id=None),
                TypeError,
                "allocation_proposal_id must be str",
            ),
            (
                make_link(allocation_proposal_id=" ", position_id=None),
                ValueError,
                "allocation_proposal_id must not be blank",
            ),
            (
                make_link(position_id=None),
                TypeError,
                "position_id must be str",
            ),
            (
                make_link(position_id=" "),
                ValueError,
                "position_id must not be blank",
            ),
        )
        for link, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(error_type, f"^{message}$"):
                    validate_explicit_portfolio_allocation_proposal_position_link(
                        link
                    )

    def test_success_preserves_exact_values_and_objects(self):
        allocation_proposal_id = " proposal-\u00e9 "
        position_id = " position-e\u0301 "
        link = ExplicitPortfolioAllocationProposalPositionLink(
            allocation_proposal_id, position_id
        )
        original_link_id = id(link)

        result = validate_explicit_portfolio_allocation_proposal_position_link(
            link
        )

        self.assertIsNone(result)
        self.assertEqual(id(link), original_link_id)
        self.assertIs(link.allocation_proposal_id, allocation_proposal_id)
        self.assertIs(link.position_id, position_id)
        self.assertEqual(link.allocation_proposal_id, " proposal-\u00e9 ")
        self.assertEqual(link.position_id, " position-e\u0301 ")

    def test_no_normalization_or_reconstruction(self):
        distinct_values = (
            ("value", "VALUE"),
            ("value", " value "),
            ("\u00e9", "e\u0301"),
        )
        for left, right in distinct_values:
            with self.subTest(left=repr(left), right=repr(right)):
                self.assertNotEqual(
                    make_link(allocation_proposal_id=left),
                    make_link(allocation_proposal_id=right),
                )
                self.assertNotEqual(
                    make_link(position_id=left),
                    make_link(position_id=right),
                )

    def test_multiplicity_and_duplicate_pairs_are_accepted(self):
        first = make_link()
        duplicate = make_link()
        same_proposal = make_link(position_id="position-002")
        same_position = make_link(allocation_proposal_id="proposal-002")
        for link in (first, duplicate, same_proposal, same_position):
            self.assertIsNone(
                validate_explicit_portfolio_allocation_proposal_position_link(
                    link
                )
            )
        self.assertEqual(first, duplicate)
        self.assertEqual(
            first.allocation_proposal_id,
            same_proposal.allocation_proposal_id,
        )
        self.assertEqual(first.position_id, same_position.position_id)

    def test_production_dependency_and_public_api_boundary(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse((root / "models.py").read_text())
        validation_tree = ast.parse((root / "validation.py").read_text())
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
            "PortfolioAllocationProposalPositionLink.models",
        )
        self.assertEqual(
            [node.name for node in model_tree.body if isinstance(node, ast.ClassDef)],
            ["ExplicitPortfolioAllocationProposalPositionLink"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_portfolio_allocation_proposal_position_link"
            ],
        )

    def test_forbidden_fields_and_responsibilities_are_absent(self):
        root = Path(__file__).resolve().parents[1]
        production = (root / "models.py").read_text() + (
            root / "validation.py"
        ).read_text()
        for forbidden in (
            "link_id",
            "timestamp",
            "label",
            "status",
            "portfolio_id",
            "portfolio_snapshot_id",
            "recommendation_id",
            "quantity",
            "amount",
            "weight",
            "capital_bucket_id",
            "risk_budget_id",
            "action",
            "lookup",
            "repository",
            "persistence",
            "runtime",
            "orchestration",
        ):
            self.assertNotIn(forbidden, production)

    def test_readme_documents_the_approved_contract(self):
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
        for required in (
            "ExplicitPortfolioAllocationProposalPositionLink",
            "validate_explicit_portfolio_allocation_proposal_position_link()",
            "allocation_proposal_id: str",
            "position_id: str",
            "frozen, hashable",
            "exact built-in `str`",
            "exact caller-supplied string object and value",
            "foreign opaque identifier",
            "Many Position links",
            "Many Allocation Proposal links",
            "duplicate exact pairs",
            "standard library",
            "Non-responsibilities",
        ):
            self.assertIn(required, readme)


if __name__ == "__main__":
    unittest.main()
