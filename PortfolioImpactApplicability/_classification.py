from PortfolioDomain.models import PortfolioSubject
from PortfolioImpactApplicability.models import (
    PortfolioImpactApplicabilityStatus,
)
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)
from ThesisPortfolioSubjectLink.models import (
    ExplicitThesisPortfolioSubjectLink,
)


def _classify_portfolio_impact_applicability_unchecked(
    semantic_thesis: SemanticallyProducedThesis,
    link: ExplicitThesisPortfolioSubjectLink,
    portfolio_subject: PortfolioSubject,
) -> PortfolioImpactApplicabilityStatus:
    if semantic_thesis.thesis.thesis_id != link.thesis_id:
        return (
            PortfolioImpactApplicabilityStatus
            .THESIS_ENDPOINT_MISMATCH
        )
    if (
        portfolio_subject.subject_id
        != link.portfolio_subject_id
    ):
        return (
            PortfolioImpactApplicabilityStatus
            .PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH
        )
    return PortfolioImpactApplicabilityStatus.APPLICABLE
