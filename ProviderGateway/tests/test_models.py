from __future__ import annotations

import unittest
from dataclasses import (
    FrozenInstanceError,
    MISSING,
    fields,
    is_dataclass,
)
from datetime import datetime, timezone

from ProviderGateway.models import (
    AVAILABILITY_VALUES,
    ENVELOPE_STATUS_VALUES,
    FAILURE_CLASS_VALUES,
    RESERVED_KB_OPEN_API_PROVIDER_ID,
    SOURCE_CLASS_VALUES,
    ExplicitCollectOutcome,
    ExplicitCollectRequest,
    ExplicitErrorDiagnostics,
    ExplicitMarketAdapterBinding,
    ExplicitMarketParameterProfile,
    ExplicitProviderFailureSignal,
    ExplicitProviderHealthSnapshot,
    ExplicitProviderPayloadEnvelope,
)
from ProviderGateway.tests.builders import (
    FIXED_CLOCK,
    make_binding,
    make_diagnostics,
    make_envelope,
    make_failure,
    make_health,
    make_profile,
    make_request,
)


class ModelContractTests(unittest.TestCase):
    def test_closed_vocabularies_are_exact(self):
        self.assertEqual(
            SOURCE_CLASS_VALUES,
            ("broker_fact", "market_fact", "research_ai"),
        )
        self.assertEqual(
            ENVELOPE_STATUS_VALUES,
            ("success", "failure"),
        )
        self.assertEqual(
            AVAILABILITY_VALUES,
            ("available", "degraded", "unavailable"),
        )
        self.assertEqual(
            FAILURE_CLASS_VALUES,
            (
                "AUTH_FAILURE",
                "TRANSPORT_FAILURE",
                "PROVIDER_ERROR",
                "UNAVAILABLE",
                "RATE_LIMITED",
                "VALIDATION_FAILURE",
            ),
        )
        self.assertEqual(
            RESERVED_KB_OPEN_API_PROVIDER_ID,
            "kb_open_api",
        )

    def test_envelope_field_contract(self):
        self._assert_frozen_model(
            ExplicitProviderPayloadEnvelope,
            [
                "envelope_id",
                "provider_id",
                "source_class",
                "collected_at",
                "status",
                "payload",
                "error_diagnostics",
                "request_correlation_id",
            ],
            {
                "envelope_id": "str",
                "provider_id": "str",
                "source_class": "str",
                "collected_at": "datetime",
                "status": "str",
                "payload": "dict | None",
                "error_diagnostics": (
                    "ExplicitErrorDiagnostics | None"
                ),
                "request_correlation_id": "str | None",
            },
        )

    def test_diagnostics_field_contract(self):
        self._assert_frozen_model(
            ExplicitErrorDiagnostics,
            ["failure_class", "detail"],
            {
                "failure_class": "str",
                "detail": "str | None",
            },
        )

    def test_health_field_contract(self):
        self._assert_frozen_model(
            ExplicitProviderHealthSnapshot,
            [
                "provider_id",
                "observed_at",
                "availability",
                "detail",
            ],
            {
                "provider_id": "str",
                "observed_at": "datetime",
                "availability": "str",
                "detail": "str | None",
            },
        )

    def test_failure_field_contract(self):
        self._assert_frozen_model(
            ExplicitProviderFailureSignal,
            [
                "provider_id",
                "observed_at",
                "failure_class",
                "detail",
                "request_correlation_id",
            ],
            {
                "provider_id": "str",
                "observed_at": "datetime",
                "failure_class": "str",
                "detail": "str | None",
                "request_correlation_id": "str | None",
            },
        )

    def test_profile_field_contract(self):
        self._assert_frozen_model(
            ExplicitMarketParameterProfile,
            [
                "profile_id",
                "venue_target",
                "session_selector",
                "timezone_selector",
                "calendar_selector",
                "request_set",
            ],
            {
                "profile_id": "str",
                "venue_target": "str",
                "session_selector": "str | None",
                "timezone_selector": "str | None",
                "calendar_selector": "str | None",
                "request_set": "tuple[str, ...]",
            },
        )

    def test_binding_field_contract(self):
        self._assert_frozen_model(
            ExplicitMarketAdapterBinding,
            [
                "provider_id",
                "credential_ref",
                "parameter_profile",
            ],
            {
                "provider_id": "str",
                "credential_ref": "str",
                "parameter_profile": (
                    "ExplicitMarketParameterProfile"
                ),
            },
        )

    def test_request_field_contract(self):
        self._assert_frozen_model(
            ExplicitCollectRequest,
            [
                "envelope_id",
                "request_correlation_id",
                "binding",
            ],
            {
                "envelope_id": "str",
                "request_correlation_id": "str | None",
                "binding": "ExplicitMarketAdapterBinding",
            },
        )

    def test_outcome_field_contract(self):
        self._assert_frozen_model(
            ExplicitCollectOutcome,
            ["result_kind", "envelope", "failure"],
            {
                "result_kind": "str",
                "envelope": (
                    "ExplicitProviderPayloadEnvelope | None"
                ),
                "failure": (
                    "ExplicitProviderFailureSignal | None"
                ),
            },
        )

    def test_envelope_is_frozen_and_equality_structural(self):
        first = make_envelope()
        same = make_envelope()
        different = make_envelope(envelope_id="envelope-002")
        self.assertEqual(first, same)
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.envelope_id = "replacement"
        with self.assertRaises(FrozenInstanceError):
            first.payload = {}
        with self.assertRaises(FrozenInstanceError):
            first.source_class = "broker_fact"

    def test_hashable_records_without_payload_dict(self):
        self.assertEqual(
            hash(make_diagnostics()),
            hash(make_diagnostics()),
        )
        self.assertEqual(
            hash(make_health()),
            hash(make_health()),
        )
        self.assertEqual(
            hash(make_failure()),
            hash(make_failure()),
        )
        self.assertEqual(
            hash(make_profile()),
            hash(make_profile()),
        )
        self.assertEqual(
            hash(make_binding()),
            hash(make_binding()),
        )
        self.assertEqual(
            hash(make_request()),
            hash(make_request()),
        )

    def test_models_do_not_generate_envelope_id(self):
        supplied = " caller-envelope-001 "
        envelope = make_envelope(envelope_id=supplied)
        self.assertIs(envelope.envelope_id, supplied)
        self.assertEqual(
            envelope.envelope_id,
            " caller-envelope-001 ",
        )

    def test_collected_at_is_not_a_request_field(self):
        names = [
            field.name
            for field in fields(ExplicitCollectRequest)
        ]
        self.assertNotIn("collected_at", names)
        self.assertEqual(
            names,
            [
                "envelope_id",
                "request_correlation_id",
                "binding",
            ],
        )

    def test_no_defaults_on_public_models(self):
        for model in (
            ExplicitErrorDiagnostics,
            ExplicitProviderPayloadEnvelope,
            ExplicitProviderHealthSnapshot,
            ExplicitProviderFailureSignal,
            ExplicitMarketParameterProfile,
            ExplicitMarketAdapterBinding,
            ExplicitCollectRequest,
            ExplicitCollectOutcome,
        ):
            for field in fields(model):
                self.assertIs(field.default, MISSING)
                self.assertIs(field.default_factory, MISSING)

    def test_unknown_constructor_fields_fail(self):
        with self.assertRaises(TypeError):
            ExplicitProviderPayloadEnvelope(
                "envelope-001",
                "market-provider-001",
                "market_fact",
                FIXED_CLOCK,
                "success",
                {},
                None,
                None,
                extra="no",
            )

    def _assert_frozen_model(
        self,
        model,
        field_names,
        annotations,
    ):
        self.assertTrue(is_dataclass(model))
        self.assertTrue(model.__dataclass_params__.frozen)
        model_fields = fields(model)
        self.assertEqual(
            [field.name for field in model_fields],
            field_names,
        )
        self.assertEqual(model.__annotations__, annotations)
        self.assertNotIn("__post_init__", model.__dict__)
        self.assertNotIn("__slots__", model.__dict__)
        public_methods = {
            name
            for name, value in model.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())


if __name__ == "__main__":
    unittest.main()
