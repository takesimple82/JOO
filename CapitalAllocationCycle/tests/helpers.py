from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from InvestmentDecisionVerticalSlice.models import (
    CioActionPosture,
    CioDecisionRecord,
    ComparisonStatus,
    OpportunityEvaluation,
    OpportunityRole,
    OpportunityComparison,
)
from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot
from OperationalCioCycle.models import OpportunityUniverse, UniverseMember
from PortfolioDomain.models import PortfolioSubject

from CapitalAllocationCycle.hip import build_frozen_hip_v1
from CapitalAllocationCycle.models import (
    CapitalAllocationRequest,
    PositionCapitalView,
    ProposedSubjectNotional,
    ResolvedExactAmount,
)
from CapitalAllocationCycle.vocabularies import (
    AMOUNT_PRESENCE_MISSING,
    AMOUNT_PRESENCE_PRESENT,
    CURRENCY_KRW,
)

UTC = timezone.utc
NOW = datetime(2026, 9, 26, 9, 0, tzinfo=UTC)


def subject(sid, name=None):
    return PortfolioSubject(sid, name or sid)


def capital_snapshot(
    *,
    snapshot_id="capital-snapshot-001",
    orderable_fact="orderable-cash-fact-001",
    valuation_fact="account-valuation-fact-001",
):
    return ExplicitCapitalSnapshot(
        snapshot_id,
        "account-primary",
        "kb_open_api",
        CURRENCY_KRW,
        NOW,
        timedelta(seconds=3600),
        "portfolio-snapshot-001",
        "portfolio-001",
        "observation-001",
        "balances-raw-001",
        "holdings-raw-001",
        orderable_fact,
        "deposit-today-fact-001",
        "deposit-d1-fact-001",
        "deposit-d2-fact-001",
        "withdrawable-fact-001",
        "orderable-total-fact-001",
        valuation_fact,
        ("position-mv-fact-a", "position-mv-fact-b"),
        "NOT_SIZING_AUTHORITY",
    )


def resolved_cash(amount="50000000", *, fact_id="orderable-cash-fact-001", presence=AMOUNT_PRESENCE_PRESENT):
    return ResolvedExactAmount(
        fact_id,
        presence,
        Decimal(amount) if presence == AMOUNT_PRESENCE_PRESENT else None,
        CURRENCY_KRW,
    )


def position(subject_id, amount, *, fact_id=None, presence=AMOUNT_PRESENCE_PRESENT):
    return PositionCapitalView(
        subject_id,
        fact_id or f"mv-{subject_id}",
        presence,
        Decimal(amount) if presence == AMOUNT_PRESENCE_PRESENT else None,
        CURRENCY_KRW,
    )


def universe(members):
    return OpportunityUniverse(
        "universe-001",
        "cycle-001",
        "portfolio-snapshot-001",
        tuple(members),
        "universe-policy-v1",
        NOW,
    )


def member(sid, sources, eligible):
    return UniverseMember(subject(sid), sources, ("prov",), eligible)


def evaluation(oid, sid, role):
    return OpportunityEvaluation(
        oid,
        sid,
        role,
        "cmp-policy",
        "prob-v1",
        "horizon-1",
        "KRW",
        None,
    )


def comparison(cid, left, right, status):
    return OpportunityComparison(cid, left, right, status)


def cio_decision(
    *,
    decision_id="cio-001",
    posture=CioActionPosture.MAINTAIN,
    comparison_ids=(),
    superior=None,
    unresolved=(),
):
    return CioDecisionRecord(
        decision_id,
        "portfolio-snapshot-001",
        "bundle-001",
        "semantic-001",
        (),
        (),
        (),
        comparison_ids,
        ("horizon-1",),
        posture,
        "what",
        "why",
        superior,
        unresolved,
        ("semantic-001",),
        False,
    )


def proposed(leg, sid, amount, *, bucket=None, risk=None, funding=()):
    return ProposedSubjectNotional(
        leg,
        sid,
        Decimal(amount),
        bucket,
        risk,
        funding,
    )


def base_request(
    *,
    hip=None,
    cash=None,
    positions=None,
    members=None,
    decisions=None,
    evaluations=None,
    comparisons=None,
    proposed_notionals=None,
):
    hold = member("HOLD-A", ("holding",), True)
    cand = member("CAND-B", ("explicit_candidate",), True)
    watch = member("WATCH-C", ("watchlist",), False)
    default_members = (hold, cand, watch)
    left = evaluation("opp-hold", "HOLD-A", OpportunityRole.CURRENT_HOLDING)
    right = evaluation("opp-cand", "CAND-B", OpportunityRole.CANDIDATE)
    default_evals = (left, right)
    default_cmp = (
        comparison(
            "cmp-001",
            left,
            right,
            ComparisonStatus.RIGHT_SUPERIOR,
        ),
    )
    default_decisions = (
        cio_decision(
            posture=CioActionPosture.CONSIDER_ROTATION,
            comparison_ids=("cmp-001",),
            superior="opp-cand",
        ),
    )
    default_positions = (
        position("HOLD-A", "20000000"),
        position("CAND-B", "0"),
    )
    default_proposed = (
        proposed("leg-hold", "HOLD-A", "10000000"),
        proposed(
            "leg-cand",
            "CAND-B",
            "10000000",
            funding=("HOLD-A",),
        ),
    )
    return CapitalAllocationRequest(
        "req-001",
        NOW,
        hip if hip is not None else build_frozen_hip_v1(effective_at=NOW),
        capital_snapshot(),
        cash if cash is not None else resolved_cash("50000000"),
        positions if positions is not None else default_positions,
        universe(members if members is not None else default_members),
        decisions if decisions is not None else default_decisions,
        evaluations if evaluations is not None else default_evals,
        comparisons if comparisons is not None else default_cmp,
        proposed_notionals if proposed_notionals is not None else default_proposed,
    )
