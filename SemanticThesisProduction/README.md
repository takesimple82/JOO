# Semantic Thesis Production

This package defines the minimum caller-supplied structural attestation that
an authoritative external or future semantic Thesis producer accepted one
`ExplicitThesis`.

`SemanticallyProducedThesis` is a frozen, hashable dataclass containing exactly
`thesis: ExplicitThesis`. The validator requires the exact wrapper and field
types, calls `validate_explicit_thesis()` exactly once, propagates its exception
unchanged, and returns `None` on success.

The wrapper preserves the original Thesis object without copying,
reconstruction, normalization, rewriting, or semantic inference. Duplicate
wrappers are allowed.

Attestation does not prove statement truth, investment validity, evidence or
Hypothesis sufficiency, producer execution, identity or provenance, portfolio
relevance, Expected Value, or suitability for action.

This package does not define producer/reference identity, semantic subtype,
confidence, conviction, lifecycle, Hypothesis linkage, Portfolio impact,
BUY/HOLD/SELL, allocation, CIO judgment, runtime, persistence, registry,
lookup, or orchestration.
