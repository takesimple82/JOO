from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from InvestmentResearchOrchestrator.models.enums import (
    EvidencePayloadKind,
)


@dataclass(frozen=True)
class EvidenceStoreRecord:
    run_id: str
    research_id: str | None
    committee_id: str | None
    provider_id: str | None
    prompt_id: str | None
    prompt_hash: str | None
    source_reference: str | None
    collected_at: datetime | None
    stored_at: datetime
    payload_kind: EvidencePayloadKind
    payload: str
