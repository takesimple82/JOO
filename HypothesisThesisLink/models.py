from dataclasses import dataclass

from SemanticHypothesisProduction.models import (
    SemanticallyProducedHypothesis,
)
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)


@dataclass(frozen=True)
class ExplicitHypothesisThesisLink:
    hypothesis: SemanticallyProducedHypothesis
    thesis: SemanticallyProducedThesis
