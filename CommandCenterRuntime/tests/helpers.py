from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from CommandCenterRuntime.change_detection import (
    detect_capital_cash_change,
    detect_portfolio_membership_change,
    detect_portfolio_quantity_change,
    detect_provider_failure,
    detect_research_evidence_admission,
    detect_broker_order_or_fill,
    detect_policy_supersession,
    detect_thesis_transition,
    detect_approval_transition,
)
from CommandCenterRuntime.integrity import integrity_seal
from CommandCenterRuntime.models import (
    AdmittedResearchEvidenceFact,
    ApprovalTransitionFact,
    BrokerOrderFillFact,
    CapitalCashFact,
    PolicySupersessionFact,
    PortfolioMembershipFact,
    PortfolioQuantityFact,
    ProviderFailureFact,
    ThesisTransitionFact,
)
from CommandCenterRuntime.service import seal_wake_from_change
from CommandCenterRuntime.wake import seal_wake_event


NOW = datetime(2026, 9, 26, 15, 35, tzinfo=timezone.utc)


def membership(fact_id: str, subjects: tuple[str, ...]) -> PortfolioMembershipFact:
    payload = {
        "fact_id": fact_id,
        "subject_ids": subjects,
        "observed_at": NOW,
    }
    return PortfolioMembershipFact(
        fact_id, subjects, NOW, integrity_seal(payload)
    )


def quantity(fact_id: str, subject: str, qty: str) -> PortfolioQuantityFact:
    q = Decimal(qty)
    payload = {
        "fact_id": fact_id,
        "subject_id": subject,
        "quantity": q,
        "observed_at": NOW,
    }
    return PortfolioQuantityFact(fact_id, subject, q, NOW, integrity_seal(payload))


def cash(fact_id: str, presence: str, amount: str | None) -> CapitalCashFact:
    amt = None if amount is None else Decimal(amount)
    payload = {
        "fact_id": fact_id,
        "presence": presence,
        "amount_krw": amt,
        "currency_code": "KRW",
        "observed_at": NOW,
    }
    return CapitalCashFact(
        fact_id, presence, amt, "KRW", NOW, integrity_seal(payload)
    )


def research(fact_id: str, evidence_id: str, subjects: tuple[str, ...]) -> AdmittedResearchEvidenceFact:
    payload = {
        "fact_id": fact_id,
        "evidence_id": evidence_id,
        "research_id": "r1",
        "subject_ids": subjects,
        "truth_class": "research_ai",
        "observed_at": NOW,
    }
    return AdmittedResearchEvidenceFact(
        fact_id, evidence_id, "r1", subjects, "research_ai", NOW, integrity_seal(payload)
    )


def thesis(fact_id: str, state: str, subject: str = "S1") -> ThesisTransitionFact:
    payload = {
        "fact_id": fact_id,
        "transition_id": "t1",
        "subject_id": subject,
        "state": state,
        "observed_at": NOW,
    }
    return ThesisTransitionFact(
        fact_id, "t1", subject, state, NOW, integrity_seal(payload)
    )


def policy(fact_id: str) -> PolicySupersessionFact:
    payload = {
        "fact_id": fact_id,
        "prior_policy_id": "hip-v1",
        "new_policy_id": "hip-v1b",
        "new_policy_seal": "seal",
        "observed_at": NOW,
    }
    return PolicySupersessionFact(
        fact_id, "hip-v1", "hip-v1b", "seal", NOW, integrity_seal(payload)
    )


def approval(fact_id: str, gate: str, decision: str) -> ApprovalTransitionFact:
    payload = {
        "fact_id": fact_id,
        "gate_kind": gate,
        "approval_or_authorization_id": "a1",
        "decision": decision,
        "bound_artifact_id": "art1",
        "observed_at": NOW,
    }
    return ApprovalTransitionFact(
        fact_id, gate, "a1", decision, "art1", NOW, integrity_seal(payload)
    )


def broker(fact_id: str, outcome: str) -> BrokerOrderFillFact:
    payload = {
        "fact_id": fact_id,
        "attempt_id": "att1",
        "outcome": outcome,
        "broker_order_no": None,
        "observed_at": NOW,
    }
    return BrokerOrderFillFact(
        fact_id, "att1", outcome, None, NOW, integrity_seal(payload)
    )


def provider_fail(fact_id: str) -> ProviderFailureFact:
    payload = {
        "fact_id": fact_id,
        "provider_id": "kb",
        "operation": "SSQM0004",
        "detail": "timeout",
        "observed_at": NOW,
    }
    return ProviderFailureFact(
        fact_id, "kb", "SSQM0004", "timeout", NOW, integrity_seal(payload)
    )


def wake_from_detected(wake_id: str, change, source: str = "FactStore"):
    return seal_wake_from_change(
        wake_event_id=wake_id,
        change=change,
        source=source,
        observed_at=NOW,
        provenance="test-provenance",
    )


__all__ = [
    "NOW",
    "approval",
    "broker",
    "cash",
    "detect_approval_transition",
    "detect_broker_order_or_fill",
    "detect_capital_cash_change",
    "detect_policy_supersession",
    "detect_portfolio_membership_change",
    "detect_portfolio_quantity_change",
    "detect_provider_failure",
    "detect_research_evidence_admission",
    "detect_thesis_transition",
    "membership",
    "policy",
    "provider_fail",
    "quantity",
    "research",
    "seal_wake_event",
    "thesis",
    "wake_from_detected",
]
