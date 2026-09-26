from __future__ import annotations

from decimal import Decimal

from ExactDecimalArithmetic.arithmetic import (
    add_exact_decimal,
    subtract_exact_decimal,
)
from InvestmentDecisionVerticalSlice.models import (
    CioActionPosture,
    ComparisonStatus,
    OpportunityRole,
)

from CapitalAllocationCycle.models import (
    AllocationLegProposal,
    CapitalAllocationRequest,
    ConstraintFinding,
)
from CapitalAllocationCycle.vocabularies import (
    ALLOCATION_ACTION_EXIT,
    ALLOCATION_ACTION_INCREASE,
    ALLOCATION_ACTION_MAINTAIN,
    ALLOCATION_ACTION_REDUCE,
    AMOUNT_PRESENCE_PRESENT,
    CONSTRAINT_FAIL,
    CONSTRAINT_PASS,
    FAILURE_CASH_CONSERVATION_VIOLATION,
    FAILURE_DOUBLE_COUNT_ROTATION_PROCEEDS,
    FAILURE_INCREASE_CAPACITY_ZERO,
    FAILURE_MAX_POSITION_EXCEEDED,
    FAILURE_MISSING_CIO_POSTURE,
    FAILURE_MISSING_ORDERABLE_CASH,
    FAILURE_POSTURE_BLOCKS_INCREASE,
    FAILURE_ROTATION_PROCEEDS_INSUFFICIENT,
    FAILURE_ROTATION_REQUIRES_EV_SUPERIORITY,
    FAILURE_SUBJECT_NOT_IN_UNIVERSE,
    FAILURE_WATCHLIST_ONLY_INELIGIBLE,
)


def _finding(code: str, status: str, leg_id: str | None, detail: str) -> ConstraintFinding:
    return ConstraintFinding(code, status, leg_id, detail)


def derive_action(current: Decimal, proposed: Decimal) -> str:
    if proposed == current:
        return ALLOCATION_ACTION_MAINTAIN
    if proposed > current:
        return ALLOCATION_ACTION_INCREASE
    if proposed == Decimal("0") and current > Decimal("0"):
        return ALLOCATION_ACTION_EXIT
    return ALLOCATION_ACTION_REDUCE


def current_market_value(
    request: CapitalAllocationRequest,
    subject_id: str,
) -> Decimal:
    for view in request.position_values:
        if view.portfolio_subject_id == subject_id:
            if view.presence != AMOUNT_PRESENCE_PRESENT or view.market_value_krw is None:
                # Missing position MV is not treated as zero holdings authority.
                raise ValueError("position market value missing for subject")
            return view.market_value_krw
    return Decimal("0")


def universe_member(request: CapitalAllocationRequest, subject_id: str):
    for member in request.universe.members:
        if member.subject.subject_id == subject_id:
            return member
    return None


def subject_postures(request: CapitalAllocationRequest) -> dict[str, CioActionPosture]:
    """Map portfolio_subject_id -> governing CIO posture (fail-closed if absent)."""
    opportunity_to_subject = {
        evaluation.opportunity_id: evaluation.portfolio_subject_id
        for evaluation in request.evaluations
    }
    postures: dict[str, CioActionPosture] = {}
    for decision in request.cio_decisions:
        # Bind posture to all subjects referenced by the decision's comparisons.
        related = set()
        for comparison in request.comparisons:
            if comparison.comparison_id in decision.comparison_ids:
                related.add(comparison.left.portfolio_subject_id)
                related.add(comparison.right.portfolio_subject_id)
        if decision.superior_opportunity_id is not None:
            subject = opportunity_to_subject.get(decision.superior_opportunity_id)
            if subject is not None:
                related.add(subject)
        for subject_id in related:
            # INVALIDATE / unresolved dominate over maintain/rotation when multiple.
            prior = postures.get(subject_id)
            if prior is None:
                postures[subject_id] = decision.posture
            elif decision.posture is CioActionPosture.INVALIDATE_THESIS:
                postures[subject_id] = decision.posture
            elif decision.posture is CioActionPosture.NO_ACTION_UNRESOLVED and prior is not CioActionPosture.INVALIDATE_THESIS:
                postures[subject_id] = decision.posture
            elif decision.posture is CioActionPosture.RESEARCH_MORE and prior in (
                CioActionPosture.MAINTAIN,
                CioActionPosture.CONSIDER_ROTATION,
            ):
                postures[subject_id] = decision.posture
    return postures


def ev_superiority_supports_rotation(
    request: CapitalAllocationRequest,
    target_subject_id: str,
    funding_subject_ids: tuple[str, ...],
) -> bool:
    """CONSIDER_ROTATION may rotate only under EV superiority + policy."""
    for comparison in request.comparisons:
        left_subject = comparison.left.portfolio_subject_id
        right_subject = comparison.right.portfolio_subject_id
        if comparison.status is ComparisonStatus.RIGHT_SUPERIOR:
            if (
                right_subject == target_subject_id
                and left_subject in funding_subject_ids
                and comparison.right.role is OpportunityRole.CANDIDATE
            ):
                return True
        if comparison.status is ComparisonStatus.LEFT_SUPERIOR:
            if (
                left_subject == target_subject_id
                and right_subject in funding_subject_ids
                and comparison.left.role is OpportunityRole.CANDIDATE
            ):
                return True
    for decision in request.cio_decisions:
        if decision.posture is not CioActionPosture.CONSIDER_ROTATION:
            continue
        if decision.superior_opportunity_id is None:
            continue
        for evaluation in request.evaluations:
            if (
                evaluation.opportunity_id == decision.superior_opportunity_id
                and evaluation.portfolio_subject_id == target_subject_id
            ):
                return True
    return False


