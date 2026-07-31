# Exact Expected Value

This package owns one deterministic calculation: the exact probability-weighted
value of an applicable, semantically produced Expected Value Assumption Set.

`ExactExpectedValue` is a frozen, hashable dataclass containing exactly:

1. `source: SemanticallyProducedExpectedValueAssumptionSet`
2. `value: Decimal`

The result preserves the exact supplied semantic source object. It does not
copy the assumption-set ID or unit ID; both remain owned by and accessible
through the source.

`ExactExpectedValueCalculation` contains the accepted assumption-set
applicability status and an optional exact result. `APPLICABLE` requires a
result. `PROBABILITY_TOTAL_MISMATCH` requires `None`.

`calculate_exact_expected_value()` validates the semantic source exactly once,
then delegates probability-total classification to the applicability-owned
private unchecked boundary. The private boundary is used only after accepted
upstream validation and is not public API.

For an applicable source, the calculator starts with exactly `Decimal("0")`.
It visits outcomes in caller order, multiplies each probability and value with
`multiply_exact_decimal()`, and accumulates each product with
`add_exact_decimal()`. Those accepted helpers remain authoritative for sign,
exponent, positive-zero behavior, and Decimal-context independence. The
calculator performs no normalization or result canonicalization.

## Non-responsibilities

This package does not create or validate assumptions independently, interpret
Portfolio Impact, infer probabilities or values, establish completeness or
truth, discount values, convert units or currencies, determine confidence or
materiality, recommend, allocate, or implement Portfolio, constraints, human
approval, audit, runtime, registry, persistence, migration, or orchestration.
