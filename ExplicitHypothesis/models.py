from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitHypothesis:
    hypothesis_id: str
    statement: str
