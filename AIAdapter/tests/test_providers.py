import builtins
import unittest
from dataclasses import fields
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from AIAdapter.base import AIAdapter
from AIAdapter.models import AIRequest, AIResponse
from AIAdapter.providers.claude import ClaudeAdapter
from AIAdapter.providers.gemini import GeminiAdapter
from AIAdapter.providers.grok import GrokAdapter
from AIAdapter.providers.perplexity import PerplexityAdapter
from AIAdapter.transport import UrllibJSONTransport


def make_request(provider: str) -> AIRequest:
    return AIRequest(
        provider=provider,
        prompt="Research this company",
        prompt_id="research",
        prompt_version="1.0",
        task_id="task-001",
    )


class ClaudeMessages:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.request = None

    def create(self, **request):
        self.request = request
        if self.error:
            raise self.error
        return self.response


class ClaudeClient:
    def __init__(self, response=None, error=None):
        self.messages = ClaudeMessages(response, error)


class GeminiModels:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.request = None

    def generate_content(self, **request):
        self.request = request
        if self.error:
            raise self.error
        return self.response


class GeminiClient:
    def __init__(self, response=None, error=None):
        self.models = GeminiModels(response, error)


class MockTransport:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.request = None

    def post(self, **request):
        self.request = request
        if self.error:
            raise self.error
        return self.response


class FalseyTransport(MockTransport):
    def __bool__(self):
        return False


class MockHTTPResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.body


def configured_adapters():
    chat_response = {
        "choices": [{"message": {"content": "provider output"}}]
    }
    return (
        (
            "claude",
            ClaudeAdapter(
                client=ClaudeClient(
                    SimpleNamespace(
                        content=[SimpleNamespace(text="provider output")]
                    )
                ),
                model="claude-test",
            ),
        ),
        (
            "gemini",
            GeminiAdapter(
                client=GeminiClient(
                    SimpleNamespace(text="provider output")
                ),
                model="gemini-test",
            ),
        ),
        (
            "grok",
            GrokAdapter(
                transport=MockTransport(chat_response),
                api_key="test-key",
                model="grok-test",
            ),
        ),
        (
            "perplexity",
            PerplexityAdapter(
                transport=MockTransport(chat_response),
                api_key="test-key",
                model="sonar-test",
            ),
        ),
    )


def assert_failed_identity(
    test_case,
    request: AIRequest,
    response: AIResponse,
):
    test_case.assertEqual(response.provider, request.provider)
    test_case.assertEqual(response.task_id, request.task_id)
    test_case.assertEqual(response.prompt_id, request.prompt_id)
    test_case.assertEqual(
        response.prompt_version,
        request.prompt_version,
    )
    test_case.assertEqual(response.status, "failed")
    test_case.assertEqual(response.content, "")
    test_case.assertTrue(response.error)


