from dataclasses import dataclass

from ExactNumericDeltaSignal.models import (
    ExactNumericDeltaSignalClassification,
)
from SemanticHypothesisProduction.models import (
    SemanticallyProducedHypothesis,
)


@dataclass(frozen=True)
class ExplicitNumericSignalHypothesisLink:
    signal: ExactNumericDeltaSignalClassification
    hypothesis: SemanticallyProducedHypothesis
