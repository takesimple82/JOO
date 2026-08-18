from __future__ import annotations

import json
from dataclasses import dataclass

KEYCHAIN_SERVICE = "joo.provider.kb_open_api"
KEYCHAIN_ACCOUNT_APP_KEY = "appKey"
KEYCHAIN_ACCOUNT_APP_SECRET = "appSecret"

STATUS_SUCCESS = "success"
STATUS_NOT_FOUND = "not_found"
STATUS_ALREADY_EXISTS = "already_exists"
STATUS_DENIED = "denied"
STATUS_OS_FAILURE = "os_failure"

_DENIED_OSSTATUS = frozenset(
    (
        -25293,
        -128,
        -25308,
        -61,
        -25292,
    )
)
_CF_STRING_ENCODING_UTF8 = 0x08000100
_SECURITY_FRAMEWORK = (
    "/System/Library/Frameworks/Security.framework/Security"
)
_COREFOUNDATION_FRAMEWORK = (
    "/System/Library/Frameworks/CoreFoundation.framework/"
    "CoreFoundation"
)


@dataclass(frozen=True)
class KbOpenApiKeychainPairResult:
    ok: bool
    code: str


def map_keychain_osstatus(status) -> str:
    if type(status) is not int:
        return STATUS_OS_FAILURE
    if status == 0:
        return STATUS_SUCCESS
    if status == -25300:
        return STATUS_NOT_FOUND
    if status == -25299:
        return STATUS_ALREADY_EXISTS
    if status in _DENIED_OSSTATUS:
        return STATUS_DENIED
    return STATUS_OS_FAILURE


