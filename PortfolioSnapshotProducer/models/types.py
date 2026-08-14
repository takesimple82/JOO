from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from PortfolioSnapshot.models import ExplicitPortfolioSnapshot


@dataclass(frozen=True)
class ExplicitPortfolioHoldingFactBinding:
    fact_id: str
    position_id: str
    portfolio_subject_id: str
    quantity_payload_key: str


@dataclass(frozen=True)
class ExplicitPortfolioWatchlistMembershipDeclaration:
    portfolio_subject_id: str


@dataclass(frozen=True)
class ExplicitPortfolioFactSelectionCriteria:
    required_source_class: str
    required_source_identity: str | None
    collected_at_start: datetime | None
    collected_at_end: datetime | None


@dataclass(frozen=True)
class ExplicitPortfolioSnapshotProductionPolicy:
    freshness_max_age: timedelta | None


@dataclass(frozen=True)
class ExplicitPortfolioSnapshotProductionRequest:
    portfolio_snapshot_id: str
    observation_context_id: str
    portfolio_id: str
    holding_fact_bindings: tuple[ExplicitPortfolioHoldingFactBinding, ...]
    watchlist_memberships: tuple[ExplicitPortfolioWatchlistMembershipDeclaration, ...]
    fact_selection: ExplicitPortfolioFactSelectionCriteria
    production_policy: ExplicitPortfolioSnapshotProductionPolicy


@dataclass(frozen=True)
class ExplicitPortfolioUsedFactProvenance:
    fact_id: str
    collected_at: datetime
    source_identity: str


@dataclass(frozen=True)
class ExplicitPortfolioSnapshotProductionProvenance:
    used_facts: tuple[ExplicitPortfolioUsedFactProvenance, ...]


@dataclass(frozen=True)
class ExplicitPortfolioSnapshotProductionFailure:
    failure_code: str
    failed_fact_id: str
    failed_position_id: str


@dataclass(frozen=True)
class ExplicitPortfolioSnapshotProductionResult:
    result_kind: str
    snapshot: ExplicitPortfolioSnapshot | None
    failure: ExplicitPortfolioSnapshotProductionFailure | None
    provenance: ExplicitPortfolioSnapshotProductionProvenance | None
