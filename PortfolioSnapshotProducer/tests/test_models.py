from __future__ import annotations

import unittest
from dataclasses import (
    FrozenInstanceError,
    MISSING,
    fields,
    is_dataclass,
)

from PortfolioSnapshot.models import ExplicitPortfolioSnapshot

from PortfolioSnapshotProducer.models import (
    COMPOSITION_SOURCE_CLASS,
    PRODUCTION_FAILURE_CODE_VALUES,
    PRODUCTION_RESULT_KIND_VALUES,
    ExplicitPortfolioFactSelectionCriteria,
    ExplicitPortfolioHoldingFactBinding,
    ExplicitPortfolioSnapshotProductionFailure,
    ExplicitPortfolioSnapshotProductionPolicy,
    ExplicitPortfolioSnapshotProductionProvenance,
    ExplicitPortfolioSnapshotProductionRequest,
    ExplicitPortfolioSnapshotProductionResult,
    ExplicitPortfolioUsedFactProvenance,
    ExplicitPortfolioWatchlistMembershipDeclaration,
)
from PortfolioSnapshotProducer.tests.builders import (
    make_binding,
    make_criteria,
    make_declaration,
    make_policy,
    make_request,
)


FORBIDDEN_FIELD_NAMES = (
    "ticker",
    "symbol",
    "alias",
    "account",
    "request_kind",
    "cash",
    "balance",
    "balances",
    "account_state",
    "nav",
    "pnl",
    "price",
    "mark",
    "fx",
    "timestamp",
    "as_of",
    "appended_at",
    "allow_partial_emission",
    "require_all_bound_subjects",
    "quantity",
)


