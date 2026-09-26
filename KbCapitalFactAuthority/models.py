from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from FactStore.models import ExplicitFactAppendRequest


@dataclass(frozen=True)
class ExplicitExactAmount:
    """Exact broker decimal amount: present zero is distinct from missing."""

    presence: str
    canonical_text: str | None
    raw_text: str | None


@dataclass(frozen=True)
class ExplicitCapitalFactBinding:
    fact_id: str
    envelope_id: str
    superseded_fact_id: str | None


@dataclass(frozen=True)
class ExplicitBalancesNormalizationRequest:
    raw_fact_id: str
    account_selector: str
    currency_code: str
    orderable_cash: ExplicitCapitalFactBinding
    deposit_today: ExplicitCapitalFactBinding
    deposit_d1: ExplicitCapitalFactBinding
    deposit_d2: ExplicitCapitalFactBinding
    withdrawable_cash: ExplicitCapitalFactBinding
    orderable_total: ExplicitCapitalFactBinding


@dataclass(frozen=True)
class ExplicitHoldingsCapitalNormalizationRequest:
    raw_fact_id: str
    account_selector: str
    account_valuation: ExplicitCapitalFactBinding
    position_bindings: tuple["ExplicitPositionMarketValueBinding", ...]


@dataclass(frozen=True)
class ExplicitPositionMarketValueBinding:
    account_selector: str
    position_class: str
    currency_code: str
    provider_symbol: str
    fact_id: str
    envelope_id: str
    superseded_fact_id: str | None


@dataclass(frozen=True)
class ExplicitNormalizedCapitalFact:
    append_request: ExplicitFactAppendRequest
    fact_kind: str
    broker_field: str
    amount: ExplicitExactAmount


@dataclass(frozen=True)
class ExplicitBalancesNormalizationResult:
    raw_fact_id: str
    collected_at: datetime
    facts: tuple[ExplicitNormalizedCapitalFact, ...]


@dataclass(frozen=True)
class ExplicitHoldingsCapitalNormalizationResult:
    raw_fact_id: str
    collected_at: datetime
    facts: tuple[ExplicitNormalizedCapitalFact, ...]


@dataclass(frozen=True)
class ExplicitCapitalFactPolicy:
    freshness_max_age: timedelta


@dataclass(frozen=True)
class ExplicitCapitalSnapshotIdentity:
    capital_snapshot_id: str
    account_selector: str


@dataclass(frozen=True)
class ExplicitCapitalPortfolioBinding:
    """Bind CapitalSnapshot to PortfolioSnapshot by ids only — never mutates it."""

    portfolio_snapshot_id: str | None
    portfolio_id: str | None
    observation_context_id: str | None


@dataclass(frozen=True)
class ExplicitCapitalSnapshot:
    capital_snapshot_id: str
    account_selector: str
    provider_id: str
    currency_code: str
    collected_at: datetime
    freshness_max_age: timedelta
    portfolio_snapshot_id: str | None
    portfolio_id: str | None
    observation_context_id: str | None
    raw_balances_fact_id: str
    raw_holdings_fact_id: str | None
    orderable_cash_fact_id: str
    deposit_today_fact_id: str
    deposit_d1_fact_id: str
    deposit_d2_fact_id: str
    withdrawable_cash_fact_id: str
    orderable_total_fact_id: str
    broker_reported_account_valuation_fact_id: str | None
    position_market_value_fact_ids: tuple[str, ...]
    sizing_authority: str


@dataclass(frozen=True)
class ExplicitCapitalFactPlaneResult:
    result_kind: str
    failure_code: str | None
    capital_snapshot: ExplicitCapitalSnapshot | None
    raw_balances_fact_id: str | None
    canonical_fact_ids: tuple[str, ...]
