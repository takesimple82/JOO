import unittest
from dataclasses import fields
from typing import get_type_hints

from AIAdapter.models import AIRequest, AIResponse
from Committee.models import (
    CommitteeExecution,
    CommitteeExecutionResult,
)
from Committee.runtime import CommitteeRuntime
from PipelineRuntime.models import (
    PipelineExecution,
    PipelineExecutionResult,
)
from PipelineRuntime.runtime import PipelineRuntime


def make_committee(
    committee_id: str,
    provider: str = "claude",
) -> CommitteeExecution:
    return CommitteeExecution(
        committee_id=committee_id,
        name=f"Committee {committee_id}",
        requests=[
            AIRequest(
                provider=provider,
                prompt=f"Research for {committee_id}",
                prompt_id="research",
                prompt_version="1.0",
                task_id=f"task-{committee_id}",
            )
        ],
    )


def make_result(
    committee: CommitteeExecution,
    status: str = "completed",
) -> CommitteeExecutionResult:
    request = committee.requests[0]
    response = AIResponse(
        provider=request.provider,
        task_id=request.task_id,
        prompt_id=request.prompt_id,
        prompt_version=request.prompt_version,
        content="result" if status == "completed" else "",
        status=status,
        error="" if status == "completed" else "provider failed",
    )
    return CommitteeExecutionResult(
        committee_id=committee.committee_id,
        responses=[response],
    )


class RecordingCommitteeRuntime(CommitteeRuntime):
    def __init__(self, results):
        self._results = iter(results)
        self.committees = []

    def run(self, committee):
        self.committees.append(committee)
        return next(self._results)


class RaisingCommitteeRuntime(CommitteeRuntime):
    def __init__(self, error):
        self.error = error
        self.committees = []

    def run(self, committee):
        self.committees.append(committee)
        raise self.error


