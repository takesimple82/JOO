from __future__ import annotations

from ProviderGateway.models import (
    ENVELOPE_STATUS_VALUES,
    SOURCE_CLASS_VALUES,
)

ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES = (
    "broker_fact",
    "market_fact",
)

FORBIDDEN_PAYLOAD_SECRET_FIELD_NAMES = (
    "token",
    "password",
    "api_key",
    "apikey",
    "secret",
    "authorization",
    "access_token",
    "refresh_token",
    "credential",
    "credentials",
)
