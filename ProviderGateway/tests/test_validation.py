from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone, tzinfo
from unittest.mock import patch

from ProviderGateway.models import (
    AVAILABILITY_VALUES,
    BROKER_REQUEST_KIND_VALUES,
    ENVELOPE_STATUS_VALUES,
    FAILURE_CLASS_VALUES,
    SOURCE_CLASS_VALUES,
    ExplicitBrokerAdapterBinding,
    ExplicitBrokerCollectRequest,
    ExplicitBrokerParameterProfile,
    ExplicitCollectOutcome,
    ExplicitErrorDiagnostics,
    ExplicitProviderPayloadEnvelope,
)
from ProviderGateway.tests.builders import (
    FIXED_CLOCK,
    make_binding,
    make_broker_binding,
    make_broker_profile,
    make_broker_request,
    make_diagnostics,
    make_envelope,
    make_failure,
    make_health,
    make_profile,
    make_request,
)
from ProviderGateway.validation import (
    validate_broker_fact_success_envelope,
    validate_explicit_broker_adapter_binding,
    validate_explicit_broker_collect_request,
    validate_explicit_broker_parameter_profile,
    validate_explicit_collect_outcome,
    validate_explicit_collect_request,
    validate_explicit_error_diagnostics,
    validate_explicit_market_adapter_binding,
    validate_explicit_market_parameter_profile,
    validate_explicit_provider_failure_signal,
    validate_explicit_provider_health_snapshot,
    validate_explicit_provider_payload_envelope,
    validate_market_fact_success_envelope,
)


class StringSubclass(str):
    pass


class DictSubclass(dict):
    pass


class TupleSubclass(tuple):
    pass


class EnvelopeSubclass(ExplicitProviderPayloadEnvelope):
    pass


class BrokerProfileSubclass(ExplicitBrokerParameterProfile):
    pass


class BrokerBindingSubclass(ExplicitBrokerAdapterBinding):
    pass


class BrokerRequestSubclass(ExplicitBrokerCollectRequest):
    pass


class DiagnosticsSubclass(ExplicitErrorDiagnostics):
    pass


class ValidationSuccessTests(unittest.TestCase):
    def test_validators_return_none(self):
        self.assertIsNone(
            validate_explicit_error_diagnostics(
                make_diagnostics()
            )
        )
        self.assertIsNone(
            validate_explicit_provider_payload_envelope(
                make_envelope()
            )
        )
        self.assertIsNone(
            validate_market_fact_success_envelope(
                make_envelope()
            )
        )
        self.assertIsNone(
            validate_explicit_provider_health_snapshot(
                make_health()
            )
        )
        self.assertIsNone(
            validate_explicit_provider_failure_signal(
                make_failure()
            )
        )
        self.assertIsNone(
            validate_explicit_market_parameter_profile(
                make_profile()
            )
        )
        self.assertIsNone(
            validate_explicit_market_adapter_binding(
                make_binding()
            )
        )
        self.assertIsNone(
            validate_explicit_collect_request(make_request())
        )
        self.assertIsNone(
            validate_explicit_collect_outcome(
                ExplicitCollectOutcome(
                    "success",
                    make_envelope(),
                    None,
                )
            )
        )
        self.assertIsNone(
            validate_explicit_collect_outcome(
                ExplicitCollectOutcome(
                    "failure",
                    None,
                    make_failure(),
                )
            )
        )

    def test_generic_envelope_accepts_every_source_class(self):
        for source_class in SOURCE_CLASS_VALUES:
            with self.subTest(source_class=source_class):
                envelope = make_envelope(
                    source_class=source_class,
                    provider_id="kb_open_api"
                    if source_class == "broker_fact"
                    else "market-provider-001",
                )
                self.assertIsNone(
                    validate_explicit_provider_payload_envelope(
                        envelope
                    )
                )

    def test_generic_envelope_accepts_broker_fact(self):
        envelope = make_envelope(
            provider_id="kb_open_api",
            source_class="broker_fact",
        )
        self.assertIsNone(
            validate_explicit_provider_payload_envelope(
                envelope
            )
        )

    def test_failure_envelope_requires_none_payload(self):
        envelope = make_envelope(
            status="failure",
            payload=None,
            error_diagnostics=make_diagnostics(),
        )
        self.assertIsNone(
            validate_explicit_provider_payload_envelope(
                envelope
            )
        )

    def test_surrounding_whitespace_is_preserved(self):
        envelope_id = " envelope-001 "
        envelope = make_envelope(envelope_id=envelope_id)
        self.assertIsNone(
            validate_explicit_provider_payload_envelope(
                envelope
            )
        )
        self.assertIs(envelope.envelope_id, envelope_id)


