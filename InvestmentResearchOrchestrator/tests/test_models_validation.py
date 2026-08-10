from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone

from InvestmentResearchOrchestrator.models.enums import (
    IRORunPhase,
    IRORunStatus,
    ScanChangeClass,
    SubjectClass,
)
from InvestmentResearchOrchestrator.models.run import IRORun
from InvestmentResearchOrchestrator.models.scan import ScanDelta
from InvestmentResearchOrchestrator.validation.run import (
    validate_iro_run,
)
from InvestmentResearchOrchestrator.validation.scan import (
    validate_scan_delta,
)


def make_run(**overrides):
    values = {
        "run_id": "run-001",
        "portfolio_snapshot_id": "snap-001",
        "prior_baseline_id": None,
        "phase": IRORunPhase.INITIALIZED,
        "status": IRORunStatus.IN_PROGRESS,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return IRORun(**values)


class IRORunValidationTests(unittest.TestCase):
    def test_valid_run_with_absent_baseline(self):
        run = make_run(prior_baseline_id=None)
        validate_iro_run(run)
        self.assertIsNone(run.prior_baseline_id)

    def test_valid_run_with_baseline_id(self):
        run = make_run(prior_baseline_id="baseline-001")
        validate_iro_run(run)
        self.assertEqual(run.prior_baseline_id, "baseline-001")

    def test_blank_run_id_fails_closed(self):
        run = make_run(run_id="  ")
        with self.assertRaisesRegex(ValueError, "run_id"):
            validate_iro_run(run)

    def test_wrong_type_run_id_fails(self):
        run = make_run(run_id=123)  # type: ignore[arg-type]
        with self.assertRaisesRegex(TypeError, "run_id"):
            validate_iro_run(run)

    def test_terminal_status_must_match_phase(self):
        run = make_run(
            phase=IRORunPhase.COMPLETED,
            status=IRORunStatus.FAILED,
        )
        with self.assertRaisesRegex(ValueError, "terminal"):
            validate_iro_run(run)

    def test_non_terminal_requires_in_progress(self):
        run = make_run(
            phase=IRORunPhase.SCANNED,
            status=IRORunStatus.COMPLETED,
        )
        with self.assertRaisesRegex(ValueError, "IN_PROGRESS"):
            validate_iro_run(run)

    def test_model_is_frozen(self):
        run = make_run()
        with self.assertRaises(FrozenInstanceError):
            run.run_id = "other"  # type: ignore[misc]

    def test_field_order(self):
        names = [field.name for field in fields(IRORun)]
        self.assertEqual(
            names,
            [
                "run_id",
                "portfolio_snapshot_id",
                "prior_baseline_id",
                "phase",
                "status",
                "created_at",
                "updated_at",
            ],
        )


class ScanDeltaValidationTests(unittest.TestCase):
    def test_materiality_basis_must_equal_change_class(self):
        delta = ScanDelta(
            subject_id="s1",
            change_class=ScanChangeClass.MEMBERSHIP_ADDED,
            materiality_basis=ScanChangeClass.QUANTITY_CHANGED,
            subject_class=SubjectClass.HOLDING,
        )
        with self.assertRaisesRegex(ValueError, "materiality_basis"):
            validate_scan_delta(delta)

    def test_valid_delta(self):
        delta = ScanDelta(
            subject_id="s1",
            change_class=ScanChangeClass.MEMBERSHIP_ADDED,
            materiality_basis=ScanChangeClass.MEMBERSHIP_ADDED,
            subject_class=SubjectClass.HOLDING,
        )
        validate_scan_delta(delta)


if __name__ == "__main__":
    unittest.main()
