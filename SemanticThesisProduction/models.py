from dataclasses import dataclass

from ExplicitThesis.models import ExplicitThesis


@dataclass(frozen=True)
class SemanticallyProducedThesis:
    thesis: ExplicitThesis
