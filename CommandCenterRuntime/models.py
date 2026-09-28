from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class WakeEvent:
    """Immutable OperationalTrigger. No AI wake without evidence."""

    wake_event_id: str
    wake_type: str
    source: str
    fact_or_evidence_id: str
    observed_at: datetime
    subject_ids: tuple[str, ...]
    provenance: str
    integrity_seal: str


@dataclass(frozen=True)
class PortfolioMembershipFact:
    fact_id: str
    subject_ids: tuple[str, ...]
    observed_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class PortfolioQuantityFact:
    fact_id: str
    subject_id: str
    quantity: Decimal
    observed_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class CapitalCashFact:
    """Present zero ≠ missing. Missing must never coerce to 0/unchanged/safe."""

    fact_id: str
    presence: str
    amount_krw: Decimal | None
    currency_code: str
    observed_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class AdmittedResearchEvidenceFact:
    fact_id: str
    evidence_id: str
    research_id: str
    subject_ids: tuple[str, ...]
    truth_class: str
    observed_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class ThesisTransitionFact:
    fact_id: str
    transition_id: str
    subject_id: str
    state: str
    observed_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class PolicySupersessionFact:
    fact_id: str
    prior_policy_id: str
    new_policy_id: str
    new_policy_seal: str
    observed_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class ApprovalTransitionFact:
    fact_id: str
    gate_kind: str
    approval_or_authorization_id: str
    decision: str
    bound_artifact_id: str
    observed_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class BrokerOrderFillFact:
    fact_id: str
    attempt_id: str
    outcome: str
    broker_order_no: str | None
    observed_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class ProviderFailureFact:
    fact_id: str
    provider_id: str
    operation: str
    detail: str
    observed_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class DetectedChange:
    change_kind: str
    prior_fact_id: str | None
    current_fact_id: str
    subject_ids: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class StagePlanEntry:
    stage: str
    required: bool
    reason: str


@dataclass(frozen=True)
class StageExecutionRecord:
    stage: str
    status: str
    reason: str
    domain_record_ids: tuple[str, ...]
    started_at: datetime | None
    finished_at: datetime | None


@dataclass(frozen=True)
class HumanAttentionItem:
    attention_id: str
    category: str
    wake_event_id: str
    bound_record_ids: tuple[str, ...]
    subject_ids: tuple[str, ...]
    unresolved: bool
    created_at: datetime
    detail: str
    priority: int
    integrity_seal: str


@dataclass(frozen=True)
class OperationalCheckpoint:
    checkpoint_id: str
    cycle_id: str
    wake_event_ids: tuple[str, ...]
    stage_records: tuple[StageExecutionRecord, ...]
    attention_ids: tuple[str, ...]
    status: str
    resume_safe: bool
    created_at: datetime
    detail: str
    integrity_seal: str


@dataclass(frozen=True)
class IdempotencyRecord:
    idempotency_key: str
    source_event_id: str
    decision_kind: str
    produced_record_id: str
    created_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class CycleOwnershipLease:
    lease_id: str
    source_event_id: str
    holder_id: str
    status: str
    acquired_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class CommandCenterReport:
    """Backend machine contract — not a large UI."""

    report_id: str
    cycle_id: str
    what_changed: tuple[str, ...]
    why_woke: tuple[str, ...]
    impacts: tuple[str, ...]
    human_actions: tuple[str, ...]
    execution_status: str
    warnings: tuple[str, ...]
    created_at: datetime
    integrity_seal: str
    artifact_references: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class CommandCenterState:
    """Rebuildable projection — NOT a second source of truth."""

    state_id: str
    latest_checkpoint_id: str | None
    unresolved_attention_ids: tuple[str, ...]
    last_wake_event_ids: tuple[str, ...]
    live_mutation_enabled: bool
    rebuilt_from_record_ids: tuple[str, ...]


@dataclass(frozen=True)
class CommandCenterCycleResult:
    result_kind: str
    failure_codes: tuple[str, ...]
    wake_events: tuple[WakeEvent, ...]
    checkpoint: OperationalCheckpoint | None
    attention_items: tuple[HumanAttentionItem, ...]
    report: CommandCenterReport | None
    state: CommandCenterState | None
    idempotency_hits: tuple[str, ...]
