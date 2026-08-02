# Explicit Portfolio Snapshot

## Responsibility

This package owns one explicit immutable Portfolio-state composition under one
accepted Portfolio Observation Context. It composes one accepted Portfolio
Holding Snapshot and an ordered tuple of accepted Portfolio Watchlist Entries.

## Model

`ExplicitPortfolioSnapshot` is a frozen, hashable dataclass containing exactly:

1. `portfolio_snapshot_id: str`
2. `observation_context: ExplicitPortfolioObservationContext`
3. `holding_snapshot: ExplicitPortfolioHoldingSnapshot`
4. `watchlist_entries: tuple[ExplicitPortfolioWatchlistEntry, ...]`

`portfolio_snapshot_id` is an opaque caller-supplied identity canonical only
within the Portfolio Snapshot namespace. It does not encode time, version,
state, source, or lifecycle. Empty holding and watchlist collections are valid,
and partial Portfolio snapshots are allowed.

## Validation

`validate_explicit_portfolio_snapshot()` validates in this exact order:

1. require the exact `ExplicitPortfolioSnapshot` model type;
2. require `portfolio_snapshot_id` to be an exact nonblank built-in `str`;
3. require the exact `ExplicitPortfolioObservationContext` root type;
4. validate the root Observation Context once;
5. require the exact `ExplicitPortfolioHoldingSnapshot` type;
6. validate the Holding Snapshot once;
7. align its context with the root by exact stored `observation_context_id`,
   then exact stored `portfolio_id`;
8. require `watchlist_entries` to be an exact built-in tuple; and
9. for each entry in caller order, require the exact
   `ExplicitPortfolioWatchlistEntry` type, validate it once, require its
   membership `portfolio_id` to align with the root, then reject a duplicate
   membership by exact stored `portfolio_id` and `portfolio_subject_id`.

Upstream exceptions propagate unchanged. Validation returns `None` on success
and does not trim, normalize, sort, convert, copy, or reconstruct any supplied
object or value.

## Invariants

- Structural identity consists only of the snapshot identity, root context,
  Holding Snapshot, and ordered watchlist tuple.
- Caller order and every exact caller-supplied object are preserved.
- Context and Portfolio alignment use exact stored values, not object identity.
- Empty collections and partial Portfolio state are valid.
- Duplicate Watchlist Entry memberships are rejected within one snapshot.
- Structural validity does not establish real-world completeness or temporal,
  economic, or market truth.

## Non-responsibilities

This package does not own production of Portfolio, Portfolio Subject,
Membership, Position, Observation Context, Holding Observation, Holding
Snapshot, or Watchlist Entry objects; cash balances; prices; cost basis;
currency; valuation; P&L; quantity units; capital buckets; risk budgets; target
weights; concentration metrics; recommendations; allocation proposals;
constraint evaluation; CIO decisions; research planning; task generation;
priority ranking; Impact or Expected Value applicability or semantic
production; completeness guarantees; market synchronization; ticker lookup;
entity resolution; registries; persistence; migration; CLI; runtime;
orchestration; automation; approval; or audit.
