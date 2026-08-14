from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from PortfolioSnapshotProducer.models.types import (
    ExplicitPortfolioFactSelectionCriteria,
    ExplicitPortfolioHoldingFactBinding,
    ExplicitPortfolioSnapshotProductionPolicy,
    ExplicitPortfolioSnapshotProductionRequest,
    ExplicitPortfolioWatchlistMembershipDeclaration,
)
from PortfolioSnapshotProducer.tests.builders import (
    COLLECTED_AT,
    make_binding,
    make_criteria,
    make_declaration,
    make_policy,
    make_request,
)
from PortfolioSnapshotProducer.validation import (
    validate_explicit_portfolio_fact_selection_criteria,
    validate_explicit_portfolio_holding_fact_binding,
    validate_explicit_portfolio_snapshot_production_policy,
    validate_explicit_portfolio_snapshot_production_request,
    validate_explicit_portfolio_watchlist_membership_declaration,
)


class StringSubclass(str):
    pass


class BindingSubclass(ExplicitPortfolioHoldingFactBinding):
    pass


class DeclarationSubclass(
    ExplicitPortfolioWatchlistMembershipDeclaration
):
    pass


class CriteriaSubclass(ExplicitPortfolioFactSelectionCriteria):
    pass


class PolicySubclass(ExplicitPortfolioSnapshotProductionPolicy):
    pass


class RequestSubclass(ExplicitPortfolioSnapshotProductionRequest):
    pass


class ValidationSuccessTests(unittest.TestCase):
    def test_validators_return_none(self):
        self.assertIsNone(
            validate_explicit_portfolio_holding_fact_binding(
                make_binding()
            )
        )
        self.assertIsNone(
            validate_explicit_portfolio_watchlist_membership_declaration(
                make_declaration()
            )
        )
        self.assertIsNone(
            validate_explicit_portfolio_fact_selection_criteria(
                make_criteria()
            )
        )
        self.assertIsNone(
            validate_explicit_portfolio_snapshot_production_policy(
                make_policy()
            )
        )
        self.assertIsNone(
            validate_explicit_portfolio_snapshot_production_request(
                make_request()
            )
        )
        self.assertIsNone(
            validate_explicit_portfolio_snapshot_production_request(
                make_request(
                    holding_fact_bindings=(),
                    watchlist_memberships=(),
                )
            )
        )

    def test_surrounding_whitespace_is_preserved(self):
        snapshot_id = " snapshot-001 "
        request = make_request(
            portfolio_snapshot_id=snapshot_id
        )
        self.assertIsNone(
            validate_explicit_portfolio_snapshot_production_request(
                request
            )
        )
        self.assertIs(request.portfolio_snapshot_id, snapshot_id)


class BindingValidationTests(unittest.TestCase):
    def test_binding_requires_exact_model_type_first(self):
        invalid = (
            None,
            object(),
            {},
            BindingSubclass(
                "fact-001",
                "position-001",
                "subject-001",
                "quantity",
            ),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^binding must be "
                    "ExplicitPortfolioHoldingFactBinding$",
                ):
                    validate_explicit_portfolio_holding_fact_binding(
                        value
                    )

    def test_binding_strings_require_exact_nonblank_str(self):
        for field in (
            "fact_id",
            "position_id",
            "portfolio_subject_id",
            "quantity_payload_key",
        ):
            for value in (None, 1, b"x", StringSubclass("x")):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(
                        TypeError,
                        f"^{field} must be str$",
                    ):
                        validate_explicit_portfolio_holding_fact_binding(
                            make_binding(**{field: value})
                        )
            for value in ("", " ", "\t", "\n", " \t\n "):
                with self.subTest(field=field, value=repr(value)):
                    with self.assertRaisesRegex(
                        ValueError,
                        f"^{field} must not be blank$",
                    ):
                        validate_explicit_portfolio_holding_fact_binding(
                            make_binding(**{field: value})
                        )


class DeclarationValidationTests(unittest.TestCase):
    def test_declaration_requires_exact_model_type_first(self):
        with self.assertRaisesRegex(
            TypeError,
            "^declaration must be "
            "ExplicitPortfolioWatchlistMembershipDeclaration$",
        ):
            validate_explicit_portfolio_watchlist_membership_declaration(
                DeclarationSubclass("watch-subject-001")
            )

    def test_subject_id_requires_exact_nonblank_str(self):
        for value in (None, 1, StringSubclass("x")):
            with self.assertRaisesRegex(
                TypeError,
                "^portfolio_subject_id must be str$",
            ):
                validate_explicit_portfolio_watchlist_membership_declaration(
                    make_declaration(
                        portfolio_subject_id=value
                    )
                )
        with self.assertRaisesRegex(
            ValueError,
            "^portfolio_subject_id must not be blank$",
        ):
            validate_explicit_portfolio_watchlist_membership_declaration(
                make_declaration(portfolio_subject_id=" ")
            )


