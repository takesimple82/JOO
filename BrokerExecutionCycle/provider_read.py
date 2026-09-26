from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.instrument import holdings_is_cd_to_ssam_is_cd
from BrokerExecutionCycle.models import (
    OrderStatusFact,
    OrderableCashFact,
    QuoteFact,
    SellableQuantityFact,
    SessionContextFact,
)
from BrokerExecutionCycle.vocabularies import (
    AMOUNT_PRESENCE_MISSING,
    AMOUNT_PRESENCE_PRESENT,
    BROKER_FIELD_NOW_PRC,
    BROKER_FIELD_ORDR_PSBL_CSH,
    BROKER_FIELD_ORDR_PSBL_Q,
    BROKER_FIELD_TRD_Q_UNT,
    CURRENCY_KRW,
    FAILURE_MISSING_TRADE_UNIT,
    FILL_CLAIM_NONE,
    FILL_CLAIM_UNKNOWN,
    MKT_TM_CLSF_REGULAR,
    PROCESS_FLAG_ACCEPT,
)


_UNSIGNED = re.compile(r"^(0|[0-9]+)(\.[0-9]+)?$")


def _parse_unsigned_decimal(raw: object, *, field: str) -> Decimal:
    if type(raw) is not str or raw.strip() == "":
        raise ValueError(f"{field} missing")
    text = raw.strip()
    if _UNSIGNED.fullmatch(text) is None:
        raise ValueError(f"{field} not exact decimal text")
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"{field} not finite") from exc
    if not value.is_finite() or value < Decimal("0"):
        raise ValueError(f"{field} invalid")
    return value


def normalize_ivu10140_quote(
    *,
    fact_id: str,
    payload: dict,
    instrument_ssam_is_cd: str,
    collected_at: datetime,
    raw_envelope_id: str,
) -> QuoteFact:
    """Normalize IVU10140 quote + trade unit. Fail closed if trade unit invalid."""
    if type(payload) is not dict:
        raise TypeError("payload must be dict")
    header = payload.get("dataHeader")
    body = payload.get("dataBody")
    if type(header) is not dict or type(body) is not dict:
        raise ValueError("IVU10140 shape invalid")
    if header.get("processFlag") != PROCESS_FLAG_ACCEPT:
        raise ValueError("IVU10140 processFlag not A")
    now_price = _parse_unsigned_decimal(body.get(BROKER_FIELD_NOW_PRC), field=BROKER_FIELD_NOW_PRC)
    if now_price <= Decimal("0"):
        # Fall back to sprc / bdy_cls_prc only if now_prc is zero and those are present?
        # Mission: no market fallback for *limit price*. Quote fact may use now_prc;
        # if zero, try sprc as quote observation (still not auto limit).
        sprc = body.get("sprc")
        if sprc is not None:
            now_price = _parse_unsigned_decimal(sprc, field="sprc")
    unit_raw = body.get(BROKER_FIELD_TRD_Q_UNT)
    if unit_raw is None or (type(unit_raw) is str and unit_raw.strip() == ""):
        raise ValueError(FAILURE_MISSING_TRADE_UNIT)
    unit = _parse_unsigned_decimal(unit_raw, field=BROKER_FIELD_TRD_Q_UNT)
    if unit <= Decimal("0"):
        raise ValueError(FAILURE_MISSING_TRADE_UNIT)
    payload_seal = {
        "fact_id": fact_id,
        "instrument_ssam_is_cd": instrument_ssam_is_cd,
        "now_price": now_price,
        "trade_quantity_unit": unit,
        "currency_code": CURRENCY_KRW,
        "collected_at": collected_at,
        "raw_envelope_id": raw_envelope_id,
    }
    return QuoteFact(
        fact_id,
        instrument_ssam_is_cd,
        now_price,
        unit,
        CURRENCY_KRW,
        collected_at,
        raw_envelope_id,
        integrity_seal(payload_seal),
    )


def normalize_orderable_cash(
    *,
    fact_id: str,
    payload: dict,
    collected_at: datetime,
    raw_envelope_id: str,
    broker_field: str = BROKER_FIELD_ORDR_PSBL_CSH,
) -> OrderableCashFact:
    """Normalize SSQM0004 / SSQM1802 orderable cash. Present zero ≠ missing."""
    if type(payload) is not dict:
        raise TypeError("payload must be dict")
    header = payload.get("dataHeader")
    body = payload.get("dataBody")
    if type(header) is not dict or type(body) is not dict:
        raise ValueError("cash payload shape invalid")
    if header.get("processFlag") != PROCESS_FLAG_ACCEPT:
        raise ValueError("cash processFlag not A")
    raw = body.get(broker_field)
    if raw is None or (type(raw) is str and raw.strip() == ""):
        presence = AMOUNT_PRESENCE_MISSING
        amount = None
    else:
        presence = AMOUNT_PRESENCE_PRESENT
        amount = _parse_unsigned_decimal(raw, field=broker_field)
    seal_payload = {
        "fact_id": fact_id,
        "presence": presence,
        "amount_krw": amount,
        "currency_code": CURRENCY_KRW,
        "broker_field": broker_field,
        "collected_at": collected_at,
        "raw_envelope_id": raw_envelope_id,
    }
    return OrderableCashFact(
        fact_id,
        presence,
        amount,
        CURRENCY_KRW,
        broker_field,
        collected_at,
        raw_envelope_id,
        integrity_seal(seal_payload),
    )


