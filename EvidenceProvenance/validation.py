from EvidenceProvenance.models import (
    SOURCE_CLASSES,
    EvidenceProvenanceMetadata,
)


def validate_evidence_provenance(
    metadata: EvidenceProvenanceMetadata,
) -> None:
    if type(metadata) is not EvidenceProvenanceMetadata:
        raise TypeError(
            "metadata must be EvidenceProvenanceMetadata"
        )
    if not isinstance(metadata.finding_id, str):
        raise TypeError("finding_id must be str")
    if not metadata.finding_id.strip():
        raise ValueError("finding_id must not be blank")
    if not isinstance(metadata.source_class, str):
        raise TypeError("source_class must be str")
    if metadata.source_class not in SOURCE_CLASSES:
        raise ValueError(
            "source_class must be primary, secondary, or unknown"
        )
