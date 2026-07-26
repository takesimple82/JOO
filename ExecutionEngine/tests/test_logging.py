import re
import unittest
from dataclasses import FrozenInstanceError, fields

from AIAdapter.base import AIAdapter
from AIAdapter.models import AIRequest, AIResponse
from ExecutionEngine.base import ExecutionEngine
from ExecutionEngine.logging import (
    ExecutionLogger,
    MemoryExecutionLogger,
)
from ExecutionEngine.models import ExecutionLog


def make_request(provider: str = "claude") -> AIRequest:
    return AIRequest(
        provider=provider,
        prompt="Research this company",
        prompt_id="research",
        prompt_version="1.0",
        task_id="task-001",
    )


def make_response(
    request: AIRequest,
    status: str = "completed",
    error: str = "",
) -> AIResponse:
    return AIResponse(
        provider=request.provider,
        task_id=request.task_id,
        prompt_id=request.prompt_id,
        prompt_version=request.prompt_version,
        content="provider output" if status == "completed" else "",
        status=status,
        error=error,
    )


class StubAdapter(AIAdapter):
    def __init__(self, response=None, error=None):
        self.provider = "claude"
        self.response = response
        self.error = error
        self.calls = 0

    def execute(self, request):
        self.calls += 1
        if self.error:
            raise self.error
        return self.response

    def normalize_response(self, request, provider_response):
        return provider_response

    def health_check(self):
        return True


class RaisingLogger(ExecutionLogger):
    def record(self, entry):
        raise RuntimeError("logging unavailable")


