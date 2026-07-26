from dataclasses import dataclass


SOURCE_CLASSES: tuple[str, ...] = (
    "primary",
    "secondary",
    "unknown",
)


@dataclass(frozen=True)
class EvidenceProvenanceMetadata:
    finding_id: str
    source_class: str
