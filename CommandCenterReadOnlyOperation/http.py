"""Minimal HTTPS POST implementation restricted to approved KB READ paths."""
from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

from ProviderGateway.adapters.kb_openapi_live_broker_transport import (
    KbOpenApiHttpResponse,
)


_ALLOWED_PATHS = frozenset({
    "/oauth2/token",
    "/api/v1/ssqm2952",
    "/api/v1/ssqm0004",
})
_ALLOWED_NETLOC = "developer.kbsec.com:32484"


def kb_read_only_http_post(url, headers, body, timeout_seconds):
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != _ALLOWED_NETLOC
        or parsed.path not in _ALLOWED_PATHS
    ):
        raise ValueError("KB read-only HTTP path not allowed")
    if type(headers) is not dict or type(body) is not bytes:
        raise TypeError("HTTP request contract mismatch")
    if type(timeout_seconds) is not int or timeout_seconds <= 0:
        raise ValueError("HTTP timeout must be positive int")
    request = Request(url, data=body, headers=headers, method="POST")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return KbOpenApiHttpResponse(
                response.status,
                response.read().decode("utf-8"),
            )
    except HTTPError as exc:
        return KbOpenApiHttpResponse(
            exc.code,
            exc.read().decode("utf-8", errors="replace"),
        )
    except (OSError, URLError) as exc:
        raise RuntimeError("KB read-only transport unavailable") from exc
