from __future__ import annotations

import sys
from dataclasses import dataclass

from ProviderGateway.adapters.kb_open_api import KbOpenApiAdapter
from ProviderGateway.adapters.kb_openapi_live_broker_transport import (
    DEFAULT_BASE_URL,
    KbOpenApiLiveBrokerTransport,
)
from ProviderGateway.adapters.ports import ExplicitTransportFailure
from ProviderGateway.auth import kb_openapi_host_identity
from ProviderGateway.auth import kb_openapi_keychain
from ProviderGateway.models.types import ExplicitBrokerAdapterBinding
from ProviderGateway.models.vocabularies import (
    RESERVED_KB_OPEN_API_PROVIDER_ID,
)

_ALLOWED_ARGV = {
    ("configure", "kb"): "configure",
    ("configure", "kb", "--replace"): "replace",
    ("configure", "kb", "--delete"): "delete",
    ("configure", "kb", "--host"): "host",
    ("configure", "kb", "--host", "--reset"): "host_reset",
    ("configure", "kb", "--replace", "--host"): "replace_host",
}

_MSG_UNSUPPORTED = "unsupported configure invocation"
_MSG_ALREADY_EXISTS = "kb openapi keychain items already exist"
_MSG_KEYCHAIN_UNAVAILABLE = "kb openapi keychain is unavailable"
_MSG_INVALID_SECRET = "kb openapi secret values are invalid"
_MSG_PAIR_WRITE_FAILED = (
    "kb openapi keychain pair write failed; "
    "run first-time configure again"
)
_MSG_HOST_WRITE_FAILED = "kb openapi host identity write failed"
_MSG_CONFIGURED_AUTO = (
    "kb openapi configured; keychain stored; "
    "host written; mac mode auto"
)
_MSG_CONFIGURED_OVERRIDE = (
    "kb openapi configured; keychain stored; "
    "host written; mac mode override"
)
_MSG_REPLACED = "kb openapi keychain pair replaced"
_MSG_REPLACE_FAILED = (
    "kb openapi keychain pair replace failed; "
    "run first-time configure again"
)
_MSG_DELETED = "kb openapi keychain pair deleted"
_MSG_DELETE_FAILED = "kb openapi keychain pair delete failed"
_MSG_HOST_WRITTEN_AUTO = (
    "kb openapi host identity written; mac mode auto"
)
_MSG_HOST_WRITTEN_OVERRIDE = (
    "kb openapi host identity written; mac mode override"
)
_MSG_HOST_RESET = "kb openapi host identity reset"
_MSG_HOST_RESET_FAILED = "kb openapi host identity reset failed"


@dataclass(frozen=True)
class KbOpenApiConfigureResult:
    ok: bool
    operation: str
    message: str


@dataclass(frozen=True)
class KbOpenApiRuntimeReady:
    adapter: object
    binding: object
    transport: object


def compose_kb_openapi_live_runtime(
    http_post,
    clock,
    parameter_profile,
    *,
    credential_ref="kb_open_api",
    keychain_backend=None,
    host_identity_path=None,
    mac_deriver=None,
    base_url=DEFAULT_BASE_URL,
    excg_mktpr_ccd="",
    http_timeout_seconds=10,
):
    if host_identity_path is None:
        host_identity_path = (
            kb_openapi_host_identity.default_kb_openapi_host_identity_path()
        )
    if mac_deriver is None:
        mac_deriver = (
            kb_openapi_host_identity.derive_active_primary_wifi_mac
        )
    resolved = kb_openapi_host_identity.resolve_kb_openapi_host_identity(
        host_identity_path,
        mac_deriver,
    )
    if resolved is None:
        return ExplicitTransportFailure("VALIDATION_FAILURE", None)
    if keychain_backend is None:
        keychain_backend = (
            kb_openapi_keychain.make_production_keychain_backend()
        )
    supplier = (
        kb_openapi_keychain.make_kb_openapi_keychain_credential_supplier(
            keychain_backend,
            expected_credential_ref=credential_ref,
        )
    )
    transport = KbOpenApiLiveBrokerTransport(
        http_post,
        clock,
        resolved.ip_addr,
        resolved.mac_addr,
        base_url=base_url,
        excg_mktpr_ccd=excg_mktpr_ccd,
        http_timeout_seconds=http_timeout_seconds,
    )
    binding = ExplicitBrokerAdapterBinding(
        RESERVED_KB_OPEN_API_PROVIDER_ID,
        credential_ref,
        parameter_profile,
    )
    adapter = KbOpenApiAdapter(
        binding,
        transport,
        supplier,
        clock,
    )
    return KbOpenApiRuntimeReady(adapter, binding, transport)


