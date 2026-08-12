# Explicit Market Instrument Endpoint

This package owns the minimum canonical Market Instrument endpoint contract.

`ExplicitMarketInstrument` is a frozen, hashable structural model containing
exactly:

1. `instrument_id: str`

The identity is an opaque, caller-supplied identifier that is canonical only
within the Market Instrument namespace. It does not encode a ticker, exchange
code, ISIN, CUSIP, display name, currency, asset class, version, state, or
lifecycle, and it is never generated or inferred automatically.

`validate_explicit_market_instrument()` requires the exact model type followed
by an exact nonblank built-in `str` identity. It returns `None` on success.
The validator does not trim, normalize, case fold, convert, copy, or
reconstruct the model or identity. Surrounding whitespace on an otherwise
nonblank identity is accepted and preserved.

Instrument identity is distinct from market identity, venue identity, session
context identity, snapshot identity, and portfolio subject identity.

## Non-responsibilities

This package does not own markets, venues, session contexts, observations,
snapshots, ticker symbols, exchange codes, ISIN/CUSIP parsing, display names,
currency, asset class, index membership, entity links, ticker or entity
resolution, Provider Gateway, Fact Store, MarketSnapshotProducer, Market Watch,
portfolio valuation, trading, registries, persistence, migration, lifecycle,
runtime, or orchestration.
