from __future__ import annotations

import inspect
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch

from FactStore.models import ExplicitFactAppendRequest
from MarketEndpoint.validation import validate_explicit_market
from MarketInstrumentObservation.models import (
    ExplicitMarketInstrumentObservation,
)
from MarketInstrumentObservation.validation import (
    validate_explicit_market_instrument_observation,
)
from MarketSessionContext.validation import (
    validate_explicit_market_session_context,
)
from MarketSnapshot.models import ExplicitMarketSnapshot
from MarketSnapshot.validation import (
    validate_explicit_market_snapshot,
)
from MarketVenue.validation import validate_explicit_market_venue

from MarketSnapshotProducer.composition.compose import (
    project_bound_payload,
)
from MarketSnapshotProducer.models import (
    ExplicitMarketSnapshotProductionResult,
)
from MarketSnapshotProducer.policy.evaluate import (
    classify_retrieved_fact,
)
from MarketSnapshotProducer.production import (
    MarketSnapshotProducer,
)
from MarketSnapshotProducer.tests.builders import (
    APPENDED_AT,
    COLLECTED_AT,
    EVALUATION_TIME,
    exploding_clock,
    make_binding,
    make_criteria,
    make_envelope,
    make_freshness_policy,
    make_instrument,
    make_korea_profile,
    make_partial_policy,
    make_payload,
    make_producer,
    make_request,
    make_store,
    make_us_profile,
    seed_market_fact,
    utc_clock,
)


class ConstructorTests(unittest.TestCase):
    def test_fact_store_requires_exact_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "^fact_store must be FactStore$",
        ):
            MarketSnapshotProducer(object(), utc_clock())

    def test_utc_clock_must_be_callable(self):
        with self.assertRaisesRegex(
            TypeError,
            "^utc_clock must be callable$",
        ):
            MarketSnapshotProducer(make_store(), None)