def increase_blocked_by_posture(posture: CioActionPosture | None) -> bool:
    if posture is None:
        return True
    return posture in (
        CioActionPosture.MAINTAIN,
        CioActionPosture.INVALIDATE_THESIS,
        CioActionPosture.NO_ACTION_UNRESOLVED,
        CioActionPosture.RESEARCH_MORE,
    )


def evaluate_leg_constraints(
    request: CapitalAllocationRequest,
    leg: AllocationLegProposal,
    postures: dict[str, CioActionPosture],
) -> tuple[ConstraintFinding, ...]:
    findings: list[ConstraintFinding] = []
    member = universe_member(request, leg.portfolio_subject_id)
    if member is None:
        findings.append(
            _finding(
                FAILURE_SUBJECT_NOT_IN_UNIVERSE,
                CONSTRAINT_FAIL,
                leg.allocation_leg_id,
                "subject absent from OpportunityUniverse",
            )
        )
        return tuple(findings)
    if not member.eligible:
        # Watchlist-only members are not allocation-eligible.
        findings.append(
            _finding(
                FAILURE_WATCHLIST_ONLY_INELIGIBLE,
                CONSTRAINT_FAIL,
                leg.allocation_leg_id,
                "watchlist-only subject rejected",
            )
        )
    posture = postures.get(leg.portfolio_subject_id)
    if leg.action == ALLOCATION_ACTION_INCREASE:
        if posture is None:
            findings.append(
                _finding(
                    FAILURE_MISSING_CIO_POSTURE,
                    CONSTRAINT_FAIL,
                    leg.allocation_leg_id,
                    "increase requires governing CIO posture",
                )
            )
        elif increase_blocked_by_posture(posture):
            findings.append(
                _finding(
                    FAILURE_POSTURE_BLOCKS_INCREASE,
                    CONSTRAINT_FAIL,
                    leg.allocation_leg_id,
                    f"posture {posture.value} blocks capital increase",
                )
            )
        elif posture is CioActionPosture.CONSIDER_ROTATION:
            if not ev_superiority_supports_rotation(
                request,
                leg.portfolio_subject_id,
                leg.rotation_funding_subject_ids,
            ):
                findings.append(
                    _finding(
                        FAILURE_ROTATION_REQUIRES_EV_SUPERIORITY,
                        CONSTRAINT_FAIL,
                        leg.allocation_leg_id,
                        "CONSIDER_ROTATION requires EV superiority",
                    )
                )
        # INVALIDATE: no buy/increase (already covered). REDUCE/EXIT allowed elsewhere.
    if leg.action == ALLOCATION_ACTION_INCREASE:
        cap = request.hip.max_position_market_value_krw
        if leg.current_market_value_krw >= cap:
            findings.append(
                _finding(
                    FAILURE_INCREASE_CAPACITY_ZERO,
                    CONSTRAINT_FAIL,
                    leg.allocation_leg_id,
                    "current MV already at/above hard cap; increase capacity=0",
                )
            )
        elif leg.proposed_market_value_krw > cap:
            findings.append(
                _finding(
                    FAILURE_MAX_POSITION_EXCEEDED,
                    CONSTRAINT_FAIL,
                    leg.allocation_leg_id,
                    "proposed MV exceeds max_position_market_value",
                )
            )
    if not findings:
        findings.append(
            _finding(CONSTRAINT_PASS, CONSTRAINT_PASS, leg.allocation_leg_id, "leg admitted")
        )
    return tuple(findings)


def evaluate_funding_constraints(
    *,
    deployable_after_reserve: Decimal,
    rotation_proceeds: Decimal,
    cash_funded_increases: Decimal,
    rotation_funded_increases: Decimal,
    double_counted: bool,
) -> tuple[ConstraintFinding, ...]:
    findings: list[ConstraintFinding] = []
    if double_counted:
        findings.append(
            _finding(
                FAILURE_DOUBLE_COUNT_ROTATION_PROCEEDS,
                CONSTRAINT_FAIL,
                None,
                "rotation proceeds double-counted across legs",
            )
        )
    if cash_funded_increases > deployable_after_reserve:
        findings.append(
            _finding(
                FAILURE_CASH_CONSERVATION_VIOLATION,
                CONSTRAINT_FAIL,
                None,
                "cash-funded increases exceed deployable after reserve",
            )
        )
    if rotation_funded_increases > rotation_proceeds:
        findings.append(
            _finding(
                FAILURE_ROTATION_PROCEEDS_INSUFFICIENT,
                CONSTRAINT_FAIL,
                None,
                "rotation-funded increases exceed eligible rotation proceeds",
            )
        )
    total_increases = add_exact_decimal(cash_funded_increases, rotation_funded_increases)
    total_sources = add_exact_decimal(deployable_after_reserve, rotation_proceeds)
    if total_increases > total_sources:
        findings.append(
            _finding(
                FAILURE_CASH_CONSERVATION_VIOLATION,
                CONSTRAINT_FAIL,
                None,
                "total increases exceed deployable + rotation proceeds",
            )
        )
    if not findings:
        findings.append(
            _finding(CONSTRAINT_PASS, CONSTRAINT_PASS, None, "funding conservation holds")
        )
    return tuple(findings)


def require_present_orderable_cash(request: CapitalAllocationRequest) -> tuple[ConstraintFinding, ...] | Decimal:
    if request.orderable_cash.presence != AMOUNT_PRESENCE_PRESENT:
        return (
            _finding(
                FAILURE_MISSING_ORDERABLE_CASH,
                CONSTRAINT_FAIL,
                None,
                "missing orderable cash is not deployable zero",
            ),
        )
    assert request.orderable_cash.amount_krw is not None
    return request.orderable_cash.amount_krw
