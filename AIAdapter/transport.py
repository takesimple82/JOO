import json
from typing import Any, Protocol
from urllib.request import Request, urlopen


class JSONTransport(Protocol):
    def post(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
        timeout: float,
    ) -> dict[str, Any]:
        ...


class UrllibJSONTransport:
    def post(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
        timeout: float,
    ) -> dict[str, Any]:
        request = Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
        result = json.loads(body)
        if not isinstance(result, dict):
            raise TypeError("Provider response must be an object")
        return result
