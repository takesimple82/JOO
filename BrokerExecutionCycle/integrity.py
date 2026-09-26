from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from datetime import datetime, timezone
from enum import Enum


def _encode(value):
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is Decimal:
        if not value.is_finite():
            raise ValueError("non-finite Decimal in seal payload")
        return {"decimal": format(value, "f")}
    if type(value) is datetime:
        if value.tzinfo is not timezone.utc:
            raise ValueError("seal datetime must be UTC")
        return {"datetime": value.isoformat()}
    if type(value) is tuple:
        return {"tuple": [_encode(x) for x in value]}
    if isinstance(value, Enum):
        return {"enum": type(value).__name__, "value": value.value}
    if type(value) is dict:
        return {k: _encode(value[k]) for k in sorted(value)}
    raise TypeError(f"unsupported seal payload type: {type(value)!r}")


def canonical_json(payload: dict) -> str:
    if type(payload) is not dict:
        raise TypeError("seal payload must be dict")
    encoded = _encode(payload)
    return json.dumps(encoded, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def integrity_seal(payload: dict) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
