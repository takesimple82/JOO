# Expected Value Assumption Set Applicability

This package deterministically classifies whether the exact probabilities in
one structurally valid Expected Value Assumption Set total exactly one.

`ExpectedValueAssumptionSetApplicabilityStatus` contains:

- `PROBABILITY_TOTAL_MISMATCH`
- `APPLICABLE`

`classify_expected_value_assumption_set_applicability()` validates the
supplied `ExplicitExpectedValueAssumptionSet` exactly once and propagates its
exception unchanged. It then traverses outcomes in caller order, beginning
with `Decimal("0")`, and accumulates every probability with
`add_exact_decimal()`.

The classifier returns `PROBABILITY_TOTAL_MISMATCH` unless the exact total is
numerically equal to `Decimal("1")`; otherwise it returns `APPLICABLE`.
Decimal scale and signed-zero representation do not affect numerical equality.
No built-in `sum()`, ordinary Decimal addition, tolerance, or epsilon is used.

A private unchecked classifier contains only the post-validation
classification logic so a future downstream validator can reuse it after
validating a semantic wrapper. The private helper is not public API.
The applicability package explicitly owns this internal boundary. Approved
internal consumers may use it only after completing the accepted upstream
validation; it is not re-exported, and probability-total logic must not be
duplicated elsewhere.

## Non-responsibilities

Applicability does not prove that outcomes are exhaustive or mutually
exclusive, that probabilities are accurate, that statements or values are
true, or that market assumptions are correct. It does not mutate, reorder,
sort, copy, normalize, or reconstruct outcomes or probabilities, calculate
Expected Value, convert units, recommend, allocate, or perform runtime,
registry, persistence, migration, lookup, or orchestration.
