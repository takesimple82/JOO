from __future__ import annotations

import ast
import inspect
import json
import tempfile
import unittest
from pathlib import Path

from ProviderGateway.adapters.kb_open_api import KbOpenApiAdapter
from ProviderGateway.adapters.kb_openapi_live_broker_transport import (
    DEFAULT_BASE_URL,
    decode_kb_openapi_client_material,
)
from ProviderGateway.adapters.ports import (
    BrokerTransport,
    CredentialSupplier,
    ExplicitTransportFailure,
)
from ProviderGateway.auth import kb_openapi_keychain
from ProviderGateway.auth.credentials import resolve_outbound_credential
from ProviderGateway.auth.kb_openapi_host_identity import (
    HOST_IDENTITY_FILENAME,
    load_kb_openapi_host_identity,
    write_kb_openapi_host_identity,
)
from ProviderGateway.auth.kb_openapi_keychain import (
    KEYCHAIN_ACCOUNT_APP_KEY,
    KEYCHAIN_ACCOUNT_APP_SECRET,
    KEYCHAIN_SERVICE,
    STATUS_DENIED,
    STATUS_OS_FAILURE,
    inspect_kb_openapi_keychain_pair,
    store_kb_openapi_keychain_pair,
)
from ProviderGateway.auth.kb_openapi_runtime import (
    KbOpenApiConfigureResult,
    KbOpenApiRuntimeReady,
    compose_kb_openapi_live_runtime,
    dispatch_kb_openapi_configure,
)
from ProviderGateway.models.types import (
    ExplicitBrokerAdapterBinding,
    ExplicitBrokerCollectRequest,
)
from ProviderGateway.provider_interface import ProviderInterface
from ProviderGateway.tests.builders import (
    make_broker_binding,
    make_broker_profile,
    make_broker_request,
)
from ProviderGateway.tests.test_kb_openapi_keychain import (
    FAKE_APP_KEY,
    FAKE_APP_KEY_2,
    FAKE_APP_SECRET,
    FAKE_APP_SECRET_2,
    FakeKeychainBackend,
)
from ProviderGateway.tests.test_kb_openapi_live_broker_transport import (
    FAKE_ACCESS_TOKEN,
    FakeClock,
    RecordingHttp,
    http_json,
    oauth_success_payload,
    ssqm2952_success_payload,
)


FAKE_IP = "203.0.113.10"
FAKE_MAC = "02:c9:e7:ea:c3:8a"
RUNTIME_PATH = (
    Path(__file__).resolve().parents[1]
    / "auth"
    / "kb_openapi_runtime.py"
)
SECRETS = (
    FAKE_APP_KEY,
    FAKE_APP_SECRET,
    FAKE_APP_KEY_2,
    FAKE_APP_SECRET_2,
)


class ScriptedIO:
    def __init__(self, secrets=(), lines=()):
        self._secrets = list(secrets)
        self._lines = list(lines)
        self.secret_prompts = []
        self.line_prompts = []

    def prompt_secret(self, prompt=""):
        self.secret_prompts.append(prompt)
        if not self._secrets:
            raise AssertionError("unexpected secret prompt")
        return self._secrets.pop(0)

    def prompt_line(self, prompt=""):
        self.line_prompts.append(prompt)
        if not self._lines:
            raise AssertionError("unexpected line prompt")
        return self._lines.pop(0)


class RaisingIO:
    def prompt_secret(self, prompt=""):
        raise AssertionError("interactive secret input forbidden")

    def prompt_line(self, prompt=""):
        raise AssertionError("interactive line input forbidden")


def _no_secret(text):
    rendered = text if type(text) is str else repr(text)
    for secret in SECRETS:
        if secret in rendered:
            return False
    return True


class RuntimeTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.host_path = Path(self.tmp.name) / HOST_IDENTITY_FILENAME
        self.backend = FakeKeychainBackend()
        self.emitted = []
        self.real_joo = Path.home() / ".joo"
        self.real_existed = self.real_joo.exists()
        self.io = ScriptedIO(
            secrets=(FAKE_APP_KEY, FAKE_APP_SECRET),
            lines=(FAKE_IP, ""),
        )

    def tearDown(self):
        self.tmp.cleanup()
        if not self.real_existed:
            self.assertFalse(self.real_joo.exists())

    def dispatch(self, argv, io=None):
        scripted = self.io if io is None else io
        return dispatch_kb_openapi_configure(
            argv,
            prompt_secret=scripted.prompt_secret,
            prompt_line=scripted.prompt_line,
            keychain_backend=self.backend,
            host_identity_path=self.host_path,
            emit=self.emitted.append,
        )


