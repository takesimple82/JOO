from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceValidationIssue:
    code: str
    message: str


@dataclass(frozen=True)
class EvidenceValidationResult:
    valid: bool
    issues: tuple[EvidenceValidationIssue, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.issues, tuple):
            raise TypeError("issues must be tuple")
