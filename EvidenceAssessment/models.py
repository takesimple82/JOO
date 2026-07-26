from dataclasses import dataclass

from EvidenceValidation.models import EvidenceValidationResult


@dataclass(frozen=True)
class EvidenceAssessmentDimension:
    code: str
    value: str
    rationale: str


@dataclass(frozen=True)
class EvidenceAssessmentResult:
    finding_id: str
    assessable: bool
    policy_version: str
    dimensions: tuple[EvidenceAssessmentDimension, ...]
    validation: EvidenceValidationResult

    def __post_init__(self) -> None:
        if not isinstance(self.dimensions, tuple):
            raise TypeError("dimensions must be tuple")
