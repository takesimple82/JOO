from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone, tzinfo

from MarketSnapshot.models import ExplicitMarketSnapshot
from ProviderGateway.validation import (
    validate_explicit_provider_payload_envelope,
)

from FactStore.models import ExplicitStoredFactRecord
from FactStore.storage import InMemoryAppendOnlyFactEngine
from FactStore.store import FactStore
from FactStore.tests.builders import (
    APPENDED_AT,
    COLLECTED_AT,
    make_broker_envelope,
    make_broker_request,
    make_diagnostics,
    make_envelope,
    make_failure,
    make_health,
    make_korea_market_envelope,
    make_request,
    make_store,
    make_stored_record,
    make_us_market_envelope,
    utc_clock,
)


class AppendSuccessTests(unittest.TestCase):
    def test_append_market_fact_success(self):
        store = make_store()
        envelope = make_envelope()
        request = make_request(envelope=envelope)
        record = store.append(request)
        self.assertIs(type(record), ExplicitStoredFactRecord)
        self.assertEqual(record.fact_id, "fact-001")
        self.assertIs(record.fact_id, request.fact_id)
        self.assertIs(record.envelope_id, envelope.envelope_id)
        self.assertIs(record.provider_id, envelope.provider_id)
        self.assertIs(record.source_class, envelope.source_class)
        self.assertEqual(record.source_class, "market_fact")
        self.assertIs(record.collected_at, envelope.collected_at)
        self.assertIs(record.appended_at, APPENDED_AT)
        self.assertIsNot(
            record.appended_at,
            record.collected_at,
        )
        self.assertNotEqual(
            record.appended_at,
            record.collected_at,
        )
        self.assertIs(record.status, envelope.status)
        self.assertEqual(record.status, "success")
        self.assertIs(record.payload, envelope.payload)
        self.assertIsNone(record.superseded_fact_id)
        self.assertIs(type(record.integrity_seal), str)
        self.assertNotEqual(record.integrity_seal, "")
        self.assertIsNone(store.verify_integrity(record.fact_id))

    def test_append_broker_fact_success(self):
        store = make_store()
        envelope = make_broker_envelope()
        self.assertIsNone(
            validate_explicit_provider_payload_envelope(
                envelope
            )
        )
        record = store.append(
            make_broker_request(envelope=envelope)
        )
        self.assertEqual(record.source_class, "broker_fact")
        self.assertEqual(record.provider_id, "kb_open_api")
        self.assertIs(record.collected_at, envelope.collected_at)
        self.assertIs(record.payload, envelope.payload)
        self.assertIs(record.appended_at, APPENDED_AT)

    def test_korea_and_us_market_facts_are_same_class(self):
        store = make_store()
        korea = store.append(
            make_request(
                fact_id="korea-fact-001",
                envelope=make_korea_market_envelope(),
            )
        )
        us = store.append(
            make_request(
                fact_id="us-fact-001",
                envelope=make_us_market_envelope(),
            )
        )
        self.assertEqual(korea.source_class, "market_fact")
        self.assertEqual(us.source_class, "market_fact")
        self.assertEqual(korea.source_class, us.source_class)
        listed = store.list_by_source_class("market_fact")
        self.assertEqual(listed, (korea, us))


