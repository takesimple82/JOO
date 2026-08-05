import ast
import inspect
import unittest
import unicodedata
from dataclasses import is_dataclass
from enum import Enum
from pathlib import Path
from unittest.mock import patch

from PortfolioAllocationLegAssociationConsistencyApplicability.classification import (
    classify_portfolio_allocation_leg_association_consistency_applicability,
)
from PortfolioAllocationLegAssociationConsistencyApplicability.models import (
    PortfolioAllocationLegAssociationConsistencyApplicabilityStatus,
)
from PortfolioAllocationLegCapitalBucketLink.models import (
    ExplicitPortfolioAllocationLegCapitalBucketLink,
)
from PortfolioAllocationLegRiskBudgetLink.models import (
    ExplicitPortfolioAllocationLegRiskBudgetLink,
)
from PortfolioRiskBudget.models import ExplicitPortfolioRiskBudget


def make_capital_bucket_link(**overrides):
    values = {
        "allocation_leg_id": "leg-001",
        "capital_bucket_id": "bucket-001",
    }
    values.update(overrides)
    return ExplicitPortfolioAllocationLegCapitalBucketLink(**values)


def make_risk_budget_link(**overrides):
    values = {
        "allocation_leg_id": "leg-001",
        "risk_budget_id": "risk-budget-001",
    }
    values.update(overrides)
    return ExplicitPortfolioAllocationLegRiskBudgetLink(**values)


def make_risk_budget(**overrides):
    values = {
        "risk_budget_id": "risk-budget-001",
        "capital_bucket_id": "bucket-001",
    }
    values.update(overrides)
    return ExplicitPortfolioRiskBudget(**values)


