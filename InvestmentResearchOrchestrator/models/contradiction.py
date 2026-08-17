from __future__ import annotations

from dataclasses import dataclass

from EvidenceContradiction.models import (
    EvidenceContradictionStatus,
)

from InvestmentResearchOrchestrator.models.enums import (
    ContradictionCaseClass,
    ContradictionCaseStatus,
    ContradictionNotesCode,
    NumericPathStatus,
)
from InvestmentResearchOrchestrator.models.re_research import (
    ReResearchRequestSet,
)


@dataclass(frozen=True)
class ContradictionEvidenceRef:
    research_id: str | None
    committee_id: str | None
    store_identity: str | None
    prompt_hash: str | None


@dataclass(frozen=True)
class ContradictionCase:
    case_id: str
    subject_key: str
    case_class: ContradictionCaseClass
    status: ContradictionCaseStatus
    evidence_refs: tuple[ContradictionEvidenceRef, ...]
    domain_status: EvidenceContradictionStatus | None
    notes_code: ContradictionNotesCode | None


@dataclass(frozen=True)
class ContradictionEvaluation:
    run_id: str
    attempt: int
    cases: tuple[ContradictionCase, ...]
    unresolved: tuple[str, ...]
    re_research_requests: ReResearchRequestSet
    numeric_path_status: NumericPathStatus
