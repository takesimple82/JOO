"""Public JSON presentation with defense-in-depth redaction."""
from __future__ import annotations

import json
import re
from dataclasses import asdict

from CommandCenterApplication.models import CommandCenterView


_SECRET_KEYS = frozenset({
    "appkey", "appsecret", "access_token", "token", "authorization",
    "password", "secret", "credential", "api_key", "gnl_ac_no1",
})
_SECRET_TEXT = re.compile(
    r"(?i)(bearer\s+[a-z0-9._-]+|(?:app.?key|app.?secret|access.?token|"
    r"api.?key|password|secret|credential)\s*[:=]\s*\S+)"
)
_ACCOUNT_NUMBER = re.compile(r"(?<!\d)(\d{8,16})(?!\d)")
_EXACT_NUMBER_KEYS = frozenset({
    "portfolio_value_krw", "orderable_cash_krw", "deployed_capital_krw",
    "available_allocation_capacity_krw", "explicit_reserve_krw",
    "max_position_krw", "broker_account_valuation_krw", "market_value_krw",
    "current_market_value_krw", "proposed_market_value_krw",
    "delta_market_value_krw", "quantity", "weight_percent", "value",
    "provider_symbol",
})


def _masked_text(value: str) -> str:
    value = _SECRET_TEXT.sub("[REDACTED]", value)
    return _ACCOUNT_NUMBER.sub(lambda m: "••••" + m.group(1)[-4:], value)


def _sanitize(value, *, key=None):
    if type(value) is str:
        if key in _EXACT_NUMBER_KEYS:
            return value
        return _masked_text(value)
    if type(value) is dict:
        result = {}
        for key, item in value.items():
            if str(key).casefold() in _SECRET_KEYS:
                result[key] = "[REDACTED]"
            else:
                result[key] = _sanitize(item, key=str(key))
        return result
    if type(value) is list:
        return [_sanitize(x, key=key) for x in value]
    if type(value) is tuple:
        return [_sanitize(x, key=key) for x in value]
    return value


def public_dict(view: CommandCenterView) -> dict:
    if type(view) is not CommandCenterView:
        raise TypeError("CommandCenterView required")
    return _sanitize(asdict(view))


def public_json(view: CommandCenterView) -> bytes:
    return json.dumps(
        public_dict(view), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
