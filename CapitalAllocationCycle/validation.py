from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from CapitalAllocationCycle.hip import verify_hip_integrity
from CapitalAllocationCycle.models import (
    CapitalAllocationProposal,
    CapitalAllocationRequest,
    HumanInvestmentPolicy,
    InvestmentHumanApproval,
    PositionCapitalView,
    ProposedSubjectNotional,
    ResolvedExactAmount,
    SealedApprovedAllocationArtifact,
)
from CapitalAllocationCycle.vocabularies import (
    AMOUNT_PRESENCE_MISSING,
    AMOUNT_PRESENCE_PRESENT,
    APPROVAL_DECISION_APPROVED,
    APPROVAL_DECISION_NEEDS_REVISION,
    APPROVAL_DECISION_REJECTED,
    CAPITAL_SOURCING_MODE_ROTATION_ALLOWED,
    CURRENCY_KRW,
    DEPLOYABLE_CAPITAL_MODE_ORDERABLE_CASH_FULL,
    ON_INVALIDATE_THESIS_BLOCK_AND_ALLOW_REDUCE_LEGS,
    PROFIT_REALIZATION_MODE_DEFER,
)
from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot
from KbCapitalFactAuthority.vocabularies import SIZING_AUTHORITY_NONE


def nonblank(name: str, value: object) -> None:
    if type(value) is not str:
        raise TypeError(f"{name} must be str")
    if value.strip() == "":
        raise ValueError(f"{name} must not be blank")


def require_utc(name: str, value: object) -> None:
    if type(value) is not datetime:
        raise TypeError(f"{name} must be datetime")
    if value.tzinfo is not timezone.utc:
        raise ValueError(f"{name} must use datetime.timezone.utc")


def require_finite_decimal(name: str, value: object) -> Decimal:
    if type(value) is not Decimal:
        raise TypeError(f"{name} must be Decimal")
    if not value.is_finite():
        raise ValueError(f"{name} must be finite")
    return value


def require_nonnegative_decimal(name: str, value: object) -> Decimal:
    amount = require_finite_decimal(name, value)
    if amount < Decimal("0"):
        raise ValueError(f"{name} must be nonnegative")
    return amount


def validate_resolved_amount(amount: ResolvedExactAmount, *, expected_fact_id: str) -> None:
    if type(amount) is not ResolvedExactAmount:
        raise TypeError("orderable_cash must be ResolvedExactAmount")
    nonblank("fact_id", amount.fact_id)
    if amount.fact_id != expected_fact_id:
        raise ValueError("resolved amount fact_id must bind CapSnapshot orderable cash")
    if amount.currency_code != CURRENCY_KRW:
        raise ValueError("resolved amount currency must be KRW")
    if amount.presence == AMOUNT_PRESENCE_MISSING:
        if amount.amount_krw is not None:
            raise ValueError("missing amount must not carry Decimal")
        return
    if amount.presence != AMOUNT_PRESENCE_PRESENT:
        raise ValueError("amount presence invalid")
    require_nonnegative_decimal("amount_krw", amount.amount_krw)


def validate_position_view(view: PositionCapitalView) -> None:
    if type(view) is not PositionCapitalView:
        raise TypeError("position view must be PositionCapitalView")
    nonblank("portfolio_subject_id", view.portfolio_subject_id)
    nonblank("market_value_fact_id", view.market_value_fact_id)
    if view.currency_code != CURRENCY_KRW:
        raise ValueError("position currency must be KRW")
    if view.presence == AMOUNT_PRESENCE_MISSING:
        if view.market_value_krw is not None:
            raise ValueError("missing position MV must not carry Decimal")
        return
    if view.presence != AMOUNT_PRESENCE_PRESENT:
        raise ValueError("position presence invalid")
    require_nonnegative_decimal("market_value_krw", view.market_value_krw)


def validate_proposed_notional(item: ProposedSubjectNotional) -> None:
    if type(item) is not ProposedSubjectNotional:
        raise TypeError("proposed notional must be ProposedSubjectNotional")
    nonblank("allocation_leg_id", item.allocation_leg_id)
    nonblank("portfolio_subject_id", item.portfolio_subject_id)
    require_nonnegative_decimal(
        "proposed_market_value_krw", item.proposed_market_value_krw
    )
    if item.capital_bucket_id is not None:
        nonblank("capital_bucket_id", item.capital_bucket_id)
    if item.risk_budget_id is not None:
        nonblank("risk_budget_id", item.risk_budget_id)
        if item.capital_bucket_id is None:
            raise ValueError("risk_budget_id requires capital_bucket_id structural link")
    if type(item.rotation_funding_subject_ids) is not tuple:
        raise TypeError("rotation_funding_subject_ids must be tuple")
    seen = set()
    for subject_id in item.rotation_funding_subject_ids:
        nonblank("rotation_funding_subject_id", subject_id)
        if subject_id in seen:
            raise ValueError("duplicate rotation funding subject")
        if subject_id == item.portfolio_subject_id:
            raise ValueError("rotation funding subject must differ from target")
        seen.add(subject_id)


