from __future__ import annotations

SECRET_FIELD_NAMES = (
    "token",
    "password",
    "api_key",
    "apikey",
    "secret",
    "authorization",
    "access_token",
    "refresh_token",
    "credential",
    "credentials",
)


def resolve_outbound_credential(
    credential_ref: str,
    supplier,
) -> str | None:
    try:
        secret = supplier(credential_ref)
    except Exception:
        return None
    if type(secret) is not str:
        return None
    if secret.strip() == "":
        return None
    return secret


def apply_outbound_credential(secret: str) -> str:
    return secret


def is_secret_field_name(name: object) -> bool:
    return type(name) is str and name in SECRET_FIELD_NAMES


def project_opaque_payload(body: dict) -> dict:
    projected = {}
    for key, value in body.items():
        if is_secret_field_name(key):
            continue
        projected[key] = value
    return projected


def payload_contains_secret(
    payload: dict,
    secret: str,
) -> bool:
    for key, value in payload.items():
        if is_secret_field_name(key):
            return True
        if value is secret:
            return True
        if type(value) is str and secret in value:
            return True
    return False


def sanitize_detail(
    detail: object,
    secret: str | None,
) -> str | None:
    if detail is None:
        return None
    if type(detail) is not str:
        return None
    if detail.strip() == "":
        return None
    if secret is not None and secret in detail:
        return None
    for name in SECRET_FIELD_NAMES:
        if name in detail:
            return None
    return detail
