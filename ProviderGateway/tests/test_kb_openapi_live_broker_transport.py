from __future__ import annotations

import ast
import inspect
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from FactStore.models.types import ExplicitFactAppendRequest
from FactStore.store import FactStore
from ProviderGateway.adapters.kb_open_api import KbOpenApiAdapter
from ProviderGateway.adapters.kb_openapi_live_broker_transport import (
    DEFAULT_BASE_URL,
    TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS,
    KbOpenApiHttpResponse,
    KbOpenApiLiveBrokerTransport,
    decode_kb_openapi_client_material,
)
from ProviderGateway.adapters.ports import (
    BrokerTransport,
    ExplicitHealthProbe,
    ExplicitTransportFailure,
    ExplicitTransportSuccess,
    MarketTransport,
)
from ProviderGateway.provider_interface import ProviderInterface
from ProviderGateway.tests.builders import (
    FakeBrokerTransport,
    broker_credential_supplier,
    make_broker_binding,
    make_broker_request,
)


UTC = timezone.utc
FIXED_CLOCK = datetime(2026, 8, 18, 12, 0, tzinfo=UTC)
FAKE_APP_KEY = "test-app-key"
FAKE_APP_SECRET = "test-app-secret"
FAKE_ACCESS_TOKEN = "test-access-token"
FAKE_ACCESS_TOKEN_2 = "test-access-token-2"
FAKE_CREDENTIAL = json.dumps(
    {"appKey": FAKE_APP_KEY, "appSecret": FAKE_APP_SECRET},
    separators=(",", ":"),
)
TRANSPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "adapters"
    / "kb_openapi_live_broker_transport.py"
)
FAKE_IP = "10.0.0.1"
FAKE_MAC = "aa:bb:cc:dd:ee:ff"
OAUTH_URL = DEFAULT_BASE_URL + "/oauth2/token"
SSQM2952_URL = DEFAULT_BASE_URL + "/api/v1/ssqm2952"
EXPECTED_OAUTH_BODY = (
    '{"dataHeader":{"ipAddr":"10.0.0.1","macAddr":"aa:bb:cc:dd:ee:ff"},'
    '"dataBody":{"appKey":"test-app-key","appSecret":"test-app-secret",'
    '"grantType":"client_credentials"}}'
).encode("utf-8")
EXPECTED_SSQM2952_BODY = (
    '{"dataHeader":{"ipAddr":"10.0.0.1","macAddr":"aa:bb:cc:dd:ee:ff"},'
    '"dataBody":{"excg_mktpr_ccd":""}}'
).encode("utf-8")


def oauth_success_payload(access_token=FAKE_ACCESS_TOKEN, expires_in=86400):
    return {
        "dataHeader": {
            "processFlag": "A",
            "processCode": "0000",
        },
        "dataBody": {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
        },
    }


def ssqm2952_success_payload():
    return {
        "dataHeader": {
            "processFlag": "A",
            "processCode": "0011",
            "processMessage": "",
            "o_msg": "정상적으로 조회되었습니다.",
        },
        "dataBody": {
            "excg_mktpr_ccd": "",
            "o_msg": "정상적으로 조회되었습니다.",
            "Record1": [
                {
                    "is_cd": "005930",
                    "hld_q": "000000000010",
                }
            ],
        },
    }


def http_json(payload, status_code=200):
    return KbOpenApiHttpResponse(
        status_code,
        json.dumps(payload, ensure_ascii=False),
    )


class RecordingHttp:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, headers, body, timeout_seconds):
        self.calls.append(
            {
                "url": url,
                "headers": dict(headers),
                "body": body,
                "timeout_seconds": timeout_seconds,
            }
        )
        if not self.responses:
            raise AssertionError("unexpected HTTP call")
        item = self.responses.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


class FakeClock:
    def __init__(self, moment=FIXED_CLOCK):
        self.moment = moment

    def __call__(self):
        return self.moment

    def advance(self, seconds):
        self.moment = self.moment + timedelta(seconds=seconds)


