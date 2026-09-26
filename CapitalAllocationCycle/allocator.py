from __future__ import annotations

from decimal import Decimal

from ExactDecimalArithmetic.arithmetic import (
    add_exact_decimal,
    subtract_exact_decimal,
)

from CapitalAllocationCycle.constraints import (
    current_market_value,
    derive_action,
    evaluate_funding_constraints,
    evaluate_leg_constraints,
    require_present_orderable_cash,
    subject_postures,
)
from CapitalAllocationCycle.integrity import integrity_seal
from CapitalAllocationCycle.models import (
    AllocationLegProposal,
    CapitalAllocationPlaneResult,
    CapitalAllocationProposal,
    CapitalAllocationRequest,
    CapitalFundingProvenance,
    ConstraintFinding,
)
from CapitalAllocationCycle.validation import validate_allocation_request
from CapitalAllocationCycle.vocabularies import (
    ALLOCATION_ACTION_EXIT,
    ALLOCATION_ACTION_INCREASE,
    ALLOCATION_ACTION_REDUCE,
    CONSTRAINT_FAIL,
)


def _proposal_seal_payload(proposal_fields: dict) -> dict:
    return proposal_fields


def allocate_capital(request: CapitalAllocationRequest) -> CapitalAllocationPlaneResult:
    """Deterministic pure allocator. Fail-closed. Never invents executable orders."""
    validate_allocation_request(request)

    orderable = require_present_orderable_cash(request)
    if type(orderable) is tuple:
        return CapitalAllocationPlaneResult(
            "failure",
            tuple(item.code for item in orderable),
            None,
        )

    reserve = request.hip.explicit_reserve_krw
    if orderable < reserve:
        return CapitalAllocationPlaneResult(
            "failure",
            ("RESERVE_EXCEEDS_ORDERABLE_CASH",),
            None,
        )
    deployable_after_reserve = subtract_exact_decimal(orderable, reserve)

    # First pass: derive actions and reduction proceeds.
    draft_legs: list[AllocationLegProposal] = []
    reduction_by_subject: dict[str, Decimal] = {}
    for item in request.proposed_notionals:
        try:
            current = current_market_value(request, item.portfolio_subject_id)
        except ValueError:
            return CapitalAllocationPlaneResult(
                "failure",
                ("MISSING_POSITION_MARKET_VALUE",),
                None,
            )
        proposed = item.proposed_market_value_krw
        action = derive_action(current, proposed)
        delta = subtract_exact_decimal(proposed, current)
        if action in (ALLOCATION_ACTION_REDUCE, ALLOCATION_ACTION_EXIT):
            proceeds = subtract_exact_decimal(current, proposed)
            reduction_by_subject[item.portfolio_subject_id] = add_exact_decimal(
                reduction_by_subject.get(item.portfolio_subject_id, Decimal("0")),
                proceeds,
            )
        draft_legs.append(
            AllocationLegProposal(
                item.allocation_leg_id,
                item.portfolio_subject_id,
                action,
                current,
                proposed,
                delta,
                item.capital_bucket_id,
                item.risk_budget_id,
                item.rotation_funding_subject_ids,
                Decimal("0"),
                Decimal("0"),
                False,
            )
        )

    # Allocate rotation proceeds without double-count: each subject's proceeds
    # may fund increases at most once in total.
    remaining_proceeds = dict(reduction_by_subject)
    claimed_from: dict[str, Decimal] = {key: Decimal("0") for key in remaining_proceeds}
    funded_legs: list[AllocationLegProposal] = []
    cash_funded_total = Decimal("0")
    rotation_funded_total = Decimal("0")
    double_counted = False

    for leg in draft_legs:
        cash_funding = Decimal("0")
        rotation_funding = Decimal("0")
        if leg.action == ALLOCATION_ACTION_INCREASE:
            need = leg.delta_market_value_krw
            for funder in leg.rotation_funding_subject_ids:
                available = remaining_proceeds.get(funder, Decimal("0"))
                if available <= Decimal("0") or need <= Decimal("0"):
                    continue
                take = available if available <= need else need
                remaining_proceeds[funder] = subtract_exact_decimal(available, take)
                claimed_from[funder] = add_exact_decimal(claimed_from.get(funder, Decimal("0")), take)
                rotation_funding = add_exact_decimal(rotation_funding, take)
                need = subtract_exact_decimal(need, take)
            if need > Decimal("0"):
                cash_funding = need
                cash_funded_total = add_exact_decimal(cash_funded_total, cash_funding)
            if rotation_funding > Decimal("0"):
                rotation_funded_total = add_exact_decimal(rotation_funded_total, rotation_funding)
        funded_legs.append(
            AllocationLegProposal(
                leg.allocation_leg_id,
                leg.portfolio_subject_id,
                leg.action,
                leg.current_market_value_krw,
                leg.proposed_market_value_krw,
                leg.delta_market_value_krw,
                leg.capital_bucket_id,
                leg.risk_budget_id,
                leg.rotation_funding_subject_ids,
                cash_funding,
                rotation_funding,
                False,
            )
        )

    # Detect double-count: claimed cannot exceed original proceeds per subject.
    for subject_id, original in reduction_by_subject.items():
        if claimed_from.get(subject_id, Decimal("0")) > original:
            double_counted = True

    rotation_proceeds_total = Decimal("0")
    for amount in reduction_by_subject.values():
        rotation_proceeds_total = add_exact_decimal(rotation_proceeds_total, amount)

    unused = subtract_exact_decimal(deployable_after_reserve, cash_funded_total)
    if unused < Decimal("0"):
        unused = Decimal("0")

    funding = CapitalFundingProvenance(
        orderable,
        reserve,
        deployable_after_reserve,
        rotation_proceeds_total,
        cash_funded_total,
        rotation_funded_total,
        unused,
    )

    postures = subject_postures(request)
    findings: list[ConstraintFinding] = []
    for leg in funded_legs:
        findings.extend(evaluate_leg_constraints(request, leg, postures))
    findings.extend(
        evaluate_funding_constraints(
            deployable_after_reserve=deployable_after_reserve,
            rotation_proceeds=rotation_proceeds_total,
            cash_funded_increases=cash_funded_total,
            rotation_funded_increases=rotation_funded_total,
            double_counted=double_counted,
        )
    )

    failure_codes = tuple(
        dict.fromkeys(item.code for item in findings if item.status == CONSTRAINT_FAIL)
    )

    proposal_id = f"proposal:{request.request_id}"
    cio_ids = tuple(decision.decision_id for decision in request.cio_decisions)
    comparison_ids = tuple(item.comparison_id for item in request.comparisons)
    seal_payload = {
        "proposal_id": proposal_id,
        "request_id": request.request_id,
        "created_at": request.created_at,
        "hip_policy_id": request.hip.policy_id,
        "hip_version": request.hip.version,
        "hip_integrity_seal": request.hip.integrity_seal,
        "capital_snapshot_id": request.capital_snapshot.capital_snapshot_id,
        "orderable_cash_fact_id": request.capital_snapshot.orderable_cash_fact_id,
        "currency_code": request.hip.currency_code,
        "legs": tuple(
            (
                leg.allocation_leg_id,
                leg.portfolio_subject_id,
                leg.action,
                leg.current_market_value_krw,
                leg.proposed_market_value_krw,
                leg.delta_market_value_krw,
                leg.capital_bucket_id,
                leg.risk_budget_id,
                leg.rotation_funding_subject_ids,
                leg.cash_funding_krw,
                leg.rotation_funding_krw,
                leg.executable,
            )
            for leg in funded_legs
        ),
        "funding": (
            funding.deployable_orderable_cash_krw,
            funding.explicit_reserve_krw,
            funding.deployable_after_reserve_krw,
            funding.rotation_proceeds_krw,
            funding.cash_funded_increases_krw,
            funding.rotation_funded_increases_krw,
            funding.unused_deployable_krw,
        ),
        "constraint_findings": tuple(
            (item.code, item.status, item.allocation_leg_id, item.detail)
            for item in findings
        ),
        "cio_decision_ids": cio_ids,
        "comparison_ids": comparison_ids,
        "universe_id": request.universe.universe_id,
        "executable": False,
    }
    proposal = CapitalAllocationProposal(
        proposal_id,
        request.request_id,
        request.created_at,
        request.hip.policy_id,
        request.hip.version,
        request.hip.integrity_seal,
        request.capital_snapshot.capital_snapshot_id,
        request.capital_snapshot.orderable_cash_fact_id,
        request.hip.currency_code,
        tuple(funded_legs),
        funding,
        tuple(findings),
        cio_ids,
        comparison_ids,
        request.universe.universe_id,
        False,
        integrity_seal(_proposal_seal_payload(seal_payload)),
    )

    if failure_codes:
        return CapitalAllocationPlaneResult("failure", failure_codes, proposal)

    return CapitalAllocationPlaneResult("success", (), proposal)