class AppendRejectTests(unittest.TestCase):
    def test_rejects_research_ai(self):
        store = make_store()
        with self.assertRaisesRegex(
            ValueError,
            "^source_class must be one of "
            "ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES$",
        ):
            store.append(
                make_request(
                    envelope=make_envelope(
                        source_class="research_ai"
                    )
                )
            )
        self.assertEqual(
            store.list_by_source_class("research_ai"),
            (),
        )

    def test_rejects_failure_and_health_and_non_envelope(self):
        store = make_store()
        with self.assertRaisesRegex(
            ValueError,
            "^status must be success$",
        ):
            store.append(
                make_request(
                    envelope=make_envelope(
                        status="failure",
                        payload=None,
                        error_diagnostics=make_diagnostics(),
                    )
                )
            )
        with self.assertRaisesRegex(
            TypeError,
            "^request must be ExplicitFactAppendRequest$",
        ):
            store.append(make_failure())
        with self.assertRaisesRegex(
            TypeError,
            "^request must be ExplicitFactAppendRequest$",
        ):
            store.append(make_health())
        with self.assertRaisesRegex(
            TypeError,
            "^request must be ExplicitFactAppendRequest$",
        ):
            store.append({"last": "10.00"})
        with self.assertRaisesRegex(
            TypeError,
            "^envelope must be "
            "ExplicitProviderPayloadEnvelope$",
        ):
            store.append(
                make_request(envelope=make_health())
            )

    def test_rejects_market_snapshot_objects(self):
        store = make_store()
        snapshot = object.__new__(ExplicitMarketSnapshot)
        with self.assertRaisesRegex(
            TypeError,
            "^request must be ExplicitFactAppendRequest$",
        ):
            store.append(snapshot)
        with self.assertRaisesRegex(
            TypeError,
            "^envelope must be "
            "ExplicitProviderPayloadEnvelope$",
        ):
            store.append(
                make_request(envelope=snapshot)
            )

    def test_does_not_repair_source_class(self):
        store = make_store()
        with self.assertRaisesRegex(
            ValueError,
            "^source_class must be one of "
            "ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES$",
        ):
            store.append(
                make_request(
                    envelope=make_envelope(
                        source_class="research_ai"
                    )
                )
            )
        broker = store.append(make_broker_request())
        self.assertEqual(broker.source_class, "broker_fact")
        fetched = store.get_by_fact_id(broker.fact_id)
        self.assertEqual(fetched.source_class, "broker_fact")
        self.assertIs(fetched.source_class, broker.source_class)

    def test_rejects_blank_fact_id_and_does_not_generate(self):
        store = make_store()
        with self.assertRaisesRegex(
            ValueError,
            "^fact_id must not be blank$",
        ):
            store.append(make_request(fact_id=" "))
        with self.assertRaises(TypeError):
            store.append(
                make_request(fact_id=None)
            )
        self.assertEqual(
            store.list_by_source_class("market_fact"),
            (),
        )

    def test_rejects_already_accepted_fact_id_and_envelope_id(
        self,
    ):
        store = make_store()
        store.append(make_request())
        with self.assertRaisesRegex(
            ValueError,
            "^fact_id already accepted$",
        ):
            store.append(
                make_request(
                    envelope=make_envelope(
                        envelope_id="envelope-002"
                    )
                )
            )
        with self.assertRaisesRegex(
            ValueError,
            "^envelope_id already accepted$",
        ):
            store.append(
                make_request(
                    fact_id="fact-002",
                    envelope=make_envelope(),
                )
            )

    def test_rejects_forbidden_secret_keys(self):
        store = make_store()
        with self.assertRaisesRegex(
            ValueError,
            "^payload must not contain forbidden "
            "secret field names$",
        ):
            store.append(
                make_request(
                    envelope=make_envelope(
                        payload={"api_key": "x", "last": "1"}
                    )
                )
            )

    def test_rejects_naive_clock(self):
        store = FactStore(utc_clock(datetime(2026, 8, 13, 12, 0)))
        with self.assertRaisesRegex(
            ValueError,
            "^appended_at tzinfo must be "
            "datetime.timezone.utc$",
        ):
            store.append(make_request())


