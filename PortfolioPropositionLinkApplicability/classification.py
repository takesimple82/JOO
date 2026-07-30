from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from EvidenceProposition.validation import (
    validate_exact_observed_numeric_proposition,
)
from PortfolioDomain.models import PortfolioSubject
from PortfolioDomain.validation import validate_portfolio_subject
from PortfolioPropositionLink.models import (
    ExplicitPropositionPortfolioSubjectLink,
)
from PortfolioPropositionLink.validation import (
    validate_explicit_proposition_portfolio_subject_link,
)
from PortfolioPropositionLinkApplicability.models import (
    PortfolioPropositionLinkApplicabilityStatus,
)


def classify_explicit_proposition_portfolio_subject_link_applicability(
    proposition: ExactObservedNumericProposition,
    subject: PortfolioSubject,
    link: ExplicitPropositionPortfolioSubjectLink,
) -> PortfolioPropositionLinkApplicabilityStatus:
    validate_explicit_proposition_portfolio_subject_link(link)
    validate_exact_observed_numeric_proposition(proposition)
    validate_portfolio_subject(subject)

    if link.proposition_id != proposition.proposition_id:
        return (
            PortfolioPropositionLinkApplicabilityStatus
            .PROPOSITION_ENDPOINT_MISMATCH
        )
    if link.portfolio_subject_id != subject.subject_id:
        return (
            PortfolioPropositionLinkApplicabilityStatus
            .PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH
        )
    return PortfolioPropositionLinkApplicabilityStatus.APPLICABLE
