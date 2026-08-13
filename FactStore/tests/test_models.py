from __future__ import annotations

import unittest
from dataclasses import (
    FrozenInstanceError,
    MISSING,
    fields,
    is_dataclass,
)
from ProviderGateway.models import (
    ENVELOPE_STATUS_VALUES as GATEWAY_ENVELOPE_STATUS_VALUES,
    SOURCE_CLASS_VALUES as GATEWAY_SOURCE_CLASS_VALUES,
)

from FactStore.models import (
    ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES,
    ENVELOPE_STATUS_VALUES,
    FORBIDDEN_PAYLOAD_SECRET_FIELD_NAMES,
    SOURCE_CLASS_VALUES,
    ExplicitFactAppendRequest,
    ExplicitStoredFactRecord,
)
from FactStore.tests.builders import (
    APPENDED_AT,
    COLLECTED_AT,
    make_envelope,
    make_request,
    make_stored_record,
)


class ModelContractTests(unittest.TestCase):
    def test_closed_vocabularies_are_exact(self):
        self.assertIs(
            SOURCE_CLASS_VALUES,
            GATEWAY_SOURCE_CLASS_VALUES,
        )
        self.assertIs(
            ENVELOPE_STATUS_VALUES,
            GATEWAY_ENVELOPE_STATUS_VALUES,
        )
        self.assertEqual(
            SOURCE_CLASS_VALUES,
            ("broker_fact", "market_fact", "research_ai"),
        )
        self.assertEqual(
            ENVELOPE_STATUS_VALUES,
            ("success", "failure"),
        )
        self.assertEqual(
            ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES,
            ("broker_fact", "market_fact"),
        )
        self.assertEqual(
            FORBIDDEN_PAYLOAD_SECRET_FIELD_NAMES,
            (
                "token",
                "password",
                "api_key",
                "apikey",
                "secret",
                "authorization",
                "access_token",
                "refresh_token",
                "credential",
                "credentials",
            ),
        )

    def test_append_request_field_contract(self):
        self._assert_frozen_model(
            ExplicitFactAppendRequest,
            [
                "fact_id",
                "envelope",
                "superseded_fact_id",
            ],
            {
                "fact_id": "str",
                "envelope": "ExplicitProviderPayloadEnvelope",
                "superseded_fact_id": "str | None",
            },
        )

    def test_stored_record_field_contract(self):
        self._assert_frozen_model(
            ExplicitStoredFactRecord,
            [
                "fact_id",
                "envelope_id",
                "provider_id",
                "source_class",
                "collected_at",
                "appended_at",
                "status",
                "payload",
                "superseded_fact_id",
                "integrity_seal",
            ],
            {
                "fact_id": "str",
                "envelope_id": "str",
                "provider_id": "str",
                "source_class": "str",
                "collected_at": "datetime",
                "appended_at": "datetime",
                "status": "str",
                "payload": "dict",
                "superseded_fact_id": "str | None",
                "integrity_seal": "str | None",
            },
        )

    def test_request_has_no_appended_at(self):
        names = [
            field.name
            for field in fields(ExplicitFactAppendRequest)
        ]
        self.assertNotIn("appended_at", names)
        self.assertNotIn("source_identity", names)

    def test_stored_record_has_no_source_identity_alias(self):
        names = [
            field.name
            for field in fields(ExplicitStoredFactRecord)
        ]
        self.assertNotIn("source_identity", names)

    def test_models_are_frozen_and_equality_structural(self):
        first = make_request()
        same = make_request()
        different = make_request(fact_id="fact-002")
        self.assertEqual(first, same)
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.fact_id = "replacement"
        record = make_stored_record()
        with self.assertRaises(FrozenInstanceError):
            record.fact_id = "replacement"
        with self.assertRaises(FrozenInstanceError):
            record.payload = {}
        with self.assertRaises(FrozenInstanceError):
            record.source_class = "broker_fact"
        with self.assertRaises(FrozenInstanceError):
            record.integrity_seal = "other"

    def test_no_defaults_on_public_models(self):
        for model in (
            ExplicitFactAppendRequest,
            ExplicitStoredFactRecord,
        ):
            for field in fields(model):
                self.assertIs(field.default, MISSING)
                self.assertIs(field.default_factory, MISSING)

    def test_unknown_constructor_fields_fail(self):
        with self.assertRaises(TypeError):
            ExplicitFactAppendRequest(
                "fact-001",
                make_envelope(),
                None,
                extra="no",
            )
        with self.assertRaises(TypeError):
            ExplicitStoredFactRecord(
                "fact-001",
                "envelope-001",
                "market-provider-001",
                "market_fact",
                COLLECTED_AT,
                APPENDED_AT,
                "success",
                {},
                None,
                None,
                extra="no",
            )

    def test_models_do_not_generate_fact_id(self):
        supplied = " caller-fact-001 "
        request = make_request(fact_id=supplied)
        self.assertIs(request.fact_id, supplied)
        self.assertEqual(request.fact_id, " caller-fact-001 ")

    def test_missing_fact_id_is_constructor_error(self):
        with self.assertRaises(TypeError):
            ExplicitFactAppendRequest(
                envelope=make_envelope(),
                superseded_fact_id=None,
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
