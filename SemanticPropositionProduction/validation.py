from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from EvidenceProposition.validation import (
    validate_exact_observed_numeric_proposition,
)
from SemanticPropositionProduction.models import (
    SemanticallyProducedNumericProposition,
)


def validate_semantically_produced_numeric_proposition(
    production: SemanticallyProducedNumericProposition,
) -> None:
    if type(production) is not SemanticallyProducedNumericProposition:
        raise TypeError(
            "production must be "
            "SemanticallyProducedNumericProposition"
        )
    if type(production.proposition) is not ExactObservedNumericProposition:
        raise TypeError(
            "proposition must be ExactObservedNumericProposition"
        )

    validate_exact_observed_numeric_proposition(
        production.proposition
    )