def normalize_sellable_quantity(
    *,
    fact_id: str,
    payload: dict,
    instrument_ssam_is_cd: str,
    collected_at: datetime,
    raw_envelope_id: str,
) -> SellableQuantityFact:
    """Normalize SSQM1801 Record1 ordr_psbl_q for instrument."""
    if type(payload) is not dict:
        raise TypeError("payload must be dict")
    header = payload.get("dataHeader")
    body = payload.get("dataBody")
    if type(header) is not dict or type(body) is not dict:
        raise ValueError("sellability payload shape invalid")
    if header.get("processFlag") != PROCESS_FLAG_ACCEPT:
        raise ValueError("sellability processFlag not A")
    records = body.get("Record1")
    matched = None
    if type(records) is list:
        for row in records:
            if type(row) is not dict:
                continue
            is_no = row.get("is_no")
            if type(is_no) is not str:
                continue
            bridged = holdings_is_cd_to_ssam_is_cd(is_no)
            if bridged == instrument_ssam_is_cd or is_no == instrument_ssam_is_cd:
                matched = row
                break
    if matched is None:
        presence = AMOUNT_PRESENCE_MISSING
        qty = None
    else:
        raw = matched.get(BROKER_FIELD_ORDR_PSBL_Q)
        if raw is None or (type(raw) is str and raw.strip() == ""):
            presence = AMOUNT_PRESENCE_MISSING
            qty = None
        else:
            presence = AMOUNT_PRESENCE_PRESENT
            qty = _parse_unsigned_decimal(raw, field=BROKER_FIELD_ORDR_PSBL_Q)
    seal_payload = {
        "fact_id": fact_id,
        "instrument_ssam_is_cd": instrument_ssam_is_cd,
        "presence": presence,
        "sellable_qty": qty,
        "collected_at": collected_at,
        "raw_envelope_id": raw_envelope_id,
    }
    return SellableQuantityFact(
        fact_id,
        instrument_ssam_is_cd,
        presence,
        qty,
        collected_at,
        raw_envelope_id,
        integrity_seal(seal_payload),
    )


def normalize_ssqm2341_status(
    *,
    fact_id: str,
    payload: dict,
    query_order_no: str | None,
    query_order_date: str | None,
    collected_at: datetime,
    raw_envelope_id: str,
) -> OrderStatusFact:
    """§19 SSQM2341 — fail closed / UNKNOWN when samples insufficient for fill claims."""
    if type(payload) is not dict:
        raise TypeError("payload must be dict")
    header = payload.get("dataHeader")
    body = payload.get("dataBody")
    if type(header) is not dict or type(body) is not dict:
        raise ValueError("SSQM2341 shape invalid")
    process_flag = header.get("processFlag")
    if type(process_flag) is not str:
        process_flag = None
    broker_order_no = body.get("ordr_no")
    if type(broker_order_no) is not str:
        broker_order_no = None
    raw_message = body.get("o_msg")
    if type(raw_message) is not str:
        raw_message = None
    records = body.get("Record1")
    # Sample fixture has empty Record1 and processFlag B — insufficient for fill certainty.
    if type(records) is not list or len(records) == 0:
        fill_claim = FILL_CLAIM_UNKNOWN
        filled_qty = None
        filled_amount = None
    else:
        # Without documented fill qty fields proven in samples, do not overclaim.
        fill_claim = FILL_CLAIM_UNKNOWN
        filled_qty = None
        filled_amount = None
    if process_flag != PROCESS_FLAG_ACCEPT:
        # Rejected/error query — still UNKNOWN for fill; state observation only.
        fill_claim = FILL_CLAIM_UNKNOWN
    seal_payload = {
        "fact_id": fact_id,
        "query_order_no": query_order_no,
        "query_order_date": query_order_date,
        "process_flag": process_flag,
        "broker_order_no": broker_order_no,
        "fill_claim": fill_claim,
        "filled_qty": filled_qty,
        "filled_amount_krw": filled_amount,
        "raw_message": raw_message,
        "collected_at": collected_at,
        "raw_envelope_id": raw_envelope_id,
    }
    return OrderStatusFact(
        fact_id,
        query_order_no,
        query_order_date,
        process_flag,
        broker_order_no,
        fill_claim,
        filled_qty,
        filled_amount,
        raw_message,
        collected_at,
        raw_envelope_id,
        integrity_seal(seal_payload),
    )


def seal_session_context(
    *,
    session_id: str,
    collected_at: datetime,
    market_time_class: str = MKT_TM_CLSF_REGULAR,
) -> SessionContextFact:
    payload = {
        "session_id": session_id,
        "market_time_class": market_time_class,
        "collected_at": collected_at,
    }
    return SessionContextFact(
        session_id,
        market_time_class,
        collected_at,
        integrity_seal(payload),
    )
