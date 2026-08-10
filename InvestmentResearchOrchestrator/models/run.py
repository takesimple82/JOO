from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from InvestmentResearchOrchestrator.models.enums import (
    IRORunPhase,
    IRORunStatus,
)


@dataclass(frozen=True)
class IRORun:
    run_id: str
    portfolio_snapshot_id: str
    prior_baseline_id: str | None
    phase: IRORunPhase
    status: IRORunStatus
    created_at: datetime
    updated_at: datetime