class ModelContractTests(unittest.TestCase):
    def test_closed_vocabularies_are_exact(self):
        self.assertEqual(
            COMPOSITION_SOURCE_CLASS,
            "broker_fact",
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
            ),
        )
        self.assertNotIn(
            "EMPTY_REQUIRED_EMISSION",
            PRODUCTION_FAILURE_CODE_VALUES,
        )

    def test_binding_field_contract(self):
        self._assert_frozen_model(
            ExplicitPortfolioHoldingFactBinding,
            [
                "fact_id",
                "position_id",
                "portfolio_subject_id",
                "quantity_payload_key",
            ],
            {
                "fact_id": "str",
                "position_id": "str",
                "portfolio_subject_id": "str",
                "quantity_payload_key": "str",
            },
        )

    def test_declaration_field_contract(self):
        self._assert_frozen_model(
            ExplicitPortfolioWatchlistMembershipDeclaration,
            ["portfolio_subject_id"],
            {"portfolio_subject_id": "str"},
        )

    def test_criteria_field_contract(self):
        self._assert_frozen_model(
            ExplicitPortfolioFactSelectionCriteria,
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
            ExplicitPortfolioSnapshotProductionPolicy,
            ["freshness_max_age"],
            {"freshness_max_age": "timedelta | None"},
        )

    def test_request_field_contract(self):
        self._assert_frozen_model(
            ExplicitPortfolioSnapshotProductionRequest,
            [
                "portfolio_snapshot_id",
                "observation_context_id",
                "portfolio_id",
                "holding_fact_bindings",
                "watchlist_memberships",
                "fact_selection",
                "production_policy",
            ],
            {
                "portfolio_snapshot_id": "str",
                "observation_context_id": "str",
                "portfolio_id": "str",
                "holding_fact_bindings": (
                    "tuple[ExplicitPortfolioHoldingFactBinding, ...]"
                ),
                "watchlist_memberships": (
                    "tuple[ExplicitPortfolioWatchlistMembershipDeclaration, ...]"
                ),
                "fact_selection": (
                    "ExplicitPortfolioFactSelectionCriteria"
                ),
                "production_policy": (
                    "ExplicitPortfolioSnapshotProductionPolicy"
                ),
            },
        )

    def test_used_fact_provenance_field_contract(self):
        self._assert_frozen_model(
            ExplicitPortfolioUsedFactProvenance,
            [
                "fact_id",
                "collected_at",
                "source_identity",
            ],
            {
                "fact_id": "str",
                "collected_at": "datetime",
                "source_identity": "str",
            },
        )

    def test_production_provenance_field_contract(self):
        self._assert_frozen_model(
            ExplicitPortfolioSnapshotProductionProvenance,
            ["used_facts"],
            {
                "used_facts": (
                    "tuple[ExplicitPortfolioUsedFactProvenance, ...]"
                ),
            },
        )

    def test_failure_field_contract(self):
        self._assert_frozen_model(
            ExplicitPortfolioSnapshotProductionFailure,
            [
                "failure_code",
                "failed_fact_id",
                "failed_position_id",
            ],
            {
                "failure_code": "str",
                "failed_fact_id": "str",
                "failed_position_id": "str",
            },
        )

    def test_result_field_contract(self):
        self._assert_frozen_model(
            ExplicitPortfolioSnapshotProductionResult,
            [
                "result_kind",
                "snapshot",
                "failure",
                "provenance",
            ],
            {
                "result_kind": "str",
                "snapshot": "ExplicitPortfolioSnapshot | None",
                "failure": (
                    "ExplicitPortfolioSnapshotProductionFailure | None"
                ),
                "provenance": (
                    "ExplicitPortfolioSnapshotProductionProvenance | None"
                ),
            },
        )

    def test_models_are_frozen_and_equality_structural(self):
        first = make_request()
        same = make_request()
        different = make_request(
            portfolio_snapshot_id="snapshot-002"
        )
        self.assertEqual(first, same)
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.portfolio_snapshot_id = "replacement"
        binding = make_binding()
        with self.assertRaises(FrozenInstanceError):
            binding.fact_id = "replacement"
        declaration = make_declaration()
        with self.assertRaises(FrozenInstanceError):
            declaration.portfolio_subject_id = "replacement"
        policy = make_policy()
        with self.assertRaises(FrozenInstanceError):
            policy.freshness_max_age = None
        criteria = make_criteria()
        with self.assertRaises(FrozenInstanceError):
            criteria.required_source_class = "market_fact"

    def test_no_defaults_on_public_models(self):
        for model in (
            ExplicitPortfolioHoldingFactBinding,
            ExplicitPortfolioWatchlistMembershipDeclaration,
            ExplicitPortfolioFactSelectionCriteria,
            ExplicitPortfolioSnapshotProductionPolicy,
            ExplicitPortfolioSnapshotProductionRequest,
            ExplicitPortfolioUsedFactProvenance,
            ExplicitPortfolioSnapshotProductionProvenance,
            ExplicitPortfolioSnapshotProductionFailure,
            ExplicitPortfolioSnapshotProductionResult,
        ):
            for field in fields(model):
                self.assertIs(field.default, MISSING)
                self.assertIs(field.default_factory, MISSING)

    def test_unknown_constructor_fields_fail(self):
        with self.assertRaises(TypeError):
            ExplicitPortfolioHoldingFactBinding(
                "fact-001",
                "position-001",
                "subject-001",
                "quantity",
                extra="no",
            )
        with self.assertRaises(TypeError):
            make_request(extra="no")

    def test_models_do_not_generate_snapshot_id(self):
        supplied = " caller-snapshot-001 "
        request = make_request(portfolio_snapshot_id=supplied)
        self.assertIs(request.portfolio_snapshot_id, supplied)
        self.assertEqual(
            request.portfolio_snapshot_id,
            " caller-snapshot-001 ",
        )

    def test_missing_snapshot_id_is_constructor_error(self):
        with self.assertRaises(TypeError):
            ExplicitPortfolioSnapshotProductionRequest(
                observation_context_id="context-001",
                portfolio_id="portfolio-001",
                holding_fact_bindings=(),
                watchlist_memberships=(),
                fact_selection=make_criteria(),
                production_policy=make_policy(),
            )

    def test_binding_has_no_quantity_value(self):
        names = [
            field.name
            for field in fields(
                ExplicitPortfolioHoldingFactBinding
            )
        ]
        self.assertEqual(
            names,
            [
                "fact_id",
                "position_id",
                "portfolio_subject_id",
                "quantity_payload_key",
            ],
        )
        self.assertNotIn("quantity", names)
        self.assertNotIn("portfolio_id", names)

    def test_result_snapshot_type_is_accepted_portfolio_snapshot(
        self,
    ):
        annotation = (
            ExplicitPortfolioSnapshotProductionResult
            .__annotations__["snapshot"]
        )
        self.assertEqual(
            annotation,
            "ExplicitPortfolioSnapshot | None",
        )
        self.assertIs(
            ExplicitPortfolioSnapshot,
            ExplicitPortfolioSnapshot,
        )

    def test_forbidden_product_fields_are_absent(self):
        for model in (
            ExplicitPortfolioHoldingFactBinding,
            ExplicitPortfolioWatchlistMembershipDeclaration,
            ExplicitPortfolioFactSelectionCriteria,
            ExplicitPortfolioSnapshotProductionPolicy,
            ExplicitPortfolioSnapshotProductionRequest,
            ExplicitPortfolioUsedFactProvenance,
            ExplicitPortfolioSnapshotProductionProvenance,
            ExplicitPortfolioSnapshotProductionFailure,
            ExplicitPortfolioSnapshotProductionResult,
        ):
            names = [field.name for field in fields(model)]
            for forbidden in FORBIDDEN_FIELD_NAMES:
                with self.subTest(
                    model=model.__name__,
                    field=forbidden,
                ):
                    self.assertNotIn(forbidden, names)

    def test_observation_context_is_not_a_producer_model(self):
        from PortfolioSnapshotProducer import models as package
        from PortfolioSnapshotProducer.models import types

        for module in (package, types):
            self.assertFalse(
                hasattr(
                    module,
                    "ExplicitPortfolioObservationContext",
                )
            )

    def test_producer_models_do_not_copy_gateway_vocabularies(
        self,
    ):
        from PortfolioSnapshotProducer import models as package
        from PortfolioSnapshotProducer.models import types
        from PortfolioSnapshotProducer.models import vocabularies

        for module in (package, types, vocabularies):
            self.assertFalse(
                hasattr(module, "BROKER_REQUEST_KIND_VALUES")
            )
            self.assertFalse(
                hasattr(module, "EMPTY_REQUIRED_EMISSION")
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