def make_transport(http, clock=None, **overrides):
    values = {
        "http_post": http,
        "clock": FakeClock() if clock is None else clock,
        "ip_addr": FAKE_IP,
        "mac_addr": FAKE_MAC,
    }
    values.update(overrides)
    return KbOpenApiLiveBrokerTransport(**values)


def read_holdings(transport, credential=FAKE_CREDENTIAL):
    return transport.read(
        make_broker_binding(),
        credential,
        make_broker_request(),
    )


class CredentialDecoderTests(unittest.TestCase):
    def test_valid_credential_decoding(self):
        decoded = decode_kb_openapi_client_material(FAKE_CREDENTIAL)
        self.assertEqual(decoded, (FAKE_APP_KEY, FAKE_APP_SECRET))

    def test_json_whitespace_around_object_is_allowed(self):
        decoded = decode_kb_openapi_client_material(
            ' \n{"appKey":"test-app-key","appSecret":"test-app-secret"}\n '
        )
        self.assertEqual(decoded, (FAKE_APP_KEY, FAKE_APP_SECRET))

    def test_key_order_does_not_matter(self):
        decoded = decode_kb_openapi_client_material(
            '{"appSecret":"test-app-secret","appKey":"test-app-key"}'
        )
        self.assertEqual(decoded, (FAKE_APP_KEY, FAKE_APP_SECRET))

    def test_values_are_not_trimmed(self):
        decoded = decode_kb_openapi_client_material(
            '{"appKey":" test-app-key ","appSecret":" test-app-secret "}'
        )
        self.assertEqual(
            decoded,
            (" test-app-key ", " test-app-secret "),
        )

    def test_malformed_credential_fail_closed(self):
        cases = (
            None,
            1,
            "",
            "{",
            "[]",
            "null",
            '"x"',
            '{"appKey":"test-app-key"}',
            '{"appSecret":"test-app-secret"}',
            '{"appKey":"test-app-key","appSecret":"test-app-secret","x":"1"}',
            '{"app_key":"test-app-key","appSecret":"test-app-secret"}',
            '{"appKey":"test-app-key","grantType":"client_credentials"}',
            '{"appKey":"test-app-key","grant_type":"client_credentials"}',
            '{"appKey":1,"appSecret":"test-app-secret"}',
            '{"appKey":"test-app-key","appSecret":""}',
            '{"appKey":"","appSecret":"test-app-secret"}',
        )
        for credential in cases:
            with self.subTest(credential=repr(credential)):
                self.assertIsNone(
                    decode_kb_openapi_client_material(credential)
                )
                result = read_holdings(
                    make_transport(
                        RecordingHttp(
                            [http_json(oauth_success_payload())]
                        )
                    ),
                    credential=credential,
                )
                self.assertIsInstance(result, ExplicitTransportFailure)
                self.assertEqual(result.failure_class, "AUTH_FAILURE")
                self.assertIsNone(result.detail)

    def test_no_secret_in_repr_exceptions_or_details(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(ssqm2952_success_payload()),
            ]
        )
        transport = make_transport(http)
        result = read_holdings(transport)
        self.assertIsInstance(result, ExplicitTransportSuccess)
        rendered = repr(transport) + repr(result)
        self.assertNotIn(FAKE_APP_SECRET, rendered)
        self.assertNotIn(FAKE_ACCESS_TOKEN, rendered)
        failure = read_holdings(
            make_transport(RecordingHttp([])),
            credential="not-json",
        )
        self.assertEqual(failure.failure_class, "AUTH_FAILURE")
        self.assertIsNone(failure.detail)
        self.assertNotIn(FAKE_APP_KEY, repr(failure))
        self.assertNotIn(FAKE_APP_SECRET, repr(failure))


