from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from FactStore.models import ExplicitFactAppendRequest
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioSnapshotProducer.models import (
    ExplicitPortfolioSnapshotProductionProvenance,
)


@dataclass(frozen=True)
class ExplicitKbPositionBinding:
    account_selector: str
    position_class: str
    currency_code: str
    provider_symbol: str
    fact_id: str
    envelope_id: str
    position_id: str
    portfolio_subject_id: str
    superseded_fact_id: str | None


@dataclass(frozen=True)
class ExplicitKbNormalizationRequest:
    raw_fact_id: str
    account_selector: str
    position_bindings: tuple[ExplicitKbPositionBinding, ...]


@dataclass(frozen=True)
class ExplicitNormalizedPosition:
    append_request: ExplicitFactAppendRequest
    position_id: str
    portfolio_subject_id: str
    quantity: str
    is_active_holding: bool


@dataclass(frozen=True)
class ExplicitKbNormalizationResult:
    raw_fact_id: str
    collected_at: datetime
    positions: tuple[ExplicitNormalizedPosition, ...]


@dataclass(frozen=True)
class ExplicitVerticalSlicePolicy:
    freshness_max_age: timedelta


@dataclass(frozen=True)
class ExplicitSnapshotIdentity:
    portfolio_snapshot_id: str
    observation_context_id: str
    portfolio_id: str


@dataclass(frozen=True)
class ExplicitIroIngressArtifact:
    ingress_id: str
    run_id: str
    portfolio_snapshot_id: str
    prior_snapshot_id: str | None
    change_class: str
    raw_fact_id: str
    normalized_fact_ids: tuple[str, ...]
    snapshot_used_fact_ids: tuple[str, ...]
    provider_id: str
    collected_at: datetime
    snapshot_provenance: ExplicitPortfolioSnapshotProductionProvenance


@dataclass(frozen=True)
class ExplicitVerticalSliceResult:
    result_kind: str
    failure_code: str | None
    snapshot: ExplicitPortfolioSnapshot | None
    change_class: str | None
    ingress: ExplicitIroIngressArtifact | None
    iro_result: object | None
