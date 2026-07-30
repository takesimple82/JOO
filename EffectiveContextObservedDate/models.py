from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitEffectiveContextObservedDate:
    effective_context_id: str
    observed_on: str
