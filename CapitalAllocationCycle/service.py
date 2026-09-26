from __future__ import annotations

from datetime import datetime

from CapitalAllocationCycle.allocator import allocate_capital
from CapitalAllocationCycle.approval import record_investment_human_approval
from CapitalAllocationCycle.artifact import seal_approved_allocation_artifact
from CapitalAllocationCycle.hip import build_frozen_hip_v1
from CapitalAllocationCycle.models import (
    CapitalAllocationPlaneResult,
    CapitalAllocationProposal,
    CapitalAllocationRequest,
    HumanInvestmentPolicy,
    InvestmentHumanApproval,
    SealedApprovedAllocationArtifact,
)
from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot


def run_capital_allocation_cycle(
    request: CapitalAllocationRequest,
) -> CapitalAllocationPlaneResult:
    """Compose deterministic allocation + fail-closed constraints. No orders."""
    return allocate_capital(request)


def approve_capital_allocation(
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
    return record_investment_human_approval(
        approval_id=approval_id,
        decision=decision,
        proposal=proposal,
        hip=hip,
        capital_snapshot=capital_snapshot,
        principal=principal,
        decided_at=decided_at,
        rationale=rationale,
    )


def seal_approved_allocation(
    *,
    artifact_id: str,
    approval: InvestmentHumanApproval,
    proposal: CapitalAllocationProposal,
    hip: HumanInvestmentPolicy,
    capital_snapshot: ExplicitCapitalSnapshot,
    sealed_at: datetime,
) -> SealedApprovedAllocationArtifact:
    return seal_approved_allocation_artifact(
        artifact_id=artifact_id,
        approval=approval,
        proposal=proposal,
        hip=hip,
        capital_snapshot=capital_snapshot,
        sealed_at=sealed_at,
    )


__all__ = [
    "allocate_capital",
    "approve_capital_allocation",
    "build_frozen_hip_v1",
    "run_capital_allocation_cycle",
    "seal_approved_allocation",
]
