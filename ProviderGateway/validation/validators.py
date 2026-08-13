from __future__ import annotations

from ProviderGateway.models.types import (
    ExplicitCollectOutcome,
    ExplicitCollectRequest,
    ExplicitErrorDiagnostics,
    ExplicitMarketAdapterBinding,
    ExplicitMarketParameterProfile,
    ExplicitProviderFailureSignal,
    ExplicitProviderHealthSnapshot,
    ExplicitProviderPayloadEnvelope,
)
from ProviderGateway.models.vocabularies import (
    AVAILABILITY_VALUES,
    ENVELOPE_STATUS_VALUES,
    FAILURE_CLASS_VALUES,
    RESERVED_KB_OPEN_API_PROVIDER_ID,
    SOURCE_CLASS_VALUES,
)
from ProviderGateway.validation.common import (
    require_exact_type,
    require_membership,
    require_nonblank_string,
    require_optional_nonblank_string,
    require_tuple_of_nonblank_str,
    require_utc_datetime,
)


def validate_explicit_error_diagnostics(
    diagnostics: ExplicitErrorDiagnostics,
) -> None:
    require_exact_type(
        "diagnostics",
        diagnostics,
        ExplicitErrorDiagnostics,
    )
    require_membership(
        "failure_class",
        diagnostics.failure_class,
        FAILURE_CLASS_VALUES,
        "FAILURE_CLASS_VALUES",
    )
    require_optional_nonblank_string(
        "detail",
        diagnostics.detail,
    )


def validate_explicit_provider_payload_envelope(
    envelope: ExplicitProviderPayloadEnvelope,
) -> None:
    require_exact_type(
        "envelope",
        envelope,
        ExplicitProviderPayloadEnvelope,
    )
    require_nonblank_string(
        "envelope_id",
        envelope.envelope_id,
    )
    require_nonblank_string(
        "provider_id",
        envelope.provider_id,
    )
    require_membership(
        "source_class",
        envelope.source_class,
        SOURCE_CLASS_VALUES,
        "SOURCE_CLASS_VALUES",
    )
    require_utc_datetime(
        "collected_at",
        envelope.collected_at,
    )
    require_membership(
        "status",
        envelope.status,
        ENVELOPE_STATUS_VALUES,
        "ENVELOPE_STATUS_VALUES",
    )
    if envelope.status == "success":
        require_exact_type(
            "payload",
            envelope.payload,
            dict,
        )
    else:
        if envelope.payload is not None:
            raise TypeError("payload must be None")
    if envelope.error_diagnostics is not None:
        require_exact_type(
            "error_diagnostics",
            envelope.error_diagnostics,
            ExplicitErrorDiagnostics,
        )
        validate_explicit_error_diagnostics(
            envelope.error_diagnostics
        )
    require_optional_nonblank_string(
        "request_correlation_id",
        envelope.request_correlation_id,
    )


def validate_market_fact_success_envelope(
    envelope: ExplicitProviderPayloadEnvelope,
) -> None:
    validate_explicit_provider_payload_envelope(envelope)
    if envelope.status != "success":
        raise ValueError("status must be success")
    if envelope.source_class != "market_fact":
        raise ValueError("source_class must be market_fact")
    if (
        envelope.provider_id
        == RESERVED_KB_OPEN_API_PROVIDER_ID
    ):
        raise ValueError(
            "provider_id must not be kb_open_api"
        )


def validate_explicit_provider_health_snapshot(
    snapshot: ExplicitProviderHealthSnapshot,
) -> None:
    require_exact_type(
        "snapshot",
        snapshot,
        ExplicitProviderHealthSnapshot,
    )
    require_nonblank_string(
        "provider_id",
        snapshot.provider_id,
    )
    require_utc_datetime(
        "observed_at",
        snapshot.observed_at,
    )
    require_membership(
        "availability",
        snapshot.availability,
        AVAILABILITY_VALUES,
        "AVAILABILITY_VALUES",
    )
    require_optional_nonblank_string(
        "detail",
        snapshot.detail,
    )


