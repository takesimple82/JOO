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

from PortfolioRiskBudget.models import (
    ExplicitPortfolioRiskBudget,
)
from PortfolioRiskBudget.validation import (
    validate_explicit_portfolio_risk_budget,
)


def make_risk_budget(**overrides):
    values = {
        "risk_budget_id": "risk-budget-001",
        "capital_bucket_id": "bucket-001",
    }
    values.update(overrides)
    return ExplicitPortfolioRiskBudget(**values)


class StringSubclass(str):
    pass


class RiskBudgetSubclass(ExplicitPortfolioRiskBudget):
    pass


class PortfolioRiskBudgetTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertTrue(
            is_dataclass(ExplicitPortfolioRiskBudget)
        )
        self.assertTrue(
            ExplicitPortfolioRiskBudget
            .__dataclass_params__.frozen
        )
        model_fields = fields(ExplicitPortfolioRiskBudget)
        self.assertEqual(
            [field.name for field in model_fields],
            ["risk_budget_id", "capital_bucket_id"],
        )
        self.assertEqual(
            get_type_hints(ExplicitPortfolioRiskBudget),
            {
                "risk_budget_id": str,
                "capital_bucket_id": str,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitPortfolioRiskBudget.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioRiskBudget.__dict__,
        )
        public_methods = {
            name
            for name, value
            in ExplicitPortfolioRiskBudget.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())

    def test_frozen_hashable_and_structural_equality(self):
        first = make_risk_budget()
        same = make_risk_budget()
        different_identity = make_risk_budget(
            risk_budget_id="risk-budget-002"
        )
        different_bucket = make_risk_budget(
            capital_bucket_id="bucket-002"
        )

        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertIsInstance(hash(first), int)
        self.assertNotEqual(first, different_identity)
        self.assertNotEqual(first, different_bucket)
        with self.assertRaises(FrozenInstanceError):
            first.risk_budget_id = "replacement"

    def test_exact_model_type_is_required_first(self):
        invalid = (
            None,
            object(),
            {},
            (),
            RiskBudgetSubclass(
                "risk-budget-001",
                "bucket-001",
            ),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^risk_budget must be "
                    "ExplicitPortfolioRiskBudget$",
                ):
                    validate_explicit_portfolio_risk_budget(
                        value
                    )

    def test_risk_budget_id_requires_exact_string(self):
        invalid = (
            None,
            1,
            b"risk-budget-001",
            StringSubclass("risk-budget-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^risk_budget_id must be str$",
                ):
                    validate_explicit_portfolio_risk_budget(
                        make_risk_budget(risk_budget_id=value)
                    )

    def test_capital_bucket_id_requires_exact_string(self):
        invalid = (
            None,
            1,
            b"bucket-001",
            StringSubclass("bucket-001"),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^capital_bucket_id must be str$",
                ):
                    validate_explicit_portfolio_risk_budget(
                        make_risk_budget(
                            capital_bucket_id=value
                        )
                    )

    def test_blank_and_whitespace_only_values_are_rejected(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(
                field="risk_budget_id",
                value=repr(value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^risk_budget_id must not be blank$",
                ):
                    validate_explicit_portfolio_risk_budget(
                        make_risk_budget(risk_budget_id=value)
                    )
            with self.subTest(
                field="capital_bucket_id",
                value=repr(value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^capital_bucket_id must not be blank$",
                ):
                    validate_explicit_portfolio_risk_budget(
                        make_risk_budget(
                            capital_bucket_id=value
                        )
                    )

    def test_surrounding_whitespace_and_objects_are_preserved(self):
        risk_budget_id = " risk-budget-é "
        capital_bucket_id = " bucket-é "
        risk_budget = ExplicitPortfolioRiskBudget(
            risk_budget_id,
            capital_bucket_id,
        )

        self.assertIsNone(
            validate_explicit_portfolio_risk_budget(
                risk_budget
            )
        )
        self.assertIs(
            risk_budget.risk_budget_id,
            risk_budget_id,
        )
        self.assertIs(
            risk_budget.capital_bucket_id,
            capital_bucket_id,
        )
        self.assertEqual(
            risk_budget.risk_budget_id,
            " risk-budget-é ",
        )
        self.assertEqual(
            risk_budget.capital_bucket_id,
            " bucket-é ",
        )

    def test_validation_order(self):
        cases = (
            (
                make_risk_budget(
                    risk_budget_id=None,
                    capital_bucket_id=None,
                ),
                TypeError,
                "risk_budget_id must be str",
            ),
            (
                make_risk_budget(
                    risk_budget_id=" ",
                    capital_bucket_id=None,
                ),
                ValueError,
                "risk_budget_id must not be blank",
            ),
            (
                make_risk_budget(capital_bucket_id=None),
                TypeError,
                "capital_bucket_id must be str",
            ),
            (
                make_risk_budget(capital_bucket_id=" "),
                ValueError,
                "capital_bucket_id must not be blank",
            ),
        )
        for risk_budget, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_risk_budget(
                        risk_budget
                    )

    def test_success_returns_none(self):
        self.assertIsNone(
            validate_explicit_portfolio_risk_budget(
                make_risk_budget()
            )
        )

    def test_uniqueness_is_not_enforced(self):
        first = make_risk_budget()
        duplicate = make_risk_budget()
        for risk_budget in (first, duplicate):
            self.assertIsNone(
                validate_explicit_portfolio_risk_budget(
                    risk_budget
                )
            )
        self.assertEqual(first, duplicate)

    def test_multiple_risk_budgets_share_capital_bucket(self):
        first = make_risk_budget(
            risk_budget_id="risk-budget-001"
        )
        second = make_risk_budget(
            risk_budget_id="risk-budget-002"
        )

        self.assertIsNone(
            validate_explicit_portfolio_risk_budget(first)
        )
        self.assertIsNone(
            validate_explicit_portfolio_risk_budget(second)
        )
        self.assertNotEqual(first, second)
        self.assertEqual(
            first.capital_bucket_id,
            second.capital_bucket_id,
        )

    def test_dependency_scope_and_public_api_are_exact(self):
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
            {"dataclasses"},
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {"PortfolioRiskBudget.models"},
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitPortfolioRiskBudget"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["validate_explicit_portfolio_risk_budget"],
        )

    def test_forbidden_responsibilities_absent_from_production(self):
        root = Path(__file__).resolve().parents[1]
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "ExplicitPortfolioCapitalBucket",
            "portfolio_id",
            "membership",
            "position",
            "holding",
            "watchlist",
            "snapshot",
            "amount",
            "limit",
            "threshold",
            "tolerance",
            "utilization",
            "remaining_capacity",
            "ratio",
            "percentage",
            "target_weight",
            "concentration",
            "currency",
            "quantity",
            "cash",
            "price",
            "cost_basis",
            "valuation",
            "profit",
            "loss",
            "observation_context",
            "timestamp",
            "label",
            "description",
            "category",
            "purpose",
            "taxonomy",
            "policy",
            "applicability",
            "semantic",
            "calculation",
            "breach",
            "monitoring",
            "recommendation",
            "allocation",
            "constraint",
            "execution",
            "ExpectedValue",
            "PortfolioImpact",
            "lookup",
            "registry",
            "persistence",
            "migration",
            "runtime",
            "orchestration",
            "automation",
            "approval",
            "override",
            "audit",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
