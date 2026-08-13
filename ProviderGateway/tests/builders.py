from __future__ import annotations

from datetime import datetime, timezone

from ProviderGateway.adapters.ports import (
    ExplicitHealthProbe,
    ExplicitTransportFailure,
    ExplicitTransportSuccess,
)
from ProviderGateway.models.types import (
    ExplicitBrokerAdapterBinding,
    ExplicitBrokerCollectRequest,
    ExplicitBrokerParameterProfile,
    ExplicitCollectRequest,
    ExplicitErrorDiagnostics,
    ExplicitMarketAdapterBinding,
    ExplicitMarketParameterProfile,
    ExplicitProviderFailureSignal,
    ExplicitProviderHealthSnapshot,
    ExplicitProviderPayloadEnvelope,
)


UTC = timezone.utc
FIXED_CLOCK = datetime(2026, 8, 13, 12, 0, tzinfo=UTC)


def utc_now():
    return FIXED_CLOCK


def make_diagnostics(**overrides):
    values = {
        "failure_class": "PROVIDER_ERROR",
        "detail": "provider reported an error",
    }
    values.update(overrides)
    return ExplicitErrorDiagnostics(**values)


def make_envelope(**overrides):
    values = {
        "envelope_id": "envelope-001",
        "provider_id": "market-provider-001",
        "source_class": "market_fact",
        "collected_at": FIXED_CLOCK,
        "status": "success",
        "payload": {"last": "10.00", "venue": "opaque-venue"},
        "error_diagnostics": None,
        "request_correlation_id": "corr-001",
    }
    values.update(overrides)
    return ExplicitProviderPayloadEnvelope(**values)


def make_health(**overrides):
    values = {
        "provider_id": "market-provider-001",
        "observed_at": FIXED_CLOCK,
        "availability": "available",
        "detail": None,
    }
    values.update(overrides)
    return ExplicitProviderHealthSnapshot(**values)


def make_failure(**overrides):
    values = {
        "provider_id": "market-provider-001",
        "observed_at": FIXED_CLOCK,
        "failure_class": "TRANSPORT_FAILURE",
        "detail": None,
        "request_correlation_id": "corr-001",
    }
    values.update(overrides)
    return ExplicitProviderFailureSignal(**values)


def make_profile(**overrides):
    values = {
        "profile_id": "profile-001",
        "venue_target": "primary-venue-capable",
        "session_selector": "regular",
        "timezone_selector": "opaque-timezone",
        "calendar_selector": "opaque-calendar",
        "request_set": ("last_price", "market_status"),
    }
    values.update(overrides)
    return ExplicitMarketParameterProfile(**values)


def make_korea_profile(**overrides):
    values = {
        "profile_id": "korea-capable-001",
        "venue_target": "korea-market-capable",
        "session_selector": "regular",
        "timezone_selector": "korea-timezone",
        "calendar_selector": "korea-calendar",
        "request_set": ("last_price", "market_status"),
    }
    values.update(overrides)
    return ExplicitMarketParameterProfile(**values)


def make_us_profile(**overrides):
    values = {
        "profile_id": "us-capable-001",
        "venue_target": "us-market-capable",
        "session_selector": "regular",
        "timezone_selector": "us-timezone",
        "calendar_selector": "us-calendar",
        "request_set": ("last_price", "market_status"),
    }
    values.update(overrides)
    return ExplicitMarketParameterProfile(**values)


def make_binding(**overrides):
    values = {
        "provider_id": "market-provider-001",
        "credential_ref": "market-cred-ref",
        "parameter_profile": make_profile(),
    }
    values.update(overrides)
    return ExplicitMarketAdapterBinding(**values)


def make_request(**overrides):
    values = {
        "envelope_id": "envelope-001",
        "request_correlation_id": "corr-001",
        "binding": make_binding(),
    }
    values.update(overrides)
    return ExplicitCollectRequest(**values)


class FakeTransport:
    def __init__(
        self,
        result=None,
        probe=None,
        raise_on_read=None,
        raise_on_probe=None,
    ):
        if result is None:
            result = ExplicitTransportSuccess(
                {
                    "last": "10.00",
                    "venue": "opaque-venue",
                    "session": "regular",
                    "timezone": "opaque-timezone",
                    "calendar": "opaque-calendar",
                    "exchange_time": "2026-01-01T09:00:00+09:00",
                }
            )
        if probe is None:
            probe = ExplicitHealthProbe("available", None)
        self.result = result
        self.probe_result = probe
        self.raise_on_read = raise_on_read
        self.raise_on_probe = raise_on_probe
        self.reads = []
        self.probes = []

    def read(self, binding, credential, request):
        self.reads.append(
            {
                "binding": binding,
                "credential": credential,
                "request": request,
            }
        )
        if self.raise_on_read is not None:
            raise self.raise_on_read
        return self.result

    def probe(self, binding):
        self.probes.append(binding)
        if self.raise_on_probe is not None:
            raise self.raise_on_probe
        return self.probe_result


def credential_supplier(secret="outbound-secret"):
    def supply(credential_ref):
        if credential_ref != "market-cred-ref":
            raise ValueError("unknown credential_ref")
        return secret

    return supply


def make_broker_profile(**overrides):
    values = {
        "profile_id": "broker-profile-001",
        "account_selector": "opaque-account-selector",
        "request_set": (
            "holdings",
            "balances",
            "account_state",
        ),
    }
    values.update(overrides)
    return ExplicitBrokerParameterProfile(**values)


def make_broker_binding(**overrides):
    values = {
        "provider_id": "kb_open_api",
        "credential_ref": "broker-cred-ref",
        "parameter_profile": make_broker_profile(),
    }
    values.update(overrides)
    return ExplicitBrokerAdapterBinding(**values)


def make_broker_request(**overrides):
    values = {
        "envelope_id": "envelope-001",
        "request_correlation_id": "corr-001",
        "binding": make_broker_binding(),
        "request_kind": "holdings",
    }
    values.update(overrides)
    return ExplicitBrokerCollectRequest(**values)


class FakeBrokerTransport:
    def __init__(
        self,
        result=None,
        probe=None,
        raise_on_read=None,
        raise_on_probe=None,
    ):
        if result is None:
            result = ExplicitTransportSuccess(
                {
                    "holdings": "opaque-holdings",
                    "account": "opaque-account",
                }
            )
        if probe is None:
            probe = ExplicitHealthProbe("available", None)
        self.result = result
        self.probe_result = probe
        self.raise_on_read = raise_on_read
        self.raise_on_probe = raise_on_probe
        self.reads = []
        self.probes = []

    def read(self, binding, credential, request):
        self.reads.append(
            {
                "binding": binding,
                "credential": credential,
                "request": request,
            }
        )
        if self.raise_on_read is not None:
            raise self.raise_on_read
        return self.result

    def probe(self, binding):
        self.probes.append(binding)
        if self.raise_on_probe is not None:
            raise self.raise_on_probe
        return self.probe_result


def broker_credential_supplier(secret="broker-outbound-secret"):
    def supply(credential_ref):
        if credential_ref != "broker-cred-ref":
            raise ValueError("unknown credential_ref")
        return secret

    return supply
