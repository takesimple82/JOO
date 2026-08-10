from __future__ import annotations

from AIAdapter.models import AIResponse
from PipelineRuntime.models import PipelineExecutionResult
from ResearchDomain.models import ResearchFinding
from ResearchDomain.validation import validate_research_finding

from InvestmentResearchOrchestrator.models.assignment import (
    CommitteeAssignmentPlan,
)
from InvestmentResearchOrchestrator.models.collection import (
    CollectedEvidence,
    CollectionBinding,
    CollectionFailureMarker,
)
from InvestmentResearchOrchestrator.models.execution import (
    ExecutionRecord,
)
from InvestmentResearchOrchestrator.validation.assignment import (
    validate_committee_assignment_plan,
)
from InvestmentResearchOrchestrator.validation.collection import (
    validate_collected_evidence,
    validate_collection_binding,
)
from InvestmentResearchOrchestrator.validation.execution import (
    validate_execution_record,
)


class EvidenceCollector:
    """Collect findings from actual results; never invent content."""

    def collect(
        self,
        *,
        execution: ExecutionRecord,
        assignment: CommitteeAssignmentPlan,
        binding: CollectionBinding | None,
        subject_id: str,
    ) -> CollectedEvidence:
        validate_execution_record(execution)
        validate_committee_assignment_plan(assignment)
        if binding is not None:
            validate_collection_binding(binding)
        if type(subject_id) is not str or subject_id.strip() == "":
            raise ValueError("subject_id must be nonblank str")

        result = execution.result
        if type(result) is not PipelineExecutionResult:
            raise TypeError(
                "result must be PipelineExecutionResult"
            )

        findings: list[ResearchFinding] = []
        failure_markers: list[CollectionFailureMarker] = []
        completed: list[str] = []
        failed: list[str] = []
        present_committees = {
            committee_result.committee_id
            for committee_result in result.committee_results
        }

        for committee_id in assignment.required_committees:
            if committee_id not in present_committees:
                failure_markers.append(
                    CollectionFailureMarker(
                        research_id=execution.research_id,
                        committee_id=committee_id,
                        reason="missing_required_committee",
                    )
                )
                continue

            committee_result = next(
                item
                for item in result.committee_results
                if item.committee_id == committee_id
            )
            if not committee_result.responses:
                failure_markers.append(
                    CollectionFailureMarker(
                        research_id=execution.research_id,
                        committee_id=committee_id,
                        reason="missing_committee_response",
                    )
                )
                continue

            response = committee_result.responses[0]
            if type(response) is not AIResponse:
                failure_markers.append(
                    CollectionFailureMarker(
                        research_id=execution.research_id,
                        committee_id=committee_id,
                        reason="invalid_response_type",
                    )
                )
                failed.append(committee_id)
                continue

            if response.status != "completed":
                failure_markers.append(
                    CollectionFailureMarker(
                        research_id=execution.research_id,
                        committee_id=committee_id,
                        reason=f"response_status_{response.status}",
                    )
                )
                failed.append(committee_id)
                continue

            if binding is None:
                failure_markers.append(
                    CollectionFailureMarker(
                        research_id=execution.research_id,
                        committee_id=committee_id,
                        reason="missing_collection_binding",
                    )
                )
                continue

            if (
                type(response.content) is not str
                or response.content.strip() == ""
            ):
                failure_markers.append(
                    CollectionFailureMarker(
                        research_id=execution.research_id,
                        committee_id=committee_id,
                        reason="blank_response_content",
                    )
                )
                failed.append(committee_id)
                continue

            finding_id = (
                f"{execution.research_id}:{committee_id}:0"
            )
            finding = ResearchFinding(
                finding_id=finding_id,
                research_id=execution.research_id,
                committee_id=committee_id,
                category=binding.category,
                statement=response.content,
                source=response.provider,
                event_date=binding.event_date,
                publication_date=binding.publication_date,
                verification_status=binding.verification_status,
            )
            try:
                validate_research_finding(finding)
            except (TypeError, ValueError) as exc:
                failure_markers.append(
                    CollectionFailureMarker(
                        research_id=execution.research_id,
                        committee_id=committee_id,
                        reason=f"finding_validation_failed:{exc}",
                    )
                )
                failed.append(committee_id)
                continue
            findings.append(finding)
            completed.append(committee_id)

        missing = tuple(
            committee_id
            for committee_id in assignment.required_committees
            if committee_id not in completed
            and committee_id not in failed
        )

        # Completeness is recorded by coordinator via router update;
        # collector returns findings/markers only.
        _ = missing

        evidence = CollectedEvidence(
            research_id=execution.research_id,
            findings=tuple(findings),
            failure_markers=tuple(failure_markers),
            report=None,
        )
        validate_collected_evidence(evidence)
        return evidence
