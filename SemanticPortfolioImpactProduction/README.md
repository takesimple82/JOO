# Semantic Portfolio Impact Production

This package defines the minimum caller-supplied structural attestation that
an authoritative external or future semantic producer accepted one
`ExplicitPortfolioImpact`.

`SemanticallyProducedPortfolioImpact` is a frozen, hashable dataclass
containing exactly:

1. `impact: ExplicitPortfolioImpact`

`validate_semantically_produced_portfolio_impact()` requires the exact
production model type and exact Impact field type. It calls
`validate_explicit_portfolio_impact()` exactly once, propagates its exception
object unchanged, and returns `None` on success.

The wrapper stores the supplied Impact object directly. It performs no
copying, reconstruction, normalization, mutation, or semantic inference.
Structural equality and hashing follow the wrapped Impact, and duplicate
wrappers are allowed.

The wrapper records only a caller-supplied attestation. It does not prove that
the Impact direction is correct, that the Thesis is true or causal, that
evidence is sufficient, or that an actual semantic producer executed.

## Non-responsibilities

This package does not define production or producer identity, provenance,
confidence, probability, timestamps, materiality, Expected Value,
recommendations, allocation, approval, runtime, registries, persistence,
migration, lookup, or orchestration.
