from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone

from InvestmentResearchOrchestrator.evidence_store import (
    EvidenceStore,
)
from InvestmentResearchOrchestrator.memory_comparison import (
    MemoryComparison,
)
from InvestmentResearchOrchestrator.models.enums import (
    EvidencePayloadKind,
    MemoryDeltaClass,
)
from InvestmentResearchOrchestrator.models.store import (
    EvidenceStoreRecord,
)


def _now():
    return datetime(2026, 1, 1, tzinfo=timezone.utc)


def _finding(
    *,
    run_id,
    subject_key,
    statement,
    research_id="r1",
    committee_id="c1",
    provider_id="claude",
    prompt_hash="hash-1",
    source_reference="claude",
    stored_at=None,
):
    return EvidenceStoreRecord(
        run_id=run_id,
        research_id=research_id,
        committee_id=committee_id,
        provider_id=provider_id,
        prompt_id="p1",
        prompt_hash=prompt_hash,
        source_reference=source_reference,
        collected_at=_now(),
        stored_at=stored_at or _now(),
        payload_kind=EvidencePayloadKind.FINDING,
        payload=(
            f'{{"subject_key":"{subject_key}",'
            f'"statement":"{statement}"}}'
        ),
    )


def _completeness(
    *,
    run_id,
    research_id,
    missing=(),
    failed=(),
):
    missing_json = ",".join(f'"{item}"' for item in missing)
    failed_json = ",".join(f'"{item}"' for item in failed)
    return EvidenceStoreRecord(
        run_id=run_id,
        research_id=research_id,
        committee_id=None,
        provider_id=None,
        prompt_id=None,
        prompt_hash=None,
        source_reference=None,
        collected_at=_now(),
        stored_at=_now(),
        payload_kind=EvidencePayloadKind.COMPLETENESS,
        payload=(
            '{"required":[],"completed":[],'
            f'"failed":[{failed_json}],'
            f'"missing":[{missing_json}]}}'
        ),
    )