class ConstructorAndProbeTests(unittest.TestCase):
    def test_constructor_rejects_invalid_config(self):
        valid = {
            "http_post": RecordingHttp([]),
            "clock": FakeClock(),
            "ip_addr": FAKE_IP,
            "mac_addr": FAKE_MAC,
        }
        cases = (
            {"http_post": None},
            {"clock": None},
            {"clock": object()},
            {"ip_addr": ""},
            {"ip_addr": "   "},
            {"ip_addr": 1},
            {"mac_addr": ""},
            {"mac_addr": 1},
            {"base_url": "http://developer.kbsec.com:32484"},
            {"base_url": "developer.kbsec.com:32484"},
            {"base_url": 1},
            {"excg_mktpr_ccd": "X"},
            {"excg_mktpr_ccd": "a"},
            {"http_timeout_seconds": True},
            {"http_timeout_seconds": 0},
            {"http_timeout_seconds": -1},
            {"http_timeout_seconds": 10.0},
        )
        for overrides in cases:
            with self.subTest(overrides=overrides):
                values = dict(valid)
                values.update(overrides)
                with self.assertRaises(ValueError):
                    KbOpenApiLiveBrokerTransport(**values)

    def test_probe_is_local_availability_only(self):
        http = RecordingHttp(
            [http_json(oauth_success_payload())]
        )
        transport = make_transport(http)
        probe = transport.probe(make_broker_binding())
        self.assertEqual(
            probe,
            ExplicitHealthProbe("available", None),
        )
        self.assertEqual(http.calls, [])


