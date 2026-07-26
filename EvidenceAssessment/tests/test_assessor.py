import pathlib
import unittest
from dataclasses import FrozenInstanceError, fields
from typing import get_type_hints
from unittest.mock import Mock, patch

from EvidenceAssessment.assessor import (
    ASSESSMENT_POLICY_VERSION,
    EvidenceAssessor,
)
from EvidenceAssessment.models import (
    EvidenceAssessmentDimension,
    EvidenceAssessmentResult,
)
from EvidenceProvenance.models import EvidenceProvenanceMetadata
from EvidenceValidation.models import (
    EvidenceValidationIssue,
    EvidenceValidationResult,
)
from ResearchDomain.models import ResearchFinding


def make_finding(
    verification_status="verified",
    **overrides,
) -> ResearchFinding:
    values = {
        "finding_id": "finding-001",
        "research_id": "research-001",
        "committee_id": "committee-001",
        "category": "financial",
        "statement": "Revenue increased year over year.",
        "source": "Company filing",
        "event_date": "2026-07-01",
        "publication_date": "2026-07-15",
        "verification_status": verification_status,
    }
    values.update(overrides)
    return ResearchFinding(**values)


def make_provenance(
    source_class="primary",
    finding_id="finding-001",
) -> EvidenceProvenanceMetadata:
    return EvidenceProvenanceMetadata(
        finding_id=finding_id,
        source_class=source_class,
    )


