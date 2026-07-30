from decimal import Decimal


def add_exact_decimal(
    augend: Decimal,
    addend: Decimal,
) -> Decimal:
    _validate_finite_decimal("augend", augend)
    _validate_finite_decimal("addend", addend)

    augend_tuple = augend.as_tuple()
    addend_tuple = addend.as_tuple()
    common_exponent = min(
        augend_tuple.exponent,
        addend_tuple.exponent,
    )

    augend_coefficient = _signed_coefficient(
        augend_tuple.sign,
        augend_tuple.digits,
    ) * 10 ** (augend_tuple.exponent - common_exponent)
    addend_coefficient = _signed_coefficient(
        addend_tuple.sign,
        addend_tuple.digits,
    ) * 10 ** (addend_tuple.exponent - common_exponent)
    result_coefficient = (
        augend_coefficient + addend_coefficient
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


def multiply_exact_decimal(
    multiplicand: Decimal,
    multiplier: Decimal,
) -> Decimal:
    _validate_finite_decimal("multiplicand", multiplicand)
    _validate_finite_decimal("multiplier", multiplier)

    multiplicand_tuple = multiplicand.as_tuple()
    multiplier_tuple = multiplier.as_tuple()
    result_exponent = (
        multiplicand_tuple.exponent
        + multiplier_tuple.exponent
    )
    result_coefficient = (
        _signed_coefficient(
            multiplicand_tuple.sign,
            multiplicand_tuple.digits,
        )
        * _signed_coefficient(
            multiplier_tuple.sign,
            multiplier_tuple.digits,
        )
    )

    result_sign = int(result_coefficient < 0)
    result_digits = _unsigned_integer_digits(
        abs(result_coefficient)
    )
    return Decimal(
        (
            result_sign,
            result_digits,
            result_exponent,
        )
    )


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
