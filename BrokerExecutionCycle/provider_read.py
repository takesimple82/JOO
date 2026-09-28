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
    BROKER_FIELD_CCLS_NTC_CCD,
    BROKER_FIELD_CRCT_CNCL_CCD,
    BROKER_FIELD_NCCLS_Q,
    BROKER_FIELD_NOW_PRC,
    BROKER_FIELD_ORDR_PSBL_CSH,
    BROKER_FIELD_ORDR_PSBL_Q,
    BROKER_FIELD_ORDR_Q_STATUS,
    BROKER_FIELD_ORGN_ORDR_NO,
    BROKER_FIELD_TL_CCLS_Q,
    BROKER_FIELD_TRD_Q_UNT,
    CURRENCY_KRW,
    FAILURE_MISSING_TRADE_UNIT,
    FILL_CLAIM_FULL,
    FILL_CLAIM_NONE,
    FILL_CLAIM_PARTIAL,
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


def _normalize_order_no(raw: object) -> str | None:
    if type(raw) is not str:
        return None
    stripped = raw.strip()
    if stripped == "":
        return None
    return stripped


def _order_nos_equal(a: str | None, b: str | None) -> bool:
    if a is None or b is None:
        return False
    # Compare without leading zeros while preserving all-zero ≠ nonzero.
    sa = a.lstrip("0") or "0"
    sb = b.lstrip("0") or "0"
    return sa == sb


def _classify_fill_from_excel_qty(
    *,
    ordered: Decimal,
    filled: Decimal,
    remaining: Decimal,
) -> str:
    """Excel fields ordr_q / tl_ccls_q / nccls_q only. No HTTP inference."""
    if ordered < Decimal("0") or filled < Decimal("0") or remaining < Decimal("0"):
        return FILL_CLAIM_UNKNOWN
    if filled + remaining != ordered:
        return FILL_CLAIM_UNKNOWN
    if filled == Decimal("0") and remaining == ordered:
        return FILL_CLAIM_NONE
    if filled == ordered and remaining == Decimal("0"):
        return FILL_CLAIM_FULL
    if filled > Decimal("0") and remaining > Decimal("0"):
        return FILL_CLAIM_PARTIAL
    return FILL_CLAIM_UNKNOWN


def normalize_ssqm2341_status(
    *,
    fact_id: str,
    payload: dict,
    query_order_no: str | None,
    query_order_date: str | None,
    collected_at: datetime,
    raw_envelope_id: str,
) -> OrderStatusFact:
    """SSQM2341 — Excel qty fields only; HTTP/processFlag alone ≠ fill."""
    if type(payload) is not dict:
        raise TypeError("payload must be dict")
    header = payload.get("dataHeader")
    body = payload.get("dataBody")
    if type(header) is not dict or type(body) is not dict:
        raise ValueError("SSQM2341 shape invalid")
    process_flag = header.get("processFlag")
    if type(process_flag) is not str:
        process_flag = None
    broker_order_no = _normalize_order_no(body.get("ordr_no"))
    raw_message = body.get("o_msg")
    if type(raw_message) is not str:
        raw_message = None

    fill_claim = FILL_CLAIM_UNKNOWN
    filled_qty = None
    filled_amount = None
    ordered_qty = None
    remaining_qty = None
    matched_ordr_no = None
    orgn_ordr_no = None
    raw_ccls_ntc_ccd = None
    raw_crct_cncl_ccd = None

    records = body.get("Record1")
    matched = None
    if process_flag == PROCESS_FLAG_ACCEPT and type(records) is list and len(records) > 0:
        query = _normalize_order_no(query_order_no)
        for row in records:
            if type(row) is not dict:
                continue
            row_no = _normalize_order_no(row.get("ordr_no"))
            if query is None:
                # Without a query order id, a multi-row grid is ambiguous.
                if len(records) == 1:
                    matched = row
                    break
                matched = None
                break
            if _order_nos_equal(query, row_no):
                matched = row
                break
        if matched is not None:
            matched_ordr_no = _normalize_order_no(matched.get("ordr_no"))
            orgn_ordr_no = _normalize_order_no(matched.get(BROKER_FIELD_ORGN_ORDR_NO))
            ntc = matched.get(BROKER_FIELD_CCLS_NTC_CCD)
            raw_ccls_ntc_ccd = ntc.strip() if type(ntc) is str else None
            crct = matched.get(BROKER_FIELD_CRCT_CNCL_CCD)
            raw_crct_cncl_ccd = crct.strip() if type(crct) is str else None
            try:
                ordered_qty = _parse_unsigned_decimal(
                    matched.get(BROKER_FIELD_ORDR_Q_STATUS),
                    field=BROKER_FIELD_ORDR_Q_STATUS,
                )
                filled_qty = _parse_unsigned_decimal(
                    matched.get(BROKER_FIELD_TL_CCLS_Q),
                    field=BROKER_FIELD_TL_CCLS_Q,
                )
                remaining_qty = _parse_unsigned_decimal(
                    matched.get(BROKER_FIELD_NCCLS_Q),
                    field=BROKER_FIELD_NCCLS_Q,
                )
                fill_claim = _classify_fill_from_excel_qty(
                    ordered=ordered_qty,
                    filled=filled_qty,
                    remaining=remaining_qty,
                )
                # Prefer matched row order no over header body ordr_no.
                if matched_ordr_no is not None:
                    broker_order_no = matched_ordr_no
            except ValueError:
                fill_claim = FILL_CLAIM_UNKNOWN
                filled_qty = None
                ordered_qty = None
                remaining_qty = None
        else:
            fill_claim = FILL_CLAIM_UNKNOWN
    else:
        # Empty Record1, processFlag≠A, or malformed — UNKNOWN (official sample case).
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
        "ordered_qty": ordered_qty,
        "remaining_qty": remaining_qty,
        "matched_ordr_no": matched_ordr_no,
        "orgn_ordr_no": orgn_ordr_no,
        "raw_ccls_ntc_ccd": raw_ccls_ntc_ccd,
        "raw_crct_cncl_ccd": raw_crct_cncl_ccd,
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
        ordered_qty,
        remaining_qty,
        matched_ordr_no,
        orgn_ordr_no,
        raw_ccls_ntc_ccd,
        raw_crct_cncl_ccd,
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
