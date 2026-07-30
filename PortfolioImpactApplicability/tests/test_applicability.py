import ast
import unittest
from pathlib import Path
from unittest.mock import patch

from ExplicitThesis.models import ExplicitThesis
from PortfolioDomain.models import PortfolioSubject
from PortfolioImpactApplicability.classification import (
    classify_portfolio_impact_applicability,
)
from PortfolioImpactApplicability.models import (
    PortfolioImpactApplicabilityStatus,
)
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)
from ThesisPortfolioSubjectLink.models import (
    ExplicitThesisPortfolioSubjectLink,
)


def make_semantic_thesis(thesis_id="thesis-001"):
    return SemanticallyProducedThesis(
        ExplicitThesis(thesis_id, "A semantic Thesis.")
    )


def make_link(**overrides):
    values = {
        "thesis_id": "thesis-001",
        "portfolio_subject_id": "subject-001",
    }
    values.update(overrides)
    return ExplicitThesisPortfolioSubjectLink(**values)


def make_subject(**overrides):
    values = {
        "subject_id": "subject-001",
        "display_name": "Subject One",
    }
    values.update(overrides)
    return PortfolioSubject(**values)


class PortfolioImpactApplicabilityTests(unittest.TestCase):
    def test_exact_status_contract(self):
        self.assertEqual(
            PortfolioImpactApplicabilityStatus.__members__,
            {
                "APPLICABLE": (
                    PortfolioImpactApplicabilityStatus.APPLICABLE
                ),
                "THESIS_ENDPOINT_MISMATCH": (
                    PortfolioImpactApplicabilityStatus
                    .THESIS_ENDPOINT_MISMATCH
                ),
                "PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH": (
                    PortfolioImpactApplicabilityStatus
                    .PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH
                ),
            },
        )
        self.assertEqual(
            [
                status.value
                for status in PortfolioImpactApplicabilityStatus
            ],
            [
                "applicable",
                "thesis_endpoint_mismatch",
                "portfolio_subject_endpoint_mismatch",
            ],
        )

    def test_applicable(self):
        self.assertIs(
            classify_portfolio_impact_applicability(
                make_semantic_thesis(),
                make_link(),
                make_subject(),
            ),
            PortfolioImpactApplicabilityStatus.APPLICABLE,
        )

    def test_thesis_endpoint_mismatch(self):
        self.assertIs(
            classify_portfolio_impact_applicability(
                make_semantic_thesis("other-thesis"),
                make_link(),
                make_subject(),
            ),
            (
                PortfolioImpactApplicabilityStatus
                .THESIS_ENDPOINT_MISMATCH
            ),
        )

    def test_portfolio_subject_endpoint_mismatch(self):
        self.assertIs(
            classify_portfolio_impact_applicability(
                make_semantic_thesis(),
                make_link(),
                make_subject(subject_id="other-subject"),
            ),
            (
                PortfolioImpactApplicabilityStatus
                .PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH
            ),
        )

    def test_thesis_mismatch_has_precedence(self):
        self.assertIs(
            classify_portfolio_impact_applicability(
                make_semantic_thesis("other-thesis"),
                make_link(),
                make_subject(subject_id="other-subject"),
            ),
            (
                PortfolioImpactApplicabilityStatus
                .THESIS_ENDPOINT_MISMATCH
            ),
        )

    def test_exact_identifier_matching(self):
        cases = (
            (
                make_semantic_thesis("THESIS-001"),
                make_link(),
                make_subject(),
                PortfolioImpactApplicabilityStatus
                .THESIS_ENDPOINT_MISMATCH,
            ),
            (
                make_semantic_thesis("\u00e9"),
                make_link(thesis_id="e\u0301"),
                make_subject(),
                PortfolioImpactApplicabilityStatus
                .THESIS_ENDPOINT_MISMATCH,
            ),
            (
                make_semantic_thesis(),
                make_link(),
                make_subject(subject_id=" subject-001 "),
                PortfolioImpactApplicabilityStatus
                .PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH,
            ),
        )
        for thesis, link, subject, expected in cases:
            with self.subTest(expected=expected):
                self.assertIs(
                    classify_portfolio_impact_applicability(
                        thesis,
                        link,
                        subject,
                    ),
                    expected,
                )

    def test_upstream_validators_run_once_in_order(self):
        thesis = make_semantic_thesis()
        link = make_link()
        subject = make_subject()
        calls = []

        with patch(
            "PortfolioImpactApplicability.classification"
            ".validate_semantically_produced_thesis",
            side_effect=lambda value: calls.append(
                ("semantic_thesis", value)
            ),
        ) as thesis_validator, patch(
            "PortfolioImpactApplicability.classification"
            ".validate_explicit_thesis_portfolio_subject_link",
            side_effect=lambda value: calls.append(
                ("link", value)
            ),
        ) as link_validator, patch(
            "PortfolioImpactApplicability.classification"
            ".validate_portfolio_subject",
            side_effect=lambda value: calls.append(
                ("portfolio_subject", value)
            ),
        ) as subject_validator:
            result = classify_portfolio_impact_applicability(
                thesis,
                link,
                subject,
            )

        self.assertIs(
            result,
            PortfolioImpactApplicabilityStatus.APPLICABLE,
        )
        self.assertEqual(
            calls,
            [
                ("semantic_thesis", thesis),
                ("link", link),
                ("portfolio_subject", subject),
            ],
        )
        thesis_validator.assert_called_once_with(thesis)
        link_validator.assert_called_once_with(link)
        subject_validator.assert_called_once_with(subject)

    def test_semantic_thesis_failure_stops_validation(self):
        error = TypeError("semantic thesis failure")
        with patch(
            "PortfolioImpactApplicability.classification"
            ".validate_semantically_produced_thesis",
            side_effect=error,
        ), patch(
            "PortfolioImpactApplicability.classification"
            ".validate_explicit_thesis_portfolio_subject_link",
        ) as link_validator, patch(
            "PortfolioImpactApplicability.classification"
            ".validate_portfolio_subject",
        ) as subject_validator:
            with self.assertRaises(TypeError) as context:
                classify_portfolio_impact_applicability(
                    make_semantic_thesis(),
                    make_link(),
                    make_subject(),
                )
        self.assertIs(context.exception, error)
        link_validator.assert_not_called()
        subject_validator.assert_not_called()

    def test_link_failure_stops_subject_validation(self):
        error = ValueError("link failure")
        with patch(
            "PortfolioImpactApplicability.classification"
            ".validate_explicit_thesis_portfolio_subject_link",
            side_effect=error,
        ), patch(
            "PortfolioImpactApplicability.classification"
            ".validate_portfolio_subject",
        ) as subject_validator:
            with self.assertRaises(ValueError) as context:
                classify_portfolio_impact_applicability(
                    make_semantic_thesis(),
                    make_link(),
                    make_subject(),
                )
        self.assertIs(context.exception, error)
        subject_validator.assert_not_called()

    def test_subject_failure_propagates_unchanged(self):
        error = TypeError("subject failure")
        with patch(
            "PortfolioImpactApplicability.classification"
            ".validate_portfolio_subject",
            side_effect=error,
        ):
            with self.assertRaises(TypeError) as context:
                classify_portfolio_impact_applicability(
                    make_semantic_thesis(),
                    make_link(),
                    make_subject(),
                )
        self.assertIs(context.exception, error)

    def test_inputs_and_fields_are_preserved(self):
        thesis_id = " thesis-\u00e9 "
        subject_id = " subject-e\u0301 "
        thesis = make_semantic_thesis(thesis_id)
        link = make_link(
            thesis_id=thesis_id,
            portfolio_subject_id=subject_id,
        )
        subject = make_subject(subject_id=subject_id)

        self.assertIs(
            classify_portfolio_impact_applicability(
                thesis,
                link,
                subject,
            ),
            PortfolioImpactApplicabilityStatus.APPLICABLE,
        )
        self.assertIs(thesis.thesis.thesis_id, thesis_id)
        self.assertIs(link.thesis_id, thesis_id)
        self.assertIs(link.portfolio_subject_id, subject_id)
        self.assertIs(subject.subject_id, subject_id)

    def test_dependency_direction_and_public_surface(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (root / "models.py").read_text()
        )
        classification_tree = ast.parse(
            (root / "classification.py").read_text()
        )

        model_imports = [
            node.module
            for node in ast.walk(model_tree)
            if isinstance(node, ast.ImportFrom)
        ]
        self.assertEqual(model_imports, ["enum"])

        imported_modules = {
            node.module
            for node in ast.walk(classification_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            imported_modules,
            {
                "PortfolioDomain.models",
                "PortfolioDomain.validation",
                "PortfolioImpactApplicability.models",
                "SemanticThesisProduction.models",
                "SemanticThesisProduction.validation",
                "ThesisPortfolioSubjectLink.models",
                "ThesisPortfolioSubjectLink.validation",
            },
        )
        functions = [
            node.name
            for node in classification_tree.body
            if isinstance(node, ast.FunctionDef)
        ]
        self.assertEqual(
            functions,
            ["classify_portfolio_impact_applicability"],
        )


if __name__ == "__main__":
    unittest.main()
