"""Authority-preserving domain-to-application projection."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from BrokerExecutionCycle.models import (
    OrderIntent,
    SubmissionRecoveryPlan,
    TradeExecutionAuthorization,
)
from BrokerExecutionCycle.vocabularies import MUTATION_TRANSPORT_LIVE_DISABLED
from CapitalAllocationCycle.hip import (
    HIP_V1_EXPLICIT_RESERVE_KRW,
    HIP_V1_MAX_POSITION_MARKET_VALUE_KRW,
)
from CapitalAllocationCycle.models import (
    CapitalAllocationProposal,
    InvestmentHumanApproval,
)
from CommandCenterRuntime.models import (
    CommandCenterReport,
    HumanAttentionItem,
    OperationalCheckpoint,
)
from InvestmentDecisionVerticalSlice.models import (
    CioDecisionRecord,
    ExactEvRecord,
    OpportunityEvaluation,
)
from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot
from KbCapitalFactAuthority.vocabularies import (
    BROKER_FIELD_ACCOUNT_VALUATION,
    BROKER_FIELD_ORDERABLE_CASH,
    BROKER_FIELD_POSITION_MARKET_VALUE,
    FACT_KIND_BROKER_REPORTED_ACCOUNT_VALUATION,
    FACT_KIND_ORDERABLE_CASH,
    FACT_KIND_POSITION_MARKET_VALUE,
)

from CommandCenterApplication.models import (
    APPLICATION_MODES,
    MODE_FIXTURE,
    AllocationView,
    ApplicationDataset,
    ApprovalView,
    AttentionView,
    CapitalView,
    ChangeView,
    CioView,
    CommandCenterView,
    EvidenceReferenceView,
    ExclusionView,
    ExecutionView,
    ExpectedValueView,
    PositionView,
    SystemHealthView,
)


POSITION_FACT_KIND = "kb_ssqm2952_position"
EXCLUSION_FACT_KINDS = frozenset({
    "kb_ssqm2952_domestic_projection_exclusions",
    "kb_ssqm2952_capital_domestic_projection_exclusions",
})
DEPLOYABLE_POLICY = "ORDERABLE_CASH_FULL"
ACCOUNT_VALUATION_AUTHORITY = "NOT_SIZING_AUTHORITY"
VALUATION_AUTHORITY = "SSQM2952.Record1[].val_amt"
LIVE_BLOCKER_CODE = "AUTHORITY_NOT_CLOSED:gnl_ac_no1"


def _decimal(value, *, field: str) -> Decimal:
    if type(value) is not str:
        raise ValueError(f"{field} missing exact decimal text")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field} invalid exact decimal text") from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f"{field} must be finite and nonnegative")
    return result


def _money(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _active_facts(facts: tuple) -> tuple:
    superseded = {x.superseded_fact_id for x in facts if x.superseded_fact_id is not None}
    return tuple(x for x in facts if x.fact_id not in superseded)


def _evidence(record, authority: str) -> EvidenceReferenceView:
    payload = record.payload
    return EvidenceReferenceView(
        record.fact_id,
        record.provider_id,
        record.source_class,
        record.collected_at.isoformat(),
        authority,
        payload.get("raw_fact_id") if type(payload) is dict else None,
    )


def _artifacts(dataset: ApplicationDataset, cls: type) -> tuple:
    return tuple(item for _row, item in _artifact_rows(dataset, cls))


def _artifact_rows(dataset: ApplicationDataset, cls: type) -> tuple:
    return tuple(
        (row, item)
        for row in dataset.artifacts
        for item in _walk(row.artifact)
        if type(item) is cls
    )


def _walk(value):
    yield value
    if type(value) in (tuple, list):
        for item in value:
            yield from _walk(item)
    elif type(value) is dict:
        for item in value.values():
            yield from _walk(item)
    elif hasattr(value, "__dataclass_fields__"):
        for field in value.__dataclass_fields__:
            yield from _walk(getattr(value, field))


def _latest(values: tuple, timestamp_field: str | None = None):
    if not values:
        return None
    if timestamp_field is None:
        return values[-1]
    return max(values, key=lambda x: getattr(x, timestamp_field))


def _attention_action(category: str) -> str:
    mapping = {
        "SUBMISSION_OUTCOME_UNKNOWN": "Query broker state; do not resubmit.",
        "OPEN_LIMIT_REQUIRES_HUMAN": "Inspect the open LIMIT order and decide manually.",
        "INVESTMENT_APPROVAL_REQUIRED": "Review evidence and approve or reject the allocation.",
        "TRADE_AUTHORIZATION_REQUIRED": "Review the exact OrderIntent before issuing TEA.",
        "PROVIDER_FAILURE": "Restore factual source and refresh before decisions.",
        "DATA_INTEGRITY_FAILURE": "Inspect authoritative evidence and keep execution blocked.",
    }
    return mapping.get(category, "Review the bound evidence and resolve manually.")


def build_command_center_view(dataset: ApplicationDataset) -> CommandCenterView:
    if type(dataset) is not ApplicationDataset:
        raise TypeError("ApplicationDataset required")
    if dataset.mode not in APPLICATION_MODES:
        raise ValueError("unsupported application mode")
    if type(dataset.generated_at) is not datetime or dataset.generated_at.tzinfo is not timezone.utc:
        raise ValueError("generated_at must be UTC")
    for fact in dataset.facts:
        if getattr(fact, "source_class", None) not in {"broker_fact", "market_fact"}:
            raise ValueError("application factual plane rejects non-factual source class")

    active = _active_facts(dataset.facts)
    by_kind: dict[str, list] = {}
    for fact in active:
        payload = fact.payload
        if type(payload) is not dict:
            raise ValueError("fact payload must be dict")
        kind = payload.get("fact_kind")
        if type(kind) is str:
            by_kind.setdefault(kind, []).append(fact)

    quantity_by_symbol = {}
    for fact in by_kind.get(POSITION_FACT_KIND, ()):
        payload = fact.payload
        if payload.get("currency_code") != "KRW":
            raise ValueError("canonical portfolio must be KRW")
        symbol = payload.get("provider_symbol")
        if type(symbol) is not str or symbol.strip() == "":
            raise ValueError("position provider_symbol required")
        quantity_by_symbol[symbol] = fact

    value_by_symbol = {}
    for fact in by_kind.get(FACT_KIND_POSITION_MARKET_VALUE, ()):
        payload = fact.payload
        if payload.get("broker_field") != BROKER_FIELD_POSITION_MARKET_VALUE:
            raise ValueError("position valuation authority mismatch")
        if payload.get("valuation_method") != "broker_val_amt":
            raise ValueError("position valuation must use broker_val_amt")
        symbol = payload.get("provider_symbol")
        if type(symbol) is not str or symbol.strip() == "":
            raise ValueError("valuation provider_symbol required")
        value_by_symbol[symbol] = fact

    active_symbols = []
    for symbol, fact in quantity_by_symbol.items():
        if _decimal(fact.payload.get("quantity"), field="quantity") > 0:
            active_symbols.append(symbol)
    total_value = sum(
        (_decimal(value_by_symbol[s].payload.get("amount"), field="market value")
         for s in active_symbols if s in value_by_symbol),
        Decimal("0"),
    )
    complete_values = all(symbol in value_by_symbol for symbol in active_symbols)
    authoritative_portfolio_total = bool(quantity_by_symbol) and complete_values

    positions = []
    for symbol in sorted(active_symbols):
        quantity_fact = quantity_by_symbol[symbol]
        quantity = _decimal(quantity_fact.payload.get("quantity"), field="quantity")
        valuation_fact = value_by_symbol.get(symbol)
        value = None if valuation_fact is None else _decimal(
            valuation_fact.payload.get("amount"), field="market value"
        )
        weight = None
        if value is not None and complete_values and total_value > 0:
            weight = format(
                (value * Decimal("100") / total_value).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
                "f",
            )
        cap_status = "UNAVAILABLE"
        if value is not None:
            cap_status = "AT_OR_ABOVE_CAP" if value >= HIP_V1_MAX_POSITION_MARKET_VALUE_KRW else "WITHIN_CAP"
        newest = max(
            quantity_fact.collected_at,
            quantity_fact.collected_at if valuation_fact is None else valuation_fact.collected_at,
        )
        positions.append(PositionView(
            symbol,
            format(quantity, "f"),
            _money(value),
            weight,
            cap_status,
            VALUATION_AUTHORITY if valuation_fact is not None else "UNAVAILABLE",
            newest.isoformat(),
            _evidence(quantity_fact, "SSQM2952.Record1[].hld_q"),
            None if valuation_fact is None else _evidence(valuation_fact, VALUATION_AUTHORITY),
        ))

    exclusions_by_identity = {}
    for kind in sorted(EXCLUSION_FACT_KINDS):
        for fact in sorted(
            by_kind.get(kind, ()), key=lambda x: (x.collected_at, x.fact_id)
        ):
            items = fact.payload.get("exclusions")
            if type(items) is not list:
                raise ValueError("exclusion provenance must contain list")
            for item in items:
                if type(item) is not dict:
                    raise ValueError("exclusion item must be dict")
                identity = (
                    str(item.get("provider_symbol", "UNAVAILABLE")),
                    str(item.get("position_class", "UNAVAILABLE")),
                    repr(item.get("raw_currency_code", "")),
                    str(item.get("reason", "UNAVAILABLE")),
                )
                exclusions_by_identity[identity] = ExclusionView(
                    *identity, fact.fact_id,
                )
    exclusions = tuple(
        exclusions_by_identity[key] for key in sorted(exclusions_by_identity)
    )

    cash_fact = _latest(tuple(by_kind.get(FACT_KIND_ORDERABLE_CASH, ())), "collected_at")
    cash = None
    cash_evidence = None
    if cash_fact is not None:
        if cash_fact.payload.get("broker_field") != BROKER_FIELD_ORDERABLE_CASH:
            raise ValueError("orderable cash authority mismatch")
        if cash_fact.payload.get("currency_code") != "KRW":
            raise ValueError("orderable cash must be KRW")
        cash = _decimal(cash_fact.payload.get("amount"), field="orderable cash")
        cash_evidence = _evidence(cash_fact, "SSQM0004.ordr_psbl_csh")

    account_fact = _latest(tuple(by_kind.get(FACT_KIND_BROKER_REPORTED_ACCOUNT_VALUATION, ())), "collected_at")
    account_value = None
    if account_fact is not None:
        if account_fact.payload.get("broker_field") != BROKER_FIELD_ACCOUNT_VALUATION:
            raise ValueError("broker account valuation authority mismatch")
        account_value = _decimal(account_fact.payload.get("amount"), field="account valuation")

    reports = _artifacts(dataset, CommandCenterReport)
    report = _latest(reports, "created_at")
    changes = () if report is None else report.what_changed
    classification = dataset.change_class or ("NO_CHANGE" if report is not None and not changes else "CHANGE_DETECTED" if changes else "UNAVAILABLE")
    if classification not in {"BASELINE_ABSENT", "NO_CHANGE", "CHANGE_DETECTED", "UNAVAILABLE"}:
        raise ValueError("invalid change classification")
    change = ChangeView(classification, tuple(changes), None if report is None else report.created_at.isoformat())

    decision_rows = _artifact_rows(dataset, CioDecisionRecord)
    decision_row = max(decision_rows, key=lambda x: x[0].created_at) if decision_rows else None
    decision = None if decision_row is None else decision_row[1]
    cio_state = "UNAVAILABLE"
    if decision is not None:
        cio_state = "EXECUTABLE" if decision.executable else "NON_EXECUTABLE"
        if decision.unresolved_reasons:
            cio_state = "BLOCKED"
    cio = CioView(
        cio_state,
        None if decision is None else decision.posture.value,
        None if decision is None else decision.what_changed,
        None if decision is None else decision.why_it_matters,
        None if decision is None else decision.superior_opportunity_id,
        () if decision is None else decision.unresolved_reasons,
        () if decision is None else decision.narrative_reference_ids,
        None if decision is None else decision.decision_id,
        None if decision_row is None else decision_row[0].created_at.isoformat(),
    )

    evaluations = _artifacts(dataset, OpportunityEvaluation)
    evs = []
    for evaluation in evaluations:
        record = evaluation.ev_record
        value = None
        status = "UNAVAILABLE"
        record_id = None
        if record is not None:
            status = record.calculation.applicability_status.value
            record_id = record.record_id
            if record.calculation.expected_value is not None:
                value = format(record.calculation.expected_value.value, "f")
        evs.append(ExpectedValueView(
            evaluation.opportunity_id,
            evaluation.portfolio_subject_id,
            status,
            value,
            evaluation.unit_id,
            record_id,
        ))

    proposals = _artifacts(dataset, CapitalAllocationProposal)
    proposal = proposals[-1] if proposals else None
    allocation = AllocationView(
        "UNAVAILABLE" if proposal is None else "PROPOSED",
        None if proposal is None else proposal.proposal_id,
        False if proposal is None else proposal.executable,
        () if proposal is None else tuple(
            x.code for x in proposal.constraint_findings if x.status != "PASS"
        ),
        () if proposal is None else tuple({
            "allocation_leg_id": x.allocation_leg_id,
            "portfolio_subject_id": x.portfolio_subject_id,
            "action": x.action,
            "current_market_value_krw": format(x.current_market_value_krw, "f"),
            "proposed_market_value_krw": format(x.proposed_market_value_krw, "f"),
            "delta_market_value_krw": format(x.delta_market_value_krw, "f"),
            "executable": x.executable,
        } for x in proposal.legs),
    )

    approvals = _artifacts(dataset, InvestmentHumanApproval)
    approval = _latest(approvals, "decided_at")
    approval_view = ApprovalView(
        "NOT_ISSUED" if approval is None else approval.decision,
        None if approval is None else approval.approval_id,
        None if approval is None else approval.proposal_id,
        None if approval is None else approval.decision,
        None if approval is None else approval.principal,
        None if approval is None else approval.decided_at.isoformat(),
    )

    intents = _artifacts(dataset, OrderIntent)
    intent = _latest(intents, "sealed_at")
    teas = _artifacts(dataset, TradeExecutionAuthorization)
    tea = _latest(teas, "authorized_at")
    recoveries = _artifacts(dataset, SubmissionRecoveryPlan)
    attention_items = _artifacts(dataset, HumanAttentionItem)
    unresolved_attention = tuple(x for x in attention_items if x.unresolved)
    open_limit = any("OPEN_LIMIT" in x.category for x in unresolved_attention)
    execution = ExecutionView(
        "LIVE_BLOCKED",
        MUTATION_TRANSPORT_LIVE_DISABLED,
        False,
        LIVE_BLOCKER_CODE,
        "KB authority for gnl_ac_no1 is not closed; real broker mutation is forbidden.",
        None if intent is None else intent.intent_id,
        "NOT_ISSUED" if tea is None else "ISSUED_ONE_SHOT",
        None if tea is None else tea.authorization_id,
        "LIMIT_ONLY",
        "NONE" if not recoveries else recoveries[-1].recovery_mode,
        open_limit,
    )

    attention_views = tuple(AttentionView(
        item.attention_id,
        item.category,
        item.priority,
        "UNRESOLVED" if item.unresolved else "RESOLVED",
        item.detail,
        "Safety or decision state requires human review.",
        item.bound_record_ids,
        _attention_action(item.category),
        item.created_at.isoformat(),
    ) for item in sorted(attention_items, key=lambda x: (x.priority, x.created_at, x.attention_id)))

    evidence = []
    for fact in active:
        kind = fact.payload.get("fact_kind")
        authority = str(fact.payload.get("authority", kind or "RAW_FACTUAL_EVIDENCE"))
        if kind == FACT_KIND_POSITION_MARKET_VALUE:
            authority = VALUATION_AUTHORITY
        elif kind == FACT_KIND_ORDERABLE_CASH:
            authority = "SSQM0004.ordr_psbl_csh"
        evidence.append(_evidence(fact, authority))

    factual_times = tuple(x.collected_at for x in active)
    last_refresh = max(factual_times) if factual_times else None
    snapshots = _artifacts(dataset, ExplicitCapitalSnapshot)
    snapshot = _latest(snapshots, "collected_at")
    freshness = "UNAVAILABLE"
    if snapshot is not None:
        age = dataset.generated_at - snapshot.collected_at
        freshness = "FRESH" if age.total_seconds() >= 0 and age <= snapshot.freshness_max_age else "STALE"
    checkpoints = _artifacts(dataset, OperationalCheckpoint)
    checkpoint = _latest(checkpoints, "created_at")
    health_state = "ATTENTION" if unresolved_attention else "NORMAL"
    if freshness in {"STALE", "UNAVAILABLE"}:
        health_state = "ATTENTION"
    health = SystemHealthView(
        health_state,
        freshness,
        None if last_refresh is None else last_refresh.isoformat(),
        "VERIFIED" if dataset.facts else "EMPTY",
        "VERIFIED" if dataset.journal_record_count else "VERIFIED_EMPTY",
        "UNAVAILABLE" if checkpoint is None else checkpoint.status,
        None if checkpoint is None else checkpoint.created_at.isoformat(),
        "ATTENTION_REQUIRED" if unresolved_attention else "CLEAR",
        MUTATION_TRANSPORT_LIVE_DISABLED,
        LIVE_BLOCKER_CODE,
        "OBSERVE_ONLY_NOT_USED_BY_APPLICATION",
    )

    return CommandCenterView(
        1,
        dataset.mode,
        "FIXTURE / DEMO — NOT REAL DATA" if dataset.mode == MODE_FIXTURE else "REAL KB READ-ONLY",
        dataset.source_label,
        dataset.generated_at.isoformat(),
        _money(total_value) if authoritative_portfolio_total else None,
        len(positions),
        tuple(positions),
        exclusions,
        CapitalView(
            _money(cash),
            _money(total_value) if authoritative_portfolio_total else None,
            _money(cash),
            format(HIP_V1_EXPLICIT_RESERVE_KRW, "f"),
            format(HIP_V1_MAX_POSITION_MARKET_VALUE_KRW, "f"),
            DEPLOYABLE_POLICY,
            _money(account_value),
            ACCOUNT_VALUATION_AUTHORITY,
            cash_evidence,
        ),
        change,
        cio,
        tuple(evs),
        allocation,
        approval_view,
        execution,
        attention_views,
        tuple(evidence),
        health,
    )
