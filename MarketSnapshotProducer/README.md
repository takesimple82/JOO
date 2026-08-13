# MarketSnapshotProducer

## Package identity

`MarketSnapshotProducer` is the frozen PF-M4 Market Snapshot operational
production package name. Creating this tree is the first implementation of
that frozen ops package, not a sibling product and not a Market\* package.

This slice is **first-slice operational production only**. It retrieves
caller-named stored `market_fact` records read-only from FactStore, composes
them under exactly one caller-supplied session profile via explicit
bindings, applies fail-closed presence and freshness policy, constructs
exact accepted Market\* instances, invokes accepted Market\* validators in
declared order, and emits `ExplicitMarketSnapshotProductionResult`.

Rejected sibling names remain forbidden: `QuoteComposer`, `PriceProducer`,
`FlowProducer`, `SessionComposer`, `MarketValuator`, `TickerResolver`.

Architecture sources:

- `docs/provider/PF_M4_MARKET_SNAPSHOT_ARCHITECTURE.md`
- `docs/market/MARKET_FIRST_SLICE_DOMAIN_ARCHITECTURE.md`
- `docs/provider/FACT_STORE_MARKET_FACT_ELIGIBILITY_RETRIEVAL_ARCHITECTURE.md`
- `docs/provider/PF_M2_FACT_STORE_ARCHITECTURE.md`

## This slice

The sole fact upstream is frozen FactStore read-only retrieval. Every bound
subject names an explicit `fact_id`. Envelope types are not a second fact
path. Gateway adapters, collect, and market HTTP are not used.

Composition content is first-slice only: market / venue identity, instrument
identity, one session context, last price, market status, and source
provenance. Korea-capable and US-capable profiles are two caller-supplied
instances of the same `ExplicitMarketSessionProfile` type. Two `produce()`
attempts; never one merged snapshot.

`market_snapshot_id` and `session_context_id` are caller-supplied opaque
nonblank strings. They are never hashed, derived, or generated.

## Public layout

```text
MarketSnapshotProducer/
  README.md
  models/
  validation/
  retrieval/
  composition/
  policy/
  production.py
  tests/
```

Callers import from `MarketSnapshotProducer.models`,
`MarketSnapshotProducer.validation`, and
`MarketSnapshotProducer.production`. There is no package-root re-export
module.

## Public surface

| Surface | Location |
| --- | --- |
| Closed vocabularies | `MarketSnapshotProducer.models` |
| Request, profile, binding, criteria, policy, result, failure | `MarketSnapshotProducer.models` |
| Producer-boundary structural validators | `MarketSnapshotProducer.validation` |
| `MarketSnapshotProducer.produce` | `MarketSnapshotProducer.production` |

```text
MarketSnapshotProducer
  __init__(fact_store, utc_clock)
  produce(request: ExplicitMarketSnapshotProductionRequest)
      -> ExplicitMarketSnapshotProductionResult
```

`fact_store` must be the exact `FactStore` type. `utc_clock` is a required
callable `() -> datetime` used only when `freshness_max_age` is not `None`.
The clock never writes `collected_at`, `market_snapshot_id`, or
`session_context_id`.

## Validation-first production

Producer-boundary validators run first. After construction, accepted
Market\* validators run in declared order. Upstream exception objects
propagate unchanged. Success returns `None` from validators and a
`result_kind="success"` production result from `produce`.

Missing named facts, stale required facts, ineligible facts, criteria
mismatches, and projection failures fail closed unless
`allow_partial_emission` is `True`, in which case that subject is omitted
and never filled. If every named subject is omitted, the result is
`EMPTY_REQUIRED_EMISSION`. Empty bindings may emit a domain-valid empty
snapshot.

## Non-responsibilities

This slice does **not** own or implement:

- Market\* structure ownership, model redefinition, or validator redesign
- ProviderGateway modification, collect, adapters, auth, ingress, health,
  signaling, or market HTTP
- FactStore append, supersession, mutation, or a second fact path via
  never-stored envelopes
- ticker / entity / alias / open-world resolution
- exclusive commercial market-data vendor freeze
- hard-coded KRX-only or NYSE/Nasdaq-only producer
- Korea vs US package split
- session-profile catalog product, holiday calendar, or timezone database
- OHLC / bid-ask / volume / turnover / richer quotes / index / native FX
  observations
- FX conversion
- valuation / PnL / NAV
- Market Watch (PF-M5)
- IRO / Evidence / Memory / Contradiction / EV / CIO ownership
- broker orders, trading, or real capital actions
- auto-generated `market_snapshot_id`
- silent stale carry-forward / synthetic prices / research AI price
- sibling composer packages
- rewrite of the committed PF-M4 architecture document
- Automation runtime dependency

MarketSnapshotProducer composes accepted Market\* snapshots from stored
facts. It does not own Market\* structure, call Gateway, append to
FactStore, watch markets, or trade.
