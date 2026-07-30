from ExplicitThesis.models import ExplicitThesis
from ExplicitThesis.validation import validate_explicit_thesis
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)


def validate_semantically_produced_thesis(
    production: SemanticallyProducedThesis,
) -> None:
    if type(production) is not SemanticallyProducedThesis:
        raise TypeError(
            "production must be SemanticallyProducedThesis"
        )
    if type(production.thesis) is not ExplicitThesis:
        raise TypeError("thesis must be ExplicitThesis")
    validate_explicit_thesis(production.thesis)
