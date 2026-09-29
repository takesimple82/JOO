"""Immutable application projection models; never investment authorities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


MODE_REAL_READ_ONLY = "REAL_READ_ONLY"
MODE_FIXTURE = "FIXTURE"
APPLICATION_MODES = frozenset({MODE_REAL_READ_ONLY, MODE_FIXTURE})


@dataclass(frozen=True)
class JournalArtifact:
    record_id: str
    kind: str
    created_at: datetime
    artifact: object


@dataclass(frozen=True)
class ApplicationDataset:
    mode: str
    source_label: str
    generated_at: datetime
    facts: tuple
    artifacts: tuple[JournalArtifact, ...]
    journal_record_count: int
    change_class: str | None = None


@dataclass(frozen=True)
class EvidenceReferenceView:
    fact_id: str
    provider: str
    truth_class: str
    collected_at: str
    authority: str
    raw_fact_id: str | None


@dataclass(frozen=True)
class PositionView:
    security: str
    quantity: str
    market_value_krw: str | None
    weight_percent: str | None
    cap_status: str
    valuation_authority: str
    freshness: str
    quantity_evidence: EvidenceReferenceView
    valuation_evidence: EvidenceReferenceView | None


@dataclass(frozen=True)
class ExclusionView:
    provider_symbol: str
    position_class: str
    raw_currency_code: str
    reason: str
    evidence_fact_id: str


@dataclass(frozen=True)
class CapitalView:
    orderable_cash_krw: str | None
    deployed_capital_krw: str | None
    available_allocation_capacity_krw: str | None
    explicit_reserve_krw: str
    max_position_krw: str
    deployable_policy: str
    broker_account_valuation_krw: str | None
    broker_account_valuation_authority: str
    orderable_cash_evidence: EvidenceReferenceView | None


@dataclass(frozen=True)
class ChangeView:
    classification: str
    statements: tuple[str, ...]
    observed_at: str | None


@dataclass(frozen=True)
class CioView:
    state: str
    posture: str | None
    what_changed: str | None
    why_it_matters: str | None
    superior_opportunity_id: str | None
    unresolved_reasons: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    decision_id: str | None
    decision_timestamp: str | None


@dataclass(frozen=True)
class ExpectedValueView:
    opportunity_id: str
    portfolio_subject_id: str
    status: str
    value: str | None
    unit_id: str
    evidence_record_id: str | None


@dataclass(frozen=True)
class AllocationView:
    state: str
    proposal_id: str | None
    executable: bool
    blocked_reasons: tuple[str, ...]
    legs: tuple[dict, ...]


@dataclass(frozen=True)
class ApprovalView:
    state: str
    approval_id: str | None
    proposal_id: str | None
    decision: str | None
    principal: str | None
    decided_at: str | None


@dataclass(frozen=True)
class ExecutionView:
    state: str
    mutation_mode: str
    live_enabled: bool
    blocker_code: str
    blocker_detail: str
    order_intent_id: str | None
    tea_state: str
    tea_id: str | None
    order_kind: str
    unknown_recovery: str
    open_limit_attention: bool


@dataclass(frozen=True)
class AttentionView:
    attention_id: str
    category: str
    priority: int
    state: str
    what_happened: str
    why_it_matters: str
    evidence_ids: tuple[str, ...]
    required_action: str
    created_at: str


@dataclass(frozen=True)
class SystemHealthView:
    state: str
    factual_freshness: str
    last_factual_refresh: str | None
    fact_store_state: str
    command_center_state: str
    last_successful_cycle: str | None
    attention_state: str
    broker_mutation_mode: str
    execution_blocker: str
    durable_ownership: str


@dataclass(frozen=True)
class CommandCenterView:
    schema_version: int
    mode: str
    mode_label: str
    source_label: str
    generated_at: str
    portfolio_value_krw: str | None
    position_count: int
    positions: tuple[PositionView, ...]
    foreign_exclusions: tuple[ExclusionView, ...]
    capital: CapitalView
    change: ChangeView
    cio: CioView
    expected_values: tuple[ExpectedValueView, ...]
    allocation: AllocationView
    investment_approval: ApprovalView
    execution: ExecutionView
    attention: tuple[AttentionView, ...]
    evidence: tuple[EvidenceReferenceView, ...]
    system_health: SystemHealthView
