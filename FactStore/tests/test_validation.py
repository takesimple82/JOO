from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone, tzinfo
from unittest.mock import patch

from ProviderGateway.models import ExplicitProviderPayloadEnvelope
from ProviderGateway.validation import (
    validate_explicit_provider_payload_envelope,
)

from FactStore.models import (
    ExplicitFactAppendRequest,
    ExplicitStoredFactRecord,
)
from FactStore.tests.builders import (
    APPENDED_AT,
    COLLECTED_AT,
    make_broker_envelope,
    make_diagnostics,
    make_envelope,
    make_request,
    make_stored_record,
)
from FactStore.validation import (
    validate_collected_at_window,
    validate_explicit_fact_append_request,
    validate_explicit_stored_fact_record,
    validate_primary_fact_append_eligibility,
    verify_stored_fact_integrity,
)


class StringSubclass(str):
    pass


class DictSubclass(dict):
    pass


class RequestSubclass(ExplicitFactAppendRequest):
    pass


class RecordSubclass(ExplicitStoredFactRecord):
    pass


class EnvelopeSubclass(ExplicitProviderPayloadEnvelope):
    pass


class ValidationSuccessTests(unittest.TestCase):
    def test_validators_return_none(self):
        request = make_request()
        self.assertIsNone(
            validate_explicit_fact_append_request(request)
        )
        self.assertIsNone(
            validate_primary_fact_append_eligibility(request)
        )
        record = make_stored_record()
        self.assertIsNone(
            validate_explicit_stored_fact_record(record)
        )
        self.assertIsNone(verify_stored_fact_integrity(record))
        self.assertIsNone(
            validate_collected_at_window(
                COLLECTED_AT,
                APPENDED_AT,
            )
        )

    def test_generic_gateway_envelope_accepts_broker_fact(self):
        envelope = make_broker_envelope()
        self.assertIsNone(
            validate_explicit_provider_payload_envelope(
                envelope
            )
        )
        request = make_request(
            fact_id="broker-fact-001",
            envelope=envelope,
        )
        self.assertIsNone(
            validate_explicit_fact_append_request(request)
        )
        self.assertIsNone(
            validate_primary_fact_append_eligibility(request)
        )

    def test_surrounding_whitespace_is_preserved(self):
        fact_id = " fact-001 "
        request = make_request(fact_id=fact_id)
        self.assertIsNone(
            validate_explicit_fact_append_request(request)
        )
        self.assertIs(request.fact_id, fact_id)


