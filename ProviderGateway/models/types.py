from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ExplicitErrorDiagnostics:
    failure_class: str
    detail: str | None


@dataclass(frozen=True)
class ExplicitProviderPayloadEnvelope:
    envelope_id: str
    provider_id: str
    source_class: str
    collected_at: datetime
    status: str
    payload: dict | None
    error_diagnostics: ExplicitErrorDiagnostics | None
    request_correlation_id: str | None


@dataclass(frozen=True)
class ExplicitProviderHealthSnapshot:
    provider_id: str
    observed_at: datetime
    availability: str
    detail: str | None


@dataclass(frozen=True)
class ExplicitProviderFailureSignal:
    provider_id: str
    observed_at: datetime
    failure_class: str
    detail: str | None
    request_correlation_id: str | None


@dataclass(frozen=True)
class ExplicitMarketParameterProfile:
    profile_id: str
    venue_target: str
    session_selector: str | None
    timezone_selector: str | None
    calendar_selector: str | None
    request_set: tuple[str, ...]


@dataclass(frozen=True)
class ExplicitMarketAdapterBinding:
    provider_id: str
    credential_ref: str
    parameter_profile: ExplicitMarketParameterProfile


@dataclass(frozen=True)
class ExplicitCollectRequest:
    envelope_id: str
    request_correlation_id: str | None
    binding: ExplicitMarketAdapterBinding


@dataclass(frozen=True)
class ExplicitCollectOutcome:
    result_kind: str
    envelope: ExplicitProviderPayloadEnvelope | None
    failure: ExplicitProviderFailureSignal | None


@dataclass(frozen=True)
class ExplicitBrokerParameterProfile:
    profile_id: str
    account_selector: str
    request_set: tuple[str, ...]


@dataclass(frozen=True)
class ExplicitBrokerAdapterBinding:
    provider_id: str
    credential_ref: str
    parameter_profile: ExplicitBrokerParameterProfile


@dataclass(frozen=True)
class ExplicitBrokerCollectRequest:
    envelope_id: str
    request_correlation_id: str | None
    binding: ExplicitBrokerAdapterBinding
    request_kind: str
