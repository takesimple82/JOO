# Explicit Thesis

This package defines the minimum structural identity and caller-supplied
statement for one explicit Thesis.

`ExplicitThesis` is a frozen, hashable dataclass containing exactly:

1. `thesis_id: str`
2. `statement: str`

`validate_explicit_thesis()` requires the exact model type and validates the
ID before the statement. Both fields must be exact nonblank built-in strings.
Whitespace-only values and subclasses are rejected. Surrounding whitespace
and Unicode representation on otherwise nonblank values are preserved.

Validation performs no trimming, normalization, rewriting, copying,
reconstruction, identity generation, or semantic inference.

A structurally valid Thesis is not a numeric Signal, Hypothesis, direction,
materiality status, or portfolio action. Its nonblank statement is not thereby
certified as an investment proposition, evidence-supported, semantically
valid, portfolio relevant, or suitable for action.

This package does not include semantic production, Hypothesis linkage,
evidence, lifecycle, catalysts, risks, invalidation conditions, confidence,
conviction, Expected Value, BUY/HOLD/SELL, target prices, Portfolio impact,
allocation, CIO judgment, runtime, persistence, registry, lookup, or
orchestration.