class AppendRequestValidationTests(unittest.TestCase):
    def test_request_requires_exact_model_type_first(self):
        invalid = (
            None,
            object(),
            {},
            RequestSubclass(
                "fact-001",
                make_envelope(),
                None,
            ),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^request must be "
                    "ExplicitFactAppendRequest$",
                ):
                    validate_explicit_fact_append_request(value)

    def test_fact_id_requires_exact_nonblank_str(self):
        for value in (None, 1, b"x", StringSubclass("f")):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^fact_id must be str$",
                ):
                    validate_explicit_fact_append_request(
                        make_request(fact_id=value)
                    )
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^fact_id must not be blank$",
                ):
                    validate_explicit_fact_append_request(
                        make_request(fact_id=value)
                    )

    def test_envelope_requires_exact_gateway_type(self):
        request = ExplicitFactAppendRequest(
            "fact-001",
            EnvelopeSubclass(
                "envelope-001",
                "market-provider-001",
                "market_fact",
                COLLECTED_AT,
                "success",
                {"last": "1"},
                None,
                None,
            ),
            None,
        )
        with self.assertRaisesRegex(
            TypeError,
            "^envelope must be "
            "ExplicitProviderPayloadEnvelope$",
        ):
            validate_explicit_fact_append_request(request)

    def test_self_supersession_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "^superseded_fact_id must not equal fact_id$",
        ):
            validate_explicit_fact_append_request(
                make_request(superseded_fact_id="fact-001")
            )

    def test_blank_superseded_fact_id_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "^superseded_fact_id must not be blank$",
        ):
            validate_explicit_fact_append_request(
                make_request(superseded_fact_id=" ")
            )

    def test_first_failure_wins_on_request(self):
        request = make_request(
            fact_id="",
            envelope=make_envelope(source_class="primary"),
            superseded_fact_id="fact-001",
        )
        with self.assertRaisesRegex(
            ValueError,
            "^fact_id must not be blank$",
        ):
            validate_explicit_fact_append_request(request)

    def test_upstream_envelope_exception_is_unchanged(self):
        error = ValueError("envelope failure")
        with patch(
            "FactStore.validation.validators"
            ".validate_explicit_provider_payload_envelope",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_fact_append_request(
                    make_request()
                )
        self.assertIs(caught.exception, error)


class EligibilityValidationTests(unittest.TestCase):
    def test_rejects_failure_status_first(self):
        request = make_request(
            envelope=make_envelope(
                status="failure",
                payload=None,
                error_diagnostics=make_diagnostics(),
                source_class="research_ai",
            )
        )
        with self.assertRaisesRegex(
            ValueError,
            "^status must be success$",
        ):
            validate_primary_fact_append_eligibility(request)

    def test_rejects_research_ai(self):
        request = make_request(
            envelope=make_envelope(source_class="research_ai")
        )
        with self.assertRaisesRegex(
            ValueError,
            "^source_class must be one of "
            "ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES$",
        ):
            validate_primary_fact_append_eligibility(request)

    def test_rejects_case_folded_or_repaired_class(self):
        for source_class in (
            "MARKET_FACT",
            "broker-fact",
            "primary",
            " market_fact",
        ):
            with self.subTest(source_class=source_class):
                envelope = make_envelope(
                    source_class=source_class
                )
                request = make_request(envelope=envelope)
                with self.assertRaisesRegex(
                    ValueError,
                    "^source_class must be one of "
                    "ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES$",
                ):
                    validate_primary_fact_append_eligibility(
                        request
                    )

    def test_rejects_payload_subclass(self):
        request = make_request(
            envelope=make_envelope(payload=DictSubclass())
        )
        with self.assertRaisesRegex(
            TypeError,
            "^payload must be dict$",
        ):
            validate_primary_fact_append_eligibility(request)

    def test_rejects_forbidden_secret_keys(self):
        request = make_request(
            envelope=make_envelope(
                payload={"token": "secret-value", "last": "1"}
            )
        )
        with self.assertRaisesRegex(
            ValueError,
            "^payload must not contain forbidden "
            "secret field names$",
        ):
            validate_primary_fact_append_eligibility(request)

    def test_secret_key_membership_is_exact(self):
        request = make_request(
            envelope=make_envelope(
                payload={"Token": "not-exact", "last": "1"}
            )
        )
        self.assertIsNone(
            validate_primary_fact_append_eligibility(request)
        )


class StoredRecordAndWindowTests(unittest.TestCase):
    def test_record_requires_exact_model_type_first(self):
        with self.assertRaisesRegex(
            TypeError,
            "^record must be ExplicitStoredFactRecord$",
        ):
            validate_explicit_stored_fact_record(
                RecordSubclass(
                    "fact-001",
                    "envelope-001",
                    "market-provider-001",
                    "market_fact",
                    COLLECTED_AT,
                    APPENDED_AT,
                    "success",
                    {"last": "1"},
                    None,
                    None,
                )
            )

    def test_naive_and_offset_datetimes_are_rejected(self):
        class UtcLike(tzinfo):
            def utcoffset(self, dt):
                return timedelta(0)

            def dst(self, dt):
                return timedelta(0)

            def tzname(self, dt):
                return "UTC"

        naive = datetime(2026, 8, 13, 12, 0)
        offset = datetime(
            2026,
            8,
            13,
            12,
            0,
            tzinfo=timezone(timedelta(hours=9)),
        )
        utc_like = datetime(
            2026,
            8,
            13,
            12,
            0,
            tzinfo=UtcLike(),
        )
        for value in (naive, offset, utc_like):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ValueError,
                    "^collected_at tzinfo must be "
                    "datetime.timezone.utc$",
                ):
                    validate_explicit_stored_fact_record(
                        make_stored_record(collected_at=value)
                    )

    def test_status_must_be_success(self):
        with self.assertRaisesRegex(
            ValueError,
            "^status must be success$",
        ):
            validate_explicit_stored_fact_record(
                make_stored_record(status="failure")
            )

    def test_window_order_and_types(self):
        with self.assertRaisesRegex(
            TypeError,
            "^collected_at_start must be datetime$",
        ):
            validate_collected_at_window("start", APPENDED_AT)
        with self.assertRaisesRegex(
            ValueError,
            "^collected_at_start must not be after "
            "collected_at_end$",
        ):
            validate_collected_at_window(
                APPENDED_AT,
                COLLECTED_AT,
            )
        self.assertIsNone(
            validate_collected_at_window(
                COLLECTED_AT,
                COLLECTED_AT,
            )
        )

    def test_integrity_mismatch_fails_closed(self):
        record = make_stored_record(
            integrity_seal="not-the-computed-seal"
        )
        with self.assertRaisesRegex(
            ValueError,
            "^integrity_seal mismatch$",
        ):
            verify_stored_fact_integrity(record)
        self.assertEqual(
            record.integrity_seal,
            "not-the-computed-seal",
        )
        self.assertEqual(
            record.source_class,
            "market_fact",
        )

    def test_first_failure_wins_on_stored_record(self):
        record = make_stored_record(
            fact_id="",
            envelope_id="",
            source_class="research_ai",
            status="failure",
        )
        with self.assertRaisesRegex(
            ValueError,
            "^fact_id must not be blank$",
        ):
            validate_explicit_stored_fact_record(record)


if __name__ == "__main__":
    unittest.main()
