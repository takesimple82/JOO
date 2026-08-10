from __future__ import annotations

import unittest
from decimal import Decimal

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

from InvestmentResearchOrchestrator.models.enums import (
    ScanChangeClass,
    SubjectClass,
)
from InvestmentResearchOrchestrator.planner import ResearchPlanner
from InvestmentResearchOrchestrator.scanner import PortfolioScanner


def make_context(
    *,
    observation_context_id="context-001",
    portfolio_id="portfolio-001",
):
    return ExplicitPortfolioObservationContext(
        observation_context_id,
        portfolio_id,
    )


def make_observation(
    context,
    *,
    position_id="position-001",
    portfolio_subject_id="subject-001",
    quantity=Decimal("10.00"),
):
    position = ExplicitPortfolioPosition(
        position_id,
        ExplicitPortfolioMembership(
            context.portfolio_id,
            portfolio_subject_id,
        ),
    )
    return ExplicitPortfolioHoldingObservation(
        position,
        context,
        quantity,
    )


def make_watchlist(
    *,
    portfolio_id="portfolio-001",
    portfolio_subject_id="watch-001",
):
    return ExplicitPortfolioWatchlistEntry(
        ExplicitPortfolioMembership(
            portfolio_id,
            portfolio_subject_id,
        )
    )


def make_snapshot(
    *,
    snapshot_id="snap-001",
    holdings=None,
    watchlist=None,
    context=None,
):
    context = context or make_context()
    if holdings is None:
        holdings = (
            make_observation(
                context,
                portfolio_subject_id="held-a",
                quantity=Decimal("1"),
            ),
        )
    if watchlist is None:
        watchlist = (
            make_watchlist(portfolio_subject_id="watch-a"),
        )
    return ExplicitPortfolioSnapshot(
        snapshot_id,
        context,
        ExplicitPortfolioHoldingSnapshot(context, holdings),
        watchlist,
    )


class ScannerPlannerTests(unittest.TestCase):
    def test_scan_skips_unchanged_subjects(self):
        context = make_context()
        current = make_snapshot(
            snapshot_id="snap-current",
            context=context,
            holdings=(
                make_observation(
                    context,
                    portfolio_subject_id="held-a",
                    quantity=Decimal("5"),
                ),
            ),
            watchlist=(
                make_watchlist(portfolio_subject_id="watch-a"),
            ),
        )
        prior = make_snapshot(
            snapshot_id="snap-prior",
            context=context,
            holdings=(
                make_observation(
                    context,
                    position_id="position-prior",
                    portfolio_subject_id="held-a",
                    quantity=Decimal("5"),
                ),
            ),
            watchlist=(
                make_watchlist(portfolio_subject_id="watch-a"),
            ),
        )
        deltas = PortfolioScanner().scan(
            run_id="run-001",
            current=current,
            prior_baseline=prior,
        )
        self.assertEqual(deltas.deltas, ())

    def test_quantity_changed_and_membership_added(self):
        context = make_context()
        current = make_snapshot(
            context=context,
            holdings=(
                make_observation(
                    context,
                    portfolio_subject_id="held-a",
                    quantity=Decimal("9"),
                ),
                make_observation(
                    context,
                    position_id="position-002",
                    portfolio_subject_id="held-b",
                    quantity=Decimal("1"),
                ),
            ),
            watchlist=(),
        )
        prior = make_snapshot(
            snapshot_id="snap-prior",
            context=context,
            holdings=(
                make_observation(
                    context,
                    portfolio_subject_id="held-a",
                    quantity=Decimal("5"),
                ),
            ),
            watchlist=(),
        )
        deltas = PortfolioScanner().scan(
            run_id="run-001",
            current=current,
            prior_baseline=prior,
        )
        classes = [d.change_class for d in deltas.deltas]
        subjects = [d.subject_id for d in deltas.deltas]
        self.assertEqual(
            classes,
            [
                ScanChangeClass.QUANTITY_CHANGED,
                ScanChangeClass.MEMBERSHIP_ADDED,
            ],
        )
        self.assertEqual(subjects, ["held-a", "held-b"])

    def test_baseline_absent_emits_presence_deltas(self):
        snapshot = make_snapshot()
        deltas = PortfolioScanner().scan(
            run_id="run-001",
            current=snapshot,
            prior_baseline=None,
        )
        self.assertTrue(
            all(
                d.change_class
                is ScanChangeClass.BASELINE_ABSENT_SUBJECT
                for d in deltas.deltas
            )
        )
        self.assertEqual(
            [d.subject_class for d in deltas.deltas],
            [SubjectClass.HOLDING, SubjectClass.WATCHLIST],
        )

    def test_empty_plan_with_reasons(self):
        from InvestmentResearchOrchestrator.models.scan import (
            ScanDeltaSet,
        )

        empty = ScanDeltaSet(run_id="run-001", deltas=())
        plan = ResearchPlanner().plan(empty)
        self.assertEqual(plan.units, ())
        self.assertEqual(len(plan.skips), 1)
        self.assertEqual(
            plan.skips[0].reason,
            "empty_scan_no_material_delta",
        )

    def test_plan_priority_mapping(self):
        snapshot = make_snapshot()
        deltas = PortfolioScanner().scan(
            run_id="run-002",
            current=snapshot,
            prior_baseline=None,
        )
        plan = ResearchPlanner().plan(deltas)
        self.assertEqual(len(plan.units), 2)
        self.assertEqual(plan.units[0].priority, "P0")
        self.assertEqual(plan.units[1].priority, "P1")
        self.assertEqual(
            plan.units[0].task_type,
            "HOLDING_STRUCTURAL",
        )
        self.assertEqual(
            plan.units[1].task_type,
            "WATCHLIST_STRUCTURAL",
        )


if __name__ == "__main__":
    unittest.main()