def _emit(emit, result):
    if emit is not None:
        emit(result.message)


def _as_argv_tuple(argv):
    if type(argv) is list:
        argv = tuple(argv)
    if type(argv) is not tuple:
        return None
    for item in argv:
        if type(item) is not str:
            return None
    return argv


def _collect_secrets(prompt_secret):
    app_key = prompt_secret("appKey: ")
    app_secret = prompt_secret("appSecret: ")
    return app_key, app_secret


def _collect_host(prompt_line):
    ip_addr = prompt_line("ip_addr: ")
    mac_input = prompt_line("mac_addr: ")
    if mac_input == "":
        return ip_addr, None
    return ip_addr, mac_input


def _configure_first_time(
    prompt_secret,
    prompt_line,
    keychain_backend,
    host_identity_path,
):
    occupancy = kb_openapi_keychain.inspect_kb_openapi_keychain_pair(
        keychain_backend
    )
    if occupancy == "occupied":
        return KbOpenApiConfigureResult(
            False,
            "configure",
            _MSG_ALREADY_EXISTS,
        )
    if occupancy != "absent":
        return KbOpenApiConfigureResult(
            False,
            "configure",
            _MSG_KEYCHAIN_UNAVAILABLE,
        )
    try:
        app_key, app_secret = _collect_secrets(prompt_secret)
    except Exception:
        return KbOpenApiConfigureResult(
            False,
            "configure",
            _MSG_KEYCHAIN_UNAVAILABLE,
        )
    stored = kb_openapi_keychain.store_kb_openapi_keychain_pair(
        keychain_backend,
        app_key,
        app_secret,
    )
    if not stored.ok:
        if stored.code == "invalid_secret":
            return KbOpenApiConfigureResult(
                False,
                "configure",
                _MSG_INVALID_SECRET,
            )
        return KbOpenApiConfigureResult(
            False,
            "configure",
            _MSG_PAIR_WRITE_FAILED,
        )
    try:
        ip_addr, mac_addr = _collect_host(prompt_line)
    except Exception:
        return KbOpenApiConfigureResult(
            False,
            "configure",
            _MSG_HOST_WRITE_FAILED,
        )
    written = kb_openapi_host_identity.write_kb_openapi_host_identity(
        host_identity_path,
        ip_addr,
        mac_addr,
    )
    if not written:
        return KbOpenApiConfigureResult(
            False,
            "configure",
            _MSG_HOST_WRITE_FAILED,
        )
    if mac_addr is None:
        message = _MSG_CONFIGURED_AUTO
    else:
        message = _MSG_CONFIGURED_OVERRIDE
    return KbOpenApiConfigureResult(True, "configure", message)


def _configure_replace(
    prompt_secret,
    prompt_line,
    keychain_backend,
    host_identity_path,
    also_host,
):
    try:
        app_key, app_secret = _collect_secrets(prompt_secret)
    except Exception:
        return KbOpenApiConfigureResult(
            False,
            "replace",
            _MSG_KEYCHAIN_UNAVAILABLE,
        )
    replaced = kb_openapi_keychain.replace_kb_openapi_keychain_pair(
        keychain_backend,
        app_key,
        app_secret,
    )
    if not replaced.ok:
        if replaced.code == "invalid_secret":
            return KbOpenApiConfigureResult(
                False,
                "replace",
                _MSG_INVALID_SECRET,
            )
        return KbOpenApiConfigureResult(
            False,
            "replace",
            _MSG_REPLACE_FAILED,
        )
    if not also_host:
        return KbOpenApiConfigureResult(
            True,
            "replace",
            _MSG_REPLACED,
        )
    host_result = _configure_host(
        prompt_line,
        host_identity_path,
        operation="replace_host",
    )
    if not host_result.ok:
        return host_result
    if host_result.message == _MSG_HOST_WRITTEN_OVERRIDE:
        message = _MSG_CONFIGURED_OVERRIDE
    else:
        message = _MSG_CONFIGURED_AUTO
    return KbOpenApiConfigureResult(True, "replace_host", message)


