from __future__ import annotations

from AIAdapter.models import AIRequest
from Committee.models import CommitteeExecution
from PipelineRuntime.models import (
    PipelineExecution,
    PipelineExecutionResult,
)
from ResearchDomain.models import ResearchTask
from ResearchDomain.validation import validate_research_task
from ResearchOrchestrator.orchestrator import (
    ResearchOrchestrator,
)

from InvestmentResearchOrchestrator.models.assignment import (
    CommitteeAssignmentPlan,
)
from InvestmentResearchOrchestrator.models.execution import (
    ExecutionRecord,
)
from InvestmentResearchOrchestrator.models.plan import (
    PlannedUnit,
)
from InvestmentResearchOrchestrator.models.prompt import (
    PromptFreezeArtifact,
)
from InvestmentResearchOrchestrator.validation.assignment import (
    validate_committee_assignment_plan,
)
from InvestmentResearchOrchestrator.validation.execution import (
    validate_execution_record,
)
from InvestmentResearchOrchestrator.validation.plan import (
    validate_planned_unit,
)
from InvestmentResearchOrchestrator.validation.prompt import (
    validate_prompt_freeze_artifact,
)


class M22Adapter:
    """Assemble ResearchDomain.ResearchTask and invoke M22 once."""

    def __init__(
        self,
        research_orchestrator: ResearchOrchestrator,
    ) -> None:
        if not isinstance(
            research_orchestrator,
            ResearchOrchestrator,
        ):
            raise TypeError(
                "research_orchestrator must be "
                "ResearchOrchestrator"
            )
        self._orchestrator = research_orchestrator

    def execute(
        self,
        *,
        unit: PlannedUnit,
        assignment: CommitteeAssignmentPlan,
        freeze_artifacts: tuple[PromptFreezeArtifact, ...],
        provider_by_committee: dict[str, str],
    ) -> ExecutionRecord:
        validate_planned_unit(unit)
        validate_committee_assignment_plan(assignment)
        if type(freeze_artifacts) is not tuple:
            raise TypeError("freeze_artifacts must be tuple")
        if len(freeze_artifacts) == 0:
            raise ValueError(
                "freeze_artifacts must not be empty"
            )
        for artifact in freeze_artifacts:
            validate_prompt_freeze_artifact(artifact)
            if artifact.research_id != unit.research_id:
                raise ValueError(
                    "freeze artifact research_id mismatch"
                )
        if type(provider_by_committee) is not dict:
            raise TypeError(
                "provider_by_committee must be dict"
            )

        artifact_by_committee = {
            artifact.committee_id: artifact
            for artifact in freeze_artifacts
        }
        committees: list[CommitteeExecution] = []
        for committee_id in assignment.required_committees:
            if committee_id not in artifact_by_committee:
                raise ValueError(
                    f"missing freeze artifact for committee "
                    f"{committee_id}"
                )
            if committee_id not in provider_by_committee:
                raise ValueError(
                    f"missing provider for committee "
                    f"{committee_id}"
                )
            provider = provider_by_committee[committee_id]
            if type(provider) is not str or provider.strip() == "":
                raise ValueError(
                    f"provider for {committee_id} must be "
                    "nonblank str"
                )
            artifact = artifact_by_committee[committee_id]
            try:
                prompt_text = artifact.frozen_prompt_bytes.decode(
                    "utf-8"
                )
            except UnicodeDecodeError as exc:
                raise ValueError(
                    "frozen_prompt_bytes must be valid UTF-8"
                ) from exc
            request = AIRequest(
                provider=provider,
                prompt=prompt_text,
                prompt_id=artifact.prompt_id,
                prompt_version=artifact.prompt_version,
                task_id=unit.research_id,
            )
            committees.append(
                CommitteeExecution(
                    committee_id=committee_id,
                    name=committee_id,
                    requests=[request],
                )
            )

        pipeline = PipelineExecution(
            pipeline_id=f"pipeline:{unit.research_id}",
            name=f"IRO pipeline for {unit.research_id}",
            committees=committees,
        )
        task = ResearchTask(
            research_id=unit.research_id,
            title=unit.title,
            objective=unit.objective,
            priority=unit.priority,
            pipeline=pipeline,
        )
        validate_research_task(task)
        result = self._orchestrator.run(task)
        if type(result) is not PipelineExecutionResult:
            raise TypeError(
                "M22 must return PipelineExecutionResult"
            )
        record = ExecutionRecord(
            research_id=unit.research_id,
            result=result,
        )
        validate_execution_record(record)
        return record
