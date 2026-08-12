# Market Session Context

This package owns one explicit caller-supplied session context in which market
state may be observed under one parameterized session profile.

`ExplicitMarketSessionContext` is a frozen, hashable dataclass with:

1. `session_context_id: str`
2. `market_id: str`
3. `venue_id: str`
4. `session_profile_id: str`
5. `timezone_id: str`
6. `calendar_id: str`

The context identity is opaque and canonical only within the Market Session
Context namespace. `market_id` and `venue_id` are foreign opaque references
stored as plain strings. Domain structure does not embed MarketEndpoint or
MarketVenue objects and does not call endpoint validators.

Session parameterization supports Korea and US (and other) profiles through
distinct caller-supplied profile, timezone, calendar, venue, and market
identities. This package does not hard-code KRX, NYSE, Nasdaq, a single
timezone, or a single trading calendar.

`validate_explicit_market_session_context()` requires the exact context model,
then validates each of the six fields in declaration order as exact nonblank
built-in strings. It returns `None` on success and preserves the supplied
identifiers without trimming, normalization, conversion, copying, or
reconstruction.

The context is timeless structural binding: it does not claim an observation
occurred now, does not own runtime clocks, and does not require a snapshot
wall-clock timestamp field.

## Non-responsibilities

This package does not own endpoint existence checks for markets or venues,
session profile catalogs, holiday calendar products, timezone databases,
observations, prices, market status, snapshots, Provider Gateway, Fact Store,
MarketSnapshotProducer, Market Watch, portfolio valuation, trading, registries,
persistence, migration, runtime clocks, or orchestration.
