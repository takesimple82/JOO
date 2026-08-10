from __future__ import annotations

from datetime import datetime
from enum import Enum


def require_string(name: str, value: object) -> None:
    if type(value) is not str:
        raise TypeError(f"{name} must be str")


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


def require_enum(name: str, value: object, enum_cls: type) -> None:
    if type(value) is not enum_cls:
        raise TypeError(f"{name} must be {enum_cls.__name__}")
    if not isinstance(value, Enum):
        raise TypeError(f"{name} must be {enum_cls.__name__}")


def require_datetime(name: str, value: object) -> None:
    if type(value) is not datetime:
        raise TypeError(f"{name} must be datetime")


def require_optional_datetime(name: str, value: object) -> None:
    if value is None:
        return
    require_datetime(name, value)


def require_bytes(name: str, value: object) -> None:
    if type(value) is not bytes:
        raise TypeError(f"{name} must be bytes")


def require_int(name: str, value: object) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be int")


def require_bool(name: str, value: object) -> None:
    if type(value) is not bool:
        raise TypeError(f"{name} must be bool")


def require_tuple_of(
    name: str,
    value: object,
    element_type: type,
) -> None:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be tuple")
    for index, item in enumerate(value):
        if type(item) is not element_type:
            raise TypeError(
                f"{name}[{index}] must be {element_type.__name__}"
            )
