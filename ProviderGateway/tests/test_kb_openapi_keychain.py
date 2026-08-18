from __future__ import annotations

import ast
import inspect
import json
import unittest
from pathlib import Path

from ProviderGateway.adapters.kb_open_api import KbOpenApiAdapter
from ProviderGateway.adapters.ports import CredentialSupplier
from ProviderGateway.auth.credentials import resolve_outbound_credential
from ProviderGateway.auth.kb_openapi_keychain import (
    KEYCHAIN_ACCOUNT_APP_KEY,
    KEYCHAIN_ACCOUNT_APP_SECRET,
    KEYCHAIN_SERVICE,
    STATUS_ALREADY_EXISTS,
    STATUS_DENIED,
    STATUS_NOT_FOUND,
    STATUS_OS_FAILURE,
    STATUS_SUCCESS,
    delete_kb_openapi_keychain_pair,
    inspect_kb_openapi_keychain_pair,
    make_kb_openapi_keychain_credential_supplier,
    make_production_keychain_backend,
    map_keychain_osstatus,
    reconstruct_kb_openapi_credential_json,
    replace_kb_openapi_keychain_pair,
    store_kb_openapi_keychain_pair,
)
from ProviderGateway.tests.builders import (
    make_broker_binding,
    make_broker_request,
    utc_now,
)


FAKE_APP_KEY = "test-app-key"
FAKE_APP_SECRET = "test-app-secret"
FAKE_APP_KEY_2 = "test-app-key-2"
FAKE_APP_SECRET_2 = "test-app-secret-2"
EXPECTED_JSON = json.dumps(
    {"appKey": FAKE_APP_KEY, "appSecret": FAKE_APP_SECRET},
    ensure_ascii=False,
    separators=(",", ":"),
)
KEYCHAIN_PATH = (
    Path(__file__).resolve().parents[1]
    / "auth"
    / "kb_openapi_keychain.py"
)
SECRETS = (FAKE_APP_KEY, FAKE_APP_SECRET, FAKE_APP_KEY_2, FAKE_APP_SECRET_2)


class FakeKeychainBackend:
    def __init__(self):
        self.items = {}
        self.calls = []
        self.add_status = {}
        self.update_status = {}
        self.delete_status = {}
        self.get_status = {}
        self.get_value = {}

    def _record(self, operation, account):
        self.calls.append((operation, KEYCHAIN_SERVICE, account))

    def add(self, service, account, secret):
        self._record("add", account)
        forced = self.add_status.get(account)
        if forced is not None:
            if forced == STATUS_SUCCESS:
                self.items[(service, account)] = secret
            return forced
        key = (service, account)
        if key in self.items:
            return STATUS_ALREADY_EXISTS
        self.items[key] = secret
        return STATUS_SUCCESS

    def update(self, service, account, secret):
        self._record("update", account)
        forced = self.update_status.get(account)
        if forced is not None:
            if forced == STATUS_SUCCESS:
                self.items[(service, account)] = secret
            return forced
        key = (service, account)
        if key not in self.items:
            return STATUS_NOT_FOUND
        self.items[key] = secret
        return STATUS_SUCCESS

    def delete(self, service, account):
        self._record("delete", account)
        forced = self.delete_status.get(account)
        if forced is not None:
            if forced == STATUS_SUCCESS:
                self.items.pop((service, account), None)
            return forced
        key = (service, account)
        if key not in self.items:
            return STATUS_NOT_FOUND
        del self.items[key]
        return STATUS_SUCCESS

    def get(self, service, account):
        self._record("get", account)
        forced = self.get_status.get(account)
        if forced is not None:
            if forced != STATUS_SUCCESS:
                return (forced, None)
        key = (service, account)
        if key not in self.items:
            return (STATUS_NOT_FOUND, None)
        if account in self.get_value:
            return (STATUS_SUCCESS, self.get_value[account])
        return (STATUS_SUCCESS, self.items[key])


def _text_has_secret(text):
    rendered = text if type(text) is str else repr(text)
    for secret in SECRETS:
        if secret in rendered:
            return True
    return False


