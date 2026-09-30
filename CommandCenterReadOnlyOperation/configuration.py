"""Non-secret, explicit domestic-binding configuration."""
from __future__ import annotations

import json
import re
from pathlib import Path

from CommandCenterReadOnlyOperation.models import (
    DomesticPositionBinding,
    ReadOnlyOperationConfig,
)


_TOP_LEVEL_KEYS = frozenset({
    "schema_version", "account_selector", "portfolio_id",
    "freshness_max_age_seconds", "domestic_bindings",
})
_BINDING_KEYS = frozenset({
    "position_class", "provider_symbol", "position_id",
    "portfolio_subject_id",
})
_FORBIDDEN_KEY = re.compile(
    r"(?i)(secret|token|password|credential|app.?key|authorization)"
)
_FULL_ACCOUNT = re.compile(r"(?<!\d)\d{8,16}(?!\d)")


def _nonblank(name, value):
    if type(value) is not str or value.strip() == "":
        raise ValueError(f"{name} must be a nonblank str")
    return value


def _assert_no_sensitive_configuration(value):
    if type(value) is dict:
        for key, item in value.items():
            if _FORBIDDEN_KEY.search(str(key)):
                raise ValueError("secret-bearing configuration key forbidden")
            _assert_no_sensitive_configuration(item)
    elif type(value) is list:
        for item in value:
            _assert_no_sensitive_configuration(item)


def load_read_only_operation_config(path) -> ReadOnlyOperationConfig:
    if not isinstance(path, (str, Path)):
        raise TypeError("config path required")
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise ValueError("operation config must already exist")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("operation config is unreadable or malformed") from exc
    if type(payload) is not dict or set(payload) != _TOP_LEVEL_KEYS:
        raise ValueError("operation config schema mismatch")
    _assert_no_sensitive_configuration(payload)
    if payload["schema_version"] != 1:
        raise ValueError("unsupported operation config version")
    account_selector = _nonblank("account_selector", payload["account_selector"])
    portfolio_id = _nonblank("portfolio_id", payload["portfolio_id"])
    if _FULL_ACCOUNT.search(account_selector):
        raise ValueError("full brokerage account identifier forbidden")
    max_age = payload["freshness_max_age_seconds"]
    if type(max_age) is not int or max_age <= 0:
        raise ValueError("freshness_max_age_seconds must be positive int")
    rows = payload["domestic_bindings"]
    if type(rows) is not list:
        raise ValueError("domestic_bindings must be list")
    bindings = []
    identities = set()
    position_ids = set()
    subject_ids = set()
    for row in rows:
        if type(row) is not dict or set(row) != _BINDING_KEYS:
            raise ValueError("domestic binding schema mismatch")
        binding = DomesticPositionBinding(*(
            _nonblank(key, row[key])
            for key in (
                "position_class", "provider_symbol", "position_id",
                "portfolio_subject_id",
            )
        ))
        identity = (binding.position_class, binding.provider_symbol)
        if identity in identities:
            raise ValueError("duplicate domestic binding identity")
        if binding.position_id in position_ids:
            raise ValueError("duplicate position_id")
        if binding.portfolio_subject_id in subject_ids:
            raise ValueError("duplicate portfolio_subject_id")
        identities.add(identity)
        position_ids.add(binding.position_id)
        subject_ids.add(binding.portfolio_subject_id)
        bindings.append(binding)
    return ReadOnlyOperationConfig(
        account_selector, portfolio_id, max_age, tuple(bindings)
    )