class HistoryTests(unittest.TestCase):
    def test_same_class_supersession_is_accepted(self):
        store = make_store()
        first = store.append(make_request())
        second = store.append(
            make_request(
                fact_id="fact-002",
                envelope=make_envelope(envelope_id="envelope-002"),
                superseded_fact_id=first.fact_id,
            )
        )
        self.assertEqual(second.superseded_fact_id, first.fact_id)
        self.assertIs(
            store.get_predecessor(second.fact_id),
            first,
        )
        self.assertIs(
            store.get_successor(first.fact_id),
            second,
        )
        self.assertIsNone(store.get_predecessor(first.fact_id))
        self.assertIsNone(store.get_successor(second.fact_id))
        self.assertEqual(
            store.get_by_fact_id(first.fact_id),
            first,
        )

    def test_broker_same_class_supersession_is_accepted(self):
        store = make_store()
        first = store.append(make_broker_request())
        second = store.append(
            make_broker_request(
                fact_id="broker-fact-002",
                envelope=make_broker_envelope(
                    envelope_id="broker-envelope-002"
                ),
                superseded_fact_id=first.fact_id,
            )
        )
        self.assertEqual(second.source_class, "broker_fact")
        self.assertIs(
            store.get_successor(first.fact_id),
            second,
        )

    def test_cross_class_supersession_is_rejected(self):
        store = make_store()
        broker = store.append(make_broker_request())
        market = store.append(make_request())
        with self.assertRaisesRegex(
            ValueError,
            "^supersession source_class must match$",
        ):
            store.append(
                make_request(
                    fact_id="fact-003",
                    envelope=make_envelope(
                        envelope_id="envelope-003"
                    ),
                    superseded_fact_id=broker.fact_id,
                )
            )
        with self.assertRaisesRegex(
            ValueError,
            "^supersession source_class must match$",
        ):
            store.append(
                make_broker_request(
                    fact_id="broker-fact-003",
                    envelope=make_broker_envelope(
                        envelope_id="broker-envelope-003"
                    ),
                    superseded_fact_id=market.fact_id,
                )
            )
        self.assertIsNone(store.get_successor(broker.fact_id))
        self.assertIsNone(store.get_successor(market.fact_id))

    def test_missing_and_duplicate_successor_are_rejected(self):
        store = make_store()
        first = store.append(make_request())
        with self.assertRaisesRegex(
            ValueError,
            "^superseded_fact_id not found$",
        ):
            store.append(
                make_request(
                    fact_id="fact-002",
                    envelope=make_envelope(
                        envelope_id="envelope-002"
                    ),
                    superseded_fact_id="missing-fact",
                )
            )
        store.append(
            make_request(
                fact_id="fact-002",
                envelope=make_envelope(envelope_id="envelope-002"),
                superseded_fact_id=first.fact_id,
            )
        )
        with self.assertRaisesRegex(
            ValueError,
            "^superseded_fact_id already superseded$",
        ):
            store.append(
                make_request(
                    fact_id="fact-003",
                    envelope=make_envelope(
                        envelope_id="envelope-003"
                    ),
                    superseded_fact_id=first.fact_id,
                )
            )


class RetrievalTests(unittest.TestCase):
    def test_get_by_fact_id_and_missing(self):
        store = make_store()
        record = store.append(make_request())
        self.assertIs(
            store.get_by_fact_id(record.fact_id),
            record,
        )
        with self.assertRaisesRegex(
            ValueError,
            "^fact_id not found$",
        ):
            store.get_by_fact_id("missing-fact")

    def test_list_by_source_identity_and_class(self):
        store = make_store()
        market = store.append(make_request())
        broker = store.append(make_broker_request())
        other_market = store.append(
            make_request(
                fact_id="fact-002",
                envelope=make_envelope(envelope_id="envelope-002"),
            )
        )
        self.assertEqual(
            store.list_by_source_identity("market-provider-001"),
            (market, other_market),
        )
        self.assertEqual(
            store.list_by_source_identity("kb_open_api"),
            (broker,),
        )
        self.assertEqual(
            store.list_by_source_identity("unknown-provider"),
            (),
        )
        self.assertEqual(
            store.list_by_source_class("market_fact"),
            (market, other_market),
        )
        self.assertEqual(
            store.list_by_source_class("broker_fact"),
            (broker,),
        )
        self.assertEqual(
            store.list_by_source_class("research_ai"),
            (),
        )

    def test_window_uses_collected_at_not_appended_at(self):
        early_collected = datetime(
            2026, 1, 1, 9, 0, tzinfo=timezone.utc
        )
        late_collected = datetime(
            2026, 6, 1, 9, 0, tzinfo=timezone.utc
        )
        store = make_store()
        early = store.append(
            make_request(
                fact_id="early-fact",
                envelope=make_envelope(
                    envelope_id="early-envelope",
                    collected_at=early_collected,
                ),
            )
        )
        late = store.append(
            make_request(
                fact_id="late-fact",
                envelope=make_envelope(
                    envelope_id="late-envelope",
                    collected_at=late_collected,
                ),
            )
        )
        window = store.list_by_collected_at_window(
            early_collected,
            early_collected,
        )
        self.assertEqual(window, (early,))
        self.assertNotIn(late, window)
        self.assertEqual(early.appended_at, APPENDED_AT)
        self.assertEqual(late.appended_at, APPENDED_AT)
        outside_append_window = store.list_by_collected_at_window(
            APPENDED_AT,
            APPENDED_AT,
        )
        self.assertEqual(outside_append_window, ())

    def test_retrieval_returns_stored_records_only(self):
        store = make_store()
        record = store.append(make_request())
        results = (
            store.get_by_fact_id(record.fact_id),
            *store.list_by_source_identity(record.provider_id),
            *store.list_by_source_class("market_fact"),
            *store.list_by_collected_at_window(
                record.collected_at,
                record.collected_at,
            ),
        )
        for item in results:
            self.assertIs(type(item), ExplicitStoredFactRecord)

    def test_source_class_not_repaired_on_read(self):
        store = make_store()
        broker = store.append(make_broker_request())
        market = store.append(make_request())
        self.assertEqual(
            store.get_by_fact_id(broker.fact_id).source_class,
            "broker_fact",
        )
        self.assertEqual(
            store.get_by_fact_id(market.fact_id).source_class,
            "market_fact",
        )


