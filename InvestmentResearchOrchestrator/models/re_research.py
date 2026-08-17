from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from InvestmentResearchOrchestrator.models.enums import (
    EscalationMarker,
    EscalationReasonCode,
    ReResearchReasonCode,
)


@dataclass(frozen=True)
class ReResearchBudget:
    max_attempts: int
    remaining: int


@dataclass(frozen=True)
class ReResearchRequest:
    request_id: str
    subject_key: str
    reason_code: ReResearchReasonCode
    task_type: str
    source_case_ids: tuple[str, ...]
    priority: str


@dataclass(frozen=True)
class ReResearchRequestSet:
    run_id: str
    attempt: int
    requests: tuple[ReResearchRequest, ...]


@dataclass(frozen=True)
class EscalationRecord:
    run_id: str
    marker: EscalationMarker
    reason_code: EscalationReasonCode
    unresolved_case_ids: tuple[str, ...]
    max_attempts: int
    remaining: int
    created_at: datetime
