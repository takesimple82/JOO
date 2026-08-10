from __future__ import annotations

import hashlib
import unittest

from AIAdapter.models import AIResponse
from Committee.models import CommitteeExecutionResult
from PipelineRuntime.models import PipelineExecutionResult
from PipelineRuntime.runtime import PipelineRuntime
from ResearchOrchestrator.orchestrator import ResearchOrchestrator

from InvestmentResearchOrchestrator.committee_manager import (
    StaticCommitteeRouter,
)
from InvestmentResearchOrchestrator.evidence_collector import (
    EvidenceCollector,
)
from InvestmentResearchOrchestrator.execution_adapter import (
    M22Adapter,
)
from InvestmentResearchOrchestrator.models.assignment import (
    StaticRoutingTable,
)
from InvestmentResearchOrchestrator.models.collection import (
    CollectionBinding,
)
from InvestmentResearchOrchestrator.models.plan import PlannedUnit
from InvestmentResearchOrchestrator.models.prompt import (
    PromptTemplate,
)
from InvestmentResearchOrchestrator.prompt_planner import (
    PromptFreeze,
)


def make_unit(**overrides):
    values = {
        "research_id": "run:unit:0:held-a",
        "subject_id": "held-a",
        "task_type": "HOLDING_STRUCTURAL",
        "priority": "P0",
        "title": "Structural research for held-a",
        "objective": "Investigate held-a",
    }
    values.update(overrides)
    return PlannedUnit(**values)


class RecordingPipelineRuntime(PipelineRuntime):
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.pipelines = []

    def run(self, pipeline):
        self.pipelines.append(pipeline)
        if self.error is not None:
            raise self.error
        return self.result


