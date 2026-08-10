from dataclasses import dataclass

from InvestmentResearchOrchestrator.models.enums import (
    MemoryDeltaClass,
)


@dataclass(frozen=True)
class MemoryDelta:
    subject_key: str
    prior_present: bool
    delta_class: MemoryDeltaClass


@dataclass(frozen=True)
class MemoryDeltaSet:
    run_id: str
    deltas: tuple[MemoryDelta, ...]
