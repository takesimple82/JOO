# Semantic Hypothesis Production

This package defines the minimum structural acceptance boundary for an
`ExplicitHypothesis` that a caller attests was accepted by an authoritative
external or future semantic Hypothesis producer.

`SemanticallyProducedHypothesis` is a frozen dataclass containing exactly:

1. `hypothesis: ExplicitHypothesis`

`validate_semantically_produced_hypothesis()` requires the exact wrapper type,
then the exact `ExplicitHypothesis` field type. It calls
`validate_explicit_hypothesis()` exactly once, propagates its exception
unchanged, and returns `None` on success.

The wrapper preserves the supplied Hypothesis object directly. It is hashable
and structurally equal, and performs no copying, reconstruction,
normalization, rewriting, or semantic inference. Duplicate wrappers are
allowed.

The wrapper is caller-supplied structural attestation only. It does not prove
statement truth, actual testability, causal or predictive correctness,
evidence sufficiency, producer execution, producer identity or provenance, or
portfolio relevance.

This package does not define producer or reference identity, confidence,
probability, semantic subtype/status, Signal linkage, evidence aggregation,
Hypothesis lifecycle, Thesis, Expected Value, Portfolio impact, CIO judgment,
runtime, persistence, registry, lookup, or orchestration.
