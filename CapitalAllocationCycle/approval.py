from __future__ import annotations

from datetime import datetime

from CapitalAllocationCycle.integrity import integrity_seal
from CapitalAllocationCycle.models import (
    CapitalAllocationProposal,
    HumanInvestmentPolicy,
    InvestmentHumanApproval,
)
from CapitalAllocationCycle.validation import validate_approval, validate_proposal
from CapitalAllocationCycle.vocabularies import (
    APPROVAL_DECISION_APPROVED,
    APPROVAL_DECISION_NEEDS_REVISION,
    APPROVAL_DECISION_REJECTED,
)
from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot


def _approval_payload(
    *,
    approval_id: str,
    decision: str,
    proposal: CapitalAllocationProposal,
    hip: HumanInvestmentPolicy,
    capital_snapshot: ExplicitCapitalSnapshot,
    principal: str,
    decided_at: datetime,
    rationale: str,
) -> dict:
    return {
        "approval_id": approval_id,
        "decision": decision,
        "proposal_id": proposal.proposal_id,
        "proposal_integrity_seal": proposal.integrity_seal,
        "capital_snapshot_id": capital_snapshot.capital_snapshot_id,
        "hip_policy_id": hip.policy_id,
        "hip_version": hip.version,
        "hip_integrity_seal": hip.integrity_seal,
        "cio_decision_ids": proposal.cio_decision_ids,
        "principal": principal,
        "decided_at": decided_at,
        "rationale": rationale,
    }


def record_investment_human_approval(
    *,
    approval_id: str,
    decision: str,
    proposal: CapitalAllocationProposal,
    hip: HumanInvestmentPolicy,
    capital_snapshot: ExplicitCapitalSnapshot,
    principal: str,
    decided_at: datetime,
    rationale: str,
) -> InvestmentHumanApproval:
    """Bind exact proposal seal + CapSnapshot + HIP version/seal + CIO refs."""
    validate_proposal(proposal)
    if decision not in (
        APPROVAL_DECISION_APPROVED,
        APPROVAL_DECISION_REJECTED,
        APPROVAL_DECISION_NEEDS_REVISION,
    ):
        raise ValueError("approval decision invalid")
    if proposal.hip_integrity_seal != hip.integrity_seal:
        raise ValueError("approval HIP seal mismatch")
    if proposal.hip_policy_id != hip.policy_id or proposal.hip_version != hip.version:
        raise ValueError("approval HIP identity mismatch")
    if proposal.capital_snapshot_id != capital_snapshot.capital_snapshot_id:
        raise ValueError("approval CapSnapshot binding mismatch")
    if hip.approval_required is not True:
        raise ValueError("HIP requires human approval")
    if decision == APPROVAL_DECISION_APPROVED and proposal.executable is not False:
        raise ValueError("cannot approve executable proposal in Block B")
    payload = _approval_payload(
        approval_id=approval_id,
        decision=decision,
        proposal=proposal,
        hip=hip,
        capital_snapshot=capital_snapshot,
        principal=principal,
        decided_at=decided_at,
        rationale=rationale,
    )
    approval = InvestmentHumanApproval(
        approval_id,
        decision,
        proposal.proposal_id,
        proposal.integrity_seal,
        capital_snapshot.capital_snapshot_id,
        hip.policy_id,
        hip.version,
        hip.integrity_seal,
        proposal.cio_decision_ids,
        principal,
        decided_at,
        rationale,
        integrity_seal(payload),
    )
    validate_approval(approval)
    return approval
