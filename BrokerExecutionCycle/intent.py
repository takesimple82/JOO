from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from CapitalAllocationCycle.models import (
    InvestmentHumanApproval,
    SealedApprovedAllocationArtifact,
)

from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.models import (
    OrderIntent,
    PreTradeFactBundle,
    PreTradeValidationResult,
)
from BrokerExecutionCycle.vocabularies import (
    CURRENCY_KRW,
    FAILURE_ACCOUNT_UNVERIFIED,
    FAILURE_IHA_INSUFFICIENT,
    FAILURE_INSTRUMENT_UNPROVEN,
    FAILURE_ORDR_CCD_FORBIDDEN,
    FAILURE_PRETRADE_STALE,
    FORBIDDEN_ORDR_CCD,
    ORDER_INTENT_KIND_LIMIT,
    ORDR_CCD_LIMIT,
)


def seal_limit_order_intent(
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
    """Seal LIMIT OrderIntent. IHA alone is insufficient — needs sealed artifact + fresh pretrade."""
    if approval.approval_id != artifact.approval_id:
        raise ValueError(FAILURE_IHA_INSUFFICIENT)
    if approval.integrity_seal != artifact.approval_integrity_seal:
        raise ValueError(FAILURE_IHA_INSUFFICIENT)
    if artifact.proposal_integrity_seal != approval.proposal_integrity_seal:
        raise ValueError(FAILURE_IHA_INSUFFICIENT)
    if not validation.passed:
        raise ValueError(FAILURE_PRETRADE_STALE)
    if validation.bundle_integrity_seal != bundle.integrity_seal:
        raise ValueError(FAILURE_PRETRADE_STALE)
    if validation.derived_qty is None or validation.derived_notional_krw is None:
        raise ValueError(FAILURE_PRETRADE_STALE)
    if not bundle.instrument.proven:
        raise ValueError(FAILURE_INSTRUMENT_UNPROVEN)
    if bundle.account.mutation_eligible is not True:
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if ORDR_CCD_LIMIT in FORBIDDEN_ORDR_CCD:
        raise ValueError(FAILURE_ORDR_CCD_FORBIDDEN)
    ordr_ccd = ORDR_CCD_LIMIT
    if ordr_ccd in FORBIDDEN_ORDR_CCD or ordr_ccd != ORDR_CCD_LIMIT:
        raise ValueError(FAILURE_ORDR_CCD_FORBIDDEN)

    limit_price = bundle.proposed_limit_price.limit_price
    payload = {
        "intent_id": intent_id,
        "side": side,
        "order_kind": ORDER_INTENT_KIND_LIMIT,
        "ordr_ccd": ordr_ccd,
        "portfolio_subject_id": portfolio_subject_id,
        "ssam_is_cd": bundle.instrument.ssam_is_cd,
        "limit_price": limit_price,
        "quantity": validation.derived_qty,
        "approved_notional_krw": validation.approved_notional_krw,
        "derived_notional_krw": validation.derived_notional_krw,
        "currency_code": CURRENCY_KRW,
        "allocation_artifact_id": artifact.artifact_id,
        "allocation_artifact_seal": artifact.integrity_seal,
        "approval_id": approval.approval_id,
        "approval_seal": approval.integrity_seal,
        "pretrade_validation_id": validation.validation_id,
        "pretrade_validation_seal": validation.integrity_seal,
        "proposed_limit_price_id": bundle.proposed_limit_price.proposal_id,
        "proposed_limit_price_seal": bundle.proposed_limit_price.integrity_seal,
        "account_binding_id": bundle.account.binding_id,
        "account_binding_seal": bundle.account.integrity_seal,
        "instrument_binding_id": bundle.instrument.binding_id,
        "instrument_binding_seal": bundle.instrument.integrity_seal,
        "sealed_at": sealed_at,
        # Explicit absence of broker ids / fills is part of the seal surface.
        "ordr_no": None,
        "fill": None,
    }
    return OrderIntent(
        intent_id,
        side,
        ORDER_INTENT_KIND_LIMIT,
        ordr_ccd,
        portfolio_subject_id,
        bundle.instrument.ssam_is_cd,
        limit_price,
        validation.derived_qty,
        validation.approved_notional_krw,
        validation.derived_notional_krw,
        CURRENCY_KRW,
        artifact.artifact_id,
        artifact.integrity_seal,
        approval.approval_id,
        approval.integrity_seal,
        validation.validation_id,
        validation.integrity_seal,
        bundle.proposed_limit_price.proposal_id,
        bundle.proposed_limit_price.integrity_seal,
        bundle.account.binding_id,
        bundle.account.integrity_seal,
        bundle.instrument.binding_id,
        bundle.instrument.integrity_seal,
        sealed_at,
        integrity_seal(payload),
    )
