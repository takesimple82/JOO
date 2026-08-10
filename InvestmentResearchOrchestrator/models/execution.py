from __future__ import annotations

from dataclasses import dataclass

from PipelineRuntime.models import PipelineExecutionResult


@dataclass(frozen=True)
class ExecutionRecord:
    research_id: str
    result: PipelineExecutionResult
