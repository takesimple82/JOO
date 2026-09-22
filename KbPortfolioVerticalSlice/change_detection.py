from __future__ import annotations

from InvestmentResearchOrchestrator.scanner import PortfolioScanner
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot


def classify_snapshot_change(
    *,
    run_id: str,
    current_snapshot: ExplicitPortfolioSnapshot,
    prior_snapshot: ExplicitPortfolioSnapshot | None,
) -> str:
    scan = PortfolioScanner().scan(
        run_id=run_id,
        current=current_snapshot,
        prior_baseline=prior_snapshot,
    )
    if len(scan.deltas) == 0:
        return "NO_CHANGE"
    if prior_snapshot is None:
        return "BASELINE_ABSENT"
    return "CHANGED"
