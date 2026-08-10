from __future__ import annotations

from decimal import Decimal

from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioSnapshot.validation import (
    validate_explicit_portfolio_snapshot,
)

from InvestmentResearchOrchestrator.models.enums import (
    ScanChangeClass,
    SubjectClass,
)
from InvestmentResearchOrchestrator.models.scan import (
    ScanDelta,
    ScanDeltaSet,
)
from InvestmentResearchOrchestrator.validation.scan import (
    validate_scan_delta_set,
)


class PortfolioScanner:
    """Structural subject deltas only (IRO-M1)."""

    def scan(
        self,
        *,
        run_id: str,
        current: ExplicitPortfolioSnapshot,
        prior_baseline: ExplicitPortfolioSnapshot | None,
    ) -> ScanDeltaSet:
        if type(run_id) is not str or run_id.strip() == "":
            raise ValueError("run_id must be nonblank str")
        validate_explicit_portfolio_snapshot(current)
        if prior_baseline is not None:
            validate_explicit_portfolio_snapshot(prior_baseline)

        current_holdings = self._holding_map(current)
        current_watchlist = self._watchlist_ids(current)

        if prior_baseline is None:
            deltas = self._baseline_absent_deltas(
                current_holdings,
                current_watchlist,
            )
            result = ScanDeltaSet(
                run_id=run_id,
                deltas=tuple(deltas),
            )
            validate_scan_delta_set(result)
            return result

        prior_holdings = self._holding_map(prior_baseline)
        prior_watchlist = self._watchlist_ids(prior_baseline)
        deltas = self._structural_deltas(
            current_holdings=current_holdings,
            current_watchlist=current_watchlist,
            prior_holdings=prior_holdings,
            prior_watchlist=prior_watchlist,
        )
        result = ScanDeltaSet(
            run_id=run_id,
            deltas=tuple(deltas),
        )
        validate_scan_delta_set(result)
        return result

    @staticmethod
    def _holding_map(
        snapshot: ExplicitPortfolioSnapshot,
    ) -> list[tuple[str, Decimal]]:
        ordered: list[tuple[str, Decimal]] = []
        for observation in snapshot.holding_snapshot.holding_observations:
            subject_id = (
                observation.position.membership.portfolio_subject_id
            )
            ordered.append((subject_id, observation.quantity))
        return ordered

    @staticmethod
    def _watchlist_ids(
        snapshot: ExplicitPortfolioSnapshot,
    ) -> list[str]:
        return [
            entry.membership.portfolio_subject_id
            for entry in snapshot.watchlist_entries
        ]

    @staticmethod
    def _baseline_absent_deltas(
        holdings: list[tuple[str, Decimal]],
        watchlist: list[str],
    ) -> list[ScanDelta]:
        deltas: list[ScanDelta] = []
        for subject_id, _quantity in holdings:
            deltas.append(
                ScanDelta(
                    subject_id=subject_id,
                    change_class=(
                        ScanChangeClass.BASELINE_ABSENT_SUBJECT
                    ),
                    materiality_basis=(
                        ScanChangeClass.BASELINE_ABSENT_SUBJECT
                    ),
                    subject_class=SubjectClass.HOLDING,
                )
            )
        for subject_id in watchlist:
            deltas.append(
                ScanDelta(
                    subject_id=subject_id,
                    change_class=(
                        ScanChangeClass.BASELINE_ABSENT_SUBJECT
                    ),
                    materiality_basis=(
                        ScanChangeClass.BASELINE_ABSENT_SUBJECT
                    ),
                    subject_class=SubjectClass.WATCHLIST,
                )
            )
        return deltas

    @staticmethod
    def _structural_deltas(
        *,
        current_holdings: list[tuple[str, Decimal]],
        current_watchlist: list[str],
        prior_holdings: list[tuple[str, Decimal]],
        prior_watchlist: list[str],
    ) -> list[ScanDelta]:
        deltas: list[ScanDelta] = []
        prior_holding_map = {
            subject_id: quantity
            for subject_id, quantity in prior_holdings
        }
        prior_watch_set = set(prior_watchlist)
        current_holding_ids = {
            subject_id for subject_id, _ in current_holdings
        }
        current_watch_set = set(current_watchlist)

        for subject_id, quantity in current_holdings:
            if subject_id not in prior_holding_map:
                deltas.append(
                    ScanDelta(
                        subject_id=subject_id,
                        change_class=(
                            ScanChangeClass.MEMBERSHIP_ADDED
                        ),
                        materiality_basis=(
                            ScanChangeClass.MEMBERSHIP_ADDED
                        ),
                        subject_class=SubjectClass.HOLDING,
                    )
                )
            elif prior_holding_map[subject_id] != quantity:
                deltas.append(
                    ScanDelta(
                        subject_id=subject_id,
                        change_class=(
                            ScanChangeClass.QUANTITY_CHANGED
                        ),
                        materiality_basis=(
                            ScanChangeClass.QUANTITY_CHANGED
                        ),
                        subject_class=SubjectClass.HOLDING,
                    )
                )

        for subject_id in current_watchlist:
            if subject_id not in prior_watch_set:
                deltas.append(
                    ScanDelta(
                        subject_id=subject_id,
                        change_class=(
                            ScanChangeClass.MEMBERSHIP_ADDED
                        ),
                        materiality_basis=(
                            ScanChangeClass.MEMBERSHIP_ADDED
                        ),
                        subject_class=SubjectClass.WATCHLIST,
                    )
                )

        for subject_id, _quantity in prior_holdings:
            if subject_id not in current_holding_ids:
                deltas.append(
                    ScanDelta(
                        subject_id=subject_id,
                        change_class=(
                            ScanChangeClass.MEMBERSHIP_REMOVED
                        ),
                        materiality_basis=(
                            ScanChangeClass.MEMBERSHIP_REMOVED
                        ),
                        subject_class=SubjectClass.HOLDING,
                    )
                )

        for subject_id in prior_watchlist:
            if subject_id not in current_watch_set:
                deltas.append(
                    ScanDelta(
                        subject_id=subject_id,
                        change_class=(
                            ScanChangeClass.MEMBERSHIP_REMOVED
                        ),
                        materiality_basis=(
                            ScanChangeClass.MEMBERSHIP_REMOVED
                        ),
                        subject_class=SubjectClass.WATCHLIST,
                    )
                )

        return deltas
