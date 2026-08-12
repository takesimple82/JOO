# Explicit Market Venue Endpoint

This package owns the minimum canonical Market Venue endpoint contract.

`ExplicitMarketVenue` is a frozen, hashable structural model containing exactly:

1. `venue_id: str`

The identity is an opaque, caller-supplied identifier that is canonical only
within the Market Venue namespace. It does not encode a market, exchange MIC,
timezone, calendar, version, state, or lifecycle, and it is never generated or
inferred automatically.

`validate_explicit_market_venue()` requires the exact model type followed by an
exact nonblank built-in `str` identity. It returns `None` on success. The
validator does not trim, normalize, case fold, convert, copy, or reconstruct
the model or identity. Surrounding whitespace on an otherwise nonblank
identity is accepted and preserved.

Venue identity is distinct from market identity, instrument identity, session
context identity, and snapshot identity. Domain structure does not equate, map,
or resolve market and venue identities.

## Non-responsibilities

This package does not own markets, instruments, session contexts, observations,
snapshots, exchange calendars, timezone databases, ticker or entity resolution,
Provider Gateway, Fact Store, MarketSnapshotProducer, Market Watch, portfolio
valuation, trading, registries, persistence, migration, lifecycle, runtime, or
orchestration.
