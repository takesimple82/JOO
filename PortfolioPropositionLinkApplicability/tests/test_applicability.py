import ast
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from PortfolioDomain.models import PortfolioSubject
from PortfolioPropositionLink.models import (
    ExplicitPropositionPortfolioSubjectLink,
)
from PortfolioPropositionLinkApplicability.classification import (
    classify_explicit_proposition_portfolio_subject_link_applicability,
)
from PortfolioPropositionLinkApplicability.models import (
    PortfolioPropositionLinkApplicabilityStatus,
)


def make_proposition(
    **overrides,
) -> ExactObservedNumericProposition:
    values = {
        "proposition_id": "proposition-001",
        "finding_id": "finding-001",
        "subject_id": "evidence-subject-001",
        "predicate_id": "predicate-001",
        "value": Decimal("1.00"),
        "unit_id": "USD",
        "effective_context_id": "context-001",
    }
    values.update(overrides)
    return ExactObservedNumericProposition(**values)


def make_subject(**overrides) -> PortfolioSubject:
    values = {
        "subject_id": "portfolio-subject-001",
        "display_name": "Subject One",
    }
    values.update(overrides)
    return PortfolioSubject(**values)


def make_link(
    **overrides,
) -> ExplicitPropositionPortfolioSubjectLink:
    values = {
        "proposition_id": "proposition-001",
        "portfolio_subject_id": "portfolio-subject-001",
    }
    values.update(overrides)
    return ExplicitPropositionPortfolioSubjectLink(**values)