class PipelineRuntimeTests(unittest.TestCase):
    def test_model_contracts(self):
        self.assertEqual(
            [field.name for field in fields(PipelineExecution)],
            ["pipeline_id", "name", "committees"],
        )
        self.assertEqual(
            [
                field.name
                for field in fields(PipelineExecutionResult)
            ],
            ["pipeline_id", "committee_results"],
        )
        self.assertEqual(
            get_type_hints(PipelineExecution),
            {
                "pipeline_id": str,
                "name": str,
                "committees": list[CommitteeExecution],
            },
        )
        self.assertEqual(
            get_type_hints(PipelineExecutionResult),
            {
                "pipeline_id": str,
                "committee_results": list[
                    CommitteeExecutionResult
                ],
            },
        )

    def test_runtime_requires_committee_runtime(self):
        with self.assertRaisesRegex(
            TypeError,
            "committee_runtime must be CommitteeRuntime",
        ):
            PipelineRuntime(object())

    def test_run_requires_pipeline_execution(self):
        runtime = PipelineRuntime(RecordingCommitteeRuntime([]))

        with self.assertRaisesRegex(
            TypeError,
            "pipeline must be PipelineExecution",
        ):
            runtime.run(object())

    def test_pipeline_identity_must_be_nonblank_strings(self):
        cases = (
            ("pipeline_id", None, TypeError, "pipeline_id must be str"),
            ("name", None, TypeError, "name must be str"),
            (
                "pipeline_id",
                "",
                ValueError,
                "pipeline_id must not be blank",
            ),
            (
                "pipeline_id",
                " \t",
                ValueError,
                "pipeline_id must not be blank",
            ),
            ("name", "", ValueError, "name must not be blank"),
            ("name", "\n", ValueError, "name must not be blank"),
        )

        for field_name, value, error_type, message in cases:
            with self.subTest(field=field_name, value=value):
                pipeline = PipelineExecution(
                    pipeline_id="pipeline-001",
                    name="Daily Research",
                    committees=[],
                )
                setattr(pipeline, field_name, value)
                runtime = RecordingCommitteeRuntime([])

                with self.assertRaisesRegex(error_type, message):
                    PipelineRuntime(runtime).run(pipeline)

                self.assertEqual(runtime.committees, [])

    def test_committees_must_be_list_of_committee_executions(self):
        runtime = RecordingCommitteeRuntime([])
        pipeline_runtime = PipelineRuntime(runtime)

        with self.assertRaisesRegex(
            TypeError,
            r"committees must be list\[CommitteeExecution\]",
        ):
            pipeline_runtime.run(
                PipelineExecution(
                    pipeline_id="pipeline-001",
                    name="Daily Research",
                    committees=(),
                )
            )

        with self.assertRaisesRegex(
            TypeError,
            "committees must contain only CommitteeExecution",
        ):
            pipeline_runtime.run(
                PipelineExecution(
                    pipeline_id="pipeline-001",
                    name="Daily Research",
                    committees=[object()],
                )
            )

        self.assertEqual(runtime.committees, [])

    def test_committees_execute_once_sequentially_in_order(self):
        committees = [
            make_committee("committee-001", "claude"),
            make_committee("committee-002", "gemini"),
            make_committee("committee-003", "grok"),
        ]
        expected_results = [
            make_result(committee)
            for committee in committees
        ]
        committee_runtime = RecordingCommitteeRuntime(
            expected_results
        )

        result = PipelineRuntime(committee_runtime).run(
            PipelineExecution(
                pipeline_id="pipeline-001",
                name="Daily Research",
                committees=committees,
            )
        )

        self.assertEqual(committee_runtime.committees, committees)
        self.assertEqual(
            len(committee_runtime.committees),
            len(committees),
        )
        for actual, expected in zip(
            result.committee_results,
            expected_results,
        ):
            self.assertIs(actual, expected)

    def test_failed_committee_result_is_preserved_unchanged(self):
        committee = make_committee("committee-001")
        failed_result = make_result(committee, status="failed")
        runtime = RecordingCommitteeRuntime([failed_result])

        result = PipelineRuntime(runtime).run(
            PipelineExecution(
                pipeline_id="pipeline-001",
                name="Daily Research",
                committees=[committee],
            )
        )

        self.assertIs(result.committee_results[0], failed_result)

    def test_committee_exception_propagates_without_continuation(self):
        committees = [
            make_committee("committee-001"),
            make_committee("committee-002"),
        ]
        error = RuntimeError("committee failed")
        committee_runtime = RaisingCommitteeRuntime(error)
        pipeline = PipelineExecution(
            pipeline_id="pipeline-001",
            name="Daily Research",
            committees=committees,
        )
        result = None

        try:
            result = PipelineRuntime(committee_runtime).run(pipeline)
        except RuntimeError as caught:
            self.assertIs(caught, error)
        else:
            self.fail("CommitteeRuntime exception did not propagate")

        self.assertIsNone(result)
        self.assertEqual(committee_runtime.committees, [committees[0]])
        self.assertIs(committee_runtime.committees[0], committees[0])

    def test_empty_pipeline_returns_empty_result(self):
        runtime = RecordingCommitteeRuntime([])
        pipeline = PipelineExecution(
            pipeline_id="pipeline-001",
            name="Daily Research",
            committees=[],
        )

        result = PipelineRuntime(runtime).run(pipeline)

        self.assertEqual(
            result,
            PipelineExecutionResult(
                pipeline_id="pipeline-001",
                committee_results=[],
            ),
        )
        self.assertEqual(runtime.committees, [])

    def test_run_does_not_modify_inputs_or_results(self):
        committee = make_committee("committee-001")
        committee_result = make_result(committee)
        pipeline = PipelineExecution(
            pipeline_id="pipeline-001",
            name="Daily Research",
            committees=[committee],
        )
        original_committees = list(pipeline.committees)
        original_requests = list(committee.requests)
        original_responses = list(committee_result.responses)
        runtime_results = [committee_result]

        result = PipelineRuntime(
            RecordingCommitteeRuntime(runtime_results)
        ).run(pipeline)

        self.assertEqual(pipeline.committees, original_committees)
        self.assertEqual(committee.requests, original_requests)
        self.assertEqual(
            committee_result.responses,
            original_responses,
        )
        self.assertIs(pipeline.committees[0], committee)
        self.assertIs(result.committee_results[0], committee_result)
        self.assertIsNot(result.committee_results, runtime_results)
        self.assertIsNot(
            result.committee_results,
            pipeline.committees,
        )


if __name__ == "__main__":
    unittest.main()
