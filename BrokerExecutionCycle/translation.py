from __future__ import annotations

from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.models import (
    OrderIntent,
    SsamRequestTranslation,
    VerifiedExecutionAccountBinding,
)
from BrokerExecutionCycle.account_binding import require_mutation_eligible_account
from BrokerExecutionCycle.authority_evidence import (
    SSAM_ACCOUNT_BINDING_FIELD,
    SSAM_EXCEL_REQUIRED_INPUT_FIELDS,
)
from BrokerExecutionCycle.vocabularies import (
    API_PATH_SSAM1801,
    API_PATH_SSAM1802,
    CRDT_TYP_CD_CASH,
    FAILURE_ACCOUNT_UNVERIFIED,
    FAILURE_ORDR_CCD_FORBIDDEN,
    FAILURE_SIDE_INVALID,
    FAILURE_UNRESOLVED_SSAM_FIELD,
    MKT_TM_CLSF_REGULAR,
    ORDR_CCD_LIMIT,
    ORDR_JB_CLSF_BUY,
    ORDR_JB_CLSF_SELL,
    SIDE_BUY,
    SIDE_SELL,
    SSAM_FIELD_CRDT_TYP_CD,
    SSAM_FIELD_GDS_NO1,
    SSAM_FIELD_GNL_AC_NO1,
    SSAM_FIELD_IS_CD,
    SSAM_FIELD_MKT_TM_CLSF,
    SSAM_FIELD_ORDR_CCD,
    SSAM_FIELD_ORDR_JB_CLSF,
    SSAM_FIELD_ORDR_Q,
    SSAM_FIELD_ORDR_UPRC,
    SSAM_FIELD_SOR_ORDR_CCD,
)


def _price_text(price) -> str:
    # Documented sample uses unpadded integer text for input ordr_uprc.
    if price != price.to_integral_value():
        raise ValueError(FAILURE_UNRESOLVED_SSAM_FIELD)
    return format(price, "f")


def _qty_text(qty) -> str:
    if qty != qty.to_integral_value():
        raise ValueError(FAILURE_UNRESOLVED_SSAM_FIELD)
    return format(qty, "f")


def translate_order_intent_to_ssam(
    *,
    translation_id: str,
    order_intent: OrderIntent,
    account: VerifiedExecutionAccountBinding,
) -> SsamRequestTranslation:
    """SSAM translation: Excel required INPUT + sample-observed account field.

    Account binding field is gnl_ac_no1 (SAMPLE_OBSERVED; Excel INPUT omits it).
    OrderIntent/TEA must map the verified binding exactly — no heuristic.
    """
    unresolved: list[str] = []
    if order_intent.ordr_ccd != ORDR_CCD_LIMIT:
        raise ValueError(FAILURE_ORDR_CCD_FORBIDDEN)
    if SSAM_ACCOUNT_BINDING_FIELD != SSAM_FIELD_GNL_AC_NO1:
        raise RuntimeError(FAILURE_UNRESOLVED_SSAM_FIELD)
    try:
        require_mutation_eligible_account(account)
    except (TypeError, ValueError):
        unresolved.append(SSAM_FIELD_GNL_AC_NO1)
    if order_intent.side == SIDE_BUY:
        api_path = API_PATH_SSAM1802
        jb = ORDR_JB_CLSF_BUY
        gds_no1 = "01"
        sor = "N"
    elif order_intent.side == SIDE_SELL:
        api_path = API_PATH_SSAM1801
        jb = ORDR_JB_CLSF_SELL
        gds_no1 = ""
        sor = ""
    else:
        raise ValueError(FAILURE_SIDE_INVALID)

    if order_intent.account_binding_id != account.binding_id:
        unresolved.append("account_binding_id")
    if order_intent.account_binding_seal != account.integrity_seal:
        unresolved.append("account_binding_seal")

    data_body = {
        SSAM_FIELD_GDS_NO1: gds_no1,
        SSAM_FIELD_ORDR_UPRC: _price_text(order_intent.limit_price),
        SSAM_FIELD_GNL_AC_NO1: account.gnl_ac_no1 if not unresolved else "",
        SSAM_FIELD_ORDR_JB_CLSF: jb,
        SSAM_FIELD_IS_CD: order_intent.ssam_is_cd,
        SSAM_FIELD_ORDR_CCD: ORDR_CCD_LIMIT,
        SSAM_FIELD_MKT_TM_CLSF: MKT_TM_CLSF_REGULAR,
        SSAM_FIELD_ORDR_Q: _qty_text(order_intent.quantity),
        SSAM_FIELD_CRDT_TYP_CD: CRDT_TYP_CD_CASH,
        SSAM_FIELD_SOR_ORDR_CCD: sor,
    }
    ready = len(unresolved) == 0
    if ready:
        for field in SSAM_EXCEL_REQUIRED_INPUT_FIELDS:
            if field not in data_body or data_body[field] in ("", None):
                unresolved.append(field)
                ready = False
        # Intent/TEA account seal must equal binding used for gnl_ac_no1.
        if data_body.get(SSAM_FIELD_GNL_AC_NO1) != account.gnl_ac_no1:
            unresolved.append(SSAM_FIELD_GNL_AC_NO1)
            ready = False
    payload_for_hash = {
        "api_path": api_path,
        "data_body": data_body,
        "order_intent_id": order_intent.intent_id,
        "order_intent_seal": order_intent.integrity_seal,
    }
    payload_hash = integrity_seal(payload_for_hash)
    seal_payload = {
        "translation_id": translation_id,
        "api_path": api_path,
        "side": order_intent.side,
        "data_body": data_body,
        "unresolved_fields": tuple(unresolved),
        "ready": ready,
        "payload_hash": payload_hash,
        "order_intent_id": order_intent.intent_id,
        "order_intent_seal": order_intent.integrity_seal,
    }
    return SsamRequestTranslation(
        translation_id,
        api_path,
        order_intent.side,
        dict(data_body),
        tuple(unresolved),
        ready,
        payload_hash,
        order_intent.intent_id,
        order_intent.integrity_seal,
        integrity_seal(seal_payload),
    )


def verify_ssam_translation(
    *,
    translation: SsamRequestTranslation,
    order_intent: OrderIntent,
    account: VerifiedExecutionAccountBinding,
) -> None:
    """Require the exact deterministic translation of the sealed intent/account."""
    if type(translation) is not SsamRequestTranslation:
        raise TypeError("SsamRequestTranslation required")
    expected = translate_order_intent_to_ssam(
        translation_id=translation.translation_id,
        order_intent=order_intent,
        account=account,
    )
    if translation != expected:
        raise ValueError("PAYLOAD_HASH_MISMATCH")
