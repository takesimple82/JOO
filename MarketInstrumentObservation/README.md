# Market Instrument Observation

This package owns one instrument observation under one session context for the
Market first-slice domain structure.

`ExplicitMarketInstrumentObservation` is a frozen, hashable dataclass
containing exactly:

1. `instrument: ExplicitMarketInstrument`
2. `session_context: ExplicitMarketSessionContext`
3. `last_price: Decimal`
4. `market_status: str`
5. `provenance: ExplicitMarketFactProvenanceReference`

`MARKET_STATUS_VALUES` is the closed vocabulary:

- `pre_open`
- `open`
- `post_close`
- `closed`
- `halted`
- `unknown`

`last_price` is exact built-in `decimal.Decimal` only and must be finite.
Float and Decimal subclasses are rejected. Structural validity of a price is
not economic reasonableness review; sign is not constrained beyond finiteness.

`validate_explicit_market_instrument_observation()` validates in declared
order: exact observation type; exact instrument type and instrument validator
once; exact session context type and session context validator once; exact
finite `Decimal` last price; exact `str` market status membership in
`MARKET_STATUS_VALUES` without case folding; exact provenance type and
provenance validator once. Upstream exceptions propagate unchanged. Success
returns `None`. No normalize, sort, convert, copy, reconstruct, infer, or
lookup is performed.

## Non-responsibilities

This package does not own OHLC, bid, ask, volume, turnover, size, trade count,
VWAP, currency amount objects, FX rates, index levels, flow fields, wall-clock
observation identity, Provider Gateway, Fact Store I/O, MarketSnapshotProducer,
Market Watch materiality, portfolio valuation, PnL, NAV, trading, ticker or
entity resolution, registries, persistence, migration, runtime, or
orchestration.
