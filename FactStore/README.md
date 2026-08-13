# FactStore

## Package identity

`FactStore` is the frozen PF-M2 Provider & Fact store package name.
Creating this tree is **package-identity reuse**, not a new product package.

This slice is the **first FactStore implementation** and the Prerequisite B
class expansion. It implements the frozen PF-M2 store model — including
`broker_fact` eligibility and retrieval — and adds `market_fact` beside it.

`broker_fact` remains eligible. `market_fact` is additive. This package does
**not** make `market_fact` the only permanently eligible class.

Rejected sibling names remain forbidden: `MarketFactStore`, `MarketAdapter`,
`MarketGateway`, `QuoteIngress`, `MarketSnapshotProducer`, `MarketHistory`,
`QuoteStore`.

Architecture sources:

- `docs/provider/PF_M2_FACT_STORE_ARCHITECTURE.md`
- `docs/provider/FACT_STORE_MARKET_FACT_ELIGIBILITY_RETRIEVAL_ARCHITECTURE.md`

## This slice

Eligible primary-fact append classes are exactly `broker_fact` and
`market_fact`. Eligibility is by frozen `source_class`, success status, and
structure. Korea-capable and US-capable market facts are the same class.

The sole success-path handoff object is the frozen PF-M1 envelope
`ProviderGateway.models.ExplicitProviderPayloadEnvelope`. `fact_id` is
caller/handoff-supplied. `collected_at` is preserved from the envelope.
`appended_at` is store-owned UTC of durable accept.

History is append-only with explicit `superseded_fact_id` on the new record.
Same-class supersession only. Retrieval is read-only.

## Public layout

```text
FactStore/
  README.md
  models/
  validation/
  ports.py
  storage.py
  store.py
  tests/
```

Callers import from `FactStore.models`, `FactStore.validation`,
`FactStore.ports`, `FactStore.storage`, and `FactStore.store`. There is no
package-root re-export module.

## Public surface

| Surface | Location |
| --- | --- |
| Closed vocabularies and forbidden secret names | `FactStore.models` |
| `ExplicitFactAppendRequest`, `ExplicitStoredFactRecord` | `FactStore.models` |
| Structural validators | `FactStore.validation` |
| Injected UTC clock port | `FactStore.ports` |
| `InMemoryAppendOnlyFactEngine` | `FactStore.storage` |
| `FactStore` append / retrieval / integrity | `FactStore.store` |

```text
FactStore
  __init__(utc_clock, storage_engine=None)
  append(request) -> ExplicitStoredFactRecord
  get_by_fact_id(fact_id)
  list_by_source_identity(source_identity)
  list_by_source_class(source_class)
  list_by_collected_at_window(collected_at_start, collected_at_end)
  get_predecessor(fact_id)
  get_successor(fact_id)
  verify_integrity(fact_id)
```

## Eligibility

An input may append as a primary fact only if all hold:

1. It is an `ExplicitFactAppendRequest` whose envelope is the frozen Gateway
   type.
2. The generic envelope validator accepts it.
3. `status` is `"success"`.
4. `source_class` is exactly `"broker_fact"` or exactly `"market_fact"`.
5. Caller-supplied `fact_id` is present, opaque, and nonblank.
6. Payload is the envelope’s opaque `dict`, with no forbidden secret keys.
7. Source class is accepted as declared. No repair.
8. Store invariants hold (`fact_id` / `envelope_id` unused; supersession
   legal).

`research_ai` never appends. Failure / outage / health inputs never become
primary facts. Market\* objects and PF-M4 snapshots are not append inputs.

## Non-responsibilities

This slice does **not** own or implement:

- `MarketSnapshotProducer` / PF-M4 composition / snapshot composition
- ProviderGateway modification, collect, or market HTTP re-fetch
- Market\* construction or validation
- ticker / entity / alias resolution
- exclusive commercial market-data vendor freeze
- hard-coded KRX-only or NYSE/Nasdaq-only client
- `research_ai` production
- news / alternative-data ingest
- `execution_fact`
- broker orders, trading, or real capital actions
- OHLC / bid / ask / volume / FX / flow productization
- EvidenceProvenance `primary | secondary | unknown` taxonomy
- secret storage, vaults, or credential persistence
- auto-generated `fact_id`
- durable filesystem / schema-as-code / tenancy
- freshness / staleness policy
- Market Watch
- IRO / Evidence Store ownership
- float valuation math or invented prices / statuses
- Automation runtime dependency

FactStore stores eligible Gateway envelopes and retrieves stored records.
It does not compose snapshots, call Gateway, or own trading.
