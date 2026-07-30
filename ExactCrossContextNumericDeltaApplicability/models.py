from enum import Enum


class ExactCrossContextNumericDeltaApplicabilityStatus(Enum):
    BASELINE_PROPOSITION_ENDPOINT_MISMATCH = (
        "baseline_proposition_endpoint_mismatch"
    )
    CURRENT_PROPOSITION_ENDPOINT_MISMATCH = (
        "current_proposition_endpoint_mismatch"
    )
    BASELINE_CONTEXT_ENDPOINT_MISMATCH = (
        "baseline_context_endpoint_mismatch"
    )
    CURRENT_CONTEXT_ENDPOINT_MISMATCH = (
        "current_context_endpoint_mismatch"
    )
    CONTEXT_DATE_CONFLICT = "context_date_conflict"
    SAME_DATE = "same_date"
    BASELINE_AFTER_CURRENT = "baseline_after_current"
    SUBJECT_MISMATCH = "subject_mismatch"
    PREDICATE_MISMATCH = "predicate_mismatch"
    UNIT_MISMATCH = "unit_mismatch"
    CALCULABLE = "calculable"
