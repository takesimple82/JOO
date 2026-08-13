from __future__ import annotations

from datetime import datetime

from ProviderGateway.models.types import (
    ExplicitCollectOutcome,
    ExplicitProviderFailureSignal,
)
from ProviderGateway.validation.validators import (
    validate_explicit_collect_outcome,
    validate_explicit_provider_failure_signal,
)


def build_provider_failure_signal(
    provider_id: str,
    observed_at: datetime,
    failure_class: str,
    detail: str | None,
    request_correlation_id: str | None,
) -> ExplicitProviderFailureSignal:
    signal = ExplicitProviderFailureSignal(
        provider_id,
        observed_at,
        failure_class,
        detail,
        request_correlation_id,
    )
    validate_explicit_provider_failure_signal(signal)
    return signal


def build_failure_outcome(
    signal: ExplicitProviderFailureSignal,
) -> ExplicitCollectOutcome:
    outcome = ExplicitCollectOutcome(
        "failure",
        None,
        signal,
    )
    validate_explicit_collect_outcome(outcome)
    return outcome
