from __future__ import annotations

import unittest
from dataclasses import (
    FrozenInstanceError,
    MISSING,
    fields,
    is_dataclass,
)

from MarketInstrument.models import ExplicitMarketInstrument
from MarketSnapshot.models import ExplicitMarketSnapshot

from MarketSnapshotProducer.models import (
    COMPOSITION_SOURCE_CLASS,
    PRODUCTION_FAILURE_CODE_VALUES,
    PRODUCTION_RESULT_KIND_VALUES,
    ExplicitMarketFactSelectionCriteria,
    ExplicitMarketSessionProfile,
    ExplicitMarketSnapshotProductionFailure,
    ExplicitMarketSnapshotProductionPolicy,
    ExplicitMarketSnapshotProductionRequest,
    ExplicitMarketSnapshotProductionResult,
    ExplicitMarketSubjectBinding,
)
from MarketSnapshotProducer.tests.builders import (
    make_binding,
    make_criteria,
    make_policy,
    make_profile,
    make_request,
)


FORBIDDEN_FIELD_NAMES = (
    "ticker",
    "alias",
    "entity",
    "ohlc",
    "open",
    "high",
    "low",
    "close",
    "bid",
    "ask",
    "volume",
    "turnover",
    "payload",
)


class ModelContractTests(unittest.TestCase):
    def test_closed_vocabularies_are_exact(self):
        self.assertEqual(
            COMPOSITION_SOURCE_CLASS,
            "market_fact",
        )
        self.assertEqual(
            PRODUCTION_RESULT_KIND_VALUES,
            ("success", "failure"),
        )
        self.assertEqual(
            PRODUCTION_FAILURE_CODE_VALUES,
            (
                "MISSING_REQUIRED_FACT",
                "STALE_REQUIRED_FACT",
                "INELIGIBLE_FACT",
                "CRITERIA_MISMATCH",
                "PROJECTION_FAILURE",
                "EMPTY_REQUIRED_EMISSION",
            ),
        )

    def test_session_profile_field_contract(self):
        self._assert_frozen_model(
            ExplicitMarketSessionProfile,
            [
                "session_profile_id",
                "market_id",
                "venue_id",
                "timezone_id",
                "calendar_id",
            ],
            {
                "session_profile_id": "str",
                "market_id": "str",
                "venue_id": "str",
                "timezone_id": "str",
                "calendar_id": "str",
            },
        )

    def test_subject_binding_field_contract(self):
        self._assert_frozen_model(
            ExplicitMarketSubjectBinding,
            [
                "instrument",
                "fact_id",
                "last_price_payload_key",
                "market_status_payload_key",
            ],
            {
                "instrument": "ExplicitMarketInstrument",
                "fact_id": "str",
                "last_price_payload_key": "str",
                "market_status_payload_key": "str",
            },
        )

    def test_criteria_field_contract(self):
        self._assert_frozen_model(
            ExplicitMarketFactSelectionCriteria,
            [
                "required_source_class",
                "required_source_identity",
                "collected_at_start",
                "collected_at_end",
            ],
            {
                "required_source_class": "str",
                "required_source_identity": "str | None",
                "collected_at_start": "datetime | None",
                "collected_at_end": "datetime | None",
            },
        )

    def test_policy_field_contract(self):
        self._assert_frozen_model(
            ExplicitMarketSnapshotProductionPolicy,
            [
                "require_all_bound_subjects",
                "allow_partial_emission",
                "freshness_max_age",
            ],
            {
                "require_all_bound_subjects": "bool",
                "allow_partial_emission": "bool",
                "freshness_max_age": "timedelta | None",
            },
        )

    def test_request_field_contract(self):
        self._assert_frozen_model(
            ExplicitMarketSnapshotProductionRequest,
            [
                "market_snapshot_id",
                "session_context_id",
                "session_profile",
                "subject_bindings",
                "fact_selection",
                "production_policy",
            ],
            {
                "market_snapshot_id": "str",
                "session_context_id": "str",
                "session_profile": (
                    "ExplicitMarketSessionProfile"
                ),
                "subject_bindings": (
                    "tuple[ExplicitMarketSubjectBinding, ...]"
                ),
                "fact_selection": (
                    "ExplicitMarketFactSelectionCriteria"
                ),
                "production_policy": (
                    "ExplicitMarketSnapshotProductionPolicy"
                ),
            },
        )

    def test_failure_field_contract(self):
        self._assert_frozen_model(
            ExplicitMarketSnapshotProductionFailure,
            [
                "failure_code",
                "omitted_instrument_ids",
            ],
            {
                "failure_code": "str",
                "omitted_instrument_ids": "tuple[str, ...]",
            },
        )

    def test_result_field_contract(self):
        self._assert_frozen_model(
            ExplicitMarketSnapshotProductionResult,
            [
                "result_kind",
                "snapshot",
                "failure",
                "omitted_instrument_ids",
            ],
            {
                "result_kind": "str",
                "snapshot": "ExplicitMarketSnapshot | None",
                "failure": (
                    "ExplicitMarketSnapshotProductionFailure | None"
                ),
                "omitted_instrument_ids": "tuple[str, ...]",
            },
        )

    def test_models_are_frozen_and_equality_structural(self):
        first = make_request()
        same = make_request()
        different = make_request(
            market_snapshot_id="snapshot-002"
        )
        self.assertEqual(first, same)
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.market_snapshot_id = "replacement"
        profile = make_profile()
        with self.assertRaises(FrozenInstanceError):
            profile.market_id = "replacement"
        binding = make_binding()
        with self.assertRaises(FrozenInstanceError):
            binding.fact_id = "replacement"
        policy = make_policy()
        with self.assertRaises(FrozenInstanceError):
            policy.allow_partial_emission = True

    def test_no_defaults_on_public_models(self):
        for model in (
            ExplicitMarketSessionProfile,
            ExplicitMarketSubjectBinding,
            ExplicitMarketFactSelectionCriteria,
            ExplicitMarketSnapshotProductionPolicy,
            ExplicitMarketSnapshotProductionRequest,
            ExplicitMarketSnapshotProductionFailure,
            ExplicitMarketSnapshotProductionResult,
        ):
            for field in fields(model):
                self.assertIs(field.default, MISSING)
                self.assertIs(field.default_factory, MISSING)

    def test_unknown_constructor_fields_fail(self):
        with self.assertRaises(TypeError):
            ExplicitMarketSessionProfile(
                "p",
                "m",
                "v",
                "t",
                "c",
                extra="no",
            )
        with self.assertRaises(TypeError):
            make_request(extra="no")

    def test_models_do_not_generate_snapshot_id(self):
        supplied = " caller-snapshot-001 "
        request = make_request(market_snapshot_id=supplied)
        self.assertIs(request.market_snapshot_id, supplied)
        self.assertEqual(
            request.market_snapshot_id,
            " caller-snapshot-001 ",
        )

    def test_missing_snapshot_id_is_constructor_error(self):
        with self.assertRaises(TypeError):
            ExplicitMarketSnapshotProductionRequest(
                session_context_id="session-context-001",
                session_profile=make_profile(),
                subject_bindings=(),
                fact_selection=make_criteria(),
                production_policy=make_policy(),
            )

    def test_binding_preserves_instrument_object(self):
        instrument = ExplicitMarketInstrument("instrument-001")
        binding = make_binding(instrument=instrument)
        self.assertIs(binding.instrument, instrument)

    def test_request_has_exactly_one_session_profile(self):
        names = [
            field.name
            for field in fields(
                ExplicitMarketSnapshotProductionRequest
            )
        ]
        self.assertEqual(
            names.count("session_profile"),
            1,
        )
        self.assertNotIn("session_profiles", names)
        self.assertEqual(
            ExplicitMarketSnapshotProductionRequest
            .__annotations__["session_profile"],
            "ExplicitMarketSessionProfile",
        )

    def test_producer_models_do_not_copy_market_status(self):
        from MarketSnapshotProducer import models as package
        from MarketSnapshotProducer.models import types
        from MarketSnapshotProducer.models import vocabularies

        for module in (package, types, vocabularies):
            self.assertFalse(
                hasattr(module, "MARKET_STATUS_VALUES")
            )

    def test_forbidden_product_fields_are_absent(self):
        for model in (
            ExplicitMarketSessionProfile,
            ExplicitMarketSubjectBinding,
            ExplicitMarketFactSelectionCriteria,
            ExplicitMarketSnapshotProductionPolicy,
            ExplicitMarketSnapshotProductionRequest,
            ExplicitMarketSnapshotProductionFailure,
            ExplicitMarketSnapshotProductionResult,
        ):
            names = [field.name for field in fields(model)]
            for forbidden in FORBIDDEN_FIELD_NAMES:
                with self.subTest(
                    model=model.__name__,
                    field=forbidden,
                ):
                    self.assertNotIn(forbidden, names)

    def test_failure_does_not_carry_prices_or_payloads(self):
        names = [
            field.name
            for field in fields(
                ExplicitMarketSnapshotProductionFailure
            )
        ]
        self.assertEqual(
            names,
            ["failure_code", "omitted_instrument_ids"],
        )
        self.assertNotIn("last_price", names)
        self.assertNotIn("market_status", names)
        self.assertNotIn("snapshot", names)

    def test_result_snapshot_type_is_accepted_market_snapshot(
        self,
    ):
        annotation = (
            ExplicitMarketSnapshotProductionResult
            .__annotations__["snapshot"]
        )
        self.assertEqual(
            annotation,
            "ExplicitMarketSnapshot | None",
        )
        self.assertIs(
            ExplicitMarketSnapshot,
            ExplicitMarketSnapshot,
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
