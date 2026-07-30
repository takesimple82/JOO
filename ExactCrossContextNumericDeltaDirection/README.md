# Exact Cross-Context Numeric Delta Direction

This package classifies the arithmetic sign of one accepted exact
cross-context numeric delta.

## Public contract

`ExactCrossContextNumericDeltaDirectionStatus` has exactly three states:

1. `NEGATIVE`
2. `ZERO`
3. `POSITIVE`

`classify_exact_cross_context_numeric_delta_direction()` accepts only an
`ExactCrossContextNumericDelta`. It calls the accepted delta validator exactly
once and propagates its exception unchanged.

After validation, classification is deterministic:

1. `delta.value.is_zero()` returns `ZERO`.
2. Otherwise, `delta.value.is_signed()` returns `NEGATIVE`.
3. Otherwise, it returns `POSITIVE`.

Positive and negative Decimal zero are both `ZERO`. The classifier performs no
subtraction, conversion, tolerance comparison, rounding, normalization,
copying, or reconstruction. It does not read or change decimal context
precision, traps, flags, or rounding mode.

## Boundaries

This package does not accept a calculation wrapper, recheck applicability,
convert units, determine materiality, generate Signal, use float or Fraction,
or implement runtime, persistence, orchestration, Hypothesis, Thesis,
Portfolio impact, or CIO decisions.
