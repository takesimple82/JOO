from __future__ import annotations

from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.models import (
    BrokerAcceptanceClassification,
    OrderStatusFact,
    SubmissionRecoveryPlan,
)
from BrokerExecutionCycle.vocabularies import (
    ACCEPTANCE_UNKNOWN,
    FAILURE_AMBIGUOUS_RECOVERY,
    FAILURE_AUTO_RESUBMIT_FORBIDDEN,
    FILL_CLAIM_UNKNOWN,
    RECOVERY_AMBIGUOUS,
    RECOVERY_HUMAN_REQUIRED,
    RECOVERY_POLICY_QUERY_THEN_HUMAN,
    RECOVERY_STATE_ONLY,
)


def plan_submission_unknown_recovery(
    *,
    plan_id: str,
    acceptance: BrokerAcceptanceClassification,
    status_fact: OrderStatusFact | None,
) -> SubmissionRecoveryPlan:
    """E — UNKNOWN → QUERY_RECOVER_THEN_HUMAN_IF_AMBIGUOUS.

    Auto recovery = STATE ONLY never reorder / never auto-resubmit.
    Ambiguous or missing status → HumanAttention.
    """
    if acceptance.outcome != ACCEPTANCE_UNKNOWN:
        raise ValueError("recovery plan only for SUBMISSION_OUTCOME_UNKNOWN")

    if status_fact is None:
        mode = RECOVERY_HUMAN_REQUIRED
        requires_human = True
        detail = f"{RECOVERY_POLICY_QUERY_THEN_HUMAN}; no status fact; human required"
    elif status_fact.fill_claim == FILL_CLAIM_UNKNOWN:
        mode = RECOVERY_AMBIGUOUS
        requires_human = True
        detail = f"{RECOVERY_POLICY_QUERY_THEN_HUMAN}; {FAILURE_AMBIGUOUS_RECOVERY}"
    elif status_fact.broker_order_no and set(status_fact.broker_order_no.strip()) <= {"0"}:
        mode = RECOVERY_AMBIGUOUS
        requires_human = True
        detail = f"{RECOVERY_POLICY_QUERY_THEN_HUMAN}; {FAILURE_AMBIGUOUS_RECOVERY}"
    else:
        # State-only recovery: update local state from READ facts; never reorder.
        mode = RECOVERY_STATE_ONLY
        requires_human = False
        detail = (
            f"{RECOVERY_POLICY_QUERY_THEN_HUMAN}; "
            "state-only recovery from SSQM2341; no reorder; no auto-resubmit"
        )

    payload = {
        "plan_id": plan_id,
        "attempt_id": acceptance.attempt_id,
        "recovery_mode": mode,
        "recovery_policy": RECOVERY_POLICY_QUERY_THEN_HUMAN,
        "may_reorder": False,
        "may_autoresubmit": False,
        "requires_human": requires_human,
        "detail": detail,
    }
    return SubmissionRecoveryPlan(
        plan_id,
        acceptance.attempt_id,
        mode,
        False,
        requires_human,
        detail,
        integrity_seal(payload),
    )


def assert_unknown_must_not_autoresubmit(*, may_reorder: bool, may_autoresubmit: bool) -> None:
    if may_reorder or may_autoresubmit:
        raise RuntimeError(FAILURE_AUTO_RESUBMIT_FORBIDDEN)
