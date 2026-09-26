from __future__ import annotations

from decimal import Decimal

from CommandCenterRuntime.models import (
    AdmittedResearchEvidenceFact,
    ApprovalTransitionFact,
    BrokerOrderFillFact,
    CapitalCashFact,
    DetectedChange,
    PolicySupersessionFact,
    PortfolioMembershipFact,
    PortfolioQuantityFact,
    ProviderFailureFact,
    ThesisTransitionFact,
)
from CommandCenterRuntime.vocabularies import (
    FAILURE_MISSING_NE_ZERO,
    WAKE_APPROVAL_TRANSITION,
    WAKE_BROKER_ORDER_OR_FILL,
    WAKE_CAPITAL_ORDERABLE_CASH_CHANGED,
    WAKE_POLICY_SUPERSEDED,
    WAKE_PORTFOLIO_MEMBERSHIP_CHANGED,
    WAKE_PORTFOLIO_QUANTITY_CHANGED,
    WAKE_PROVIDER_FAILURE,
    WAKE_RECONCILIATION_MISMATCH,
    WAKE_RESEARCH_EVIDENCE_ADMITTED,
    WAKE_SUBMISSION_OUTCOME_UNKNOWN,
    WAKE_THESIS_TRANSITION,
)


def detect_portfolio_membership_change(
    prior: PortfolioMembershipFact | None,
    current: PortfolioMembershipFact,
) -> DetectedChange | None:
    if prior is not None and prior.integrity_seal == current.integrity_seal:
        return None
    if prior is not None and prior.subject_ids == current.subject_ids:
        return None
    return DetectedChange(
        WAKE_PORTFOLIO_MEMBERSHIP_CHANGED,
        None if prior is None else prior.fact_id,
        current.fact_id,
        current.subject_ids,
        "membership set identity changed",
    )


def detect_portfolio_quantity_change(
    prior: PortfolioQuantityFact | None,
    current: PortfolioQuantityFact,
) -> DetectedChange | None:
    if type(current.quantity) is not Decimal or not current.quantity.is_finite():
        raise ValueError("quantity must be finite Decimal")
    if prior is not None and prior.integrity_seal == current.integrity_seal:
        return None
    if (
        prior is not None
        and prior.subject_id == current.subject_id
        and prior.quantity == current.quantity
    ):
        return None
    return DetectedChange(
        WAKE_PORTFOLIO_QUANTITY_CHANGED,
        None if prior is None else prior.fact_id,
        current.fact_id,
        (current.subject_id,),
        "quantity identity changed",
    )


def detect_capital_cash_change(
    prior: CapitalCashFact | None,
    current: CapitalCashFact,
) -> DetectedChange | None:
    """Exact presence+amount change. Missing ≠ 0 / unchanged / safe."""
    if current.presence not in {"present", "missing"}:
        raise ValueError("capital presence must be present|missing")
    if current.presence == "missing":
        if current.amount_krw is not None:
            raise ValueError("missing capital must carry amount_krw=None")
    else:
        if current.amount_krw is None:
            raise ValueError(FAILURE_MISSING_NE_ZERO)
        if type(current.amount_krw) is not Decimal or not current.amount_krw.is_finite():
            raise ValueError("amount_krw must be finite Decimal when present")
    if prior is not None and prior.integrity_seal == current.integrity_seal:
        return None
    if prior is not None and (
        prior.presence == current.presence
        and prior.amount_krw == current.amount_krw
        and prior.currency_code == current.currency_code
    ):
        return None
    return DetectedChange(
        WAKE_CAPITAL_ORDERABLE_CASH_CHANGED,
        None if prior is None else prior.fact_id,
        current.fact_id,
        (),
        f"orderable cash presence/amount changed ({current.presence})",
    )


def detect_research_evidence_admission(
    current: AdmittedResearchEvidenceFact,
) -> DetectedChange:
    if current.truth_class != "research_ai":
        # Still admissible as wake, but truth class must not be broker_fact.
        if current.truth_class == "broker_fact":
            raise ValueError("research evidence cannot claim broker_fact truth class")
    return DetectedChange(
        WAKE_RESEARCH_EVIDENCE_ADMITTED,
        None,
        current.fact_id,
        current.subject_ids,
        f"admitted evidence {current.evidence_id}",
    )


def detect_thesis_transition(current: ThesisTransitionFact) -> DetectedChange:
    return DetectedChange(
        WAKE_THESIS_TRANSITION,
        None,
        current.fact_id,
        (current.subject_id,),
        f"thesis state={current.state}",
    )


def detect_policy_supersession(current: PolicySupersessionFact) -> DetectedChange:
    return DetectedChange(
        WAKE_POLICY_SUPERSEDED,
        None,
        current.fact_id,
        (),
        f"policy {current.prior_policy_id} -> {current.new_policy_id}",
    )


def detect_approval_transition(current: ApprovalTransitionFact) -> DetectedChange:
    if current.gate_kind not in {
        "INVESTMENT_HUMAN_APPROVAL",
        "TRADE_EXECUTION_AUTHORIZATION",
    }:
        raise ValueError("gate_kind must be IHA or TEA; gates never merge")
    return DetectedChange(
        WAKE_APPROVAL_TRANSITION,
        None,
        current.fact_id,
        (),
        f"{current.gate_kind}:{current.decision}",
    )


def detect_broker_order_or_fill(current: BrokerOrderFillFact) -> DetectedChange:
    if current.outcome == "SUBMISSION_OUTCOME_UNKNOWN":
        kind = WAKE_SUBMISSION_OUTCOME_UNKNOWN
    elif current.outcome == "RECONCILIATION_MISMATCH":
        kind = WAKE_RECONCILIATION_MISMATCH
    else:
        kind = WAKE_BROKER_ORDER_OR_FILL
    return DetectedChange(
        kind,
        None,
        current.fact_id,
        (),
        f"broker outcome={current.outcome}",
    )


def detect_provider_failure(current: ProviderFailureFact) -> DetectedChange:
    return DetectedChange(
        WAKE_PROVIDER_FAILURE,
        None,
        current.fact_id,
        (),
        f"provider={current.provider_id} op={current.operation}",
    )
