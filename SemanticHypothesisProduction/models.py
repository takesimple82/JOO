from dataclasses import dataclass

from ExplicitHypothesis.models import ExplicitHypothesis


@dataclass(frozen=True)
class SemanticallyProducedHypothesis:
    hypothesis: ExplicitHypothesis
