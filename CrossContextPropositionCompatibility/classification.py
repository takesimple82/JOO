from CrossContextPropositionCompatibility.models import (
    CrossContextPropositionCompatibilityStatus,
)
from SemanticPropositionProduction.models import (
    SemanticallyProducedNumericProposition,
)
from SemanticPropositionProduction.validation import (
    validate_semantically_produced_numeric_proposition,
)


def classify_cross_context_proposition_compatibility(
    baseline: SemanticallyProducedNumericProposition,
    current: SemanticallyProducedNumericProposition,
) -> CrossContextPropositionCompatibilityStatus:
    validate_semantically_produced_numeric_proposition(baseline)
    validate_semantically_produced_numeric_proposition(current)

    if (
        baseline.proposition.subject_id
        != current.proposition.subject_id
    ):
        return (
            CrossContextPropositionCompatibilityStatus
            .SUBJECT_MISMATCH
        )
    if (
        baseline.proposition.predicate_id
        != current.proposition.predicate_id
    ):
        return (
            CrossContextPropositionCompatibilityStatus
            .PREDICATE_MISMATCH
        )
    if (
        baseline.proposition.unit_id
        != current.proposition.unit_id
    ):
        return (
            CrossContextPropositionCompatibilityStatus
            .UNIT_MISMATCH
        )
    return CrossContextPropositionCompatibilityStatus.COMPATIBLE
