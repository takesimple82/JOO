from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.models import (
    OrderableCashFact,
    PreTradeFactBundle,
    PreTradeValidationFinding,
    PreTradeValidationResult,
    ProposedLimitPrice,
    QuoteFact,
    SellableQuantityFact,
    SessionContextFact,
    InstrumentIdentityBinding,
    VerifiedExecutionAccountBinding,
)
from BrokerExecutionCycle.qty import derive_limit_quantity, require_valid_limit_price
from BrokerExecutionCycle.vocabularies import (
    AMOUNT_PRESENCE_PRESENT,
    CURRENCY_KRW,
    FAILURE_ACCOUNT_UNVERIFIED,
    FAILURE_BUY_CASH_INSUFFICIENT,
    FAILURE_EXPOSURE_CAP,
    FAILURE_INSTRUMENT_UNPROVEN,
    FAILURE_INVALID_LIMIT_PRICE,
    FAILURE_INVALID_QTY,
    FAILURE_MISSING_PROPOSED_LIMIT_PRICE,
    FAILURE_MISSING_TRADE_UNIT,
    FAILURE_PRETRADE_STALE,
    FAILURE_SELL_EXCEEDS_SELLABLE,
    FAILURE_SIDE_INVALID,
    HIP_V1_MAX_EXPOSURE_KRW,
    SIDE_BUY,
    SIDE_SELL,
)


CONSTRAINT_PASS = "PASS"
CONSTRAINT_FAIL = "FAIL"


def seal_proposed_limit_price(
    *,
    proposal_id: str,
    instrument_ssam_is_cd: str,
    limit_price: Decimal,
    bound_at: datetime,
    principal: str,
    currency_code: str = CURRENCY_KRW,
) -> ProposedLimitPrice:
    price = require_valid_limit_price(limit_price)
    if type(principal) is not str or principal.strip() == "":
        raise ValueError(FAILURE_MISSING_PROPOSED_LIMIT_PRICE)
    payload = {
        "proposal_id": proposal_id,
        "instrument_ssam_is_cd": instrument_ssam_is_cd,
        "limit_price": price,
        "currency_code": currency_code,
        "bound_at": bound_at,
        "principal": principal,
    }
    return ProposedLimitPrice(
        proposal_id,
        instrument_ssam_is_cd,
        price,
        currency_code,
        bound_at,
        principal,
        integrity_seal(payload),
    )


def seal_pretrade_fact_bundle(
    *,
    bundle_id: str,
    quote: QuoteFact,
    orderable_cash: OrderableCashFact,
    sellable: SellableQuantityFact | None,
    instrument: InstrumentIdentityBinding,
    account: VerifiedExecutionAccountBinding,
    session: SessionContextFact,
    proposed_limit_price: ProposedLimitPrice,
    collected_at: datetime,
) -> PreTradeFactBundle:
    payload = {
        "bundle_id": bundle_id,
        "quote_seal": quote.integrity_seal,
        "cash_seal": orderable_cash.integrity_seal,
        "sellable_seal": None if sellable is None else sellable.integrity_seal,
        "instrument_seal": instrument.integrity_seal,
        "account_seal": account.integrity_seal,
        "session_seal": session.integrity_seal,
        "proposed_limit_price_seal": proposed_limit_price.integrity_seal,
        "collected_at": collected_at,
    }
    return PreTradeFactBundle(
        bundle_id,
        quote,
        orderable_cash,
        sellable,
        instrument,
        account,
        session,
        proposed_limit_price,
        collected_at,
        integrity_seal(payload),
    )


def _finding(code: str, status: str, detail: str) -> PreTradeValidationFinding:
    return PreTradeValidationFinding(code, status, detail)


