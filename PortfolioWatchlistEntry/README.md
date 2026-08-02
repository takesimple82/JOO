# Explicit Portfolio Watchlist Entry

## Responsibilities

This package owns one explicit caller-supplied declaration that one accepted
Portfolio Membership is a watchlist entry.

`ExplicitPortfolioWatchlistEntry` is a frozen, hashable dataclass containing
exactly:

1. `membership: ExplicitPortfolioMembership`

The exact caller-supplied Membership object is retained. The entry creates no
second identity namespace and has no independent watchlist-entry identity.

## Invariants

- Structural identity consists only of the accepted Portfolio Membership.
- The membership is the exact caller-supplied object.
- Equality is structural over the exact stored membership.
- Duplicate or shared memberships are not interpreted by this single-entry
  contract.

## Validation order

`validate_explicit_portfolio_watchlist_entry()` requires, in order:

1. the exact `ExplicitPortfolioWatchlistEntry` model type;
2. the exact `ExplicitPortfolioMembership` field type; and
3. successful validation of that Membership exactly once.

Upstream exceptions propagate unchanged. Validation returns `None` on success
and does not normalize, convert, copy, or reconstruct the entry or membership.

## Non-responsibilities

This package does not own Portfolio, Portfolio Subject, or Membership
production, endpoint existence, semantic truth, watchlist collections,
snapshots, duplicate detection, uniqueness, positions, holding state,
quantities, observation contexts, prices, cost basis, currency, valuation,
P&L, priority, ranking, rationale, status, lifecycle, effective dates,
research planning, task generation, cash, capital buckets, risk budgets,
target weights, recommendations, allocation, constraints, execution, ticker
lookup, entity resolution, registries, persistence, migration, CLI, runtime,
orchestration, or automation.
