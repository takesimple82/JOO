# Evidence Comparison

## Purpose

Evidence Comparison compares two accepted
`ExactObservedNumericProposition` objects and returns one deterministic
`EvidenceComparisonStatus`. It performs no extraction, aggregation, or
contradiction classification.

## Comparison Identity

Two propositions are comparable only when these fields are exactly equal, in
this order:

1. `subject_id`
2. `predicate_id`
3. `unit_id`
4. `effective_context_id`

`proposition_id` and `finding_id` do not participate in comparability. The
contract assumes the single authoritative Knowledge Engine producer and
canonical identifier namespace accepted by Evidence Proposition.

## Statuses

- `NOT_COMPARABLE`: at least one comparison-identity field differs.
- `NUMERICALLY_COMPATIBLE`: all identity fields match and the finite Decimal
  values are mathematically equal.
- `NUMERICALLY_INCOMPATIBLE`: all identity fields match and the finite Decimal
  values are mathematically unequal.

Non-comparability is normal domain output. Numerical incompatibility is not a
final contradiction and does not select truth, authority, freshness, or
preferred evidence.

## Validation and Equality

The accepted proposition validator always validates the left input first and
the right input second. Its exceptions propagate unchanged. Comparison begins
only after both validations succeed.

Values use direct Decimal mathematical equality. Consequently,
`Decimal("1.0")` equals `Decimal("1.00")`, `Decimal("0")` equals
`Decimal("-0")`, and `Decimal("1E+2")` equals `Decimal("100")`.

For valid inputs, comparison status is symmetric when argument order is
reversed. The function does not mutate, reconstruct, trim, case-fold,
normalize, quantize, round, or convert either proposition or its values.

## Boundaries

This package does not establish truth, contradiction, corroboration, support,
opposition, source independence, duplication, linkage correctness, unit
equivalence, or context overlap. It performs no tolerance handling, registry
lookup, provider call, runtime execution, persistence, or serialization.

Production code depends only on Evidence Proposition, this package, and the
Python standard library. Evidence Proposition and Evidence Aggregation remain
independent and unchanged. Final contradiction semantics belong to a future
Evidence Contradiction boundary.
