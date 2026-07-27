from EvidenceComparison.comparison import (
    compare_exact_observed_numeric_propositions,
)
from EvidenceComparison.models import EvidenceComparisonStatus
from EvidenceContradiction.models import (
    EvidenceContradictionStatus,
)
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)


def classify_exact_observed_numeric_contradiction_candidate(
    left: ExactObservedNumericProposition,
    right: ExactObservedNumericProposition,
) -> EvidenceContradictionStatus:
    comparison_status = (
        compare_exact_observed_numeric_propositions(
            left,
            right,
        )
    )

    if comparison_status is EvidenceComparisonStatus.NOT_COMPARABLE:
        return EvidenceContradictionStatus.NOT_ELIGIBLE
    if (
        comparison_status
        is EvidenceComparisonStatus.NUMERICALLY_COMPATIBLE
    ):
        return (
            EvidenceContradictionStatus
            .NO_CONTRADICTION_CANDIDATE
        )
    if (
        comparison_status
        is EvidenceComparisonStatus.NUMERICALLY_INCOMPATIBLE
    ):
        return (
            EvidenceContradictionStatus.CONTRADICTION_CANDIDATE
        )

    raise RuntimeError(
        "unsupported evidence comparison status"
    )
