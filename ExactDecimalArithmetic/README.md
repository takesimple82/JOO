# Exact Decimal Arithmetic

This package provides context-independent arithmetic for exact finite
`decimal.Decimal` values.

## Public contracts

`add_exact_decimal(augend, addend) -> Decimal` validates the augend first and
the addend second. It aligns both signed integer coefficients at the finer
input exponent and adds them with Python integers. The result retains that
finer exponent.

`multiply_exact_decimal(multiplicand, multiplier) -> Decimal` validates the
multiplicand first and the multiplier second. It multiplies the signed integer
coefficients with Python integers and uses the sum of the input exponents.
Nonzero result signs follow the XOR of the input signs.

`subtract_exact_decimal(minuend, subtrahend) -> Decimal` validates the minuend
first and the subtrahend second. Each must be the exact built-in `Decimal`
type and finite.

All public functions require exact finite built-in Decimal operands in
declared order. Validation raises:

- `TypeError("<name> must be Decimal")` for a wrong type or Decimal subclass.
- `ValueError("<name> must be finite")` for NaN or infinity.

Each function returns the exact mathematical result. Calculations do not use
Decimal arithmetic operators. They read immutable Decimal tuples, operate on
exact Python integer coefficients, and construct results directly from Decimal
tuples.

Addition and subtraction use the finer input exponent. Multiplication uses the
sum of the input exponents. A zero result is deterministic positive zero at
the exponent selected by the operation. Inputs remain unchanged. The
implementation neither reads nor changes the active decimal context, its
precision, traps, flags, or rounding mode.

## Non-responsibilities

This package does not know about propositions, identifiers, units,
compatibility, baseline/current roles, direction classification, materiality,
Signal, unit conversion, float or Fraction values, runtime, persistence,
orchestration, or CIO decisions.