class MemoryComparisonTests(unittest.TestCase):
    def test_no_prior(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            store.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="hello",
                )
            )
            deltas = MemoryComparison().compare(
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

    def test_added_removed_unchanged_statement_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            current = EvidenceStore(tmp + "/current")
            prior = EvidenceStore(tmp + "/prior")
            prior.append(
                _finding(
                    run_id="prior-run",
                    subject_key="kept",
                    statement="same",
                    research_id="r-kept",
                )
            )
            prior.append(
                _finding(
                    run_id="prior-run",
                    subject_key="changed",
                    statement="old",
                    research_id="r-changed",
                )
            )
            prior.append(
                _finding(
                    run_id="prior-run",
                    subject_key="removed",
                    statement="gone",
                    research_id="r-removed",
                )
            )
            current.append(
                _finding(
                    run_id="run-001",
                    subject_key="kept",
                    statement="same",
                    research_id="r-kept",
                )
            )
            current.append(
                _finding(
                    run_id="run-001",
                    subject_key="changed",
                    statement="new",
                    research_id="r-changed",
                )
            )
            current.append(
                _finding(
                    run_id="run-001",
                    subject_key="added",
                    statement="fresh",
                    research_id="r-added",
                )
            )
            deltas = MemoryComparison().compare(
                run_id="run-001",
                current_store=current,
                prior_store=prior,
                prior_run_id="prior-run",
                subject_keys=("kept", "changed", "added", "removed"),
            )
            classes = {
                delta.subject_key: delta.delta_class
                for delta in deltas.deltas
            }
            self.assertEqual(
                classes["kept"],
                MemoryDeltaClass.UNCHANGED,
            )
            self.assertEqual(
                classes["changed"],
                MemoryDeltaClass.STATEMENT_CHANGED,
            )
            self.assertEqual(
                classes["added"],
                MemoryDeltaClass.ADDED,
            )
            self.assertEqual(
                classes["removed"],
                MemoryDeltaClass.REMOVED,
            )

    def test_ignores_pure_stored_at_and_detects_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            current = EvidenceStore(tmp + "/current")
            prior = EvidenceStore(tmp + "/prior")
            prior.append(
                _finding(
                    run_id="prior-run",
                    subject_key="held-a",
                    statement="same",
                    stored_at=datetime(
                        2026, 1, 1, tzinfo=timezone.utc
                    ),
                )
            )
            current.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="same",
                    stored_at=datetime(
                        2026, 2, 1, tzinfo=timezone.utc
                    ),
                )
            )
            unchanged = MemoryComparison().compare(
                run_id="run-001",
                current_store=current,
                prior_store=prior,
                prior_run_id="prior-run",
                subject_keys=("held-a",),
            )
            self.assertEqual(
                unchanged.deltas[0].delta_class,
                MemoryDeltaClass.UNCHANGED,
            )

            current2 = EvidenceStore(tmp + "/current2")
            current2.append(
                _finding(
                    run_id="run-002",
                    subject_key="held-a",
                    statement="same",
                    prompt_hash="hash-other",
                    provider_id="other",
                )
            )
            changed = MemoryComparison().compare(
                run_id="run-002",
                current_store=current2,
                prior_store=prior,
                prior_run_id="prior-run",
                subject_keys=("held-a",),
            )
            self.assertEqual(
                changed.deltas[0].delta_class,
                MemoryDeltaClass.PROVENANCE_CHANGED,
            )
            self.assertIsNotNone(changed.deltas[0].detail)

    def test_multi_finding_set_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            current = EvidenceStore(tmp + "/current")
            prior = EvidenceStore(tmp + "/prior")
            prior.append(
                _finding(
                    run_id="prior-run",
                    subject_key="held-a",
                    statement="one",
                    research_id="r1",
                    committee_id="c1",
                )
            )
            prior.append(
                _finding(
                    run_id="prior-run",
                    subject_key="held-a",
                    statement="two",
                    research_id="r1",
                    committee_id="c2",
                )
            )
            current.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="one",
                    research_id="r1",
                    committee_id="c1",
                )
            )
            current.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="three",
                    research_id="r1",
                    committee_id="c2",
                )
            )
            deltas = MemoryComparison().compare(
                run_id="run-001",
                current_store=current,
                prior_store=prior,
                prior_run_id="prior-run",
                subject_keys=("held-a",),
            )
            self.assertEqual(
                deltas.deltas[0].delta_class,
                MemoryDeltaClass.MULTI_FINDING_SET_CHANGED,
            )

    def test_confidence_gap_when_completeness_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            current = EvidenceStore(tmp + "/current")
            prior = EvidenceStore(tmp + "/prior")
            prior.append(
                _finding(
                    run_id="prior-run",
                    subject_key="held-a",
                    statement="same",
                    research_id="run-001:unit:0:held-a",
                )
            )
            current.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="same",
                    research_id="run-001:unit:0:held-a",
                )
            )
            current.append(
                _completeness(
                    run_id="run-001",
                    research_id="run-001:unit:0:held-a",
                    missing=("committee-b",),
                )
            )
            deltas = MemoryComparison().compare(
                run_id="run-001",
                current_store=current,
                prior_store=prior,
                prior_run_id="prior-run",
                subject_keys=("held-a",),
            )
            self.assertEqual(
                deltas.deltas[0].delta_class,
                MemoryDeltaClass.CONFIDENCE_GAP,
            )

    def test_exact_statement_no_trim_or_case_fold(self):
        with tempfile.TemporaryDirectory() as tmp:
            current = EvidenceStore(tmp + "/current")
            prior = EvidenceStore(tmp + "/prior")
            prior.append(
                _finding(
                    run_id="prior-run",
                    subject_key="held-a",
                    statement="Hello",
                )
            )
            current.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="hello",
                )
            )
            deltas = MemoryComparison().compare(
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

    def test_invalid_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            with self.assertRaisesRegex(ValueError, "run_id"):
                MemoryComparison().compare(
                    run_id="  ",
                    current_store=store,
                    prior_store=None,
                    prior_run_id=None,
                    subject_keys=("held-a",),
                )
            with self.assertRaisesRegex(TypeError, "subject_keys"):
                MemoryComparison().compare(
                    run_id="run-001",
                    current_store=store,
                    prior_store=None,
                    prior_run_id=None,
                    subject_keys=["held-a"],  # type: ignore[arg-type]
                )

    def test_subject_order_caller_then_current_then_prior(self):
        with tempfile.TemporaryDirectory() as tmp:
            current = EvidenceStore(tmp + "/current")
            prior = EvidenceStore(tmp + "/prior")
            prior.append(
                _finding(
                    run_id="prior-run",
                    subject_key="prior-only",
                    statement="old",
                    research_id="r-prior",
                )
            )
            current.append(
                _finding(
                    run_id="run-001",
                    subject_key="current-only",
                    statement="new",
                    research_id="r-current",
                )
            )
            deltas = MemoryComparison().compare(
                run_id="run-001",
                current_store=current,
                prior_store=prior,
                prior_run_id="prior-run",
                subject_keys=("caller",),
            )
            self.assertEqual(
                [delta.subject_key for delta in deltas.deltas],
                ["caller", "current-only", "prior-only"],
            )


if __name__ == "__main__":
    unittest.main()
