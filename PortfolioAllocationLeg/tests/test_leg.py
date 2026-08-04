import ast
import inspect
import unittest
import unicodedata
from dataclasses import FrozenInstanceError, MISSING, fields, is_dataclass
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from PortfolioAllocationLeg.models import ExplicitPortfolioAllocationLeg
from PortfolioAllocationLeg.validation import (
    validate_explicit_portfolio_allocation_leg,
)
from PortfolioAllocationProposalPositionLink.models import (
    ExplicitPortfolioAllocationProposalPositionLink,
)


def make_link(**overrides):
    values = {
        "allocation_proposal_id": "proposal-001",
        "position_id": "position-001",
    }
    values.update(overrides)
    return ExplicitPortfolioAllocationProposalPositionLink(**values)


def make_leg(**overrides):
    values = {
        "allocation_leg_id": "leg-001",
        "link": make_link(),
    }
    values.update(overrides)
    return ExplicitPortfolioAllocationLeg(**values)


class StringSubclass(str):
    pass


class LinkSubclass(ExplicitPortfolioAllocationProposalPositionLink):
    pass


class LegSubclass(ExplicitPortfolioAllocationLeg):
    pass


class PortfolioAllocationLegTests(unittest.TestCase):
    def test_exact_dataclass_contract(self):
        model = ExplicitPortfolioAllocationLeg
        self.assertTrue(is_dataclass(model))
        self.assertTrue(model.__dataclass_params__.frozen)
        model_fields = fields(model)
        self.assertEqual(
            [field.name for field in model_fields],
            ["allocation_leg_id", "link"],
        )
        self.assertEqual(
            get_type_hints(model),
            {
                "allocation_leg_id": str,
                "link": ExplicitPortfolioAllocationProposalPositionLink,
            },
        )
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
        public_properties = {
            name
            for name, value in model.__dict__.items()
            if not name.startswith("_") and isinstance(value, property)
        }
        self.assertEqual(public_properties, set())

    def test_frozen_hashable_and_structural_equality(self):
        first = make_leg()
        duplicate = make_leg()
        self.assertEqual(first, duplicate)
        self.assertEqual(hash(first), hash(duplicate))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(first, make_leg(allocation_leg_id="leg-002"))
        self.assertNotEqual(first, make_leg(link=make_link(position_id="position-002")))
        with self.assertRaises(FrozenInstanceError):
            first.allocation_leg_id = "replacement"
        with self.assertRaises(FrozenInstanceError):
            first.link = make_link()

    def test_exact_model_type_is_required_first_and_subclass_rejected(self):
        invalid = (
            None,
            object(),
            {},
            (),
            LegSubclass("leg-001", make_link()),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^leg must be ExplicitPortfolioAllocationLeg$",
                ):
                    validate_explicit_portfolio_allocation_leg(value)

    def test_allocation_leg_id_requires_exact_builtin_string(self):
        invalid = (None, 1, b"leg-001", StringSubclass("leg-001"))
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^allocation_leg_id must be str$",
                ):
                    validate_explicit_portfolio_allocation_leg(
                        make_leg(allocation_leg_id=value)
                    )

    def test_empty_and_whitespace_only_ids_are_rejected(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^allocation_leg_id must not be blank$",
                ):
                    validate_explicit_portfolio_allocation_leg(
                        make_leg(allocation_leg_id=value)
                    )

    def test_exact_link_type_is_required_and_subclass_rejected(self):
        subclass = LinkSubclass("proposal-001", "position-001")
        for value in (None, object(), {}, subclass):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^link must be "
                    "ExplicitPortfolioAllocationProposalPositionLink$",
                ):
                    validate_explicit_portfolio_allocation_leg(
                        make_leg(link=value)
                    )

    def test_validation_order_and_first_failure(self):
        cases = (
            (
                make_leg(allocation_leg_id=None, link=None),
                TypeError,
                "allocation_leg_id must be str",
            ),
            (
                make_leg(allocation_leg_id=" ", link=None),
                ValueError,
                "allocation_leg_id must not be blank",
            ),
            (
                make_leg(link=None),
                TypeError,
                "link must be ExplicitPortfolioAllocationProposalPositionLink",
            ),
        )
        for leg, error_type, message in cases:
            with self.subTest(message=message):
                with patch(
                    "PortfolioAllocationLeg.validation."
                    "validate_explicit_portfolio_allocation_proposal_position_link"
                ) as validator:
                    with self.assertRaisesRegex(error_type, f"^{message}$"):
                        validate_explicit_portfolio_allocation_leg(leg)
                validator.assert_not_called()

    def test_upstream_validator_called_once_with_retained_link(self):
        link = make_link()
        leg = make_leg(link=link)
        with patch(
            "PortfolioAllocationLeg.validation."
            "validate_explicit_portfolio_allocation_proposal_position_link"
        ) as validator:
            result = validate_explicit_portfolio_allocation_leg(leg)
        self.assertIsNone(result)
        validator.assert_called_once_with(link)
        self.assertIs(validator.call_args.args[0], link)

    def test_upstream_exception_propagates_with_identity(self):
        error = ValueError("upstream link failure")
        with patch(
            "PortfolioAllocationLeg.validation."
            "validate_explicit_portfolio_allocation_proposal_position_link",
            side_effect=error,
        ) as validator:
            with self.assertRaises(ValueError) as caught:
                validate_explicit_portfolio_allocation_leg(make_leg())
        self.assertIs(caught.exception, error)
        validator.assert_called_once()

    def test_preservation_and_no_normalization_or_reconstruction(self):
        allocation_leg_id = " Leg-\u00e9 "
        link = make_link(
            allocation_proposal_id=" Proposal-e\u0301 ",
            position_id=" Position-\u00e9 ",
        )
        leg = ExplicitPortfolioAllocationLeg(allocation_leg_id, link)
        self.assertIsNone(validate_explicit_portfolio_allocation_leg(leg))
        self.assertIs(leg.allocation_leg_id, allocation_leg_id)
        self.assertIs(leg.link, link)
        self.assertEqual(leg.allocation_leg_id, " Leg-\u00e9 ")
        composed = unicodedata.normalize("NFC", "e\u0301")
        decomposed = unicodedata.normalize("NFD", "\u00e9")
        self.assertNotEqual(make_leg(allocation_leg_id=composed), make_leg(allocation_leg_id=decomposed))
        self.assertNotEqual(make_leg(allocation_leg_id="leg"), make_leg(allocation_leg_id="LEG"))
        self.assertNotEqual(make_leg(allocation_leg_id="leg"), make_leg(allocation_leg_id=" leg "))

    def test_multiplicity_equal_links_and_duplicate_legs_are_accepted(self):
        shared_link = make_link()
        same_proposal = make_link(position_id="position-002")
        same_position = make_link(allocation_proposal_id="proposal-002")
        equal_distinct_link = make_link()
        legs = (
            ExplicitPortfolioAllocationLeg("leg-001", shared_link),
            ExplicitPortfolioAllocationLeg("leg-002", shared_link),
            ExplicitPortfolioAllocationLeg("leg-003", same_proposal),
            ExplicitPortfolioAllocationLeg("leg-004", same_position),
            ExplicitPortfolioAllocationLeg("leg-005", equal_distinct_link),
            ExplicitPortfolioAllocationLeg("leg-001", make_link()),
        )
        for leg in legs:
            self.assertIsNone(validate_explicit_portfolio_allocation_leg(leg))
        self.assertIs(legs[0].link, legs[1].link)
        self.assertEqual(legs[0].link.allocation_proposal_id, legs[2].link.allocation_proposal_id)
        self.assertEqual(legs[0].link.position_id, legs[3].link.position_id)
        self.assertIsNot(legs[0].link, legs[4].link)
        self.assertEqual(legs[0].link, legs[4].link)
        self.assertEqual(legs[0], legs[5])

    def test_signature_import_boundary_and_public_api_are_exact(self):
        signature = inspect.signature(validate_explicit_portfolio_allocation_leg)
        self.assertEqual(list(signature.parameters), ["leg"])
        self.assertIs(
            signature.parameters["leg"].annotation,
            ExplicitPortfolioAllocationLeg,
        )
        self.assertIs(signature.return_annotation, None)

        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse((root / "models.py").read_text())
        validation_tree = ast.parse((root / "validation.py").read_text())
        self.assertEqual(
            {
                node.module
                for node in ast.walk(model_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "dataclasses",
                "PortfolioAllocationProposalPositionLink.models",
            },
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "PortfolioAllocationLeg.models",
                "PortfolioAllocationProposalPositionLink.models",
                "PortfolioAllocationProposalPositionLink.validation",
            },
        )
        self.assertEqual(
            [node.name for node in model_tree.body if isinstance(node, ast.ClassDef)],
            ["ExplicitPortfolioAllocationLeg"],
        )
        self.assertEqual(
            [node.name for node in validation_tree.body if isinstance(node, ast.FunctionDef)],
            ["validate_explicit_portfolio_allocation_leg"],
        )

    def test_forbidden_fields_and_responsibilities_absent_from_production(self):
        root = Path(__file__).resolve().parents[1]
        production = (root / "models.py").read_text() + (root / "validation.py").read_text()
        for forbidden in (
            "quantity",
            "amount",
            "currency",
            "unit_id",
            "weight",
            "target",
            "delta",
            "portfolio_id",
            "position_id",
            "recommendation_id",
            "snapshot_id",
            "capital_bucket_id",
            "risk_budget_id",
            "applicability",
            "lookup",
            "repository",
            "registry",
            "persistence",
            "runtime",
            "execution",
            "approval",
        ):
            self.assertNotIn(forbidden, production)

    def test_readme_matches_frozen_contract(self):
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
        normalized = " ".join(readme.split())
        required = (
            "ExplicitPortfolioAllocationLeg",
            "validate_explicit_portfolio_allocation_leg()",
            "allocation_leg_id: str",
            "link: ExplicitPortfolioAllocationProposalPositionLink",
            "frozen, hashable",
            "first local validation failure wins",
            "exact exception object identity preserved",
            "exact built-in `str`",
            "exact caller-supplied string object",
            "Unicode form remain exact",
            "duplicate complete Leg values",
            "uniqueness is not enforced",
            "owns no collection, ordering",
            "Dependency boundary",
            "Non-responsibilities",
            "proposed absolute quantity",
            "M45 applicability classification",
            "runtime, CLI, automation",
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, normalized)


if __name__ == "__main__":
    unittest.main()
