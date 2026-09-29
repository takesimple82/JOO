"""Phase 4 C — Open LIMIT policy: human-only monitoring + cancel escalation.

No automatic cancel / modify / reprice / chase / market conversion of an open
LIMIT. Monitor → reconcile → HumanAttention → Human decides.
SSAM1805/1806 remain draft-only; DEFERRED_NO_AUTO_POLICY stays compatible.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from BrokerExecutionCycle.authority_evidence import CANCEL_MODIFY_AUTO_POLICY
from BrokerExecutionCycle.cancel_modify import (
    CANCEL_MODIFY_POLICY,
    assert_no_auto_cancel_modify,
)
from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.models import OrderStatusFact
from BrokerExecutionCycle.vocabularies import (
    FAILURE_OPEN_LIMIT_AUTO_POLICY,
    FILL_CLAIM_FULL,
    FILL_CLAIM_NONE,
    FILL_CLAIM_PARTIAL,
    FILL_CLAIM_UNKNOWN,
    OPEN_LIMIT_POLICY,
)


OPEN_LIMIT_STATUS_OPEN = "OPEN_LIMIT_REMAINING"
OPEN_LIMIT_STATUS_UNKNOWN = "OPEN_LIMIT_STATUS_UNKNOWN"
OPEN_LIMIT_STATUS_CLOSED = "OPEN_LIMIT_CLOSED"


@dataclass(frozen=True)
class OpenLimitHumanAttentionSignal:
    """Safety-critical open-LIMIT escalation. No secrets. No auto mutation."""

    signal_id: str
    account_binding_id: str
    broker_order_no: str | None
    status: str
    ordered_qty: Decimal | None
    filled_qty: Decimal | None
    remaining_qty: Decimal | None
    why_human_needed: str
    auto_policy: str
    open_limit_policy: str
    observed_at: datetime
    integrity_seal: str


def classify_open_limit_status(status_fact: OrderStatusFact) -> str:
    if type(status_fact) is not OrderStatusFact:
        raise TypeError("OrderStatusFact required")
    if status_fact.fill_claim == FILL_CLAIM_UNKNOWN:
        return OPEN_LIMIT_STATUS_UNKNOWN
    if status_fact.fill_claim == FILL_CLAIM_FULL:
        return OPEN_LIMIT_STATUS_CLOSED
    remaining = status_fact.remaining_qty
    if remaining is not None and type(remaining) is Decimal and remaining > Decimal("0"):
        return OPEN_LIMIT_STATUS_OPEN
    if status_fact.fill_claim in (FILL_CLAIM_NONE, FILL_CLAIM_PARTIAL):
        # Remaining unknown but not full → treat as open requiring human view.
        return OPEN_LIMIT_STATUS_OPEN
    return OPEN_LIMIT_STATUS_UNKNOWN


def seal_open_limit_human_attention(
    *,
    signal_id: str,
    account_binding_id: str,
    status_fact: OrderStatusFact,
    observed_at: datetime,
) -> OpenLimitHumanAttentionSignal:
    """Build HumanAttention payload for an open/ambiguous LIMIT. Never auto-acts."""
    if CANCEL_MODIFY_POLICY != CANCEL_MODIFY_AUTO_POLICY:
        raise RuntimeError(FAILURE_OPEN_LIMIT_AUTO_POLICY)
    if OPEN_LIMIT_POLICY != "HUMAN_ONLY_MONITOR_CANCEL_ESCALATION":
        raise RuntimeError(FAILURE_OPEN_LIMIT_AUTO_POLICY)
    if type(account_binding_id) is not str or account_binding_id.strip() == "":
        raise ValueError("account_binding_id required")
    status = classify_open_limit_status(status_fact)
    if status == OPEN_LIMIT_STATUS_CLOSED:
        raise ValueError("closed LIMIT does not require open-limit attention")
    if status == OPEN_LIMIT_STATUS_UNKNOWN:
        why = (
            "open LIMIT status UNKNOWN after query; "
            "QUERY_RECOVER_THEN_HUMAN_IF_AMBIGUOUS; no auto cancel/modify/resubmit"
        )
    else:
        why = (
            "open LIMIT remains with remaining quantity; "
            "human must decide cancel/modify; no automatic action"
        )
    # Provenance only — never include secrets / passwords / tokens.
    broker_order_no = status_fact.broker_order_no
    payload = {
        "signal_id": signal_id,
        "account_binding_id": account_binding_id,
        "broker_order_no": broker_order_no,
        "status": status,
        "ordered_qty": status_fact.ordered_qty,
        "filled_qty": status_fact.filled_qty,
        "remaining_qty": status_fact.remaining_qty,
        "why_human_needed": why,
        "auto_policy": CANCEL_MODIFY_AUTO_POLICY,
        "open_limit_policy": OPEN_LIMIT_POLICY,
        "observed_at": observed_at,
    }
    return OpenLimitHumanAttentionSignal(
        signal_id,
        account_binding_id,
        broker_order_no,
        status,
        status_fact.ordered_qty,
        status_fact.filled_qty,
        status_fact.remaining_qty,
        why,
        CANCEL_MODIFY_AUTO_POLICY,
        OPEN_LIMIT_POLICY,
        observed_at,
        integrity_seal(payload),
    )


def assert_open_limit_never_auto_mutates() -> None:
    """Hard stop: open LIMIT path must not auto-submit SSAM1805/1806."""
    assert_no_auto_cancel_modify()
