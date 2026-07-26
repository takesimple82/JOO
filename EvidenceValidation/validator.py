from ResearchDomain.models import ResearchFinding
from ResearchDomain.validation import validate_research_finding


class EvidenceValidator:
    def validate(
        self,
        finding: ResearchFinding,
    ) -> None:
        return validate_research_finding(finding)
