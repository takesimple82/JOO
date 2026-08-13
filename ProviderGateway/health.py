from __future__ import annotations

from datetime import datetime

from ProviderGateway.models.types import (
    ExplicitProviderHealthSnapshot,
)
from ProviderGateway.validation.validators import (
    validate_explicit_provider_health_snapshot,
)


def build_provider_health_snapshot(
    provider_id: str,
    observed_at: datetime,
    availability: str,
    detail: str | None,
) -> ExplicitProviderHealthSnapshot:
    snapshot = ExplicitProviderHealthSnapshot(
        provider_id,
        observed_at,
        availability,
        detail,
    )
    validate_explicit_provider_health_snapshot(snapshot)
    return snapshot