class IntegrityAndImmutabilityTests(unittest.TestCase):
    def test_stored_record_is_immutable_after_accept(self):
        store = make_store()
        record = store.append(make_request())
        from dataclasses import FrozenInstanceError

        with self.assertRaises(FrozenInstanceError):
            record.fact_id = "other"
        with self.assertRaises(FrozenInstanceError):
            record.source_class = "broker_fact"
        with self.assertRaises(FrozenInstanceError):
            record.integrity_seal = "other"
        with self.assertRaises(FrozenInstanceError):
            record.payload = {}

    def test_payload_mutation_fails_integrity_closed(self):
        store = make_store()
        record = store.append(make_request())
        original = dict(record.payload)
        record.payload["injected"] = "mutated"
        with self.assertRaisesRegex(
            ValueError,
            "^integrity_seal mismatch$",
        ):
            store.verify_integrity(record.fact_id)
        self.assertEqual(record.payload["injected"], "mutated")
        self.assertNotEqual(record.payload, original)
        fetched = store.get_by_fact_id(record.fact_id)
        self.assertIs(fetched, record)
        self.assertIn("injected", fetched.payload)

    def test_injected_bad_seal_fails_closed(self):
        engine = InMemoryAppendOnlyFactEngine()
        bad = make_stored_record(integrity_seal="bad-seal")
        engine.append(bad)
        store = FactStore(utc_clock(), engine)
        with self.assertRaisesRegex(
            ValueError,
            "^integrity_seal mismatch$",
        ):
            store.verify_integrity(bad.fact_id)
        self.assertEqual(
            store.get_by_fact_id(bad.fact_id).integrity_seal,
            "bad-seal",
        )
        self.assertEqual(
            store.get_by_fact_id(bad.fact_id).source_class,
            "market_fact",
        )


class ClockAndEngineTests(unittest.TestCase):
    def test_default_engine_is_in_memory(self):
        store = FactStore(utc_clock())
        record = store.append(make_request())
        self.assertEqual(
            store.get_by_fact_id(record.fact_id),
            record,
        )

    def test_offset_clock_is_rejected(self):
        class UtcLike(tzinfo):
            def utcoffset(self, dt):
                return timedelta(0)

            def dst(self, dt):
                return timedelta(0)

            def tzname(self, dt):
                return "UTC"

        for value in (
            datetime(2026, 8, 13, 12, 0),
            datetime(
                2026,
                8,
                13,
                12,
                0,
                tzinfo=timezone(timedelta(hours=9)),
            ),
            datetime(2026, 8, 13, 12, 0, tzinfo=UtcLike()),
        ):
            with self.subTest(value=value):
                store = FactStore(utc_clock(value))
                with self.assertRaisesRegex(
                    ValueError,
                    "^appended_at tzinfo must be "
                    "datetime.timezone.utc$",
                ):
                    store.append(make_request())


if __name__ == "__main__":
    unittest.main()