class ProductionSuccessTests(unittest.TestCase):
    def test_success_emits_accepted_snapshot(self):
        store = make_store()
        record = seed_market_fact(store)
        producer = make_producer(store, exploding_clock())
        request = make_request()
        result = producer.produce(request)
        self.assertIs(
            type(result),
            ExplicitMarketSnapshotProductionResult,
        )
        self.assertEqual(result.result_kind, "success")
        self.assertIsNone(result.failure)
        self.assertEqual(result.omitted_instrument_ids, ())
        snapshot = result.snapshot
        self.assertIs(type(snapshot), ExplicitMarketSnapshot)
        self.assertIs(
            snapshot.market_snapshot_id,
            request.market_snapshot_id,
        )
        self.assertEqual(
            snapshot.market_snapshot_id,
            "snapshot-001",
        )
        context = snapshot.session_context
        self.assertIs(
            context.session_context_id,
            request.session_context_id,
        )
        self.assertEqual(context.market_id, "korea-market")
        self.assertEqual(context.venue_id, "korea-venue")
        self.assertEqual(
            context.session_profile_id,
            "korea-session-profile",
        )
        self.assertEqual(len(snapshot.instrument_observations), 1)
        observation = snapshot.instrument_observations[0]
        self.assertIs(
            type(observation),
            ExplicitMarketInstrumentObservation,
        )
        self.assertIs(
            observation.instrument,
            request.subject_bindings[0].instrument,
        )
        self.assertIs(observation.session_context, context)
        self.assertEqual(observation.last_price, Decimal("10.00"))
        self.assertEqual(observation.market_status, "open")
        self.assertIs(
            observation.provenance.fact_id,
            record.fact_id,
        )
        self.assertIs(
            observation.provenance.source_identity,
            record.provider_id,
        )
        self.assertEqual(
            observation.provenance.collected_at,
            record.collected_at.isoformat(),
        )
        self.assertNotEqual(
            observation.provenance.collected_at,
            APPENDED_AT.isoformat(),
        )

    def test_domain_validators_invoked_before_emission(self):
        store = make_store()
        seed_market_fact(store)
        producer = make_producer(store, exploding_clock())
        with (
            patch(
                "MarketSnapshotProducer.production"
                ".validate_explicit_market",
                wraps=validate_explicit_market,
            ) as market,
            patch(
                "MarketSnapshotProducer.production"
                ".validate_explicit_market_venue",
                wraps=validate_explicit_market_venue,
            ) as venue,
            patch(
                "MarketSnapshotProducer.production"
                ".validate_explicit_market_session_context",
                wraps=validate_explicit_market_session_context,
            ) as session,
            patch(
                "MarketSnapshotProducer.production"
                ".validate_explicit_market_instrument"
                "_observation",
                wraps=(
                    validate_explicit_market_instrument_observation
                ),
            ) as observation,
            patch(
                "MarketSnapshotProducer.production"
                ".validate_explicit_market_snapshot",
                wraps=validate_explicit_market_snapshot,
            ) as snapshot,
        ):
            result = producer.produce(make_request())
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(market.call_count, 1)
        self.assertEqual(venue.call_count, 1)
        self.assertEqual(session.call_count, 1)
        self.assertEqual(observation.call_count, 1)
        self.assertEqual(snapshot.call_count, 1)

    def test_last_price_from_str_is_finite_decimal(self):
        store = make_store()
        seed_market_fact(
            store,
            envelope=make_envelope(
                payload=make_payload(last_price="10.50")
            ),
        )
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(make_request())
        last_price = (
            result.snapshot.instrument_observations[0]
            .last_price
        )
        self.assertIs(type(last_price), Decimal)
        self.assertEqual(last_price, Decimal("10.50"))
        self.assertTrue(last_price.is_finite())

    def test_decimal_payload_value_is_same_object(self):
        price = Decimal("12.34")
        projected = project_bound_payload(
            {
                "last_price": price,
                "market_status": "open",
            },
            "last_price",
            "market_status",
        )
        self.assertIsNotNone(projected)
        self.assertIs(projected[0], price)

    def test_float_last_price_is_projection_failure(self):
        store = make_store()
        seed_market_fact(
            store,
            envelope=make_envelope(
                payload=make_payload(last_price=10.0)
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
        self.assertEqual(
            result.omitted_instrument_ids,
            ("instrument-001",),
        )

    def test_int_and_bool_last_price_are_rejected(self):
        for value in (10, True, None):
            with self.subTest(value=value):
                store = make_store()
                seed_market_fact(
                    store,
                    envelope=make_envelope(
                        envelope_id=f"envelope-{value!r}",
                        payload=make_payload(last_price=value),
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

    def test_market_status_is_closed_and_not_case_folded(self):
        store = make_store()
        seed_market_fact(
            store,
            envelope=make_envelope(
                payload=make_payload(market_status="OPEN")
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

    def test_unknown_status_is_accepted_vocabulary_member(self):
        store = make_store()
        seed_market_fact(
            store,
            envelope=make_envelope(
                payload=make_payload(market_status="unknown")
            ),
        )
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(make_request())
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(
            result.snapshot.instrument_observations[0]
            .market_status,
            "unknown",
        )

    def test_korea_and_us_profiles_succeed_separately(self):
        store = make_store()
        seed_market_fact(
            store,
            fact_id="korea-fact-001",
            envelope=make_envelope(
                envelope_id="korea-envelope-001",
                payload=make_payload(last_price="100"),
            ),
        )
        seed_market_fact(
            store,
            fact_id="us-fact-001",
            envelope=make_envelope(
                envelope_id="us-envelope-001",
                payload=make_payload(last_price="10.00"),
            ),
        )
        producer = make_producer(store, exploding_clock())
        korea = producer.produce(
            make_request(
                market_snapshot_id="korea-snapshot",
                session_context_id="korea-session",
                session_profile=make_korea_profile(),
                subject_bindings=(
                    make_binding(
                        instrument=make_instrument(
                            instrument_id="korea-instrument"
                        ),
                        fact_id="korea-fact-001",
                    ),
                ),
            )
        )
        us = producer.produce(
            make_request(
                market_snapshot_id="us-snapshot",
                session_context_id="us-session",
                session_profile=make_us_profile(),
                subject_bindings=(
                    make_binding(
                        instrument=make_instrument(
                            instrument_id="us-instrument"
                        ),
                        fact_id="us-fact-001",
                    ),
                ),
            )
        )
        self.assertEqual(korea.result_kind, "success")
        self.assertEqual(us.result_kind, "success")
        self.assertEqual(
            korea.snapshot.session_context.market_id,
            "korea-market",
        )
        self.assertEqual(
            us.snapshot.session_context.market_id,
            "us-market",
        )
        self.assertNotEqual(
            korea.snapshot.session_context.market_id,
            us.snapshot.session_context.market_id,
        )
        self.assertEqual(
            korea.snapshot.instrument_observations[0]
            .last_price,
            Decimal("100"),
        )
        self.assertEqual(
            us.snapshot.instrument_observations[0].last_price,
            Decimal("10.00"),
        )

    def test_empty_bindings_emit_empty_snapshot(self):
        producer = make_producer(
            make_store(),
            exploding_clock(),
        )
        result = producer.produce(
            make_request(subject_bindings=())
        )
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(
            result.snapshot.instrument_observations,
            (),
        )
        self.assertEqual(result.omitted_instrument_ids, ())
        self.assertIsNone(result.failure)

    def test_clock_unused_when_freshness_is_none(self):
        store = make_store()
        seed_market_fact(store)
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(make_request())
        self.assertEqual(result.result_kind, "success")

    def test_clock_never_becomes_collected_at(self):
        store = make_store()
        record = seed_market_fact(store)
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
        collected_at = (
            result.snapshot.instrument_observations[0]
            .provenance.collected_at
        )
        self.assertEqual(
            collected_at,
            record.collected_at.isoformat(),
        )
        self.assertNotEqual(
            collected_at,
            clock_time.isoformat(),
        )


class ProductionFailureTests(unittest.TestCase):
    def test_missing_required_fact_fails_closed(self):
        producer = make_producer(
            make_store(),
            exploding_clock(),
        )
        result = producer.produce(make_request())
        self.assertEqual(result.result_kind, "failure")
        self.assertIsNone(result.snapshot)
        self.assertEqual(
            result.failure.failure_code,
            "MISSING_REQUIRED_FACT",
        )
        self.assertEqual(
            result.failure.omitted_instrument_ids,
            ("instrument-001",),
        )
        self.assertEqual(
            result.omitted_instrument_ids,
            ("instrument-001",),
        )

    def test_stale_required_fact_fails_closed(self):
        store = make_store()
        seed_market_fact(store)
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
        seed_market_fact(store)
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

    def test_broker_fact_is_ineligible(self):
        store = make_store()
        store.append(
            ExplicitFactAppendRequest(
                "broker-fact-001",
                make_envelope(
                    envelope_id="broker-envelope-001",
                    provider_id="kb_open_api",
                    source_class="broker_fact",
                    payload={"holding": "opaque-broker-body"},
                ),
                None,
            )
        )
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(
            make_request(
                subject_bindings=(
                    make_binding(fact_id="broker-fact-001"),
                )
            )
        )
        self.assertEqual(
            result.failure.failure_code,
            "INELIGIBLE_FACT",
        )
        self.assertIsNone(result.snapshot)

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
        seed_market_fact(store)
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

    def test_criteria_mismatch_on_collected_at_window(self):
        store = make_store()
        seed_market_fact(store)
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

    def test_blank_snapshot_id_is_rejected_without_generation(
        self,
    ):
        producer = make_producer(
            make_store(),
            exploding_clock(),
        )
        with self.assertRaisesRegex(
            ValueError,
            "^market_snapshot_id must not be blank$",
        ):
            producer.produce(
                make_request(market_snapshot_id=" ")
            )
        source = inspect.getsource(MarketSnapshotProducer)
        self.assertNotIn("uuid", source)
        self.assertNotIn("token_hex", source)
        self.assertNotIn("hashlib", source)

    def test_all_omitted_is_empty_required_emission(self):
        producer = make_producer(
            make_store(),
            exploding_clock(),
        )
        result = producer.produce(
            make_request(
                subject_bindings=(
                    make_binding(
                        instrument=make_instrument(
                            instrument_id="a"
                        ),
                        fact_id="missing-a",
                    ),
                    make_binding(
                        instrument=make_instrument(
                            instrument_id="b"
                        ),
                        fact_id="missing-b",
                    ),
                ),
                production_policy=make_partial_policy(),
            )
        )
        self.assertEqual(result.result_kind, "failure")
        self.assertIsNone(result.snapshot)
        self.assertEqual(
            result.failure.failure_code,
            "EMPTY_REQUIRED_EMISSION",
        )
        self.assertEqual(
            result.omitted_instrument_ids,
            ("a", "b"),
        )

    def test_authorized_partial_emission_omits_without_fill(
        self,
    ):
        store = make_store()
        seed_market_fact(
            store,
            fact_id="fact-present",
            envelope=make_envelope(
                envelope_id="envelope-present"
            ),
        )
        present = make_instrument(instrument_id="present")
        missing = make_instrument(instrument_id="missing")
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(
            make_request(
                subject_bindings=(
                    make_binding(
                        instrument=present,
                        fact_id="fact-present",
                    ),
                    make_binding(
                        instrument=missing,
                        fact_id="fact-missing",
                    ),
                ),
                production_policy=make_partial_policy(),
            )
        )
        self.assertEqual(result.result_kind, "success")
        self.assertIsNone(result.failure)
        self.assertEqual(
            result.omitted_instrument_ids,
            ("missing",),
        )
        observations = result.snapshot.instrument_observations
        self.assertEqual(len(observations), 1)
        self.assertIs(observations[0].instrument, present)
        self.assertEqual(
            observations[0].instrument.instrument_id,
            "present",
        )

    def test_store_exception_propagates_when_fail_closed(self):
        store = make_store()
        seed_market_fact(store)
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

    def test_store_exception_omits_when_partial_allowed(self):
        store = make_store()
        seed_market_fact(
            store,
            fact_id="fact-ok",
            envelope=make_envelope(envelope_id="envelope-ok"),
        )
        seed_market_fact(
            store,
            fact_id="fact-bad",
            envelope=make_envelope(envelope_id="envelope-bad"),
        )

        def verify(fact_id):
            if fact_id == "fact-bad":
                raise TypeError("integrity failure")
            return store.__class__.verify_integrity(
                store,
                fact_id,
            )

        producer = make_producer(store, exploding_clock())
        with patch.object(
            store,
            "verify_integrity",
            side_effect=verify,
        ):
            result = producer.produce(
                make_request(
                    subject_bindings=(
                        make_binding(
                            instrument=make_instrument(
                                instrument_id="ok"
                            ),
                            fact_id="fact-ok",
                        ),
                        make_binding(
                            instrument=make_instrument(
                                instrument_id="bad"
                            ),
                            fact_id="fact-bad",
                        ),
                    ),
                    production_policy=make_partial_policy(),
                )
            )
        self.assertEqual(result.result_kind, "success")
        self.assertEqual(
            result.omitted_instrument_ids,
            ("bad",),
        )
        self.assertEqual(
            len(result.snapshot.instrument_observations),
            1,
        )

    def test_market_validator_exception_is_unchanged(self):
        store = make_store()
        seed_market_fact(store)
        error = ValueError("market failure")
        producer = make_producer(store, exploding_clock())
        with patch(
            "MarketSnapshotProducer.production"
            ".validate_explicit_market",
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
                "^market_snapshot_id must not be blank$",
            ):
                producer.produce(
                    make_request(market_snapshot_id="")
                )

    def test_missing_fact_does_not_synthesize_price(self):
        result = make_producer(
            make_store(),
            exploding_clock(),
        ).produce(make_request())
        self.assertIsNone(result.snapshot)
        self.assertNotIn(
            "last_price",
            result.failure.__dataclass_fields__,
        )

    def test_observation_order_follows_caller_bindings(self):
        store = make_store()
        seed_market_fact(
            store,
            fact_id="fact-a",
            envelope=make_envelope(
                envelope_id="envelope-a",
                payload=make_payload(last_price="1"),
            ),
        )
        seed_market_fact(
            store,
            fact_id="fact-b",
            envelope=make_envelope(
                envelope_id="envelope-b",
                payload=make_payload(last_price="2"),
            ),
        )
        first = make_instrument(instrument_id="first")
        second = make_instrument(instrument_id="second")
        result = make_producer(
            store,
            exploding_clock(),
        ).produce(
            make_request(
                subject_bindings=(
                    make_binding(
                        instrument=first,
                        fact_id="fact-a",
                    ),
                    make_binding(
                        instrument=second,
                        fact_id="fact-b",
                    ),
                )
            )
        )
        observations = result.snapshot.instrument_observations
        self.assertIs(observations[0].instrument, first)
        self.assertIs(observations[1].instrument, second)
        self.assertEqual(
            observations[0].last_price,
            Decimal("1"),
        )
        self.assertEqual(
            observations[1].last_price,
            Decimal("2"),
        )


if __name__ == "__main__":
    unittest.main()
