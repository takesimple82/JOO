from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceAggregationMetadata:
    finding_id: str
    aggregation_key: str
    source_reference_id: str
