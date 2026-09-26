from __future__ import annotations

from datetime import datetime

from CapitalAllocationCycle.integrity import integrity_seal
from CapitalAllocationCycle.models import (
    CapitalAllocationProposal,
    HumanInvestmentPolicy,
    InvestmentHumanApproval,
    SealedApprovedAllocationArtifact,
)
from CapitalAllocationCycle.validation import validate_artifact
from CapitalAllocationCycle.vocabularies import APPROVAL_DECISION_APPROVED
from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot


def seal_approved_allocation_artifact(
    *,
    artifact_id: str,
    approval: InvestmentHumanApproval,
    proposal: CapitalAllocationProposal,
    hip: HumanInvestmentPolicy,
    capital_snapshot: ExplicitCapitalSnapshot,
    sealed_at: datetime,
) -> SealedApprovedAllocationArtifact:
    """Sealed approved allocation for future Block C — no order payload."""
    if approval.decision != APPROVAL_DECISION_APPROVED:
        raise ValueError("artifact requires APPROVED decision")
    if approval.proposal_id != proposal.proposal_id:
        raise ValueError("artifact proposal binding mismatch")
    if approval.proposal_integrity_seal != proposal.integrity_seal:
        raise ValueError("artifact proposal seal mismatch")
    if approval.hip_integrity_seal != hip.integrity_seal:
        raise ValueError("artifact HIP seal mismatch")
    if approval.capital_snapshot_id != capital_snapshot.capital_snapshot_id:
        raise ValueError("artifact CapSnapshot binding mismatch")
    if proposal.executable is not False:
        raise ValueError("artifact must not carry executable proposal")
    payload = {
        "artifact_id": artifact_id,
        "approval_id": approval.approval_id,
        "proposal_id": proposal.proposal_id,
        "proposal_integrity_seal": proposal.integrity_seal,
        "approval_integrity_seal": approval.integrity_seal,
        "capital_snapshot_id": capital_snapshot.capital_snapshot_id,
        "hip_policy_id": hip.policy_id,
        "hip_version": hip.version,
        "hip_integrity_seal": hip.integrity_seal,
        "legs": tuple(
            (
                leg.allocation_leg_id,
                leg.portfolio_subject_id,
                leg.action,
                leg.current_market_value_krw,
                leg.proposed_market_value_krw,
                leg.delta_market_value_krw,
                leg.cash_funding_krw,
                leg.rotation_funding_krw,
                leg.executable,
            )
            for leg in proposal.legs
        ),
        "funding": (
            proposal.funding.deployable_orderable_cash_krw,
            proposal.funding.explicit_reserve_krw,
            proposal.funding.deployable_after_reserve_krw,
            proposal.funding.rotation_proceeds_krw,
            proposal.funding.cash_funded_increases_krw,
            proposal.funding.rotation_funded_increases_krw,
            proposal.funding.unused_deployable_krw,
        ),
        "sealed_at": sealed_at,
        # Explicit absence of order fields is part of the seal surface.
        "order_payload": None,
        "broker_order_ids": (),
        "ssam_fields": (),
    }
    artifact = SealedApprovedAllocationArtifact(
        artifact_id,
        approval.approval_id,
        proposal.proposal_id,
        proposal.integrity_seal,
        approval.integrity_seal,
        capital_snapshot.capital_snapshot_id,
        hip.policy_id,
        hip.version,
        hip.integrity_seal,
        proposal.legs,
        proposal.funding,
        sealed_at,
        integrity_seal(payload),
    )
    validate_artifact(artifact)
    return artifact
