from EvidenceAssessment.assessor import (
    ASSESSMENT_POLICY_VERSION,
)
from EvidenceAssessment.models import EvidenceAssessmentResult
from EvidenceAggregation.models import (
    EvidenceAggregationItem,
    EvidenceAggregationMetadata,
)
from EvidenceProvenance.models import EvidenceProvenanceMetadata
from EvidenceProvenance.validation import (
    validate_evidence_provenance,
)
from ResearchDomain.models import ResearchFinding
from ResearchDomain.validation import validate_research_finding


def validate_evidence_aggregation_metadata(
    metadata: EvidenceAggregationMetadata,
) -> None:
    if type(metadata) is not EvidenceAggregationMetadata:
        raise TypeError(
            "metadata must be EvidenceAggregationMetadata"
        )

    _require_nonblank_string(
        "finding_id",
        metadata.finding_id,
    )
    _require_nonblank_string(
        "aggregation_key",
        metadata.aggregation_key,
    )
    _require_nonblank_string(
        "source_reference_id",
        metadata.source_reference_id,
    )


def validate_evidence_aggregation_item(
    item: EvidenceAggregationItem,
) -> None:
    if type(item) is not EvidenceAggregationItem:
        raise TypeError(
            "item must be EvidenceAggregationItem"
        )
    if type(item.finding) is not ResearchFinding:
        raise TypeError("finding must be ResearchFinding")
    if type(item.provenance) is not EvidenceProvenanceMetadata:
        raise TypeError(
            "provenance must be EvidenceProvenanceMetadata"
        )
    if type(item.assessment) is not EvidenceAssessmentResult:
        raise TypeError(
            "assessment must be EvidenceAssessmentResult"
        )
    if type(item.metadata) is not EvidenceAggregationMetadata:
        raise TypeError(
            "metadata must be EvidenceAggregationMetadata"
        )

    validate_research_finding(item.finding)
    validate_evidence_provenance(item.provenance)
    validate_evidence_aggregation_metadata(item.metadata)

    if not isinstance(item.assessment.finding_id, str):
        raise TypeError("assessment finding_id must be str")
    if not isinstance(item.assessment.policy_version, str):
        raise TypeError(
            "assessment policy_version must be str"
        )

    if item.provenance.finding_id != item.finding.finding_id:
        raise ValueError(
            "provenance finding_id must match finding finding_id"
        )
    if item.assessment.finding_id != item.finding.finding_id:
        raise ValueError(
            "assessment finding_id must match finding finding_id"
        )
    if item.metadata.finding_id != item.finding.finding_id:
        raise ValueError(
            "aggregation metadata finding_id must match "
            "finding finding_id"
        )

    if (
        item.assessment.policy_version
        != ASSESSMENT_POLICY_VERSION
    ):
        raise ValueError(
            "assessment policy_version must be "
            f"{ASSESSMENT_POLICY_VERSION}"
        )


def _require_nonblank_string(name: str, value: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be str")
    if not value.strip():
        raise ValueError(f"{name} must not be blank")
