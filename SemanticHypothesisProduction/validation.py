from ExplicitHypothesis.models import ExplicitHypothesis
from ExplicitHypothesis.validation import (
    validate_explicit_hypothesis,
)
from SemanticHypothesisProduction.models import (
    SemanticallyProducedHypothesis,
)


def validate_semantically_produced_hypothesis(
    production: SemanticallyProducedHypothesis,
) -> None:
    if type(production) is not SemanticallyProducedHypothesis:
        raise TypeError(
            "production must be SemanticallyProducedHypothesis"
        )
    if type(production.hypothesis) is not ExplicitHypothesis:
        raise TypeError(
            "hypothesis must be ExplicitHypothesis"
        )
    validate_explicit_hypothesis(production.hypothesis)
