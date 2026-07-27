from EvidenceComparison.models import EvidenceComparisonStatus
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from EvidenceProposition.validation import (
    validate_exact_observed_numeric_proposition,
)


def compare_exact_observed_numeric_propositions(
    left: ExactObservedNumericProposition,
    right: ExactObservedNumericProposition,
) -> EvidenceComparisonStatus:
    validate_exact_observed_numeric_proposition(left)
    validate_exact_observed_numeric_proposition(right)

    if left.subject_id != right.subject_id:
        return EvidenceComparisonStatus.NOT_COMPARABLE
    if left.predicate_id != right.predicate_id:
        return EvidenceComparisonStatus.NOT_COMPARABLE
    if left.unit_id != right.unit_id:
        return EvidenceComparisonStatus.NOT_COMPARABLE
    if left.effective_context_id != right.effective_context_id:
        return EvidenceComparisonStatus.NOT_COMPARABLE

    if left.value == right.value:
        return EvidenceComparisonStatus.NUMERICALLY_COMPATIBLE
    return EvidenceComparisonStatus.NUMERICALLY_INCOMPATIBLE
