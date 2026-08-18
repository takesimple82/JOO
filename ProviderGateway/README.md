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

## KB OpenAPI live factual transport

`KbOpenApiLiveBrokerTransport` occupies the existing `BrokerTransport`
port in `adapters/kb_openapi_live_broker_transport.py`.

- First live fact is **SSQM2952** (`POST /api/v1/ssqm2952`) for
  `request_kind="holdings"` only.
- HTTP and clock are injected. Tests must use a fake HTTP seam. This
  package does not ship a live network client.
- Runtime credential JSON uses exact keys only, for example
  `{"appKey":"<runtime>","appSecret":"<runtime>"}`. Tests use fake
  placeholders only.
- A successful read returns the parsed SSQM2952 object unchanged as raw
  `broker_fact` evidence. It is **not** PF-M3-ready.
- Transport does not own FactStore. A rightful caller may later append
  the existing Gateway success envelope.
- Real credentials and live KB Open API require a separately authorized
  controlled pilot. This README does not authorize them.
- No orders.

## KB OpenAPI runtime credential configuration

This additive runtime composition occupies the existing
`CredentialSupplier` port and the existing live-transport constructor
arguments. It does **not** change the ProviderGateway public collect
API, `CredentialSupplier`, `resolve_outbound_credential`,
`decode_kb_openapi_client_material`, `KbOpenApiAdapter`,
`BrokerTransport`, or the Gateway envelope.

It is **not** a general secrets platform, CLI framework, IP discovery
service, scheduler, FactStore, Snapshot, market, overseas, or order
path.

### Keychain item identity

Production secrets persist only as two macOS login-keychain generic
password items:

```text
service:   joo.provider.kb_open_api
accounts:  appKey
           appSecret
```

The production backend uses Security.framework via stdlib `ctypes`
(`SecItemAdd`, `SecItemUpdate`, `SecItemCopyMatching`,
`SecItemDelete`). Tests inject an in-memory fake and must never
construct the production backend or mutate the real Keychain.

Runtime retrieves both items and reconstructs the existing compact
credential JSON `{"appKey":"...","appSecret":"..."}`. The default
composition `credential_ref` is `kb_open_api`. Missing, denied, or
malformed Keychain material becomes existing `AUTH_FAILURE` with
`detail=None`. Access tokens are never written to Keychain.

### Host file identity

Non-secret host identity lives only at:

```text
~/.joo/kb_openapi_host_identity.json
```

Allowed keys are `ip_addr` (required) and optional `mac_addr`. The file
contains no secret. Tests must inject a temporary path and must not
create `~/.joo`.

`ip_addr` is the configured non-secret value sent as `dataHeader.ipAddr`.
There is no external public-IP lookup, no local-interface inference, and
no automatic replacement. A stale configured value remains until
operator reconfiguration or an existing live KB failure.

`mac_addr` is an optional override. When absent, runtime derives the
current locally assigned MAC of the active primary Wi-Fi interface
(SystemConfiguration IEEE80211 BSD-name discovery plus `getifaddrs`
AF_LINK). That is not `networksetup` Wi-Fi ID, not AP/BSSID, and not an
Ethernet / Bluetooth / Thunderbolt fallback.

### One-time configure semantics

Narrow argv dispatch only, via
`python -m ProviderGateway.auth.kb_openapi_runtime`:

```text
configure kb
configure kb --replace
configure kb --delete
configure kb --host
configure kb --host --reset
configure kb --replace --host
```

Anything else is a visible failure and does not mutate Keychain or the
host file. This is not a general CLI framework.

First-time `configure kb` refuses if either Keychain item already
exists, collects hidden `appKey` / `appSecret`, pair-writes and
verifies both, then writes the host file. Pair-write failure does not
write the host file. Keychain success plus later host-file failure
leaves Keychain unchanged; recover with `--host`.

`--replace` replaces the Keychain pair only. `--delete` deletes the
pair and leaves the host file. `--host` updates host identity only.

### Normal run

After one-time configure, `compose_kb_openapi_live_runtime(...)` plus
existing `collect()` requires zero secret, IP, or MAC input. Host or
MAC composition failure is existing `VALIDATION_FAILURE` with
`detail=None` before transport construction.

Tests use fake Keychain, fake MAC hooks, a temporary host file, and
fake `http_post`. They do not call live KB, do not use real
credentials, and do not mutate the real Keychain.
