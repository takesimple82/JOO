from enum import Enum


class EvidenceComparisonStatus(Enum):
    NOT_COMPARABLE = "not_comparable"
    NUMERICALLY_COMPATIBLE = "numerically_compatible"
    NUMERICALLY_INCOMPATIBLE = "numerically_incompatible"
