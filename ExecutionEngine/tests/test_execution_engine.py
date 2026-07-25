import unittest
from dataclasses import fields

from AIAdapter.base import AIAdapter
from AIAdapter.models import AIRequest, AIResponse
from ExecutionEngine.base import ExecutionEngine


def make_request(provider: str = "claude") -> AIRequest:
    return AIRequest(
        provider=provider,
        prompt="Research this company",
        prompt_id="research",
        prompt_version="1.0",
        task_id="task-001",
    )


def make_response(request: AIRequest) -> AIResponse:
    return AIResponse(
        provider=request.provider,
        task_id=request.task_id,
        prompt_id=request.prompt_id,
        prompt_version=request.prompt_version,
        content="provider output",
        status="completed",
        error="",
    )


class StubAdapter(AIAdapter):
    def __init__(
        self,
        provider,
        response=None,
        error=None,
    ):
        self.provider = provider
        self.response = response
        self.error = error
        self.calls = 0

    def execute(self, request):
        self.calls += 1
        if self.error:
            raise self.error
        if callable(self.response):
            return self.response(request)
        return self.response

    def normalize_response(self, request, provider_response):
        return provider_response

    def health_check(self):
        return True


class ExecutionEngineTests(unittest.TestCase):
    def test_construction_with_configured_adapters(self):
        engine = ExecutionEngine(
            [StubAdapter("claude"), StubAdapter("gemini")]
        )

        self.assertEqual(
            engine.registered_providers(),
            ("claude", "gemini"),
        )

    def test_successful_resolution_executes_once_and_returns_unchanged(self):
        request = make_request()
        expected = make_response(request)
        adapter = StubAdapter("claude", response=expected)
        engine = ExecutionEngine([adapter])

        result = engine.execute(request)

        self.assertIs(result, expected)
        self.assertEqual(adapter.calls, 1)

    def test_provider_lookup_is_case_insensitive(self):
        request = make_request("CLAUDE")
        expected = make_response(request)
        adapter = StubAdapter("claude", response=expected)

        result = ExecutionEngine([adapter]).execute(request)

        self.assertIs(result, expected)
        self.assertEqual(adapter.calls, 1)

    def test_unsupported_provider_returns_failed_response(self):
        request = make_request("unknown")

        result = ExecutionEngine().execute(request)

        self.assertEqual(
            result,
            AIResponse(
                provider="unknown",
                task_id=request.task_id,
                prompt_id=request.prompt_id,
                prompt_version=request.prompt_version,
                content="",
                status="failed",
                error="Unsupported provider: unknown",
            ),
        )

    def test_duplicate_registration_is_rejected(self):
        engine = ExecutionEngine([StubAdapter("claude")])

        with self.assertRaisesRegex(
            ValueError,
            "provider already registered",
        ):
            engine.register_adapter(StubAdapter("CLAUDE"))

    def test_blank_provider_registration_is_rejected(self):
        for provider in ("", "   "):
            with self.subTest(provider=provider):
                with self.assertRaisesRegex(
                    ValueError,
                    "provider must not be blank",
                ):
                    ExecutionEngine([StubAdapter(provider)])

    def test_non_adapter_registration_is_rejected(self):
        with self.assertRaisesRegex(
            TypeError,
            "adapter must be a concrete AIAdapter",
        ):
            ExecutionEngine([object()])

    def test_non_string_adapter_provider_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "adapter provider must not be blank",
        ):
            ExecutionEngine([StubAdapter(None)])

    def test_failed_later_registration_does_not_leak_registry(self):
        first = StubAdapter("claude")

        with self.assertRaisesRegex(
            ValueError,
            "adapter provider must not be blank",
        ):
            ExecutionEngine([first, StubAdapter(None)])

        fresh_engine = ExecutionEngine()
        self.assertEqual(fresh_engine.registered_providers(), ())
        self.assertEqual(first.calls, 0)

    def test_unexpected_adapter_exception_is_normalized(self):
        request = make_request()
        adapter = StubAdapter(
            "claude",
            error=RuntimeError("secret details"),
        )

        result = ExecutionEngine([adapter]).execute(request)

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.content, "")
        self.assertEqual(
            result.error,
            "Execution failed for provider claude: RuntimeError",
        )
        self.assertNotIn("secret details", result.error)
        self.assertEqual(result.task_id, request.task_id)
        self.assertEqual(result.prompt_id, request.prompt_id)
        self.assertEqual(
            result.prompt_version,
            request.prompt_version,
        )

    def test_non_response_adapter_result_is_normalized(self):
        request = make_request()
        adapter = StubAdapter("claude", response=object())

        result = ExecutionEngine([adapter]).execute(request)

        self.assertEqual(
            result,
            AIResponse(
                provider=request.provider,
                task_id=request.task_id,
                prompt_id=request.prompt_id,
                prompt_version=request.prompt_version,
                content="",
                status="failed",
                error="Invalid response from provider: claude",
            ),
        )

    def test_engine_instances_do_not_share_registry_state(self):
        first = ExecutionEngine([StubAdapter("claude")])
        second = ExecutionEngine()

        self.assertTrue(first.has_provider("claude"))
        self.assertFalse(second.has_provider("claude"))
        self.assertEqual(second.registered_providers(), ())

    def test_execute_does_not_mutate_request(self):
        request = make_request()
        original = AIRequest(**vars(request))
        adapter = StubAdapter(
            "claude",
            response=lambda value: make_response(value),
        )

        ExecutionEngine([adapter]).execute(request)

        self.assertEqual(request, original)

    def test_non_request_input_raises_narrow_type_error(self):
        with self.assertRaisesRegex(TypeError, "request must be AIRequest"):
            ExecutionEngine().execute(object())

    def test_non_string_identity_raises_narrow_type_error(self):
        request = make_request()
        request.provider = None

        with self.assertRaisesRegex(
            TypeError,
            "AIRequest identity fields must be str",
        ):
            ExecutionEngine().execute(request)

    def test_blank_request_fields_return_failed_response(self):
        field_names = (
            "provider",
            "task_id",
            "prompt_id",
            "prompt_version",
            "prompt",
        )
        for field_name in field_names:
            with self.subTest(field=field_name):
                request = make_request()
                setattr(request, field_name, "")

                result = ExecutionEngine().execute(request)

                self.assertEqual(result.status, "failed")
                self.assertEqual(result.content, "")
                self.assertEqual(
                    result.error,
                    f"Invalid execution request field: {field_name}",
                )

    def test_whitespace_only_request_fields_return_failed_response(self):
        field_names = (
            "provider",
            "task_id",
            "prompt_id",
            "prompt_version",
            "prompt",
        )
        whitespace_values = (" ", "   ", "\t", "\n")

        for field_name in field_names:
            for whitespace in whitespace_values:
                with self.subTest(
                    field=field_name,
                    whitespace=repr(whitespace),
                ):
                    request = make_request()
                    setattr(request, field_name, whitespace)
                    original = AIRequest(**vars(request))
                    adapter = StubAdapter("claude")

                    result = ExecutionEngine([adapter]).execute(request)

                    self.assertEqual(result.status, "failed")
                    self.assertEqual(result.content, "")
                    self.assertEqual(
                        result.error,
                        (
                            "Invalid execution request field: "
                            f"{field_name}"
                        ),
                    )
                    self.assertEqual(result.provider, request.provider)
                    self.assertEqual(result.task_id, request.task_id)
                    self.assertEqual(result.prompt_id, request.prompt_id)
                    self.assertEqual(
                        result.prompt_version,
                        request.prompt_version,
                    )
                    self.assertEqual(adapter.calls, 0)
                    self.assertEqual(request, original)

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
