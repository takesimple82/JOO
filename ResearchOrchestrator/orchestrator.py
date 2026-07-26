from PipelineRuntime.models import PipelineExecutionResult
from PipelineRuntime.runtime import PipelineRuntime
from ResearchDomain.models import ResearchTask
from ResearchDomain.validation import validate_research_task


class ResearchOrchestrator:
    def __init__(self, pipeline_runtime: PipelineRuntime):
        if not isinstance(pipeline_runtime, PipelineRuntime):
            raise TypeError(
                "pipeline_runtime must be PipelineRuntime"
            )
        self._pipeline_runtime = pipeline_runtime

    def run(
        self,
        task: ResearchTask,
    ) -> PipelineExecutionResult:
        validate_research_task(task)
        return self._pipeline_runtime.run(task.pipeline)
