from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from MarketInstrument.models import ExplicitMarketInstrument

from MarketSnapshotProducer.models.types import (
    ExplicitMarketFactSelectionCriteria,
    ExplicitMarketSessionProfile,
    ExplicitMarketSnapshotProductionPolicy,
    ExplicitMarketSnapshotProductionRequest,
    ExplicitMarketSubjectBinding,
)
from MarketSnapshotProducer.tests.builders import (
    COLLECTED_AT,
    make_binding,
    make_criteria,
    make_instrument,
    make_policy,
    make_profile,
    make_request,
)
from MarketSnapshotProducer.validation import (
    validate_explicit_market_fact_selection_criteria,
    validate_explicit_market_session_profile,
    validate_explicit_market_snapshot_production_policy,
    validate_explicit_market_snapshot_production_request,
    validate_explicit_market_subject_binding,
)


class StringSubclass(str):
    pass


class ProfileSubclass(ExplicitMarketSessionProfile):
    pass


class BindingSubclass(ExplicitMarketSubjectBinding):
    pass


class CriteriaSubclass(ExplicitMarketFactSelectionCriteria):
    pass


class PolicySubclass(ExplicitMarketSnapshotProductionPolicy):
    pass


class RequestSubclass(ExplicitMarketSnapshotProductionRequest):
    pass


class InstrumentSubclass(ExplicitMarketInstrument):
    pass


class ValidationSuccessTests(unittest.TestCase):
    def test_validators_return_none(self):
        self.assertIsNone(
            validate_explicit_market_session_profile(
                make_profile()
            )
        )
        self.assertIsNone(
            validate_explicit_market_subject_binding(
                make_binding()
            )
        )
        self.assertIsNone(
            validate_explicit_market_fact_selection_criteria(
                make_criteria()
            )
        )
        self.assertIsNone(
            validate_explicit_market_snapshot_production_policy(
                make_policy()
            )
        )
        self.assertIsNone(
            validate_explicit_market_snapshot_production_request(
                make_request()
            )
        )
        self.assertIsNone(
            validate_explicit_market_snapshot_production_request(
                make_request(subject_bindings=())
            )
        )

    def test_surrounding_whitespace_is_preserved(self):
        snapshot_id = " snapshot-001 "
        request = make_request(
            market_snapshot_id=snapshot_id
        )
        self.assertIsNone(
            validate_explicit_market_snapshot_production_request(
                request
            )
        )
        self.assertIs(request.market_snapshot_id, snapshot_id)


class SessionProfileValidationTests(unittest.TestCase):
    def test_profile_requires_exact_model_type_first(self):
        invalid = (
            None,
            object(),
            {},
            ProfileSubclass(
                "korea-session-profile",
                "korea-market",
                "korea-venue",
                "korea-timezone",
                "korea-calendar",
            ),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^profile must be "
                    "ExplicitMarketSessionProfile$",
                ):
                    validate_explicit_market_session_profile(
                        value
                    )

    def test_profile_ids_require_exact_nonblank_str(self):
        for field in (
            "session_profile_id",
            "market_id",
            "venue_id",
            "timezone_id",
            "calendar_id",
        ):
            for value in (None, 1, b"x", StringSubclass("x")):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(
                        TypeError,
                        f"^{field} must be str$",
                    ):
                        validate_explicit_market_session_profile(
                            make_profile(**{field: value})
                        )
            for value in ("", " ", "\t", "\n", " \t\n "):
                with self.subTest(field=field, value=repr(value)):
                    with self.assertRaisesRegex(
                        ValueError,
                        f"^{field} must not be blank$",
                    ):
                        validate_explicit_market_session_profile(
                            make_profile(**{field: value})
                        )


