# ProviderGateway

## Package identity

`ProviderGateway` is the frozen PF-M1 Provider & Fact ingress package name.
This tree is **package-identity reuse**, not a new product package.

This package delivers the frozen **additive market-adapter path** and the
additive KB Open API broker-adapter path occupying reserved
`adapters/kb_open_api.py`.

The market path remains the Prerequisite A / S4 `MarketApiAdapter` path. It
does **not** deliver broker collect or `broker_fact` production.

Rejected sibling names remain forbidden: `MarketAdapter`, `MarketGateway`,
`QuoteIngress`, `MarketFactStore`, `BrokerAdapter`, `BrokerGateway`,
`KbGateway`, `BrokerFactStore`.

## This slice

The Market API Adapter attaches to the single PF-M1 Provider Interface and
maps one read-oriented market-provider attempt into one immutable envelope or
one first-class failure signal.

- Success-path fact envelopes use `source_class = "market_fact"` exactly.
- `source_class` is explicit at construction and is never inferred.
- `provider_id` is Gateway-owned and must not be
  `RESERVED_KB_OPEN_API_PROVIDER_ID` (`"kb_open_api"`).
- `collected_at` is assigned at Gateway acceptance from an injected UTC clock.
- Korea-capable and US-capable bindings are two parameter profiles of the
  same `MarketApiAdapter` class. They are not product forks and not
  `if-Korea-else-US` collect logic.

The KB Open API Adapter occupies `adapters/kb_open_api.py` and attaches to
the same Provider Interface. It maps one read-oriented broker collect
attempt (`holdings`, `balances`, or `account_state`) into one immutable
envelope or one first-class failure signal.

- Success-path fact envelopes use `source_class = "broker_fact"` exactly.
- `provider_id` is exactly `RESERVED_KB_OPEN_API_PROVIDER_ID`
  (`"kb_open_api"`).
- `collected_at` is assigned at Gateway acceptance from an injected UTC clock.
- One collect attempt, one `request_kind`, one envelope.

Architecture sources:

- `docs/provider/PROVIDER_GATEWAY_MARKET_ADAPTER_PATH_ARCHITECTURE.md`
- `docs/provider/PF_M1_PROVIDER_GATEWAY_ARCHITECTURE.md`
- `docs/provider/PF_M1_KB_OPENAPI_BROKER_FIRST_SLICE_ADDITIVE_ARCHITECTURE.md`

## Public layout

```text
ProviderGateway/
  README.md
  models/
  validation/
  provider_interface.py
  adapters/
    market_api.py
    kb_open_api.py
  auth/
  health.py
  signaling.py
  ingress.py
  tests/
```

`adapters/kb_open_api.py` is occupied by `KbOpenApiAdapter`.

## Public surface

| Surface | Location |
| --- | --- |
| Closed vocabularies and reserved KB id | `ProviderGateway.models` |
| Envelope, diagnostics, health, failure, profile, binding, collect types | `ProviderGateway.models` |
| Broker profile, binding, collect types | `ProviderGateway.models` |
| Structural validators | `ProviderGateway.validation` |
| `ProviderInterface` | `ProviderGateway.provider_interface` |
| `MarketApiAdapter` | `ProviderGateway.adapters.market_api` |
| `KbOpenApiAdapter` | `ProviderGateway.adapters.kb_open_api` |
| `collect(...)` / `health()` | Provider Interface methods on `MarketApiAdapter` and `KbOpenApiAdapter` |
| `RESERVED_KB_OPEN_API_PROVIDER_ID` | `"kb_open_api"` |

Callers import those modules. There is no package-root re-export module.

## Provider Interface

```text
ProviderInterface
  provider_id -> str
  declared_source_class -> str
  collect(request: ExplicitCollectRequest | ExplicitBrokerCollectRequest) -> ExplicitCollectOutcome
  health() -> ExplicitProviderHealthSnapshot
```

`MarketApiAdapter.declared_source_class` is exactly `"market_fact"`.
`MarketApiAdapter.collect` accepts exact `ExplicitCollectRequest` only.

`KbOpenApiAdapter.declared_source_class` is exactly `"broker_fact"`.
`KbOpenApiAdapter.collect` accepts exact `ExplicitBrokerCollectRequest` only.

Constructor ports (injected; no exclusive vendor HTTP client):

- transport: one read attempt returns a structured wire body or a structured
  transport/auth/provider failure
- credential supplier: resolves `credential_ref` to a secret for outbound use
  only
- UTC clock: returns `datetime` whose `tzinfo is datetime.timezone.utc`

## Validation

Validators are type / nonblank / membership / required-presence only.
They return `None` on success. First failure wins. Upstream exception
objects propagate unchanged. Surrounding whitespace on otherwise nonblank
strings is accepted and preserved. Validators do not trim, sort, convert,
copy, or reconstruct.

`validate_explicit_provider_payload_envelope` accepts any frozen source
class, including `broker_fact`, so the PF-M1 field model is not redesigned.
`validate_market_fact_success_envelope` is the market-path extra rule.
`validate_broker_fact_success_envelope` is the broker-path extra rule.

## Non-responsibilities

This slice does **not** own or implement:

- FactStore append, eligibility, persistence, or retrieval (Prerequisite B)
- Market\* construction or validation (`ExplicitMarket`,
  `ExplicitMarketVenue`, `ExplicitMarketInstrument`,
  `ExplicitMarketSessionContext`, `ExplicitMarketFactProvenanceReference`,
  `ExplicitMarketInstrumentObservation`, `ExplicitMarketSnapshot`)
- Market Snapshot composition or Portfolio Snapshot
- `MarketSnapshotProducer` / PF-M4 production
- Market Watch
- ticker / entity / alias resolution
- exclusive commercial market-data vendor freeze
- hard-coded KRX-only or NYSE/Nasdaq-only client
- `research_ai` production
- news / alternative-data ingest
- broker orders, trading, or real capital actions
- read-only orders / fills as `request_kind`
- additional broker adapters beyond KB Open API
- vendor SDK / URL map / live network client
- FactStore append
- PF-M3 production
- PF-M5
- trading writes
- secrets vault / token persistence
- OHLC / bid / ask / volume / FX / flow productization
- EvidenceProvenance `primary | secondary | unknown` taxonomy
- secret storage, vaults, or credential invention
- auto-generated `envelope_id`
- float valuation math or invented prices / statuses
- IRO run coordination
- Automation runtime dependency

Gateway emits a handoff candidate only. It does not append and does not
call FactStore.
