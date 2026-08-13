from __future__ import annotations

from ProviderGateway.ingress import (
    collect_market_attempt,
    observe_market_health,
    read_utc_clock,
)
from ProviderGateway.models.types import (
    ExplicitCollectOutcome,
    ExplicitCollectRequest,
    ExplicitMarketAdapterBinding,
    ExplicitProviderHealthSnapshot,
)
from ProviderGateway.provider_interface import ProviderInterface
from ProviderGateway.signaling import (
    build_failure_outcome,
    build_provider_failure_signal,
)
from ProviderGateway.validation.validators import (
    validate_explicit_collect_request,
    validate_explicit_market_adapter_binding,
)


class MarketApiAdapter(ProviderInterface):
    def __init__(
        self,
        binding: ExplicitMarketAdapterBinding,
        transport,
        credential_supplier,
        clock,
    ):
        validate_explicit_market_adapter_binding(binding)
        self._binding = binding
        self._transport = transport
        self._credential_supplier = credential_supplier
        self._clock = clock

    @property
    def provider_id(self) -> str:
        return self._binding.provider_id

    @property
    def declared_source_class(self) -> str:
        return "market_fact"

    def collect(
        self,
        request: ExplicitCollectRequest,
    ) -> ExplicitCollectOutcome:
        validate_explicit_collect_request(request)
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
        return collect_market_attempt(
            request,
            self._transport,
            self._credential_supplier,
            self._clock,
        )

    def health(self) -> ExplicitProviderHealthSnapshot:
        return observe_market_health(
            self._binding,
            self._transport,
            self._clock,
        )
