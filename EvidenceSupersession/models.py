from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitPropositionSupersession:
    superseded_proposition_id: str
    superseding_proposition_id: str
