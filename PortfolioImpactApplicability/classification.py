from PortfolioDomain.models import PortfolioSubject
from PortfolioDomain.validation import validate_portfolio_subject
from PortfolioImpactApplicability.models import (
    PortfolioImpactApplicabilityStatus,
)
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)
from SemanticThesisProduction.validation import (
    validate_semantically_produced_thesis,
)
from ThesisPortfolioSubjectLink.models import (
    ExplicitThesisPortfolioSubjectLink,
)
from ThesisPortfolioSubjectLink.validation import (
    validate_explicit_thesis_portfolio_subject_link,
)


def classify_portfolio_impact_applicability(
    semantic_thesis: SemanticallyProducedThesis,
    link: ExplicitThesisPortfolioSubjectLink,
    portfolio_subject: PortfolioSubject,
) -> PortfolioImpactApplicabilityStatus:
    validate_semantically_produced_thesis(semantic_thesis)
    validate_explicit_thesis_portfolio_subject_link(link)
    validate_portfolio_subject(portfolio_subject)

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
