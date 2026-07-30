# Exact Decimal Arithmetic

This package provides context-independent arithmetic for exact finite
`decimal.Decimal` values.

## Public contract

`subtract_exact_decimal(minuend, subtrahend) -> Decimal` validates the minuend
first and the subtrahend second. Each must be the exact built-in `Decimal`
type and finite.

Validation raises:

- `TypeError("<name> must be Decimal")` for a wrong type or Decimal subclass.
- `ValueError("<name> must be finite")` for NaN or infinity.

The function returns the exact mathematical result of `minuend - subtrahend`.
It does not use Decimal arithmetic operators. Instead, it reads each immutable
Decimal tuple, aligns signed integer coefficients at the finer input exponent,
subtracts those exact Python integers, and constructs the result directly from
a Decimal tuple.

The result uses the finer input exponent and therefore preserves that input
scale. A zero result is deterministic positive zero at the finer exponent.
Inputs remain unchanged. The implementation neither reads nor changes the
active decimal context, its precision, traps, flags, or rounding mode.

## Non-responsibilities

This package does not know about propositions, identifiers, units,
compatibility, baseline/current roles, direction classification, materiality,
Signal, unit conversion, float or Fraction values, runtime, persistence,
orchestration, or CIO decisions.
