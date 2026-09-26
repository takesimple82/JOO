from __future__ import annotations

import ast
import hashlib
import unittest
from pathlib import Path

from BrokerExecutionCycle.mutation_transport import (
    LiveMutationTransportDisabled,
    default_mutation_transport,
)


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def production_paths(package: Path):
    return tuple(p for p in package.rglob("*.py") if "tests" not in p.parts)


class BoundaryTests(unittest.TestCase):
    def test_no_joo_automation_or_generic_orchestration(self):
        source = "\n".join(path.read_text() for path in production_paths(ROOT))
        for forbidden in (
            "joo_auto",
            "JOOAutomation",
            "JOO-Automation",
            "while True",
            "CREATE TABLE",
            "uuid4",
            "float(",
            "celery",
            "apscheduler",
            "workflow_engine",
            "LoopCore",
            "task_queue",
            "distributed_scheduler",
            "orchestration_dsl",
        ):
            self.assertNotIn(forbidden, source)

        imported = set()
        for path in production_paths(ROOT):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(a.name.split(".")[0] for a in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
        forbidden_pkgs = {
            "joo_auto",
            "JOOAutomation",
            "AIAdapter",
            "Committee",
            "ExecutionEngine",
            "PipelineRuntime",
        }
        self.assertTrue(imported.isdisjoint(forbidden_pkgs), imported)

    def test_live_mutation_disabled_default(self):
        transport = default_mutation_transport()
        self.assertIsInstance(transport, LiveMutationTransportDisabled)
        with self.assertRaises(RuntimeError):
            transport.submit("/api/v1/ssam1802", {})

    def test_preserved_docs_hashes_unchanged(self):
        expected = {
            "docs/JOO_PRODUCT_ARCHITECTURE.md": (
                "bb745ebb8f1ca21a114cbe980aa67fa5b97a41423a9c7d0233921fd4e4b3bfa3"
            ),
            "docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md": (
                "fd32ae81147cdcc8156dd277cccd0fa4193dd8ffd6775249bd0ef2f8da9f16cf"
            ),
        }
        for rel, digest in expected.items():
            data = (REPO / rel).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_a_b_c_packages_do_not_import_command_center(self):
        for package in (
            "OperationalCioCycle",
            "CapitalAllocationCycle",
            "KbCapitalFactAuthority",
            "BrokerExecutionCycle",
            "ExactExpectedValue",
        ):
            for path in production_paths(REPO / package):
                tree = ast.parse(path.read_text())
                for node in ast.walk(tree):
                    modules = []
                    if isinstance(node, ast.Import):
                        modules = [a.name for a in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        modules = [node.module or ""]
                    for module in modules:
                        self.assertFalse(
                            module.startswith("CommandCenterRuntime"),
                            (package, path, module),
                        )

    def test_journal_kinds_and_codec_admit_block_d(self):
        from InvestmentDecisionVerticalSlice.models import JournalRecordKind
        from OperationalCioCycle.codec import encode, decode
        from CommandCenterRuntime.models import WakeEvent
        from CommandCenterRuntime.tests.helpers import NOW
        from CommandCenterRuntime.wake import seal_wake_event

        for name in (
            "WAKE_EVENT",
            "OPERATIONAL_CHECKPOINT",
            "HUMAN_ATTENTION_ITEM",
            "PROVIDER_OPERATION_FAILURE",
        ):
            self.assertEqual(JournalRecordKind[name].value, name)

        event = seal_wake_event(
            wake_event_id="w1",
            wake_type="PROVIDER_FAILURE",
            source="FactStore",
            fact_or_evidence_id="f1",
            observed_at=NOW,
            subject_ids=(),
            provenance="p",
        )
        self.assertIsInstance(event, WakeEvent)
        self.assertEqual(decode(encode(event)), event)


if __name__ == "__main__":
    unittest.main()
