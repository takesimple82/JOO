# Portfolio Observation Context

This package owns one explicit caller-supplied context in which the state of
one canonical Portfolio may be observed.

`ExplicitPortfolioObservationContext` is a frozen, hashable dataclass with:

1. `observation_context_id: str`
2. `portfolio_id: str`

The context identity is opaque and canonical only within the Portfolio
Observation Context namespace. `portfolio_id` refers to the accepted
`ExplicitPortfolio.portfolio_id`. Neither identity encodes time, version,
state, source, or lifecycle.

`validate_explicit_portfolio_observation_context()` requires the exact context
model, validates the exact nonblank built-in context ID, then validates the
exact nonblank built-in Portfolio ID. It returns `None` on success and
preserves the supplied identifiers without trimming, normalization,
conversion, copying, or reconstruction.

The context is distinct from `ResearchSnapshot`, portfolio configuration
versions, holding observations, and complete Portfolio snapshots. It does not
claim an observation occurred and does not generate or require a timestamp.

## Non-responsibilities

This package does not own holdings, positions, collections, quantities, prices,
valuation, research reproducibility, timestamps, runtime clocks, persistence
events, data sources, lifecycle, recommendations, allocation, lookup,
registries, persistence, migration, runtime, or orchestration.