class RouterPromptAdapterCollectorTests(unittest.TestCase):
    def test_completeness_block_structure(self):
        table = StaticRoutingTable(
            routes=(
                (
                    "HOLDING_STRUCTURAL",
                    ("committee-a", "committee-b"),
                ),
            )
        )
        router = StaticCommitteeRouter(table)
        plan = router.route(make_unit())
        self.assertEqual(
            plan.required_committees,
            ("committee-a", "committee-b"),
        )
        self.assertEqual(
            plan.completeness.required,
            ("committee-a", "committee-b"),
        )
        self.assertEqual(plan.completeness.completed, ())
        self.assertEqual(plan.completeness.failed, ())
        self.assertEqual(plan.completeness.missing, ())

        updated = router.update_completeness(
            plan,
            completed=("committee-a",),
            failed=(),
            missing=("committee-b",),
        )
        self.assertEqual(
            updated.completeness.completed,
            ("committee-a",),
        )
        self.assertEqual(
            updated.completeness.missing,
            ("committee-b",),
        )

    def test_unknown_task_type_fails_closed(self):
        table = StaticRoutingTable(
            routes=(("HOLDING_STRUCTURAL", ("committee-a",)),)
        )
        router = StaticCommitteeRouter(table)
        with self.assertRaisesRegex(ValueError, "unknown task_type"):
            router.route(
                make_unit(task_type="UNKNOWN_TYPE")
            )

    def test_prompt_freeze_hash_stability(self):
        freeze = PromptFreeze()
        template = PromptTemplate(
            prompt_id="tpl-1",
            prompt_version="1.0",
            template_bytes=b"Research {subject_id} carefully",
        )
        first = freeze.freeze(
            research_id="r1",
            committee_id="committee-a",
            template=template,
            bindings={"subject_id": "held-a"},
        )
        second = freeze.freeze(
            research_id="r1",
            committee_id="committee-a",
            template=template,
            bindings={"subject_id": "held-a"},
        )
        self.assertEqual(first.prompt_hash, second.prompt_hash)
        self.assertEqual(
            first.prompt_hash,
            hashlib.sha256(first.frozen_prompt_bytes).hexdigest(),
        )
        freeze.verify_hash(first)

    def test_prompt_hash_mismatch_fails_closed(self):
        freeze = PromptFreeze()
        template = PromptTemplate(
            prompt_id="tpl-1",
            prompt_version="1.0",
            template_bytes=b"Hello {name}",
        )
        artifact = freeze.freeze(
            research_id="r1",
            committee_id="c1",
            template=template,
            bindings={"name": "world"},
        )
        tampered = type(artifact)(
            research_id=artifact.research_id,
            committee_id=artifact.committee_id,
            prompt_id=artifact.prompt_id,
            prompt_version=artifact.prompt_version,
            frozen_prompt_bytes=artifact.frozen_prompt_bytes,
            prompt_hash="0" * 64,
            attempt_index=0,
        )
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            freeze.verify_hash(tampered)

    def test_missing_binding_fails_closed(self):
        freeze = PromptFreeze()
        template = PromptTemplate(
            prompt_id="tpl-1",
            prompt_version="1.0",
            template_bytes=b"Hello {name}",
        )
        with self.assertRaisesRegex(ValueError, "missing required binding"):
            freeze.freeze(
                research_id="r1",
                committee_id="c1",
                template=template,
                bindings={},
            )

    def test_adapter_invokes_m22_once_and_preserves_result(self):
        expected = PipelineExecutionResult(
            pipeline_id="pipeline:run:unit:0:held-a",
            committee_results=[
                CommitteeExecutionResult(
                    committee_id="committee-a",
                    responses=[
                        AIResponse(
                            provider="claude",
                            task_id="run:unit:0:held-a",
                            prompt_id="tpl-1",
                            prompt_version="1.0",
                            content="actual finding text",
                            status="completed",
                            error="",
                        )
                    ],
                )
            ],
        )
        runtime = RecordingPipelineRuntime(expected)
        orchestrator = ResearchOrchestrator(runtime)
        adapter = M22Adapter(orchestrator)
        freeze = PromptFreeze()
        artifact = freeze.freeze(
            research_id="run:unit:0:held-a",
            committee_id="committee-a",
            template=PromptTemplate(
                prompt_id="tpl-1",
                prompt_version="1.0",
                template_bytes=b"Research {subject_id}",
            ),
            bindings={"subject_id": "held-a"},
        )
        table = StaticRoutingTable(
            routes=(("HOLDING_STRUCTURAL", ("committee-a",)),)
        )
        assignment = StaticCommitteeRouter(table).route(make_unit())
        record = adapter.execute(
            unit=make_unit(),
            assignment=assignment,
            freeze_artifacts=(artifact,),
            provider_by_committee={"committee-a": "claude"},
        )
        self.assertEqual(len(runtime.pipelines), 1)
        self.assertIs(record.result, expected)
        request = runtime.pipelines[0].committees[0].requests[0]
        self.assertEqual(request.task_id, "run:unit:0:held-a")
        self.assertEqual(request.prompt, "Research held-a")

    def test_adapter_propagates_original_exception(self):
        original = RuntimeError("pipeline exploded")
        runtime = RecordingPipelineRuntime(error=original)
        adapter = M22Adapter(ResearchOrchestrator(runtime))
        freeze = PromptFreeze()
        artifact = freeze.freeze(
            research_id="run:unit:0:held-a",
            committee_id="committee-a",
            template=PromptTemplate(
                prompt_id="tpl-1",
                prompt_version="1.0",
                template_bytes=b"Research {subject_id}",
            ),
            bindings={"subject_id": "held-a"},
        )
        table = StaticRoutingTable(
            routes=(("HOLDING_STRUCTURAL", ("committee-a",)),)
        )
        assignment = StaticCommitteeRouter(table).route(make_unit())
        with self.assertRaises(RuntimeError) as ctx:
            adapter.execute(
                unit=make_unit(),
                assignment=assignment,
                freeze_artifacts=(artifact,),
                provider_by_committee={"committee-a": "claude"},
            )
        self.assertIs(ctx.exception, original)

    def test_collector_requires_binding_no_invention(self):
        execution_result = PipelineExecutionResult(
            pipeline_id="p1",
            committee_results=[
                CommitteeExecutionResult(
                    committee_id="committee-a",
                    responses=[
                        AIResponse(
                            provider="claude",
                            task_id="run:unit:0:held-a",
                            prompt_id="tpl-1",
                            prompt_version="1.0",
                            content="actual finding text",
                            status="completed",
                            error="",
                        )
                    ],
                )
            ],
        )
        from InvestmentResearchOrchestrator.models.execution import (
            ExecutionRecord,
        )

        table = StaticRoutingTable(
            routes=(("HOLDING_STRUCTURAL", ("committee-a",)),)
        )
        assignment = StaticCommitteeRouter(table).route(make_unit())
        record = ExecutionRecord(
            research_id="run:unit:0:held-a",
            result=execution_result,
        )
        without = EvidenceCollector().collect(
            execution=record,
            assignment=assignment,
            binding=None,
            subject_id="held-a",
        )
        self.assertEqual(without.findings, ())
        self.assertEqual(len(without.failure_markers), 1)
        self.assertEqual(
            without.failure_markers[0].reason,
            "missing_collection_binding",
        )

        binding = CollectionBinding(
            category="market",
            event_date="2026-01-01",
            publication_date="2026-01-02",
            verification_status="unverified",
        )
        with_binding = EvidenceCollector().collect(
            execution=record,
            assignment=assignment,
            binding=binding,
            subject_id="held-a",
        )
        self.assertEqual(len(with_binding.findings), 1)
        self.assertEqual(
            with_binding.findings[0].statement,
            "actual finding text",
        )
        self.assertEqual(
            with_binding.findings[0].category,
            "market",
        )


if __name__ == "__main__":
    unittest.main()
