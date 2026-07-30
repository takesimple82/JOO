from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitThesis:
    thesis_id: str
    statement: str
