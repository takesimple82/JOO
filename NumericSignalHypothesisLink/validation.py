from ExactNumericDeltaSignal.models import (
    ExactNumericDeltaSignalClassification,
)
from NumericSignalHypothesisLink.models import (
    ExplicitNumericSignalHypothesisLink,
)
from SemanticHypothesisProduction.models import (
    SemanticallyProducedHypothesis,
)
from SemanticHypothesisProduction.validation import (
    validate_semantically_produced_hypothesis,
)


def validate_explicit_numeric_signal_hypothesis_link(
    link: ExplicitNumericSignalHypothesisLink,
) -> None:
    if type(link) is not ExplicitNumericSignalHypothesisLink:
        raise TypeError(
            "link must be ExplicitNumericSignalHypothesisLink"
        )
    if type(link.signal) is not ExactNumericDeltaSignalClassification:
        raise TypeError(
            "signal must be "
            "ExactNumericDeltaSignalClassification"
        )
    if type(link.hypothesis) is not SemanticallyProducedHypothesis:
        raise TypeError(
            "hypothesis must be SemanticallyProducedHypothesis"
        )
    validate_semantically_produced_hypothesis(
        link.hypothesis
    )
