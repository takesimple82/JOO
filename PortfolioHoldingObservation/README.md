# Explicit Portfolio Holding Observation

This package owns one explicit caller-supplied quantity observation for one
accepted Portfolio Position in one accepted Portfolio Observation Context.

`ExplicitPortfolioHoldingObservation` is a frozen, hashable dataclass
containing:

1. `position: ExplicitPortfolioPosition`
2. `observation_context: ExplicitPortfolioObservationContext`
3. `quantity: Decimal`

The exact supplied Position and Observation Context objects are retained.
`quantity` is an exact finite built-in `decimal.Decimal`; its exponent,
trailing zeros, and signed-zero representation are preserved.

`validate_explicit_portfolio_holding_observation()` requires the exact
observation model, validates the exact Position and Observation Context once
each in field order, requires
`position.membership.portfolio_id == observation_context.portfolio_id`, then
validates the quantity. Upstream exceptions propagate unchanged. Validation
returns `None` on success and does not convert, copy, normalize, or reconstruct
any supplied object.

Structural validity requires the Position membership and Observation Context
to name the same Portfolio using exact stored identifier equality. It does not
interpret positive, zero, or negative quantity as long, closed, or short
state.

## Non-responsibilities

This package does not own Position or Observation Context production,
observation identity, timestamps, quantity units, prices, cost basis, currency,
valuation, P&L, complete holding or Portfolio snapshots, collections,
watchlists, allocation, recommendations, lifecycle, lookup, registries,
persistence, migration, runtime, or orchestration.
