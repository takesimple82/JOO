# PortfolioSnapshotProducer

## Package identity

`PortfolioSnapshotProducer` is the frozen PF-M3 Portfolio Snapshot operational
production package name. Creating this tree is the first implementation of
that frozen ops package, not a sibling product and not a Portfolio\* package.

This slice is **first-slice operational production only**. It retrieves
caller-named stored `broker_fact` records read-only from FactStore, composes
holdings via explicit bindings plus caller-declared watchlist memberships,
applies fail-closed eligibility / criteria / freshness policy, constructs
exact accepted Portfolio\* instances, invokes accepted Portfolio\* validators
in declared order, and emits `ExplicitPortfolioSnapshotProductionResult`.

Rejected sibling names remain forbidden: `PortfolioComposer`,
`HoldingsComposer`, `PortfolioValuator`, `PortfolioFactStore`,
`CashSnapshotProducer`, `WatchlistProducer`, `PositionResolver`,
`WatchlistStore`, `WatchlistComposer`, `SnapshotFactory`.

Architecture sources:

- `docs/provider/PF_M3_PORTFOLIO_SNAPSHOT_ARCHITECTURE.md`
- `docs/provider/PF_M2_FACT_STORE_ARCHITECTURE.md`
- `docs/provider/FACT_STORE_MARKET_FACT_ELIGIBILITY_RETRIEVAL_ARCHITECTURE.md`
- accepted Portfolio\* domain packages (structure ownership remains there)

## This slice

The sole fact upstream is frozen FactStore read-only retrieval. Every holding
binding names an explicit `fact_id`. Envelope types are not a second fact
path. Gateway adapters, collect, KB Open API, and HTTP are not used.

Composition content is first-slice only: one observation context, holdings
composition from named stored facts, and caller-declared watchlist
membership. Empty holdings bindings and empty watchlist declarations are
valid partial state. Cash, balances, `account_state`, valuation, and snapshot
timestamps are not composition content.

`portfolio_snapshot_id`, `observation_context_id`, `portfolio_id`,
`position_id`, and `portfolio_subject_id` are caller-supplied opaque
nonblank strings. They are never hashed, derived, or generated.

## Public layout

```text
PortfolioSnapshotProducer/
  README.md
  models/
  validation/
  retrieval/
  composition/
  policy/
  production.py
  tests/
```

Callers import from `PortfolioSnapshotProducer.models`,
`PortfolioSnapshotProducer.validation`, and
`PortfolioSnapshotProducer.production`. There is no package-root re-export
module.

## Public surface

| Surface | Location |
| --- | --- |
| Closed vocabularies | `PortfolioSnapshotProducer.models` |
| Request, binding, declaration, criteria, policy, provenance, failure, result | `PortfolioSnapshotProducer.models` |
| Producer-boundary structural validators | `PortfolioSnapshotProducer.validation` |
| `PortfolioSnapshotProducer.produce` | `PortfolioSnapshotProducer.production` |

```text
PortfolioSnapshotProducer
  __init__(fact_store, utc_clock)
  produce(request: ExplicitPortfolioSnapshotProductionRequest)
      -> ExplicitPortfolioSnapshotProductionResult
```

`fact_store` must be the exact `FactStore` type. `utc_clock` is a required
callable `() -> datetime` used only when `freshness_max_age` is not `None`.
The clock never writes `collected_at`, `portfolio_snapshot_id`,
`observation_context_id`, or any domain field.

## Validation-first production

Producer-boundary validators run first. After construction, accepted
Portfolio\* validators run in declared order. Upstream exception objects
propagate unchanged. Success returns `None` from validators and a
`result_kind="success"` production result from `produce`.

Missing named facts, stale required facts, ineligible facts, criteria
mismatches, and projection failures fail closed with no snapshot. There is
no authorized partial-omission path. Empty bindings may emit a domain-valid
empty holding snapshot and/or empty watchlist.

## Non-responsibilities

This slice does **not** own or implement:

- Portfolio\* structure ownership, model redefinition, or validator redesign
- ProviderGateway modification, collect, adapters, auth, ingress, health,
  signaling, KB Open API, or HTTP
- FactStore append, supersession, mutation, new retrieval API, or a second
  fact path via never-stored envelopes
- `request_kind` inference or payload-shape classification of holdings vs
  balances vs `account_state`
- intra-payload batched holdings selectors
- cash / balances / `account_state` snapshot fields
- valuation / marks / NAV / PnL / FX
- Market Snapshot nesting / MarketSnapshotProducer ownership
- snapshot timestamps
- automatic identity generation
- WatchlistStore / WatchlistProducer
- sibling composer packages
- IRO ownership
- Human Approval
- broker orders, trading, or real capital actions
- PF-M5 / Market Watch
- rewrite of the committed PF-M3 architecture document
- Automation runtime dependency

PortfolioSnapshotProducer composes accepted Portfolio\* snapshots from stored
facts. It does not own Portfolio\* structure, call Gateway, append to
FactStore, value portfolios, watch markets, or trade.
