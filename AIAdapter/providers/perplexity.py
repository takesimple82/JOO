from __future__ import annotations

import os
from typing import Any

from AIAdapter.base import AIAdapter
from AIAdapter.models import AIRequest, AIResponse
from AIAdapter.transport import JSONTransport, UrllibJSONTransport


class PerplexityAdapter(AIAdapter):
    provider = "perplexity"

    def __init__(
        self,
        transport: JSONTransport | None = None,
        api_key: str | None = None,
        model: str | None = None,
        endpoint: str = "https://api.perplexity.ai/v1/sonar",
        timeout: float = 60.0,
    ):
        self._transport = (
            transport
            if transport is not None
            else UrllibJSONTransport()
        )
        self._api_key = (
            api_key
            if api_key is not None
            else os.getenv("PERPLEXITY_API_KEY", "")
        )
        self.model = (
            model
            if model is not None
            else os.getenv("PERPLEXITY_MODEL", "")
        )
        self.endpoint = endpoint
        self.timeout = timeout

    def execute(self, request: AIRequest) -> AIResponse:
        configuration_error = self._configuration_error()
        if configuration_error:
            return self._failure_response(request, configuration_error)
        if not self.validate_request(request):
            return self._failure_response(
                request,
                "Invalid perplexity provider request",
            )

        try:
            response = self._transport.post(
                url=self.endpoint,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                payload={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": request.prompt}
                    ],
                },
                timeout=self.timeout,
            )
            return self.normalize_response(request, response)
        except Exception as error:
            return self._exception_response(request, error)

    def normalize_response(
        self,
        request: AIRequest,
        provider_response: Any,
    ) -> AIResponse:
        content = provider_response["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content:
            raise ValueError("Perplexity response did not contain text")
        return self._success_response(request, content)

    def health_check(self) -> bool:
        return not self._configuration_error()

    def _configuration_error(self) -> str:
        if not self._api_key:
            return "Missing PERPLEXITY_API_KEY"
        if not self.model:
            return "Missing PERPLEXITY_MODEL"
        return ""
