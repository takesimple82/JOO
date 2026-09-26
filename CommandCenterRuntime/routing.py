from __future__ import annotations

from CommandCenterRuntime.models import StagePlanEntry, WakeEvent
from CommandCenterRuntime.vocabularies import (
    STAGE_BROKER_STATUS,
    STAGE_CAPITAL_ALLOCATION,
    STAGE_CAPITAL_SNAPSHOT,
    STAGE_CIO,
    STAGE_EXPECTED_VALUE,
    STAGE_FACT_REFRESH,
    STAGE_INVESTMENT_HUMAN_GATE,
    STAGE_PORTFOLIO_SNAPSHOT,
    STAGE_PRETRADE,
    STAGE_RECONCILIATION,
    STAGE_RESEARCH,
    STAGE_SEMANTIC_ADMISSION,
    STAGE_THESIS,
    STAGE_TRADE_HUMAN_GATE,
    WAKE_APPROVAL_TRANSITION,
    WAKE_BROKER_ORDER_OR_FILL,
    WAKE_CAPITAL_ORDERABLE_CASH_CHANGED,
    WAKE_POLICY_SUPERSEDED,
    WAKE_PORTFOLIO_MEMBERSHIP_CHANGED,
    WAKE_PORTFOLIO_QUANTITY_CHANGED,
    WAKE_PROVIDER_FAILURE,
    WAKE_RECONCILIATION_MISMATCH,
    WAKE_RECOVERY_RESUME,
    WAKE_RESEARCH_EVIDENCE_ADMITTED,
    WAKE_SUBMISSION_OUTCOME_UNKNOWN,
    WAKE_THESIS_TRANSITION,
)


def _entries(*pairs: tuple[str, str]) -> tuple[StagePlanEntry, ...]:
    return tuple(StagePlanEntry(stage, True, reason) for stage, reason in pairs)


def route_wake(event: WakeEvent) -> tuple[StagePlanEntry, ...]:
    """Deterministic wake → required stages. No auto research on capital-only."""
    wt = event.wake_type
    if wt in {WAKE_PORTFOLIO_MEMBERSHIP_CHANGED, WAKE_PORTFOLIO_QUANTITY_CHANGED}:
        # Meaningful portfolio change → refresh + CIO path (research through CIO).
        return _entries(
            (STAGE_FACT_REFRESH, "portfolio change requires fact refresh"),
            (STAGE_PORTFOLIO_SNAPSHOT, "membership/qty changed"),
            (STAGE_RESEARCH, "portfolio change may need research"),
            (STAGE_SEMANTIC_ADMISSION, "research predecessor"),
            (STAGE_THESIS, "semantic predecessor"),
            (STAGE_EXPECTED_VALUE, "thesis predecessor"),
            (STAGE_CIO, "meaningful portfolio wake escalates to CIO"),
        )
    if wt == WAKE_CAPITAL_ORDERABLE_CASH_CHANGED:
        # Capital-only: CapitalSnapshot refresh; invalidate stale allocation path
        # attention via allocation gate — NO auto research.
        return _entries(
            (STAGE_FACT_REFRESH, "capital change requires fact refresh"),
            (STAGE_CAPITAL_SNAPSHOT, "orderable cash changed"),
            (STAGE_CAPITAL_ALLOCATION, "invalidate/revise stale allocation if needed"),
            (STAGE_INVESTMENT_HUMAN_GATE, "allocation revision needs Human"),
        )
    if wt == WAKE_RESEARCH_EVIDENCE_ADMITTED:
        return _entries(
            (STAGE_FACT_REFRESH, "new evidence admitted"),
            (STAGE_PORTFOLIO_SNAPSHOT, "research scoped to portfolio"),
            (STAGE_RESEARCH, "new evidence"),
            (STAGE_SEMANTIC_ADMISSION, "research → semantic"),
            (STAGE_THESIS, "semantic → thesis"),
            (STAGE_EXPECTED_VALUE, "thesis → EV"),
            (STAGE_CIO, "EV → CIO"),
        )
    if wt == WAKE_THESIS_TRANSITION:
        return _entries(
            (STAGE_FACT_REFRESH, "thesis transition"),
            (STAGE_THESIS, "thesis transition fact"),
            (STAGE_EXPECTED_VALUE, "recompute EV after thesis"),
            (STAGE_CIO, "CIO after thesis"),
        )
    if wt == WAKE_POLICY_SUPERSEDED:
        return _entries(
            (STAGE_FACT_REFRESH, "policy supersession"),
            (STAGE_CAPITAL_SNAPSHOT, "policy binds capital rules"),
            (STAGE_CAPITAL_ALLOCATION, "invalidate allocation under new policy"),
            (STAGE_INVESTMENT_HUMAN_GATE, "policy conflict / revision"),
        )
    if wt == WAKE_APPROVAL_TRANSITION:
        # Do not auto-approve / create authority — surface attention only via gates.
        return _entries(
            (STAGE_FACT_REFRESH, "approval transition observed"),
            (STAGE_INVESTMENT_HUMAN_GATE, "preserve IHA gate"),
            (STAGE_TRADE_HUMAN_GATE, "preserve TEA gate"),
        )
    if wt in {
        WAKE_BROKER_ORDER_OR_FILL,
        WAKE_SUBMISSION_OUTCOME_UNKNOWN,
        WAKE_RECONCILIATION_MISMATCH,
    }:
        return _entries(
            (STAGE_FACT_REFRESH, "broker event"),
            (STAGE_BROKER_STATUS, "order/fill/unknown status"),
            (STAGE_RECONCILIATION, "reconcile then maybe CIO"),
            (STAGE_PORTFOLIO_SNAPSHOT, "post-recon portfolio refresh"),
            (STAGE_CIO, "recon may escalate to CIO"),
        )
    if wt == WAKE_PROVIDER_FAILURE:
        return _entries(
            (STAGE_FACT_REFRESH, "provider outage recorded as data"),
        )
    if wt == WAKE_RECOVERY_RESUME:
        return _entries(
            (STAGE_FACT_REFRESH, "recovery always refreshes first"),
            (STAGE_BROKER_STATUS, "recovery must not reorder mutation"),
            (STAGE_RECONCILIATION, "preserve UNKNOWN/recon"),
        )
    raise ValueError(f"unroutable wake_type: {wt}")
