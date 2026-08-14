from __future__ import annotations

import inspect
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch

from FactStore.models import ExplicitFactAppendRequest
from PortfolioHoldingObservation.models import (
    ExplicitPortfolioHoldingObservation,
)
from PortfolioHoldingObservation.validation import (
    validate_explicit_portfolio_holding_observation,
)
from PortfolioHoldingSnapshot.models import (
    ExplicitPortfolioHoldingSnapshot,
)
from PortfolioHoldingSnapshot.validation import (
    validate_explicit_portfolio_holding_snapshot,
)
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioObservationContext.validation import (
    validate_explicit_portfolio_observation_context,
)
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioSnapshot.validation import (
    validate_explicit_portfolio_snapshot,
)
from PortfolioWatchlistEntry.models import (
    ExplicitPortfolioWatchlistEntry,
)
from PortfolioWatchlistEntry.validation import (
    validate_explicit_portfolio_watchlist_entry,
)

from PortfolioSnapshotProducer.composition.compose import (
    project_bound_quantity,
)
from PortfolioSnapshotProducer.models import (
    ExplicitPortfolioSnapshotProductionResult,
)
from PortfolioSnapshotProducer.policy.evaluate import (
    classify_retrieved_fact,
)
from PortfolioSnapshotProducer.production import (
    PortfolioSnapshotProducer,
)
from PortfolioSnapshotProducer.tests.builders import (
    APPENDED_AT,
    COLLECTED_AT,
    EVALUATION_TIME,
    exploding_clock,
    make_binding,
    make_criteria,
    make_declaration,
    make_envelope,
    make_freshness_policy,
    make_payload,
    make_producer,
    make_request,
    make_store,
    seed_broker_fact,
    utc_clock,
)


class ConstructorTests(unittest.TestCase):
    def test_fact_store_requires_exact_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "^fact_store must be FactStore$",
        ):
            PortfolioSnapshotProducer(object(), utc_clock())

    def test_utc_clock_must_be_callable(self):
        with self.assertRaisesRegex(
            TypeError,
            "^utc_clock must be callable$",
        ):
            PortfolioSnapshotProducer(make_store(), None)