class ExactTypeAndBlankTests(unittest.TestCase):
    def test_envelope_requires_exact_model_type_first(self):
        invalid = (
            None,
            object(),
            {},
            EnvelopeSubclass(
                "envelope-001",
                "market-provider-001",
                "market_fact",
                FIXED_CLOCK,
                "success",
                {"last": "1"},
                None,
                None,
            ),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^envelope must be "
                    "ExplicitProviderPayloadEnvelope$",
                ):
                    validate_explicit_provider_payload_envelope(
                        value
                    )

    def test_envelope_id_requires_exact_nonblank_str(self):
        for value in (None, 1, b"x", StringSubclass("e")):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^envelope_id must be str$",
                ):
                    validate_explicit_provider_payload_envelope(
                        make_envelope(envelope_id=value)
                    )
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^envelope_id must not be blank$",
                ):
                    validate_explicit_provider_payload_envelope(
                        make_envelope(envelope_id=value)
                    )

    def test_provider_id_requires_exact_nonblank_str(self):
        with self.assertRaisesRegex(
            TypeError,
            "^provider_id must be str$",
        ):
            validate_explicit_provider_payload_envelope(
                make_envelope(provider_id=StringSubclass("p"))
            )
        with self.assertRaisesRegex(
            ValueError,
            "^provider_id must not be blank$",
        ):
            validate_explicit_provider_payload_envelope(
                make_envelope(provider_id=" ")
            )

    def test_source_class_membership_is_exact(self):
        for value in (
            "MARKET_FACT",
            "market-fact",
            "primary",
            "secondary",
            "unknown",
            "broker",
            "",
            " market_fact",
        ):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^source_class must be one of "
                    "SOURCE_CLASS_VALUES$",
                ):
                    validate_explicit_provider_payload_envelope(
                        make_envelope(source_class=value)
                    )
        with self.assertRaisesRegex(
            TypeError,
            "^source_class must be str$",
        ):
            validate_explicit_provider_payload_envelope(
                make_envelope(
                    source_class=StringSubclass(
                        "market_fact"
                    )
                )
            )

    def test_collected_at_requires_utc_datetime(self):
        with self.assertRaisesRegex(
            TypeError,
            "^collected_at must be datetime$",
        ):
            validate_explicit_provider_payload_envelope(
                make_envelope(collected_at="2026-08-13")
            )
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
                    validate_explicit_provider_payload_envelope(
                        make_envelope(collected_at=value)
                    )

    def test_status_membership_and_payload_pairing(self):
        with self.assertRaisesRegex(
            ValueError,
            "^status must be one of ENVELOPE_STATUS_VALUES$",
        ):
            validate_explicit_provider_payload_envelope(
                make_envelope(status="SUCCESS")
            )
        with self.assertRaisesRegex(
            TypeError,
            "^payload must be dict$",
        ):
            validate_explicit_provider_payload_envelope(
                make_envelope(payload=DictSubclass())
            )
        with self.assertRaisesRegex(
            TypeError,
            "^payload must be None$",
        ):
            validate_explicit_provider_payload_envelope(
                make_envelope(
                    status="failure",
                    payload={"last": "1"},
                )
            )

    def test_error_diagnostics_nested_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "^error_diagnostics must be "
            "ExplicitErrorDiagnostics$",
        ):
            validate_explicit_provider_payload_envelope(
                make_envelope(
                    error_diagnostics=DiagnosticsSubclass(
                        "PROVIDER_ERROR",
                        None,
                    )
                )
            )

    def test_request_correlation_optional_nonblank(self):
        self.assertIsNone(
            validate_explicit_provider_payload_envelope(
                make_envelope(request_correlation_id=None)
            )
        )
        with self.assertRaisesRegex(
            ValueError,
            "^request_correlation_id must not be blank$",
        ):
            validate_explicit_provider_payload_envelope(
                make_envelope(request_correlation_id=" ")
            )