class OsStatusMappingTests(unittest.TestCase):
    def test_exact_osstatus_mapping(self):
        self.assertEqual(map_keychain_osstatus(0), STATUS_SUCCESS)
        self.assertEqual(map_keychain_osstatus(-25300), STATUS_NOT_FOUND)
        self.assertEqual(
            map_keychain_osstatus(-25299),
            STATUS_ALREADY_EXISTS,
        )
        for status in (-25293, -128, -25308, -61, -25292):
            with self.subTest(status=status):
                self.assertEqual(
                    map_keychain_osstatus(status),
                    STATUS_DENIED,
                )
        self.assertEqual(map_keychain_osstatus(-1), STATUS_OS_FAILURE)
        self.assertEqual(map_keychain_osstatus(1), STATUS_OS_FAILURE)
        self.assertEqual(map_keychain_osstatus(True), STATUS_OS_FAILURE)


class FakeBackendContractTests(unittest.TestCase):
    def test_add_update_get_delete(self):
        backend = FakeKeychainBackend()
        self.assertEqual(
            backend.add(
                KEYCHAIN_SERVICE,
                KEYCHAIN_ACCOUNT_APP_KEY,
                FAKE_APP_KEY,
            ),
            STATUS_SUCCESS,
        )
        self.assertEqual(
            backend.get(
                KEYCHAIN_SERVICE,
                KEYCHAIN_ACCOUNT_APP_KEY,
            ),
            (STATUS_SUCCESS, FAKE_APP_KEY),
        )
        self.assertEqual(
            backend.add(
                KEYCHAIN_SERVICE,
                KEYCHAIN_ACCOUNT_APP_KEY,
                FAKE_APP_KEY_2,
            ),
            STATUS_ALREADY_EXISTS,
        )
        self.assertEqual(
            backend.update(
                KEYCHAIN_SERVICE,
                KEYCHAIN_ACCOUNT_APP_KEY,
                FAKE_APP_KEY_2,
            ),
            STATUS_SUCCESS,
        )
        self.assertEqual(
            backend.get(
                KEYCHAIN_SERVICE,
                KEYCHAIN_ACCOUNT_APP_KEY,
            ),
            (STATUS_SUCCESS, FAKE_APP_KEY_2),
        )
        self.assertEqual(
            backend.delete(
                KEYCHAIN_SERVICE,
                KEYCHAIN_ACCOUNT_APP_KEY,
            ),
            STATUS_SUCCESS,
        )
        self.assertEqual(
            backend.get(
                KEYCHAIN_SERVICE,
                KEYCHAIN_ACCOUNT_APP_KEY,
            ),
            (STATUS_NOT_FOUND, None),
        )
        self.assertEqual(
            backend.delete(
                KEYCHAIN_SERVICE,
                KEYCHAIN_ACCOUNT_APP_KEY,
            ),
            STATUS_NOT_FOUND,
        )

    def test_exact_service_and_account_identities(self):
        self.assertEqual(KEYCHAIN_SERVICE, "joo.provider.kb_open_api")
        self.assertEqual(KEYCHAIN_ACCOUNT_APP_KEY, "appKey")
        self.assertEqual(KEYCHAIN_ACCOUNT_APP_SECRET, "appSecret")
        backend = FakeKeychainBackend()
        result = store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        self.assertTrue(result.ok)
        self.assertEqual(
            set(backend.items),
            {
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_KEY),
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_SECRET),
            },
        )
        self.assertEqual(
            backend.items[
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_KEY)
            ],
            FAKE_APP_KEY,
        )
        self.assertEqual(
            backend.items[
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_SECRET)
            ],
            FAKE_APP_SECRET,
        )