def validate_human_investment_policy(hip: HumanInvestmentPolicy) -> None:
    if type(hip) is not HumanInvestmentPolicy:
        raise TypeError("hip must be HumanInvestmentPolicy")
    nonblank("policy_id", hip.policy_id)
    nonblank("version", hip.version)
    require_utc("effective_at", hip.effective_at)
    if hip.currency_code != CURRENCY_KRW:
        raise ValueError("HIP currency must be KRW domestic")
    if hip.deployable_capital_mode != DEPLOYABLE_CAPITAL_MODE_ORDERABLE_CASH_FULL:
        raise ValueError("HIP deployable_capital_mode must be ORDERABLE_CASH_FULL")
    # Explicit zero reserve must be present Decimal("0"), never a missing field.
    require_nonnegative_decimal("explicit_reserve_krw", hip.explicit_reserve_krw)
    require_nonnegative_decimal(
        "max_position_market_value_krw", hip.max_position_market_value_krw
    )
    if hip.capital_sourcing_mode != CAPITAL_SOURCING_MODE_ROTATION_ALLOWED:
        raise ValueError("HIP capital_sourcing_mode must be ROTATION_ALLOWED")
    if hip.on_invalidate_thesis != ON_INVALIDATE_THESIS_BLOCK_AND_ALLOW_REDUCE_LEGS:
        raise ValueError("HIP on_invalidate_thesis must be BLOCK_AND_ALLOW_REDUCE_LEGS")
    if type(hip.leverage_allowed) is not bool or hip.leverage_allowed is not False:
        raise ValueError("HIP leverage_allowed must be False")
    if type(hip.approval_required) is not bool or hip.approval_required is not True:
        raise ValueError("HIP approval_required must be True")
    if hip.profit_realization_mode != PROFIT_REALIZATION_MODE_DEFER:
        raise ValueError("HIP profit_realization_mode must be DEFER")
    nonblank("integrity_seal", hip.integrity_seal)
    verify_hip_integrity(hip)


def validate_capital_snapshot_for_allocation(
    snapshot: ExplicitCapitalSnapshot,
) -> None:
    if type(snapshot) is not ExplicitCapitalSnapshot:
        raise TypeError("capital_snapshot must be ExplicitCapitalSnapshot")
    if snapshot.currency_code != CURRENCY_KRW:
        raise ValueError("CapSnapshot currency must be KRW")
    if snapshot.sizing_authority != SIZING_AUTHORITY_NONE:
        raise ValueError("CapSnapshot sizing_authority must remain NOT_SIZING_AUTHORITY")
    nonblank("orderable_cash_fact_id", snapshot.orderable_cash_fact_id)
    # Broker account valuation fact may exist but must never be used as deployable.
    if snapshot.broker_reported_account_valuation_fact_id == snapshot.orderable_cash_fact_id:
        raise ValueError("account valuation must not alias orderable cash")


def validate_allocation_request(request: CapitalAllocationRequest) -> None:
    if type(request) is not CapitalAllocationRequest:
        raise TypeError("request must be CapitalAllocationRequest")
    nonblank("request_id", request.request_id)
    require_utc("created_at", request.created_at)
    validate_human_investment_policy(request.hip)
    validate_capital_snapshot_for_allocation(request.capital_snapshot)
    validate_resolved_amount(
        request.orderable_cash,
        expected_fact_id=request.capital_snapshot.orderable_cash_fact_id,
    )
    if type(request.position_values) is not tuple:
        raise TypeError("position_values must be tuple")
    subjects = set()
    for view in request.position_values:
        validate_position_view(view)
        if view.portfolio_subject_id in subjects:
            raise ValueError("duplicate position subject")
        subjects.add(view.portfolio_subject_id)
    if type(request.proposed_notionals) is not tuple:
        raise TypeError("proposed_notionals must be tuple")
    leg_ids = set()
    proposal_subjects = set()
    for item in request.proposed_notionals:
        validate_proposed_notional(item)
        if item.allocation_leg_id in leg_ids:
            raise ValueError("duplicate allocation_leg_id")
        if item.portfolio_subject_id in proposal_subjects:
            raise ValueError("duplicate proposed subject")
        leg_ids.add(item.allocation_leg_id)
        proposal_subjects.add(item.portfolio_subject_id)
    for name in ("cio_decisions", "evaluations", "comparisons"):
        if type(getattr(request, name)) is not tuple:
            raise TypeError(f"{name} must be tuple")


def validate_proposal(proposal: CapitalAllocationProposal) -> None:
    if type(proposal) is not CapitalAllocationProposal:
        raise TypeError("proposal must be CapitalAllocationProposal")
    nonblank("proposal_id", proposal.proposal_id)
    nonblank("integrity_seal", proposal.integrity_seal)
    if proposal.executable is not False:
        raise ValueError("proposal must be non-executable")
    if proposal.currency_code != CURRENCY_KRW:
        raise ValueError("proposal currency must be KRW")


def validate_approval(approval: InvestmentHumanApproval) -> None:
    if type(approval) is not InvestmentHumanApproval:
        raise TypeError("approval must be InvestmentHumanApproval")
    nonblank("approval_id", approval.approval_id)
    nonblank("principal", approval.principal)
    require_utc("decided_at", approval.decided_at)
    if approval.decision not in (
        APPROVAL_DECISION_APPROVED,
        APPROVAL_DECISION_REJECTED,
        APPROVAL_DECISION_NEEDS_REVISION,
    ):
        raise ValueError("approval decision invalid")
    nonblank("integrity_seal", approval.integrity_seal)


def validate_artifact(artifact: SealedApprovedAllocationArtifact) -> None:
    if type(artifact) is not SealedApprovedAllocationArtifact:
        raise TypeError("artifact must be SealedApprovedAllocationArtifact")
    nonblank("artifact_id", artifact.artifact_id)
    require_utc("sealed_at", artifact.sealed_at)
    nonblank("integrity_seal", artifact.integrity_seal)
    for leg in artifact.legs:
        if leg.executable is not False:
            raise ValueError("artifact legs must remain non-executable")
