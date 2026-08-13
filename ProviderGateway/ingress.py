from __future__ import annotations

from datetime import datetime, timezone

from ProviderGateway.adapters.ports import (
    ExplicitHealthProbe,
    ExplicitTransportFailure,
    ExplicitTransportSuccess,
)
from ProviderGateway.auth.credentials import (
    apply_outbound_credential,
    payload_contains_secret,
    project_opaque_payload,
    resolve_outbound_credential,
    sanitize_detail,
)
from ProviderGateway.health import build_provider_health_snapshot
from ProviderGateway.models.types import (
    ExplicitBrokerAdapterBinding,
    ExplicitBrokerCollectRequest,
    ExplicitCollectOutcome,
    ExplicitCollectRequest,
    ExplicitMarketAdapterBinding,
    ExplicitProviderHealthSnapshot,
    ExplicitProviderPayloadEnvelope,
)
from ProviderGateway.models.vocabularies import (
    AVAILABILITY_VALUES,
    FAILURE_CLASS_VALUES,
)
from ProviderGateway.signaling import (
    build_failure_outcome,
    build_provider_failure_signal,
)
from ProviderGateway.validation.validators import (
    validate_broker_fact_success_envelope,
    validate_explicit_broker_collect_request,
    validate_explicit_collect_outcome,
    validate_explicit_collect_request,
    validate_market_fact_success_envelope,
)


def read_utc_clock(clock) -> datetime:
    observed_at = clock()
    if type(observed_at) is not datetime:
        raise TypeError("collected_at must be datetime")
    if observed_at.tzinfo is not timezone.utc:
        raise ValueError(
            "collected_at tzinfo must be datetime.timezone.utc"
        )
    return observed_at


def _usable_wire_body(body: object) -> bool:
    return type(body) is dict and len(body) > 0


def _known_failure_class(failure_class: object) -> str:
    if (
        type(failure_class) is str
        and failure_class in FAILURE_CLASS_VALUES
    ):
        return failure_class
    return "VALIDATION_FAILURE"


def _failure_outcome(
    binding: ExplicitMarketAdapterBinding,
    clock,
    failure_class: str,
    detail: str | None,
    request_correlation_id: str | None,
    secret: str | None,
) -> ExplicitCollectOutcome:
    signal = build_provider_failure_signal(
        binding.provider_id,
        read_utc_clock(clock),
        _known_failure_class(failure_class),
        sanitize_detail(detail, secret),
        request_correlation_id,
    )
    return build_failure_outcome(signal)


def _broker_failure_outcome(
    binding: ExplicitBrokerAdapterBinding,
    clock,
    failure_class: str,
    detail: str | None,
    request_correlation_id: str | None,
    secret: str | None,
) -> ExplicitCollectOutcome:
    signal = build_provider_failure_signal(
        binding.provider_id,
        read_utc_clock(clock),
        _known_failure_class(failure_class),
        sanitize_detail(detail, secret),
        request_correlation_id,
    )
    return build_failure_outcome(signal)


def collect_market_attempt(
    request: ExplicitCollectRequest,
    transport,
    credential_supplier,
    clock,
) -> ExplicitCollectOutcome:
    validate_explicit_collect_request(request)
    binding = request.binding
    secret = resolve_outbound_credential(
        binding.credential_ref,
        credential_supplier,
    )
    if secret is None:
        return _failure_outcome(
            binding,
            clock,
            "AUTH_FAILURE",
            None,
            request.request_correlation_id,
            None,
        )
    outbound_credential = apply_outbound_credential(secret)
    try:
        result = transport.read(
            binding,
            outbound_credential,
            request,
        )
    except Exception:
        return _failure_outcome(
            binding,
            clock,
            "TRANSPORT_FAILURE",
            None,
            request.request_correlation_id,
            secret,
        )
    if type(result) is ExplicitTransportFailure:
        return _failure_outcome(
            binding,
            clock,
            result.failure_class,
            result.detail,
            request.request_correlation_id,
            secret,
        )
    if type(result) is not ExplicitTransportSuccess:
        return _failure_outcome(
            binding,
            clock,
            "VALIDATION_FAILURE",
            None,
            request.request_correlation_id,
            secret,
        )
    if not _usable_wire_body(result.body):
        return _failure_outcome(
            binding,
            clock,
            "VALIDATION_FAILURE",
            None,
            request.request_correlation_id,
            secret,
        )
    payload = project_opaque_payload(result.body)
    if not _usable_wire_body(payload):
        return _failure_outcome(
            binding,
            clock,
            "VALIDATION_FAILURE",
            None,
            request.request_correlation_id,
            secret,
        )
    if payload_contains_secret(payload, secret):
        return _failure_outcome(
            binding,
            clock,
            "VALIDATION_FAILURE",
            None,
            request.request_correlation_id,
            secret,
        )
    collected_at = read_utc_clock(clock)
    envelope = ExplicitProviderPayloadEnvelope(
        request.envelope_id,
        binding.provider_id,
        "market_fact",
        collected_at,
        "success",
        payload,
        None,
        request.request_correlation_id,
    )
    validate_market_fact_success_envelope(envelope)
    outcome = ExplicitCollectOutcome(
        "success",
        envelope,
        None,
    )
    validate_explicit_collect_outcome(outcome)
    return outcome