class MarketFactSuccessEnvelopeTests(unittest.TestCase):
    def test_rejects_success_with_non_market_fact(self):
        for source_class in ("broker_fact", "research_ai"):
            with self.subTest(source_class=source_class):
                with self.assertRaisesRegex(
                    ValueError,
                    "^source_class must be market_fact$",
                ):
                    validate_market_fact_success_envelope(
                        make_envelope(
                            source_class=source_class
                        )
                    )

    def test_rejects_failure_status(self):
        with self.assertRaisesRegex(
            ValueError,
            "^status must be success$",
        ):
            validate_market_fact_success_envelope(
                make_envelope(
                    status="failure",
                    payload=None,
                    error_diagnostics=make_diagnostics(),
                )
            )

    def test_rejects_reserved_kb_provider_id(self):
        with self.assertRaisesRegex(
            ValueError,
            "^provider_id must not be kb_open_api$",
        ):
            validate_market_fact_success_envelope(
                make_envelope(provider_id="kb_open_api")
            )


class BindingAndProfileTests(unittest.TestCase):
    def test_profile_request_set_rules(self):
        with self.assertRaisesRegex(
            TypeError,
            "^request_set must be tuple$",
        ):
            validate_explicit_market_parameter_profile(
                make_profile(request_set=["last_price"])
            )
        with self.assertRaisesRegex(
            TypeError,
            "^request_set must be tuple$",
        ):
            validate_explicit_market_parameter_profile(
                make_profile(
                    request_set=TupleSubclass(
                        ("last_price",)
                    )
                )
            )
        with self.assertRaisesRegex(
            ValueError,
            "^request_set must not be empty$",
        ):
            validate_explicit_market_parameter_profile(
                make_profile(request_set=())
            )
        with self.assertRaisesRegex(
            TypeError,
            r"^request_set\[0\] must be str$",
        ):
            validate_explicit_market_parameter_profile(
                make_profile(request_set=(1,))
            )
        with self.assertRaisesRegex(
            ValueError,
            r"^request_set\[0\] must not be blank$",
        ):
            validate_explicit_market_parameter_profile(
                make_profile(request_set=(" ",))
            )

    def test_binding_rejects_reserved_kb_provider_id(self):
        with self.assertRaisesRegex(
            ValueError,
            "^provider_id must not be kb_open_api$",
        ):
            validate_explicit_market_adapter_binding(
                make_binding(provider_id="kb_open_api")
            )

    def test_health_and_failure_vocabularies(self):
        for availability in AVAILABILITY_VALUES:
            self.assertIsNone(
                validate_explicit_provider_health_snapshot(
                    make_health(availability=availability)
                )
            )
        with self.assertRaisesRegex(
            ValueError,
            "^availability must be one of "
            "AVAILABILITY_VALUES$",
        ):
            validate_explicit_provider_health_snapshot(
                make_health(availability="up")
            )
        for failure_class in FAILURE_CLASS_VALUES:
            self.assertIsNone(
                validate_explicit_provider_failure_signal(
                    make_failure(failure_class=failure_class)
                )
            )
        with self.assertRaisesRegex(
            ValueError,
            "^failure_class must be one of "
            "FAILURE_CLASS_VALUES$",
        ):
            validate_explicit_provider_failure_signal(
                make_failure(failure_class="TIMEOUT")
            )

    def test_outcome_mutual_exclusion(self):
        with self.assertRaisesRegex(
            TypeError,
            "^failure must be None$",
        ):
            validate_explicit_collect_outcome(
                ExplicitCollectOutcome(
                    "success",
                    make_envelope(),
                    make_failure(),
                )
            )
        with self.assertRaisesRegex(
            TypeError,
            "^envelope must be None$",
        ):
            validate_explicit_collect_outcome(
                ExplicitCollectOutcome(
                    "failure",
                    make_envelope(),
                    make_failure(),
                )
            )
        with self.assertRaisesRegex(
            TypeError,
            "^envelope must be "
            "ExplicitProviderPayloadEnvelope$",
        ):
            validate_explicit_collect_outcome(
                ExplicitCollectOutcome("success", None, None)
            )
        with self.assertRaisesRegex(
            ValueError,
            "^result_kind must be one of "
            "ENVELOPE_STATUS_VALUES$",
        ):
            validate_explicit_collect_outcome(
                ExplicitCollectOutcome(
                    "ok",
                    make_envelope(),
                    None,
                )
            )