class CriteriaValidationTests(unittest.TestCase):
    def test_criteria_requires_exact_model_type_first(self):
        with self.assertRaisesRegex(
            TypeError,
            "^criteria must be "
            "ExplicitPortfolioFactSelectionCriteria$",
        ):
            validate_explicit_portfolio_fact_selection_criteria(
                CriteriaSubclass(
                    "broker_fact",
                    None,
                    None,
                    None,
                )
            )

    def test_required_source_class_must_be_broker_fact(self):
        with self.assertRaisesRegex(
            TypeError,
            "^required_source_class must be str$",
        ):
            validate_explicit_portfolio_fact_selection_criteria(
                make_criteria(
                    required_source_class=StringSubclass(
                        "broker_fact"
                    )
                )
            )
        for value in (
            "market_fact",
            "research_ai",
            "BROKER_FACT",
            " broker_fact",
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ValueError,
                    "^required_source_class must be "
                    "broker_fact$",
                ):
                    validate_explicit_portfolio_fact_selection_criteria(
                        make_criteria(
                            required_source_class=value
                        )
                    )

    def test_optional_source_identity_and_window(self):
        self.assertIsNone(
            validate_explicit_portfolio_fact_selection_criteria(
                make_criteria(
                    required_source_identity="provider-001",
                    collected_at_start=COLLECTED_AT,
                    collected_at_end=COLLECTED_AT,
                )
            )
        )
        with self.assertRaisesRegex(
            ValueError,
            "^required_source_identity must not be blank$",
        ):
            validate_explicit_portfolio_fact_selection_criteria(
                make_criteria(required_source_identity=" ")
            )
        with self.assertRaisesRegex(
            ValueError,
            "^collected_at_start and collected_at_end must "
            "both be None or both be set$",
        ):
            validate_explicit_portfolio_fact_selection_criteria(
                make_criteria(collected_at_start=COLLECTED_AT)
            )
        later = datetime(2026, 2, 1, tzinfo=timezone.utc)
        with self.assertRaisesRegex(
            ValueError,
            "^collected_at_start must not be after "
            "collected_at_end$",
        ):
            validate_explicit_portfolio_fact_selection_criteria(
                make_criteria(
                    collected_at_start=later,
                    collected_at_end=COLLECTED_AT,
                )
            )

    def test_window_requires_utc_datetime(self):
        naive = datetime(2026, 1, 15, 9, 30)
        with self.assertRaisesRegex(
            TypeError,
            "^collected_at_start must be datetime$",
        ):
            validate_explicit_portfolio_fact_selection_criteria(
                make_criteria(
                    collected_at_start="2026-01-15",
                    collected_at_end=COLLECTED_AT,
                )
            )
        with self.assertRaisesRegex(
            ValueError,
            "^collected_at_start tzinfo must be "
            "datetime.timezone.utc$",
        ):
            validate_explicit_portfolio_fact_selection_criteria(
                make_criteria(
                    collected_at_start=naive,
                    collected_at_end=COLLECTED_AT,
                )
            )


class PolicyValidationTests(unittest.TestCase):
    def test_policy_requires_exact_model_type_first(self):
        with self.assertRaisesRegex(
            TypeError,
            "^policy must be "
            "ExplicitPortfolioSnapshotProductionPolicy$",
        ):
            validate_explicit_portfolio_snapshot_production_policy(
                PolicySubclass(None)
            )

    def test_freshness_max_age_type_and_negative(self):
        self.assertIsNone(
            validate_explicit_portfolio_snapshot_production_policy(
                make_policy(freshness_max_age=timedelta(0))
            )
        )
        with self.assertRaisesRegex(
            TypeError,
            "^freshness_max_age must be timedelta$",
        ):
            validate_explicit_portfolio_snapshot_production_policy(
                make_policy(freshness_max_age=True)
            )
        with self.assertRaisesRegex(
            TypeError,
            "^freshness_max_age must be timedelta$",
        ):
            validate_explicit_portfolio_snapshot_production_policy(
                make_policy(freshness_max_age=1)
            )
        with self.assertRaisesRegex(
            ValueError,
            "^freshness_max_age must not be negative$",
        ):
            validate_explicit_portfolio_snapshot_production_policy(
                make_policy(
                    freshness_max_age=timedelta(seconds=-1)
                )
            )


