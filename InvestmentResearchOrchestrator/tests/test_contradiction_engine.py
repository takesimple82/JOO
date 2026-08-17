from __future__ import annotations

import tempfile
import unittest
from dataclasses import fields
from datetime import datetime, timezone
from decimal import Decimal

from EvidenceContradiction.models import (
    EvidenceContradictionStatus,
)
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)

from InvestmentResearchOrchestrator.contradiction_engine import (
    ContradictionEngine,
)
from InvestmentResearchOrchestrator.evidence_store import (
    EvidenceStore,
)
from InvestmentResearchOrchestrator.memory_comparison import (
    MemoryComparison,
)
from InvestmentResearchOrchestrator.models.contradiction import (
    ContradictionCase,
)
from InvestmentResearchOrchestrator.models.enums import (
    ContradictionCaseClass,
    ContradictionCaseStatus,
    EvidencePayloadKind,
    MemoryDeltaClass,
    NumericPathStatus,
)
from InvestmentResearchOrchestrator.models.memory import (
    MemoryDelta,
    MemoryDeltaSet,
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
    research_id,
    committee_id,
):
    return EvidenceStoreRecord(
        run_id=run_id,
        research_id=research_id,
        committee_id=committee_id,
        provider_id="claude",
        prompt_id="p1",
        prompt_hash="hash-1",
        source_reference="claude",
        collected_at=_now(),
        stored_at=_now(),
        payload_kind=EvidencePayloadKind.FINDING,
        payload=(
            f'{{"subject_key":"{subject_key}",'
            f'"statement":"{statement}"}}'
        ),
    )


def _completeness(*, run_id, research_id, missing=(), failed=()):
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


def _empty_memory(run_id, *subject_keys):
    return MemoryDeltaSet(
        run_id=run_id,
        deltas=tuple(
            MemoryDelta(
                subject_key=key,
                prior_present=False,
                delta_class=MemoryDeltaClass.NO_PRIOR,
            )
            for key in subject_keys
        ),
    )


def _proposition(**overrides):
    values = {
        "proposition_id": "proposition-001",
        "finding_id": "finding-001",
        "subject_id": "held-a",
        "predicate_id": "predicate-001",
        "value": Decimal("100"),
        "unit_id": "USD",
        "effective_context_id": "context-001",
    }
    values.update(overrides)
    return ExactObservedNumericProposition(**values)