def reconstruct_kb_openapi_credential_json(
    app_key: str,
    app_secret: str,
) -> str:
    return json.dumps(
        {
            "appKey": app_key,
            "appSecret": app_secret,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _usable_secret(value) -> bool:
    if type(value) is not str:
        return False
    if value == "":
        return False
    if value != value.strip():
        return False
    return True


def inspect_kb_openapi_keychain_pair(backend) -> str:
    try:
        first_status, _ignored = backend.get(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_KEY,
        )
    except Exception:
        return STATUS_OS_FAILURE
    if first_status == STATUS_DENIED:
        return STATUS_DENIED
    if first_status == STATUS_OS_FAILURE:
        return STATUS_OS_FAILURE
    try:
        second_status, _ignored = backend.get(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_SECRET,
        )
    except Exception:
        return STATUS_OS_FAILURE
    if second_status == STATUS_DENIED:
        return STATUS_DENIED
    if second_status == STATUS_OS_FAILURE:
        return STATUS_OS_FAILURE
    if (
        first_status == STATUS_SUCCESS
        or second_status == STATUS_SUCCESS
    ):
        return "occupied"
    if (
        first_status == STATUS_NOT_FOUND
        and second_status == STATUS_NOT_FOUND
    ):
        return "absent"
    return STATUS_OS_FAILURE


def _both_absent(backend) -> bool:
    try:
        first_status, _ignored = backend.get(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_KEY,
        )
        second_status, _ignored = backend.get(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_SECRET,
        )
    except Exception:
        return False
    return (
        first_status == STATUS_NOT_FOUND
        and second_status == STATUS_NOT_FOUND
    )


def _best_effort_clear_pair(backend) -> bool:
    try:
        backend.delete(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_KEY,
        )
    except Exception:
        pass
    try:
        backend.delete(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_SECRET,
        )
    except Exception:
        pass
    return _both_absent(backend)


def _write_one(backend, account, secret, replace: bool) -> str:
    if replace:
        status = backend.update(
            KEYCHAIN_SERVICE,
            account,
            secret,
        )
        if status == STATUS_NOT_FOUND:
            status = backend.add(
                KEYCHAIN_SERVICE,
                account,
                secret,
            )
        return status
    return backend.add(
        KEYCHAIN_SERVICE,
        account,
        secret,
    )


def _mutate_and_verify(backend, app_key, app_secret, replace: bool):
    try:
        key_status = _write_one(
            backend,
            KEYCHAIN_ACCOUNT_APP_KEY,
            app_key,
            replace,
        )
        if key_status != STATUS_SUCCESS:
            _best_effort_clear_pair(backend)
            return KbOpenApiKeychainPairResult(False, "write_failed")
        secret_status = _write_one(
            backend,
            KEYCHAIN_ACCOUNT_APP_SECRET,
            app_secret,
            replace,
        )
        if secret_status != STATUS_SUCCESS:
            _best_effort_clear_pair(backend)
            return KbOpenApiKeychainPairResult(False, "write_failed")
        got_key_status, got_key = backend.get(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_KEY,
        )
        got_secret_status, got_secret = backend.get(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_SECRET,
        )
        if (
            got_key_status != STATUS_SUCCESS
            or got_secret_status != STATUS_SUCCESS
            or got_key != app_key
            or got_secret != app_secret
        ):
            _best_effort_clear_pair(backend)
            return KbOpenApiKeychainPairResult(False, "write_failed")
        return KbOpenApiKeychainPairResult(True, "stored")
    except Exception:
        _best_effort_clear_pair(backend)
        return KbOpenApiKeychainPairResult(False, "write_failed")


def store_kb_openapi_keychain_pair(backend, app_key, app_secret):
    occupancy = inspect_kb_openapi_keychain_pair(backend)
    if occupancy == "occupied":
        return KbOpenApiKeychainPairResult(False, "already_exists")
    if occupancy != "absent":
        return KbOpenApiKeychainPairResult(False, "unavailable")
    if not _usable_secret(app_key) or not _usable_secret(app_secret):
        return KbOpenApiKeychainPairResult(False, "invalid_secret")
    return _mutate_and_verify(
        backend,
        app_key,
        app_secret,
        False,
    )


def replace_kb_openapi_keychain_pair(backend, app_key, app_secret):
    if not _usable_secret(app_key) or not _usable_secret(app_secret):
        return KbOpenApiKeychainPairResult(False, "invalid_secret")
    return _mutate_and_verify(
        backend,
        app_key,
        app_secret,
        True,
    )


def delete_kb_openapi_keychain_pair(backend):
    try:
        backend.delete(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_KEY,
        )
        backend.delete(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_SECRET,
        )
    except Exception:
        pass
    if _both_absent(backend):
        return KbOpenApiKeychainPairResult(True, "deleted")
    return KbOpenApiKeychainPairResult(False, "delete_failed")


def make_kb_openapi_keychain_credential_supplier(
    backend,
    expected_credential_ref="kb_open_api",
):
    def supply(credential_ref):
        if credential_ref != expected_credential_ref:
            raise RuntimeError("unexpected credential_ref")
        key_status, app_key = backend.get(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_KEY,
        )
        if key_status != STATUS_SUCCESS or type(app_key) is not str:
            raise RuntimeError(
                "kb openapi keychain retrieve failed"
            )
        if app_key.strip() == "":
            raise RuntimeError(
                "kb openapi keychain retrieve failed"
            )
        secret_status, app_secret = backend.get(
            KEYCHAIN_SERVICE,
            KEYCHAIN_ACCOUNT_APP_SECRET,
        )
        if (
            secret_status != STATUS_SUCCESS
            or type(app_secret) is not str
        ):
            raise RuntimeError(
                "kb openapi keychain retrieve failed"
            )
        if app_secret.strip() == "":
            raise RuntimeError(
                "kb openapi keychain retrieve failed"
            )
        return reconstruct_kb_openapi_credential_json(
            app_key,
            app_secret,
        )

    return supply


def make_production_keychain_backend():
    return _SecurityFrameworkKeychainBackend()


class _SecurityFrameworkKeychainBackend:
    def __init__(self):
        import ctypes

        self._ctypes = ctypes
        self._cf = ctypes.CDLL(_COREFOUNDATION_FRAMEWORK)
        self._sec = ctypes.CDLL(_SECURITY_FRAMEWORK)
        self._bind()
        self._allocator = self._symbol(
            self._cf,
            "kCFAllocatorDefault",
        )
        self._true = self._symbol(self._cf, "kCFBooleanTrue")
        self._sec_class = self._symbol(self._sec, "kSecClass")
        self._generic_password = self._symbol(
            self._sec,
            "kSecClassGenericPassword",
        )
        self._attr_service = self._symbol(
            self._sec,
            "kSecAttrService",
        )
        self._attr_account = self._symbol(
            self._sec,
            "kSecAttrAccount",
        )
        self._value_data = self._symbol(self._sec, "kSecValueData")
        self._return_data = self._symbol(self._sec, "kSecReturnData")
        self._match_limit = self._symbol(self._sec, "kSecMatchLimit")
        self._match_limit_one = self._symbol(
            self._sec,
            "kSecMatchLimitOne",
        )

    def _symbol(self, library, name):
        return self._ctypes.c_void_p.in_dll(library, name).value

    def _bind(self):
        ctypes = self._ctypes
        cf = self._cf
        sec = self._sec
        cf.CFStringCreateWithCString.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_uint32,
        ]
        cf.CFStringCreateWithCString.restype = ctypes.c_void_p
        cf.CFDataCreate.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_long,
        ]
        cf.CFDataCreate.restype = ctypes.c_void_p
        cf.CFDataGetLength.argtypes = [ctypes.c_void_p]
        cf.CFDataGetLength.restype = ctypes.c_long
        cf.CFDataGetBytePtr.argtypes = [ctypes.c_void_p]
        cf.CFDataGetBytePtr.restype = ctypes.c_void_p
        cf.CFDictionaryCreate.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_long,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        cf.CFDictionaryCreate.restype = ctypes.c_void_p
        cf.CFRelease.argtypes = [ctypes.c_void_p]
        cf.CFRelease.restype = None
        sec.SecItemAdd.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        sec.SecItemAdd.restype = ctypes.c_int32
        sec.SecItemUpdate.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        sec.SecItemUpdate.restype = ctypes.c_int32
        sec.SecItemCopyMatching.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        sec.SecItemCopyMatching.restype = ctypes.c_int32
        sec.SecItemDelete.argtypes = [ctypes.c_void_p]
        sec.SecItemDelete.restype = ctypes.c_int32

    def _release(self, ref):
        if ref:
            self._cf.CFRelease(ref)

    def _cfstring(self, text):
        return self._cf.CFStringCreateWithCString(
            self._allocator,
            text.encode("utf-8"),
            _CF_STRING_ENCODING_UTF8,
        )

    def _cfdata(self, text):
        raw = text.encode("utf-8")
        buffer = self._ctypes.create_string_buffer(raw, len(raw))
        ref = self._cf.CFDataCreate(
            self._allocator,
            self._ctypes.cast(buffer, self._ctypes.c_void_p),
            len(raw),
        )
        return ref, buffer

    def _cfdict(self, pairs):
        count = len(pairs)
        keys = (self._ctypes.c_void_p * count)()
        values = (self._ctypes.c_void_p * count)()
        for index, (key, value) in enumerate(pairs):
            keys[index] = key
            values[index] = value
        ref = self._cf.CFDictionaryCreate(
            self._allocator,
            keys,
            values,
            count,
            None,
            None,
        )
        return ref, keys, values

    def _run_query(self, service, account, extra, callback):
        owned = []
        keep = []
        try:
            service_ref = self._cfstring(service)
            if not service_ref:
                return callback(None)
            owned.append(service_ref)
            account_ref = self._cfstring(account)
            if not account_ref:
                return callback(None)
            owned.append(account_ref)
            pairs = [
                (self._sec_class, self._generic_password),
                (self._attr_service, service_ref),
                (self._attr_account, account_ref),
            ]
            pairs.extend(extra)
            query, keys, values = self._cfdict(pairs)
            keep.append(keys)
            keep.append(values)
            if not query:
                return callback(None)
            owned.append(query)
            return callback(query)
        finally:
            for ref in reversed(owned):
                self._release(ref)

    def add(self, service, account, secret):
        if type(secret) is not str:
            return STATUS_OS_FAILURE
        data_ref = None
        try:
            data_ref, _buffer = self._cfdata(secret)
            if not data_ref:
                return STATUS_OS_FAILURE

            def _call(query):
                if query is None:
                    return STATUS_OS_FAILURE
                status = self._sec.SecItemAdd(query, None)
                return map_keychain_osstatus(int(status))

            return self._run_query(
                service,
                account,
                ((self._value_data, data_ref),),
                _call,
            )
        except Exception:
            return STATUS_OS_FAILURE
        finally:
            self._release(data_ref)

    def update(self, service, account, secret):
        if type(secret) is not str:
            return STATUS_OS_FAILURE
        data_ref = None
        attrs_ref = None
        try:
            data_ref, _buffer = self._cfdata(secret)
            if not data_ref:
                return STATUS_OS_FAILURE
            attrs_ref, attrs_keys, attrs_values = self._cfdict(
                ((self._value_data, data_ref),)
            )
            if not attrs_ref:
                return STATUS_OS_FAILURE

            def _call(query):
                if query is None:
                    return STATUS_OS_FAILURE
                status = self._sec.SecItemUpdate(query, attrs_ref)
                return map_keychain_osstatus(int(status))

            return self._run_query(service, account, (), _call)
        except Exception:
            return STATUS_OS_FAILURE
        finally:
            self._release(attrs_ref)
            self._release(data_ref)

    def delete(self, service, account):
        try:

            def _call(query):
                if query is None:
                    return STATUS_OS_FAILURE
                status = self._sec.SecItemDelete(query)
                return map_keychain_osstatus(int(status))

            return self._run_query(service, account, (), _call)
        except Exception:
            return STATUS_OS_FAILURE

    def get(self, service, account):
        ctypes = self._ctypes
        result = ctypes.c_void_p()
        try:

            def _call(query):
                if query is None:
                    return (STATUS_OS_FAILURE, None)
                status = self._sec.SecItemCopyMatching(
                    query,
                    ctypes.byref(result),
                )
                mapped = map_keychain_osstatus(int(status))
                if mapped != STATUS_SUCCESS:
                    return (mapped, None)
                data_ref = result.value
                if not data_ref:
                    return (STATUS_OS_FAILURE, None)
                try:
                    length = int(self._cf.CFDataGetLength(data_ref))
                    pointer = self._cf.CFDataGetBytePtr(data_ref)
                    if not pointer or length < 0:
                        return (STATUS_OS_FAILURE, None)
                    raw = ctypes.string_at(pointer, length)
                finally:
                    self._release(data_ref)
                try:
                    secret = raw.decode("utf-8")
                except UnicodeDecodeError:
                    return (STATUS_OS_FAILURE, None)
                return (STATUS_SUCCESS, secret)

            return self._run_query(
                service,
                account,
                (
                    (self._return_data, self._true),
                    (self._match_limit, self._match_limit_one),
                ),
                _call,
            )
        except Exception:
            return (STATUS_OS_FAILURE, None)
