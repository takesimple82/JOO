"""Immutable contracts for the real KB read-only producer boundary."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioSnapshotProducer.models import (
    ExplicitPortfolioSnapshotProductionProvenance,
)


@dataclass(frozen=True)
class DomesticPositionBinding:
    position_class: str
    provider_symbol: str
    position_id: str
    portfolio_subject_id: str


@dataclass(frozen=True)
class ReadOnlyOperationConfig:
    account_selector: str
    portfolio_id: str
    freshness_max_age_seconds: int
    domestic_bindings: tuple[DomesticPositionBinding, ...]


@dataclass(frozen=True)
class ReadOnlyObservation:
    observation_id: str
    created_at: datetime
    portfolio_snapshot: ExplicitPortfolioSnapshot
    portfolio_provenance: ExplicitPortfolioSnapshotProductionProvenance
    capital_snapshot: ExplicitCapitalSnapshot
    change_class: str
    application_fact_ids: tuple[str, ...]
    raw_fact_ids: tuple[str, ...]
    live_mutation_enabled: bool


@dataclass(frozen=True)
class ReadOnlyOperationResult:
    observation: ReadOnlyObservation
    fact_store_path: str
    journal_path: str
    appended_fact_count: int
