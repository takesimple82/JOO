from enum import Enum


class EvidenceSupersessionApplicabilityStatus(Enum):
    NOT_CONTRADICTION_CANDIDATE = (
        "not_contradiction_candidate"
    )
    RELATION_ENDPOINT_MISMATCH = (
        "relation_endpoint_mismatch"
    )
    APPLICABLE = "applicable"