class ProviderAdapterTests(unittest.TestCase):
    def test_supported_adapters_implement_interface(self):
        for provider, adapter in configured_adapters():
            with self.subTest(provider=provider):
                self.assertIsInstance(adapter, AIAdapter)
                self.assertTrue(
                    adapter.validate_request(make_request(provider))
                )
                self.assertTrue(adapter.health_check())

    def test_successful_response_extraction(self):
        for provider, adapter in configured_adapters():
            with self.subTest(provider=provider):
                request = make_request(provider)
                response = adapter.execute(request)

                self.assertEqual(
                    response,
                    AIResponse(
                        provider=provider,
                        task_id=request.task_id,
                        prompt_id=request.prompt_id,
                        prompt_version=request.prompt_version,
                        content="provider output",
                        status="completed",
                        error="",
                    ),
                )

    def test_provider_specific_request_construction(self):
        adapters = dict(configured_adapters())

        claude = adapters["claude"]
        claude.execute(make_request("claude"))
        self.assertEqual(
            claude._client.messages.request,
            {
                "model": "claude-test",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": "Research this company",
                    }
                ],
            },
        )

        gemini = adapters["gemini"]
        gemini.execute(make_request("gemini"))
        self.assertEqual(
            gemini._client.models.request,
            {
                "model": "gemini-test",
                "contents": "Research this company",
            },
        )

        for provider in ("grok", "perplexity"):
            adapter = adapters[provider]
            adapter.execute(make_request(provider))
            self.assertEqual(
                adapter._transport.request["payload"],
                {
                    "model": adapter.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": "Research this company",
                        }
                    ],
                },
            )

    def test_provider_exceptions_return_stable_failed_response(self):
        adapters = (
            (
                "claude",
                ClaudeAdapter(
                    client=ClaudeClient(
                        error=RuntimeError("secret details")
                    ),
                    model="claude-test",
                ),
            ),
            (
                "gemini",
                GeminiAdapter(
                    client=GeminiClient(
                        error=RuntimeError("secret details")
                    ),
                    model="gemini-test",
                ),
            ),
            (
                "grok",
                GrokAdapter(
                    transport=MockTransport(
                        error=RuntimeError("secret details")
                    ),
                    api_key="test-key",
                    model="grok-test",
                ),
            ),
            (
                "perplexity",
                PerplexityAdapter(
                    transport=MockTransport(
                        error=RuntimeError("secret details")
                    ),
                    api_key="test-key",
                    model="sonar-test",
                ),
            ),
        )

        for provider, adapter in adapters:
            with self.subTest(provider=provider):
                response = adapter.execute(make_request(provider))

                self.assertEqual(response.status, "failed")
                self.assertEqual(response.content, "")
                self.assertEqual(
                    response.error,
                    f"{provider} provider request failed: RuntimeError",
                )
                self.assertNotIn("secret details", response.error)

    def test_invalid_requests_return_failed_response(self):
        for provider, adapter in configured_adapters():
            with self.subTest(provider=provider):
                request = make_request(provider)
                request.prompt = ""
                response = adapter.execute(request)

                self.assertEqual(response.status, "failed")
                self.assertEqual(
                    response.error,
                    f"Invalid {provider} provider request",
                )

    def test_missing_configuration_returns_failed_response(self):
        adapters = (
            ("claude", ClaudeAdapter(api_key="", model="")),
            ("gemini", GeminiAdapter(api_key="", model="")),
            ("grok", GrokAdapter(api_key="", model="")),
            ("perplexity", PerplexityAdapter(api_key="", model="")),
        )

        for provider, adapter in adapters:
            with self.subTest(provider=provider):
                response = adapter.execute(make_request(provider))

                self.assertEqual(response.status, "failed")
                self.assertEqual(response.content, "")
                self.assertIn("API_KEY", response.error)
                self.assertFalse(adapter.health_check())

    def test_missing_optional_sdks_return_failed_response(self):
        original_import = builtins.__import__

        def missing_anthropic(name, *args, **kwargs):
            if name == "anthropic":
                raise ModuleNotFoundError("secret anthropic detail")
            return original_import(name, *args, **kwargs)

        def missing_google_genai(name, *args, **kwargs):
            if name == "google":
                raise ModuleNotFoundError("secret google detail")
            return original_import(name, *args, **kwargs)

        cases = (
            (
                "claude",
                missing_anthropic,
                lambda: ClaudeAdapter(
                    api_key="test-key",
                    model="claude-test",
                ),
                "Optional package 'anthropic' is unavailable",
            ),
            (
                "gemini",
                missing_google_genai,
                lambda: GeminiAdapter(
                    api_key="test-key",
                    model="gemini-test",
                ),
                "Optional package 'google-genai' is unavailable",
            ),
        )

        for provider, import_hook, factory, diagnostic in cases:
            with self.subTest(provider=provider):
                with patch("builtins.__import__", side_effect=import_hook):
                    adapter = factory()

                self.assertFalse(adapter.health_check())
                request = make_request(provider)
                response = adapter.execute(request)
                assert_failed_identity(self, request, response)
                self.assertEqual(response.error, diagnostic)
                self.assertNotIn("secret", response.error)

    def test_sdk_client_initialization_exceptions_are_normalized(self):
        class ClientInitializationError(Exception):
            pass

        def fail_client_initialization(**kwargs):
            raise ClientInitializationError("secret constructor detail")

        anthropic = ModuleType("anthropic")
        anthropic.Anthropic = fail_client_initialization
        google = ModuleType("google")
        google.genai = SimpleNamespace(
            Client=fail_client_initialization
        )

        cases = (
            (
                "claude",
                {"anthropic": anthropic},
                lambda: ClaudeAdapter(
                    api_key="test-key",
                    model="claude-test",
                ),
                (
                    "Anthropic client initialization failed: "
                    "ClientInitializationError"
                ),
            ),
            (
                "gemini",
                {"google": google},
                lambda: GeminiAdapter(
                    api_key="test-key",
                    model="gemini-test",
                ),
                (
                    "Gemini client initialization failed: "
                    "ClientInitializationError"
                ),
            ),
        )

        for provider, modules, factory, diagnostic in cases:
            with self.subTest(provider=provider):
                with patch.dict("sys.modules", modules):
                    adapter = factory()

                self.assertFalse(adapter.health_check())
                request = make_request(provider)
                response = adapter.execute(request)
                assert_failed_identity(self, request, response)
                self.assertEqual(response.error, diagnostic)
                self.assertNotIn("secret", response.error)

    def test_claude_empty_or_malformed_responses_fail_safely(self):
        responses = (
            SimpleNamespace(content=[]),
            SimpleNamespace(
                content=[
                    SimpleNamespace(text=None),
                    SimpleNamespace(other="not text"),
                ]
            ),
        )

        for response_value in responses:
            with self.subTest(response=response_value):
                adapter = ClaudeAdapter(
                    client=ClaudeClient(response_value),
                    model="claude-test",
                )
                request = make_request("claude")
                response = adapter.execute(request)

                assert_failed_identity(self, request, response)
                self.assertEqual(
                    response.error,
                    "claude provider request failed: ValueError",
                )

    def test_gemini_empty_or_malformed_responses_fail_safely(self):
        responses = (
            SimpleNamespace(text=""),
            SimpleNamespace(),
            SimpleNamespace(text=123),
        )

        for response_value in responses:
            with self.subTest(response=response_value):
                adapter = GeminiAdapter(
                    client=GeminiClient(response_value),
                    model="gemini-test",
                )
                request = make_request("gemini")
                response = adapter.execute(request)

                assert_failed_identity(self, request, response)
                self.assertEqual(
                    response.error,
                    "gemini provider request failed: ValueError",
                )

    def test_http_provider_malformed_responses_fail_safely(self):
        malformed_responses = (
            {},
            {"choices": []},
            {"choices": [{}]},
            {"choices": [{"message": {}}]},
            {"choices": [{"message": {"content": ""}}]},
            {"choices": [{"message": {"content": 123}}]},
        )
        adapter_factories = (
            (
                "grok",
                lambda response: GrokAdapter(
                    transport=MockTransport(response),
                    api_key="test-key",
                    model="grok-test",
                ),
            ),
            (
                "perplexity",
                lambda response: PerplexityAdapter(
                    transport=MockTransport(response),
                    api_key="test-key",
                    model="sonar-test",
                ),
            ),
        )

        for provider, factory in adapter_factories:
            for malformed_response in malformed_responses:
                with self.subTest(
                    provider=provider,
                    response=malformed_response,
                ):
                    adapter = factory(malformed_response)
                    request = make_request(provider)
                    response = adapter.execute(request)

                    assert_failed_identity(self, request, response)
                    self.assertTrue(
                        response.error.startswith(
                            f"{provider} provider request failed: "
                        )
                    )

    def test_transport_non_object_and_malformed_json_fail_safely(self):
        bodies = (b"[]", b"{not-json")
        adapter_factories = (
            (
                "grok",
                lambda: GrokAdapter(
                    api_key="test-key",
                    model="grok-test",
                ),
            ),
            (
                "perplexity",
                lambda: PerplexityAdapter(
                    api_key="test-key",
                    model="sonar-test",
                ),
            ),
        )

        for provider, factory in adapter_factories:
            for body in bodies:
                with self.subTest(provider=provider, body=body):
                    with patch(
                        "AIAdapter.transport.urlopen",
                        return_value=MockHTTPResponse(body),
                    ):
                        adapter = factory()
                        request = make_request(provider)
                        response = adapter.execute(request)

                    assert_failed_identity(self, request, response)
                    self.assertTrue(
                        response.error.startswith(
                            f"{provider} provider request failed: "
                        )
                    )

    def test_falsey_injected_transports_are_preserved(self):
        response = {
            "choices": [{"message": {"content": "provider output"}}]
        }
        grok_transport = FalseyTransport(response)
        perplexity_transport = FalseyTransport(response)

        grok = GrokAdapter(
            transport=grok_transport,
            api_key="test-key",
            model="grok-test",
        )
        perplexity = PerplexityAdapter(
            transport=perplexity_transport,
            api_key="test-key",
            model="sonar-test",
        )

        self.assertIs(grok._transport, grok_transport)
        self.assertIs(perplexity._transport, perplexity_transport)

    def test_health_checks_do_not_invoke_providers(self):
        for provider, adapter in configured_adapters():
            with self.subTest(provider=provider):
                self.assertTrue(adapter.health_check())

                if provider == "claude":
                    self.assertIsNone(adapter._client.messages.request)
                elif provider == "gemini":
                    self.assertIsNone(adapter._client.models.request)
                else:
                    self.assertIsNone(adapter._transport.request)

    def test_stage_one_dataclass_contracts_are_unchanged(self):
        self.assertEqual(
            [field.name for field in fields(AIRequest)],
            [
                "provider",
                "prompt",
                "prompt_id",
                "prompt_version",
                "task_id",
            ],
        )
        self.assertEqual(
            [field.name for field in fields(AIResponse)],
            [
                "provider",
                "task_id",
                "prompt_id",
                "prompt_version",
                "content",
                "status",
                "error",
            ],
        )


if __name__ == "__main__":
    unittest.main()