class PortfolioAllocationLegAssociationConsistencyApplicabilityTests(
    unittest.TestCase
):
    def classify(self, capital_bucket_link=None, risk_budget_link=None, risk_budget=None):
        return classify_portfolio_allocation_leg_association_consistency_applicability(
            capital_bucket_link or make_capital_bucket_link(),
            risk_budget_link or make_risk_budget_link(),
            risk_budget or make_risk_budget(),
        )

    def test_exact_status_enum_contract(self):
        status = PortfolioAllocationLegAssociationConsistencyApplicabilityStatus
        self.assertTrue(issubclass(status, Enum))
        self.assertFalse(is_dataclass(status))
        self.assertEqual(
            [member.name for member in status],
            [
                "ALLOCATION_LEG_ENDPOINT_MISMATCH",
                "RISK_BUDGET_ENDPOINT_MISMATCH",
                "CAPITAL_BUCKET_ENDPOINT_MISMATCH",
                "APPLICABLE",
            ],
        )
        self.assertEqual(
            [member.value for member in status],
            [member.name for member in status],
        )
        self.assertEqual(len(status.__members__), 4)
        self.assertEqual(
            {member.name: member for member in status},
            status.__members__,
        )
        public_methods = {
            name
            for name, item in status.__dict__.items()
            if not name.startswith("_") and callable(item)
        }
        self.assertEqual(public_methods, set())
        public_properties = {
            name
            for name, item in status.__dict__.items()
            if not name.startswith("_") and isinstance(item, property)
        }
        self.assertEqual(public_properties, set())

    def test_enum_identity_equality_hash_and_immutability(self):
        status = PortfolioAllocationLegAssociationConsistencyApplicabilityStatus
        self.assertIs(status.APPLICABLE, status.APPLICABLE)
        self.assertEqual(status.APPLICABLE, status.APPLICABLE)
        self.assertEqual(hash(status.APPLICABLE), hash(status.APPLICABLE))
        self.assertNotEqual(
            status.APPLICABLE,
            status.CAPITAL_BUCKET_ENDPOINT_MISMATCH,
        )
        with self.assertRaises(AttributeError):
            status.APPLICABLE.value = "replacement"

    def test_exact_classifier_signature(self):
        classifier = (
            classify_portfolio_allocation_leg_association_consistency_applicability
        )
        signature = inspect.signature(classifier)
        self.assertEqual(
            list(signature.parameters),
            ["capital_bucket_link", "risk_budget_link", "risk_budget"],
        )
        expected_annotations = (
            ExplicitPortfolioAllocationLegCapitalBucketLink,
            ExplicitPortfolioAllocationLegRiskBudgetLink,
            ExplicitPortfolioRiskBudget,
        )
        for parameter, annotation in zip(
            signature.parameters.values(),
            expected_annotations,
        ):
            self.assertEqual(
                parameter.kind,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
            self.assertIs(parameter.default, inspect.Parameter.empty)
            self.assertIs(parameter.annotation, annotation)
        self.assertIs(
            signature.return_annotation,
            PortfolioAllocationLegAssociationConsistencyApplicabilityStatus,
        )

    def test_upstream_validators_called_once_in_exact_order(self):
        calls = []
        capital_bucket_link = make_capital_bucket_link()
        risk_budget_link = make_risk_budget_link()
        risk_budget = make_risk_budget()
        with patch(
            "PortfolioAllocationLegAssociationConsistencyApplicability."
            "classification."
            "validate_explicit_portfolio_allocation_leg_capital_bucket_link",
            side_effect=lambda item: calls.append(("capital", item)),
        ) as capital_validator, patch(
            "PortfolioAllocationLegAssociationConsistencyApplicability."
            "classification."
            "validate_explicit_portfolio_allocation_leg_risk_budget_link",
            side_effect=lambda item: calls.append(("risk_link", item)),
        ) as risk_link_validator, patch(
            "PortfolioAllocationLegAssociationConsistencyApplicability."
            "classification.validate_explicit_portfolio_risk_budget",
            side_effect=lambda item: calls.append(("risk_budget", item)),
        ) as risk_budget_validator:
            result = self.classify(
                capital_bucket_link,
                risk_budget_link,
                risk_budget,
            )
        self.assertIs(
            result,
            PortfolioAllocationLegAssociationConsistencyApplicabilityStatus.APPLICABLE,
        )
        self.assertEqual(
            calls,
            [
                ("capital", capital_bucket_link),
                ("risk_link", risk_budget_link),
                ("risk_budget", risk_budget),
            ],
        )
        capital_validator.assert_called_once_with(capital_bucket_link)
        risk_link_validator.assert_called_once_with(risk_budget_link)
        risk_budget_validator.assert_called_once_with(risk_budget)

    def test_first_upstream_failure_stops_later_validation(self):
        error = ValueError("first upstream failure")
        with patch(
            "PortfolioAllocationLegAssociationConsistencyApplicability."
            "classification."
            "validate_explicit_portfolio_allocation_leg_capital_bucket_link",
            side_effect=error,
        ) as first, patch(
            "PortfolioAllocationLegAssociationConsistencyApplicability."
            "classification."
            "validate_explicit_portfolio_allocation_leg_risk_budget_link"
        ) as second, patch(
            "PortfolioAllocationLegAssociationConsistencyApplicability."
            "classification.validate_explicit_portfolio_risk_budget"
        ) as third:
            with self.assertRaises(ValueError) as caught:
                self.classify()
        self.assertIs(caught.exception, error)
        first.assert_called_once()
        second.assert_not_called()
        third.assert_not_called()

    def test_second_upstream_failure_stops_third_validation(self):
        error = TypeError("second upstream failure")
        with patch(
            "PortfolioAllocationLegAssociationConsistencyApplicability."
            "classification."
            "validate_explicit_portfolio_allocation_leg_capital_bucket_link"
        ) as first, patch(
            "PortfolioAllocationLegAssociationConsistencyApplicability."
            "classification."
            "validate_explicit_portfolio_allocation_leg_risk_budget_link",
            side_effect=error,
        ) as second, patch(
            "PortfolioAllocationLegAssociationConsistencyApplicability."
            "classification.validate_explicit_portfolio_risk_budget"
        ) as third:
            with self.assertRaises(TypeError) as caught:
                self.classify()
        self.assertIs(caught.exception, error)
        first.assert_called_once()
        second.assert_called_once()
        third.assert_not_called()

    def test_real_upstream_exception_contracts_and_required_inputs(self):
        cases = (
            (
                None,
                make_risk_budget_link(),
                make_risk_budget(),
                TypeError,
                "link must be ExplicitPortfolioAllocationLegCapitalBucketLink",
            ),
            (
                make_capital_bucket_link(),
                None,
                make_risk_budget(),
                TypeError,
                "link must be ExplicitPortfolioAllocationLegRiskBudgetLink",
            ),
            (
                make_capital_bucket_link(),
                make_risk_budget_link(),
                None,
                TypeError,
                "risk_budget must be ExplicitPortfolioRiskBudget",
            ),
            (
                make_capital_bucket_link(capital_bucket_id=""),
                make_risk_budget_link(),
                make_risk_budget(),
                ValueError,
                "capital_bucket_id must not be blank",
            ),
            (
                make_capital_bucket_link(),
                make_risk_budget_link(risk_budget_id=""),
                make_risk_budget(),
                ValueError,
                "risk_budget_id must not be blank",
            ),
            (
                make_capital_bucket_link(),
                make_risk_budget_link(),
                make_risk_budget(capital_bucket_id=""),
                ValueError,
                "capital_bucket_id must not be blank",
            ),
        )
        for capital_link, risk_link, risk_budget, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(error_type, f"^{message}$"):
                    classify_portfolio_allocation_leg_association_consistency_applicability(
                        capital_link,
                        risk_link,
                        risk_budget,
                    )

    def test_allocation_leg_mismatch_has_first_precedence(self):
        result = self.classify(
            make_capital_bucket_link(
                allocation_leg_id="leg-001",
                capital_bucket_id="bucket-left",
            ),
            make_risk_budget_link(
                allocation_leg_id="leg-002",
                risk_budget_id="risk-left",
            ),
            make_risk_budget(
                risk_budget_id="risk-right",
                capital_bucket_id="bucket-right",
            ),
        )
        self.assertIs(
            result,
            PortfolioAllocationLegAssociationConsistencyApplicabilityStatus
            .ALLOCATION_LEG_ENDPOINT_MISMATCH,
        )

    def test_risk_budget_mismatch_has_second_precedence(self):
        result = self.classify(
            make_capital_bucket_link(capital_bucket_id="bucket-left"),
            make_risk_budget_link(risk_budget_id="risk-left"),
            make_risk_budget(
                risk_budget_id="risk-right",
                capital_bucket_id="bucket-right",
            ),
        )
        self.assertIs(
            result,
            PortfolioAllocationLegAssociationConsistencyApplicabilityStatus
            .RISK_BUDGET_ENDPOINT_MISMATCH,
        )

    def test_capital_bucket_mismatch_has_third_precedence(self):
        result = self.classify(
            make_capital_bucket_link(capital_bucket_id="bucket-left"),
            make_risk_budget_link(),
            make_risk_budget(capital_bucket_id="bucket-right"),
        )
        self.assertIs(
            result,
            PortfolioAllocationLegAssociationConsistencyApplicabilityStatus
            .CAPITAL_BUCKET_ENDPOINT_MISMATCH,
        )

    def test_fully_aligned_set_is_applicable(self):
        self.assertIs(
            self.classify(),
            PortfolioAllocationLegAssociationConsistencyApplicabilityStatus.APPLICABLE,
        )

    def test_exact_string_comparisons_case_whitespace_and_unicode(self):
        status = PortfolioAllocationLegAssociationConsistencyApplicabilityStatus
        composed = unicodedata.normalize("NFC", "e\u0301")
        decomposed = unicodedata.normalize("NFD", "\u00e9")
        cases = (
            (
                make_capital_bucket_link(allocation_leg_id="leg"),
                make_risk_budget_link(allocation_leg_id="LEG"),
                make_risk_budget(),
                status.ALLOCATION_LEG_ENDPOINT_MISMATCH,
            ),
            (
                make_capital_bucket_link(),
                make_risk_budget_link(risk_budget_id=" risk-budget-001 "),
                make_risk_budget(),
                status.RISK_BUDGET_ENDPOINT_MISMATCH,
            ),
            (
                make_capital_bucket_link(capital_bucket_id=composed),
                make_risk_budget_link(),
                make_risk_budget(capital_bucket_id=decomposed),
                status.CAPITAL_BUCKET_ENDPOINT_MISMATCH,
            ),
        )
        for capital_link, risk_link, risk_budget, expected in cases:
            with self.subTest(expected=expected):
                self.assertIs(
                    classify_portfolio_allocation_leg_association_consistency_applicability(
                        capital_link,
                        risk_link,
                        risk_budget,
                    ),
                    expected,
                )

    def test_equal_distinct_strings_and_all_objects_are_preserved(self):
        capital_leg_id = "".join(("leg", "-001"))
        risk_leg_id = "".join(("leg-", "001"))
        capital_bucket_id = "".join(("bucket", "-001"))
        endpoint_bucket_id = "".join(("bucket-", "001"))
        link_risk_id = "".join(("risk-budget", "-001"))
        endpoint_risk_id = "".join(("risk-budget-", "001"))
        capital_link = make_capital_bucket_link(
            allocation_leg_id=capital_leg_id,
            capital_bucket_id=capital_bucket_id,
        )
        risk_link = make_risk_budget_link(
            allocation_leg_id=risk_leg_id,
            risk_budget_id=link_risk_id,
        )
        risk_budget = make_risk_budget(
            risk_budget_id=endpoint_risk_id,
            capital_bucket_id=endpoint_bucket_id,
        )
        before = (
            capital_link.allocation_leg_id,
            capital_link.capital_bucket_id,
            risk_link.allocation_leg_id,
            risk_link.risk_budget_id,
            risk_budget.risk_budget_id,
            risk_budget.capital_bucket_id,
        )
        self.assertIs(
            self.classify(capital_link, risk_link, risk_budget),
            PortfolioAllocationLegAssociationConsistencyApplicabilityStatus.APPLICABLE,
        )
        after = (
            capital_link.allocation_leg_id,
            capital_link.capital_bucket_id,
            risk_link.allocation_leg_id,
            risk_link.risk_budget_id,
            risk_budget.risk_budget_id,
            risk_budget.capital_bucket_id,
        )
        for original, retained in zip(before, after):
            self.assertIs(retained, original)

    def test_duplicates_can_participate_without_collection_behavior(self):
        first = make_capital_bucket_link()
        duplicate = make_capital_bucket_link()
        self.assertEqual(first, duplicate)
        for capital_link in (first, duplicate):
            self.assertIs(
                self.classify(capital_link),
                PortfolioAllocationLegAssociationConsistencyApplicabilityStatus.APPLICABLE,
            )

    def test_imports_and_production_definitions_are_exact(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse((root / "models.py").read_text())
        classification_tree = ast.parse((root / "classification.py").read_text())
        self.assertEqual(
            {
                node.module
                for node in ast.walk(model_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {"enum"},
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(classification_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "PortfolioAllocationLegAssociationConsistencyApplicability.models",
                "PortfolioAllocationLegCapitalBucketLink.models",
                "PortfolioAllocationLegCapitalBucketLink.validation",
                "PortfolioAllocationLegRiskBudgetLink.models",
                "PortfolioAllocationLegRiskBudgetLink.validation",
                "PortfolioRiskBudget.models",
                "PortfolioRiskBudget.validation",
            },
        )
        self.assertEqual(
            [node.name for node in model_tree.body if isinstance(node, ast.ClassDef)],
            ["PortfolioAllocationLegAssociationConsistencyApplicabilityStatus"],
        )
        self.assertEqual(
            [
                node.name
                for node in classification_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["classify_portfolio_allocation_leg_association_consistency_applicability"],
        )

    def test_production_and_readme_boundaries(self):
        root = Path(__file__).resolve().parents[1]
        production = (root / "models.py").read_text() + (root / "classification.py").read_text()
        for forbidden in (
            "PortfolioAllocationLeg.models",
            "PortfolioCapitalBucket",
            "constraint",
            "repository",
            "registry",
            "mapping",
            "database",
            "lookup",
            "persistence",
            "runtime",
            "orchestration",
            "execution",
            "amount",
            "capacity",
            "utilization",
            "severity",
        ):
            self.assertNotIn(forbidden, production)

        readme = (root / "README.md").read_text()
        normalized = " ".join(readme.split())
        required = (
            "PortfolioAllocationLegAssociationConsistencyApplicability",
            "PortfolioAllocationLegAssociationConsistencyApplicabilityStatus",
            "classify_portfolio_allocation_leg_association_consistency_applicability()",
            "ALLOCATION_LEG_ENDPOINT_MISMATCH",
            "RISK_BUDGET_ENDPOINT_MISMATCH",
            "CAPITAL_BUCKET_ENDPOINT_MISMATCH",
            "APPLICABLE",
            "required",
            "exactly once",
            "first upstream exception object",
            "first mismatch wins",
            "exact stored string equality",
            "one explicitly supplied comparison set",
            "does not detect duplicates",
            "Dependency boundary",
            "Non-responsibilities",
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, normalized)

        for contradictory in (
            "looks up endpoints",
            "enforces uniqueness",
            "evaluates risk limits",
            "proves execution eligibility",
            "accepts optional `None` inputs",
        ):
            with self.subTest(contradictory=contradictory):
                self.assertNotIn(contradictory, normalized)


if __name__ == "__main__":
    unittest.main()
