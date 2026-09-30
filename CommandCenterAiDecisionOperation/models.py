"""Immutable Phase 8 evidence and operational-state contracts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ObservationEvidencePackage:
    package_id: str
    observation_id: str
    observation_sequence: int
    portfolio_snapshot_id: str
    capital_snapshot_id: str
    fact_ids: tuple[str, ...]
    raw_fact_ids: tuple[str, ...]
    truth_class: str
    factual_collected_at: datetime
    created_at: datetime


@dataclass(frozen=True)
class AiCioDecisionAttempt:
    attempt_id: str
    mode: str
    evidence_package: ObservationEvidencePackage
    research_state: str
    committee_state: str
    contradiction_state: str
    cio_state: str
    ev_state: str
    allocation_state: str
    iha_state: str
    blocker_codes: tuple[str, ...]
    created_at: datetime
    executable: bool
    broker_mutation_enabled: bool
