from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class QuoteFact:
    """IVU10140-normalized quote / trade-unit fact. READ only."""

    fact_id: str
    instrument_ssam_is_cd: str
    now_price: Decimal
    trade_quantity_unit: Decimal
    currency_code: str
    collected_at: datetime
    raw_envelope_id: str
    integrity_seal: str


@dataclass(frozen=True)
class OrderableCashFact:
    """SSQM0004 / SSQM1802 orderable cash. Present zero ≠ missing."""

    fact_id: str
    presence: str
    amount_krw: Decimal | None
    currency_code: str
    broker_field: str
    collected_at: datetime
    raw_envelope_id: str
    integrity_seal: str


@dataclass(frozen=True)
class SellableQuantityFact:
    """SSQM1801 / holdings ordr_psbl_q sellability. Present zero ≠ missing."""

    fact_id: str
    instrument_ssam_is_cd: str
    presence: str
    sellable_qty: Decimal | None
    collected_at: datetime
    raw_envelope_id: str
    integrity_seal: str


@dataclass(frozen=True)
class OrderStatusFact:
    """SSQM2341 status/fill observation. Do not overclaim fills."""

    fact_id: str
    query_order_no: str | None
    query_order_date: str | None
    process_flag: str | None
    broker_order_no: str | None
    fill_claim: str
    filled_qty: Decimal | None
    filled_amount_krw: Decimal | None
    raw_message: str | None
    collected_at: datetime
    raw_envelope_id: str
    integrity_seal: str


@dataclass(frozen=True)
class InstrumentIdentityBinding:
    """Deterministic holdings↔SSAM bridge. Fail closed if unproven."""

    binding_id: str
    portfolio_subject_id: str
    holdings_is_cd: str
    ssam_is_cd: str
    proven: bool
    integrity_seal: str


@dataclass(frozen=True)
class VerifiedExecutionAccountBinding:
    """Verified account binding. No secrets. Mutation false until verified."""

    binding_id: str
    account_selector: str
    gnl_ac_no1: str
    status: str
    verified_at: datetime | None
    verification_method: str
    mutation_eligible: bool
    integrity_seal: str


@dataclass(frozen=True)
class SessionContextFact:
    session_id: str
    market_time_class: str
    collected_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class ProposedLimitPrice:
    """Human/deterministic bound limit price. No AI. No market fallback."""

    proposal_id: str
    instrument_ssam_is_cd: str
    limit_price: Decimal
    currency_code: str
    bound_at: datetime
    principal: str
    integrity_seal: str


@dataclass(frozen=True)
class PreTradeFactBundle:
    bundle_id: str
    quote: QuoteFact
    orderable_cash: OrderableCashFact
    sellable: SellableQuantityFact | None
    instrument: InstrumentIdentityBinding
    account: VerifiedExecutionAccountBinding
    session: SessionContextFact
    proposed_limit_price: ProposedLimitPrice
    collected_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class PreTradeValidationFinding:
    code: str
    status: str
    detail: str


@dataclass(frozen=True)
class PreTradeValidationResult:
    validation_id: str
    bundle_id: str
    bundle_integrity_seal: str
    side: str
    approved_notional_krw: Decimal
    raw_qty: Decimal | None
    derived_qty: Decimal | None
    derived_notional_krw: Decimal | None
    passed: bool
    findings: tuple[PreTradeValidationFinding, ...]
    validated_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class OrderIntent:
    """Immutable sealed LIMIT intent. ordr_ccd=00. No ordr_no/fill yet."""

    intent_id: str
    side: str
    order_kind: str
    ordr_ccd: str
    portfolio_subject_id: str
    ssam_is_cd: str
    limit_price: Decimal
    quantity: Decimal
    approved_notional_krw: Decimal
    derived_notional_krw: Decimal
    currency_code: str
    allocation_artifact_id: str
    allocation_artifact_seal: str
    approval_id: str
    approval_seal: str
    pretrade_validation_id: str
    pretrade_validation_seal: str
    proposed_limit_price_id: str
    proposed_limit_price_seal: str
    account_binding_id: str
    account_binding_seal: str
    instrument_binding_id: str
    instrument_binding_seal: str
    sealed_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class TradeExecutionAuthorization:
    """Separate TEA. Binds exact OrderIntent seal. One-shot."""

    authorization_id: str
    order_intent_id: str
    order_intent_seal: str
    allocation_artifact_id: str
    allocation_artifact_seal: str
    approval_id: str
    approval_seal: str
    account_binding_id: str
    account_binding_seal: str
    authorized_at: datetime
    principal: str
    one_shot: bool
    integrity_seal: str


@dataclass(frozen=True)
class MutationAuthorityState:
    """Durable one-shot consumption tracker (in-memory / caller-owned)."""

    authorization_id: str
    tea_seal: str
    consumed: bool
    attempt_id: str | None
    payload_hash: str | None
    consumed_at: datetime | None


@dataclass(frozen=True)
class SsamRequestTranslation:
    """Documented SSAM fields only. Unresolved → NOT READY."""

    translation_id: str
    api_path: str
    side: str
    data_body: dict
    unresolved_fields: tuple[str, ...]
    ready: bool
    payload_hash: str
    order_intent_id: str
    order_intent_seal: str
    integrity_seal: str


@dataclass(frozen=True)
class BrokerSubmitAttempt:
    attempt_id: str
    authorization_id: str
    tea_seal: str
    order_intent_id: str
    order_intent_seal: str
    translation_id: str
    payload_hash: str
    transport_mode: str
    attempted_at: datetime
    durable_pre_send: bool
    integrity_seal: str


@dataclass(frozen=True)
class BrokerAcceptanceClassification:
    classification_id: str
    attempt_id: str
    outcome: str
    process_flag: str | None
    broker_order_no: str | None
    http_status: int | None
    raw_message: str | None
    classified_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class SubmissionRecoveryPlan:
    plan_id: str
    attempt_id: str
    recovery_mode: str
    may_reorder: bool
    requires_human: bool
    detail: str
    integrity_seal: str


@dataclass(frozen=True)
class FillFact:
    """Separate from acceptance. Fail closed when samples insufficient."""

    fact_id: str
    broker_order_no: str | None
    fill_claim: str
    filled_qty: Decimal | None
    filled_amount_krw: Decimal | None
    status_fact_id: str | None
    observed_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class ReconciliationResult:
    result_id: str
    attempt_id: str
    acceptance_outcome: str
    fill_claim: str
    status: str
    cash_corroborated: bool | None
    holdings_corroborated: bool | None
    detail: str
    reconciled_at: datetime
    integrity_seal: str


@dataclass(frozen=True)
class BrokerExecutionCycleResult:
    result_kind: str
    failure_codes: tuple[str, ...]
    order_intent: OrderIntent | None
    tea: TradeExecutionAuthorization | None
    attempt: BrokerSubmitAttempt | None
    acceptance: BrokerAcceptanceClassification | None
    recovery: SubmissionRecoveryPlan | None
    fill: FillFact | None
    reconciliation: ReconciliationResult | None
