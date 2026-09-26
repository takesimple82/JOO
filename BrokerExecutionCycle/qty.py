from __future__ import annotations

from decimal import Decimal

from ExactDecimalArithmetic.arithmetic import multiply_exact_decimal

from BrokerExecutionCycle.vocabularies import (
    FAILURE_DERIVED_NOTIONAL_EXCEEDS_APPROVED,
    FAILURE_INVALID_LIMIT_PRICE,
    FAILURE_INVALID_QTY,
    FAILURE_MISSING_TRADE_UNIT,
)


def _require_positive_decimal(name: str, value: object) -> Decimal:
    if type(value) is not Decimal:
        raise TypeError(f"{name} must be Decimal")
    if not value.is_finite():
        raise ValueError(f"{name} must be finite")
    if value <= Decimal("0"):
        raise ValueError(f"{name} must be > 0")
    return value


def _floor_div_nonneg(numerator: Decimal, denominator: Decimal) -> Decimal:
    """Exact floor division for nonnegative Decimals. No float."""
    _require_positive_decimal("denominator", denominator)
    if type(numerator) is not Decimal or not numerator.is_finite():
        raise TypeError("numerator must be finite Decimal")
    if numerator < Decimal("0"):
        raise ValueError("numerator must be nonnegative")
    # Decimal // is floor division; keep domain on Decimal only.
    return numerator // denominator


def derive_limit_quantity(
    *,
    approved_notional: Decimal,
    limit_price: Decimal,
    trade_quantity_unit: Decimal | None,
) -> tuple[Decimal, Decimal, Decimal]:
    """C0-D3 qty derivation.

    raw_qty = floor(approved_notional / limit_price)
    derived_qty = floor(raw_qty / trade_quantity_unit) * trade_quantity_unit
    derived_notional = derived_qty * limit_price
    Fail closed if trade unit missing/invalid (do NOT assume 1).
    """
    if trade_quantity_unit is None:
        raise ValueError(FAILURE_MISSING_TRADE_UNIT)
    unit = trade_quantity_unit
    if type(unit) is not Decimal or not unit.is_finite() or unit <= Decimal("0"):
        raise ValueError(FAILURE_MISSING_TRADE_UNIT)
    notional = _require_positive_decimal("approved_notional", approved_notional)
    price = _require_positive_decimal("limit_price", limit_price)
    raw_qty = _floor_div_nonneg(notional, price)
    if raw_qty <= Decimal("0"):
        raise ValueError(FAILURE_INVALID_QTY)
    units = _floor_div_nonneg(raw_qty, unit)
    derived_qty = multiply_exact_decimal(units, unit)
    if derived_qty <= Decimal("0"):
        raise ValueError(FAILURE_INVALID_QTY)
    derived_notional = multiply_exact_decimal(derived_qty, price)
    if derived_notional > notional:
        raise ValueError(FAILURE_DERIVED_NOTIONAL_EXCEEDS_APPROVED)
    return raw_qty, derived_qty, derived_notional


def require_valid_limit_price(price: object) -> Decimal:
    try:
        return _require_positive_decimal("limit_price", price)
    except (TypeError, ValueError) as exc:
        raise ValueError(FAILURE_INVALID_LIMIT_PRICE) from exc
