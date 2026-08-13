from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from ProviderGateway.models.types import (
    ExplicitCollectRequest,
    ExplicitMarketAdapterBinding,
)


@dataclass(frozen=True)
class ExplicitTransportSuccess:
    body: dict


@dataclass(frozen=True)
class ExplicitTransportFailure:
    failure_class: str
    detail: str | None


@dataclass(frozen=True)
class ExplicitHealthProbe:
    availability: str
    detail: str | None


class MarketTransport(Protocol):
    def read(
        self,
        binding: ExplicitMarketAdapterBinding,
        credential: str,
        request: ExplicitCollectRequest,
    ) -> ExplicitTransportSuccess | ExplicitTransportFailure:
        ...

    def probe(
        self,
        binding: ExplicitMarketAdapterBinding,
    ) -> ExplicitHealthProbe | ExplicitTransportFailure:
        ...


class CredentialSupplier(Protocol):
    def __call__(self, credential_ref: str) -> object:
        ...


class UtcClock(Protocol):
    def __call__(self) -> datetime:
        ...
