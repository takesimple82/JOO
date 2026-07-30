from enum import Enum


class PortfolioPropositionLinkApplicabilityStatus(Enum):
    PROPOSITION_ENDPOINT_MISMATCH = (
        "proposition_endpoint_mismatch"
    )
    PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH = (
        "portfolio_subject_endpoint_mismatch"
    )
    APPLICABLE = "applicable"
