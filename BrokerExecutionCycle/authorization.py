from __future__ import annotations

from datetime import datetime

from CapitalAllocationCycle.models import (
    InvestmentHumanApproval,
    SealedApprovedAllocationArtifact,
)
from CapitalAllocationCycle.vocabularies import APPROVAL_DECISION_APPROVED

from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.models import (
    MutationAuthorityState,
    OrderIntent,
    TradeExecutionAuthorization,
)
from BrokerExecutionCycle.vocabularies import (
    FAILURE_IHA_INSUFFICIENT,
    FAILURE_PRICE_CHANGED,
    FAILURE_TEA_CONSUMED,
    FAILURE_TEA_REPLAY,
    FAILURE_TEA_SEAL_MISMATCH,
)


def issue_trade_execution_authorization(
    *,
    authorization_id: str,
    order_intent: OrderIntent,
    artifact: SealedApprovedAllocationArtifact,
    approval: InvestmentHumanApproval,
    authorized_at: datetime,
    principal: str,
) -> TradeExecutionAuthorization:
    """C0-D2: separate TEA. IHA alone insufficient. Binds exact OrderIntent seal."""
    if approval.decision != APPROVAL_DECISION_APPROVED:
        raise ValueError(FAILURE_IHA_INSUFFICIENT)
    if order_intent.approval_id != approval.approval_id:
        raise ValueError(FAILURE_IHA_INSUFFICIENT)
    if order_intent.approval_seal != approval.integrity_seal:
        raise ValueError(FAILURE_IHA_INSUFFICIENT)
    if order_intent.allocation_artifact_id != artifact.artifact_id:
        raise ValueError(FAILURE_IHA_INSUFFICIENT)
    if order_intent.allocation_artifact_seal != artifact.integrity_seal:
        raise ValueError(FAILURE_IHA_INSUFFICIENT)
    if type(principal) is not str or principal.strip() == "":
        raise ValueError("TEA principal required")
    payload = {
        "authorization_id": authorization_id,
        "order_intent_id": order_intent.intent_id,
        "order_intent_seal": order_intent.integrity_seal,
        "allocation_artifact_id": artifact.artifact_id,
        "allocation_artifact_seal": artifact.integrity_seal,
        "approval_id": approval.approval_id,
        "approval_seal": approval.integrity_seal,
        "account_binding_id": order_intent.account_binding_id,
        "account_binding_seal": order_intent.account_binding_seal,
        "authorized_at": authorized_at,
        "principal": principal,
        "one_shot": True,
    }
    return TradeExecutionAuthorization(
        authorization_id,
        order_intent.intent_id,
        order_intent.integrity_seal,
        artifact.artifact_id,
        artifact.integrity_seal,
        approval.approval_id,
        approval.integrity_seal,
        order_intent.account_binding_id,
        order_intent.account_binding_seal,
        authorized_at,
        principal,
        True,
        integrity_seal(payload),
    )


def initial_mutation_authority(tea: TradeExecutionAuthorization) -> MutationAuthorityState:
    return MutationAuthorityState(
        tea.authorization_id,
        tea.integrity_seal,
        False,
        None,
        None,
        None,
    )


def assert_tea_binds_intent(
    tea: TradeExecutionAuthorization,
    order_intent: OrderIntent,
) -> None:
    if tea.order_intent_id != order_intent.intent_id:
        raise ValueError(FAILURE_TEA_SEAL_MISMATCH)
    if tea.order_intent_seal != order_intent.integrity_seal:
        raise ValueError(FAILURE_TEA_SEAL_MISMATCH)


def assert_limit_price_unchanged(
    tea: TradeExecutionAuthorization,
    order_intent: OrderIntent,
    current_proposed_limit_price_seal: str,
) -> None:
    """Price change invalidates TEA — caller must re-seal intent + re-issue TEA."""
    del tea  # TEA already bound to intent seal; price drift shows on intent surface.
    if order_intent.proposed_limit_price_seal != current_proposed_limit_price_seal:
        raise ValueError(FAILURE_PRICE_CHANGED)


def consume_one_shot(
    state: MutationAuthorityState,
    *,
    tea: TradeExecutionAuthorization,
    attempt_id: str,
    payload_hash: str,
    consumed_at: datetime,
) -> MutationAuthorityState:
    if state.authorization_id != tea.authorization_id:
        raise ValueError(FAILURE_TEA_SEAL_MISMATCH)
    if state.tea_seal != tea.integrity_seal:
        raise ValueError(FAILURE_TEA_SEAL_MISMATCH)
    if state.consumed:
        raise ValueError(FAILURE_TEA_CONSUMED)
    if tea.one_shot is not True:
        raise ValueError(FAILURE_TEA_REPLAY)
    return MutationAuthorityState(
        tea.authorization_id,
        tea.integrity_seal,
        True,
        attempt_id,
        payload_hash,
        consumed_at,
    )
