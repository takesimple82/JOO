from enum import Enum


class ExpectedValueAssumptionSetApplicabilityStatus(Enum):
    PROBABILITY_TOTAL_MISMATCH = (
        "probability_total_mismatch"
    )
    APPLICABLE = "applicable"
