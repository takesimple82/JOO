import pathlib
import unittest
from dataclasses import FrozenInstanceError, fields
from typing import get_type_hints
from unittest.mock import patch

from EvidenceAggregation.models import (
    EvidenceAggregationItem,
    EvidenceAggregationMetadata,
)
from EvidenceAggregation.validation import (
    validate_evidence_aggregation_item,
)
from EvidenceAssessment.assessor import (
    ASSESSMENT_POLICY_VERSION,
)
from EvidenceAssessment.models import EvidenceAssessmentResult
from EvidenceProvenance.models import EvidenceProvenanceMetadata
from EvidenceValidation.models import (
    EvidenceValidationIssue,
    EvidenceValidationResult,
)
from ResearchDomain.models import ResearchFinding


def make_finding(**overrides) -> ResearchFinding:
    values = {
        "finding_id": "finding-001",
        "research_id": "research-001",
        "committee_id": "committee-001",
        "category": "financial",
        "statement": "Revenue increased.",
        "source": "Company filing",
        "event_date": "2026-07-01",
        "publication_date": "2026-07-02",
        "verification_status": "verified",
    }
    values.update(overrides)
    return ResearchFinding(**values)


def make_provenance(**overrides) -> EvidenceProvenanceMetadata:
    values = {
        "finding_id": "finding-001",
        "source_class": "primary",
    }
    values.update(overrides)
    return EvidenceProvenanceMetadata(**values)


def make_assessment(**overrides) -> EvidenceAssessmentResult:
    values = {
        "finding_id": "finding-001",
        "assessable": False,
        "policy_version": ASSESSMENT_POLICY_VERSION,
        "dimensions": (),
        "validation": EvidenceValidationResult(
            valid=False,
            issues=(
                EvidenceValidationIssue(
                    code="INVALID_EVENT_DATE",
                    message=(
                        "event_date must be a valid YYYY-MM-DD date"
                    ),
                ),
            ),
        ),
    }
    values.update(overrides)
    return EvidenceAssessmentResult(**values)


def make_metadata(**overrides) -> EvidenceAggregationMetadata:
    values = {
        "finding_id": "finding-001",
        "aggregation_key": "group-001",
        "source_reference_id": "source-reference-001",
    }
    values.update(overrides)
    return EvidenceAggregationMetadata(**values)


def make_item(**overrides) -> EvidenceAggregationItem:
    values = {
        "finding": make_finding(),
        "provenance": make_provenance(),
        "assessment": make_assessment(),
        "metadata": make_metadata(),
    }
    values.update(overrides)
    return EvidenceAggregationItem(**values)


class DerivedItem(EvidenceAggregationItem):
    pass


class DerivedFinding(ResearchFinding):
    pass


class DerivedProvenance(EvidenceProvenanceMetadata):
    pass


class DerivedAssessment(EvidenceAssessmentResult):
    pass


class DerivedMetadata(EvidenceAggregationMetadata):
    pass


