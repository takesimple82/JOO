from __future__ import annotations

from datetime import datetime, timedelta, timezone


def require_exact_type(
    name: str,
    value: object,
    expected: type,
) -> None:
    if type(value) is not expected:
        raise TypeError(
            f"{name} must be {expected.__name__}"
        )


def require_string(name: str, value: object) -> None:
    require_exact_type(name, value, str)


def require_nonblank_string(name: str, value: object) -> None:
    require_string(name, value)
    if value.strip() == "":
        raise ValueError(f"{name} must not be blank")


def require_optional_nonblank_string(
    name: str,
    value: object,
) -> None:
    if value is None:
        return
    require_nonblank_string(name, value)


def require_membership(
    name: str,
    value: object,
    allowed: tuple[str, ...],
    allowed_name: str,
) -> None:
    require_string(name, value)
    if value not in allowed:
        raise ValueError(
            f"{name} must be one of {allowed_name}"
        )


def require_utc_datetime(name: str, value: object) -> None:
    require_exact_type(name, value, datetime)
    if value.tzinfo is not timezone.utc:
        raise ValueError(
            f"{name} tzinfo must be datetime.timezone.utc"
        )


def require_exact_bool(name: str, value: object) -> None:
    require_exact_type(name, value, bool)


def require_optional_nonnegative_timedelta(
    name: str,
    value: object,
) -> None:
    if value is None:
        return
    require_exact_type(name, value, timedelta)
    if value < timedelta(0):
        raise ValueError(f"{name} must not be negative")
