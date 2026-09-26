from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from KbCapitalFactAuthority.models import ExplicitExactAmount
from KbCapitalFactAuthority.vocabularies import (
    AMOUNT_PRESENCE_MISSING,
    AMOUNT_PRESENCE_PRESENT,
)


_DECIMAL_TEXT = re.compile(r"^(0|-?[0-9]+)(\.[0-9]+)?$")
_UNSIGNED_DECIMAL_TEXT = re.compile(r"^(0|[0-9]+)(\.[0-9]+)?$")


def missing_amount() -> ExplicitExactAmount:
    return ExplicitExactAmount(
        AMOUNT_PRESENCE_MISSING,
        None,
        None,
    )


def parse_broker_amount(
    raw: object,
    *,
    field_name: str,
    allow_missing: bool,
    unsigned: bool = True,
) -> ExplicitExactAmount:
    if raw is None:
        if allow_missing:
            return missing_amount()
        raise ValueError(f"{field_name} is missing")
    if type(raw) is not str:
        raise TypeError(f"{field_name} must be str")
    if raw.strip() == "":
        if allow_missing:
            return missing_amount()
        raise ValueError(f"{field_name} must not be blank")
    pattern = _UNSIGNED_DECIMAL_TEXT if unsigned else _DECIMAL_TEXT
    if pattern.fullmatch(raw) is None:
        raise ValueError(
            f"{field_name} must be exact decimal text"
        )
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(
            f"{field_name} must be finite Decimal"
        ) from exc
    if not value.is_finite():
        raise ValueError(f"{field_name} must be finite")
    if unsigned and value < Decimal(0):
        raise ValueError(f"{field_name} must be nonnegative")
    return ExplicitExactAmount(
        AMOUNT_PRESENCE_PRESENT,
        format(value, "f"),
        raw,
    )


def require_present_amount(
    amount: ExplicitExactAmount,
    *,
    field_name: str,
) -> ExplicitExactAmount:
    if type(amount) is not ExplicitExactAmount:
        raise TypeError("amount must be ExplicitExactAmount")
    if amount.presence != AMOUNT_PRESENCE_PRESENT:
        raise ValueError(f"{field_name} must be present")
    if amount.canonical_text is None or amount.raw_text is None:
        raise ValueError(f"{field_name} present amount incomplete")
    return amount
