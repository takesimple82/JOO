from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone

from PortfolioSnapshot.models import ExplicitPortfolioSnapshot

from InvestmentResearchOrchestrator.committee_manager import (
    StaticCommitteeRouter,
)
from InvestmentResearchOrchestrator.evidence_collector import (
    EvidenceCollector,
)
from InvestmentResearchOrchestrator.evidence_store import (
    EvidenceStore,
    utc_now,
)
from InvestmentResearchOrchestrator.execution_adapter import (
    M22Adapter,
)
from InvestmentResearchOrchestrator.memory_comparison_stub import (
    MemoryComparisonStub,
)
from InvestmentResearchOrchestrator.models.collection import (
    CollectionBinding,
)
from InvestmentResearchOrchestrator.models.enums import (
    EvidencePayloadKind,
    IRORunPhase,
    IRORunStatus,
)
from InvestmentResearchOrchestrator.models.memory import (
    MemoryDeltaSet,
)
from InvestmentResearchOrchestrator.models.plan import ResearchPlan
from InvestmentResearchOrchestrator.models.prompt import (
    PromptFreezeArtifact,
    PromptTemplate,
)
from InvestmentResearchOrchestrator.models.run import IRORun
from InvestmentResearchOrchestrator.models.scan import ScanDeltaSet
from InvestmentResearchOrchestrator.models.store import (
    EvidenceStoreRecord,
)
from InvestmentResearchOrchestrator.planner import ResearchPlanner
from InvestmentResearchOrchestrator.prompt_planner import (
    PromptFreeze,
)
from InvestmentResearchOrchestrator.scanner import PortfolioScanner
from InvestmentResearchOrchestrator.validation.run import (
    validate_iro_run,
)


@dataclass(frozen=True)
class IRORunResult:
    run: IRORun
    scan: ScanDeltaSet | None
    plan: ResearchPlan | None
    freeze_artifacts: tuple[PromptFreezeArtifact, ...]
    memory: MemoryDeltaSet | None
    error: str | None