class BindingValidationTests(unittest.TestCase):
    def test_binding_requires_exact_model_type_first(self):
        with self.assertRaisesRegex(
            TypeError,
            "^binding must be ExplicitMarketSubjectBinding$",
        ):
            validate_explicit_market_subject_binding(
                BindingSubclass(
                    make_instrument(),
                    "fact-001",
                    "last_price",
                    "market_status",
                )
            )

    def test_instrument_requires_exact_type(self):
        binding = ExplicitMarketSubjectBinding(
            InstrumentSubclass("instrument-001"),
            "fact-001",
            "last_price",
            "market_status",
        )
        with self.assertRaisesRegex(
            TypeError,
            "^instrument must be ExplicitMarketInstrument$",
        ):
            validate_explicit_market_subject_binding(binding)

    def test_instrument_validator_exception_is_unchanged(self):
        error = ValueError("instrument failure")
        with patch(
            "MarketSnapshotProducer.validation.validators"
            ".validate_explicit_market_instrument",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_market_subject_binding(
                    make_binding()
                )
            self.assertIs(caught.exception, error)

    def test_binding_strings_require_exact_nonblank_str(self):
        for field in (
            "fact_id",
            "last_price_payload_key",
            "market_status_payload_key",
        ):
            for value in (None, 1, StringSubclass("x")):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(
                        TypeError,
                        f"^{field} must be str$",
                    ):
                        validate_explicit_market_subject_binding(
                            make_binding(**{field: value})
                        )
            with self.assertRaisesRegex(
                ValueError,
                f"^{field} must not be blank$",
            ):
                validate_explicit_market_subject_binding(
                    make_binding(**{field: " "})
                )


class CriteriaValidationTests(unittest.TestCase):
    def test_criteria_requires_exact_model_type_first(self):
        with self.assertRaisesRegex(
            TypeError,
            "^criteria must be "
            "ExplicitMarketFactSelectionCriteria$",
        ):
            validate_explicit_market_fact_selection_criteria(
                CriteriaSubclass(
                    "market_fact",
                    None,
                    None,
                    None,
                )
            )

    def test_required_source_class_must_be_market_fact(self):
        with self.assertRaisesRegex(
            TypeError,
            "^required_source_class must be str$",
        ):
            validate_explicit_market_fact_selection_criteria(
                make_criteria(
                    required_source_class=StringSubclass(
                        "market_fact"
                    )
                )
            )
        for value in (
            "broker_fact",
            "research_ai",
            "MARKET_FACT",
            " market_fact",
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ValueError,
                    "^required_source_class must be "
                    "market_fact$",
                ):
                    validate_explicit_market_fact_selection_criteria(
                        make_criteria(
                            required_source_class=value
                        )
                    )

    def test_optional_source_identity_and_window(self):
        self.assertIsNone(
            validate_explicit_market_fact_selection_criteria(
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
            validate_explicit_market_fact_selection_criteria(
                make_criteria(required_source_identity=" ")
            )
        with self.assertRaisesRegex(
            ValueError,
            "^collected_at_start and collected_at_end must "
            "both be None or both be set$",
        ):
            validate_explicit_market_fact_selection_criteria(
                make_criteria(collected_at_start=COLLECTED_AT)
            )
        later = datetime(2026, 2, 1, tzinfo=timezone.utc)
        with self.assertRaisesRegex(
            ValueError,
            "^collected_at_start must not be after "
            "collected_at_end$",
        ):
            validate_explicit_market_fact_selection_criteria(
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
            validate_explicit_market_fact_selection_criteria(
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
            validate_explicit_market_fact_selection_criteria(
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
            "ExplicitMarketSnapshotProductionPolicy$",
        ):
            validate_explicit_market_snapshot_production_policy(
                PolicySubclass(True, False, None)
            )

    def test_bools_require_exact_bool(self):
        for field in (
            "require_all_bound_subjects",
            "allow_partial_emission",
        ):
            for value in (None, 1, 0, "true"):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(
                        TypeError,
                        f"^{field} must be bool$",
                    ):
                        validate_explicit_market_snapshot_production_policy(
                            make_policy(**{field: value})
                        )

    def test_contradictory_pair_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "^require_all_bound_subjects and "
            "allow_partial_emission must not both be True$",
        ):
            validate_explicit_market_snapshot_production_policy(
                make_policy(
                    require_all_bound_subjects=True,
                    allow_partial_emission=True,
                )
            )

    def test_freshness_max_age_type_and_negative(self):
        self.assertIsNone(
            validate_explicit_market_snapshot_production_policy(
                make_policy(freshness_max_age=timedelta(0))
            )
        )
        with self.assertRaisesRegex(
            TypeError,
            "^freshness_max_age must be timedelta$",
        ):
            validate_explicit_market_snapshot_production_policy(
                make_policy(freshness_max_age=True)
            )
        with self.assertRaisesRegex(
            TypeError,
            "^freshness_max_age must be timedelta$",
        ):
            validate_explicit_market_snapshot_production_policy(
                make_policy(freshness_max_age=1)
            )
        with self.assertRaisesRegex(
            ValueError,
            "^freshness_max_age must not be negative$",
        ):
            validate_explicit_market_snapshot_production_policy(
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
                "session-context-001",
                make_profile(),
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
                    "ExplicitMarketSnapshotProductionRequest$",
                ):
                    validate_explicit_market_snapshot_production_request(
                        value
                    )

    def test_snapshot_id_requires_exact_nonblank_str(self):
        for value in (None, 1, b"x", StringSubclass("s")):
            with self.assertRaisesRegex(
                TypeError,
                "^market_snapshot_id must be str$",
            ):
                validate_explicit_market_snapshot_production_request(
                    make_request(market_snapshot_id=value)
                )
        for value in ("", " ", "\t", "\n"):
            with self.assertRaisesRegex(
                ValueError,
                "^market_snapshot_id must not be blank$",
            ):
                validate_explicit_market_snapshot_production_request(
                    make_request(market_snapshot_id=value)
                )

    def test_subject_bindings_require_exact_tuple(self):
        with self.assertRaisesRegex(
            TypeError,
            "^subject_bindings must be tuple$",
        ):
            validate_explicit_market_snapshot_production_request(
                make_request(subject_bindings=[make_binding()])
            )

    def test_duplicate_instrument_id_is_rejected(self):
        first = make_binding(fact_id="fact-001")
        second = make_binding(fact_id="fact-002")
        with self.assertRaisesRegex(
            ValueError,
            "^subject_bindings must not contain "
            "duplicate instrument_id$",
        ):
            validate_explicit_market_snapshot_production_request(
                make_request(
                    subject_bindings=(first, second)
                )
            )

    def test_first_failure_wins_on_request(self):
        request = make_request(
            market_snapshot_id="",
            session_context_id="",
            subject_bindings="bad",
        )
        with self.assertRaisesRegex(
            ValueError,
            "^market_snapshot_id must not be blank$",
        ):
            validate_explicit_market_snapshot_production_request(
                request
            )

    def test_profile_validator_exception_is_unchanged(self):
        error = ValueError("profile failure")
        with patch(
            "MarketSnapshotProducer.validation.validators"
            ".validate_explicit_market_session_profile",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_market_snapshot_production_request(
                    make_request()
                )
            self.assertIs(caught.exception, error)


if __name__ == "__main__":
    unittest.main()