def _configure_delete(keychain_backend):
    deleted = kb_openapi_keychain.delete_kb_openapi_keychain_pair(
        keychain_backend
    )
    if deleted.ok:
        return KbOpenApiConfigureResult(
            True,
            "delete",
            _MSG_DELETED,
        )
    return KbOpenApiConfigureResult(
        False,
        "delete",
        _MSG_DELETE_FAILED,
    )


def _configure_host(prompt_line, host_identity_path, operation="host"):
    try:
        ip_addr, mac_addr = _collect_host(prompt_line)
    except Exception:
        return KbOpenApiConfigureResult(
            False,
            operation,
            _MSG_HOST_WRITE_FAILED,
        )
    written = kb_openapi_host_identity.write_kb_openapi_host_identity(
        host_identity_path,
        ip_addr,
        mac_addr,
    )
    if not written:
        return KbOpenApiConfigureResult(
            False,
            operation,
            _MSG_HOST_WRITE_FAILED,
        )
    if mac_addr is None:
        message = _MSG_HOST_WRITTEN_AUTO
    else:
        message = _MSG_HOST_WRITTEN_OVERRIDE
    return KbOpenApiConfigureResult(True, operation, message)


def _configure_host_reset(host_identity_path):
    deleted = kb_openapi_host_identity.delete_kb_openapi_host_identity(
        host_identity_path
    )
    if deleted:
        return KbOpenApiConfigureResult(
            True,
            "host_reset",
            _MSG_HOST_RESET,
        )
    return KbOpenApiConfigureResult(
        False,
        "host_reset",
        _MSG_HOST_RESET_FAILED,
    )


def dispatch_kb_openapi_configure(
    argv,
    *,
    prompt_secret,
    prompt_line,
    keychain_backend,
    host_identity_path,
    emit=None,
):
    parsed = _as_argv_tuple(argv)
    if parsed is None:
        result = KbOpenApiConfigureResult(
            False,
            "unsupported",
            _MSG_UNSUPPORTED,
        )
        _emit(emit, result)
        return result
    operation = _ALLOWED_ARGV.get(parsed)
    if operation is None:
        result = KbOpenApiConfigureResult(
            False,
            "unsupported",
            _MSG_UNSUPPORTED,
        )
        _emit(emit, result)
        return result
    if operation == "configure":
        result = _configure_first_time(
            prompt_secret,
            prompt_line,
            keychain_backend,
            host_identity_path,
        )
    elif operation == "replace":
        result = _configure_replace(
            prompt_secret,
            prompt_line,
            keychain_backend,
            host_identity_path,
            False,
        )
    elif operation == "replace_host":
        result = _configure_replace(
            prompt_secret,
            prompt_line,
            keychain_backend,
            host_identity_path,
            True,
        )
    elif operation == "delete":
        result = _configure_delete(keychain_backend)
    elif operation == "host":
        result = _configure_host(prompt_line, host_identity_path)
    else:
        result = _configure_host_reset(host_identity_path)
    _emit(emit, result)
    return result


if __name__ == "__main__":
    import getpass

    _result = dispatch_kb_openapi_configure(
        sys.argv[1:],
        prompt_secret=getpass.getpass,
        prompt_line=input,
        keychain_backend=(
            kb_openapi_keychain.make_production_keychain_backend()
        ),
        host_identity_path=(
            kb_openapi_host_identity.default_kb_openapi_host_identity_path()
        ),
        emit=print,
    )
    raise SystemExit(0 if _result.ok else 1)
