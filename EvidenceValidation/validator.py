from EvidenceValidation.models import EvidenceValidationResult
from ResearchDomain.models import ResearchFinding
from ResearchDomain.validation import validate_research_finding


class EvidenceValidator:
    def validate(
        self,
        finding: ResearchFinding,
    ) -> EvidenceValidationResult:
        validate_research_finding(finding)
        return EvidenceValidationResult(
            valid=True,
            issues=(),
        )