class RunCoordinator:
    """Sequential M1 lifecycle wiring + empty-scan short-circuit."""

    def __init__(
        self,
        *,
        scanner: PortfolioScanner,
        planner: ResearchPlanner,
        committee_router: StaticCommitteeRouter,
        prompt_freeze: PromptFreeze,
        execution_adapter: M22Adapter,
        evidence_collector: EvidenceCollector,
        evidence_store: EvidenceStore,
        memory_stub: MemoryComparisonStub,
    ) -> None:
        if type(scanner) is not PortfolioScanner:
            raise TypeError("scanner must be PortfolioScanner")
        if type(planner) is not ResearchPlanner:
            raise TypeError("planner must be ResearchPlanner")
        if type(committee_router) is not StaticCommitteeRouter:
            raise TypeError(
                "committee_router must be StaticCommitteeRouter"
            )
        if type(prompt_freeze) is not PromptFreeze:
            raise TypeError("prompt_freeze must be PromptFreeze")
        if type(execution_adapter) is not M22Adapter:
            raise TypeError(
                "execution_adapter must be M22Adapter"
            )
        if type(evidence_collector) is not EvidenceCollector:
            raise TypeError(
                "evidence_collector must be EvidenceCollector"
            )
        if type(evidence_store) is not EvidenceStore:
            raise TypeError(
                "evidence_store must be EvidenceStore"
            )
        if type(memory_stub) is not MemoryComparisonStub:
            raise TypeError(
                "memory_stub must be MemoryComparisonStub"
            )
        self._scanner = scanner
        self._planner = planner
        self._router = committee_router
        self._prompt_freeze = prompt_freeze
        self._adapter = execution_adapter
        self._collector = evidence_collector
        self._store = evidence_store
        self._memory = memory_stub

    def run(
        self,
        *,
        run: IRORun,
        current_snapshot: ExplicitPortfolioSnapshot,
        prior_baseline: ExplicitPortfolioSnapshot | None,
        templates_by_committee: dict[str, PromptTemplate],
        bindings_by_committee: dict[str, dict[str, str]],
        provider_by_committee: dict[str, str],
        collection_binding: CollectionBinding | None,
        prior_store: EvidenceStore | None = None,
        prior_run_id: str | None = None,
    ) -> IRORunResult:
        validate_iro_run(run)
        if run.phase is not IRORunPhase.INITIALIZED:
            raise ValueError(
                "run phase must be INITIALIZED to start"
            )
        if run.status is not IRORunStatus.IN_PROGRESS:
            raise ValueError(
                "run status must be IN_PROGRESS to start"
            )

        freeze_artifacts: list[PromptFreezeArtifact] = []
        scan: ScanDeltaSet | None = None
        plan: ResearchPlan | None = None
        memory: MemoryDeltaSet | None = None

        try:
            scan = self._scanner.scan(
                run_id=run.run_id,
                current=current_snapshot,
                prior_baseline=prior_baseline,
            )
            run = self._advance(
                run,
                phase=IRORunPhase.SCANNED,
            )

            if len(scan.deltas) == 0:
                run = self._terminalize(
                    run,
                    phase=(
                        IRORunPhase.SHORT_CIRCUITED_NO_MATERIAL_DELTA
                    ),
                    status=(
                        IRORunStatus.SHORT_CIRCUITED_NO_MATERIAL_DELTA
                    ),
                )
                return IRORunResult(
                    run=run,
                    scan=scan,
                    plan=None,
                    freeze_artifacts=(),
                    memory=None,
                    error=None,
                )

            plan = self._planner.plan(scan)
            run = self._advance(run, phase=IRORunPhase.PLANNED)

            assignments = []
            for unit in plan.units:
                assignment = self._router.route(unit)
                assignments.append(assignment)
            run = self._advance(run, phase=IRORunPhase.ROUTED)

            unit_artifacts: list[
                tuple[object, object, tuple[PromptFreezeArtifact, ...]]
            ] = []
            for unit, assignment in zip(plan.units, assignments):
                artifacts: list[PromptFreezeArtifact] = []
                for committee_id in assignment.required_committees:
                    if committee_id not in templates_by_committee:
                        raise ValueError(
                            f"missing template for committee "
                            f"{committee_id}"
                        )
                    template = templates_by_committee[committee_id]
                    bindings = bindings_by_committee.get(
                        committee_id,
                        {},
                    )
                    # Inject structural subject binding defaults
                    # only when keys are already expected by template
                    # and present in caller bindings; no invention.
                    artifact = self._prompt_freeze.freeze(
                        research_id=unit.research_id,
                        committee_id=committee_id,
                        template=template,
                        bindings=bindings,
                    )
                    self._prompt_freeze.verify_hash(artifact)
                    artifacts.append(artifact)
                    freeze_artifacts.append(artifact)
                    self._store.append(
                        EvidenceStoreRecord(
                            run_id=run.run_id,
                            research_id=unit.research_id,
                            committee_id=committee_id,
                            provider_id=None,
                            prompt_id=artifact.prompt_id,
                            prompt_hash=artifact.prompt_hash,
                            source_reference=None,
                            collected_at=None,
                            stored_at=utc_now(),
                            payload_kind=(
                                EvidencePayloadKind.PROMPT_FREEZE
                            ),
                            payload=json.dumps(
                                {
                                    "prompt_hash": (
                                        artifact.prompt_hash
                                    ),
                                    "attempt_index": (
                                        artifact.attempt_index
                                    ),
                                },
                                separators=(",", ":"),
                            ),
                        )
                    )
                unit_artifacts.append(
                    (unit, assignment, tuple(artifacts))
                )
            run = self._advance(
                run,
                phase=IRORunPhase.PROMPTS_FROZEN,
            )

            executions = []
            for unit, assignment, artifacts in unit_artifacts:
                record = self._adapter.execute(
                    unit=unit,
                    assignment=assignment,
                    freeze_artifacts=artifacts,
                    provider_by_committee=provider_by_committee,
                )
                executions.append((unit, assignment, record))
                self._store.append(
                    EvidenceStoreRecord(
                        run_id=run.run_id,
                        research_id=unit.research_id,
                        committee_id=None,
                        provider_id=None,
                        prompt_id=None,
                        prompt_hash=None,
                        source_reference=None,
                        collected_at=None,
                        stored_at=utc_now(),
                        payload_kind=(
                            EvidencePayloadKind.EXECUTION_RECORD
                        ),
                        payload=json.dumps(
                            {
                                "pipeline_id": (
                                    record.result.pipeline_id
                                ),
                                "committee_count": len(
                                    record.result.committee_results
                                ),
                            },
                            separators=(",", ":"),
                        ),
                    )
                )
            run = self._advance(run, phase=IRORunPhase.EXECUTED)

            subject_keys: list[str] = []
            for unit, assignment, record in executions:
                collected = self._collector.collect(
                    execution=record,
                    assignment=assignment,
                    binding=collection_binding,
                    subject_id=unit.subject_id,
                )
                subject_keys.append(unit.subject_id)

                completed = tuple(
                    finding.committee_id
                    for finding in collected.findings
                )
                failed = tuple(
                    marker.committee_id
                    for marker in collected.failure_markers
                    if marker.reason.startswith("response_status_")
                    or marker.reason
                    in {
                        "invalid_response_type",
                        "blank_response_content",
                    }
                    or marker.reason.startswith(
                        "finding_validation_failed:"
                    )
                )
                missing = tuple(
                    committee_id
                    for committee_id in assignment.required_committees
                    if committee_id not in completed
                    and committee_id not in failed
                )
                completeness = self._router.update_completeness(
                    assignment,
                    completed=completed,
                    failed=failed,
                    missing=missing,
                )
                self._store.append(
                    EvidenceStoreRecord(
                        run_id=run.run_id,
                        research_id=unit.research_id,
                        committee_id=None,
                        provider_id=None,
                        prompt_id=None,
                        prompt_hash=None,
                        source_reference=None,
                        collected_at=utc_now(),
                        stored_at=utc_now(),
                        payload_kind=(
                            EvidencePayloadKind.COMPLETENESS
                        ),
                        payload=json.dumps(
                            {
                                "required": list(
                                    completeness.completeness.required
                                ),
                                "completed": list(
                                    completeness.completeness.completed
                                ),
                                "failed": list(
                                    completeness.completeness.failed
                                ),
                                "missing": list(
                                    completeness.completeness.missing
                                ),
                            },
                            separators=(",", ":"),
                        ),
                    )
                )
                for finding in collected.findings:
                    self._store.append(
                        EvidenceStoreRecord(
                            run_id=run.run_id,
                            research_id=finding.research_id,
                            committee_id=finding.committee_id,
                            provider_id=finding.source,
                            prompt_id=None,
                            prompt_hash=None,
                            source_reference=finding.source,
                            collected_at=utc_now(),
                            stored_at=utc_now(),
                            payload_kind=(
                                EvidencePayloadKind.FINDING
                            ),
                            payload=json.dumps(
                                {
                                    "subject_key": unit.subject_id,
                                    "finding_id": finding.finding_id,
                                    "statement": finding.statement,
                                    "category": finding.category,
                                },
                                separators=(",", ":"),
                            ),
                        )
                    )
                for marker in collected.failure_markers:
                    self._store.append(
                        EvidenceStoreRecord(
                            run_id=run.run_id,
                            research_id=marker.research_id,
                            committee_id=marker.committee_id,
                            provider_id=None,
                            prompt_id=None,
                            prompt_hash=None,
                            source_reference=None,
                            collected_at=utc_now(),
                            stored_at=utc_now(),
                            payload_kind=(
                                EvidencePayloadKind.COLLECTION_FAILURE
                            ),
                            payload=json.dumps(
                                {"reason": marker.reason},
                                separators=(",", ":"),
                            ),
                        )
                    )
            run = self._advance(run, phase=IRORunPhase.COLLECTED)
            run = self._advance(run, phase=IRORunPhase.STORED)

            memory = self._memory.compare(
                run_id=run.run_id,
                current_store=self._store,
                prior_store=prior_store,
                prior_run_id=prior_run_id,
                subject_keys=tuple(subject_keys),
            )
            run = self._advance(
                run,
                phase=IRORunPhase.MEMORY_COMPARED,
            )
            run = self._terminalize(
                run,
                phase=IRORunPhase.COMPLETED,
                status=IRORunStatus.COMPLETED,
            )
            return IRORunResult(
                run=run,
                scan=scan,
                plan=plan,
                freeze_artifacts=tuple(freeze_artifacts),
                memory=memory,
                error=None,
            )
        except Exception as exc:
            failed_run = self._terminalize(
                run,
                phase=IRORunPhase.FAILED,
                status=IRORunStatus.FAILED,
            )
            return IRORunResult(
                run=failed_run,
                scan=scan,
                plan=plan,
                freeze_artifacts=tuple(freeze_artifacts),
                memory=memory,
                error=f"{type(exc).__name__}: {exc}",
            )

    @staticmethod
    def _advance(run: IRORun, *, phase: IRORunPhase) -> IRORun:
        updated = replace(
            run,
            phase=phase,
            status=IRORunStatus.IN_PROGRESS,
            updated_at=datetime.now(timezone.utc),
        )
        validate_iro_run(updated)
        return updated

    @staticmethod
    def _terminalize(
        run: IRORun,
        *,
        phase: IRORunPhase,
        status: IRORunStatus,
    ) -> IRORun:
        updated = replace(
            run,
            phase=phase,
            status=status,
            updated_at=datetime.now(timezone.utc),
        )
        validate_iro_run(updated)
        return updated