class EvidenceAggregationItemTests(unittest.TestCase):
    def test_exact_model_contract_and_nested_identity(self):
        self.assertEqual(
            [field.name for field in fields(EvidenceAggregationItem)],
            ["finding", "provenance", "assessment", "metadata"],
        )
        self.assertEqual(
            get_type_hints(EvidenceAggregationItem),
            {
                "finding": ResearchFinding,
                "provenance": EvidenceProvenanceMetadata,
                "assessment": EvidenceAssessmentResult,
                "metadata": EvidenceAggregationMetadata,
            },
        )

        finding = make_finding()
        provenance = make_provenance()
        assessment = make_assessment()
        metadata = make_metadata()
        item = EvidenceAggregationItem(
            finding=finding,
            provenance=provenance,
            assessment=assessment,
            metadata=metadata,
        )

        self.assertIs(item.finding, finding)
        self.assertIs(item.provenance, provenance)
        self.assertIs(item.assessment, assessment)
        self.assertIs(item.metadata, metadata)

        with self.assertRaises(FrozenInstanceError):
            item.finding = make_finding()

    def test_valid_item_returns_none_without_mutation(self):
        item = make_item()
        finding_values = vars(item.finding).copy()
        item_values = vars(item).copy()
        validation = item.assessment.validation

        result = validate_evidence_aggregation_item(item)

        self.assertIsNone(result)
        self.assertEqual(vars(item.finding), finding_values)
        self.assertEqual(vars(item), item_values)
        self.assertIs(item.assessment.validation, validation)

    def test_exact_item_type_is_required(self):
        cases = (
            object(),
            DerivedItem(
                finding=make_finding(),
                provenance=make_provenance(),
                assessment=make_assessment(),
                metadata=make_metadata(),
            ),
        )

        for value in cases:
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    TypeError,
                    "^item must be EvidenceAggregationItem$",
                ):
                    validate_evidence_aggregation_item(value)

    def test_exact_nested_types_are_required_in_order(self):
        cases = (
            (
                {"finding": object()},
                "finding must be ResearchFinding",
            ),
            (
                {
                    "finding": object(),
                    "provenance": object(),
                },
                "finding must be ResearchFinding",
            ),
            (
                {"provenance": object()},
                "provenance must be EvidenceProvenanceMetadata",
            ),
            (
                {"assessment": object()},
                "assessment must be EvidenceAssessmentResult",
            ),
            (
                {"metadata": object()},
                "metadata must be EvidenceAggregationMetadata",
            ),
            (
                {
                    "finding": DerivedFinding(
                        **vars(make_finding())
                    )
                },
                "finding must be ResearchFinding",
            ),
            (
                {
                    "provenance": DerivedProvenance(
                        **vars(make_provenance())
                    )
                },
                "provenance must be EvidenceProvenanceMetadata",
            ),
            (
                {
                    "assessment": DerivedAssessment(
                        **vars(make_assessment())
                    )
                },
                "assessment must be EvidenceAssessmentResult",
            ),
            (
                {
                    "metadata": DerivedMetadata(
                        **vars(make_metadata())
                    )
                },
                "metadata must be EvidenceAggregationMetadata",
            ),
        )

        for overrides, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    TypeError,
                    f"^{message}$",
                ):
                    validate_evidence_aggregation_item(
                        make_item(**overrides)
                    )

    def test_upstream_validators_run_in_exact_order(self):
        calls = []

        with patch(
            "EvidenceAggregation.validation."
            "validate_research_finding",
            side_effect=lambda value: calls.append("finding"),
        ), patch(
            "EvidenceAggregation.validation."
            "validate_evidence_provenance",
            side_effect=lambda value: calls.append("provenance"),
        ), patch(
            "EvidenceAggregation.validation."
            "validate_evidence_aggregation_metadata",
            side_effect=lambda value: calls.append("metadata"),
        ):
            validate_evidence_aggregation_item(make_item())

        self.assertEqual(
            calls,
            ["finding", "provenance", "metadata"],
        )

    def test_upstream_exception_identity_stops_later_validation(self):
        error = ValueError("accepted upstream failure")
        calls = []

        with patch(
            "EvidenceAggregation.validation."
            "validate_research_finding",
            side_effect=error,
        ), patch(
            "EvidenceAggregation.validation."
            "validate_evidence_provenance",
            side_effect=lambda value: calls.append("provenance"),
        ), patch(
            "EvidenceAggregation.validation."
            "validate_evidence_aggregation_metadata",
            side_effect=lambda value: calls.append("metadata"),
        ):
            try:
                validate_evidence_aggregation_item(make_item())
            except ValueError as caught:
                self.assertIs(caught, error)
            else:
                self.fail("upstream exception did not propagate")

        self.assertEqual(calls, [])

    def test_assessment_consumed_field_types_are_validated_in_order(
        self,
    ):
        cases = (
            (
                {
                    "finding_id": None,
                    "policy_version": None,
                },
                "assessment finding_id must be str",
            ),
            (
                {"policy_version": None},
                "assessment policy_version must be str",
            ),
        )

        for overrides, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    TypeError,
                    f"^{message}$",
                ):
                    validate_evidence_aggregation_item(
                        make_item(
                            assessment=make_assessment(
                                **overrides
                            )
                        )
                    )

    def test_linkage_validation_is_deterministic(self):
        cases = (
            (
                {
                    "provenance": make_provenance(
                        finding_id="other"
                    ),
                    "assessment": make_assessment(
                        finding_id="other"
                    ),
                    "metadata": make_metadata(
                        finding_id="other"
                    ),
                },
                "provenance finding_id must match "
                "finding finding_id",
            ),
            (
                {
                    "assessment": make_assessment(
                        finding_id="other"
                    )
                },
                "assessment finding_id must match "
                "finding finding_id",
            ),
            (
                {
                    "metadata": make_metadata(
                        finding_id="other"
                    )
                },
                "aggregation metadata finding_id must match "
                "finding finding_id",
            ),
        )

        for overrides, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    ValueError,
                    f"^{message}$",
                ):
                    validate_evidence_aggregation_item(
                        make_item(**overrides)
                    )

    def test_policy_version_uses_accepted_constant(self):
        self.assertIsNone(
            validate_evidence_aggregation_item(make_item())
        )

        with self.assertRaisesRegex(
            ValueError,
            (
                "^assessment policy_version must be "
                f"{ASSESSMENT_POLICY_VERSION}$"
            ),
        ):
            validate_evidence_aggregation_item(
                make_item(
                    assessment=make_assessment(
                        policy_version="unsupported"
                    )
                )
            )

        validation_source = pathlib.Path(
            __file__
        ).parents[1].joinpath("validation.py").read_text()
        self.assertIn(
            "ASSESSMENT_POLICY_VERSION",
            validation_source,
        )
        self.assertNotIn(
            'ASSESSMENT_POLICY_VERSION = "1.0"',
            validation_source,
        )

    def test_unassessable_evidence_is_preserved_and_accepted(self):
        validation = EvidenceValidationResult(
            valid=False,
            issues=(
                EvidenceValidationIssue(
                    code="INVALID_EVENT_DATE",
                    message=(
                        "event_date must be a valid YYYY-MM-DD date"
                    ),
                ),
            ),
        )
        assessment = make_assessment(
            assessable=False,
            dimensions=(),
            validation=validation,
        )
        item = make_item(assessment=assessment)

        self.assertIsNone(
            validate_evidence_aggregation_item(item)
        )
        self.assertIs(item.assessment, assessment)
        self.assertIs(item.assessment.validation, validation)
        self.assertIs(item.assessment.assessable, False)
        self.assertEqual(item.assessment.dimensions, ())

    def test_assessment_internal_policy_is_not_recertified(self):
        validation = EvidenceValidationResult(
            valid=True,
            issues=(),
        )
        assessment = make_assessment(
            assessable=False,
            dimensions=(),
            validation=validation,
        )

        self.assertIsNone(
            validate_evidence_aggregation_item(
                make_item(assessment=assessment)
            )
        )

    def test_no_reconstruction_normalization_or_assessor_call(self):
        finding = make_finding(statement=" Exact statement ")
        provenance = make_provenance()
        assessment = make_assessment()
        metadata = make_metadata(
            aggregation_key=" group-001 ",
        )
        item = EvidenceAggregationItem(
            finding,
            provenance,
            assessment,
            metadata,
        )
        before = (
            vars(finding).copy(),
            vars(provenance).copy(),
            vars(assessment).copy(),
            vars(metadata).copy(),
        )

        with patch(
            "EvidenceAssessment.assessor.EvidenceAssessor",
        ) as assessor:
            validate_evidence_aggregation_item(item)

        assessor.assert_not_called()
        self.assertIs(item.finding, finding)
        self.assertIs(item.provenance, provenance)
        self.assertIs(item.assessment, assessment)
        self.assertIs(item.metadata, metadata)
        self.assertEqual(
            (
                vars(finding),
                vars(provenance),
                vars(assessment),
                vars(metadata),
            ),
            before,
        )
        self.assertEqual(
            item.metadata.aggregation_key,
            " group-001 ",
        )

    def test_dependency_and_feature_boundaries(self):
        package_root = pathlib.Path(__file__).parents[1]
        production_source = (
            package_root.joinpath("models.py").read_text()
            + package_root.joinpath("validation.py").read_text()
        )
        prohibited_dependencies = (
            "EvidenceValidation",
            "ResearchLogging",
            "ResearchOrchestrator",
            "PipelineRuntime",
            "CommitteeRuntime",
            "ExecutionEngine",
            "AIAdapter",
            "providers",
        )
        for dependency in prohibited_dependencies:
            with self.subTest(dependency=dependency):
                self.assertNotIn(
                    dependency,
                    production_source,
                )

        prohibited_symbols = (
            "class EvidenceAggregator",
            "AggregationRequest",
            "AggregationResult",
            "AcceptedRecord",
            "RejectedRecord",
            "DuplicateRecord",
            "corroboration",
            "contradiction",
            "score",
        )
        for symbol in prohibited_symbols:
            with self.subTest(symbol=symbol):
                self.assertNotIn(
                    symbol,
                    production_source,
                )


if __name__ == "__main__":
    unittest.main()