class PairWriteTests(unittest.TestCase):
    def test_first_time_pair_write(self):
        backend = FakeKeychainBackend()
        result = store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.code, "stored")
        self.assertEqual(
            backend.get(
                KEYCHAIN_SERVICE,
                KEYCHAIN_ACCOUNT_APP_KEY,
            )[1],
            FAKE_APP_KEY,
        )
        self.assertEqual(
            backend.get(
                KEYCHAIN_SERVICE,
                KEYCHAIN_ACCOUNT_APP_SECRET,
            )[1],
            FAKE_APP_SECRET,
        )

    def test_first_time_refuses_existing_before_write(self):
        backend = FakeKeychainBackend()
        backend.items[
            (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_KEY)
        ] = FAKE_APP_KEY
        result = store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY_2,
            FAKE_APP_SECRET_2,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "already_exists")
        operations = [call[0] for call in backend.calls]
        self.assertNotIn("add", operations)
        self.assertNotIn("update", operations)
        self.assertEqual(
            backend.items[
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_KEY)
            ],
            FAKE_APP_KEY,
        )
        self.assertNotIn(
            (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_SECRET),
            backend.items,
        )

    def test_first_time_refuses_when_only_secret_exists(self):
        backend = FakeKeychainBackend()
        backend.items[
            (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_SECRET)
        ] = FAKE_APP_SECRET
        result = store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET_2,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "already_exists")
        self.assertNotIn("add", [call[0] for call in backend.calls])

    def test_first_time_denied_is_unavailable_without_write(self):
        backend = FakeKeychainBackend()
        backend.get_status[KEYCHAIN_ACCOUNT_APP_KEY] = STATUS_DENIED
        result = store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "unavailable")
        self.assertEqual(backend.items, {})

    def test_blank_and_whitespace_rejected_before_write(self):
        cases = (
            ("", FAKE_APP_SECRET),
            (FAKE_APP_KEY, ""),
            (" " + FAKE_APP_KEY, FAKE_APP_SECRET),
            (FAKE_APP_KEY, FAKE_APP_SECRET + " "),
            ("   ", FAKE_APP_SECRET),
            (FAKE_APP_KEY, "\t"),
            (1, FAKE_APP_SECRET),
            (FAKE_APP_KEY, None),
        )
        for app_key, app_secret in cases:
            backend = FakeKeychainBackend()
            with self.subTest(app_key=repr(app_key)):
                result = store_kb_openapi_keychain_pair(
                    backend,
                    app_key,
                    app_secret,
                )
                self.assertFalse(result.ok)
                self.assertEqual(result.code, "invalid_secret")
                self.assertEqual(backend.items, {})

    def test_partial_first_time_write_deletes_both(self):
        backend = FakeKeychainBackend()
        backend.add_status[KEYCHAIN_ACCOUNT_APP_SECRET] = (
            STATUS_OS_FAILURE
        )
        result = store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "write_failed")
        self.assertEqual(backend.items, {})
        self.assertTrue(
            inspect_kb_openapi_keychain_pair(backend) == "absent"
            or backend.items == {}
        )

    def test_verification_mismatch_deletes_both(self):
        backend = FakeKeychainBackend()
        backend.get_value[KEYCHAIN_ACCOUNT_APP_SECRET] = (
            FAKE_APP_SECRET_2
        )
        result = store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "write_failed")
        self.assertEqual(backend.items, {})


class PairReplaceTests(unittest.TestCase):
    def test_replace_pair_verification(self):
        backend = FakeKeychainBackend()
        store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        result = replace_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY_2,
            FAKE_APP_SECRET_2,
        )
        self.assertTrue(result.ok)
        self.assertEqual(
            backend.items[
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_KEY)
            ],
            FAKE_APP_KEY_2,
        )
        self.assertEqual(
            backend.items[
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_SECRET)
            ],
            FAKE_APP_SECRET_2,
        )

    def test_replace_adds_missing_item(self):
        backend = FakeKeychainBackend()
        backend.items[
            (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_KEY)
        ] = FAKE_APP_KEY
        result = replace_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY_2,
            FAKE_APP_SECRET_2,
        )
        self.assertTrue(result.ok)
        self.assertEqual(
            backend.items[
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_KEY)
            ],
            FAKE_APP_KEY_2,
        )
        self.assertEqual(
            backend.items[
                (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_SECRET)
            ],
            FAKE_APP_SECRET_2,
        )

    def test_partial_replace_deletes_both(self):
        backend = FakeKeychainBackend()
        store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        backend.update_status[KEYCHAIN_ACCOUNT_APP_SECRET] = (
            STATUS_OS_FAILURE
        )
        result = replace_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY_2,
            FAKE_APP_SECRET_2,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "write_failed")
        self.assertEqual(backend.items, {})

    def test_mixed_old_new_never_reported_success(self):
        backend = FakeKeychainBackend()
        store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        backend.get_value[KEYCHAIN_ACCOUNT_APP_KEY] = FAKE_APP_KEY_2
        backend.get_value[KEYCHAIN_ACCOUNT_APP_SECRET] = FAKE_APP_SECRET
        result = replace_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY_2,
            FAKE_APP_SECRET_2,
        )
        self.assertFalse(result.ok)
        self.assertEqual(backend.items, {})


