from __future__ import annotations

import unittest
from datetime import datetime, timezone

from ProviderGateway.adapters.market_api import MarketApiAdapter
from ProviderGateway.adapters.ports import (
    ExplicitHealthProbe,
    ExplicitTransportFailure,
    ExplicitTransportSuccess,
)
from ProviderGateway.provider_interface import ProviderInterface
from ProviderGateway.tests.builders import (
    FIXED_CLOCK,
    FakeTransport,
    credential_supplier,
    make_binding,
    make_korea_profile,
    make_request,
    make_us_profile,
    utc_now,
)


class MarketApiAdapterTests(unittest.TestCase):
    def test_adapter_implements_provider_interface(self):
        adapter = self._adapter()
        self.assertIsInstance(adapter, ProviderInterface)
        self.assertEqual(
            adapter.provider_id,
            "market-provider-001",
        )
        self.assertEqual(
            adapter.declared_source_class,
            "market_fact",
        )

    def test_success_path_tags_market_fact_explicitly(self):
        adapter = self._adapter()
        outcome = adapter.collect(make_request())
        self.assertEqual(outcome.result_kind, "success")
        self.assertIsNone(outcome.failure)
        envelope = outcome.envelope
        self.assertEqual(envelope.source_class, "market_fact")
        self.assertEqual(
            envelope.provider_id,
            "market-provider-001",
        )
        self.assertNotEqual(
            envelope.provider_id,
            "kb_open_api",
        )
        self.assertEqual(envelope.status, "success")
        self.assertEqual(envelope.envelope_id, "envelope-001")
        self.assertEqual(envelope.collected_at, FIXED_CLOCK)
        self.assertIs(envelope.collected_at.tzinfo, timezone.utc)
        self.assertIsInstance(envelope.payload, dict)
        self.assertIsNone(envelope.error_diagnostics)

    def test_caller_supplied_envelope_id_is_preserved(self):
        supplied = " caller-envelope-99 "
        adapter = self._adapter()
        outcome = adapter.collect(
            make_request(envelope_id=supplied)
        )
        self.assertEqual(
            outcome.envelope.envelope_id,
            supplied,
        )
        self.assertIs(
            outcome.envelope.envelope_id,
            supplied,
        )

    def test_exchange_clock_does_not_replace_collected_at(self):
        transport = FakeTransport(
            ExplicitTransportSuccess(
                {
                    "last": "10.00",
                    "exchange_time": (
                        "2020-01-01T00:00:00+09:00"
                    ),
                }
            )
        )
        adapter = self._adapter(transport=transport)
        outcome = adapter.collect(make_request())
        self.assertEqual(
            outcome.envelope.collected_at,
            FIXED_CLOCK,
        )
        self.assertEqual(
            outcome.envelope.payload["exchange_time"],
            "2020-01-01T00:00:00+09:00",
        )
        self.assertNotEqual(
            outcome.envelope.collected_at.isoformat(),
            outcome.envelope.payload["exchange_time"],
        )

    def test_venue_session_timezone_calendar_stay_opaque(self):
        transport = FakeTransport(
            ExplicitTransportSuccess(
                {
                    "last": "10.00",
                    "venue": "opaque-venue-code",
                    "session": "opaque-session",
                    "timezone": "opaque-timezone",
                    "calendar": "opaque-calendar",
                }
            )
        )
        adapter = self._adapter(transport=transport)
        payload = adapter.collect(make_request()).envelope.payload
        self.assertEqual(payload["venue"], "opaque-venue-code")
        self.assertEqual(payload["session"], "opaque-session")
        self.assertEqual(payload["timezone"], "opaque-timezone")
        self.assertEqual(payload["calendar"], "opaque-calendar")

    def test_korea_and_us_profiles_use_same_adapter_class(self):
        korea_binding = make_binding(
            provider_id="market-korea-001",
            parameter_profile=make_korea_profile(),
        )
        us_binding = make_binding(
            provider_id="market-us-001",
            parameter_profile=make_us_profile(),
        )
        korea_transport = FakeTransport(
            ExplicitTransportSuccess(
                {"last": "1", "venue": "korea-capable"}
            )
        )
        us_transport = FakeTransport(
            ExplicitTransportSuccess(
                {"last": "2", "venue": "us-capable"}
            )
        )
        korea_adapter = MarketApiAdapter(
            korea_binding,
            korea_transport,
            credential_supplier(),
            utc_now,
        )
        us_adapter = MarketApiAdapter(
            us_binding,
            us_transport,
            credential_supplier(),
            utc_now,
        )
        self.assertIs(type(korea_adapter), MarketApiAdapter)
        self.assertIs(type(us_adapter), MarketApiAdapter)
        self.assertIs(
            type(korea_adapter),
            type(us_adapter),
        )
        korea_outcome = korea_adapter.collect(
            make_request(binding=korea_binding)
        )
        us_outcome = us_adapter.collect(
            make_request(binding=us_binding)
        )
        self.assertEqual(korea_outcome.result_kind, "success")
        self.assertEqual(us_outcome.result_kind, "success")
        self.assertEqual(
            korea_outcome.envelope.payload["venue"],
            "korea-capable",
        )
        self.assertEqual(
            us_outcome.envelope.payload["venue"],
            "us-capable",
        )
        self.assertNotEqual(
            korea_outcome.envelope.envelope_id,
            None,
        )
        self.assertIsNot(
            korea_outcome.envelope,
            us_outcome.envelope,
        )

    def test_one_attempt_does_not_merge_profiles(self):
        transport = FakeTransport()
        adapter = self._adapter(transport=transport)
        first = adapter.collect(make_request())
        second = adapter.collect(
            make_request(envelope_id="envelope-002")
        )
        self.assertEqual(len(transport.reads), 2)
        self.assertEqual(first.result_kind, "success")
        self.assertEqual(second.result_kind, "success")
        self.assertNotEqual(
            first.envelope.envelope_id,
            second.envelope.envelope_id,
        )
        self.assertNotIn(
            "us-capable",
            first.envelope.payload,
        )
        self.assertNotIn(
            "korea-capable",
            first.envelope.payload,
        )

    def test_secrets_do_not_survive_mapping(self):
        secret = "super-secret-token-value"
        transport = FakeTransport(
            ExplicitTransportSuccess(
                {
                    "last": "10.00",
                    "token": secret,
                    "password": "hunter2",
                    "venue": "opaque-venue",
                }
            )
        )
        adapter = self._adapter(
            transport=transport,
            supplier=credential_supplier(secret),
        )
        outcome = adapter.collect(make_request())
        payload = outcome.envelope.payload
        self.assertEqual(payload["last"], "10.00")
        self.assertNotIn("token", payload)
        self.assertNotIn("password", payload)
        self.assertNotIn(secret, payload.values())
        self.assertNotIn("hunter2", payload.values())
        rendered = repr(payload)
        self.assertNotIn(secret, rendered)
        self.assertNotIn("hunter2", rendered)
        self.assertIsNone(outcome.envelope.error_diagnostics)

    def test_secret_value_in_body_is_not_success(self):
        secret = "super-secret-token-value"
        transport = FakeTransport(
            ExplicitTransportSuccess(
                {
                    "last": secret,
                    "venue": "opaque-venue",
                }
            )
        )
        adapter = self._adapter(
            transport=transport,
            supplier=credential_supplier(secret),
        )
        outcome = adapter.collect(make_request())
        self.assertEqual(outcome.result_kind, "failure")
        self.assertIsNone(outcome.envelope)
        self.assertEqual(
            outcome.failure.failure_class,
            "VALIDATION_FAILURE",
        )
        self.assertIsNone(outcome.failure.detail)
        self.assertNotIn(secret, repr(outcome.failure))

    def test_empty_wire_is_validation_failure(self):
        bodies = ({}, None, "not-a-dict", [])
        for body in bodies:
            with self.subTest(body=repr(body)):
                transport = FakeTransport(
                    ExplicitTransportSuccess({"last": "1"})
                )
                transport.result = ExplicitTransportSuccess(
                    body
                )
                adapter = self._adapter(transport=transport)
                outcome = adapter.collect(make_request())
                self.assertEqual(outcome.result_kind, "failure")
                self.assertIsNone(outcome.envelope)
                self.assertEqual(
                    outcome.failure.failure_class,
                    "VALIDATION_FAILURE",
                )
                self.assertNotIn(
                    "last",
                    repr(outcome.failure),
                )

    def test_transport_failures_are_not_synthetic_success(self):
        cases = (
            "AUTH_FAILURE",
            "TRANSPORT_FAILURE",
            "PROVIDER_ERROR",
            "UNAVAILABLE",
            "RATE_LIMITED",
        )
        for failure_class in cases:
            with self.subTest(failure_class=failure_class):
                transport = FakeTransport(
                    ExplicitTransportFailure(
                        failure_class,
                        "provider unavailable",
                    )
                )
                adapter = self._adapter(transport=transport)
                outcome = adapter.collect(make_request())
                self.assertEqual(outcome.result_kind, "failure")
                self.assertIsNone(outcome.envelope)
                self.assertEqual(
                    outcome.failure.failure_class,
                    failure_class,
                )
                self.assertNotIn(
                    "last",
                    repr(outcome.failure),
                )
                self.assertNotEqual(
                    outcome.failure.failure_class,
                    "success",
                )

    def test_raised_transport_is_transport_failure(self):
        transport = FakeTransport(
            raise_on_read=RuntimeError("socket closed")
        )
        adapter = self._adapter(transport=transport)
        outcome = adapter.collect(make_request())
        self.assertEqual(outcome.result_kind, "failure")
        self.assertIsNone(outcome.envelope)
        self.assertEqual(
            outcome.failure.failure_class,
            "TRANSPORT_FAILURE",
        )
        self.assertIsNone(outcome.failure.detail)

    def test_missing_credentials_are_auth_failure(self):
        def missing(_ref):
            return ""

        adapter = self._adapter(supplier=missing)
        outcome = adapter.collect(make_request())
        self.assertEqual(outcome.result_kind, "failure")
        self.assertIsNone(outcome.envelope)
        self.assertEqual(
            outcome.failure.failure_class,
            "AUTH_FAILURE",
        )

    def test_market_path_never_emits_broker_or_research(self):
        adapter = self._adapter()
        outcome = adapter.collect(make_request())
        self.assertEqual(
            outcome.envelope.source_class,
            "market_fact",
        )
        self.assertNotEqual(
            outcome.envelope.source_class,
            "broker_fact",
        )
        self.assertNotEqual(
            outcome.envelope.source_class,
            "research_ai",
        )
        self.assertEqual(
            adapter.declared_source_class,
            "market_fact",
        )

    def test_health_does_not_fabricate_an_envelope(self):
        transport = FakeTransport(
            probe=ExplicitHealthProbe("available", None)
        )
        adapter = self._adapter(transport=transport)
        snapshot = adapter.health()
        self.assertEqual(
            snapshot.provider_id,
            "market-provider-001",
        )
        self.assertEqual(snapshot.availability, "available")
        self.assertEqual(snapshot.observed_at, FIXED_CLOCK)
        self.assertFalse(hasattr(snapshot, "payload"))
        self.assertFalse(hasattr(snapshot, "source_class"))
        self.assertEqual(len(transport.reads), 0)
        self.assertEqual(len(transport.probes), 1)

    def test_health_degraded_and_unavailable(self):
        degraded = self._adapter(
            transport=FakeTransport(
                probe=ExplicitTransportFailure(
                    "RATE_LIMITED",
                    None,
                )
            )
        ).health()
        self.assertEqual(degraded.availability, "degraded")
        unavailable = self._adapter(
            transport=FakeTransport(
                probe=ExplicitTransportFailure(
                    "UNAVAILABLE",
                    None,
                )
            )
        ).health()
        self.assertEqual(
            unavailable.availability,
            "unavailable",
        )

    def test_reserved_kb_binding_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "^provider_id must not be kb_open_api$",
        ):
            MarketApiAdapter(
                make_binding(provider_id="kb_open_api"),
                FakeTransport(),
                credential_supplier(),
                utc_now,
            )

    def test_transport_receives_outbound_secret_only(self):
        secret = "outbound-secret"
        transport = FakeTransport()
        adapter = self._adapter(
            transport=transport,
            supplier=credential_supplier(secret),
        )
        outcome = adapter.collect(make_request())
        self.assertEqual(outcome.result_kind, "success")
        self.assertEqual(
            transport.reads[0]["credential"],
            secret,
        )
        self.assertNotIn(secret, outcome.envelope.payload)
        self.assertNotIn(
            "token",
            outcome.envelope.payload,
        )

    def _adapter(
        self,
        transport=None,
        supplier=None,
        clock=None,
        binding=None,
    ):
        if transport is None:
            transport = FakeTransport()
        if supplier is None:
            supplier = credential_supplier()
        if clock is None:
            clock = utc_now
        if binding is None:
            binding = make_binding()
        return MarketApiAdapter(
            binding,
            transport,
            supplier,
            clock,
        )


if __name__ == "__main__":
    unittest.main()
