from enum import Enum


class EvidenceContradictionStatus(Enum):
    NOT_ELIGIBLE = "not_eligible"
    NO_CONTRADICTION_CANDIDATE = (
        "no_contradiction_candidate"
    )
    CONTRADICTION_CANDIDATE = "contradiction_candidate"
