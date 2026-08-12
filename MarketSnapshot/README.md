# Explicit Market Snapshot

## Responsibility

This package owns one explicit immutable market-state composition under one
accepted Market Session Context. It composes an ordered tuple of accepted
Market Instrument Observations for a single session context.

## Model

`ExplicitMarketSnapshot` is a frozen, hashable dataclass containing exactly:

1. `market_snapshot_id: str`
2. `session_context: ExplicitMarketSessionContext`
3. `instrument_observations: tuple[ExplicitMarketInstrumentObservation, ...]`

`market_snapshot_id` is an opaque caller-supplied identity canonical only
within the Market Snapshot namespace. It does not encode time, version, state,
source, or lifecycle. Empty instrument observation collections are valid, and
partial market snapshots are allowed. Completeness is not domain-owned.

## Validation

`validate_explicit_market_snapshot()` validates in this exact order:

1. require the exact `ExplicitMarketSnapshot` model type;
2. require `market_snapshot_id` to be an exact nonblank built-in `str`;
3. require the exact `ExplicitMarketSessionContext` root type;
4. validate the root session context once;
5. require `instrument_observations` to be an exact built-in tuple; and
6. for each observation in caller order, require the exact
   `ExplicitMarketInstrumentObservation` type, validate it once, align its
   session context to the root by exact stored equality of all six session
   fields (`session_context_id`, `market_id`, `venue_id`,
   `session_profile_id`, `timezone_id`, `calendar_id`; object identity of
   nested contexts is not required), then reject a duplicate
   `instrument.instrument_id` by exact stored string.

Upstream exceptions propagate unchanged. Validation returns `None` on success
and does not trim, normalize, sort, convert, copy, or reconstruct any supplied
object or value.

## Invariants

- Structural identity consists only of the snapshot identity, root session
  context, and ordered instrument observation tuple.
- Caller order and every exact caller-supplied object are preserved.
- Session alignment uses exact stored field values, not object identity.
- Empty collections and partial market state are valid.
- Duplicate instrument identities are rejected within one snapshot.
- Structural validity does not establish market truth, quote completeness, or
  Market Watch materiality.

## Non-responsibilities

This package does not own production of Market, Venue, Instrument, Session
Context, Observation, or Provenance objects; Provider Gateway; Fact Store;
MarketSnapshotProducer runtime or fail-closed production policy; Market Watch;
OHLC; bid/ask; volume; turnover; FX; sector; futures; options; flows; index
identity; portfolio valuation; PnL; NAV; research; trading; ticker or entity
resolution; registries; persistence; migration; CLI; runtime; orchestration;
automation; approval; or audit.
