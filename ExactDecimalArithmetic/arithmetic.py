from decimal import Decimal


def subtract_exact_decimal(
    minuend: Decimal,
    subtrahend: Decimal,
) -> Decimal:
    _validate_finite_decimal("minuend", minuend)
    _validate_finite_decimal("subtrahend", subtrahend)

    minuend_tuple = minuend.as_tuple()
    subtrahend_tuple = subtrahend.as_tuple()
    common_exponent = min(
        minuend_tuple.exponent,
        subtrahend_tuple.exponent,
    )

    minuend_coefficient = _signed_coefficient(
        minuend_tuple.sign,
        minuend_tuple.digits,
    ) * 10 ** (minuend_tuple.exponent - common_exponent)
    subtrahend_coefficient = _signed_coefficient(
        subtrahend_tuple.sign,
        subtrahend_tuple.digits,
    ) * 10 ** (
        subtrahend_tuple.exponent - common_exponent
    )
    result_coefficient = (
        minuend_coefficient - subtrahend_coefficient
    )

    result_sign = int(result_coefficient < 0)
    result_digits = _unsigned_integer_digits(
        abs(result_coefficient)
    )
    return Decimal(
        (
            result_sign,
            result_digits,
            common_exponent,
        )
    )


def _validate_finite_decimal(name: str, value: Decimal) -> None:
    if type(value) is not Decimal:
        raise TypeError(f"{name} must be Decimal")
    if not value.is_finite():
        raise ValueError(f"{name} must be finite")


def _signed_coefficient(
    sign: int,
    digits: tuple[int, ...],
) -> int:
    coefficient = 0
    for digit in digits:
        coefficient = coefficient * 10 + digit
    return -coefficient if sign else coefficient


def _unsigned_integer_digits(
    value: int,
) -> tuple[int, ...]:
    if value == 0:
        return (0,)

    reversed_digits = []
    while value:
        value, digit = divmod(value, 10)
        reversed_digits.append(digit)
    return tuple(reversed(reversed_digits))