class OAuthSerializationTests(unittest.TestCase):
    def test_oauth_request_exact_compact_json_and_path(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(ssqm2952_success_payload()),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertIsInstance(result, ExplicitTransportSuccess)
        oauth = http.calls[0]
        self.assertEqual(oauth["url"], OAUTH_URL)
        self.assertEqual(
            oauth["headers"],
            {"Content-Type": "application/json"},
        )
        self.assertNotIn("Authorization", oauth["headers"])
        self.assertEqual(oauth["body"], EXPECTED_OAUTH_BODY)
        self.assertNotIn(b"grant_type", oauth["body"])
        self.assertIn(b"grantType", oauth["body"])
        self.assertEqual(oauth["timeout_seconds"], 10)
        self.assertNotIn(b"?", oauth["url"].encode("utf-8"))

    def test_oauth_token_success_then_ssqm2952(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(ssqm2952_success_payload()),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertIsInstance(result, ExplicitTransportSuccess)
        self.assertEqual(len(http.calls), 2)
        self.assertEqual(http.calls[0]["url"], OAUTH_URL)
        self.assertEqual(http.calls[1]["url"], SSQM2952_URL)

    def test_missing_access_token_is_auth_failure_without_ssqm(self):
        payload = oauth_success_payload()
        del payload["dataBody"]["access_token"]
        http = RecordingHttp([http_json(payload)])
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "AUTH_FAILURE")
        self.assertIsNone(result.detail)
        self.assertEqual(len(http.calls), 1)
        self.assertEqual(http.calls[0]["url"], OAUTH_URL)

    def test_flat_candidate_a_body_is_auth_failure(self):
        http = RecordingHttp(
            [
                http_json(
                    {
                        "access_token": FAKE_ACCESS_TOKEN,
                        "token_type": "Bearer",
                        "expires_in": 86400,
                        "grant_type": "client_credentials",
                    }
                )
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "AUTH_FAILURE")
        self.assertEqual(len(http.calls), 1)
        self.assertEqual(http.calls[0]["url"], OAUTH_URL)


class TokenCacheTests(unittest.TestCase):
    def test_token_reuse_before_expiry_makes_zero_second_oauth(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(ssqm2952_success_payload()),
                http_json(ssqm2952_success_payload()),
            ]
        )
        transport = make_transport(http)
        first = read_holdings(transport)
        second = read_holdings(transport)
        self.assertIsInstance(first, ExplicitTransportSuccess)
        self.assertIsInstance(second, ExplicitTransportSuccess)
        urls = [call["url"] for call in http.calls]
        self.assertEqual(
            urls,
            [OAUTH_URL, SSQM2952_URL, SSQM2952_URL],
        )

    def test_token_reissue_after_injected_clock_expiry(self):
        clock = FakeClock()
        http = RecordingHttp(
            [
                http_json(oauth_success_payload(expires_in=61)),
                http_json(ssqm2952_success_payload()),
                http_json(
                    oauth_success_payload(
                        FAKE_ACCESS_TOKEN_2,
                        expires_in=61,
                    )
                ),
                http_json(ssqm2952_success_payload()),
            ]
        )
        transport = make_transport(http, clock=clock)
        first = read_holdings(transport)
        clock.advance(TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS)
        clock.advance(1)
        second = read_holdings(transport)
        self.assertIsInstance(first, ExplicitTransportSuccess)
        self.assertIsInstance(second, ExplicitTransportSuccess)
        urls = [call["url"] for call in http.calls]
        self.assertEqual(
            urls,
            [OAUTH_URL, SSQM2952_URL, OAUTH_URL, SSQM2952_URL],
        )
        self.assertEqual(
            http.calls[3]["headers"]["Authorization"],
            "Bearer " + FAKE_ACCESS_TOKEN_2,
        )

    def test_unusable_expires_in_is_one_shot_not_cached(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload(expires_in=60)),
                http_json(ssqm2952_success_payload()),
                http_json(
                    oauth_success_payload(FAKE_ACCESS_TOKEN_2)
                ),
                http_json(ssqm2952_success_payload()),
            ]
        )
        transport = make_transport(http)
        first = read_holdings(transport)
        second = read_holdings(transport)
        self.assertIsInstance(first, ExplicitTransportSuccess)
        self.assertIsInstance(second, ExplicitTransportSuccess)
        urls = [call["url"] for call in http.calls]
        self.assertEqual(
            urls,
            [OAUTH_URL, SSQM2952_URL, OAUTH_URL, SSQM2952_URL],
        )

    def test_one_bounded_401_retry_only(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                KbOpenApiHttpResponse(401, "{}"),
                http_json(
                    oauth_success_payload(FAKE_ACCESS_TOKEN_2)
                ),
                http_json(ssqm2952_success_payload()),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertIsInstance(result, ExplicitTransportSuccess)
        urls = [call["url"] for call in http.calls]
        self.assertEqual(
            urls,
            [OAUTH_URL, SSQM2952_URL, OAUTH_URL, SSQM2952_URL],
        )
        self.assertEqual(
            http.calls[3]["headers"]["Authorization"],
            "Bearer " + FAKE_ACCESS_TOKEN_2,
        )

    def test_still_unauthorized_after_retry_is_auth_failure(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                KbOpenApiHttpResponse(401, "{}"),
                http_json(
                    oauth_success_payload(FAKE_ACCESS_TOKEN_2)
                ),
                KbOpenApiHttpResponse(401, "{}"),
                http_json(oauth_success_payload("should-not-use")),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "AUTH_FAILURE")
        self.assertIsNone(result.detail)
        urls = [call["url"] for call in http.calls]
        self.assertEqual(
            urls,
            [OAUTH_URL, SSQM2952_URL, OAUTH_URL, SSQM2952_URL],
        )

    def test_oauth_429_is_rate_limited_without_retry_or_ssqm(self):
        http = RecordingHttp(
            [
                KbOpenApiHttpResponse(429, "{}"),
                http_json(oauth_success_payload()),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "RATE_LIMITED")
        self.assertIsNone(result.detail)
        self.assertEqual(len(http.calls), 1)
        self.assertEqual(http.calls[0]["url"], OAUTH_URL)

    def test_oauth_process_flag_b_is_auth_failure(self):
        payload = oauth_success_payload()
        payload["dataHeader"]["processFlag"] = "B"
        http = RecordingHttp([http_json(payload)])
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "AUTH_FAILURE")
        self.assertEqual(len(http.calls), 1)

    def test_deterministic_injected_clock(self):
        clock = FakeClock(FIXED_CLOCK)
        http = RecordingHttp(
            [
                http_json(oauth_success_payload(expires_in=120)),
                http_json(ssqm2952_success_payload()),
            ]
        )
        transport = make_transport(http, clock=clock)
        result = read_holdings(transport)
        self.assertIsInstance(result, ExplicitTransportSuccess)
        expected_expiry = FIXED_CLOCK + timedelta(
            seconds=120 - TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS
        )
        self.assertEqual(transport._expires_at, expected_expiry)
        self.assertEqual(clock.moment, FIXED_CLOCK)


class Ssqm2952SerializationTests(unittest.TestCase):
    def test_ssqm2952_exact_request_serialization(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(ssqm2952_success_payload()),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertIsInstance(result, ExplicitTransportSuccess)
        ssqm = http.calls[1]
        self.assertEqual(ssqm["url"], SSQM2952_URL)
        self.assertEqual(ssqm["body"], EXPECTED_SSQM2952_BODY)
        self.assertNotIn(b"account_selector", ssqm["body"])
        self.assertNotIn(b"grant_type", ssqm["body"])
        self.assertEqual(ssqm["timeout_seconds"], 10)

    def test_authorization_bearer_header(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(ssqm2952_success_payload()),
            ]
        )
        read_holdings(make_transport(http))
        self.assertEqual(
            http.calls[1]["headers"],
            {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + FAKE_ACCESS_TOKEN,
            },
        )

    def test_successful_payload_returned_unchanged(self):
        payload = ssqm2952_success_payload()
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(payload),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertIsInstance(result, ExplicitTransportSuccess)
        self.assertEqual(result.body, payload)
        self.assertEqual(
            result.body["dataBody"]["Record1"][0]["hld_q"],
            "000000000010",
        )
        self.assertIn("dataHeader", result.body)
        self.assertIn("dataBody", result.body)
        self.assertNotIn("access_token", result.body)
        self.assertNotIn("access_token", result.body["dataBody"])

    def test_process_flag_b_is_provider_error_not_empty_holdings(self):
        payload = ssqm2952_success_payload()
        payload["dataHeader"]["processFlag"] = "B"
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(payload),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "PROVIDER_ERROR")
        self.assertIsNone(result.detail)
        self.assertFalse(hasattr(result, "body"))
        self.assertNotIsInstance(result, ExplicitTransportSuccess)

    def test_kb_http_500_is_provider_error(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                KbOpenApiHttpResponse(500, "{}"),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "PROVIDER_ERROR")
        self.assertIsNone(result.detail)

    def test_kb_http_429_is_rate_limited_without_retry(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                KbOpenApiHttpResponse(429, "{}"),
                http_json(ssqm2952_success_payload()),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "RATE_LIMITED")
        self.assertIsNone(result.detail)
        self.assertEqual(len(http.calls), 2)

    def test_malformed_kb_json_is_validation_failure(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                KbOpenApiHttpResponse(200, "{"),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "VALIDATION_FAILURE")
        self.assertIsNone(result.detail)

    def test_unsupported_request_kinds_do_not_call_http(self):
        for request_kind in ("balances", "account_state"):
            with self.subTest(request_kind=request_kind):
                http = RecordingHttp(
                    [http_json(oauth_success_payload())]
                )
                transport = make_transport(http)
                result = transport.read(
                    make_broker_binding(),
                    FAKE_CREDENTIAL,
                    make_broker_request(request_kind=request_kind),
                )
                self.assertEqual(
                    result.failure_class,
                    "VALIDATION_FAILURE",
                )
                self.assertEqual(http.calls, [])
                self.assertNotIn(
                    "/api/v1/ssam",
                    json.dumps([call["url"] for call in http.calls]),
                )