class RequestValidationTests(unittest.TestCase):
    def test_request_requires_exact_model_type_first(self):
        invalid = (
            None,
            object(),
            {},
            RequestSubclass(
                "snapshot-001",
                "context-001",
                "portfolio-001",
                (),
                (),
                make_criteria(),
                make_policy(),
            ),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^request must be "
                    "ExplicitPortfolioSnapshotProductionRequest$",
                ):
                    validate_explicit_portfolio_snapshot_production_request(
                        value
                    )

    def test_identity_fields_require_exact_nonblank_str(self):
        for field in (
            "portfolio_snapshot_id",
            "observation_context_id",
            "portfolio_id",
        ):
            for value in (None, 1, b"x", StringSubclass("s")):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(
                        TypeError,
                        f"^{field} must be str$",
                    ):
                        validate_explicit_portfolio_snapshot_production_request(
                            make_request(**{field: value})
                        )
            for value in ("", " ", "\t", "\n"):
                with self.subTest(field=field, value=repr(value)):
                    with self.assertRaisesRegex(
                        ValueError,
                        f"^{field} must not be blank$",
                    ):
                        validate_explicit_portfolio_snapshot_production_request(
                            make_request(**{field: value})
                        )

    def test_holding_bindings_require_exact_tuple(self):
        with self.assertRaisesRegex(
            TypeError,
            "^holding_fact_bindings must be tuple$",
        ):
            validate_explicit_portfolio_snapshot_production_request(
                make_request(
                    holding_fact_bindings=[make_binding()]
                )
            )

    def test_watchlist_memberships_require_exact_tuple(self):
        with self.assertRaisesRegex(
            TypeError,
            "^watchlist_memberships must be tuple$",
        ):
            validate_explicit_portfolio_snapshot_production_request(
                make_request(
                    watchlist_memberships=[make_declaration()]
                )
            )

    def test_duplicate_position_id_is_rejected(self):
        first = make_binding(fact_id="fact-001")
        second = make_binding(fact_id="fact-002")
        with self.assertRaisesRegex(
            ValueError,
            "^holding_fact_bindings must not contain "
            "duplicate position_id$",
        ):
            validate_explicit_portfolio_snapshot_production_request(
                make_request(
                    holding_fact_bindings=(first, second)
                )
            )

    def test_duplicate_watchlist_subject_is_rejected(self):
        first = make_declaration(
            portfolio_subject_id="watch-subject-001"
        )
        second = make_declaration(
            portfolio_subject_id="watch-subject-001"
        )
        with self.assertRaisesRegex(
            ValueError,
            "^watchlist_memberships must not contain "
            "duplicate portfolio_subject_id$",
        ):
            validate_explicit_portfolio_snapshot_production_request(
                make_request(
                    watchlist_memberships=(first, second)
                )
            )

    def test_same_fact_id_on_two_bindings_is_allowed(self):
        first = make_binding(
            fact_id="fact-001",
            position_id="position-001",
            quantity_payload_key="qty_a",
        )
        second = make_binding(
            fact_id="fact-001",
            position_id="position-002",
            portfolio_subject_id="subject-002",
            quantity_payload_key="qty_b",
        )
        self.assertIsNone(
            validate_explicit_portfolio_snapshot_production_request(
                make_request(
                    holding_fact_bindings=(first, second)
                )
            )
        )

    def test_same_subject_on_holding_and_watchlist_is_allowed(
        self,
    ):
        self.assertIsNone(
            validate_explicit_portfolio_snapshot_production_request(
                make_request(
                    holding_fact_bindings=(
                        make_binding(
                            portfolio_subject_id="shared"
                        ),
                    ),
                    watchlist_memberships=(
                        make_declaration(
                            portfolio_subject_id="shared"
                        ),
                    ),
                )
            )
        )

    def test_first_failure_wins_on_request(self):
        request = make_request(
            portfolio_snapshot_id="",
            observation_context_id="",
            holding_fact_bindings="bad",
        )
        with self.assertRaisesRegex(
            ValueError,
            "^portfolio_snapshot_id must not be blank$",
        ):
            validate_explicit_portfolio_snapshot_production_request(
                request
            )

    def test_binding_validator_exception_is_unchanged(self):
        error = ValueError("binding failure")
        with patch(
            "PortfolioSnapshotProducer.validation.validators"
            ".validate_explicit_portfolio_holding_fact_binding",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_portfolio_snapshot_production_request(
                    make_request()
                )
            self.assertIs(caught.exception, error)


if __name__ == "__main__":
    unittest.main()
