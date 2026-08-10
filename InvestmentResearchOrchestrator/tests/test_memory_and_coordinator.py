from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal

from AIAdapter.models import AIResponse
from Committee.models import CommitteeExecutionResult
from PipelineRuntime.models import PipelineExecutionResult
from PipelineRuntime.runtime import PipelineRuntime
from PortfolioHoldingObservation.models import (
    ExplicitPortfolioHoldingObservation,
)
from PortfolioHoldingSnapshot.models import (
    ExplicitPortfolioHoldingSnapshot,
)
from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioPosition.models import ExplicitPortfolioPosition
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioWatchlistEntry.models import (
    ExplicitPortfolioWatchlistEntry,
)
from ResearchOrchestrator.orchestrator import ResearchOrchestrator

from InvestmentResearchOrchestrator.committee_manager import (
    StaticCommitteeRouter,
)
from InvestmentResearchOrchestrator.evidence_collector import (
    EvidenceCollector,
)
from InvestmentResearchOrchestrator.evidence_store import (
    EvidenceStore,
)
from InvestmentResearchOrchestrator.execution_adapter import (
    M22Adapter,
)
from InvestmentResearchOrchestrator.memory_comparison_stub import (
    MemoryComparisonStub,
)
from InvestmentResearchOrchestrator.models.assignment import (
    StaticRoutingTable,
)
from InvestmentResearchOrchestrator.models.collection import (
    CollectionBinding,
)
from InvestmentResearchOrchestrator.models.enums import (
    EvidencePayloadKind,
    IRORunPhase,
    IRORunStatus,
    MemoryDeltaClass,
)
from InvestmentResearchOrchestrator.models.prompt import (
    PromptTemplate,
)
from InvestmentResearchOrchestrator.models.run import IRORun
from InvestmentResearchOrchestrator.models.store import (
    EvidenceStoreRecord,
)
from InvestmentResearchOrchestrator.planner import ResearchPlanner
from InvestmentResearchOrchestrator.prompt_planner import (
    PromptFreeze,
)
from InvestmentResearchOrchestrator.run_coordinator import (
    RunCoordinator,
)
from InvestmentResearchOrchestrator.scanner import PortfolioScanner


def make_context():
    return ExplicitPortfolioObservationContext(
        "context-001",
        "portfolio-001",
    )


def make_snapshot(
    *,
    snapshot_id,
    subject_id="held-a",
    quantity=Decimal("1"),
    watchlist_ids=(),
):
    context = make_context()
    observation = ExplicitPortfolioHoldingObservation(
        ExplicitPortfolioPosition(
            "position-001",
            ExplicitPortfolioMembership(
                context.portfolio_id,
                subject_id,
            ),
        ),
        context,
        quantity,
    )
    watchlist = tuple(
        ExplicitPortfolioWatchlistEntry(
            ExplicitPortfolioMembership(
                context.portfolio_id,
                watch_id,
            )
        )
        for watch_id in watchlist_ids
    )
    return ExplicitPortfolioSnapshot(
        snapshot_id,
        context,
        ExplicitPortfolioHoldingSnapshot(
            context,
            (observation,),
        ),
        watchlist,
    )


def make_run(**overrides):
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    values = {
        "run_id": "run-001",
        "portfolio_snapshot_id": "snap-current",
        "prior_baseline_id": "snap-prior",
        "phase": IRORunPhase.INITIALIZED,
        "status": IRORunStatus.IN_PROGRESS,
        "created_at": now,
        "updated_at": now,
    }
    values.update(overrides)
    return IRORun(**values)


class RecordingPipelineRuntime(PipelineRuntime):
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.pipelines = []

    def run(self, pipeline):
        self.pipelines.append(pipeline)
        if self.error is not None:
            raise self.error
        if self.result is not None:
            return self.result
        # Build success result matching assembled pipeline committees.
        committee_results = []
        for committee in pipeline.committees:
            responses = []
            for request in committee.requests:
                responses.append(
                    AIResponse(
                        provider=request.provider,
                        task_id=request.task_id,
                        prompt_id=request.prompt_id,
                        prompt_version=request.prompt_version,
                        content=f"content-for-{request.task_id}",
                        status="completed",
                        error="",
                    )
                )
            committee_results.append(
                CommitteeExecutionResult(
                    committee_id=committee.committee_id,
                    responses=responses,
                )
            )
        return PipelineExecutionResult(
            pipeline_id=pipeline.pipeline_id,
            committee_results=committee_results,
        )


