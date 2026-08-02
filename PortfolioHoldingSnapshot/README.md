# Explicit Portfolio Holding Snapshot

## Responsibility

This package owns one explicit immutable holding-state collection for one
accepted Portfolio Observation Context.

## Model

`ExplicitPortfolioHoldingSnapshot` is a frozen, hashable dataclass containing
exactly:

1. `observation_context: ExplicitPortfolioObservationContext`
2. `holding_observations: tuple[ExplicitPortfolioHoldingObservation, ...]`

The tuple may be empty. The exact caller-supplied context, tuple, observations,
positions, and quantities are retained in caller order.

## Validation

`validate_explicit_portfolio_holding_snapshot()` requires the exact snapshot
model, validates the root Observation Context once, requires an exact built-in
tuple, and validates every exact Holding Observation once in caller order.
Upstream exceptions propagate unchanged.

Each observation context must match the root context by exact stored
`observation_context_id` and `portfolio_id` values. The root and element
contexts may be distinct caller-supplied objects. Each
`position.position_id` may occur at most once. Validation returns `None` on
success and does not normalize, sort, convert, copy, or reconstruct any
supplied value.

## Invariants

- Structural identity consists only of the root Observation Context and the
  ordered tuple of Holding Observations.
- Empty and partial holding-state collections are valid.
- Caller order and every exact caller-supplied object are preserved.
- Every element context aligns with the root context by exact stored
  `observation_context_id` and `portfolio_id` values; alignment does not
  require Python object identity.
- Position identifiers are unique within the collection by exact stored value.
- Quantity remains owned by each Holding Observation and its exact `Decimal`
  representation is preserved.

## Non-responsibilities

This package does not own snapshot identity, Position, Observation Context, or
Holding Observation production, completeness, normalization, sorting, prices,
cost basis, currency, valuation, P&L, quantity units, cash, capital buckets,
risk budgets, target weights, watchlists, complete Portfolio snapshots,
allocation, CLI, automation, runtime, persistence, registries, lookup,
lifecycle, migration, or orchestration.