class ResidualSecretTests(unittest.TestCase):
    def test_residual_app_key_detection(self):
        payload = ssqm2952_success_payload()
        payload["dataBody"]["note"] = FAKE_APP_KEY
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(payload),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "VALIDATION_FAILURE")
        self.assertIsNone(result.detail)

    def test_residual_app_secret_detection(self):
        payload = ssqm2952_success_payload()
        payload["dataBody"]["Record1"][0]["leak"] = FAKE_APP_SECRET
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(payload),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "VALIDATION_FAILURE")
        self.assertIsNone(result.detail)

    def test_residual_access_token_detection(self):
        payload = ssqm2952_success_payload()
        payload["dataBody"]["access_token"] = FAKE_ACCESS_TOKEN
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(payload),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "VALIDATION_FAILURE")
        self.assertIsNone(result.detail)

    def test_nested_forbidden_key_is_detected(self):
        payload = ssqm2952_success_payload()
        payload["dataBody"]["Record1"][0]["appKey"] = "nested"
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(payload),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "VALIDATION_FAILURE")
        self.assertIsNone(result.detail)

    def test_token_response_never_becomes_broker_fact(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(ssqm2952_success_payload()),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertIsInstance(result, ExplicitTransportSuccess)
        self.assertNotEqual(result.body, oauth_success_payload())
        self.assertIn("Record1", result.body["dataBody"])
        self.assertNotIn("token_type", result.body)
        self.assertNotIn("expires_in", result.body)
        self.assertNotIn("access_token", result.body)


class GatewayAndCompatibilityTests(unittest.TestCase):
    def test_gateway_envelope_provider_id_and_source_class_unchanged(self):
        adapter_clock = FakeClock(
            datetime(2026, 1, 1, 9, 0, tzinfo=UTC)
        )
        transport_clock = FakeClock(FIXED_CLOCK)
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(ssqm2952_success_payload()),
            ]
        )
        transport = make_transport(http, clock=transport_clock)
        adapter = KbOpenApiAdapter(
            make_broker_binding(),
            transport,
            broker_credential_supplier(FAKE_CREDENTIAL),
            adapter_clock,
        )
        self.assertIsInstance(adapter, ProviderInterface)
        outcome = adapter.collect(make_broker_request())
        self.assertEqual(outcome.result_kind, "success")
        envelope = outcome.envelope
        self.assertEqual(envelope.provider_id, "kb_open_api")
        self.assertEqual(envelope.source_class, "broker_fact")
        self.assertEqual(envelope.status, "success")
        self.assertEqual(
            envelope.collected_at,
            datetime(2026, 1, 1, 9, 0, tzinfo=UTC),
        )
        self.assertNotEqual(envelope.collected_at, FIXED_CLOCK)
        self.assertEqual(
            envelope.payload["dataBody"]["Record1"][0]["hld_q"],
            "000000000010",
        )
        self.assertNotIn("access_token", envelope.payload)

    def test_fake_broker_transport_still_satisfies_the_port(self):
        fake = FakeBrokerTransport()
        live = make_transport(RecordingHttp([]))
        for transport in (fake, live):
            self.assertTrue(callable(transport.read))
            self.assertTrue(callable(transport.probe))
            signature = inspect.signature(transport.read)
            self.assertEqual(
                list(signature.parameters),
                ["binding", "credential", "request"],
            )
            probe_signature = inspect.signature(transport.probe)
            self.assertEqual(
                list(probe_signature.parameters),
                ["binding"],
            )
        adapter = KbOpenApiAdapter(
            make_broker_binding(),
            fake,
            broker_credential_supplier(),
            FakeClock(),
        )
        outcome = adapter.collect(make_broker_request())
        self.assertEqual(outcome.result_kind, "success")
        self.assertEqual(outcome.envelope.source_class, "broker_fact")

    def test_collect_recipe_can_append_to_factstore(self):
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(ssqm2952_success_payload()),
            ]
        )
        adapter = KbOpenApiAdapter(
            make_broker_binding(),
            make_transport(http),
            broker_credential_supplier(FAKE_CREDENTIAL),
            FakeClock(),
        )
        outcome = adapter.collect(make_broker_request())
        store = FactStore(FakeClock())
        record = store.append(
            ExplicitFactAppendRequest(
                "fact-001",
                outcome.envelope,
                None,
            )
        )
        self.assertEqual(record.source_class, "broker_fact")
        self.assertEqual(record.provider_id, "kb_open_api")
        self.assertIn("dataHeader", record.payload)
        self.assertIn("dataBody", record.payload)
        self.assertNotIn("appKey", record.payload)
        self.assertNotIn("appSecret", record.payload)
        self.assertNotIn("access_token", record.payload)

    def test_injected_client_exception_is_transport_failure(self):
        http = RecordingHttp([TimeoutError("timed out")])
        result = read_holdings(make_transport(http))
        self.assertEqual(result.failure_class, "TRANSPORT_FAILURE")
        self.assertIsNone(result.detail)
        self.assertNotIn("timed out", repr(result))


