from dataclasses import dataclass

from Committee.models import (
    CommitteeExecution,
    CommitteeExecutionResult,
)


@dataclass
class PipelineExecution:
    pipeline_id: str
    name: str
    committees: list[CommitteeExecution]


@dataclass
class PipelineExecutionResult:
    pipeline_id: str
    committee_results: list[CommitteeExecutionResult]
