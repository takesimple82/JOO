"""Typed Block E wiring inputs; policy values remain owned by Blocks B/C."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from BrokerExecutionCycle.models import (
    BrokerAcceptanceClassification,
    OrderStatusFact,
    OrderIntent,
    PreTradeFactBundle,
    TradeExecutionAuthorization,
    VerifiedExecutionAccountBinding,
)
from CapitalAllocationCycle.models import (
    HumanInvestmentPolicy,
    InvestmentHumanApproval,
    PositionCapitalView,
    ProposedSubjectNotional,
    SealedApprovedAllocationArtifact,
)
from CommandCenterRuntime.models import ApprovalTransitionFact


@dataclass(frozen=True)
class AllocationComposition:
    request_id: str
    hip: HumanInvestmentPolicy
    position_values: tuple[PositionCapitalView, ...]
    proposed_notionals: tuple[ProposedSubjectNotional, ...]


@dataclass(frozen=True)
class PreTradeComposition:
    intent_id: str
    side: str
    portfolio_subject_id: str
    approved_notional_krw: Decimal
    bundle: PreTradeFactBundle
    freshness_max_age: timedelta


@dataclass(frozen=True)
class BrokerReadRecovery:
    acceptance: BrokerAcceptanceClassification
    status_fact: OrderStatusFact | None
    raw_status_fact_id: str | None
    fact_store: object | None
    cash_corroborated: bool | None
    holdings_corroborated: bool | None


@dataclass(frozen=True)
class ProductionDomainInputs:
    source_fact_store: object | None = None
    operational_cio_kwargs: dict | None = None
    capital_fact_kwargs: dict | None = None
    allocation: AllocationComposition | None = None
    investment_approval: InvestmentHumanApproval | None = None
    approved_artifact: SealedApprovedAllocationArtifact | None = None
    pretrade: PreTradeComposition | None = None
    trade_authorization: TradeExecutionAuthorization | None = None
    account: VerifiedExecutionAccountBinding | None = None
    approval_transitions: tuple[ApprovalTransitionFact, ...] = ()
    broker_recovery: BrokerReadRecovery | None = None


@dataclass(frozen=True)
class ProductionCycleResult:
    command_center: object
    artifact_references: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class MockSubmissionResult:
    attempt: object
    authority: object
    acceptance: object
    recovery: object | None
    fill: object | None
    reconciliation: object