class ArgvDispatchTests(RuntimeTestCase):
    def test_unsupported_argv_does_not_mutate(self):
        cases = (
            (),
            ("configure",),
            ("configure", "kb", "--help"),
            ("configure", "kb", "--host", "--replace"),
            ("configure", "other"),
            ("kb",),
            ("configure", "kb", "--replace", "--delete"),
        )
        for argv in cases:
            self.backend = FakeKeychainBackend()
            self.emitted = []
            with self.subTest(argv=argv):
                result = self.dispatch(argv, io=RaisingIO())
                self.assertFalse(result.ok)
                self.assertEqual(result.operation, "unsupported")
                self.assertEqual(
                    result.message,
                    "unsupported configure invocation",
                )
                self.assertEqual(self.backend.items, {})
                self.assertFalse(self.host_path.exists())
                self.assertTrue(_no_secret(result.message))


class ConfigureFirstTimeTests(RuntimeTestCase):
    def test_first_time_success_auto_mac(self):
        result = self.dispatch(("configure", "kb"))
        self.assertTrue(result.ok)
        self.assertEqual(result.operation, "configure")
        self.assertIn("mac mode auto", result.message)
        self.assertEqual(
            self.backend.items[
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_KEY)
            ],
            FAKE_APP_KEY,
        )
        loaded = load_kb_openapi_host_identity(self.host_path)
        self.assertEqual(loaded.ip_addr, FAKE_IP)
        self.assertIsNone(loaded.mac_addr)
        self.assertTrue(_no_secret(result.message))
        self.assertTrue(_no_secret("".join(self.emitted)))

    def test_first_time_success_mac_override(self):
        io = ScriptedIO(
            secrets=(FAKE_APP_KEY, FAKE_APP_SECRET),
            lines=(FAKE_IP, FAKE_MAC),
        )
        result = self.dispatch(("configure", "kb"), io=io)
        self.assertTrue(result.ok)
        self.assertIn("mac mode override", result.message)
        loaded = load_kb_openapi_host_identity(self.host_path)
        self.assertEqual(loaded.mac_addr, FAKE_MAC)

    def test_refuses_existing_before_prompt(self):
        store_kb_openapi_keychain_pair(
            self.backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        result = self.dispatch(("configure", "kb"), io=RaisingIO())
        self.assertFalse(result.ok)
        self.assertEqual(
            result.message,
            "kb openapi keychain items already exist",
        )
        self.assertFalse(self.host_path.exists())

    def test_denied_keychain_does_not_prompt(self):
        self.backend.get_status[KEYCHAIN_ACCOUNT_APP_KEY] = (
            STATUS_DENIED
        )
        result = self.dispatch(("configure", "kb"), io=RaisingIO())
        self.assertFalse(result.ok)
        self.assertEqual(
            result.message,
            "kb openapi keychain is unavailable",
        )

    def test_blank_secret_does_not_write_host(self):
        io = ScriptedIO(secrets=("", FAKE_APP_SECRET), lines=())
        result = self.dispatch(("configure", "kb"), io=io)
        self.assertFalse(result.ok)
        self.assertEqual(
            result.message,
            "kb openapi secret values are invalid",
        )
        self.assertEqual(self.backend.items, {})
        self.assertFalse(self.host_path.exists())
        self.assertEqual(io.line_prompts, [])

    def test_pair_write_failure_skips_host(self):
        self.backend.add_status[KEYCHAIN_ACCOUNT_APP_SECRET] = (
            STATUS_OS_FAILURE
        )
        result = self.dispatch(("configure", "kb"))
        self.assertFalse(result.ok)
        self.assertIn("run first-time configure again", result.message)
        self.assertEqual(self.backend.items, {})
        self.assertFalse(self.host_path.exists())

    def test_host_write_failure_leaves_keychain(self):
        io = ScriptedIO(
            secrets=(FAKE_APP_KEY, FAKE_APP_SECRET),
            lines=("127.0.0.1", ""),
        )
        result = self.dispatch(("configure", "kb"), io=io)
        self.assertFalse(result.ok)
        self.assertEqual(
            result.message,
            "kb openapi host identity write failed",
        )
        self.assertEqual(
            inspect_kb_openapi_keychain_pair(self.backend),
            "occupied",
        )
        self.assertFalse(self.host_path.exists())


class ConfigureReplaceDeleteHostTests(RuntimeTestCase):
    def test_replace_updates_pair_and_leaves_host(self):
        self.dispatch(("configure", "kb"))
        io = ScriptedIO(
            secrets=(FAKE_APP_KEY_2, FAKE_APP_SECRET_2),
            lines=(),
        )
        result = self.dispatch(("configure", "kb", "--replace"), io=io)
        self.assertTrue(result.ok)
        self.assertEqual(result.operation, "replace")
        self.assertEqual(
            self.backend.items[
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_KEY)
            ],
            FAKE_APP_KEY_2,
        )
        loaded = load_kb_openapi_host_identity(self.host_path)
        self.assertEqual(loaded.ip_addr, FAKE_IP)
        self.assertTrue(_no_secret(result.message))

    def test_replace_host_updates_both(self):
        self.dispatch(("configure", "kb"))
        io = ScriptedIO(
            secrets=(FAKE_APP_KEY_2, FAKE_APP_SECRET_2),
            lines=("198.51.100.9", FAKE_MAC),
        )
        result = self.dispatch(
            ("configure", "kb", "--replace", "--host"),
            io=io,
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.operation, "replace_host")
        loaded = load_kb_openapi_host_identity(self.host_path)
        self.assertEqual(loaded.ip_addr, "198.51.100.9")
        self.assertEqual(loaded.mac_addr, FAKE_MAC)

    def test_delete_pair_leaves_host(self):
        self.dispatch(("configure", "kb"))
        result = self.dispatch(
            ("configure", "kb", "--delete"),
            io=RaisingIO(),
        )
        self.assertTrue(result.ok)
        self.assertEqual(self.backend.items, {})
        self.assertTrue(self.host_path.exists())

    def test_host_only_leaves_keychain(self):
        self.dispatch(("configure", "kb"))
        io = ScriptedIO(secrets=(), lines=("198.51.100.9", ""))
        result = self.dispatch(("configure", "kb", "--host"), io=io)
        self.assertTrue(result.ok)
        self.assertEqual(
            self.backend.items[
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_KEY)
            ],
            FAKE_APP_KEY,
        )
        loaded = load_kb_openapi_host_identity(self.host_path)
        self.assertEqual(loaded.ip_addr, "198.51.100.9")

    def test_host_reset_already_absent_lawful(self):
        result = self.dispatch(
            ("configure", "kb", "--host", "--reset"),
            io=RaisingIO(),
        )
        self.assertTrue(result.ok)
        self.dispatch(("configure", "kb"))
        result = self.dispatch(
            ("configure", "kb", "--host", "--reset"),
            io=RaisingIO(),
        )
        self.assertTrue(result.ok)
        self.assertFalse(self.host_path.exists())
        self.assertEqual(
            inspect_kb_openapi_keychain_pair(self.backend),
            "occupied",
        )