def _availability_for_probe_failure(
    failure_class: str,
) -> str:
    if failure_class in ("RATE_LIMITED", "PROVIDER_ERROR"):
        return "degraded"
    return "unavailable"


def observe_market_health(
    binding: ExplicitMarketAdapterBinding,
    transport,
    clock,
) -> ExplicitProviderHealthSnapshot:
    try:
        probe = transport.probe(binding)
    except Exception:
        return build_provider_health_snapshot(
            binding.provider_id,
            read_utc_clock(clock),
            "unavailable",
            None,
        )
    if type(probe) is ExplicitTransportFailure:
        return build_provider_health_snapshot(
            binding.provider_id,
            read_utc_clock(clock),
            _availability_for_probe_failure(
                _known_failure_class(probe.failure_class)
            ),
            sanitize_detail(probe.detail, None),
        )
    if type(probe) is not ExplicitHealthProbe:
        return build_provider_health_snapshot(
            binding.provider_id,
            read_utc_clock(clock),
            "unavailable",
            None,
        )
    availability = probe.availability
    if (
        type(availability) is not str
        or availability not in AVAILABILITY_VALUES
    ):
        availability = "unavailable"
    return build_provider_health_snapshot(
        binding.provider_id,
        read_utc_clock(clock),
        availability,
        sanitize_detail(probe.detail, None),
    )


def collect_broker_attempt(
    request: ExplicitBrokerCollectRequest,
    transport,
    credential_supplier,
    clock,
) -> ExplicitCollectOutcome:
    validate_explicit_broker_collect_request(request)
    binding = request.binding
    secret = resolve_outbound_credential(
        binding.credential_ref,
        credential_supplier,
    )
    if secret is None:
        return _broker_failure_outcome(
            binding,
            clock,
            "AUTH_FAILURE",
            None,
            request.request_correlation_id,
            None,
        )
    outbound_credential = apply_outbound_credential(secret)
    try:
        result = transport.read(
            binding,
            outbound_credential,
            request,
        )
    except Exception:
        return _broker_failure_outcome(
            binding,
            clock,
            "TRANSPORT_FAILURE",
            None,
            request.request_correlation_id,
            secret,
        )
    if type(result) is ExplicitTransportFailure:
        return _broker_failure_outcome(
            binding,
            clock,
            result.failure_class,
            result.detail,
            request.request_correlation_id,
            secret,
        )
    if type(result) is not ExplicitTransportSuccess:
        return _broker_failure_outcome(
            binding,
            clock,
            "VALIDATION_FAILURE",
            None,
            request.request_correlation_id,
            secret,
        )
    if not _usable_wire_body(result.body):
        return _broker_failure_outcome(
            binding,
            clock,
            "VALIDATION_FAILURE",
            None,
            request.request_correlation_id,
            secret,
        )
    payload = project_opaque_payload(result.body)
    if not _usable_wire_body(payload):
        return _broker_failure_outcome(
            binding,
            clock,
            "VALIDATION_FAILURE",
            None,
            request.request_correlation_id,
            secret,
        )
    if payload_contains_secret(payload, secret):
        return _broker_failure_outcome(
            binding,
            clock,
            "VALIDATION_FAILURE",
            None,
            request.request_correlation_id,
            secret,
        )
    collected_at = read_utc_clock(clock)
    envelope = ExplicitProviderPayloadEnvelope(
        request.envelope_id,
        binding.provider_id,
        "broker_fact",
        collected_at,
        "success",
        payload,
        None,
        request.request_correlation_id,
    )
    validate_broker_fact_success_envelope(envelope)
    outcome = ExplicitCollectOutcome(
        "success",
        envelope,
        None,
    )
    validate_explicit_collect_outcome(outcome)
    return outcome


def observe_broker_health(
    binding: ExplicitBrokerAdapterBinding,
    transport,
    clock,
) -> ExplicitProviderHealthSnapshot:
    try:
        probe = transport.probe(binding)
    except Exception:
        return build_provider_health_snapshot(
            binding.provider_id,
            read_utc_clock(clock),
            "unavailable",
            None,
        )
    if type(probe) is ExplicitTransportFailure:
        return build_provider_health_snapshot(
            binding.provider_id,
            read_utc_clock(clock),
            _availability_for_probe_failure(
                _known_failure_class(probe.failure_class)
            ),
            sanitize_detail(probe.detail, None),
        )
    if type(probe) is not ExplicitHealthProbe:
        return build_provider_health_snapshot(
            binding.provider_id,
            read_utc_clock(clock),
            "unavailable",
            None,
        )
    availability = probe.availability
    if (
        type(availability) is not str
        or availability not in AVAILABILITY_VALUES
    ):
        availability = "unavailable"
    return build_provider_health_snapshot(
        binding.provider_id,
        read_utc_clock(clock),
        availability,
        sanitize_detail(probe.detail, None),
    )
