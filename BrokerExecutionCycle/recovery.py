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
    FILL_CLAIM_UNKNOWN,
    RECOVERY_AMBIGUOUS,
    RECOVERY_HUMAN_REQUIRED,
    RECOVERY_STATE_ONLY,
)


def plan_submission_unknown_recovery(
    *,
    plan_id: str,
    acceptance: BrokerAcceptanceClassification,
    status_fact: OrderStatusFact | None,
) -> SubmissionRecoveryPlan:
    """C0-D5: SUBMISSION_OUTCOME_UNKNOWN → READ-only recovery.

    Auto recovery = STATE ONLY never reorder. Ambiguous → Human.
    """
    if acceptance.outcome != ACCEPTANCE_UNKNOWN:
        raise ValueError("recovery plan only for SUBMISSION_OUTCOME_UNKNOWN")

    if status_fact is None:
        mode = RECOVERY_HUMAN_REQUIRED
        requires_human = True
        detail = "no status fact; human required"
    elif status_fact.fill_claim == FILL_CLAIM_UNKNOWN:
        mode = RECOVERY_AMBIGUOUS
        requires_human = True
        detail = FAILURE_AMBIGUOUS_RECOVERY
    elif status_fact.broker_order_no and set(status_fact.broker_order_no.strip()) <= {"0"}:
        mode = RECOVERY_AMBIGUOUS
        requires_human = True
        detail = FAILURE_AMBIGUOUS_RECOVERY
    else:
        # State-only recovery: update local state from READ facts; never reorder.
        mode = RECOVERY_STATE_ONLY
        requires_human = False
        detail = "state-only recovery from SSQM2341; no reorder"

    payload = {
        "plan_id": plan_id,
        "attempt_id": acceptance.attempt_id,
        "recovery_mode": mode,
        "may_reorder": False,
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