def validate_pretrade(
    *,
    validation_id: str,
    bundle: PreTradeFactBundle,
    side: str,
    approved_notional_krw: Decimal,
    validated_at: datetime,
    max_exposure_krw: Decimal | None = None,
) -> PreTradeValidationResult:
    """Fail-closed pre-trade matrix (C0-D3/D4 + cash/sellable/exposure)."""
    findings: list[PreTradeValidationFinding] = []
    raw_qty = None
    derived_qty = None
    derived_notional = None
    exposure_cap = (
        Decimal(HIP_V1_MAX_EXPOSURE_KRW)
        if max_exposure_krw is None
        else max_exposure_krw
    )

    if side not in (SIDE_BUY, SIDE_SELL):
        findings.append(_finding(FAILURE_SIDE_INVALID, CONSTRAINT_FAIL, "side"))
    if not bundle.instrument.proven:
        findings.append(
            _finding(FAILURE_INSTRUMENT_UNPROVEN, CONSTRAINT_FAIL, "instrument")
        )
    if bundle.account.mutation_eligible is not True:
        findings.append(
            _finding(FAILURE_ACCOUNT_UNVERIFIED, CONSTRAINT_FAIL, "account")
        )
    try:
        price = require_valid_limit_price(bundle.proposed_limit_price.limit_price)
    except ValueError:
        findings.append(
            _finding(FAILURE_INVALID_LIMIT_PRICE, CONSTRAINT_FAIL, "limit_price")
        )
        price = None
    if (
        price is not None
        and bundle.proposed_limit_price.instrument_ssam_is_cd
        != bundle.instrument.ssam_is_cd
        and bundle.instrument.proven
    ):
        findings.append(
            _finding(
                FAILURE_PRETRADE_STALE,
                CONSTRAINT_FAIL,
                "proposed price instrument mismatch",
            )
        )
    if type(approved_notional_krw) is not Decimal or not approved_notional_krw.is_finite():
        findings.append(_finding(FAILURE_INVALID_QTY, CONSTRAINT_FAIL, "notional"))
        approved_notional_krw = Decimal("0")
    elif approved_notional_krw <= Decimal("0"):
        findings.append(_finding(FAILURE_INVALID_QTY, CONSTRAINT_FAIL, "notional<=0"))

    if not findings:
        try:
            raw_qty, derived_qty, derived_notional = derive_limit_quantity(
                approved_notional=approved_notional_krw,
                limit_price=price,
                trade_quantity_unit=bundle.quote.trade_quantity_unit,
            )
        except ValueError as exc:
            code = str(exc) if str(exc) else FAILURE_MISSING_TRADE_UNIT
            findings.append(_finding(code, CONSTRAINT_FAIL, "qty"))

    if derived_notional is not None and derived_notional > exposure_cap:
        findings.append(
            _finding(FAILURE_EXPOSURE_CAP, CONSTRAINT_FAIL, "exposure")
        )

    if side == SIDE_BUY and derived_notional is not None:
        cash = bundle.orderable_cash
        if (
            cash.presence != AMOUNT_PRESENCE_PRESENT
            or cash.amount_krw is None
            or cash.amount_krw < derived_notional
        ):
            findings.append(
                _finding(FAILURE_BUY_CASH_INSUFFICIENT, CONSTRAINT_FAIL, "cash")
            )

    if side == SIDE_SELL and derived_qty is not None:
        sellable = bundle.sellable
        if (
            sellable is None
            or sellable.presence != AMOUNT_PRESENCE_PRESENT
            or sellable.sellable_qty is None
            or sellable.sellable_qty < derived_qty
        ):
            findings.append(
                _finding(FAILURE_SELL_EXCEEDS_SELLABLE, CONSTRAINT_FAIL, "sellable")
            )
        elif (
            bundle.instrument.proven
            and sellable.instrument_ssam_is_cd != bundle.instrument.ssam_is_cd
        ):
            findings.append(
                _finding(FAILURE_INSTRUMENT_UNPROVEN, CONSTRAINT_FAIL, "sellable is_cd")
            )

    passed = len(findings) == 0
    if passed:
        findings.append(_finding("PRETRADE_OK", CONSTRAINT_PASS, "ok"))

    payload = {
        "validation_id": validation_id,
        "bundle_id": bundle.bundle_id,
        "bundle_integrity_seal": bundle.integrity_seal,
        "side": side,
        "approved_notional_krw": approved_notional_krw,
        "raw_qty": raw_qty,
        "derived_qty": derived_qty,
        "derived_notional_krw": derived_notional,
        "passed": passed,
        "findings": tuple((f.code, f.status, f.detail) for f in findings),
        "validated_at": validated_at,
    }
    return PreTradeValidationResult(
        validation_id,
        bundle.bundle_id,
        bundle.integrity_seal,
        side,
        approved_notional_krw,
        raw_qty,
        derived_qty,
        derived_notional,
        passed,
        tuple(findings),
        validated_at,
        integrity_seal(payload),
    )
