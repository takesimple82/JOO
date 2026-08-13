from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from MarketInstrument.models import ExplicitMarketInstrument
from MarketSnapshot.models import ExplicitMarketSnapshot


@dataclass(frozen=True)
class ExplicitMarketSessionProfile:
    session_profile_id: str
    market_id: str
    venue_id: str
    timezone_id: str
    calendar_id: str


@dataclass(frozen=True)
class ExplicitMarketSubjectBinding:
    instrument: ExplicitMarketInstrument
    fact_id: str
    last_price_payload_key: str
    market_status_payload_key: str


@dataclass(frozen=True)
class ExplicitMarketFactSelectionCriteria:
    required_source_class: str
    required_source_identity: str | None
    collected_at_start: datetime | None
    collected_at_end: datetime | None


@dataclass(frozen=True)
class ExplicitMarketSnapshotProductionPolicy:
    require_all_bound_subjects: bool
    allow_partial_emission: bool
    freshness_max_age: timedelta | None


@dataclass(frozen=True)
class ExplicitMarketSnapshotProductionRequest:
    market_snapshot_id: str
    session_context_id: str
    session_profile: ExplicitMarketSessionProfile
    subject_bindings: tuple[ExplicitMarketSubjectBinding, ...]
    fact_selection: ExplicitMarketFactSelectionCriteria
    production_policy: ExplicitMarketSnapshotProductionPolicy


@dataclass(frozen=True)
class ExplicitMarketSnapshotProductionFailure:
    failure_code: str
    omitted_instrument_ids: tuple[str, ...]


@dataclass(frozen=True)
class ExplicitMarketSnapshotProductionResult:
    result_kind: str
    snapshot: ExplicitMarketSnapshot | None
    failure: ExplicitMarketSnapshotProductionFailure | None
    omitted_instrument_ids: tuple[str, ...]