def validate_explicit_provider_failure_signal(
    signal: ExplicitProviderFailureSignal,
) -> None:
    require_exact_type(
        "signal",
        signal,
        ExplicitProviderFailureSignal,
    )
    require_nonblank_string(
        "provider_id",
        signal.provider_id,
    )
    require_utc_datetime(
        "observed_at",
        signal.observed_at,
    )
    require_membership(
        "failure_class",
        signal.failure_class,
        FAILURE_CLASS_VALUES,
        "FAILURE_CLASS_VALUES",
    )
    require_optional_nonblank_string(
        "detail",
        signal.detail,
    )
    require_optional_nonblank_string(
        "request_correlation_id",
        signal.request_correlation_id,
    )


def validate_explicit_market_parameter_profile(
    profile: ExplicitMarketParameterProfile,
) -> None:
    require_exact_type(
        "profile",
        profile,
        ExplicitMarketParameterProfile,
    )
    require_nonblank_string(
        "profile_id",
        profile.profile_id,
    )
    require_nonblank_string(
        "venue_target",
        profile.venue_target,
    )
    require_optional_nonblank_string(
        "session_selector",
        profile.session_selector,
    )
    require_optional_nonblank_string(
        "timezone_selector",
        profile.timezone_selector,
    )
    require_optional_nonblank_string(
        "calendar_selector",
        profile.calendar_selector,
    )
    require_tuple_of_nonblank_str(
        "request_set",
        profile.request_set,
    )


def validate_explicit_market_adapter_binding(
    binding: ExplicitMarketAdapterBinding,
) -> None:
    require_exact_type(
        "binding",
        binding,
        ExplicitMarketAdapterBinding,
    )
    require_nonblank_string(
        "provider_id",
        binding.provider_id,
    )
    if binding.provider_id == RESERVED_KB_OPEN_API_PROVIDER_ID:
        raise ValueError(
            "provider_id must not be kb_open_api"
        )
    require_nonblank_string(
        "credential_ref",
        binding.credential_ref,
    )
    require_exact_type(
        "parameter_profile",
        binding.parameter_profile,
        ExplicitMarketParameterProfile,
    )
    validate_explicit_market_parameter_profile(
        binding.parameter_profile
    )


def validate_explicit_collect_request(
    request: ExplicitCollectRequest,
) -> None:
    require_exact_type(
        "request",
        request,
        ExplicitCollectRequest,
    )
    require_nonblank_string(
        "envelope_id",
        request.envelope_id,
    )
    require_optional_nonblank_string(
        "request_correlation_id",
        request.request_correlation_id,
    )
    require_exact_type(
        "binding",
        request.binding,
        ExplicitMarketAdapterBinding,
    )
    validate_explicit_market_adapter_binding(request.binding)


def validate_explicit_collect_outcome(
    outcome: ExplicitCollectOutcome,
) -> None:
    require_exact_type(
        "outcome",
        outcome,
        ExplicitCollectOutcome,
    )
    require_membership(
        "result_kind",
        outcome.result_kind,
        ENVELOPE_STATUS_VALUES,
        "ENVELOPE_STATUS_VALUES",
    )
    if outcome.result_kind == "success":
        require_exact_type(
            "envelope",
            outcome.envelope,
            ExplicitProviderPayloadEnvelope,
        )
        validate_explicit_provider_payload_envelope(
            outcome.envelope
        )
        if outcome.failure is not None:
            raise TypeError("failure must be None")
        return
    require_exact_type(
        "failure",
        outcome.failure,
        ExplicitProviderFailureSignal,
    )
    validate_explicit_provider_failure_signal(
        outcome.failure
    )
    if outcome.envelope is not None:
        raise TypeError("envelope must be None")
