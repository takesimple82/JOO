from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from AIAdapter.models import AIResponse
from Committee.models import CommitteeExecutionResult
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
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
from InvestmentResearchOrchestrator.contradiction_engine import (
    ContradictionEngine,
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
from InvestmentResearchOrchestrator.memory_comparison import (
    MemoryComparison,
)
from InvestmentResearchOrchestrator.models.assignment import (
    StaticRoutingTable,
)
from InvestmentResearchOrchestrator.models.collection import (
    CollectionBinding,
)
from InvestmentResearchOrchestrator.models.enums import (
    EscalationReasonCode,
    EvidencePayloadKind,
    IRORunPhase,
    IRORunStatus,
)
from InvestmentResearchOrchestrator.models.prompt import (
    PromptTemplate,
)
from InvestmentResearchOrchestrator.models.run import IRORun
from InvestmentResearchOrchestrator.planner import ResearchPlanner
from InvestmentResearchOrchestrator.prompt_planner import (
    PromptFreeze,
)
from InvestmentResearchOrchestrator.re_research import (
    make_re_research_budget,
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
    def __init__(self):
        self.pipelines = []

    def run(self, pipeline):
        self.pipelines.append(pipeline)
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
                        content=(
                            f"content-for-"
                            f"{committee.committee_id}"
                        ),
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


def _binding():
    return CollectionBinding(
        category="market",
        event_date="2026-01-01",
        publication_date="2026-01-02",
        verification_status="unverified",
    )


def _template():
    return PromptTemplate(
        prompt_id="tpl-1",
        prompt_version="1.0",
        template_bytes=b"Research {subject_id}",
    )


class M2CoordinatorTests(unittest.TestCase):
    def _make_coordinator(
        self,
        tmp: str,
        *,
        max_attempts: int,
        committees: tuple[str, ...] = ("committee-a",),
        runtime: RecordingPipelineRuntime | None = None,
    ) -> tuple[RunCoordinator, RecordingPipelineRuntime]:
        table = StaticRoutingTable(
            routes=(
                ("HOLDING_STRUCTURAL", committees),
                ("WATCHLIST_STRUCTURAL", committees),
            )
        )
        runtime = runtime or RecordingPipelineRuntime()
        coordinator = RunCoordinator(
            scanner=PortfolioScanner(),
            planner=ResearchPlanner(),
            committee_router=StaticCommitteeRouter(table),
            prompt_freeze=PromptFreeze(),
            execution_adapter=M22Adapter(
                ResearchOrchestrator(runtime)
            ),
            evidence_collector=EvidenceCollector(),
            evidence_store=EvidenceStore(tmp),
            memory_comparison=MemoryComparison(),
            contradiction_engine=ContradictionEngine(),
            re_research_budget=make_re_research_budget(
                max_attempts=max_attempts
            ),
        )
        return coordinator, runtime

    def _run_kwargs(self, committees):
        template = _template()
        return {
            "run": make_run(),
            "current_snapshot": make_snapshot(
                snapshot_id="snap-current",
                quantity=Decimal("5"),
            ),
            "prior_baseline": make_snapshot(
                snapshot_id="snap-prior",
                quantity=Decimal("1"),
            ),
            "templates_by_committee": {
                committee_id: template for committee_id in committees
            },
            "bindings_by_committee": {
                committee_id: {"subject_id": "held-a"}
                for committee_id in committees
            },
            "provider_by_committee": {
                committee_id: "claude" for committee_id in committees
            },
            "collection_binding": _binding(),
        }

    def test_empty_scan_short_circuit_skips_contradiction(self):
        with tempfile.TemporaryDirectory() as tmp:
            coordinator, runtime = self._make_coordinator(
                tmp,
                max_attempts=2,
            )
            result = coordinator.run(
                run=make_run(),
                current_snapshot=make_snapshot(
                    snapshot_id="snap-current",
                    quantity=Decimal("3"),
                ),
                prior_baseline=make_snapshot(
                    snapshot_id="snap-prior",
                    quantity=Decimal("3"),
                ),
                templates_by_committee={},
                bindings_by_committee={},
                provider_by_committee={},
                collection_binding=None,
            )
            self.assertEqual(
                result.run.phase,
                IRORunPhase.SHORT_CIRCUITED_NO_MATERIAL_DELTA,
            )
            self.assertIsNone(result.memory)
            self.assertIsNone(result.contradiction)
            self.assertEqual(runtime.pipelines, [])
            store = EvidenceStore(tmp)
            self.assertEqual(store.list_for_run("run-001"), ())

    def test_initial_wave_does_not_consume_budget(self):
        committees = ("committee-a",)
        with tempfile.TemporaryDirectory() as tmp:
            coordinator, _ = self._make_coordinator(
                tmp,
                max_attempts=2,
                committees=committees,
            )
            result = coordinator.run(**self._run_kwargs(committees))
            self.assertIsNone(result.error)
            self.assertEqual(result.run.phase, IRORunPhase.COMPLETED)
            self.assertEqual(result.re_research_attempt, 0)
            self.assertIsNotNone(result.budget)
            self.assertEqual(result.budget.remaining, 2)
            self.assertEqual(result.budget.max_attempts, 2)

    def test_budget_exhaustion_escalates(self):
        committees = ("committee-a", "committee-b")
        with tempfile.TemporaryDirectory() as tmp:
            coordinator, runtime = self._make_coordinator(
                tmp,
                max_attempts=1,
                committees=committees,
            )
            result = coordinator.run(**self._run_kwargs(committees))
            self.assertIsNone(result.error)
            self.assertEqual(
                result.run.phase,
                IRORunPhase.ESCALATED_HUMAN_REVIEW,
            )
            self.assertEqual(
                result.run.status,
                IRORunStatus.ESCALATED_HUMAN_REVIEW,
            )
            self.assertIsNotNone(result.escalation)
            self.assertEqual(
                result.escalation.reason_code,
                EscalationReasonCode.RE_RESEARCH_BUDGET_EXHAUSTED,
            )
            self.assertEqual(result.budget.remaining, 0)
            self.assertEqual(result.re_research_attempt, 1)
            self.assertEqual(len(runtime.pipelines), 2)

    def test_non_progress_escalates_without_burning_budget(self):
        committees = ("committee-a", "committee-b")
        with tempfile.TemporaryDirectory() as tmp:
            coordinator, runtime = self._make_coordinator(
                tmp,
                max_attempts=5,
                committees=committees,
            )
            result = coordinator.run(**self._run_kwargs(committees))
            self.assertIsNone(result.error)
            self.assertEqual(
                result.run.phase,
                IRORunPhase.ESCALATED_HUMAN_REVIEW,
            )
            self.assertEqual(
                result.escalation.reason_code,
                EscalationReasonCode.NON_PROGRESS,
            )
            self.assertEqual(result.budget.remaining, 4)
            self.assertEqual(result.re_research_attempt, 1)
            self.assertEqual(len(runtime.pipelines), 2)

    def test_empty_re_research_plan_escalates_unplanable(self):
        committees = ("committee-a",)
        with tempfile.TemporaryDirectory() as tmp:
            coordinator, runtime = self._make_coordinator(
                tmp,
                max_attempts=1,
                committees=committees,
            )
            kwargs = self._run_kwargs(committees)
            kwargs["numeric_pairs"] = (
                (
                    ExactObservedNumericProposition(
                        "proposition-001",
                        "finding-001",
                        "other-subject",
                        "predicate-001",
                        Decimal("100"),
                        "USD",
                        "context-001",
                    ),
                    ExactObservedNumericProposition(
                        "proposition-002",
                        "finding-002",
                        "other-subject",
                        "predicate-001",
                        Decimal("200"),
                        "USD",
                        "context-001",
                    ),
                ),
            )
            result = coordinator.run(**kwargs)
            self.assertIsNone(result.error)
            self.assertEqual(
                result.run.phase,
                IRORunPhase.ESCALATED_HUMAN_REVIEW,
            )
            self.assertEqual(
                result.escalation.reason_code,
                EscalationReasonCode.UNPLANABLE_REQUESTS,
            )
            self.assertEqual(len(runtime.pipelines), 1)
            self.assertEqual(result.re_research_attempt, 1)

    def test_re_research_freezes_new_attempt_and_calls_m22_once(self):
        committees = ("committee-a", "committee-b")
        with tempfile.TemporaryDirectory() as tmp:
            coordinator, runtime = self._make_coordinator(
                tmp,
                max_attempts=1,
                committees=committees,
            )
            result = coordinator.run(**self._run_kwargs(committees))
            self.assertIsNone(result.error)
            attempts = {
                artifact.attempt_index
                for artifact in result.freeze_artifacts
            }
            self.assertEqual(attempts, {0, 1})
            self.assertTrue(
                any(
                    artifact.research_id.startswith(
                        "run-001:attempt:1:unit:"
                    )
                    for artifact in result.freeze_artifacts
                )
            )
            self.assertEqual(len(runtime.pipelines), 2)

    def test_append_only_audit_kinds(self):
        committees = ("committee-a", "committee-b")
        with tempfile.TemporaryDirectory() as tmp:
            coordinator, _ = self._make_coordinator(
                tmp,
                max_attempts=1,
                committees=committees,
            )
            result = coordinator.run(**self._run_kwargs(committees))
            self.assertIsNone(result.error)
            store = EvidenceStore(tmp)
            records = store.list_for_run("run-001")
            kinds = [record.payload_kind for record in records]
            self.assertIn(EvidencePayloadKind.FINDING, kinds)
            self.assertIn(EvidencePayloadKind.MEMORY_DELTA_SET, kinds)
            self.assertIn(
                EvidencePayloadKind.CONTRADICTION_EVALUATION,
                kinds,
            )
            self.assertIn(
                EvidencePayloadKind.RE_RESEARCH_ADMISSION,
                kinds,
            )
            self.assertIn(EvidencePayloadKind.ESCALATION, kinds)
            path = Path(tmp) / "run-001.jsonl"
            before = path.read_text(encoding="utf-8")
            lines = before.strip().split("\n")
            self.assertEqual(len(lines), len(records))
            first_line = lines[0]
            after = path.read_text(encoding="utf-8")
            self.assertEqual(after, before)
            self.assertEqual(
                after.strip().split("\n")[0],
                first_line,
            )

    def test_no_infinite_loop_even_with_large_budget(self):
        committees = ("committee-a", "committee-b")
        with tempfile.TemporaryDirectory() as tmp:
            coordinator, runtime = self._make_coordinator(
                tmp,
                max_attempts=8,
                committees=committees,
            )
            result = coordinator.run(**self._run_kwargs(committees))
            self.assertIsNone(result.error)
            self.assertEqual(
                result.run.status,
                IRORunStatus.ESCALATED_HUMAN_REVIEW,
            )
            self.assertLessEqual(len(runtime.pipelines), 2)
            self.assertGreater(result.budget.remaining, 0)

    def test_prompt_attempt_index_lift(self):
        freeze = PromptFreeze()
        artifact = freeze.freeze(
            research_id="r1",
            committee_id="c1",
            template=_template(),
            bindings={"subject_id": "held-a"},
            attempt_index=2,
        )
        self.assertEqual(artifact.attempt_index, 2)
        freeze.verify_hash(artifact)
        with self.assertRaisesRegex(ValueError, "attempt_index"):
            freeze.freeze(
                research_id="r1",
                committee_id="c1",
                template=_template(),
                bindings={"subject_id": "held-a"},
                attempt_index=-1,
            )


if __name__ == "__main__":
    unittest.main()
