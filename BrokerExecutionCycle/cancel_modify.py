"""D — Cancel/Modify authority (Excel SSAM1805/1806).

Endpoints and Excel-documented fields are modeled for future human-gated use.
Block C does NOT auto-cancel/modify, does NOT place live SSAM1805/1806,
does NOT invent retry policy merely because endpoints exist.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from BrokerExecutionCycle.authority_evidence import (
    CANCEL_API,
    CANCEL_MODIFY_AUTO_POLICY,
    CRCT_CLSF_FULL,
    CRCT_CLSF_PARTIAL,
    MODIFY_API,
)
from BrokerExecutionCycle.vocabularies import (
    CRDT_TYP_CD_CASH,
    FAILURE_CANCEL_MODIFY_NOT_AUTO,
    FAILURE_UNRESOLVED_SSAM_FIELD,
    MKT_TM_CLSF_REGULAR,
    ORDR_CCD_LIMIT,
    ORDR_JB_CLSF_CANCEL,
    ORDR_JB_CLSF_MODIFY,
    SSAM_FIELD_CRCT_CLSF,
    SSAM_FIELD_CRDT_TYP_CD,
    SSAM_FIELD_IS_CD,
    SSAM_FIELD_MKT_TM_CLSF,
    SSAM_FIELD_ORDR_CCD,
    SSAM_FIELD_ORDR_JB_CLSF,
    SSAM_FIELD_ORDR_Q,
    SSAM_FIELD_ORDR_UPRC,
    SSAM_FIELD_ORGN_ORDR_NO,
    SSAM_FIELD_SOR_ORDR_CCD,
)


CANCEL_MODIFY_POLICY = CANCEL_MODIFY_AUTO_POLICY
MODIFY_API_PATH = MODIFY_API
CANCEL_API_PATH = CANCEL_API
MODIFY_JB_CLSF = ORDR_JB_CLSF_MODIFY
CANCEL_JB_CLSF = ORDR_JB_CLSF_CANCEL

CANCEL_MODIFY_STATE_UNKNOWN = "CANCEL_MODIFY_STATE_UNKNOWN"
CANCEL_MODIFY_IDENTITY_ORGN = "orgn_ordr_no"
CANCEL_MODIFY_IDENTITY_NEW = "ordr_no"


@dataclass(frozen=True)
class CancelModifyRequestDraft:
    """Human-gated draft only — never auto-submitted."""

    api_path: str
    data_body: dict
    crct_clsf: str
    orgn_ordr_no: str
    auto_policy: str
    ready: bool
    unresolved: tuple[str, ...]


def assert_no_auto_cancel_modify() -> None:
    raise RuntimeError(FAILURE_CANCEL_MODIFY_NOT_AUTO)


def _integral_text(value: Decimal) -> str:
    if type(value) is not Decimal or not value.is_finite() or value <= Decimal("0"):
        raise ValueError(FAILURE_UNRESOLVED_SSAM_FIELD)
    if value != value.to_integral_value():
        raise ValueError(FAILURE_UNRESOLVED_SSAM_FIELD)
    return format(value, "f")


def _require_orgn(orgn_ordr_no: str) -> str:
    if type(orgn_ordr_no) is not str or orgn_ordr_no.strip() == "":
        raise ValueError(FAILURE_UNRESOLVED_SSAM_FIELD)
    stripped = orgn_ordr_no.strip()
    if set(stripped) <= {"0"}:
        raise ValueError(FAILURE_UNRESOLVED_SSAM_FIELD)
    return stripped


def draft_modify_request(
    *,
    ssam_is_cd: str,
    orgn_ordr_no: str,
    limit_price: Decimal,
    quantity: Decimal,
    crct_clsf: str,
    sor_ordr_ccd: str = "N",
) -> CancelModifyRequestDraft:
    """Excel SSAM1805 required INPUT + sample ordr_jb_clsf=3."""
    unresolved: list[str] = []
    if crct_clsf not in (CRCT_CLSF_PARTIAL, CRCT_CLSF_FULL):
        unresolved.append(SSAM_FIELD_CRCT_CLSF)
    if type(ssam_is_cd) is not str or ssam_is_cd.strip() == "":
        unresolved.append(SSAM_FIELD_IS_CD)
    orgn = ""
    try:
        orgn = _require_orgn(orgn_ordr_no)
    except ValueError:
        unresolved.append(SSAM_FIELD_ORGN_ORDR_NO)
    qty_text = ""
    px_text = ""
    try:
        qty_text = _integral_text(quantity)
    except ValueError:
        unresolved.append(SSAM_FIELD_ORDR_Q)
    try:
        px_text = _integral_text(limit_price)
    except ValueError:
        unresolved.append(SSAM_FIELD_ORDR_UPRC)
    ready = len(unresolved) == 0
    body = {
        SSAM_FIELD_MKT_TM_CLSF: MKT_TM_CLSF_REGULAR,
        SSAM_FIELD_IS_CD: ssam_is_cd if ready or SSAM_FIELD_IS_CD not in unresolved else "",
        SSAM_FIELD_ORDR_Q: qty_text if SSAM_FIELD_ORDR_Q not in unresolved else "",
        SSAM_FIELD_ORDR_UPRC: px_text if SSAM_FIELD_ORDR_UPRC not in unresolved else "",
        SSAM_FIELD_ORDR_CCD: ORDR_CCD_LIMIT,
        SSAM_FIELD_CRCT_CLSF: crct_clsf,
        SSAM_FIELD_ORGN_ORDR_NO: orgn,
        SSAM_FIELD_ORDR_JB_CLSF: ORDR_JB_CLSF_MODIFY,
        SSAM_FIELD_CRDT_TYP_CD: CRDT_TYP_CD_CASH,
        SSAM_FIELD_SOR_ORDR_CCD: sor_ordr_ccd,
    }
    return CancelModifyRequestDraft(
        MODIFY_API_PATH,
        body,
        crct_clsf,
        orgn,
        CANCEL_MODIFY_POLICY,
        ready,
        tuple(unresolved),
    )


def draft_cancel_request(
    *,
    ssam_is_cd: str,
    orgn_ordr_no: str,
    crct_clsf: str,
    quantity: Decimal | None = None,
) -> CancelModifyRequestDraft:
    """Excel SSAM1806: is_cd, crct_clsf, orgn_ordr_no required; ordr_q optional."""
    unresolved: list[str] = []
    if crct_clsf not in (CRCT_CLSF_PARTIAL, CRCT_CLSF_FULL):
        unresolved.append(SSAM_FIELD_CRCT_CLSF)
    if type(ssam_is_cd) is not str or ssam_is_cd.strip() == "":
        unresolved.append(SSAM_FIELD_IS_CD)
    orgn = ""
    try:
        orgn = _require_orgn(orgn_ordr_no)
    except ValueError:
        unresolved.append(SSAM_FIELD_ORGN_ORDR_NO)
    qty_text = None
    if crct_clsf == CRCT_CLSF_PARTIAL:
        if quantity is None:
            unresolved.append(SSAM_FIELD_ORDR_Q)
        else:
            try:
                qty_text = _integral_text(quantity)
            except ValueError:
                unresolved.append(SSAM_FIELD_ORDR_Q)
    elif quantity is not None:
        try:
            qty_text = _integral_text(quantity)
        except ValueError:
            unresolved.append(SSAM_FIELD_ORDR_Q)
    ready = len(unresolved) == 0
    body = {
        SSAM_FIELD_IS_CD: ssam_is_cd if SSAM_FIELD_IS_CD not in unresolved else "",
        SSAM_FIELD_CRCT_CLSF: crct_clsf,
        SSAM_FIELD_ORGN_ORDR_NO: orgn,
        SSAM_FIELD_ORDR_JB_CLSF: ORDR_JB_CLSF_CANCEL,
        SSAM_FIELD_ORDR_CCD: ORDR_CCD_LIMIT,
        SSAM_FIELD_CRDT_TYP_CD: CRDT_TYP_CD_CASH,
    }
    if qty_text is not None and SSAM_FIELD_ORDR_Q not in unresolved:
        body[SSAM_FIELD_ORDR_Q] = qty_text
    return CancelModifyRequestDraft(
        CANCEL_API_PATH,
        body,
        crct_clsf,
        orgn,
        CANCEL_MODIFY_POLICY,
        ready,
        tuple(unresolved),
    )


def map_cancel_modify_terminal_state(
    *,
    remaining_qty: Decimal | None,
    fill_claim: str | None,
    raw_crct_cncl_ccd: str | None,
) -> str:
    """crct_cncl_ccd has no Excel enum table → always UNKNOWN for terminal axis."""
    del remaining_qty, fill_claim, raw_crct_cncl_ccd
    return CANCEL_MODIFY_STATE_UNKNOWN
