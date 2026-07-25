from abc import ABC, abstractmethod
from typing import Any

from AIAdapter.models import AIRequest, AIResponse


class AIAdapter(ABC):
    provider = ""

    def validate_request(self, request: AIRequest) -> bool:
        return (
            isinstance(request, AIRequest)
            and bool(self.provider)
            and request.provider.casefold() == self.provider.casefold()
            and bool(request.prompt)
            and bool(request.prompt_id)
            and bool(request.prompt_version)
            and bool(request.task_id)
        )

    @abstractmethod
    def execute(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError

    @abstractmethod
    def normalize_response(
        self,
        request: AIRequest,
        provider_response: Any,
    ) -> AIResponse:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        raise NotImplementedError

    @staticmethod
    def _success_response(
        request: AIRequest,
        content: str,
    ) -> AIResponse:
        return AIResponse(
            provider=request.provider,
            task_id=request.task_id,
            prompt_id=request.prompt_id,
            prompt_version=request.prompt_version,
            content=content,
            status="completed",
            error="",
        )

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

    def _exception_response(
        self,
        request: AIRequest,
        error: Exception,
    ) -> AIResponse:
        diagnostic = (
            f"{self.provider} provider request failed: "
            f"{type(error).__name__}"
        )
        return self._failure_response(request, diagnostic)