class ValidationOrderTests(unittest.TestCase):
    def test_first_failure_wins_on_envelope(self):
        envelope = make_envelope(
            envelope_id="",
            provider_id="",
            source_class="primary",
            collected_at=datetime(2026, 1, 1),
            status="SUCCESS",
            payload="bad",
        )
        with self.assertRaisesRegex(
            ValueError,
            "^envelope_id must not be blank$",
        ):
            validate_explicit_provider_payload_envelope(
                envelope
            )

    def test_upstream_diagnostics_exception_is_unchanged(self):
        error = ValueError("diagnostics failure")
        envelope = make_envelope(
            error_diagnostics=make_diagnostics()
        )
        with patch(
            "ProviderGateway.validation.validators"
            ".validate_explicit_error_diagnostics",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_provider_payload_envelope(
                    envelope
                )
        self.assertIs(caught.exception, error)

    def test_upstream_profile_exception_is_unchanged(self):
        error = ValueError("profile failure")
        binding = make_binding()
        with patch(
            "ProviderGateway.validation.validators"
            ".validate_explicit_market_parameter_profile",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_market_adapter_binding(
                    binding
                )
        self.assertIs(caught.exception, error)

    def test_market_fact_success_propagates_envelope_error(
        self,
    ):
        error = ValueError("envelope failure")
        with patch(
            "ProviderGateway.validation.validators"
            ".validate_explicit_provider_payload_envelope",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_market_fact_success_envelope(
                    make_envelope()
                )
        self.assertIs(caught.exception, error)

    def test_collect_request_propagates_binding_error(self):
        error = ValueError("binding failure")
        with patch(
            "ProviderGateway.validation.validators"
            ".validate_explicit_market_adapter_binding",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_collect_request(
                    make_request()
                )
        self.assertIs(caught.exception, error)


class BrokerValidationSuccessTests(unittest.TestCase):
    def test_broker_validators_return_none(self):
        self.assertIsNone(
            validate_explicit_broker_parameter_profile(
                make_broker_profile()
            )
        )
        self.assertIsNone(
            validate_explicit_broker_adapter_binding(
                make_broker_binding()
            )
        )
        self.assertIsNone(
            validate_explicit_broker_collect_request(
                make_broker_request()
            )
        )
        self.assertIsNone(
            validate_broker_fact_success_envelope(
                make_envelope(
                    provider_id="kb_open_api",
                    source_class="broker_fact",
                )
            )
        )

    def test_each_authorized_kind_is_accepted(self):
        for request_kind in BROKER_REQUEST_KIND_VALUES:
            with self.subTest(request_kind=request_kind):
                self.assertIsNone(
                    validate_explicit_broker_collect_request(
                        make_broker_request(
                            request_kind=request_kind
                        )
                    )
                )

    def test_duplicate_request_set_kinds_are_preserved(self):
        profile = make_broker_profile(
            request_set=("holdings", "holdings")
        )
        self.assertIsNone(
            validate_explicit_broker_parameter_profile(profile)
        )
        self.assertEqual(
            profile.request_set,
            ("holdings", "holdings"),
        )

    def test_surrounding_whitespace_is_preserved(self):
        selector = " account-001 "
        profile = make_broker_profile(
            account_selector=selector
        )
        self.assertIsNone(
            validate_explicit_broker_parameter_profile(profile)
        )
        self.assertIs(profile.account_selector, selector)


class BrokerExactTypeAndMembershipTests(unittest.TestCase):
    def test_profile_requires_exact_model_type_first(self):
        invalid = (
            None,
            object(),
            {},
            BrokerProfileSubclass(
                "broker-profile-001",
                "opaque-account-selector",
                ("holdings",),
            ),
        )
        for value in invalid:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^profile must be "
                    "ExplicitBrokerParameterProfile$",
                ):
                    validate_explicit_broker_parameter_profile(
                        value
                    )

    def test_request_set_rules(self):
        with self.assertRaisesRegex(
            TypeError,
            "^request_set must be tuple$",
        ):
            validate_explicit_broker_parameter_profile(
                make_broker_profile(request_set=["holdings"])
            )
        with self.assertRaisesRegex(
            TypeError,
            "^request_set must be tuple$",
        ):
            validate_explicit_broker_parameter_profile(
                make_broker_profile(
                    request_set=TupleSubclass(("holdings",))
                )
            )
        with self.assertRaisesRegex(
            ValueError,
            "^request_set must not be empty$",
        ):
            validate_explicit_broker_parameter_profile(
                make_broker_profile(request_set=())
            )
        with self.assertRaisesRegex(
            TypeError,
            r"^request_set\[0\] must be str$",
        ):
            validate_explicit_broker_parameter_profile(
                make_broker_profile(request_set=(1,))
            )
        with self.assertRaisesRegex(
            ValueError,
            r"^request_set\[0\] must not be blank$",
        ):
            validate_explicit_broker_parameter_profile(
                make_broker_profile(request_set=(" ",))
            )
        with self.assertRaisesRegex(
            ValueError,
            r"^request_set\[0\] must be one of "
            r"BROKER_REQUEST_KIND_VALUES$",
        ):
            validate_explicit_broker_parameter_profile(
                make_broker_profile(request_set=("orders",))
            )

    def test_rejects_orders_and_fills_as_request_kind(self):
        for request_kind in ("orders", "fills", "last_price"):
            with self.subTest(request_kind=request_kind):
                with self.assertRaisesRegex(
                    ValueError,
                    "^request_kind must be one of "
                    "BROKER_REQUEST_KIND_VALUES$",
                ):
                    validate_explicit_broker_collect_request(
                        make_broker_request(
                            request_kind=request_kind
                        )
                    )

    def test_request_kind_must_be_in_request_set(self):
        binding = make_broker_binding(
            parameter_profile=make_broker_profile(
                request_set=("balances",)
            )
        )
        with self.assertRaisesRegex(
            ValueError,
            "^request_kind must be in request_set$",
        ):
            validate_explicit_broker_collect_request(
                make_broker_request(
                    binding=binding,
                    request_kind="holdings",
                )
            )

    def test_binding_rejects_non_kb_provider_id(self):
        with self.assertRaisesRegex(
            ValueError,
            "^provider_id must be kb_open_api$",
        ):
            validate_explicit_broker_adapter_binding(
                make_broker_binding(
                    provider_id="other-broker"
                )
            )

    def test_binding_rejects_blank_before_kb_id(self):
        with self.assertRaisesRegex(
            ValueError,
            "^provider_id must not be blank$",
        ):
            validate_explicit_broker_adapter_binding(
                make_broker_binding(provider_id=" ")
            )

    def test_binding_requires_exact_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "^binding must be ExplicitBrokerAdapterBinding$",
        ):
            validate_explicit_broker_adapter_binding(
                BrokerBindingSubclass(
                    "kb_open_api",
                    "broker-cred-ref",
                    make_broker_profile(),
                )
            )

    def test_request_requires_exact_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "^request must be ExplicitBrokerCollectRequest$",
        ):
            validate_explicit_broker_collect_request(
                BrokerRequestSubclass(
                    "envelope-001",
                    None,
                    make_broker_binding(),
                    "holdings",
                )
            )
        with self.assertRaisesRegex(
            TypeError,
            "^request must be ExplicitBrokerCollectRequest$",
        ):
            validate_explicit_broker_collect_request(
                make_request()
            )


class BrokerFactSuccessEnvelopeTests(unittest.TestCase):
    def test_rejects_success_with_non_broker_fact(self):
        for source_class in ("market_fact", "research_ai"):
            with self.subTest(source_class=source_class):
                with self.assertRaisesRegex(
                    ValueError,
                    "^source_class must be broker_fact$",
                ):
                    validate_broker_fact_success_envelope(
                        make_envelope(
                            provider_id="kb_open_api",
                            source_class=source_class,
                        )
                    )

    def test_rejects_failure_status(self):
        with self.assertRaisesRegex(
            ValueError,
            "^status must be success$",
        ):
            validate_broker_fact_success_envelope(
                make_envelope(
                    provider_id="kb_open_api",
                    source_class="broker_fact",
                    status="failure",
                    payload=None,
                    error_diagnostics=make_diagnostics(),
                )
            )

    def test_rejects_non_kb_provider_id(self):
        with self.assertRaisesRegex(
            ValueError,
            "^provider_id must be kb_open_api$",
        ):
            validate_broker_fact_success_envelope(
                make_envelope(
                    provider_id="market-provider-001",
                    source_class="broker_fact",
                )
            )

    def test_market_success_still_rejects_kb_provider_id(self):
        with self.assertRaisesRegex(
            ValueError,
            "^provider_id must not be kb_open_api$",
        ):
            validate_market_fact_success_envelope(
                make_envelope(provider_id="kb_open_api")
            )

    def test_market_binding_still_rejects_kb_provider_id(self):
        with self.assertRaisesRegex(
            ValueError,
            "^provider_id must not be kb_open_api$",
        ):
            validate_explicit_market_adapter_binding(
                make_binding(provider_id="kb_open_api")
            )


class BrokerValidationOrderTests(unittest.TestCase):
    def test_first_failure_wins_on_profile(self):
        profile = make_broker_profile(
            profile_id="",
            account_selector="",
            request_set=(),
        )
        with self.assertRaisesRegex(
            ValueError,
            "^profile_id must not be blank$",
        ):
            validate_explicit_broker_parameter_profile(profile)

    def test_upstream_profile_exception_is_unchanged(self):
        error = ValueError("broker profile failure")
        binding = make_broker_binding()
        with patch(
            "ProviderGateway.validation.validators"
            ".validate_explicit_broker_parameter_profile",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_broker_adapter_binding(
                    binding
                )
        self.assertIs(caught.exception, error)

    def test_upstream_binding_exception_is_unchanged(self):
        error = ValueError("broker binding failure")
        with patch(
            "ProviderGateway.validation.validators"
            ".validate_explicit_broker_adapter_binding",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_explicit_broker_collect_request(
                    make_broker_request()
                )
        self.assertIs(caught.exception, error)

    def test_broker_fact_success_propagates_envelope_error(
        self,
    ):
        error = ValueError("envelope failure")
        with patch(
            "ProviderGateway.validation.validators"
            ".validate_explicit_provider_payload_envelope",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as caught:
                validate_broker_fact_success_envelope(
                    make_envelope(
                        provider_id="kb_open_api",
                        source_class="broker_fact",
                    )
                )
        self.assertIs(caught.exception, error)


if __name__ == "__main__":
    unittest.main()