class MemoryAndCoordinatorTests(unittest.TestCase):
    def test_memory_stub_no_prior(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            store.append(
                EvidenceStoreRecord(
                    run_id="run-001",
                    research_id="r1",
                    committee_id="c1",
                    provider_id="claude",
                    prompt_id=None,
                    prompt_hash=None,
                    source_reference="claude",
                    collected_at=datetime(
                        2026, 1, 1, tzinfo=timezone.utc
                    ),
                    stored_at=datetime(
                        2026, 1, 1, tzinfo=timezone.utc
                    ),
                    payload_kind=EvidencePayloadKind.FINDING,
                    payload=(
                        '{"subject_key":"held-a",'
                        '"statement":"hello"}'
                    ),
                )
            )
            deltas = MemoryComparisonStub().compare(
                run_id="run-001",
                current_store=store,
                prior_store=None,
                prior_run_id=None,
                subject_keys=("held-a",),
            )
            self.assertEqual(len(deltas.deltas), 1)
            self.assertEqual(
                deltas.deltas[0].delta_class,
                MemoryDeltaClass.NO_PRIOR,
            )
            self.assertFalse(deltas.deltas[0].prior_present)

    def test_memory_stub_statement_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            current = EvidenceStore(tmp + "/current")
            prior = EvidenceStore(tmp + "/prior")
            now = datetime(2026, 1, 1, tzinfo=timezone.utc)
            prior.append(
                EvidenceStoreRecord(
                    run_id="prior-run",
                    research_id="r1",
                    committee_id="c1",
                    provider_id="claude",
                    prompt_id=None,
                    prompt_hash=None,
                    source_reference="claude",
                    collected_at=now,
                    stored_at=now,
                    payload_kind=EvidencePayloadKind.FINDING,
                    payload=(
                        '{"subject_key":"held-a",'
                        '"statement":"old"}'
                    ),
                )
            )
            current.append(
                EvidenceStoreRecord(
                    run_id="run-001",
                    research_id="r1",
                    committee_id="c1",
                    provider_id="claude",
                    prompt_id=None,
                    prompt_hash=None,
                    source_reference="claude",
                    collected_at=now,
                    stored_at=now,
                    payload_kind=EvidencePayloadKind.FINDING,
                    payload=(
                        '{"subject_key":"held-a",'
                        '"statement":"new"}'
                    ),
                )
            )
            deltas = MemoryComparisonStub().compare(
                run_id="run-001",
                current_store=current,
                prior_store=prior,
                prior_run_id="prior-run",
                subject_keys=("held-a",),
            )
            self.assertEqual(
                deltas.deltas[0].delta_class,
                MemoryDeltaClass.STATEMENT_CHANGED,
            )

    def test_empty_scan_short_circuit(self):
        with tempfile.TemporaryDirectory() as tmp:
            context_current = make_snapshot(
                snapshot_id="snap-current",
                quantity=Decimal("3"),
            )
            context_prior = make_snapshot(
                snapshot_id="snap-prior",
                quantity=Decimal("3"),
            )
            coordinator = self._make_coordinator(tmp)
            result = coordinator.run(
                run=make_run(),
                current_snapshot=context_current,
                prior_baseline=context_prior,
                templates_by_committee={},
                bindings_by_committee={},
                provider_by_committee={},
                collection_binding=None,
            )
            self.assertEqual(
                result.run.phase,
                IRORunPhase.SHORT_CIRCUITED_NO_MATERIAL_DELTA,
            )
            self.assertEqual(
                result.run.status,
                IRORunStatus.SHORT_CIRCUITED_NO_MATERIAL_DELTA,
            )
            self.assertIsNotNone(result.scan)
            self.assertEqual(result.scan.deltas, ())
            self.assertIsNone(result.plan)
            self.assertIsNone(result.error)

    def test_full_path_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            current = make_snapshot(
                snapshot_id="snap-current",
                quantity=Decimal("5"),
                watchlist_ids=(),
            )
            prior = make_snapshot(
                snapshot_id="snap-prior",
                quantity=Decimal("1"),
                watchlist_ids=(),
            )
            coordinator = self._make_coordinator(tmp)
            template = PromptTemplate(
                prompt_id="tpl-1",
                prompt_version="1.0",
                template_bytes=b"Research {subject_id}",
            )
            result = coordinator.run(
                run=make_run(prior_baseline_id="snap-prior"),
                current_snapshot=current,
                prior_baseline=prior,
                templates_by_committee={
                    "committee-a": template,
                },
                bindings_by_committee={
                    "committee-a": {"subject_id": "held-a"},
                },
                provider_by_committee={
                    "committee-a": "claude",
                },
                collection_binding=CollectionBinding(
                    category="market",
                    event_date="2026-01-01",
                    publication_date="2026-01-02",
                    verification_status="unverified",
                ),
            )
            self.assertIsNone(result.error)
            self.assertEqual(
                result.run.phase,
                IRORunPhase.COMPLETED,
            )
            self.assertEqual(
                result.run.status,
                IRORunStatus.COMPLETED,
            )
            self.assertIsNotNone(result.plan)
            self.assertEqual(len(result.plan.units), 1)
            self.assertEqual(len(result.freeze_artifacts), 1)
            self.assertIsNotNone(result.memory)
            store = EvidenceStore(tmp)
            records = store.list_for_run("run-001")
            kinds = {record.payload_kind for record in records}
            self.assertIn(EvidencePayloadKind.PROMPT_FREEZE, kinds)
            self.assertIn(EvidencePayloadKind.FINDING, kinds)
            self.assertIn(EvidencePayloadKind.COMPLETENESS, kinds)

    def _make_coordinator(self, tmp: str) -> RunCoordinator:
        table = StaticRoutingTable(
            routes=(
                ("HOLDING_STRUCTURAL", ("committee-a",)),
                ("WATCHLIST_STRUCTURAL", ("committee-a",)),
            )
        )
        runtime = RecordingPipelineRuntime()
        return RunCoordinator(
            scanner=PortfolioScanner(),
            planner=ResearchPlanner(),
            committee_router=StaticCommitteeRouter(table),
            prompt_freeze=PromptFreeze(),
            execution_adapter=M22Adapter(
                ResearchOrchestrator(runtime)
            ),
            evidence_collector=EvidenceCollector(),
            evidence_store=EvidenceStore(tmp),
            memory_stub=MemoryComparisonStub(),
        )


if __name__ == "__main__":
    unittest.main()
