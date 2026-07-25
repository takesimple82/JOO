from __future__ import annotations

import os
from typing import Any

from AIAdapter.base import AIAdapter
from AIAdapter.models import AIRequest, AIResponse


class ClaudeAdapter(AIAdapter):
    provider = "claude"

    def __init__(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ):
        self.model = (
            model
            if model is not None
            else os.getenv("ANTHROPIC_MODEL", "")
        )
        self.max_tokens = max_tokens
        resolved_api_key = (
            api_key
            if api_key is not None
            else os.getenv("ANTHROPIC_API_KEY", "")
        )
        self._configuration_error = ""
        self._client = client

        if self._client is None and not resolved_api_key:
            self._configuration_error = "Missing ANTHROPIC_API_KEY"
        elif self._client is None:
            try:
                from anthropic import Anthropic

                self._client = Anthropic(api_key=resolved_api_key)
            except ImportError:
                self._configuration_error = (
                    "Optional package 'anthropic' is unavailable"
                )
            except Exception as error:
                self._configuration_error = (
                    "Anthropic client initialization failed: "
                    f"{type(error).__name__}"
                )

        if not self.model:
            self._configuration_error = (
                self._configuration_error or "Missing ANTHROPIC_MODEL"
            )

    def execute(self, request: AIRequest) -> AIResponse:
        if self._configuration_error:
            return self._failure_response(
                request,
                self._configuration_error,
            )
        if not self.validate_request(request):
            return self._failure_response(
                request,
                "Invalid claude provider request",
            )

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": request.prompt}],
            )
            return self.normalize_response(request, response)
        except Exception as error:
            return self._exception_response(request, error)

    def normalize_response(
        self,
        request: AIRequest,
        provider_response: Any,
    ) -> AIResponse:
        blocks = getattr(provider_response, "content", ())
        content = "\n".join(
            block.text
            for block in blocks
            if isinstance(getattr(block, "text", None), str)
        )
        if not content:
            raise ValueError("Claude response did not contain text")
        return self._success_response(request, content)

    def health_check(self) -> bool:
        return not self._configuration_error and self._client is not None
