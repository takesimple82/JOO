from enum import Enum


class CrossContextPropositionCompatibilityStatus(Enum):
    SUBJECT_MISMATCH = "subject_mismatch"
    PREDICATE_MISMATCH = "predicate_mismatch"
    UNIT_MISMATCH = "unit_mismatch"
    COMPATIBLE = "compatible"
