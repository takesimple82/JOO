from __future__ import annotations

from PipelineRuntime.models import PipelineExecutionResult

from InvestmentResearchOrchestrator.models.execution import (
    ExecutionRecord,
)
from InvestmentResearchOrchestrator.validation.common import (
    require_nonblank_string,
)


def validate_execution_record(record: ExecutionRecord) -> None:
    if type(record) is not ExecutionRecord:
        raise TypeError("record must be ExecutionRecord")
    require_nonblank_string(
        "research_id",
        record.research_id,
    )
    if type(record.result) is not PipelineExecutionResult:
        raise TypeError(
            "result must be PipelineExecutionResult"
        )