class EvidenceAssessmentTests(unittest.TestCase):
    def test_exact_model_contracts(self):
        self.assertEqual(
            [field.name for field in fields(EvidenceAssessmentDimension)],
            ["code", "value", "rationale"],
        )
        self.assertEqual(
            get_type_hints(EvidenceAssessmentDimension),
            {
                "code": str,
                "value": str,
                "rationale": str,
            },
        )
        self.assertEqual(
            [field.name for field in fields(EvidenceAssessmentResult)],
            [
                "finding_id",
                "assessable",
                "policy_version",
                "dimensions",
                "validation",
            ],
        )
        self.assertEqual(
            get_type_hints(EvidenceAssessmentResult),
            {
                "finding_id": str,
                "assessable": bool,
                "policy_version": str,
                "dimensions": tuple[
                    EvidenceAssessmentDimension,
                    ...,
                ],
                "validation": EvidenceValidationResult,
            },
        )
        self.assertEqual(ASSESSMENT_POLICY_VERSION, "1.0")

    def test_models_are_frozen_hashable_and_require_tuple(self):
        dimension = EvidenceAssessmentDimension(
            code="VERIFICATION_STATUS",
            value="verified",
            rationale=(
                "The finding is explicitly classified as verified."
            ),
        )
        validation = EvidenceValidationResult(
            valid=True,
            issues=(),
        )
        result = EvidenceAssessmentResult(
            finding_id="finding-001",
            assessable=True,
            policy_version="1.0",
            dimensions=(dimension,),
            validation=validation,
        )

        with self.assertRaises(FrozenInstanceError):
            dimension.value = "unverified"
        with self.assertRaises(FrozenInstanceError):
            result.assessable = False
        with self.assertRaisesRegex(
            TypeError,
            "dimensions must be tuple",
        ):
            EvidenceAssessmentResult(
                finding_id="finding-001",
                assessable=True,
                policy_version="1.0",
                dimensions=[],
                validation=validation,
            )

        self.assertIsInstance(hash(dimension), int)
        self.assertIsInstance(hash(result), int)

    def test_assessable_combinations_preserve_exact_policy_values(self):
        verification_rationales = {
            "verified": (
                "The finding is explicitly classified as verified."
            ),
            "partially_verified": (
                "The finding is explicitly classified as "
                "partially verified."
            ),
            "unverified": (
                "The finding is explicitly classified as unverified."
            ),
        }
        source_rationales = {
            "primary": (
                "The source is explicitly classified as "
                "primary provenance."
            ),
            "secondary": (
                "The source is explicitly classified as "
                "secondary provenance."
            ),
            "unknown": (
                "The source provenance class is explicitly unknown."
            ),
        }

        for verification_status in verification_rationales:
            for source_class in source_rationales:
                with self.subTest(
                    verification_status=verification_status,
                    source_class=source_class,
                ):
                    result = EvidenceAssessor().assess(
                        make_finding(verification_status),
                        make_provenance(source_class),
                    )

                    self.assertIs(result.assessable, True)
                    self.assertEqual(result.policy_version, "1.0")
                    self.assertEqual(len(result.dimensions), 2)
                    self.assertEqual(
                        result.dimensions,
                        (
                            EvidenceAssessmentDimension(
                                code="VERIFICATION_STATUS",
                                value=verification_status,
                                rationale=(
                                    verification_rationales[
                                        verification_status
                                    ]
                                ),
                            ),
                            EvidenceAssessmentDimension(
                                code="SOURCE_CLASS",
                                value=source_class,
                                rationale=source_rationales[
                                    source_class
                                ],
                            ),
                        ),
                    )

    def test_validation_result_identity_is_preserved(self):
        validation = EvidenceValidationResult(
            valid=True,
            issues=(),
        )
        validator = Mock()
        validator.validate.return_value = validation

        with patch(
            "EvidenceAssessment.assessor.EvidenceValidator",
            return_value=validator,
        ):
            result = EvidenceAssessor().assess(
                make_finding(),
                make_provenance(),
            )

        self.assertIs(result.validation, validation)
        validator.validate.assert_called_once()

    def test_invalid_evidence_is_unassessable(self):
        cases = (
            {"event_date": "invalid"},
            {"publication_date": "invalid"},
            {
                "event_date": "2026-07-15",
                "publication_date": "2026-07-14",
            },
        )
        for overrides in cases:
            with self.subTest(overrides=overrides):
                result = EvidenceAssessor().assess(
                    make_finding(**overrides),
                    make_provenance(),
                )

                self.assertIs(result.assessable, False)
                self.assertEqual(result.dimensions, ())
                self.assertEqual(result.policy_version, "1.0")
                self.assertIs(result.validation.valid, False)

    def test_invalid_evidence_preserves_validation_identity(self):
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
        validator = Mock()
        validator.validate.return_value = validation

        with patch(
            "EvidenceAssessment.assessor.EvidenceValidator",
            return_value=validator,
        ):
            result = EvidenceAssessor().assess(
                make_finding(),
                make_provenance(),
            )

        self.assertIs(result.validation, validation)
        self.assertIs(result.assessable, False)
        self.assertEqual(result.dimensions, ())

    def test_domain_exception_identity_propagates_first(self):
        error = TypeError("finding must be ResearchFinding")
        validator = Mock()
        validator.validate.side_effect = error

        with patch(
            "EvidenceAssessment.assessor.EvidenceValidator",
            return_value=validator,
        ), patch(
            (
                "EvidenceAssessment.assessor."
                "validate_evidence_provenance"
            )
        ) as provenance_validator, patch(
            "EvidenceAssessment.assessor.EvidenceAssessmentResult"
        ) as result_model:
            try:
                EvidenceAssessor().assess(
                    object(),
                    make_provenance(),
                )
            except TypeError as caught:
                self.assertIs(caught, error)
            else:
                self.fail("domain exception did not propagate")

        validator.validate.assert_called_once()
        provenance_validator.assert_not_called()
        result_model.assert_not_called()

    def test_provenance_validation_runs_after_evidence_validation(self):
        call_order = []
        validation = EvidenceValidationResult(
            valid=True,
            issues=(),
        )
        validator = Mock()

        def validate_finding(value):
            call_order.append("evidence")
            return validation

        validator.validate.side_effect = validate_finding

        def validate_provenance(value):
            call_order.append("provenance")

        with patch(
            "EvidenceAssessment.assessor.EvidenceValidator",
            return_value=validator,
        ), patch(
            (
                "EvidenceAssessment.assessor."
                "validate_evidence_provenance"
            ),
            side_effect=validate_provenance,
        ):
            EvidenceAssessor().assess(
                make_finding(),
                make_provenance(),
            )

        self.assertEqual(call_order, ["evidence", "provenance"])

    def test_provenance_exception_identity_propagates(self):
        error = ValueError("invalid provenance")
        validation = EvidenceValidationResult(
            valid=True,
            issues=(),
        )
        validator = Mock()
        validator.validate.return_value = validation

        with patch(
            "EvidenceAssessment.assessor.EvidenceValidator",
            return_value=validator,
        ), patch(
            (
                "EvidenceAssessment.assessor."
                "validate_evidence_provenance"
            ),
            side_effect=error,
        ), patch(
            "EvidenceAssessment.assessor.EvidenceAssessmentResult"
        ) as result_model:
            try:
                EvidenceAssessor().assess(
                    make_finding(),
                    make_provenance(),
                )
            except ValueError as caught:
                self.assertIs(caught, error)
            else:
                self.fail("provenance exception did not propagate")

        validator.validate.assert_called_once()
        result_model.assert_not_called()

    def test_finding_id_mismatch_is_contract_error(self):
        with patch(
            "EvidenceAssessment.assessor.EvidenceAssessmentResult"
        ) as result_model:
            with self.assertRaisesRegex(
                ValueError,
                "provenance finding_id must match finding finding_id",
            ):
                EvidenceAssessor().assess(
                    make_finding(),
                    make_provenance(finding_id="finding-002"),
                )

        result_model.assert_not_called()

    def test_assessment_does_not_mutate_inputs_or_outputs(self):
        finding = make_finding()
        provenance = make_provenance()
        finding_values = vars(finding).copy()
        provenance_values = vars(provenance).copy()

        result = EvidenceAssessor().assess(finding, provenance)
        result_values = vars(result).copy()
        dimension_values = [
            vars(dimension).copy()
            for dimension in result.dimensions
        ]

        self.assertEqual(vars(finding), finding_values)
        self.assertEqual(vars(provenance), provenance_values)
        self.assertEqual(vars(result), result_values)
        self.assertEqual(
            [vars(item) for item in result.dimensions],
            dimension_values,
        )

    def test_no_inference_from_unapproved_finding_fields(self):
        first = EvidenceAssessor().assess(
            make_finding(
                source="Source A",
                statement="Short statement",
                category="category-a",
                committee_id="committee-a",
            ),
            make_provenance("secondary"),
        )
        second = EvidenceAssessor().assess(
            make_finding(
                source="Completely different source",
                statement="A substantially different statement",
                category="category-b",
                committee_id="committee-b",
            ),
            make_provenance("secondary"),
        )

        self.assertEqual(first.dimensions, second.dimensions)

    def test_public_boundaries_and_upstream_contracts(self):
        package_root = pathlib.Path(__file__).parents[1]
        source = (
            package_root.joinpath("models.py").read_text()
            + package_root.joinpath("assessor.py").read_text()
        )
        prohibited_names = (
            "ResearchLogging",
            "ResearchOrchestrator",
            "PipelineRuntime",
            "CommitteeRuntime",
            "ExecutionEngine",
            "AIAdapter",
            "providers",
            "score",
            "grade",
            "confidence",
            "rank",
            "recommendation",
            "corroboration",
        )
        for name in prohibited_names:
            with self.subTest(name=name):
                self.assertNotIn(name.lower(), source.lower())

        self.assertEqual(
            [field.name for field in fields(ResearchFinding)],
            [
                "finding_id",
                "research_id",
                "committee_id",
                "category",
                "statement",
                "source",
                "event_date",
                "publication_date",
                "verification_status",
            ],
        )
        self.assertEqual(
            [
                field.name
                for field in fields(EvidenceProvenanceMetadata)
            ],
            ["finding_id", "source_class"],
        )

        repository_root = package_root.parent
        upstream_roots = (
            repository_root / "ResearchDomain",
            repository_root / "EvidenceValidation",
            repository_root / "EvidenceProvenance",
        )
        for upstream_root in upstream_roots:
            for path in upstream_root.rglob("*.py"):
                self.assertNotIn(
                    "EvidenceAssessment",
                    path.read_text(),
                )


if __name__ == "__main__":
    unittest.main()
