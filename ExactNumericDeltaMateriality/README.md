# Exact Numeric Delta Materiality

This package classifies whether the absolute magnitude of one accepted exact
cross-context numeric delta exceeds an explicit caller-supplied threshold.

## Public policy

`ExactNumericDeltaMaterialityPolicy` is a frozen dataclass containing:

1. `unit_id: str`
2. `threshold: Decimal`

`validate_exact_numeric_delta_materiality_policy()` requires the exact policy
type, an exact nonblank built-in string unit, and an exact finite built-in
Decimal threshold. The threshold must be non-negative. Positive and negative
Decimal zero are valid zero thresholds. Inputs are not normalized or coerced.

## Public classification

`ExactNumericDeltaMaterialityStatus` has:

- `UNIT_MISMATCH`
- `IMMATERIAL`
- `MATERIAL`

`classify_exact_numeric_delta_materiality(delta, policy)` validates the delta
exactly once and then the policy exactly once. If their stored unit IDs differ
exactly, it returns `UNIT_MISMATCH`.

For equal units, the classifier obtains the exact magnitude with
`delta.value.copy_abs()`. A magnitude strictly greater than the policy
threshold is `MATERIAL`; equality and smaller magnitudes are `IMMATERIAL`.
With a zero threshold, zero is immaterial and every nonzero finite delta is
material. Positive and negative deltas of equal magnitude classify equally.

## Boundaries

Direction and calculation wrappers are not inputs. This package does not
recheck applicability, convert or look up units, hardcode thresholds, use
tolerance, epsilon, float, Fraction, or Decimal subtraction, mutate decimal
context, generate Signal, or implement runtime, persistence, orchestration,
Hypothesis, Thesis, Portfolio impact, or CIO decisions.
