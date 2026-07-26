from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone

from AIAdapter.base import AIAdapter
from AIAdapter.models import AIRequest, AIResponse
from ExecutionEngine.logging import (
    ExecutionLogger,
    MemoryExecutionLogger,
)
from ExecutionEngine.models import ExecutionLog


class ExecutionEngine:
    def __init__(
        self,
        adapters: Iterable[AIAdapter] = (),
        logger: ExecutionLogger | None = None,
    ):
        self._adapters: dict[str, AIAdapter] = {}
        if logger is not None and not isinstance(logger, ExecutionLogger):
            raise TypeError("logger must be ExecutionLogger")
        self._logger = (
            logger if logger is not None else MemoryExecutionLogger()
        )
        for adapter in adapters:
            self.register_adapter(adapter)

    def register_adapter(self, adapter: AIAdapter) -> None:
        if not isinstance(adapter, AIAdapter):
            raise TypeError("adapter must be a concrete AIAdapter")

        provider = adapter.provider
        if not isinstance(provider, str) or not provider.strip():
            raise ValueError("adapter provider must not be blank")
        if provider != provider.strip():
            raise ValueError(
                "adapter provider must not contain surrounding whitespace"
            )

        key = provider.casefold()
        if key in self._adapters:
            raise ValueError(f"provider already registered: {provider}")
        self._adapters[key] = adapter

    def has_provider(self, provider: str) -> bool:
        return (
            isinstance(provider, str)
            and bool(provider)
            and provider.casefold() in self._adapters
        )

    def registered_providers(self) -> tuple[str, ...]:
        return tuple(
            self._adapters[key].provider
            for key in sorted(self._adapters)
        )

    def prepare(self):
        raise NotImplementedError

    def execute(self, request: AIRequest) -> AIResponse:
        self._validate_input_type(request)
        self._record(request, "start")

        invalid_field = self._invalid_request_field(request)
        if invalid_field:
            response = self._failure_response(
                request,
                f"Invalid execution request field: {invalid_field}",
            )
            self._record_failure(request, response)
            return response

        adapter = self._adapters.get(request.provider.casefold())
        if adapter is None:
            response = self._failure_response(
                request,
                f"Unsupported provider: {request.provider}",
            )
            self._record_failure(request, response)
            return response

        try:
            response = adapter.execute(request)
        except Exception as error:
            response = self._failure_response(
                request,
                (
                    f"Execution failed for provider "
                    f"{request.provider}: {type(error).__name__}"
                ),
            )
            self._record_failure(request, response)
            return response

        if not isinstance(response, AIResponse):
            response = self._failure_response(
                request,
                f"Invalid response from provider: {request.provider}",
            )
            self._record_failure(request, response)
            return response

        if response.status == "completed":
            self._record(request, "success")
        else:
            self._record_failure(request, response)
        return response

    def finalize(self):
        raise NotImplementedError

    def export(self):
        raise NotImplementedError

    @staticmethod
    def _validate_input_type(request: AIRequest) -> None:
        if not isinstance(request, AIRequest):
            raise TypeError("request must be AIRequest")

        identity_fields = (
            request.provider,
            request.task_id,
            request.prompt_id,
            request.prompt_version,
        )
        if not all(isinstance(value, str) for value in identity_fields):
            raise TypeError("AIRequest identity fields must be str")

    @staticmethod
    def _invalid_request_field(request: AIRequest) -> str:
        fields = (
            ("provider", request.provider),
            ("task_id", request.task_id),
            ("prompt_id", request.prompt_id),
            ("prompt_version", request.prompt_version),
            ("prompt", request.prompt),
        )
        for name, value in fields:
            if not isinstance(value, str) or not value.strip():
                return name
        return ""

    @staticmethod
    def _failure_response(
        request: AIRequest,
        error: str,
    ) -> AIResponse:
        return AIResponse(
            provider=request.provider,
            task_id=request.task_id,
            prompt_id=request.prompt_id,
            prompt_version=request.prompt_version,
            content="",
            status="failed",
            error=error,
        )

    def _record_failure(
        self,
        request: AIRequest,
        response: AIResponse,
    ) -> None:
        self._record(request, "failure", response.error)

    def _record(
        self,
        request: AIRequest,
        event_type: str,
        error: str = "",
    ) -> None:
        try:
            entry = ExecutionLog(
                task_id=request.task_id,
                provider=request.provider,
                prompt_id=request.prompt_id,
                prompt_version=request.prompt_version,
                event_type=event_type,
                occurred_at=self._utc_now(),
                error=error,
            )
            self._logger.record(entry)
        except Exception:
            return

    @staticmethod
    def _utc_now() -> str:
        return (
            datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        )
