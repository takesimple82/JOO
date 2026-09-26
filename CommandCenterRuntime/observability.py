from __future__ import annotations

import json
from datetime import datetime, timezone


_SECRET_KEYS = frozenset({
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "gnl_ac_no1",
    "credential",
    "private_key",
})


def _redact(value):
    if type(value) is dict:
        out = {}
        for key, item in value.items():
            if type(key) is str and key.lower() in _SECRET_KEYS:
                out[key] = "***REDACTED***"
            else:
                out[key] = _redact(item)
        return out
    if type(value) is list:
        return [_redact(x) for x in value]
    if type(value) is tuple:
        return tuple(_redact(x) for x in value)
    return value


def structured_event(
    *,
    event_type: str,
    cycle_id: str,
    fields: dict,
    observed_at: datetime | None = None,
) -> str:
    """Structured observability line. Never logs secrets."""
    if observed_at is None:
        observed_at = datetime.now(timezone.utc)
    if type(observed_at) is not datetime or observed_at.tzinfo is not timezone.utc:
        raise ValueError("observed_at must be UTC")
    payload = {
        "event_type": event_type,
        "cycle_id": cycle_id,
        "observed_at": observed_at.isoformat(),
        "fields": _redact(fields),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
