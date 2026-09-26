from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from typing import TYPE_CHECKING

from InvestmentDecisionVerticalSlice.models import (
    CioDecisionRecord,
    OpportunityComparison,
    OpportunityEvaluation,
)
from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot

if TYPE_CHECKING:
    # Avoid runtime import of OperationalCioCycle (pulls codec → circular with this package).
    from OperationalCioCycle.models import OpportunityUniverse


@dataclass(frozen=True)
class HumanInvestmentPolicy:
    """Immutable human investment policy with explicit reserve and integrity seal."""

    policy_id: str
    version: str
    effective_at: datetime
    currency_code: str
    deployable_capital_mode: str
    explicit_reserve_krw: Decimal
    max_position_market_value_krw: Decimal
    capital_sourcing_mode: str
    on_invalidate_thesis: str
    leverage_allowed: bool
    approval_required: bool
    profit_realization_mode: str
    integrity_seal: str


@dataclass(frozen=True)
class ResolvedExactAmount:
    """Present zero is distinct from missing — never coerce missing to 0."""

    fact_id: str
    presence: str
    amount_krw: Decimal | None
    currency_code: str


@dataclass(frozen=True)
class PositionCapitalView:
    portfolio_subject_id: str
    market_value_fact_id: str
    presence: str
    market_value_krw: Decimal | None
    currency_code: str


@dataclass(frozen=True)
class ProposedSubjectNotional:
    """NON-EXECUTABLE KRW notional intent. No broker order payload."""

    allocation_leg_id: str
    portfolio_subject_id: str
    proposed_market_value_krw: Decimal
    capital_bucket_id: str | None
    risk_budget_id: str | None
    rotation_funding_subject_ids: tuple[str, ...]


@dataclass(frozen=True)
class CapitalAllocationRequest:
    request_id: str
    created_at: datetime
    hip: HumanInvestmentPolicy
    capital_snapshot: ExplicitCapitalSnapshot
    orderable_cash: ResolvedExactAmount
    position_values: tuple[PositionCapitalView, ...]
    universe: OpportunityUniverse
    cio_decisions: tuple[CioDecisionRecord, ...]
    evaluations: tuple[OpportunityEvaluation, ...]
    comparisons: tuple[OpportunityComparison, ...]
    proposed_notionals: tuple[ProposedSubjectNotional, ...]


@dataclass(frozen=True)
class AllocationLegProposal:
    allocation_leg_id: str
    portfolio_subject_id: str
    action: str
    current_market_value_krw: Decimal
    proposed_market_value_krw: Decimal
    delta_market_value_krw: Decimal
    capital_bucket_id: str | None
    risk_budget_id: str | None
    rotation_funding_subject_ids: tuple[str, ...]
    cash_funding_krw: Decimal
    rotation_funding_krw: Decimal
    executable: bool


@dataclass(frozen=True)
class CapitalFundingProvenance:
    deployable_orderable_cash_krw: Decimal
    explicit_reserve_krw: Decimal
    deployable_after_reserve_krw: Decimal
    rotation_proceeds_krw: Decimal
    cash_funded_increases_krw: Decimal
    rotation_funded_increases_krw: Decimal
    unused_deployable_krw: Decimal


@dataclass(frozen=True)
class ConstraintFinding:
    code: str
    status: str
    allocation_leg_id: str | None
    detail: str


@dataclass(frozen=True)
class CapitalAllocationProposal:
    proposal_id: str
    request_id: str
    created_at: datetime
    hip_policy_id: str
    hip_version: str
    hip_integrity_seal: str
    capital_snapshot_id: str
    orderable_cash_fact_id: str
    currency_code: str
    legs: tuple[AllocationLegProposal, ...]
    funding: CapitalFundingProvenance
    constraint_findings: tuple[ConstraintFinding, ...]
    cio_decision_ids: tuple[str, ...]
    comparison_ids: tuple[str, ...]
    universe_id: str
    executable: bool
    integrity_seal: str


@dataclass(frozen=True)
class CapitalAllocationPlaneResult:
    result_kind: str
    failure_codes: tuple[str, ...]
    proposal: CapitalAllocationProposal | None


@dataclass(frozen=True)
class InvestmentHumanApproval:
    approval_id: str
    decision: str
    proposal_id: str
    proposal_integrity_seal: str
    capital_snapshot_id: str
    hip_policy_id: str
    hip_version: str
    hip_integrity_seal: str
    cio_decision_ids: tuple[str, ...]
    principal: str
    decided_at: datetime
    rationale: str
    integrity_seal: str


@dataclass(frozen=True)
class SealedApprovedAllocationArtifact:
    """Sealed artifact for future Block C — contains no order payload."""

    artifact_id: str
    approval_id: str
    proposal_id: str
    proposal_integrity_seal: str
    approval_integrity_seal: str
    capital_snapshot_id: str
    hip_policy_id: str
    hip_version: str
    hip_integrity_seal: str
    legs: tuple[AllocationLegProposal, ...]
    funding: CapitalFundingProvenance
    sealed_at: datetime
    integrity_seal: str
