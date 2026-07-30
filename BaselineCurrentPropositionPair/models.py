from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitBaselineCurrentPropositionPair:
    baseline_proposition_id: str
    current_proposition_id: str