class ProductionSuccessTests(unittest.TestCase):
    def test_success_emits_accepted_snapshot(self):
        store = make_store()
        record = seed_broker_fact(store)
        producer = make_producer(store, exploding_clock())
        request = make_request()
        result = producer.produce(request)
        self.assertIs(
            type(result),
            ExplicitPortfolioSnapshotProductionResult,
        )
        self.assertEqual(result.result_kind, "success")
        self.assertIsNone(result.failure)
        self.assertIsNotNone(result.provenance)
        snapshot = result.snapshot
        self.assertIs(type(snapshot), ExplicitPortfolioSnapshot)
        self.assertIs(
            snapshot.portfolio_snapshot_id,
            request.portfolio_snapshot_id,
        )
        self.assertEqual(
            snapshot.portfolio_snapshot_id,
            "snapshot-001",
        )
        context = snapshot.observation_context
        self.assertIs(
            type(context),
            ExplicitPortfolioObservationContext,
        )
        self.assertIs(
            context.observation_context_id,
            request.observation_context_id,
        )
        self.assertIs(context.portfolio_id, request.portfolio_id)
        self.assertEqual(
            [field for field in context.__dataclass_fields__],
            ["observation_context_id", "portfolio_id"],
        )
        holding_snapshot = snapshot.holding_snapshot
        self.assertIs(
            type(holding_snapshot),
            ExplicitPortfolioHoldingSnapshot,
        )
        self.assertIs(
            holding_snapshot.observation_context,
            context,
        )
        self.assertEqual(len(holding_snapshot.holding_observations), 1)
        observation = holding_snapshot.holding_observations[0]
        self.assertIs(
            type(observation),
            ExplicitPortfolioHoldingObservation,
        )
        self.assertIs(observation.observation_context, context)
        self.assertEqual(
            observation.position.position_id,
            "position-001",
        )
        self.assertEqual(
            observation.position.membership.portfolio_subject_id,
            "subject-001",
        )
        self.assertEqual(
            observation.position.membership.portfolio_id,
            "portfolio-001",
        )
        self.assertIs(type(observation.quantity), Decimal)
        self.assertEqual(observation.quantity, Decimal("10.00"))
        self.assertTrue(observation.quantity.is_finite())
        self.assertEqual(snapshot.watchlist_entries, ())
        used = result.provenance.used_facts
        self.assertEqual(len(used), 1)
        self.assertIs(used[0].fact_id, record.fact_id)
        self.assertIs(used[0].collected_at, record.collected_at)
        self.assertIs(used[0].source_identity, record.provider_id)
        self.assertIsNot(used[0].collected_at, record.appended_at)
        self.assertNotEqual(used[0].collected_at, APPENDED_AT)

    def test_domain_validators_invoked_before_emission(self):
        store = make_store()
        seed_broker_fact(store)
        producer = make_producer(store, exploding_clock())
        with (
            patch(
                "PortfolioSnapshotProducer.production"
                ".validate_explicit_portfolio_observation"
                "_context",
                wraps=validate_explicit_portfolio_observation_context,
            ) as context,
            patch(
                "PortfolioSnapshotProducer.production"
                ".validate_explicit_portfolio_holding"
                "_observation",
                wraps=validate_explicit_portfolio_holding_observation,
            ) as observation,
            patch(
                "PortfolioSnapshotProducer.production"
                ".validate_explicit_portfolio_holding_snapshot",
                wraps=validate_explicit_portfolio_holding_snapshot,
            ) as holding,
            patch(
                "PortfolioSnapshotProducer.production"
                ".validate_explicit_portfolio_watchlist_entry",
                wraps=validate_explicit_portfolio_watchlist_entry,
            ) as watchlist,
            patch(
                "PortfolioSnapshotProducer.production"
                ".validate_explicit_portfolio_snapshot",
                wraps=validate_explicit_portfolio_snapshot,
            ) as snapshot,
        ):
            result = producer.produce(
                make_request(
                    watchlist_memberships=(make_declaration(),)
                )
            )
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(context.call_count, 1)
        self.assertEqual(observation.call_count, 1)
        self.assertEqual(holding.call_count, 1)
        self.assertEqual(watchlist.call_count, 1)
        self.assertEqual(snapshot.call_count, 1)

    def test_ordered_watchlist_preserves_caller_order(self):
        store = make_store()
        seed_broker_fact(store)
        first = make_declaration(portfolio_subject_id="watch-a")
        second = make_declaration(portfolio_subject_id="watch-b")
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(
            make_request(
                watchlist_memberships=(first, second)
            )
        )
        self.assertEqual(result.result_kind, "success")
        entries = result.snapshot.watchlist_entries
        self.assertEqual(len(entries), 2)
        self.assertIs(
            type(entries[0]),
            ExplicitPortfolioWatchlistEntry,
        )
        self.assertIs(
            entries[0].membership.portfolio_subject_id,
            first.portfolio_subject_id,
        )
        self.assertIs(
            entries[1].membership.portfolio_subject_id,
            second.portfolio_subject_id,
        )
        self.assertEqual(
            entries[0].membership.portfolio_id,
            "portfolio-001",
        )

    def test_empty_holdings_emit_empty_holding_snapshot(self):
        producer = make_producer(
            make_store(),
            exploding_clock(),
        )
        result = producer.produce(
            make_request(
                holding_fact_bindings=(),
                watchlist_memberships=(make_declaration(),),
            )
        )
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(
            result.snapshot.holding_snapshot.holding_observations,
            (),
        )
        self.assertEqual(len(result.snapshot.watchlist_entries), 1)
        self.assertEqual(result.provenance.used_facts, ())
        self.assertIsNone(result.failure)

    def test_empty_watchlist_emits_empty_watchlist(self):
        store = make_store()
        seed_broker_fact(store)
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(make_request(watchlist_memberships=()))
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(result.snapshot.watchlist_entries, ())
        self.assertEqual(
            len(result.snapshot.holding_snapshot.holding_observations),
            1,
        )

    def test_combined_empty_holdings_and_watchlist_is_valid(self):
        producer = make_producer(
            make_store(),
            exploding_clock(),
        )
        result = producer.produce(
            make_request(
                holding_fact_bindings=(),
                watchlist_memberships=(),
            )
        )
        self.assertEqual(result.result_kind, "success")
        self.assertIsNone(result.failure)
        self.assertEqual(
            result.snapshot.holding_snapshot.holding_observations,
            (),
        )
        self.assertEqual(result.snapshot.watchlist_entries, ())
        self.assertEqual(result.provenance.used_facts, ())

    def test_quantity_from_str_is_finite_decimal(self):
        store = make_store()
        seed_broker_fact(
            store,
            envelope=make_envelope(
                payload=make_payload(quantity="10.50")
            ),
        )
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(make_request())
        quantity = (
            result.snapshot.holding_snapshot
            .holding_observations[0]
            .quantity
        )
        self.assertIs(type(quantity), Decimal)
        self.assertEqual(quantity, Decimal("10.50"))
        self.assertTrue(quantity.is_finite())
        self.assertEqual(
            quantity.as_tuple(),
            Decimal("10.50").as_tuple(),
        )

    def test_decimal_payload_value_is_same_object(self):
        quantity = Decimal("10.00")
        projected = project_bound_quantity(
            {"quantity": quantity},
            "quantity",
        )
        self.assertIs(projected, quantity)
        self.assertEqual(
            projected.as_tuple(),
            quantity.as_tuple(),
        )

    def test_zero_and_negative_finite_decimals_succeed(self):
        for text in ("0", "-1.50"):
            with self.subTest(text=text):
                store = make_store()
                seed_broker_fact(
                    store,
                    envelope=make_envelope(
                        envelope_id=f"envelope-{text}",
                        payload=make_payload(quantity=text),
                    ),
                )
                result = make_producer(
                    store,
                    exploding_clock(),
                ).produce(make_request())
                self.assertEqual(result.result_kind, "success")
                self.assertEqual(
                    result.snapshot.holding_snapshot
                    .holding_observations[0]
                    .quantity,
                    Decimal(text),
                )

    def test_same_fact_id_two_bindings_different_keys(self):
        store = make_store()
        seed_broker_fact(
            store,
            envelope=make_envelope(
                payload={
                    "quantity": "5",
                    "cash_amount": "1000.00",
                }
            ),
        )
        first = make_binding(
            fact_id="fact-001",
            position_id="position-001",
            portfolio_subject_id="subject-001",
            quantity_payload_key="quantity",
        )
        second = make_binding(
            fact_id="fact-001",
            position_id="position-002",
            portfolio_subject_id="subject-002",
            quantity_payload_key="cash_amount",
        )
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(
            make_request(holding_fact_bindings=(first, second))
        )
        self.assertEqual(result.result_kind, "success")
        observations = (
            result.snapshot.holding_snapshot.holding_observations
        )
        self.assertEqual(len(observations), 2)
        self.assertEqual(observations[0].quantity, Decimal("5"))
        self.assertEqual(
            observations[1].quantity,
            Decimal("1000.00"),
        )
        self.assertEqual(len(result.provenance.used_facts), 2)
        self.assertIs(
            result.provenance.used_facts[0].fact_id,
            result.provenance.used_facts[1].fact_id,
        )

    def test_observation_order_follows_caller_bindings(self):
        store = make_store()
        seed_broker_fact(
            store,
            fact_id="fact-a",
            envelope=make_envelope(
                envelope_id="envelope-a",
                payload=make_payload(quantity="1"),
            ),
        )
        seed_broker_fact(
            store,
            fact_id="fact-b",
            envelope=make_envelope(
                envelope_id="envelope-b",
                payload=make_payload(quantity="2"),
            ),
        )
        first = make_binding(
            fact_id="fact-a",
            position_id="position-a",
            portfolio_subject_id="subject-a",
        )
        second = make_binding(
            fact_id="fact-b",
            position_id="position-b",
            portfolio_subject_id="subject-b",
        )
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(
            make_request(holding_fact_bindings=(first, second))
        )
        observations = (
            result.snapshot.holding_snapshot.holding_observations
        )
        self.assertEqual(
            observations[0].position.position_id,
            "position-a",
        )
        self.assertEqual(
            observations[1].position.position_id,
            "position-b",
        )
        self.assertEqual(observations[0].quantity, Decimal("1"))
        self.assertEqual(observations[1].quantity, Decimal("2"))

    def test_clock_unused_when_freshness_is_none(self):
        store = make_store()
        seed_broker_fact(store)
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(make_request())
        self.assertEqual(result.result_kind, "success")

    def test_clock_never_becomes_collected_at(self):
        store = make_store()
        record = seed_broker_fact(store)
        clock_time = datetime(2099, 1, 1, tzinfo=timezone.utc)
        result = make_producer(
            store,
            utc_clock(clock_time),
        ).produce(
            make_request(
                production_policy=make_freshness_policy(
                    timedelta(days=36500)
                )
            )
        )
        self.assertEqual(result.result_kind, "success")
        collected_at = result.provenance.used_facts[0].collected_at
        self.assertIs(collected_at, record.collected_at)
        self.assertNotEqual(collected_at, clock_time)

    def test_appended_at_is_not_freshness_or_provenance_time(
        self,
    ):
        store = make_store()
        record = seed_broker_fact(store)
        result = make_producer(
            store,
            utc_clock(EVALUATION_TIME),
        ).produce(
            make_request(
                production_policy=make_freshness_policy(
                    timedelta(hours=1)
                )
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertEqual(
            result.failure.failure_code,
            "STALE_REQUIRED_FACT",
        )
        self.assertIsNone(result.snapshot)
        age_from_appended = EVALUATION_TIME - APPENDED_AT
        self.assertLess(age_from_appended, timedelta(hours=1))
        self.assertNotEqual(record.collected_at, record.appended_at)


class ProductionFailureTests(unittest.TestCase):
    def test_missing_required_fact_fails_closed(self):
        producer = make_producer(
            make_store(),
            exploding_clock(),
        )
        binding = make_binding()
        result = producer.produce(
            make_request(holding_fact_bindings=(binding,))
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIsNone(result.snapshot)
        self.assertIsNone(result.provenance)
        self.assertEqual(
            result.failure.failure_code,
            "MISSING_REQUIRED_FACT",
        )
        self.assertIs(result.failure.failed_fact_id, binding.fact_id)
        self.assertIs(
            result.failure.failed_position_id,
            binding.position_id,
        )

    def test_no_discovery_via_list_by_source_class(self):
        store = make_store()
        seed_broker_fact(store)
        producer = make_producer(store, exploding_clock())
        with patch.object(
            store,
            "list_by_source_class",
            side_effect=AssertionError("discovery"),
        ):
            result = producer.produce(
                make_request(
                    holding_fact_bindings=(
                        make_binding(fact_id="unnamed-fact"),
                    )
                )
            )
        self.assertEqual(
            result.failure.failure_code,
            "MISSING_REQUIRED_FACT",
        )
        self.assertIsNone(result.snapshot)

    def test_stale_required_fact_fails_closed(self):
        store = make_store()
        seed_broker_fact(store)
        result = make_producer(
            store,
            utc_clock(EVALUATION_TIME),
        ).produce(
            make_request(
                production_policy=make_freshness_policy(
                    timedelta(hours=1)
                )
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIsNone(result.snapshot)
        self.assertEqual(
            result.failure.failure_code,
            "STALE_REQUIRED_FACT",
        )

    def test_equal_freshness_age_is_not_stale(self):
        store = make_store()
        seed_broker_fact(store)
        age = EVALUATION_TIME - COLLECTED_AT
        result = make_producer(
            store,
            utc_clock(EVALUATION_TIME),
        ).produce(
            make_request(
                production_policy=make_freshness_policy(age)
            )
        )
        self.assertEqual(result.result_kind, "success")

    def test_market_fact_is_ineligible(self):
        store = make_store()
        store.append(
            ExplicitFactAppendRequest(
                "market-fact-001",
                make_envelope(
                    envelope_id="market-envelope-001",
                    provider_id="market-provider-001",
                    source_class="market_fact",
                    payload={"quantity": "10.00"},
                ),
                None,
            )
        )
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(
            make_request(
                holding_fact_bindings=(
                    make_binding(fact_id="market-fact-001"),
                )
            )
        )
        self.assertEqual(
            result.failure.failure_code,
            "INELIGIBLE_FACT",
        )
        self.assertIsNone(result.snapshot)

    def test_non_success_record_is_ineligible(self):
        record = type("Record", (), {})()
        record.source_class = "broker_fact"
        record.status = "provider_error"
        record.provider_id = "kb_open_api"
        record.collected_at = COLLECTED_AT
        self.assertEqual(
            classify_retrieved_fact(
                record,
                make_criteria(),
                None,
                None,
            ),
            "INELIGIBLE_FACT",
        )

    def test_research_ai_is_ineligible_composition_source(self):
        record = type("Record", (), {})()
        record.source_class = "research_ai"
        record.status = "success"
        record.provider_id = "research-provider"
        record.collected_at = COLLECTED_AT
        self.assertEqual(
            classify_retrieved_fact(
                record,
                make_criteria(),
                None,
                None,
            ),
            "INELIGIBLE_FACT",
        )

    def test_criteria_mismatch_on_source_identity(self):
        store = make_store()
        seed_broker_fact(store)
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(
            make_request(
                fact_selection=make_criteria(
                    required_source_identity="other-provider"
                )
            )
        )
        self.assertEqual(
            result.failure.failure_code,
            "CRITERIA_MISMATCH",
        )
        self.assertIsNone(result.snapshot)

    def test_criteria_mismatch_on_collected_at_window(self):
        store = make_store()
        seed_broker_fact(store)
        start = datetime(2026, 6, 1, tzinfo=timezone.utc)
        end = datetime(2026, 6, 30, tzinfo=timezone.utc)
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(
            make_request(
                fact_selection=make_criteria(
                    collected_at_start=start,
                    collected_at_end=end,
                )
            )
        )
        self.assertEqual(
            result.failure.failure_code,
            "CRITERIA_MISMATCH",
        )

    def test_float_quantity_is_projection_failure(self):
        store = make_store()
        seed_broker_fact(
            store,
            envelope=make_envelope(
                payload=make_payload(quantity=10.0)
            ),
        )
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(make_request())
        self.assertEqual(result.result_kind, "failure")
        self.assertIsNone(result.snapshot)
        self.assertEqual(
            result.failure.failure_code,
            "PROJECTION_FAILURE",
        )

    def test_int_bool_none_missing_key_are_rejected(self):
        cases = (
            ("int", make_payload(quantity=10)),
            ("bool", make_payload(quantity=True)),
            ("none", make_payload(quantity=None)),
            ("missing", {"other": "10.00"}),
        )
        for label, payload in cases:
            with self.subTest(label=label):
                store = make_store()
                seed_broker_fact(
                    store,
                    envelope=make_envelope(
                        envelope_id=f"envelope-{label}",
                        payload=payload,
                    ),
                )
                result = make_producer(
                    store,
                    exploding_clock(),
                ).produce(make_request())
                self.assertEqual(
                    result.failure.failure_code,
                    "PROJECTION_FAILURE",
                )
                self.assertIsNone(result.snapshot)

    def test_non_dict_payload_is_projection_failure(self):
        self.assertIsNone(
            project_bound_quantity(["10.00"], "quantity")
        )
        self.assertIsNone(
            project_bound_quantity("10.00", "quantity")
        )

    def test_non_finite_decimal_is_projection_failure(self):
        for value in (
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
            "NaN",
            "Infinity",
        ):
            with self.subTest(value=value):
                self.assertIsNone(
                    project_bound_quantity(
                        {"quantity": value},
                        "quantity",
                    )
                )

    def test_first_failure_wins_and_does_not_emit_partial(self):
        store = make_store()
        seed_broker_fact(
            store,
            fact_id="fact-second",
            envelope=make_envelope(
                envelope_id="envelope-second",
                payload=make_payload(quantity="2"),
            ),
        )
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(
            make_request(
                holding_fact_bindings=(
                    make_binding(
                        fact_id="missing-first",
                        position_id="position-first",
                    ),
                    make_binding(
                        fact_id="fact-second",
                        position_id="position-second",
                        portfolio_subject_id="subject-second",
                    ),
                )
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIsNone(result.snapshot)
        self.assertEqual(
            result.failure.failure_code,
            "MISSING_REQUIRED_FACT",
        )
        self.assertEqual(
            result.failure.failed_fact_id,
            "missing-first",
        )

    def test_blank_snapshot_id_is_rejected_without_generation(
        self,
    ):
        producer = make_producer(
            make_store(),
            exploding_clock(),
        )
        with self.assertRaisesRegex(
            ValueError,
            "^portfolio_snapshot_id must not be blank$",
        ):
            producer.produce(
                make_request(portfolio_snapshot_id=" ")
            )
        source = inspect.getsource(PortfolioSnapshotProducer)
        self.assertNotIn("uuid", source)
        self.assertNotIn("token_hex", source)
        self.assertNotIn("hashlib", source)

    def test_store_exception_propagates_unchanged(self):
        store = make_store()
        seed_broker_fact(store)
        error = TypeError("integrity failure")
        producer = make_producer(store, exploding_clock())
        with patch.object(
            store,
            "verify_integrity",
            side_effect=error,
        ):
            with self.assertRaises(TypeError) as caught:
                producer.produce(make_request())
            self.assertIs(caught.exception, error)

    def test_non_missing_store_value_error_propagates(self):
        store = make_store()
        seed_broker_fact(store)
        error = ValueError("integrity_seal mismatch")
        producer = make_producer(store, exploding_clock())
        with patch.object(
            store,
            "verify_integrity",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                producer.produce(make_request())
            self.assertIs(caught.exception, error)

    def test_portfolio_validator_exception_is_unchanged(self):
        store = make_store()
        seed_broker_fact(store)
        error = ValueError("snapshot failure")
        producer = make_producer(store, exploding_clock())
        with patch(
            "PortfolioSnapshotProducer.production"
            ".validate_explicit_portfolio_snapshot",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                producer.produce(make_request())
            self.assertIs(caught.exception, error)

    def test_invalid_request_does_not_touch_store(self):
        store = make_store()
        producer = make_producer(store, exploding_clock())
        with patch.object(
            store,
            "get_by_fact_id",
            side_effect=AssertionError("store touched"),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "^portfolio_snapshot_id must not be blank$",
            ):
                producer.produce(
                    make_request(portfolio_snapshot_id="")
                )

    def test_missing_fact_does_not_synthesize_holding(self):
        result = make_producer(
            make_store(),
            exploding_clock(),
        ).produce(make_request())
        self.assertIsNone(result.snapshot)
        self.assertNotIn(
            "quantity",
            result.failure.__dataclass_fields__,
        )

    def test_emitted_snapshot_has_no_valuation_or_cash_fields(
        self,
    ):
        store = make_store()
        seed_broker_fact(store)
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(make_request())
        snapshot = result.snapshot
        names = list(snapshot.__dataclass_fields__)
        self.assertEqual(
            names,
            [
                "portfolio_snapshot_id",
                "observation_context",
                "holding_snapshot",
                "watchlist_entries",
            ],
        )
        for forbidden in (
            "nav",
            "pnl",
            "price",
            "cash",
            "balances",
            "account_state",
            "timestamp",
            "collected_at",
        ):
            self.assertNotIn(forbidden, names)


if __name__ == "__main__":
    unittest.main()
