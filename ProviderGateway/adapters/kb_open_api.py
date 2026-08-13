from __future__ import annotations

from ProviderGateway.ingress import (
    collect_broker_attempt,
    observe_broker_health,
    read_utc_clock,
)
from ProviderGateway.models.types import (
    ExplicitBrokerAdapterBinding,
    ExplicitBrokerCollectRequest,
    ExplicitCollectOutcome,
    ExplicitProviderHealthSnapshot,
)
from ProviderGateway.provider_interface import ProviderInterface
from ProviderGateway.signaling import (
    build_failure_outcome,
    build_provider_failure_signal,
)
from ProviderGateway.validation.validators import (
    validate_explicit_broker_adapter_binding,
    validate_explicit_broker_collect_request,
)


class KbOpenApiAdapter(ProviderInterface):
    def __init__(
        self,
        binding: ExplicitBrokerAdapterBinding,
        transport,
        credential_supplier,
        clock,
    ):
        validate_explicit_broker_adapter_binding(binding)
        self._binding = binding
        self._transport = transport
        self._credential_supplier = credential_supplier
        self._clock = clock

    @property
    def provider_id(self) -> str:
        return self._binding.provider_id

    @property
    def declared_source_class(self) -> str:
        return "broker_fact"

    def collect(
        self,
        request: ExplicitBrokerCollectRequest,
    ) -> ExplicitCollectOutcome:
        validate_explicit_broker_collect_request(request)
        if (
            request.binding.provider_id
            != self._binding.provider_id
        ):
            signal = build_provider_failure_signal(
                self._binding.provider_id,
                read_utc_clock(self._clock),
                "VALIDATION_FAILURE",
                None,
                request.request_correlation_id,
            )
            return build_failure_outcome(signal)
        return collect_broker_attempt(
            request,
            self._transport,
            self._credential_supplier,
            self._clock,
        )

    def health(self) -> ExplicitProviderHealthSnapshot:
        return observe_broker_health(
            self._binding,
            self._transport,
            self._clock,
        )
