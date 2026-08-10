from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from InvestmentResearchOrchestrator.evidence_store import (
    EvidenceStore,
)
from InvestmentResearchOrchestrator.models.enums import (
    EvidencePayloadKind,
)
from InvestmentResearchOrchestrator.models.store import (
    EvidenceStoreRecord,
)


def make_record(**overrides):
    values = {
        "run_id": "run-001",
        "research_id": "research-001",
        "committee_id": "committee-a",
        "provider_id": "claude",
        "prompt_id": "prompt-1",
        "prompt_hash": "abc",
        "source_reference": "claude",
        "collected_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "stored_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "payload_kind": EvidencePayloadKind.FINDING,
        "payload": '{"statement":"hello"}',
    }
    values.update(overrides)
    return EvidenceStoreRecord(**values)


class EvidenceStoreTests(unittest.TestCase):
    def test_append_only_preserves_prior_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            first = make_record(payload='{"statement":"one"}')
            second = make_record(
                research_id="research-002",
                payload='{"statement":"two"}',
            )
            store.append(first)
            store.append(second)
            records = store.list_for_run("run-001")
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0].payload, first.payload)
            self.assertEqual(records[1].payload, second.payload)

            path = Path(tmp) / "run-001.jsonl"
            lines = path.read_text(encoding="utf-8").strip().split(
                "\n"
            )
            self.assertEqual(len(lines), 2)

    def test_empty_store_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            self.assertEqual(store.list_for_run("missing"), ())

    def test_list_by_research_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            store.append(make_record(research_id="r1"))
            store.append(make_record(research_id="r2"))
            matched = store.list_by_research_id("run-001", "r1")
            self.assertEqual(len(matched), 1)
            self.assertEqual(matched[0].research_id, "r1")

    def test_does_not_rewrite_prior_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            store.append(make_record(payload="first"))
            before = (Path(tmp) / "run-001.jsonl").read_text(
                encoding="utf-8"
            )
            store.append(make_record(payload="second"))
            after = (Path(tmp) / "run-001.jsonl").read_text(
                encoding="utf-8"
            )
            self.assertTrue(after.startswith(before))


if __name__ == "__main__":
    unittest.main()
