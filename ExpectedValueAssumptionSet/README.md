# Expected Value Assumption Set

This package defines immutable, caller-supplied outcome assumptions for one
semantically produced Portfolio Impact. It does not calculate Expected Value.

`ExplicitExpectedValueOutcomeAssumption` contains exactly:

1. `outcome_id: str`
2. `statement: str`
3. `probability: Decimal`
4. `value: Decimal`

The outcome validator requires exact nonblank built-in strings and exact
finite built-in Decimal values. Probability must be in the inclusive range
zero through one. Negative, zero, and positive outcome values are accepted.

`ExplicitExpectedValueAssumptionSet` contains exactly:

1. `assumption_set_id: str`
2. `impact: SemanticallyProducedPortfolioImpact`
3. `unit_id: str`
4. `outcomes: tuple[ExplicitExpectedValueOutcomeAssumption, ...]`

The set validator requires an exact nonblank ID, validates the exact semantic
Impact exactly once, requires an exact nonblank unit and an exact nonempty
built-in tuple, then validates every outcome exactly once in caller order.
After an outcome is valid, the first duplicate `outcome_id` is rejected.

Both models are frozen, hashable, and structurally equal. Validation preserves
the supplied Impact, tuple, outcome, string, and Decimal objects and tuple
order. It does not sort, trim, normalize, copy, reconstruct, deduplicate,
infer, or convert any input.

## Boundaries

Structural validation does not require probabilities to total one and does
not prove that outcomes are exhaustive, mutually exclusive, likely, or
correct. The opaque set-level `unit_id` applies to all outcome values without
unit or currency conversion.

This package does not own fixed scenario enums, generated IDs, confidence,
materiality, discounting, probability inference, exact Expected Value
arithmetic or calculation, recommendations, allocation, runtime, registries,
persistence, migration, lookup, or orchestration.
