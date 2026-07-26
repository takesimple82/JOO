import pathlib
import unittest
from unittest.mock import patch

from AIAdapter.models import AIRequest, AIResponse
from Committee.models import (
    CommitteeExecution,
    CommitteeExecutionResult,
)
from PipelineRuntime.models import (
    PipelineExecution,
    PipelineExecutionResult,
)
from PipelineRuntime.runtime import PipelineRuntime
from ResearchDomain.models import ResearchTask
from ResearchOrchestrator.orchestrator import (
    ResearchOrchestrator,
)


def make_pipeline() -> PipelineExecution:
    return PipelineExecution(
        pipeline_id="pipeline-001",
        name="Research Pipeline",
        committees=[
            CommitteeExecution(
                committee_id="committee-001",
                name="Market Committee",
                requests=[
                    AIRequest(
                        provider="claude",
                        prompt="Research the company",
                        prompt_id="research",
                        prompt_version="1.0",
                        task_id="task-001",
                    )
                ],
            ),
            CommitteeExecution(
                committee_id="committee-002",
                name="Risk Committee",
                requests=[],
            ),
        ],
    )


def make_task() -> ResearchTask:
    return ResearchTask(
        research_id="research-001",
        title="Company Research",
        objective="Evaluate the investment evidence",
        priority="P1",
        pipeline=make_pipeline(),
    )


def make_result() -> PipelineExecutionResult:
    response = AIResponse(
        provider="claude",
        task_id="task-001",
        prompt_id="research",
        prompt_version="1.0",
        content="provider result",
        status="completed",
        error="",
    )
    return PipelineExecutionResult(
        pipeline_id="pipeline-001",
        committee_results=[
            CommitteeExecutionResult(
                committee_id="committee-001",
                responses=[response],
            ),
            CommitteeExecutionResult(
                committee_id="committee-002",
                responses=[],
            ),
        ],
    )


class RecordingPipelineRuntime(PipelineRuntime):
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.pipelines = []

    def run(self, pipeline):
        self.pipelines.append(pipeline)
        if self.error is not None:
            raise self.error
        return self.result


class ResearchOrchestratorTests(unittest.TestCase):
    def test_constructor_accepts_and_preserves_pipeline_runtime(self):
        runtime = RecordingPipelineRuntime(make_result())

        orchestrator = ResearchOrchestrator(runtime)

        self.assertIs(orchestrator._pipeline_runtime, runtime)

    def test_constructor_rejects_non_pipeline_runtime(self):
        with self.assertRaisesRegex(
            TypeError,
            "pipeline_runtime must be PipelineRuntime",
        ):
            ResearchOrchestrator(object())

    def test_valid_task_delegates_once_and_returns_exact_result(self):
        task = make_task()
        expected = make_result()
        runtime = RecordingPipelineRuntime(expected)

        result = ResearchOrchestrator(runtime).run(task)

        self.assertEqual(runtime.pipelines, [task.pipeline])
        self.assertIs(runtime.pipelines[0], task.pipeline)
        self.assertIs(result, expected)
        self.assertEqual(
            [
                item.committee_id
                for item in result.committee_results
            ],
            ["committee-001", "committee-002"],
        )
        for actual, expected_item in zip(
            result.committee_results,
            expected.committee_results,
        ):
            self.assertIs(actual, expected_item)

    def test_invalid_tasks_fail_before_pipeline_execution(self):
        invalid_cases = (
            (
                "wrong input type",
                object(),
                TypeError,
                "task must be ResearchTask",
            ),
            (
                "blank research id",
                self._task_with(research_id=" "),
                ValueError,
                "research_id must not be blank",
            ),
            (
                "unsupported priority",
                self._task_with(priority="P3"),
                ValueError,
                "priority must be P0, P1, or P2",
            ),
            (
                "invalid pipeline",
                self._task_with(pipeline=object()),
                TypeError,
                "pipeline must be PipelineExecution",
            ),
        )

        for name, task, error_type, message in invalid_cases:
            with self.subTest(case=name):
                runtime = RecordingPipelineRuntime(make_result())
                result = None

                with self.assertRaisesRegex(error_type, message):
                    result = ResearchOrchestrator(runtime).run(task)

                self.assertEqual(runtime.pipelines, [])
                self.assertIsNone(result)

    def test_validation_exception_identity_is_preserved(self):
        task = make_task()
        error = ValueError("validation failed")
        runtime = RecordingPipelineRuntime(make_result())

        with patch(
            (
                "ResearchOrchestrator.orchestrator."
                "validate_research_task"
            ),
            side_effect=error,
        ):
            try:
                ResearchOrchestrator(runtime).run(task)
            except ValueError as caught:
                self.assertIs(caught, error)
            else:
                self.fail("validation exception did not propagate")

        self.assertEqual(runtime.pipelines, [])

    def test_pipeline_exception_propagates_without_retry(self):
        task = make_task()
        error = RuntimeError("pipeline failed")
        runtime = RecordingPipelineRuntime(error=error)
        result = None

        try:
            result = ResearchOrchestrator(runtime).run(task)
        except RuntimeError as caught:
            self.assertIs(caught, error)
        else:
            self.fail("pipeline exception did not propagate")

        self.assertIsNone(result)
        self.assertEqual(runtime.pipelines, [task.pipeline])
        self.assertIs(runtime.pipelines[0], task.pipeline)

    def test_successful_run_does_not_mutate_inputs_or_result(self):
        task = make_task()
        result_object = make_result()
        runtime = RecordingPipelineRuntime(result_object)
        task_values = vars(task).copy()
        pipeline_values = vars(task.pipeline).copy()
        committees = list(task.pipeline.committees)
        committee_values = [
            vars(committee).copy()
            for committee in task.pipeline.committees
        ]
        request_lists = [
            list(committee.requests)
            for committee in task.pipeline.committees
        ]
        result_values = vars(result_object).copy()
        committee_results = list(result_object.committee_results)
        committee_result_values = [
            vars(item).copy()
            for item in result_object.committee_results
        ]
        response_lists = [
            list(item.responses)
            for item in result_object.committee_results
        ]

        actual = ResearchOrchestrator(runtime).run(task)

        self.assertIs(actual, result_object)
        self.assertEqual(vars(task), task_values)
        self.assertEqual(vars(task.pipeline), pipeline_values)
        self.assertEqual(task.pipeline.committees, committees)
        self.assertEqual(
            [vars(item) for item in task.pipeline.committees],
            committee_values,
        )
        self.assertEqual(
            [
                item.requests
                for item in task.pipeline.committees
            ],
            request_lists,
        )
        self.assertEqual(vars(result_object), result_values)
        self.assertEqual(
            result_object.committee_results,
            committee_results,
        )
        self.assertEqual(
            [
                vars(item)
                for item in result_object.committee_results
            ],
            committee_result_values,
        )
        self.assertEqual(
            [
                item.responses
                for item in result_object.committee_results
            ],
            response_lists,
        )

    def test_runtime_isolation(self):
        source = pathlib.Path(
            __file__
        ).parents[1].joinpath("orchestrator.py").read_text()

        self.assertNotIn("CommitteeRuntime", source)
        self.assertNotIn("ExecutionEngine", source)
        self.assertNotIn("AIAdapter", source)
        self.assertNotIn("providers", source)
        self.assertNotIn("ResearchFinding", source)
        self.assertNotIn("ResearchReport", source)

    @staticmethod
    def _task_with(**overrides):
        values = vars(make_task()).copy()
        values.update(overrides)
        return ResearchTask(**values)


if __name__ == "__main__":
    unittest.main()