class PairDeleteTests(unittest.TestCase):
    def test_delete_both(self):
        backend = FakeKeychainBackend()
        store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        result = delete_kb_openapi_keychain_pair(backend)
        self.assertTrue(result.ok)
        self.assertEqual(result.code, "deleted")
        self.assertEqual(backend.items, {})

    def test_already_absent_is_lawful(self):
        backend = FakeKeychainBackend()
        result = delete_kb_openapi_keychain_pair(backend)
        self.assertTrue(result.ok)
        self.assertEqual(result.code, "deleted")

    def test_partial_delete_is_not_success(self):
        backend = FakeKeychainBackend()
        store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        backend.delete_status[KEYCHAIN_ACCOUNT_APP_SECRET] = (
            STATUS_DENIED
        )
        result = delete_kb_openapi_keychain_pair(backend)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "delete_failed")
        self.assertIn(
            (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_SECRET),
            backend.items,
        )


class CredentialSupplierTests(unittest.TestCase):
    def test_exact_compact_json(self):
        reconstructed = reconstruct_kb_openapi_credential_json(
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        self.assertEqual(reconstructed, EXPECTED_JSON)
        self.assertEqual(
            reconstructed,
            '{"appKey":"test-app-key","appSecret":"test-app-secret"}',
        )
        backend = FakeKeychainBackend()
        store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        supplier = make_kb_openapi_keychain_credential_supplier(
            backend
        )
        self.assertEqual(supplier("kb_open_api"), EXPECTED_JSON)

    def test_supplier_occupies_credential_supplier(self):
        backend = FakeKeychainBackend()
        store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        supplier = make_kb_openapi_keychain_credential_supplier(
            backend
        )
        self.assertTrue(callable(supplier))
        self.assertEqual(
            inspect.signature(supplier).parameters["credential_ref"].name,
            inspect.signature(CredentialSupplier.__call__)
            .parameters["credential_ref"]
            .name,
        )

    def test_unexpected_ref_fails_without_retrieve(self):
        backend = FakeKeychainBackend()
        store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        supplier = make_kb_openapi_keychain_credential_supplier(
            backend
        )
        backend.calls.clear()
        with self.assertRaises(RuntimeError) as raised:
            supplier("other-ref")
        self.assertEqual(
            str(raised.exception),
            "unexpected credential_ref",
        )
        self.assertEqual(backend.calls, [])
        self.assertIsNone(
            resolve_outbound_credential("other-ref", supplier)
        )

    def test_missing_denied_malformed_become_auth_none(self):
        cases = []
        missing = FakeKeychainBackend()
        cases.append(missing)
        denied = FakeKeychainBackend()
        denied.get_status[KEYCHAIN_ACCOUNT_APP_KEY] = STATUS_DENIED
        cases.append(denied)
        malformed = FakeKeychainBackend()
        malformed.items[
            (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_KEY)
        ] = "   "
        malformed.items[
            (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_SECRET)
        ] = FAKE_APP_SECRET
        cases.append(malformed)
        for backend in cases:
            supplier = make_kb_openapi_keychain_credential_supplier(
                backend
            )
            with self.subTest(backend=backend):
                self.assertIsNone(
                    resolve_outbound_credential(
                        "kb_open_api",
                        supplier,
                    )
                )

    def test_missing_app_key_does_not_retrieve_secret(self):
        backend = FakeKeychainBackend()
        backend.items[
            (KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT_APP_SECRET)
        ] = FAKE_APP_SECRET
        supplier = make_kb_openapi_keychain_credential_supplier(
            backend
        )
        backend.calls.clear()
        self.assertIsNone(
            resolve_outbound_credential("kb_open_api", supplier)
        )
        accounts = [call[2] for call in backend.calls]
        self.assertEqual(accounts, [KEYCHAIN_ACCOUNT_APP_KEY])

    def test_collect_auth_failure_detail_none(self):
        backend = FakeKeychainBackend()
        supplier = make_kb_openapi_keychain_credential_supplier(
            backend
        )

        class _Transport:
            def read(self, binding, credential, request):
                raise AssertionError("transport must not run")

            def probe(self, binding):
                raise AssertionError("probe must not run")

        adapter = KbOpenApiAdapter(
            make_broker_binding(credential_ref="kb_open_api"),
            _Transport(),
            supplier,
            utc_now,
        )
        outcome = adapter.collect(
            make_broker_request(
                binding=make_broker_binding(
                    credential_ref="kb_open_api"
                )
            )
        )
        self.assertEqual(outcome.result_kind, "failure")
        self.assertEqual(outcome.failure.failure_class, "AUTH_FAILURE")
        self.assertIsNone(outcome.failure.detail)


class LeakProofTests(unittest.TestCase):
    def test_no_secret_in_pair_result_or_exception(self):
        backend = FakeKeychainBackend()
        result = store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        self.assertFalse(_text_has_secret(result))
        self.assertFalse(_text_has_secret(result.message if hasattr(result, "message") else result.code))
        failed = store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY_2,
            FAKE_APP_SECRET_2,
        )
        self.assertFalse(_text_has_secret(failed))
        supplier = make_kb_openapi_keychain_credential_supplier(
            backend
        )
        try:
            supplier("other-ref")
        except Exception as exc:
            self.assertFalse(_text_has_secret(exc))
            self.assertFalse(_text_has_secret(str(exc)))

    def test_calls_do_not_record_secret_payloads(self):
        backend = FakeKeychainBackend()
        store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        rendered = repr(backend.calls)
        self.assertFalse(_text_has_secret(rendered))