class ContradictionEngineTests(unittest.TestCase):
    def test_multi_committee_conflict_requests_re_research(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            store.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="bullish",
                    research_id="run-001:unit:0:held-a",
                    committee_id="committee-a",
                )
            )
            store.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="bearish",
                    research_id="run-001:unit:0:held-a",
                    committee_id="committee-b",
                )
            )
            evaluation = ContradictionEngine().evaluate(
                run_id="run-001",
                attempt=0,
                current_store=store,
                memory=_empty_memory("run-001", "held-a"),
                subject_keys=("held-a",),
            )
            classes = [
                case.case_class for case in evaluation.cases
            ]
            self.assertIn(
                ContradictionCaseClass.MULTI_COMMITTEE_STATEMENT_CONFLICT,
                classes,
            )
            self.assertEqual(
                evaluation.unresolved,
                tuple(
                    case.case_id
                    for case in evaluation.cases
                    if case.status
                    is ContradictionCaseStatus.UNRESOLVED
                ),
            )
            self.assertGreater(
                len(evaluation.re_research_requests.requests),
                0,
            )
            self.assertEqual(
                evaluation.numeric_path_status,
                NumericPathStatus.NOT_APPLICABLE,
            )

    def test_equal_multi_committee_is_not_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            store.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="same",
                    research_id="run-001:unit:0:held-a",
                    committee_id="committee-a",
                )
            )
            store.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="same",
                    research_id="run-001:unit:0:held-a",
                    committee_id="committee-b",
                )
            )
            evaluation = ContradictionEngine().evaluate(
                run_id="run-001",
                attempt=0,
                current_store=store,
                memory=_empty_memory("run-001", "held-a"),
                subject_keys=("held-a",),
            )
            classes = [
                case.case_class for case in evaluation.cases
            ]
            self.assertNotIn(
                ContradictionCaseClass.MULTI_COMMITTEE_STATEMENT_CONFLICT,
                classes,
            )

    def test_unresolved_set_explicit_and_no_majority_api(self):
        names = [field.name for field in fields(ContradictionCase)]
        self.assertNotIn("truth", names)
        self.assertNotIn("winner", names)
        self.assertNotIn("majority", names)
        self.assertNotIn("vote", names)
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            evaluation = ContradictionEngine().evaluate(
                run_id="run-001",
                attempt=0,
                current_store=store,
                memory=_empty_memory("run-001"),
                subject_keys=(),
            )
            self.assertEqual(evaluation.unresolved, ())
            self.assertEqual(
                evaluation.re_research_requests.requests,
                (),
            )

    def test_path_a_candidate_and_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            absent = ContradictionEngine().evaluate(
                run_id="run-001",
                attempt=0,
                current_store=store,
                memory=_empty_memory("run-001"),
                subject_keys=(),
            )
            self.assertEqual(
                absent.numeric_path_status,
                NumericPathStatus.NOT_APPLICABLE,
            )
            supplied = ContradictionEngine().evaluate(
                run_id="run-001",
                attempt=0,
                current_store=store,
                memory=_empty_memory("run-001", "held-a"),
                subject_keys=("held-a",),
                numeric_pairs=(
                    (
                        _proposition(value=Decimal("100")),
                        _proposition(
                            proposition_id="proposition-002",
                            finding_id="finding-002",
                            value=Decimal("200"),
                        ),
                    ),
                ),
            )
            self.assertEqual(
                supplied.numeric_path_status,
                NumericPathStatus.APPLIED,
            )
            self.assertTrue(
                any(
                    case.case_class
                    is ContradictionCaseClass.NUMERIC_CANDIDATE
                    and case.domain_status
                    is EvidenceContradictionStatus.CONTRADICTION_CANDIDATE
                    for case in supplied.cases
                )
            )

    def test_path_a_domain_exception_propagates(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            with self.assertRaisesRegex(TypeError, "value"):
                ContradictionEngine().evaluate(
                    run_id="run-001",
                    attempt=0,
                    current_store=store,
                    memory=_empty_memory("run-001"),
                    subject_keys=(),
                    numeric_pairs=(
                        (
                            _proposition(value=1),  # type: ignore[arg-type]
                            _proposition(
                                proposition_id="proposition-002",
                                finding_id="finding-002",
                            ),
                        ),
                    ),
                )

    def test_prior_vs_current_from_memory_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            current = EvidenceStore(tmp + "/current")
            prior = EvidenceStore(tmp + "/prior")
            prior.append(
                _finding(
                    run_id="prior-run",
                    subject_key="held-a",
                    statement="old",
                    research_id="prior-run:unit:0:held-a",
                    committee_id="committee-a",
                )
            )
            current.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="new",
                    research_id="run-001:unit:0:held-a",
                    committee_id="committee-a",
                )
            )
            memory = MemoryComparison().compare(
                run_id="run-001",
                current_store=current,
                prior_store=prior,
                prior_run_id="prior-run",
                subject_keys=("held-a",),
            )
            evaluation = ContradictionEngine().evaluate(
                run_id="run-001",
                attempt=0,
                current_store=current,
                memory=memory,
                subject_keys=("held-a",),
            )
            self.assertTrue(
                any(
                    case.case_class
                    is ContradictionCaseClass.PRIOR_VS_CURRENT_STATEMENT_CONFLICT
                    for case in evaluation.cases
                )
            )

    def test_confidence_insufficient_from_completeness_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            store.append(
                _finding(
                    run_id="run-001",
                    subject_key="held-a",
                    statement="only",
                    research_id="run-001:unit:0:held-a",
                    committee_id="committee-a",
                )
            )
            store.append(
                _completeness(
                    run_id="run-001",
                    research_id="run-001:unit:0:held-a",
                    missing=("committee-b",),
                )
            )
            evaluation = ContradictionEngine().evaluate(
                run_id="run-001",
                attempt=0,
                current_store=store,
                memory=_empty_memory("run-001", "held-a"),
                subject_keys=("held-a",),
            )
            self.assertTrue(
                any(
                    case.case_class
                    is ContradictionCaseClass.CONFIDENCE_INSUFFICIENT
                    for case in evaluation.cases
                )
            )


if __name__ == "__main__":
    unittest.main()