class ProductionBoundaryTests(unittest.TestCase):
    def test_production_live_transport_does_not_name_factstore(self):
        source = TRANSPORT_PATH.read_text()
        self.assertNotIn("FactStore", source)
        self.assertNotIn("quantity_payload_key", source)
        self.assertNotIn("PortfolioSnapshot", source)
        self.assertNotIn("MarketSnapshot", source)

    def test_no_snapshot_produce_or_nested_path_claim(self):
        source = TRANSPORT_PATH.read_text()
        self.assertNotIn("produce(", source)
        self.assertNotIn("dataBody.Record1", source)
        payload = ssqm2952_success_payload()
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(payload),
            ]
        )
        result = read_holdings(make_transport(http))
        self.assertEqual(
            result.body["dataBody"]["Record1"],
            payload["dataBody"]["Record1"],
        )

    def test_no_ssam_or_order_paths(self):
        source = TRANSPORT_PATH.read_text()
        lowered = source.casefold()
        self.assertNotIn("/api/v1/ssam", lowered)
        self.assertNotIn("ssam1802", lowered)
        self.assertNotIn("ssqm1802", lowered)
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(ssqm2952_success_payload()),
            ]
        )
        read_holdings(make_transport(http))
        for call in http.calls:
            self.assertNotIn("ssam", call["url"].casefold())
            self.assertNotIn("ssqm1802", call["url"].casefold())

    def test_class_is_not_market_transport(self):
        source = TRANSPORT_PATH.read_text()
        self.assertNotIn("MarketTransport", source)
        self.assertNotIn("IVU", source)
        self.assertNotIn("/api/v1/ivu", source.casefold())
        self.assertNotIn("/api/v1/gs", source.casefold())
        self.assertNotEqual(
            KbOpenApiLiveBrokerTransport.__name__,
            MarketTransport.__name__,
        )
        self.assertTrue(
            callable(getattr(BrokerTransport, "read", None))
        )

    def test_no_live_network_imports_or_wall_clock(self):
        source = TRANSPORT_PATH.read_text()
        self.assertNotIn("datetime.now", source)
        self.assertNotIn("datetime.utcnow", source)
        self.assertNotIn("urlopen", source)
        self.assertNotIn("developer.kbsec.com", source.split("https://")[0])
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported.add(node.module.split(".")[0])
        self.assertTrue(
            imported.isdisjoint(
                {
                    "socket",
                    "urllib",
                    "http",
                    "requests",
                    "httpx",
                    "ssl",
                    "AIAdapter",
                }
            ),
            imported,
        )
        self.assertIn("json", imported)

    def test_no_real_credentials_in_fixtures(self):
        source = Path(__file__).read_text()
        self.assertIn("test-app-key", source)
        self.assertIn("test-app-secret", source)
        self.assertIn(FAKE_APP_KEY, source)
        self.assertIn(FAKE_APP_SECRET, source)
        self.assertNotRegex(
            source,
            r'appSecret":\s*"[A-Za-z0-9]{24,}"',
        )


if __name__ == "__main__":
    unittest.main()