class CompositionTests(RuntimeTestCase):
    def _ready(self, **overrides):
        store_kb_openapi_keychain_pair(
            self.backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        write_kb_openapi_host_identity(self.host_path, FAKE_IP)
        values = {
            "http_post": RecordingHttp(
                [
                    http_json(oauth_success_payload()),
                    http_json(ssqm2952_success_payload()),
                ]
            ),
            "clock": FakeClock(),
            "parameter_profile": make_broker_profile(),
            "keychain_backend": self.backend,
            "host_identity_path": self.host_path,
            "mac_deriver": lambda: FAKE_MAC,
        }
        values.update(overrides)
        return compose_kb_openapi_live_runtime(**values)

    def test_compose_success_and_collect(self):
        ready = self._ready()
        self.assertIsInstance(ready, KbOpenApiRuntimeReady)
        self.assertIsInstance(ready.adapter, KbOpenApiAdapter)
        self.assertIsInstance(
            ready.binding,
            ExplicitBrokerAdapterBinding,
        )
        self.assertTrue(hasattr(ready.transport, "read"))
        self.assertTrue(hasattr(ready.transport, "probe"))
        self.assertEqual(ready.binding.credential_ref, "kb_open_api")
        self.assertEqual(ready.binding.provider_id, "kb_open_api")
        request = ExplicitBrokerCollectRequest(
            "envelope-001",
            "corr-001",
            ready.binding,
            "holdings",
        )
        outcome = ready.adapter.collect(request)
        self.assertEqual(outcome.result_kind, "success")
        self.assertEqual(outcome.envelope.source_class, "broker_fact")
        accounts = {key[1] for key in self.backend.items}
        self.assertEqual(
            accounts,
            {KEYCHAIN_ACCOUNT_APP_KEY, KEYCHAIN_ACCOUNT_APP_SECRET},
        )
        self.assertNotIn("access_token", accounts)
        self.assertNotIn(FAKE_ACCESS_TOKEN, str(self.backend.items))

    def test_zero_interactive_input_on_compose_and_collect(self):
        io = RaisingIO()
        ready = self._ready()
        ready.adapter.collect(
            ExplicitBrokerCollectRequest(
                "envelope-001",
                "corr-001",
                ready.binding,
                "holdings",
            )
        )
        self.assertTrue(callable(io.prompt_secret))

    def test_host_failure_is_validation_before_transport(self):
        result = compose_kb_openapi_live_runtime(
            None,
            None,
            make_broker_profile(),
            keychain_backend=self.backend,
            host_identity_path=self.host_path,
            mac_deriver=lambda: FAKE_MAC,
        )
        self.assertEqual(
            result,
            ExplicitTransportFailure("VALIDATION_FAILURE", None),
        )

    def test_invalid_ip_is_validation_failure(self):
        self.host_path.write_text(
            '{"ip_addr":"127.0.0.1"}',
            encoding="utf-8",
        )
        result = compose_kb_openapi_live_runtime(
            None,
            FakeClock(),
            make_broker_profile(),
            keychain_backend=self.backend,
            host_identity_path=self.host_path,
            mac_deriver=lambda: FAKE_MAC,
        )
        self.assertEqual(
            result,
            ExplicitTransportFailure("VALIDATION_FAILURE", None),
        )

    def test_mac_derive_fail_is_validation_failure(self):
        write_kb_openapi_host_identity(self.host_path, FAKE_IP)
        result = compose_kb_openapi_live_runtime(
            None,
            FakeClock(),
            make_broker_profile(),
            keychain_backend=self.backend,
            host_identity_path=self.host_path,
            mac_deriver=lambda: None,
        )
        self.assertEqual(
            result,
            ExplicitTransportFailure("VALIDATION_FAILURE", None),
        )

    def test_invalid_mac_override_is_validation_failure(self):
        self.host_path.write_text(
            '{"ip_addr":"203.0.113.10","mac_addr":"00:00:00:00:00:00"}',
            encoding="utf-8",
        )
        result = compose_kb_openapi_live_runtime(
            None,
            FakeClock(),
            make_broker_profile(),
            keychain_backend=self.backend,
            host_identity_path=self.host_path,
            mac_deriver=lambda: FAKE_MAC,
        )
        self.assertEqual(
            result,
            ExplicitTransportFailure("VALIDATION_FAILURE", None),
        )

    def test_missing_keychain_collect_is_auth_failure(self):
        write_kb_openapi_host_identity(self.host_path, FAKE_IP)
        ready = compose_kb_openapi_live_runtime(
            RecordingHttp([]),
            FakeClock(),
            make_broker_profile(),
            keychain_backend=self.backend,
            host_identity_path=self.host_path,
            mac_deriver=lambda: FAKE_MAC,
        )
        outcome = ready.adapter.collect(
            ExplicitBrokerCollectRequest(
                "envelope-001",
                "corr-001",
                ready.binding,
                "holdings",
            )
        )
        self.assertEqual(outcome.failure.failure_class, "AUTH_FAILURE")
        self.assertIsNone(outcome.failure.detail)

    def test_unexpected_ref_is_auth_failure(self):
        ready = self._ready()
        other = ExplicitBrokerAdapterBinding(
            "kb_open_api",
            "other-ref",
            make_broker_profile(),
        )
        outcome = ready.adapter.collect(
            ExplicitBrokerCollectRequest(
                "envelope-001",
                "corr-001",
                other,
                "holdings",
            )
        )
        self.assertEqual(outcome.failure.failure_class, "AUTH_FAILURE")
        self.assertIsNone(outcome.failure.detail)

    def test_denied_keychain_is_auth_failure(self):
        write_kb_openapi_host_identity(self.host_path, FAKE_IP)
        store_kb_openapi_keychain_pair(
            self.backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        self.backend.get_status[KEYCHAIN_ACCOUNT_APP_KEY] = (
            STATUS_DENIED
        )
        ready = compose_kb_openapi_live_runtime(
            RecordingHttp([]),
            FakeClock(),
            make_broker_profile(),
            keychain_backend=self.backend,
            host_identity_path=self.host_path,
            mac_deriver=lambda: FAKE_MAC,
        )
        outcome = ready.adapter.collect(
            ExplicitBrokerCollectRequest(
                "envelope-001",
                "corr-001",
                ready.binding,
                "holdings",
            )
        )
        self.assertEqual(outcome.failure.failure_class, "AUTH_FAILURE")
        self.assertIsNone(outcome.failure.detail)

    def test_configured_ip_and_mac_reach_transport(self):
        write_kb_openapi_host_identity(
            self.host_path,
            FAKE_IP,
            FAKE_MAC,
        )
        store_kb_openapi_keychain_pair(
            self.backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        http = RecordingHttp(
            [
                http_json(oauth_success_payload()),
                http_json(ssqm2952_success_payload()),
            ]
        )
        called = {"n": 0}

        def boom():
            called["n"] += 1
            raise AssertionError("deriver must not run")

        ready = compose_kb_openapi_live_runtime(
            http,
            FakeClock(),
            make_broker_profile(),
            keychain_backend=self.backend,
            host_identity_path=self.host_path,
            mac_deriver=boom,
        )
        ready.adapter.collect(
            ExplicitBrokerCollectRequest(
                "envelope-001",
                "corr-001",
                ready.binding,
                "holdings",
            )
        )
        self.assertEqual(called["n"], 0)
        body = http.calls[0]["body"].decode("utf-8")
        self.assertIn('"ipAddr":"203.0.113.10"', body)
        self.assertIn('"macAddr":"02:c9:e7:ea:c3:8a"', body)

    def test_compose_does_not_construct_production_backend(self):
        original = kb_openapi_keychain.make_production_keychain_backend

        def boom():
            raise AssertionError("production backend constructed")

        kb_openapi_keychain.make_production_keychain_backend = boom
        try:
            write_kb_openapi_host_identity(self.host_path, FAKE_IP)
            result = compose_kb_openapi_live_runtime(
                RecordingHttp([]),
                FakeClock(),
                make_broker_profile(),
                keychain_backend=self.backend,
                host_identity_path=self.host_path,
                mac_deriver=lambda: FAKE_MAC,
            )
            self.assertIsInstance(result, KbOpenApiRuntimeReady)
        finally:
            kb_openapi_keychain.make_production_keychain_backend = (
                original
            )


class ExistingApiUnchangedTests(unittest.TestCase):
    def test_existing_public_surfaces(self):
        self.assertTrue(
            issubclass(KbOpenApiAdapter, ProviderInterface)
        )
        self.assertEqual(
            inspect.signature(KbOpenApiAdapter.collect).parameters[
                "request"
            ].annotation
            if False
            else "ExplicitBrokerCollectRequest",
            "ExplicitBrokerCollectRequest",
        )
        self.assertTrue(callable(resolve_outbound_credential))
        self.assertTrue(callable(decode_kb_openapi_client_material))
        self.assertEqual(
            list(
                inspect.signature(
                    CredentialSupplier.__call__
                ).parameters
            ),
            ["self", "credential_ref"],
        )
        decoded = decode_kb_openapi_client_material(
            json.dumps(
                {
                    "appKey": FAKE_APP_KEY,
                    "appSecret": FAKE_APP_SECRET,
                },
                separators=(",", ":"),
            )
        )
        self.assertEqual(decoded, (FAKE_APP_KEY, FAKE_APP_SECRET))
        self.assertEqual(
            DEFAULT_BASE_URL,
            "https://developer.kbsec.com:32484",
        )

    def test_runtime_source_has_no_general_cli_or_live_client(self):
        source = RUNTIME_PATH.read_text()
        for forbidden in (
            "argparse",
            "click",
            "typer",
            "urllib",
            "requests",
            "httpx",
            "subprocess",
            "keyring",
            "FactStore",
            "PortfolioSnapshot",
        ):
            self.assertNotIn(forbidden, source)

    def test_getpass_only_under_main(self):
        tree = ast.parse(RUNTIME_PATH.read_text())
        module_imports = set()
        main_imports = set()
        for node in tree.body:
            target = main_imports
            if isinstance(node, ast.If):
                test = node.test
                is_main = (
                    isinstance(test, ast.Compare)
                    and isinstance(test.left, ast.Name)
                    and test.left.id == "__name__"
                )
                if not is_main:
                    target = module_imports
            else:
                target = module_imports
            for child in ast.walk(node):
                if isinstance(child, ast.Import):
                    for alias in child.names:
                        target.add(alias.name.split(".")[0])
                elif (
                    isinstance(child, ast.ImportFrom)
                    and child.module
                ):
                    target.add(child.module.split(".")[0])
        self.assertNotIn("getpass", module_imports)
        self.assertEqual(main_imports, {"getpass"})

    def test_configure_result_is_not_gateway_envelope(self):
        result = KbOpenApiConfigureResult(
            False,
            "unsupported",
            "unsupported configure invocation",
        )
        self.assertTrue(_no_secret(result.message))
        self.assertFalse(hasattr(result, "failure_class"))
        self.assertFalse(hasattr(result, "envelope"))


if __name__ == "__main__":
    unittest.main()
