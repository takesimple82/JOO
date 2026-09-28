from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from FactStore.sqlite_storage import SQLiteAppendOnlyFactEngine
from FactStore.store import FactStore
from InvestmentResearchOrchestrator.models.enums import (
    IRORunPhase,
    IRORunStatus,
)
from InvestmentResearchOrchestrator.models.run import IRORun
from PortfolioSnapshotProducer.production import PortfolioSnapshotProducer
from ProviderGateway.models import (
    ExplicitBrokerAdapterBinding,
    ExplicitBrokerCollectRequest,
    ExplicitBrokerParameterProfile,
    ExplicitCollectOutcome,
    ExplicitProviderFailureSignal,
    ExplicitProviderPayloadEnvelope,
)

from KbPortfolioVerticalSlice.models import (
    ExplicitKbNormalizationRequest,
    ExplicitKbPositionBinding,
    ExplicitSnapshotIdentity,
    ExplicitVerticalSlicePolicy,
)
from KbPortfolioVerticalSlice.service import (
    run_kb_portfolio_vertical_slice,
)
from KbPortfolioVerticalSlice.validation import validate_iro_ingress


UTC = timezone.utc
COLLECTED = datetime(2026, 9, 22, 0, 0, tzinfo=UTC)

# Official SSQM2952.Record1.crncy_cd fixed-width String(3) blank.
OFFICIAL_FIXED_WIDTH_BLANK = "   "


class FakeAdapter:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = []

    def collect(self, request):
        self.calls.append(request)
        return self.outcome


class RecordingCoordinator:
    def __init__(self):
        self.calls = []

    def run(self, **kwargs):
        self.calls.append(kwargs)
        return "existing-iro-result"


def collect_request(suffix="001"):
    profile = ExplicitBrokerParameterProfile(
        f"profile-{suffix}",
        "account-primary",
        ("holdings",),
    )
    binding = ExplicitBrokerAdapterBinding(
        "kb_open_api",
        "credential-ref",
        profile,
    )
    return ExplicitBrokerCollectRequest(
        f"raw-envelope-{suffix}",
        f"correlation-{suffix}",
        binding,
        "holdings",
        None,
    )


def payload(
    quantity="000000000010",
    *,
    duplicate=False,
    currency="KRW",
    valuation="000000710000",
    now_price="0000071000",
):
    row = {
        "clsf": "domestic-stock",
        "crncy_cd": currency,
        "is_cd": "005930",
        "is_nm": "삼성전자",
        "hld_q": quantity,
        "now_prc": now_price,
        "val_amt": valuation,
    }
    rows = [row]
    if duplicate:
        rows.append(dict(row))
    return {
        "dataHeader": {
            "processFlag": "A",
            "processCode": "0011",
        },
        "dataBody": {"Record1": rows},
    }


def successful_outcome(
    suffix="001",
    quantity="000000000010",
    *,
    currency="KRW",
    provider_id="kb_open_api",
):
    envelope = ExplicitProviderPayloadEnvelope(
        f"raw-envelope-{suffix}",
        provider_id,
        "broker_fact",
        COLLECTED,
        "success",
        payload(quantity, currency=currency),
        None,
        f"correlation-{suffix}",
    )
    return ExplicitCollectOutcome("success", envelope, None)


def normalization_request(suffix="001", *, currency="KRW"):
    binding = ExplicitKbPositionBinding(
        "account-primary",
        "domestic-stock",
        currency,
        "005930",
        f"position-fact-{suffix}",
        f"position-envelope-{suffix}",
        "position-samsung",
        "subject-samsung",
        None,
    )
    return ExplicitKbNormalizationRequest(
        f"raw-fact-{suffix}",
        "account-primary",
        (binding,),
    )


def run_model(snapshot_id, prior_id=None, suffix="001"):
    return IRORun(
        f"run-{suffix}",
        snapshot_id,
        prior_id,
        IRORunPhase.INITIALIZED,
        IRORunStatus.IN_PROGRESS,
        COLLECTED,
        COLLECTED,
    )


class VerticalSliceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        path = Path(self.temporary.name) / "facts.sqlite3"
        self.engine = SQLiteAppendOnlyFactEngine(path)
        self.store = FactStore(lambda: COLLECTED, self.engine)

    def tearDown(self):
        self.engine.close()
        self.temporary.cleanup()

    def execute(
        self,
        *,
        suffix="001",
        quantity="000000000010",
        evaluation_time=COLLECTED,
        prior=None,
        coordinator=None,
        max_age=timedelta(minutes=5),
        raw_currency="KRW",
        binding_currency="KRW",
    ):
        snapshot_id = f"snapshot-{suffix}"
        coordinator = coordinator or RecordingCoordinator()
        result = run_kb_portfolio_vertical_slice(
            adapter=FakeAdapter(
                successful_outcome(
                    suffix,
                    quantity,
                    currency=raw_currency,
                )
            ),
            collect_request=collect_request(suffix),
            raw_fact_id=f"raw-fact-{suffix}",
            normalization_request=normalization_request(
                suffix,
                currency=binding_currency,
            ),
            fact_store=self.store,
            snapshot_producer=PortfolioSnapshotProducer(
                self.store, lambda: evaluation_time
            ),
            snapshot_identity=ExplicitSnapshotIdentity(
                snapshot_id,
                f"context-{suffix}",
                "portfolio-main",
            ),
            watchlist_memberships=(),
            policy=ExplicitVerticalSlicePolicy(max_age),
            run=run_model(
                snapshot_id,
                None if prior is None else prior.portfolio_snapshot_id,
                suffix,
            ),
            prior_snapshot=prior,
            ingress_id=f"ingress-{suffix}",
            coordinator=coordinator,
            iro_run_arguments={},
        )
        return result, coordinator

    def test_end_to_end_baseline_preserves_raw_and_wakes_iro(self):
        result, coordinator = self.execute()
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(result.change_class, "BASELINE_ABSENT")
        self.assertEqual(result.iro_result, "existing-iro-result")
        self.assertEqual(len(coordinator.calls), 1)
        raw = self.store.get_by_fact_id("raw-fact-001")
        self.assertEqual(raw.payload, payload())
        canonical = self.store.get_by_fact_id("position-fact-001")
        self.assertEqual(canonical.payload["raw_fact_id"], raw.fact_id)
        self.assertEqual(canonical.payload["raw_quantity"], "000000000010")
        self.assertEqual(canonical.payload["quantity"], "10")
        self.assertEqual(canonical.payload["currency_code"], "KRW")
        self.assertEqual(canonical.payload["raw_currency_code"], "KRW")
        self.assertEqual(
            result.snapshot.holding_snapshot.holding_observations[0].quantity,
            10,
        )
        self.assertEqual(
            result.ingress.snapshot_used_fact_ids,
            ("position-fact-001",),
        )

    def test_blank_domestic_currency_preserves_raw_and_canonicalizes_krw(self):
        result, _coordinator = self.execute(raw_currency="")
        raw = self.store.get_by_fact_id("raw-fact-001")
        canonical = self.store.get_by_fact_id("position-fact-001")
        self.assertEqual(
            raw.payload["dataBody"]["Record1"][0]["crncy_cd"],
            "",
        )
        self.assertEqual(canonical.payload["raw_currency_code"], "")
        self.assertEqual(canonical.payload["currency_code"], "KRW")
        self.assertEqual(result.snapshot.portfolio_snapshot_id, "snapshot-001")

    def test_official_fixed_width_blank_preserves_three_spaces(self):
        result, _coordinator = self.execute(
            raw_currency=OFFICIAL_FIXED_WIDTH_BLANK
        )
        raw = self.store.get_by_fact_id("raw-fact-001")
        canonical = self.store.get_by_fact_id("position-fact-001")
        self.assertEqual(
            raw.payload["dataBody"]["Record1"][0]["crncy_cd"],
            "   ",
        )
        self.assertEqual(len(canonical.payload["raw_currency_code"]), 3)
        self.assertEqual(canonical.payload["raw_currency_code"], "   ")
        self.assertNotEqual(canonical.payload["raw_currency_code"], "")
        self.assertEqual(canonical.payload["currency_code"], "KRW")
        self.assertEqual(result.snapshot.portfolio_snapshot_id, "snapshot-001")

    def test_blank_domestic_currency_replays_deterministically(self):
        self.execute(raw_currency=OFFICIAL_FIXED_WIDTH_BLANK)
        reopened = SQLiteAppendOnlyFactEngine(
            Path(self.temporary.name) / "facts.sqlite3"
        )
        try:
            replay = FactStore(lambda: COLLECTED, reopened)
            raw = replay.get_by_fact_id("raw-fact-001")
            canonical = replay.get_by_fact_id("position-fact-001")
            self.assertEqual(
                raw.payload["dataBody"]["Record1"][0]["crncy_cd"],
                "   ",
            )
            self.assertEqual(canonical.payload["raw_currency_code"], "   ")
            self.assertEqual(canonical.payload["currency_code"], "KRW")
        finally:
            reopened.close()

    def test_unsupported_nonblank_currency_fails_closed(self):
        with self.assertRaisesRegex(
            ValueError,
            "^unsupported SSQM2952 currency$",
        ):
            self.execute(raw_currency="USD", binding_currency="USD")
        raw = self.store.get_by_fact_id("raw-fact-001")
        self.assertEqual(
            raw.payload["dataBody"]["Record1"][0]["crncy_cd"],
            "USD",
        )
        with self.assertRaisesRegex(ValueError, "^fact_id not found$"):
            self.store.get_by_fact_id("position-fact-001")

    def test_blank_currency_with_foreign_binding_fails_closed(self):
        with self.assertRaisesRegex(
            ValueError,
            "^blank crncy_cd requires explicit KRW binding$",
        ):
            self.execute(
                raw_currency=OFFICIAL_FIXED_WIDTH_BLANK,
                binding_currency="USD",
            )
        raw = self.store.get_by_fact_id("raw-fact-001")
        self.assertEqual(
            raw.payload["dataBody"]["Record1"][0]["crncy_cd"],
            "   ",
        )
        with self.assertRaisesRegex(ValueError, "^fact_id not found$"):
            self.store.get_by_fact_id("position-fact-001")

    def test_blank_currency_from_unknown_provider_fails_closed(self):
        request = collect_request()
        request = replace(
            request,
            binding=replace(request.binding, provider_id="unknown"),
        )
        outcome = successful_outcome(
            currency=OFFICIAL_FIXED_WIDTH_BLANK, provider_id="unknown"
        )
        with self.assertRaisesRegex(
            ValueError,
            "^raw provider must be kb_open_api$",
        ):
            run_kb_portfolio_vertical_slice(
                adapter=FakeAdapter(outcome),
                collect_request=request,
                raw_fact_id="raw-fact-001",
                normalization_request=normalization_request(),
                fact_store=self.store,
                snapshot_producer=PortfolioSnapshotProducer(
                    self.store, lambda: COLLECTED
                ),
                snapshot_identity=ExplicitSnapshotIdentity(
                    "snapshot-001", "context-001", "portfolio-main"
                ),
                watchlist_memberships=(),
                policy=ExplicitVerticalSlicePolicy(timedelta(minutes=5)),
                run=run_model("snapshot-001"),
                prior_snapshot=None,
                ingress_id="ingress-001",
                coordinator=RecordingCoordinator(),
                iro_run_arguments={},
            )
        with self.assertRaisesRegex(ValueError, "^fact_id not found$"):
            self.store.get_by_fact_id("position-fact-001")

    def test_zero_quantity_is_historical_but_not_active(self):
        result, coordinator = self.execute(
            quantity="000000000000",
            raw_currency=OFFICIAL_FIXED_WIDTH_BLANK,
        )
        canonical = self.store.get_by_fact_id("position-fact-001")
        self.assertEqual(canonical.payload["quantity"], "0")
        self.assertEqual(canonical.payload["currency_code"], "KRW")
        self.assertEqual(canonical.payload["raw_currency_code"], "   ")
        self.assertEqual(
            result.snapshot.holding_snapshot.holding_observations,
            (),
        )
        self.assertEqual(result.change_class, "NO_CHANGE")
        self.assertEqual(coordinator.calls, [])
        self.assertIsNone(result.ingress)

    def test_no_change_does_not_wake_iro(self):
        first, _ = self.execute()
        second, coordinator = self.execute(
            suffix="002", prior=first.snapshot
        )
        self.assertEqual(second.change_class, "NO_CHANGE")
        self.assertIsNone(second.ingress)
        self.assertEqual(coordinator.calls, [])

    def test_exact_quantity_change_wakes_iro(self):
        first, _ = self.execute()
        second, coordinator = self.execute(
            suffix="002",
            quantity="000000000011",
            prior=first.snapshot,
        )
        self.assertEqual(second.change_class, "CHANGED")
        self.assertEqual(len(coordinator.calls), 1)

    def test_expired_cycle_fails_without_iro(self):
        coordinator = RecordingCoordinator()
        result, _ = self.execute(
            evaluation_time=COLLECTED + timedelta(minutes=6),
            coordinator=coordinator,
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertEqual(result.failure_code, "STALE_REQUIRED_FACT")
        self.assertEqual(coordinator.calls, [])
        self.assertIsNotNone(
            self.store.get_by_fact_id("position-fact-001")
        )

    def test_missing_freshness_policy_fails_before_collection(self):
        adapter = FakeAdapter(successful_outcome())
        with self.assertRaisesRegex(
            TypeError, "^freshness_max_age must be timedelta$"
        ):
            run_kb_portfolio_vertical_slice(
                adapter=adapter,
                collect_request=collect_request(),
                raw_fact_id="raw-fact-001",
                normalization_request=normalization_request(),
                fact_store=self.store,
                snapshot_producer=PortfolioSnapshotProducer(
                    self.store, lambda: COLLECTED
                ),
                snapshot_identity=ExplicitSnapshotIdentity(
                    "snapshot-001", "context-001", "portfolio-main"
                ),
                watchlist_memberships=(),
                policy=ExplicitVerticalSlicePolicy(None),
                run=run_model("snapshot-001"),
                prior_snapshot=None,
                ingress_id="ingress-001",
                coordinator=RecordingCoordinator(),
                iro_run_arguments={},
            )
        self.assertEqual(adapter.calls, [])

    def test_provider_outage_does_not_write_or_wake(self):
        signal = ExplicitProviderFailureSignal(
            "kb_open_api",
            COLLECTED,
            "PROVIDER_ERROR",
            None,
            "correlation-001",
        )
        adapter = FakeAdapter(
            ExplicitCollectOutcome("failure", None, signal)
        )
        coordinator = RecordingCoordinator()
        result = run_kb_portfolio_vertical_slice(
            adapter=adapter,
            collect_request=collect_request(),
            raw_fact_id="raw-fact-001",
            normalization_request=normalization_request(),
            fact_store=self.store,
            snapshot_producer=PortfolioSnapshotProducer(
                self.store, lambda: COLLECTED
            ),
            snapshot_identity=ExplicitSnapshotIdentity(
                "snapshot-001", "context-001", "portfolio-main"
            ),
            watchlist_memberships=(),
            policy=ExplicitVerticalSlicePolicy(timedelta(minutes=5)),
            run=run_model("snapshot-001"),
            prior_snapshot=None,
            ingress_id="ingress-001",
            coordinator=coordinator,
            iro_run_arguments={},
        )
        self.assertEqual(result.failure_code, "PROVIDER_UNAVAILABLE")
        self.assertEqual(self.store.list_by_source_class("broker_fact"), ())
        self.assertEqual(coordinator.calls, [])

    def test_duplicate_response_rejects_without_partial_positions(self):
        outcome = successful_outcome()
        outcome.envelope.payload["dataBody"]["Record1"].append(
            dict(outcome.envelope.payload["dataBody"]["Record1"][0])
        )
        with self.assertRaisesRegex(
            ValueError, "^duplicate canonical response identity$"
        ):
            run_kb_portfolio_vertical_slice(
                adapter=FakeAdapter(outcome),
                collect_request=collect_request(),
                raw_fact_id="raw-fact-001",
                normalization_request=normalization_request(),
                fact_store=self.store,
                snapshot_producer=PortfolioSnapshotProducer(
                    self.store, lambda: COLLECTED
                ),
                snapshot_identity=ExplicitSnapshotIdentity(
                    "snapshot-001", "context-001", "portfolio-main"
                ),
                watchlist_memberships=(),
                policy=ExplicitVerticalSlicePolicy(timedelta(minutes=5)),
                run=run_model("snapshot-001"),
                prior_snapshot=None,
                ingress_id="ingress-001",
                coordinator=RecordingCoordinator(),
                iro_run_arguments={},
            )
        self.assertIsNotNone(self.store.get_by_fact_id("raw-fact-001"))
        with self.assertRaisesRegex(ValueError, "^fact_id not found$"):
            self.store.get_by_fact_id("position-fact-001")

    def test_decimal_float_and_malformed_cycle_reject(self):
        for bad in (1.0, "NaN", "-1", " 1", "1e2"):
            with self.subTest(bad=bad):
                suffix = str(len(self.store.list_by_source_class("broker_fact")))
                outcome = successful_outcome(suffix)
                outcome.envelope.payload["dataBody"]["Record1"][0][
                    "hld_q"
                ] = bad
                with self.assertRaises((TypeError, ValueError)):
                    run_kb_portfolio_vertical_slice(
                        adapter=FakeAdapter(outcome),
                        collect_request=collect_request(suffix),
                        raw_fact_id=f"raw-fact-{suffix}",
                        normalization_request=normalization_request(suffix),
                        fact_store=self.store,
                        snapshot_producer=PortfolioSnapshotProducer(
                            self.store, lambda: COLLECTED
                        ),
                        snapshot_identity=ExplicitSnapshotIdentity(
                            f"snapshot-{suffix}",
                            f"context-{suffix}",
                            "portfolio-main",
                        ),
                        watchlist_memberships=(),
                        policy=ExplicitVerticalSlicePolicy(
                            timedelta(minutes=5)
                        ),
                        run=run_model(f"snapshot-{suffix}", suffix=suffix),
                        prior_snapshot=None,
                        ingress_id=f"ingress-{suffix}",
                        coordinator=RecordingCoordinator(),
                        iro_run_arguments={},
                    )

    def test_forged_snapshot_and_provenance_identity_rejected(self):
        result, _ = self.execute()
        forged = replace(result.ingress, portfolio_snapshot_id="forged")
        with self.assertRaisesRegex(
            ValueError, "^run snapshot identity mismatch$"
        ):
            validate_iro_ingress(
                forged,
                run=run_model("snapshot-001"),
                current_snapshot=result.snapshot,
                prior_snapshot=None,
                raw_record=self.store.get_by_fact_id("raw-fact-001"),
                normalized_records=(
                    self.store.get_by_fact_id("position-fact-001"),
                ),
            )
        forged = replace(
            result.ingress,
            snapshot_used_fact_ids=("raw-fact-001",),
        )
        with self.assertRaisesRegex(
            ValueError, "^snapshot facts must be normalized facts$"
        ):
            validate_iro_ingress(
                forged,
                run=run_model("snapshot-001"),
                current_snapshot=result.snapshot,
                prior_snapshot=None,
                raw_record=self.store.get_by_fact_id("raw-fact-001"),
                normalized_records=(
                    self.store.get_by_fact_id("position-fact-001"),
                ),
            )

    def test_forged_raw_provenance_rejected(self):
        result, _ = self.execute()
        forged = replace(result.ingress, raw_fact_id="forged")
        with self.assertRaisesRegex(
            ValueError, "^raw fact provenance mismatch$"
        ):
            validate_iro_ingress(
                forged,
                run=run_model("snapshot-001"),
                current_snapshot=result.snapshot,
                prior_snapshot=None,
                raw_record=self.store.get_by_fact_id("raw-fact-001"),
                normalized_records=(
                    self.store.get_by_fact_id("position-fact-001"),
                ),
            )

    def test_padded_krw_is_unsupported_nonblank(self):
        for index, padded in enumerate((" KRW", "KRW "), start=1):
            with self.subTest(padded=repr(padded)):
                suffix = f"pad{index}"
                with self.assertRaisesRegex(
                    ValueError,
                    "^unsupported SSQM2952 currency$",
                ):
                    self.execute(suffix=suffix, raw_currency=padded)
                with self.assertRaisesRegex(
                    ValueError, "^fact_id not found$"
                ):
                    self.store.get_by_fact_id(f"position-fact-{suffix}")

    def test_blank_currency_without_binding_fails_closed(self):
        outcome = successful_outcome(currency=OFFICIAL_FIXED_WIDTH_BLANK)
        empty_request = ExplicitKbNormalizationRequest(
            "raw-fact-001",
            "account-primary",
            (),
        )
        with self.assertRaisesRegex(
            ValueError,
            "^blank crncy_cd requires one explicit domestic binding$",
        ):
            run_kb_portfolio_vertical_slice(
                adapter=FakeAdapter(outcome),
                collect_request=collect_request(),
                raw_fact_id="raw-fact-001",
                normalization_request=empty_request,
                fact_store=self.store,
                snapshot_producer=PortfolioSnapshotProducer(
                    self.store, lambda: COLLECTED
                ),
                snapshot_identity=ExplicitSnapshotIdentity(
                    "snapshot-001", "context-001", "portfolio-main"
                ),
                watchlist_memberships=(),
                policy=ExplicitVerticalSlicePolicy(timedelta(minutes=5)),
                run=run_model("snapshot-001"),
                prior_snapshot=None,
                ingress_id="ingress-001",
                coordinator=RecordingCoordinator(),
                iro_run_arguments={},
            )
        raw = self.store.get_by_fact_id("raw-fact-001")
        self.assertEqual(
            raw.payload["dataBody"]["Record1"][0]["crncy_cd"],
            "   ",
        )
        with self.assertRaisesRegex(ValueError, "^fact_id not found$"):
            self.store.get_by_fact_id("position-fact-001")

    def test_exact_krw_still_requires_krw_binding(self):
        result, _ = self.execute(raw_currency="KRW", binding_currency="KRW")
        canonical = self.store.get_by_fact_id("position-fact-001")
        self.assertEqual(canonical.payload["raw_currency_code"], "KRW")
        self.assertEqual(canonical.payload["currency_code"], "KRW")
        self.assertEqual(result.result_kind, "success")




if __name__ == "__main__":
    unittest.main()
