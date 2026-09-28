from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from CapitalAllocationCycle.models import (
    InvestmentHumanApproval,
    SealedApprovedAllocationArtifact,
)

from BrokerExecutionCycle.acceptance import classify_submission_outcome
from BrokerExecutionCycle.authorization import (
    initial_mutation_authority,
    issue_trade_execution_authorization,
)
from BrokerExecutionCycle.intent import seal_limit_order_intent
from BrokerExecutionCycle.models import (
    BrokerExecutionCycleResult,
    MutationAuthorityState,
    OrderIntent,
    PreTradeFactBundle,
    PreTradeValidationResult,
    TradeExecutionAuthorization,
    VerifiedExecutionAccountBinding,
)
from BrokerExecutionCycle.mutation_gate import execute_mutation_attempt
from BrokerExecutionCycle.mutation_transport import MutationTransport
from BrokerExecutionCycle.pretrade import validate_pretrade
from BrokerExecutionCycle.reconciliation import (
    fill_fact_from_status,
    reconcile_acceptance_and_fill,
)
from BrokerExecutionCycle.recovery import plan_submission_unknown_recovery
from BrokerExecutionCycle.translation import translate_order_intent_to_ssam
from BrokerExecutionCycle.vocabularies import (
    ACCEPTANCE_UNKNOWN,
    FAILURE_IHA_INSUFFICIENT,
)


def run_pretrade_validation(
    *,
    validation_id: str,
    bundle: PreTradeFactBundle,
    side: str,
    approved_notional_krw: Decimal,
    validated_at: datetime,
) -> PreTradeValidationResult:
    return validate_pretrade(
        validation_id=validation_id,
        bundle=bundle,
        side=side,
        approved_notional_krw=approved_notional_krw,
        validated_at=validated_at,
    )


def seal_order_intent_from_approval_chain(
    *,
    intent_id: str,
    side: str,
    portfolio_subject_id: str,
    bundle: PreTradeFactBundle,
    validation: PreTradeValidationResult,
    artifact: SealedApprovedAllocationArtifact,
    approval: InvestmentHumanApproval,
    sealed_at: datetime,
) -> OrderIntent:
    return seal_limit_order_intent(
        intent_id=intent_id,
        side=side,
        portfolio_subject_id=portfolio_subject_id,
        bundle=bundle,
        validation=validation,
        artifact=artifact,
        approval=approval,
        sealed_at=sealed_at,
    )


def authorize_trade_execution(
    *,
    authorization_id: str,
    order_intent: OrderIntent,
    artifact: SealedApprovedAllocationArtifact,
    approval: InvestmentHumanApproval,
    authorized_at: datetime,
    principal: str,
) -> tuple[TradeExecutionAuthorization, MutationAuthorityState]:
    tea = issue_trade_execution_authorization(
        authorization_id=authorization_id,
        order_intent=order_intent,
        artifact=artifact,
        approval=approval,
        authorized_at=authorized_at,
        principal=principal,
    )
    return tea, initial_mutation_authority(tea)


def run_broker_execution_cycle(
    *,
    intent_id: str,
    authorization_id: str,
    attempt_id: str,
    classification_id: str,
    side: str,
    portfolio_subject_id: str,
    approved_notional_krw: Decimal,
    bundle: PreTradeFactBundle,
    artifact: SealedApprovedAllocationArtifact,
    approval: InvestmentHumanApproval,
    account: VerifiedExecutionAccountBinding,
    now: datetime,
    principal: str,
    transport: MutationTransport,
    status_payload: dict | None = None,
    cash_corroborated: bool | None = None,
    holdings_corroborated: bool | None = None,
    durable_pre_send_appender=None,
) -> BrokerExecutionCycleResult:
    """Full product path with mock transport only.

    Chain: fresh pretrade → OrderIntent → TEA → mutation → accept/reject/unknown
    → optional status/fill → reconciliation.
    """
    if artifact.approval_id != approval.approval_id:
        return BrokerExecutionCycleResult(
            "failure",
            (FAILURE_IHA_INSUFFICIENT,),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    validation = validate_pretrade(
        validation_id=f"pretrade-{intent_id}",
        bundle=bundle,
        side=side,
        approved_notional_krw=approved_notional_krw,
        validated_at=now,
    )
    if not validation.passed:
        codes = tuple(f.code for f in validation.findings if f.status == "FAIL")
        return BrokerExecutionCycleResult(
            "failure",
            codes,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    intent = seal_limit_order_intent(
        intent_id=intent_id,
        side=side,
        portfolio_subject_id=portfolio_subject_id,
        bundle=bundle,
        validation=validation,
        artifact=artifact,
        approval=approval,
        sealed_at=now,
    )
    tea, authority = authorize_trade_execution(
        authorization_id=authorization_id,
        order_intent=intent,
        artifact=artifact,
        approval=approval,
        authorized_at=now,
        principal=principal,
    )
    translation = translate_order_intent_to_ssam(
        translation_id=f"tr-{intent_id}",
        order_intent=intent,
        account=account,
    )
    if not translation.ready:
        return BrokerExecutionCycleResult(
            "failure",
            tuple(translation.unresolved_fields) or ("UNRESOLVED_SSAM_FIELD",),
            intent,
            tea,
            None,
            None,
            None,
            None,
            None,
        )

    attempt, _authority, response = execute_mutation_attempt(
        attempt_id=attempt_id,
        tea=tea,
        order_intent=intent,
        translation=translation,
        account=account,
        authority=authority,
        attempted_at=now,
        transport=transport,
        durable_pre_send_appender=durable_pre_send_appender,
    )
    acceptance = classify_submission_outcome(
        classification_id=classification_id,
        attempt_id=attempt_id,
        response=response,
        classified_at=now,
    )

    recovery = None
    fill = None
    if acceptance.outcome == ACCEPTANCE_UNKNOWN:
        status_fact = None
        if status_payload is not None:
            from BrokerExecutionCycle.provider_read import normalize_ssqm2341_status

            status_fact = normalize_ssqm2341_status(
                fact_id=f"status-{attempt_id}",
                payload=status_payload,
                query_order_no=None,
                query_order_date=None,
                collected_at=now,
                raw_envelope_id=f"env-status-{attempt_id}",
            )
            fill = fill_fact_from_status(
                fact_id=f"fill-{attempt_id}",
                status=status_fact,
                observed_at=now,
            )
        recovery = plan_submission_unknown_recovery(
            plan_id=f"recovery-{attempt_id}",
            acceptance=acceptance,
            status_fact=status_fact,
        )

    recon = reconcile_acceptance_and_fill(
        result_id=f"recon-{attempt_id}",
        attempt_id=attempt_id,
        acceptance=acceptance,
        fill=fill,
        cash_corroborated=cash_corroborated,
        holdings_corroborated=holdings_corroborated,
        reconciled_at=now,
    )
    return BrokerExecutionCycleResult(
        "success",
        (),
        intent,
        tea,
        attempt,
        acceptance,
        recovery,
        fill,
        recon,
    )


__all__ = [
    "authorize_trade_execution",
    "run_broker_execution_cycle",
    "run_pretrade_validation",
    "seal_order_intent_from_approval_chain",
]
