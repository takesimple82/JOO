from dataclasses import dataclass

from EvidenceAssessment.models import EvidenceAssessmentResult
from EvidenceProvenance.models import EvidenceProvenanceMetadata
from ResearchDomain.models import ResearchFinding


@dataclass(frozen=True)
class EvidenceAggregationMetadata:
    finding_id: str
    aggregation_key: str
    source_reference_id: str


@dataclass(frozen=True)
class EvidenceAggregationItem:
    finding: ResearchFinding
    provenance: EvidenceProvenanceMetadata
    assessment: EvidenceAssessmentResult
    metadata: EvidenceAggregationMetadata


@dataclass(frozen=True)
class EvidenceAggregationBatch:
    items: tuple[EvidenceAggregationItem, ...]
