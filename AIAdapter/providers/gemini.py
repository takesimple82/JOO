from __future__ import annotations

import os
from typing import Any

from AIAdapter.base import AIAdapter
from AIAdapter.models import AIRequest, AIResponse


class GeminiAdapter(AIAdapter):
    provider = "gemini"

    def __init__(
        self,
        client: Any | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.model = (
            model
            if model is not None
            else os.getenv("GEMINI_MODEL", "")
        )
        resolved_api_key = (
            api_key
            if api_key is not None
            else os.getenv("GEMINI_API_KEY", "")
        )
        self._configuration_error = ""
        self._client = client

        if self._client is None and not resolved_api_key:
            self._configuration_error = "Missing GEMINI_API_KEY"
        elif self._client is None:
            try:
                from google import genai

                self._client = genai.Client(api_key=resolved_api_key)
            except ImportError:
                self._configuration_error = (
                    "Optional package 'google-genai' is unavailable"
                )
            except Exception as error:
                self._configuration_error = (
                    "Gemini client initialization failed: "
                    f"{type(error).__name__}"
                )

        if not self.model:
            self._configuration_error = (
                self._configuration_error or "Missing GEMINI_MODEL"
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
                "Invalid gemini provider request",
            )

        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=request.prompt,
            )
            return self.normalize_response(request, response)
        except Exception as error:
            return self._exception_response(request, error)

    def normalize_response(
        self,
        request: AIRequest,
        provider_response: Any,
    ) -> AIResponse:
        content = getattr(provider_response, "text", None)
        if not isinstance(content, str) or not content:
            raise ValueError("Gemini response did not contain text")
        return self._success_response(request, content)

    def health_check(self) -> bool:
        return not self._configuration_error and self._client is not None
