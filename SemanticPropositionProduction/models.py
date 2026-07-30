from dataclasses import dataclass

from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)


@dataclass(frozen=True)
class SemanticallyProducedNumericProposition:
    proposition: ExactObservedNumericProposition
