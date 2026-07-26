from Committee.models import CommitteeExecution
from Committee.runtime import CommitteeRuntime
from PipelineRuntime.models import (
    PipelineExecution,
    PipelineExecutionResult,
)


class PipelineRuntime:
    def __init__(self, committee_runtime: CommitteeRuntime) -> None:
        if not isinstance(committee_runtime, CommitteeRuntime):
            raise TypeError(
                "committee_runtime must be CommitteeRuntime"
            )
        self._committee_runtime = committee_runtime

    def run(
        self,
        pipeline: PipelineExecution,
    ) -> PipelineExecutionResult:
        self._validate_pipeline(pipeline)

        committee_results = [
            self._committee_runtime.run(committee)
            for committee in pipeline.committees
        ]
        return PipelineExecutionResult(
            pipeline_id=pipeline.pipeline_id,
            committee_results=committee_results,
        )

    @staticmethod
    def _validate_pipeline(pipeline: PipelineExecution) -> None:
        if not isinstance(pipeline, PipelineExecution):
            raise TypeError("pipeline must be PipelineExecution")

        identity_fields = (
            ("pipeline_id", pipeline.pipeline_id),
            ("name", pipeline.name),
        )
        for name, value in identity_fields:
            if not isinstance(value, str):
                raise TypeError(f"{name} must be str")
            if not value.strip():
                raise ValueError(f"{name} must not be blank")

        if not isinstance(pipeline.committees, list):
            raise TypeError(
                "committees must be list[CommitteeExecution]"
            )
        if not all(
            isinstance(committee, CommitteeExecution)
            for committee in pipeline.committees
        ):
            raise TypeError(
                "committees must contain only CommitteeExecution"
            )
