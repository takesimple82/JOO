from collections.abc import Iterable

from AIAdapter.base import AIAdapter
from AIAdapter.models import AIRequest, AIResponse


class ExecutionEngine:
    def __init__(self, adapters: Iterable[AIAdapter] = ()):
        self._adapters: dict[str, AIAdapter] = {}
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

        invalid_field = self._invalid_request_field(request)
        if invalid_field:
            return self._failure_response(
                request,
                f"Invalid execution request field: {invalid_field}",
            )

        adapter = self._adapters.get(request.provider.casefold())
        if adapter is None:
            return self._failure_response(
                request,
                f"Unsupported provider: {request.provider}",
            )

        try:
            response = adapter.execute(request)
        except Exception as error:
            return self._failure_response(
                request,
                (
                    f"Execution failed for provider "
                    f"{request.provider}: {type(error).__name__}"
                ),
            )

        if not isinstance(response, AIResponse):
            return self._failure_response(
                request,
                f"Invalid response from provider: {request.provider}",
            )
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
