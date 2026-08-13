from __future__ import annotations

from abc import ABC, abstractmethod

from ProviderGateway.models.types import (
    ExplicitCollectOutcome,
    ExplicitCollectRequest,
    ExplicitProviderHealthSnapshot,
)


class ProviderInterface(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def declared_source_class(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def collect(
        self,
        request: ExplicitCollectRequest,
    ) -> ExplicitCollectOutcome:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> ExplicitProviderHealthSnapshot:
        raise NotImplementedError
