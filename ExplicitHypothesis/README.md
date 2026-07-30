# Explicit Hypothesis

This package defines the minimum canonical structural identity and
caller-supplied statement for one explicit Hypothesis.

## Public contract

`ExplicitHypothesis` is a frozen dataclass containing exactly:

1. `hypothesis_id: str`
2. `statement: str`

It has no defaults, custom methods, slots, or generated identity. It is
hashable and uses structural equality.

`validate_explicit_hypothesis()` requires the exact model type, then validates
`hypothesis_id` and `statement` in that order. Each field must be an exact
nonblank built-in string. The validator rejects subclasses and returns `None`
on success.

Validation does not trim, normalize, rewrite, case-fold, copy, reconstruct, or
infer either value. Whitespace-only strings are rejected, while surrounding
whitespace on otherwise nonblank strings is accepted and preserved.

## Semantic limitation

This model is only a structural boundary. A valid object does not certify that
its statement is testable, explanatory, causal, predictive,
evidence-supported, semantically valid, or portfolio relevant. Arbitrary
nonblank text is not thereby established as a valid semantic Hypothesis.

## Non-responsibilities

This package does not include Signal objects or identities, Signal linkage,
finding, proposition, subject, predicate, or effective-context identifiers,
evidence aggregation, semantic production or attestation, lifecycle or
status, confidence, probability, Thesis, Expected Value, Portfolio impact,
CIO judgment, runtime, persistence, registry, lookup, or orchestration.