class ExecutionLoggingTests(unittest.TestCase):
    def test_execution_log_contract(self):
        self.assertEqual(
            [field.name for field in fields(ExecutionLog)],
            [
                "task_id",
                "provider",
                "prompt_id",
                "prompt_version",
                "event_type",
                "occurred_at",
                "error",
            ],
        )

    def test_execution_log_is_immutable(self):
        entry = self._make_log()

        with self.assertRaises(FrozenInstanceError):
            entry.event_type = "failure"

    def test_execution_log_rejects_invalid_event_type(self):
        with self.assertRaisesRegex(
            ValueError,
            "event_type must be start, success, or failure",
        ):
            self._make_log(event_type="complete")

    def test_execution_log_rejects_non_string_fields(self):
        field_names = (
            "task_id",
            "provider",
            "prompt_id",
            "prompt_version",
            "occurred_at",
            "error",
        )
        for field_name in field_names:
            with self.subTest(field=field_name):
                with self.assertRaisesRegex(
                    TypeError,
                    f"{field_name} must be str",
                ):
                    self._make_log(**{field_name: None})

    def test_memory_logger_records_entries_in_order(self):
        logger = MemoryExecutionLogger()
        entry = ExecutionLog(
            task_id="task-001",
            provider="claude",
            prompt_id="research",
            prompt_version="1.0",
            event_type="start",
            occurred_at="2026-07-26T00:00:00Z",
            error="",
        )

        logger.record(entry)

        self.assertEqual(logger.entries(), (entry,))

    def test_memory_logger_rejects_non_log_entries(self):
        with self.assertRaisesRegex(TypeError, "entry must be ExecutionLog"):
            MemoryExecutionLogger().record(object())

    def test_success_records_start_and_success(self):
        request = make_request()
        response = make_response(request)
        adapter = StubAdapter(response=response)
        logger = MemoryExecutionLogger()

        result = ExecutionEngine([adapter], logger=logger).execute(request)

        self.assertIs(result, response)
        self.assertEqual(adapter.calls, 1)
        self.assertEqual(
            [entry.event_type for entry in logger.entries()],
            ["start", "success"],
        )
        self._assert_log_identity(logger.entries(), request)
        self._assert_utc_timestamps(logger.entries())
        self.assertEqual(logger.entries()[1].error, "")

    def test_all_engine_failure_paths_record_start_and_failure(self):
        request = make_request()
        cases = (
            (
                "unsupported provider",
                request,
                (),
                "Unsupported provider: claude",
            ),
            (
                "blank prompt",
                AIRequest(
                    provider="claude",
                    prompt=" ",
                    prompt_id="research",
                    prompt_version="1.0",
                    task_id="task-001",
                ),
                (StubAdapter(),),
                "Invalid execution request field: prompt",
            ),
            (
                "adapter exception",
                request,
                (StubAdapter(error=RuntimeError("secret")),),
                "Execution failed for provider claude: RuntimeError",
            ),
            (
                "invalid adapter response",
                request,
                (StubAdapter(response=object()),),
                "Invalid response from provider: claude",
            ),
            (
                "failed adapter response",
                request,
                (
                    StubAdapter(
                        response=make_response(
                            request,
                            status="failed",
                            error="provider failed",
                        )
                    ),
                ),
                "provider failed",
            ),
        )

        for name, case_request, adapters, expected_error in cases:
            with self.subTest(case=name):
                logger = MemoryExecutionLogger()
                engine = ExecutionEngine(adapters, logger=logger)

                result = engine.execute(case_request)

                self.assertEqual(
                    [entry.event_type for entry in logger.entries()],
                    ["start", "failure"],
                )
                self._assert_log_identity(
                    logger.entries(),
                    case_request,
                )
                self.assertEqual(
                    logger.entries()[1].error,
                    expected_error,
                )
                self.assertIsInstance(result, AIResponse)

    def test_logger_injection_is_validated(self):
        with self.assertRaisesRegex(
            TypeError,
            "logger must be ExecutionLogger",
        ):
            ExecutionEngine(logger=object())

    def test_logger_exceptions_do_not_change_success_response(self):
        request = make_request()
        response = make_response(request)
        engine = ExecutionEngine(
            [StubAdapter(response=response)],
            logger=RaisingLogger(),
        )

        result = engine.execute(request)

        self.assertIs(result, response)

    def test_logger_exceptions_do_not_change_failure_response(self):
        request = make_request("unsupported")
        engine = ExecutionEngine(logger=RaisingLogger())

        result = engine.execute(request)

        self.assertEqual(result.status, "failed")
        self.assertEqual(
            result.error,
            "Unsupported provider: unsupported",
        )

    def test_log_construction_failure_does_not_change_response(self):
        request = make_request()
        response = make_response(request, status="failed")
        response.error = None
        logger = MemoryExecutionLogger()
        engine = ExecutionEngine(
            [StubAdapter(response=response)],
            logger=logger,
        )

        result = engine.execute(request)

        self.assertIs(result, response)
        self.assertEqual(
            [entry.event_type for entry in logger.entries()],
            ["start"],
        )

    def test_unrepresentable_inputs_are_rejected_before_logging(self):
        logger = MemoryExecutionLogger()
        engine = ExecutionEngine(logger=logger)

        with self.assertRaises(TypeError):
            engine.execute(object())

        request = make_request()
        request.task_id = None
        with self.assertRaises(TypeError):
            engine.execute(request)

        self.assertEqual(logger.entries(), ())

    def test_logger_instances_do_not_share_entries(self):
        first = MemoryExecutionLogger()
        second = MemoryExecutionLogger()
        request = make_request()

        ExecutionEngine(logger=first).execute(request)

        self.assertEqual(len(first.entries()), 2)
        self.assertEqual(second.entries(), ())

    def test_request_is_not_mutated_by_logging(self):
        request = make_request()
        original = AIRequest(**vars(request))

        ExecutionEngine(logger=MemoryExecutionLogger()).execute(request)

        self.assertEqual(request, original)

    def _assert_log_identity(self, entries, request):
        for entry in entries:
            self.assertEqual(entry.task_id, request.task_id)
            self.assertEqual(entry.provider, request.provider)
            self.assertEqual(entry.prompt_id, request.prompt_id)
            self.assertEqual(
                entry.prompt_version,
                request.prompt_version,
            )

    def _assert_utc_timestamps(self, entries):
        pattern = re.compile(
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        )
        for entry in entries:
            self.assertRegex(entry.occurred_at, pattern)

    def _make_log(self, **overrides):
        values = {
            "task_id": "task-001",
            "provider": "claude",
            "prompt_id": "research",
            "prompt_version": "1.0",
            "event_type": "start",
            "occurred_at": "2026-07-26T00:00:00Z",
            "error": "",
        }
        values.update(overrides)
        return ExecutionLog(**values)


if __name__ == "__main__":
    unittest.main()
