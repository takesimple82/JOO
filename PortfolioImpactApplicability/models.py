from enum import Enum


class PortfolioImpactApplicabilityStatus(Enum):
    APPLICABLE = "applicable"
    THESIS_ENDPOINT_MISMATCH = "thesis_endpoint_mismatch"
    PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH = (
        "portfolio_subject_endpoint_mismatch"
    )