class PortfolioPropositionLinkApplicabilityTests(
    unittest.TestCase
):
    def test_exact_enum_contract(self):
        self.assertEqual(
            PortfolioPropositionLinkApplicabilityStatus.__members__,
            {
                "PROPOSITION_ENDPOINT_MISMATCH": (
                    PortfolioPropositionLinkApplicabilityStatus
                    .PROPOSITION_ENDPOINT_MISMATCH
                ),
                "PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH": (
                    PortfolioPropositionLinkApplicabilityStatus
                    .PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH
                ),
                "APPLICABLE": (
                    PortfolioPropositionLinkApplicabilityStatus
                    .APPLICABLE
                ),
            },
        )
        self.assertEqual(
            [
                status.value
                for status in
                PortfolioPropositionLinkApplicabilityStatus
            ],
            [
                "proposition_endpoint_mismatch",
                "portfolio_subject_endpoint_mismatch",
                "applicable",
            ],
        )

    def test_integrated_applicable_link(self):
        self.assertIs(
            classify_explicit_proposition_portfolio_subject_link_applicability(
                make_proposition(),
                make_subject(),
                make_link(),
            ),
            PortfolioPropositionLinkApplicabilityStatus.APPLICABLE,
        )

    def test_integrated_proposition_endpoint_mismatch(self):
        self.assertIs(
            classify_explicit_proposition_portfolio_subject_link_applicability(
                make_proposition(proposition_id="other"),
                make_subject(),
                make_link(),
            ),
            (
                PortfolioPropositionLinkApplicabilityStatus
                .PROPOSITION_ENDPOINT_MISMATCH
            ),
        )

    def test_integrated_portfolio_subject_endpoint_mismatch(self):
        self.assertIs(
            classify_explicit_proposition_portfolio_subject_link_applicability(
                make_proposition(),
                make_subject(subject_id="other"),
                make_link(),
            ),
            (
                PortfolioPropositionLinkApplicabilityStatus
                .PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH
            ),
        )

    def test_proposition_mismatch_takes_precedence(self):
        self.assertIs(
            classify_explicit_proposition_portfolio_subject_link_applicability(
                make_proposition(proposition_id="other"),
                make_subject(subject_id="other"),
                make_link(),
            ),
            (
                PortfolioPropositionLinkApplicabilityStatus
                .PROPOSITION_ENDPOINT_MISMATCH
            ),
        )

    def test_evidence_subject_id_does_not_participate(self):
        for evidence_subject_id in (
            "portfolio-subject-001",
            "different-subject",
        ):
            with self.subTest(
                evidence_subject_id=evidence_subject_id
            ):
                self.assertIs(
                    classify_explicit_proposition_portfolio_subject_link_applicability(
                        make_proposition(
                            subject_id=evidence_subject_id
                        ),
                        make_subject(),
                        make_link(),
                    ),
                    (
                        PortfolioPropositionLinkApplicabilityStatus
                        .APPLICABLE
                    ),
                )

    def test_exact_identifier_matching_without_normalization(self):
        cases = (
            (
                make_proposition(proposition_id="PROPOSITION-001"),
                make_subject(),
                make_link(),
                (
                    PortfolioPropositionLinkApplicabilityStatus
                    .PROPOSITION_ENDPOINT_MISMATCH
                ),
            ),
            (
                make_proposition(),
                make_subject(subject_id=" portfolio-subject-001 "),
                make_link(),
                (
                    PortfolioPropositionLinkApplicabilityStatus
                    .PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH
                ),
            ),
            (
                make_proposition(proposition_id="\u00e9"),
                make_subject(),
                make_link(proposition_id="e\u0301"),
                (
                    PortfolioPropositionLinkApplicabilityStatus
                    .PROPOSITION_ENDPOINT_MISMATCH
                ),
            ),
        )

        for proposition, subject, link, expected in cases:
            with self.subTest(expected=expected):
                self.assertIs(
                    classify_explicit_proposition_portfolio_subject_link_applicability(
                        proposition,
                        subject,
                        link,
                    ),
                    expected,
                )

    def test_upstream_validators_run_once_in_exact_order(self):
        proposition = make_proposition()
        subject = make_subject()
        link = make_link()
        calls = []

        with patch(
            "PortfolioPropositionLinkApplicability"
            ".classification"
            ".validate_explicit_proposition_portfolio_subject_link",
            side_effect=lambda value: calls.append(
                ("link", value)
            ),
        ) as link_validator, patch(
            "PortfolioPropositionLinkApplicability"
            ".classification"
            ".validate_exact_observed_numeric_proposition",
            side_effect=lambda value: calls.append(
                ("proposition", value)
            ),
        ) as proposition_validator, patch(
            "PortfolioPropositionLinkApplicability"
            ".classification"
            ".validate_portfolio_subject",
            side_effect=lambda value: calls.append(
                ("subject", value)
            ),
        ) as subject_validator:
            result = (
                classify_explicit_proposition_portfolio_subject_link_applicability(
                    proposition,
                    subject,
                    link,
                )
            )

        self.assertIs(
            result,
            PortfolioPropositionLinkApplicabilityStatus.APPLICABLE,
        )
        self.assertEqual(
            calls,
            [
                ("link", link),
                ("proposition", proposition),
                ("subject", subject),
            ],
        )
        link_validator.assert_called_once_with(link)
        proposition_validator.assert_called_once_with(proposition)
        subject_validator.assert_called_once_with(subject)

    def test_link_failure_stops_later_validation(self):
        error = TypeError("link failure")

        with patch(
            "PortfolioPropositionLinkApplicability"
            ".classification"
            ".validate_explicit_proposition_portfolio_subject_link",
            side_effect=error,
        ), patch(
            "PortfolioPropositionLinkApplicability"
            ".classification"
            ".validate_exact_observed_numeric_proposition",
        ) as proposition_validator, patch(
            "PortfolioPropositionLinkApplicability"
            ".classification"
            ".validate_portfolio_subject",
        ) as subject_validator:
            with self.assertRaises(TypeError) as context:
                classify_explicit_proposition_portfolio_subject_link_applicability(
                    make_proposition(),
                    make_subject(),
                    make_link(),
                )

        self.assertIs(context.exception, error)
        proposition_validator.assert_not_called()
        subject_validator.assert_not_called()

    def test_proposition_failure_stops_subject_validation(self):
        error = ValueError("proposition failure")

        with patch(
            "PortfolioPropositionLinkApplicability"
            ".classification"
            ".validate_exact_observed_numeric_proposition",
            side_effect=error,
        ), patch(
            "PortfolioPropositionLinkApplicability"
            ".classification"
            ".validate_portfolio_subject",
        ) as subject_validator:
            with self.assertRaises(ValueError) as context:
                classify_explicit_proposition_portfolio_subject_link_applicability(
                    make_proposition(),
                    make_subject(),
                    make_link(),
                )

        self.assertIs(context.exception, error)
        subject_validator.assert_not_called()

    def test_subject_failure_propagates_unchanged(self):
        error = TypeError("subject failure")

        with patch(
            "PortfolioPropositionLinkApplicability"
            ".classification"
            ".validate_portfolio_subject",
            side_effect=error,
        ):
            with self.assertRaises(TypeError) as context:
                classify_explicit_proposition_portfolio_subject_link_applicability(
                    make_proposition(),
                    make_subject(),
                    make_link(),
                )

        self.assertIs(context.exception, error)

    def test_inputs_and_field_objects_are_preserved(self):
        proposition_id = " proposition-\u00e9 "
        portfolio_subject_id = " subject-e\u0301 "
        proposition = make_proposition(
            proposition_id=proposition_id
        )
        subject = make_subject(
            subject_id=portfolio_subject_id
        )
        link = make_link(
            proposition_id=proposition_id,
            portfolio_subject_id=portfolio_subject_id,
        )
        input_ids = (
            id(proposition),
            id(subject),
            id(link),
        )

        result = (
            classify_explicit_proposition_portfolio_subject_link_applicability(
                proposition,
                subject,
                link,
            )
        )

        self.assertIs(
            result,
            PortfolioPropositionLinkApplicabilityStatus.APPLICABLE,
        )
        self.assertEqual(
            (
                id(proposition),
                id(subject),
                id(link),
            ),
            input_ids,
        )
        self.assertIs(proposition.proposition_id, proposition_id)
        self.assertIs(subject.subject_id, portfolio_subject_id)
        self.assertIs(link.proposition_id, proposition_id)
        self.assertIs(
            link.portfolio_subject_id,
            portfolio_subject_id,
        )

    def test_production_structure_and_dependency_direction(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (root / "models.py").read_text()
        )
        classification_tree = ast.parse(
            (root / "classification.py").read_text()
        )

        model_imports = [
            node
            for node in ast.walk(model_tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        self.assertEqual(len(model_imports), 1)
        self.assertEqual(model_imports[0].module, "enum")

        imported_modules = {
            node.module
            for node in ast.walk(classification_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            imported_modules,
            {
                "EvidenceProposition.models",
                "EvidenceProposition.validation",
                "PortfolioDomain.models",
                "PortfolioDomain.validation",
                "PortfolioPropositionLink.models",
                "PortfolioPropositionLink.validation",
                "PortfolioPropositionLinkApplicability.models",
            },
        )

        functions = [
            node
            for node in classification_tree.body
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            )
        ]
        self.assertEqual(
            [function.name for function in functions],
            [
                "classify_explicit_proposition_portfolio_subject_link_applicability"
            ],
        )
        self.assertFalse(
            any(
                isinstance(node, (ast.For, ast.While))
                for node in ast.walk(classification_tree)
            )
        )

        repository_root = root.parent
        upstream_directories = (
            "EvidenceProposition",
            "PortfolioDomain",
            "PortfolioPropositionLink",
        )
        for directory in upstream_directories:
            for path in (
                repository_root / directory
            ).glob("*.py"):
                self.assertNotIn(
                    "PortfolioPropositionLinkApplicability",
                    path.read_text(),
                )


if __name__ == "__main__":
    unittest.main()
