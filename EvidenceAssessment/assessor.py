from EvidenceAssessment.models import (
    EvidenceAssessmentDimension,
    EvidenceAssessmentResult,
)
from EvidenceProvenance.models import EvidenceProvenanceMetadata
from EvidenceProvenance.validation import (
    validate_evidence_provenance,
)
from EvidenceValidation.validator import EvidenceValidator
from ResearchDomain.models import ResearchFinding


ASSESSMENT_POLICY_VERSION = "1.0"

_VERIFICATION_RATIONALES = {
    "verified": (
        "The finding is explicitly classified as verified."
    ),
    "partially_verified": (
        "The finding is explicitly classified as partially verified."
    ),
    "unverified": (
        "The finding is explicitly classified as unverified."
    ),
}

_SOURCE_CLASS_RATIONALES = {
    "primary": (
        "The source is explicitly classified as primary provenance."
    ),
    "secondary": (
        "The source is explicitly classified as secondary provenance."
    ),
    "unknown": (
        "The source provenance class is explicitly unknown."
    ),
}


class EvidenceAssessor:
    def assess(
        self,
        finding: ResearchFinding,
        provenance: EvidenceProvenanceMetadata,
    ) -> EvidenceAssessmentResult:
        validation = EvidenceValidator().validate(finding)
        validate_evidence_provenance(provenance)

        if provenance.finding_id != finding.finding_id:
            raise ValueError(
                "provenance finding_id must match finding finding_id"
            )

        if not validation.valid:
            return EvidenceAssessmentResult(
                finding_id=finding.finding_id,
                assessable=False,
                policy_version=ASSESSMENT_POLICY_VERSION,
                dimensions=(),
                validation=validation,
            )

        dimensions = (
            EvidenceAssessmentDimension(
                code="VERIFICATION_STATUS",
                value=finding.verification_status,
                rationale=_VERIFICATION_RATIONALES[
                    finding.verification_status
                ],
            ),
            EvidenceAssessmentDimension(
                code="SOURCE_CLASS",
                value=provenance.source_class,
                rationale=_SOURCE_CLASS_RATIONALES[
                    provenance.source_class
                ],
            ),
        )
        return EvidenceAssessmentResult(
            finding_id=finding.finding_id,
            assessable=True,
            policy_version=ASSESSMENT_POLICY_VERSION,
            dimensions=dimensions,
            validation=validation,
        )
