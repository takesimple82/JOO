from dataclasses import dataclass

from InvestmentResearchOrchestrator.models.enums import (
    ScanChangeClass,
    SubjectClass,
)


@dataclass(frozen=True)
class ScanDelta:
    subject_id: str
    change_class: ScanChangeClass
    materiality_basis: ScanChangeClass
    subject_class: SubjectClass


@dataclass(frozen=True)
class ScanDeltaSet:
    run_id: str
    deltas: tuple[ScanDelta, ...]
