import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields, is_dataclass
from pathlib import Path
from typing import get_type_hints

from PortfolioAllocationProposalEndpoint.models import (
    ExplicitPortfolioAllocationProposalEndpoint,
)
from PortfolioAllocationProposalEndpoint.validation import (
    validate_explicit_portfolio_allocation_proposal_endpoint,
)


def make_endpoint(**overrides):
    values = {
        "allocation_proposal_id": "proposal-001",
        "recommendation_id": "recommendation-001",
    }
    values.update(overrides)
    return ExplicitPortfolioAllocationProposalEndpoint(**values)


class StringSubclass(str):
    pass


class EndpointSubclass(ExplicitPortfolioAllocationProposalEndpoint):
    pass


class PortfolioAllocationProposalEndpointTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertTrue(is_dataclass(ExplicitPortfolioAllocationProposalEndpoint))
        self.assertTrue(
            ExplicitPortfolioAllocationProposalEndpoint.__dataclass_params__.frozen
        )
        model_fields = fields(ExplicitPortfolioAllocationProposalEndpoint)
        self.assertEqual(
            [field.name for field in model_fields],
            ["allocation_proposal_id", "recommendation_id"],
        )
        self.assertEqual(
            get_type_hints(ExplicitPortfolioAllocationProposalEndpoint),
            {"allocation_proposal_id": str, "recommendation_id": str},
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__", ExplicitPortfolioAllocationProposalEndpoint.__dict__
        )
        self.assertNotIn("__slots__", ExplicitPortfolioAllocationProposalEndpoint.__dict__)
        public_methods = {
            name
            for name, value in ExplicitPortfolioAllocationProposalEndpoint.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_frozen_hashable_and_structural_equality(self):
        first = make_endpoint()
        duplicate = make_endpoint()
        self.assertEqual(first, duplicate)
        self.assertEqual(hash(first), hash(duplicate))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(
            first, make_endpoint(allocation_proposal_id="proposal-002")
        )
        self.assertNotEqual(
            first, make_endpoint(recommendation_id="recommendation-002")
        )
        with self.assertRaises(FrozenInstanceError):
            first.allocation_proposal_id = "replacement"

    def test_exact_model_type_is_required_first(self):
        invalid = (
            None,
            object(),
            {},
            (),
            EndpointSubclass("proposal-001", "recommendation-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^endpoint must be ExplicitPortfolioAllocationProposalEndpoint$",
                ):
                    validate_explicit_portfolio_allocation_proposal_endpoint(value)

    def test_identifiers_require_exact_builtin_strings(self):
        invalid = (None, 1, b"identifier", StringSubclass("identifier"))
        for field_name in ("allocation_proposal_id", "recommendation_id"):
            for value in invalid:
                with self.subTest(field=field_name, value_type=type(value)):
                    with self.assertRaisesRegex(
                        TypeError, f"^{field_name} must be str$"
                    ):
                        validate_explicit_portfolio_allocation_proposal_endpoint(
                            make_endpoint(**{field_name: value})
                        )

    def test_empty_and_whitespace_only_identifiers_are_rejected(self):
        for field_name in ("allocation_proposal_id", "recommendation_id"):
            for value in ("", " ", "\t", "\n", " \t\n "):
                with self.subTest(field=field_name, value=repr(value)):
                    with self.assertRaisesRegex(
                        ValueError, f"^{field_name} must not be blank$"
                    ):
                        validate_explicit_portfolio_allocation_proposal_endpoint(
                            make_endpoint(**{field_name: value})
                        )

    def test_validation_order(self):
        cases = (
            (
                make_endpoint(allocation_proposal_id=None, recommendation_id=None),
                TypeError,
                "allocation_proposal_id must be str",
            ),
            (
                make_endpoint(allocation_proposal_id=" ", recommendation_id=None),
                ValueError,
                "allocation_proposal_id must not be blank",
            ),
            (
                make_endpoint(recommendation_id=None),
                TypeError,
                "recommendation_id must be str",
            ),
            (
                make_endpoint(recommendation_id=" "),
                ValueError,
                "recommendation_id must not be blank",
            ),
        )
        for endpoint, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(error_type, f"^{message}$"):
                    validate_explicit_portfolio_allocation_proposal_endpoint(endpoint)

    def test_surrounding_whitespace_and_exact_objects_are_preserved(self):
        allocation_proposal_id = " proposal-é "
        recommendation_id = " recommendation-é "
        endpoint = ExplicitPortfolioAllocationProposalEndpoint(
            allocation_proposal_id, recommendation_id
        )
        self.assertIsNone(
            validate_explicit_portfolio_allocation_proposal_endpoint(endpoint)
        )
        self.assertIs(endpoint.allocation_proposal_id, allocation_proposal_id)
        self.assertIs(endpoint.recommendation_id, recommendation_id)
        self.assertEqual(endpoint.allocation_proposal_id, " proposal-é ")
        self.assertEqual(endpoint.recommendation_id, " recommendation-é ")

    def test_multiplicity_and_duplicate_pairs_are_accepted(self):
        first = make_endpoint(allocation_proposal_id="proposal-001")
        second = make_endpoint(allocation_proposal_id="proposal-002")
        duplicate = make_endpoint(allocation_proposal_id="proposal-001")
        for endpoint in (first, second, duplicate):
            self.assertIsNone(
                validate_explicit_portfolio_allocation_proposal_endpoint(endpoint)
            )
        self.assertEqual(first.recommendation_id, second.recommendation_id)
        self.assertEqual(first, duplicate)

    def test_dependency_scope_and_public_api_are_exact(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse((root / "models.py").read_text())
        validation_tree = ast.parse((root / "validation.py").read_text())
        self.assertEqual(
            {
                node.module
                for node in ast.walk(model_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {"dataclasses"},
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {"PortfolioAllocationProposalEndpoint.models"},
        )
        self.assertEqual(
            [node.name for node in model_tree.body if isinstance(node, ast.ClassDef)],
            ["ExplicitPortfolioAllocationProposalEndpoint"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["validate_explicit_portfolio_allocation_proposal_endpoint"],
        )

    def test_forbidden_fields_and_responsibilities_are_absent(self):
        root = Path(__file__).resolve().parents[1]
        production = (root / "models.py").read_text() + (
            root / "validation.py"
        ).read_text()
        for forbidden in (
            "portfolio_id",
            "portfolio_snapshot_id",
            "capital_bucket_id",
            "risk_budget_id",
            "target",
            "content",
            "link_id",
            "timestamp",
            "label",
            "ExplicitPortfolioRecommendationEndpoint",
            "PortfolioRecommendationEndpoint",
            "lookup",
            "uniqueness",
            "persistence",
            "runtime",
            "orchestration",
        ):
            self.assertNotIn(forbidden, production)

    def test_readme_documents_the_approved_contract(self):
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
        for required in (
            "allocation_proposal_id: str",
            "recommendation_id: str",
            "exact caller-supplied string object and value",
            "foreign opaque identifier",
            "Multiple Allocation Proposals",
            "duplicate exact",
            "uniqueness",
            "persistence",
            "runtime",
        ):
            self.assertIn(required, readme)


if __name__ == "__main__":
    unittest.main()
