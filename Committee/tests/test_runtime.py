import unittest
from dataclasses import fields

from AIAdapter.models import AIRequest, AIResponse
from Committee.base import Committee
from Committee.models import (
    CommitteeExecution,
    CommitteeExecutionResult,
    CommitteeResult,
)
from Committee.runtime import CommitteeRuntime
from ExecutionEngine.base import ExecutionEngine


def make_request(provider: str, task_id: str) -> AIRequest:
    return AIRequest(
        provider=provider,
        prompt=f"Research {task_id}",
        prompt_id="research",
        prompt_version="1.0",
        task_id=task_id,
    )


def make_response(request: AIRequest, status="completed") -> AIResponse:
    return AIResponse(
        provider=request.provider,
        task_id=request.task_id,
        prompt_id=request.prompt_id,
        prompt_version=request.prompt_version,
        content=f"Result for {request.task_id}",
        status=status,
        error="" if status == "completed" else "provider failed",
    )


class RecordingExecutionEngine(ExecutionEngine):
    def __init__(self, responses):
        super().__init__()
        self._responses = iter(responses)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return next(self._responses)


class CommitteeRuntimeTests(unittest.TestCase):
    def test_m14_model_contracts(self):
        self.assertEqual(
            [field.name for field in fields(CommitteeExecution)],
            ["committee_id", "name", "requests"],
        )
        self.assertEqual(
            [
                field.name
                for field in fields(CommitteeExecutionResult)
            ],
            ["committee_id", "responses"],
        )

    def test_stage_one_contracts_are_unchanged(self):
        self.assertEqual(
            [
                name
                for name in (
                    "prepare",
                    "execute",
                    "validate",
                    "export",
                )
                if callable(getattr(Committee, name, None))
            ],
            ["prepare", "execute", "validate", "export"],
        )
        self.assertEqual(
            [field.name for field in fields(CommitteeResult)],
            [
                "committee",
                "task_id",
                "provider",
                "prompt_id",
                "prompt_version",
                "status",
                "summary",
                "error",
            ],
        )

    def test_runtime_requires_execution_engine(self):
        with self.assertRaisesRegex(
            TypeError,
            "execution_engine must be ExecutionEngine",
        ):
            CommitteeRuntime(object())

    def test_run_requires_committee(self):
        runtime = CommitteeRuntime(ExecutionEngine())

        with self.assertRaisesRegex(
            TypeError,
            "committee must be CommitteeExecution",
        ):
            runtime.run(object())

    def test_committee_identity_must_be_nonblank_strings(self):
        cases = (
            ("committee_id", None, TypeError, "committee_id must be str"),
            ("name", None, TypeError, "name must be str"),
            (
                "committee_id",
                "",
                ValueError,
                "committee_id must not be blank",
            ),
            (
                "committee_id",
                " \t",
                ValueError,
                "committee_id must not be blank",
            ),
            ("name", "", ValueError, "name must not be blank"),
            ("name", "\n", ValueError, "name must not be blank"),
        )
        runtime = CommitteeRuntime(ExecutionEngine())

        for field_name, value, error_type, message in cases:
            with self.subTest(field=field_name, value=value):
                committee = CommitteeExecution(
                    committee_id="committee-001",
                    name="Market Committee",
                    requests=[],
                )
                setattr(committee, field_name, value)

                with self.assertRaisesRegex(error_type, message):
                    runtime.run(committee)

    def test_requests_must_be_list_of_ai_requests(self):
        runtime = CommitteeRuntime(ExecutionEngine())

        with self.assertRaisesRegex(
            TypeError,
            r"requests must be list\[AIRequest\]",
        ):
            runtime.run(
                CommitteeExecution(
                    committee_id="committee-001",
                    name="Market Committee",
                    requests=(),
                )
            )

        with self.assertRaisesRegex(
            TypeError,
            "requests must contain only AIRequest",
        ):
            runtime.run(
                CommitteeExecution(
                    committee_id="committee-001",
                    name="Market Committee",
                    requests=[object()],
                )
            )

    def test_requests_execute_sequentially_and_preserve_order(self):
        requests = [
            make_request("claude", "task-001"),
            make_request("gemini", "task-002"),
            make_request("grok", "task-003"),
        ]
        responses = [make_response(request) for request in requests]
        engine = RecordingExecutionEngine(responses)
        runtime = CommitteeRuntime(engine)

        result = runtime.run(
            CommitteeExecution(
                committee_id="committee-001",
                name="Market Committee",
                requests=requests,
            )
        )

        self.assertEqual(result.committee_id, "committee-001")
        self.assertEqual(engine.requests, requests)
        self.assertEqual(len(result.responses), len(responses))
        for actual, expected in zip(result.responses, responses):
            self.assertIs(actual, expected)

    def test_failed_responses_are_preserved_unchanged(self):
        request = make_request("claude", "task-001")
        response = make_response(request, status="failed")
        runtime = CommitteeRuntime(
            RecordingExecutionEngine([response])
        )

        result = runtime.run(
            CommitteeExecution(
                committee_id="committee-001",
                name="Risk Committee",
                requests=[request],
            )
        )

        self.assertIs(result.responses[0], response)

    def test_empty_committee_returns_empty_result(self):
        committee = CommitteeExecution(
            committee_id="committee-001",
            name="Market Committee",
            requests=[],
        )

        result = CommitteeRuntime(ExecutionEngine()).run(committee)

        self.assertEqual(
            result,
            CommitteeExecutionResult(
                committee_id="committee-001",
                responses=[],
            ),
        )

    def test_run_does_not_modify_committee_requests_or_responses(self):
        request = make_request("claude", "task-001")
        response = make_response(request)
        committee = CommitteeExecution(
            committee_id="committee-001",
            name="Market Committee",
            requests=[request],
        )
        original_request = AIRequest(**vars(request))
        original_response = AIResponse(**vars(response))
        original_requests = list(committee.requests)

        result = CommitteeRuntime(
            RecordingExecutionEngine([response])
        ).run(committee)

        self.assertEqual(request, original_request)
        self.assertEqual(response, original_response)
        self.assertEqual(committee.requests, original_requests)
        self.assertIs(committee.requests[0], request)
        self.assertIs(result.responses[0], response)
        self.assertIsNot(result.responses, committee.requests)


if __name__ == "__main__":
    unittest.main()
