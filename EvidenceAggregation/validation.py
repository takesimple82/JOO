from EvidenceAggregation.models import (
    EvidenceAggregationMetadata,
)


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


def _require_nonblank_string(name: str, value: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be str")
    if not value.strip():
        raise ValueError(f"{name} must not be blank")
