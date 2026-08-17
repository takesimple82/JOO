from __future__ import annotations

from InvestmentResearchOrchestrator.models.enums import (
    IRORunPhase,
    IRORunStatus,
)
from InvestmentResearchOrchestrator.models.run import IRORun
from InvestmentResearchOrchestrator.validation.common import (
    require_datetime,
    require_enum,
    require_nonblank_string,
    require_optional_nonblank_string,
)


def validate_iro_run(run: IRORun) -> None:
    if type(run) is not IRORun:
        raise TypeError("run must be IRORun")
    require_nonblank_string("run_id", run.run_id)
    require_nonblank_string(
        "portfolio_snapshot_id",
        run.portfolio_snapshot_id,
    )
    require_optional_nonblank_string(
        "prior_baseline_id",
        run.prior_baseline_id,
    )
    require_enum("phase", run.phase, IRORunPhase)
    require_enum("status", run.status, IRORunStatus)
    require_datetime("created_at", run.created_at)
    require_datetime("updated_at", run.updated_at)
    _validate_phase_status_consistency(run)


def _validate_phase_status_consistency(run: IRORun) -> None:
    terminal_phases = {
        IRORunPhase.COMPLETED: IRORunStatus.COMPLETED,
        IRORunPhase.SHORT_CIRCUITED_NO_MATERIAL_DELTA: (
            IRORunStatus.SHORT_CIRCUITED_NO_MATERIAL_DELTA
        ),
        IRORunPhase.FAILED: IRORunStatus.FAILED,
        IRORunPhase.ESCALATED_HUMAN_REVIEW: (
            IRORunStatus.ESCALATED_HUMAN_REVIEW
        ),
    }
    if run.phase in terminal_phases:
        expected = terminal_phases[run.phase]
        if run.status is not expected:
            raise ValueError(
                "status must match terminal phase"
            )
        return
    if run.status is not IRORunStatus.IN_PROGRESS:
        raise ValueError(
            "status must be IN_PROGRESS for non-terminal phase"
        )