class IsolationTests(unittest.TestCase):
    def test_import_does_not_construct_production_backend(self):
        source = KEYCHAIN_PATH.read_text()
        tree = ast.parse(source)
        module_calls = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                if node.name == "make_production_keychain_backend":
                    continue
            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                func = child.func
                if (
                    isinstance(func, ast.Name)
                    and func.id == "_SecurityFrameworkKeychainBackend"
                ):
                    module_calls.append(node)
        self.assertEqual(module_calls, [])
        self.assertTrue(callable(make_production_keychain_backend))
        self.assertNotIn("CDLL", source.split("class _Security")[0])

    def test_tests_do_not_construct_production_backend(self):
        self.assertTrue(callable(make_production_keychain_backend))
        self.assertNotIn(
            "make_production_keychain_backend" + "()",
            Path(__file__).read_text(),
        )

    def test_source_forbids_secret_backends(self):
        source = KEYCHAIN_PATH.read_text()
        for forbidden in (
            "subprocess",
            "keyring",
            "PyObjC",
            "objc",
            "requests",
            "httpx",
            "add-generic-password",
            "find-generic-password",
        ):
            self.assertNotIn(forbidden, source)

    def test_access_token_never_written(self):
        backend = FakeKeychainBackend()
        store_kb_openapi_keychain_pair(
            backend,
            FAKE_APP_KEY,
            FAKE_APP_SECRET,
        )
        accounts = {key[1] for key in backend.items}
        self.assertEqual(
            accounts,
            {KEYCHAIN_ACCOUNT_APP_KEY, KEYCHAIN_ACCOUNT_APP_SECRET},
        )
        self.assertNotIn("access_token", accounts)
        self.assertNotIn("token", accounts)
        for value in backend.items.values():
            self.assertNotIn("test-access-token", value)


if __name__ == "__main__":
    unittest.main()
