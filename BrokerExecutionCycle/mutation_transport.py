from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from BrokerExecutionCycle.vocabularies import (
    ACCEPTANCE_UNKNOWN,
    FAILURE_LIVE_MUTATION_DISABLED,
    MUTATION_TRANSPORT_LIVE_DISABLED,
    MUTATION_TRANSPORT_MOCK,
    PROCESS_FLAG_ACCEPT,
    PROCESS_FLAG_REJECT,
)


@dataclass(frozen=True)
class MutationTransportResponse:
    http_status: int | None
    process_flag: str | None
    ordr_no: str | None
    raw_message: str | None
    transport_error: str | None


class MutationTransport(Protocol):
    def submit(self, api_path: str, data_body: dict) -> MutationTransportResponse:
        ...


class LiveMutationTransportDisabled:
    """§15 live disabled by default. Never calls SSAM against production."""

    mode = MUTATION_TRANSPORT_LIVE_DISABLED

    def submit(self, api_path: str, data_body: dict) -> MutationTransportResponse:
        del api_path, data_body
        raise RuntimeError(FAILURE_LIVE_MUTATION_DISABLED)


class MockMutationTransport:
    """Mock-only SSAM mutation transport for tests."""

    mode = MUTATION_TRANSPORT_MOCK

    def __init__(
        self,
        *,
        process_flag: str = PROCESS_FLAG_ACCEPT,
        ordr_no: str = "0040000638",
        http_status: int = 200,
        raw_message: str = "mock accept",
        raise_timeout: bool = False,
        drop_response: bool = False,
    ):
        self.process_flag = process_flag
        self.ordr_no = ordr_no
        self.http_status = http_status
        self.raw_message = raw_message
        self.raise_timeout = raise_timeout
        self.drop_response = drop_response
        self.calls: list[tuple[str, dict]] = []

    def submit(self, api_path: str, data_body: dict) -> MutationTransportResponse:
        self.calls.append((api_path, dict(data_body)))
        if self.raise_timeout:
            return MutationTransportResponse(
                None, None, None, None, ACCEPTANCE_UNKNOWN
            )
        if self.drop_response:
            return MutationTransportResponse(
                self.http_status, None, None, None, ACCEPTANCE_UNKNOWN
            )
        return MutationTransportResponse(
            self.http_status,
            self.process_flag,
            self.ordr_no if self.process_flag == PROCESS_FLAG_ACCEPT else "0000000000",
            self.raw_message,
            None,
        )


def default_mutation_transport() -> LiveMutationTransportDisabled:
    return LiveMutationTransportDisabled()
