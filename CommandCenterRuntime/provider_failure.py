from __future__ import annotations

from datetime import datetime, timezone

from CommandCenterRuntime.integrity import integrity_seal
from CommandCenterRuntime.models import ProviderFailureFact


def seal_provider_operation_failure(
    *,
    fact_id: str,
    provider_id: str,
    operation: str,
    detail: str,
    observed_at: datetime,
) -> ProviderFailureFact:
    """Provider outage as data. Missing ≠ 0 / unchanged / safe / approved."""
    if type(observed_at) is not datetime or observed_at.tzinfo is not timezone.utc:
        raise ValueError("observed_at must be UTC")
    for label, value in (
        ("fact_id", fact_id),
        ("provider_id", provider_id),
        ("operation", operation),
        ("detail", detail),
    ):
        if type(value) is not str or value.strip() == "":
            raise ValueError(f"{label} must be nonblank str")
    payload = {
        "fact_id": fact_id,
        "provider_id": provider_id,
        "operation": operation,
        "detail": detail,
        "observed_at": observed_at,
    }
    return ProviderFailureFact(
        fact_id,
        provider_id,
        operation,
        detail,
        observed_at,
        integrity_seal(payload),
    )
