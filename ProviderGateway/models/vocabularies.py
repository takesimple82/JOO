from __future__ import annotations


SOURCE_CLASS_VALUES = (
    "broker_fact",
    "market_fact",
    "research_ai",
)

ENVELOPE_STATUS_VALUES = (
    "success",
    "failure",
)

AVAILABILITY_VALUES = (
    "available",
    "degraded",
    "unavailable",
)

FAILURE_CLASS_VALUES = (
    "AUTH_FAILURE",
    "TRANSPORT_FAILURE",
    "PROVIDER_ERROR",
    "UNAVAILABLE",
    "RATE_LIMITED",
    "VALIDATION_FAILURE",
)

RESERVED_KB_OPEN_API_PROVIDER_ID = "kb_open_api"

BROKER_REQUEST_KIND_VALUES = (
    "holdings",
    "balances",
    "account_state",
)
