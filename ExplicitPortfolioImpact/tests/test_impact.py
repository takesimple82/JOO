import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from ExplicitPortfolioImpact.models import (
    ExplicitPortfolioImpact,
)
from ExplicitPortfolioImpact.validation import (
    validate_explicit_portfolio_impact,
)
from ExplicitThesis.models import ExplicitThesis
from PortfolioDomain.models import PortfolioSubject
from PortfolioImpactApplicability.models import (
    PortfolioImpactApplicabilityStatus,
)
from PortfolioImpactInterpretationPolicy.models import (
    PortfolioImpactDirection,
    PortfolioImpactInterpretationPolicy,
    PortfolioImpactInterpretationPolicyApplicabilityStatus,
)
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)
from ThesisPortfolioSubjectLink.models import (
    ExplicitThesisPortfolioSubjectLink,
)


def make_thesis(thesis_id="thesis-001"):
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


def make_policy(**overrides):
    values = {
        "policy_id": "policy-001",
        "policy_version": "version-001",
        "allowed_directions": (
            PortfolioImpactDirection.BENEFICIAL,
            PortfolioImpactDirection.NEUTRAL,
            PortfolioImpactDirection.ADVERSE,
        ),
        "allowed_horizon_ids": ("long-term",),
        "rationale_required": True,
    }
    values.update(overrides)
    return PortfolioImpactInterpretationPolicy(**values)


def make_impact(**overrides):
    values = {
        "impact_id": "impact-001",
        "semantic_thesis": make_thesis(),
        "link": make_link(),
        "portfolio_subject": make_subject(),
        "policy": make_policy(),
        "direction": PortfolioImpactDirection.BENEFICIAL,
        "horizon_id": "long-term",
        "rationale": "Caller-supplied rationale.",
    }
    values.update(overrides)
    return ExplicitPortfolioImpact(**values)


class StringSubclass(str):
    pass


class ImpactSubclass(ExplicitPortfolioImpact):
    pass


class ExplicitPortfolioImpactTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(ExplicitPortfolioImpact)
        self.assertEqual(
            [field.name for field in model_fields],
            [
                "impact_id",
                "semantic_thesis",
                "link",
                "portfolio_subject",
                "policy",
                "direction",
                "horizon_id",
                "rationale",
            ],
        )
        self.assertEqual(
            get_type_hints(ExplicitPortfolioImpact),
            {
                "impact_id": str,
                "semantic_thesis": SemanticallyProducedThesis,
                "link": ExplicitThesisPortfolioSubjectLink,
                "portfolio_subject": PortfolioSubject,
                "policy": PortfolioImpactInterpretationPolicy,
                "direction": PortfolioImpactDirection,
                "horizon_id": str,
                "rationale": str,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__slots__",
            ExplicitPortfolioImpact.__dict__,
        )

    def test_frozen_hashable_structural_equality(self):
        first = make_impact()
        same = make_impact()
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        with self.assertRaises(FrozenInstanceError):
            first.impact_id = "replacement"

    def test_exact_impact_and_identifier_contract(self):
        with self.assertRaisesRegex(
            TypeError,
            "^impact must be ExplicitPortfolioImpact$",
        ):
            validate_explicit_portfolio_impact(
                ImpactSubclass(
                    **{
                        field.name: getattr(make_impact(), field.name)
                        for field in fields(ExplicitPortfolioImpact)
                    }
                )
            )
        cases = (
            (
                make_impact(impact_id=None),
                TypeError,
                "impact_id must be str",
            ),
            (
                make_impact(
                    impact_id=StringSubclass("impact")
                ),
                TypeError,
                "impact_id must be str",
            ),
            (
                make_impact(impact_id=" \t "),
                ValueError,
                "impact_id must not be blank",
            ),
        )
        for impact, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_impact(impact)

    def test_exact_upstream_field_types(self):
        cases = (
            (
                "semantic_thesis",
                None,
                "semantic_thesis must be "
                "SemanticallyProducedThesis",
            ),
            (
                "link",
                None,
                "link must be "
                "ExplicitThesisPortfolioSubjectLink",
            ),
            (
                "portfolio_subject",
                None,
                "portfolio_subject must be PortfolioSubject",
            ),
            (
                "policy",
                None,
                "policy must be "
                "PortfolioImpactInterpretationPolicy",
            ),
        )
        for field_name, value, message in cases:
            with self.subTest(field_name=field_name):
                with self.assertRaisesRegex(
                    TypeError,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_impact(
                        make_impact(**{field_name: value})
                    )

    def test_scalar_interpretation_field_types(self):
        cases = (
            (
                make_impact(direction=None),
                TypeError,
                "direction must be PortfolioImpactDirection",
            ),
            (
                make_impact(horizon_id=None),
                TypeError,
                "horizon_id must be str",
            ),
            (
                make_impact(
                    horizon_id=StringSubclass("long-term")
                ),
                TypeError,
                "horizon_id must be str",
            ),
            (
                make_impact(horizon_id=" "),
                ValueError,
                "horizon_id must not be blank",
            ),
            (
                make_impact(rationale=None),
                TypeError,
                "rationale must be str",
            ),
            (
                make_impact(
                    rationale=StringSubclass("rationale")
                ),
                TypeError,
                "rationale must be str",
            ),
        )
        for impact, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_impact(impact)

    def test_upstream_validators_run_once_in_order(self):
        impact = make_impact()
        calls = []
        patches = (
            patch(
                "ExplicitPortfolioImpact.validation"
                ".validate_semantically_produced_thesis",
                side_effect=lambda value: calls.append(
                    ("semantic_thesis", value)
                ),
            ),
            patch(
                "ExplicitPortfolioImpact.validation"
                ".validate_explicit_thesis_portfolio_subject_link",
                side_effect=lambda value: calls.append(
                    ("link", value)
                ),
            ),
            patch(
                "ExplicitPortfolioImpact.validation"
                ".validate_portfolio_subject",
                side_effect=lambda value: calls.append(
                    ("portfolio_subject", value)
                ),
            ),
            patch(
                "ExplicitPortfolioImpact.validation"
                ".validate_portfolio_impact_interpretation_policy",
                side_effect=lambda value: calls.append(
                    ("policy", value)
                ),
            ),
        )
        with patches[0] as thesis_validator, (
            patches[1]
        ) as link_validator, patches[2] as subject_validator, (
            patches[3]
        ) as policy_validator:
            result = validate_explicit_portfolio_impact(impact)

        self.assertIsNone(result)
        self.assertEqual(
            calls,
            [
                ("semantic_thesis", impact.semantic_thesis),
                ("link", impact.link),
                ("portfolio_subject", impact.portfolio_subject),
                ("policy", impact.policy),
            ],
        )
        thesis_validator.assert_called_once_with(
            impact.semantic_thesis
        )
        link_validator.assert_called_once_with(impact.link)
        subject_validator.assert_called_once_with(
            impact.portfolio_subject
        )
        policy_validator.assert_called_once_with(impact.policy)

    def test_upstream_exception_propagates_and_stops(self):
        impact = make_impact()
        error = ValueError("semantic thesis failure")
        with patch(
            "ExplicitPortfolioImpact.validation"
            ".validate_semantically_produced_thesis",
            side_effect=error,
        ), patch(
            "ExplicitPortfolioImpact.validation"
            ".validate_explicit_thesis_portfolio_subject_link",
        ) as link_validator:
            with self.assertRaises(ValueError) as context:
                validate_explicit_portfolio_impact(impact)
        self.assertIs(context.exception, error)
        link_validator.assert_not_called()

    def test_endpoint_failure_mapping_and_precedence(self):
        cases = (
            (
                make_impact(
                    semantic_thesis=make_thesis("other"),
                    portfolio_subject=make_subject(
                        subject_id="other"
                    ),
                ),
                "semantic_thesis thesis_id must match "
                "link thesis_id",
            ),
            (
                make_impact(
                    portfolio_subject=make_subject(
                        subject_id="other"
                    )
                ),
                "portfolio_subject subject_id must match "
                "link portfolio_subject_id",
            ),
        )
        for impact, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    ValueError,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_impact(impact)

    def test_policy_failure_mapping_and_precedence(self):
        policy = make_policy(
            allowed_directions=(
                PortfolioImpactDirection.NEUTRAL,
            ),
            allowed_horizon_ids=("allowed",),
            rationale_required=True,
        )
        cases = (
            (
                make_impact(
                    policy=policy,
                    direction=PortfolioImpactDirection.ADVERSE,
                    horizon_id="other",
                    rationale="",
                ),
                "direction must be allowed by policy",
            ),
            (
                make_impact(
                    policy=policy,
                    direction=PortfolioImpactDirection.NEUTRAL,
                    horizon_id="other",
                    rationale="",
                ),
                "horizon_id must be allowed by policy",
            ),
            (
                make_impact(
                    policy=policy,
                    direction=PortfolioImpactDirection.NEUTRAL,
                    horizon_id="allowed",
                    rationale=" ",
                ),
                "rationale must not be blank when policy "
                "requires rationale",
            ),
        )
        for impact, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    ValueError,
                    f"^{message}$",
                ):
                    validate_explicit_portfolio_impact(impact)

    def test_blank_rationale_allowed_by_policy(self):
        impact = make_impact(
            policy=make_policy(rationale_required=False),
            rationale=" \t ",
        )
        self.assertIsNone(
            validate_explicit_portfolio_impact(impact)
        )

    def test_private_classifiers_receive_validated_objects(self):
        impact = make_impact()
        with patch(
            "ExplicitPortfolioImpact.validation"
            "._classify_portfolio_impact_applicability_unchecked",
            return_value=(
                PortfolioImpactApplicabilityStatus.APPLICABLE
            ),
        ) as endpoint_classifier, patch(
            "ExplicitPortfolioImpact.validation"
            "._classify_portfolio_impact_interpretation_policy_applicability_unchecked",
            return_value=(
                PortfolioImpactInterpretationPolicyApplicabilityStatus
                .APPLICABLE
            ),
        ) as policy_classifier:
            result = validate_explicit_portfolio_impact(impact)
        self.assertIsNone(result)
        endpoint_classifier.assert_called_once_with(
            impact.semantic_thesis,
            impact.link,
            impact.portfolio_subject,
        )
        policy_classifier.assert_called_once_with(
            impact.policy,
            impact.direction,
            impact.horizon_id,
            impact.rationale,
        )

    def test_full_object_and_string_identity_preserved(self):
        impact_id = " impact-\u00e9 "
        horizon_id = " horizon-e\u0301 "
        rationale = " rationale-\u00e9 "
        thesis = make_thesis()
        link = make_link()
        subject = make_subject()
        policy = make_policy(
            allowed_horizon_ids=(horizon_id,)
        )
        impact = ExplicitPortfolioImpact(
            impact_id,
            thesis,
            link,
            subject,
            policy,
            PortfolioImpactDirection.BENEFICIAL,
            horizon_id,
            rationale,
        )
        self.assertIsNone(
            validate_explicit_portfolio_impact(impact)
        )
        self.assertIs(impact.impact_id, impact_id)
        self.assertIs(impact.semantic_thesis, thesis)
        self.assertIs(impact.link, link)
        self.assertIs(impact.portfolio_subject, subject)
        self.assertIs(impact.policy, policy)
        self.assertIs(impact.horizon_id, horizon_id)
        self.assertIs(impact.rationale, rationale)

    def test_cardinality_and_conflicts_are_not_rejected(self):
        first = make_impact()
        same_endpoints = make_impact(
            impact_id="impact-002",
            direction=PortfolioImpactDirection.ADVERSE,
        )
        same_content_new_identity = make_impact(
            impact_id="impact-003"
        )
        for impact in (
            first,
            same_endpoints,
            same_content_new_identity,
        ):
            self.assertIsNone(
                validate_explicit_portfolio_impact(impact)
            )
        self.assertNotEqual(first, same_endpoints)
        self.assertNotEqual(first, same_content_new_identity)

    def test_dependency_direction_and_public_surface(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (root / "models.py").read_text()
        )
        validation_tree = ast.parse(
            (root / "validation.py").read_text()
        )
        functions = [
            node.name
            for node in validation_tree.body
            if isinstance(node, ast.FunctionDef)
        ]
        self.assertEqual(
            functions,
            ["validate_explicit_portfolio_impact"],
        )
        model_modules = {
            node.module
            for node in ast.walk(model_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            model_modules,
            {
                "dataclasses",
                "PortfolioDomain.models",
                "PortfolioImpactInterpretationPolicy.models",
                "SemanticThesisProduction.models",
                "ThesisPortfolioSubjectLink.models",
            },
        )


if __name__ == "__main__":
    unittest.main()
