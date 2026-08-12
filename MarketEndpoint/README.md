# Explicit Market Endpoint

This package owns the minimum canonical Market endpoint contract.

`ExplicitMarket` is a frozen, hashable structural model containing exactly:

1. `market_id: str`

The identity is an opaque, caller-supplied identifier that is canonical only
within the Market namespace. It does not encode a venue, exchange, timezone,
calendar, version, state, or lifecycle, and it is never generated or inferred
automatically.

`validate_explicit_market()` requires the exact model type followed by an
exact nonblank built-in `str` identity. It returns `None` on success. The
validator does not trim, normalize, case fold, convert, copy, or reconstruct
the model or identity. Surrounding whitespace on an otherwise nonblank
identity is accepted and preserved.

Market identity is distinct from venue identity, instrument identity, session
context identity, snapshot identity, and Fact Store fact identity.

## Non-responsibilities

This package does not own venues, instruments, session contexts, observations,
snapshots, market status, prices, OHLC, bid/ask, volume, FX, sector, futures,
options, flows, ticker or entity resolution, Provider Gateway, Fact Store,
MarketSnapshotProducer, Market Watch, portfolio valuation, trading, registries,
persistence, migration, lifecycle, runtime, or orchestration.

Downstream venue, instrument, session, observation, and snapshot contracts are
intentionally not present.
