# PF-M1 KB Open API Broker First Slice Additive Architecture

## Status and milestone

- Status: Architecture authored for independent review; additive
  ProviderGateway KB Open API broker-first first-slice freeze
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Provider & Fact** (Layer 2 — Provider Gateway)
- Milestone: **PF-M1 KB Open API Broker First Slice**
- Owner package identity (frozen PF-M1; not created by this document):
  `ProviderGateway`
- Additive capability: **KB Open API broker-adapter path** (slot reserved by
  PF-M1; occupied here as architecture, not as implementation)
- This document is **not** a greenfield ProviderGateway architecture and
  **not** a redesign of PF-M1 identity, the frozen market-adapter path,
  FactStore, MarketSnapshotProducer, or Market\*
- Repository boundary: architecture authoring only; this document alone
  authorizes no production code, test, package scaffold, schema module,
  configuration, run artifact, or Git history mutation

This document freezes **only** the additive ProviderGateway broker-adapter
path required to occupy the reserved KB Open API slot after the market-adapter
path already exists.

It does **not** redesign frozen PF-M1 envelope / source-class identity.

It does **not** create a new package.

It does **not** own FactStore append, eligibility, persistence, or retrieval.

It does **not** own Market\* models, validators, or structural invariants.

It does **not** authorize PF-M3 Portfolio Snapshot production.

It does **not** modify MarketSnapshotProducer or begin PF-M5.

Implementation requires a separate authorization after architecture review.

---

## Normative first-slice surface (must remain explicit)

### This freeze implements ONLY

| # | Responsibility |
| --- | --- |
| 1 | **KB Open API Adapter** occupation of the reserved broker-adapter slot |
| 2 | **Provider Interface attachment** of that adapter without a second ingress plane |
| 3 | **Broker-only request, binding, and transport types** distinct from market types |
| 4 | **Exact first-slice read surface**: holdings, balances, and account-state observations |
| 5 | **Wire → immutable provider payload envelope** mapping for those broker responses |
| 6 | **`source_class = broker_fact`** tagging on success-path fact envelopes |
| 7 | **`provider_id = "kb_open_api"`** on the broker path only |
| 8 | **Broker-path health / failure / outage signaling** without inventing facts |
| 9 | **Handoff surface** that a later rightful caller may append to FactStore |

### This freeze does NOT implement

| Concern | Owner (elsewhere) |
| --- | --- |
| **Fact Store** append / eligibility / retrieval | Frozen PF-M2 / `FactStore` — already accepts `broker_fact` |
| **Portfolio Snapshot** production | PF-M3 — not this slice |
| **Market API Adapter** behavior | Frozen market-adapter path — unchanged |
| **Market Snapshot** composition | Frozen PF-M4 `MarketSnapshotProducer` |
| **Market\*** structure / validators / invariants | Frozen Market\* packages |
| **Read-only orders / fills** | Later authorized broker-observation slice |
| **Trading writes / Broker Execution** | Layer 15 BX-M1 |
| **Human Approval** (capital) | Layer 14 Human Authority |
| **Research AI** transport runtime | Stage 1/2 + later explicit freeze |
| **News / alternative data** | Architecture amendment required first |
| **Ticker / entity resolution** | Outside permanently |

---

## 1. Repository checkpoint

Verified immediately before authoring. No authoring proceeds from an
unverified checkpoint.

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| Path | `/Users/takesimple/Projects/JOO` | `/Users/takesimple/Projects/JOO` | Match |
| Branch | `feature/stage2-provider-runtime` | `feature/stage2-provider-runtime` | Match |
| HEAD | `v7.8-stage5-pf-m4-implementation` | `5c54f80d5815487ef440d9b57c56c16503c66550` tagged exactly `v7.8-stage5-pf-m4-implementation` | Match |
| Exact tag at HEAD | `v7.8-stage5-pf-m4-implementation` | Exact match (`git describe --exact-match --tags HEAD`) | Match |
| Tracked tree | Clean | Clean (`git status --short` shows only expected untracked docs) | Match |
| Unexpected dirty tracked files | None | None | Match |
| Unexpected in-boundary untracked production files | None | None | Match |

**Preserved out-of-boundary untracked files (read-only; not modified, not
staged):**

- `docs/JOO_PRODUCT_ARCHITECTURE.md`
- `docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md`

**Production package state at this freeze**

| Package | Repository state at this freeze |
| --- | --- |
| `ProviderGateway` | **Present.** Market-adapter path accepted. `adapters/kb_open_api.py` **absent** and currently test-frozen as absent. |
| `FactStore` | **Present.** `broker_fact` and `market_fact` eligibility already accepted. |
| `MarketSnapshotProducer` | **Present and frozen** at HEAD tag `v7.8-stage5-pf-m4-implementation`. |
| Market\* domain packages | **Present and frozen.** This freeze must not import or construct them. |
| `PortfolioSnapshotProducer` | **Absent.** PF-M3 production remains deferred. |

Checkpoint status: **Pass**. Not REVIEW BLOCKED.

---

## 2. Human authority and sequencing

### 2.1 Human authority consumed

The human operator explicitly selected **PF-M1 KB Open API Broker First
Slice** as the next milestone after PF-M4 completion.

That selection consumes the post–PF-M4 sequencing stop. The independent
post–PF-M4 next-milestone review had left an **unranked** open set:

1. KB Open API Broker First Slice
2. PF-M3 Portfolio Snapshot production
3. IRO-M2 implementation

Human authority ranks item 1 next. It does **not**:

- authorize implementation;
- reopen PF-M4;
- start PF-M3 production;
- start PF-M5;
- modify IRO;
- modify Automation runtime architecture;
- rank the remaining open set.

### 2.2 Required review token consumed

| Review | Token |
| --- | --- |
| `~/JOO-Automation/results/pf_m1_kb_openapi_architecture_review/latest.md` | **ARCHITECTURE CHANGES REQUIRED** |

That review is the reason this additive freeze exists. The original PF-M1
document remains the **identity** of the broker-first slice. It is no longer a
sufficient **implementation architecture** for the current repository.

This freeze incorporates every required change from that review (§5–§16).

### 2.3 Sequencing position

```text
PF-M4 production frozen at v7.8
        │
        │  human selection
        ▼
This document — additive PF-M1 KB broker first-slice architecture
        │
        │  later, separately authorized
        ▼
KB broker first-slice implementation
        │
        │  later, separately authorized
        ▼
[PF-M3 Portfolio Snapshot production — not this milestone]
```

| Step | Work | This document |
| --- | --- | --- |
| Original PF-M1 identity | Envelope, source class, Provider Interface intent, reserved KB slot | **Frozen. Not rewritten.** |
| Market-adapter path | `MarketApiAdapter` and market binding/request/transport | **Frozen. Not rewritten.** |
| FactStore `broker_fact` eligibility | Already accepted | **Consume only.** |
| PF-M4 production | `MarketSnapshotProducer` at `v7.8` | **Frozen. Not this slice.** |
| This freeze | Additive KB broker-path architecture | **This document** |
| KB broker implementation | `adapters/kb_open_api.py` and authorized additive files | **Not authorized** |
| PF-M3 production | `PortfolioSnapshotProducer` | **Not authorized** |

### 2.4 How to read the original PF-M1 first-implementation sentence

PF-M1 first-slice language that treats `ProviderGateway` as a new package
with `kb_open_api.py` as the **sole** adapter is the **original greenfield
delivery assumption**. That world no longer exists.

This freeze **occupies the reserved slot inside the existing package**. It
does not:

- recreate `ProviderGateway`;
- delete or rewrite the market-adapter path;
- retag market envelopes as `broker_fact`;
- change PF-M1 package identity;
- reopen FactStore or MarketSnapshotProducer.

---

## 3. Existing frozen contracts

Authority order is highest first. This freeze obeys and does not rewrite
higher authorities.

| Priority | Authority | Review result for this freeze |
| --- | --- | --- |
| 1 | `JOO_CONSTITUTION.md` | Single owner; public APIs change only through an approved architectural milestone; architecture ambiguity is never resolved in implementation |
| 2 | `docs/provider/PF_M1_PROVIDER_GATEWAY_ARCHITECTURE.md` | Identity reused: one package `ProviderGateway`; immutable envelope field model; source-class taxonomy; Provider Interface **intent**; reserved `adapters/kb_open_api.py`; `broker_fact` success tagging |
| 2 | `docs/provider/PROVIDER_GATEWAY_MARKET_ADAPTER_PATH_ARCHITECTURE.md` | Additive market path already accepted; `kb_open_api.py` reserved; broker/market isolation; market `provider_id` must not be `"kb_open_api"` |
| 2 | Accepted `ProviderGateway` implementation | Market path live; collect request currently market-specialized; tests freeze `kb_open_api.py` as absent |
| 2 | `docs/provider/PF_M2_FACT_STORE_ARCHITECTURE.md` and FactStore B freeze | `broker_fact` already eligible; Gateway must not append; store must not re-call providers |
| 2 | `docs/provider/PF_M3_PORTFOLIO_SNAPSHOT_ARCHITECTURE.md` | Downstream consumer of stored broker facts. Not this slice. Not a Gateway upstream. |
| 2 | `docs/provider/PF_M4_MARKET_SNAPSHOT_ARCHITECTURE.md` + implementation | `MarketSnapshotProducer` remains frozen. Broker ingress is not a Market Snapshot responsibility. |
| 2 | `docs/market/MARKET_FIRST_SLICE_DOMAIN_ARCHITECTURE.md` + Market\* | Consume-only as a sequencing fact. No type dependency. |
| 2 | Frozen IRO / IRO-M1 / IRO-M2 | Untouched |
| 2 | Frozen Automation M1–M3 | Untouched; development-only |
| 3 | `docs/JOO_PRODUCT_ARCHITECTURE.md` (present untracked; READ ONLY) | Layer 2 owns KB Open API as first broker; holdings, balances, orders, fills, and account-state are Layer 2 **lifetime** broker facts; research AI is never primary truth |
| 4 | Exact repository HEAD / tag | §1 |
| 5 | Human selection after PF-M4 | §2 |

If any statement in this document appears to conflict with a higher authority
in that authority’s scope, the higher authority wins and this document is
defective — not a silent override.

**Conflict-rule check (pre-authoring):** this freeze does not redesign the
frozen PF-M1 envelope / source-class identity, create a new package, own
FactStore, own MarketSnapshotProducer, own Market\*, or start PF-M3 / PF-M5.
**No ARCHITECTURE CONFLICT.**

### 3.1 What is already sufficient

These points are **not** reopened:

- Owner package remains `ProviderGateway`.
- Envelope field model is already generic enough for `broker_fact`.
- Source-class taxonomy remains `broker_fact | market_fact | research_ai`.
- Reserved broker identity already exists:
  `RESERVED_KB_OPEN_API_PROVIDER_ID = "kb_open_api"`.
- FactStore already accepts a structurally valid success envelope with
  `source_class = "broker_fact"`.
- Market path already rejects `provider_id == "kb_open_api"`.
- Failure-class intent, health snapshot intent, credential-supplier port,
  UTC clock port, and secret-projection helpers already exist and are
  path-neutral enough to reuse.
- Trading, Human Approval, IRO, Evidence, news ingest, ticker/entity
  resolution, PF-M3 production, and PF-M5 are outside this slice.

### 3.2 What the previous review proved is no longer sufficient

The accepted `ProviderGateway` public surface is market-specialized:

- `ProviderInterface.collect` takes `ExplicitCollectRequest`.
- `ExplicitCollectRequest.binding` is exactly `ExplicitMarketAdapterBinding`.
- That binding requires `ExplicitMarketParameterProfile` with `venue_target`,
  session / timezone / calendar selectors, and a market `request_set`.
- Ingress, `MarketTransport`, and collect validators are written against that
  market binding.
- There is no broker binding type, no broker collect request, no broker
  transport port, and no `validate_broker_fact_success_envelope`.
- Package tests freeze `adapters/kb_open_api.py` as **absent**.
- PF-M1 §6.2 left “related broker-reported facts … selected by authorized
  implementation” open.

Those are the ambiguities this freeze closes.

---

## 4. Additive-vs-greenfield ruling

### 4.1 Ruling

| Option | Verdict |
| --- | --- |
| **Additive capability of existing `ProviderGateway`** | **Selected and frozen** |
| Greenfield recreation of `ProviderGateway` as a new sole-adapter package | **Rejected** — the package and market path already exist |
| New package (`BrokerAdapter`, `BrokerGateway`, `KbGateway`, `BrokerFactStore`, sibling envelope package) | **Rejected** — invents a second ingress plane |
| Relocate broker ingress into `FactStore` | **Rejected** — dual write / store-as-gateway |
| Relocate broker ingress into `MarketSnapshotProducer` | **Rejected** — PF-M4 ownership collapse |
| Relocate broker ingress into Market\* or Portfolio\* | **Rejected** — domain packages are not ingress |
| Occupy `kb_open_api.py` by reusing `ExplicitMarketAdapterBinding` with dummy venue / session / timezone / calendar values | **Rejected** — path collapse |
| Rename `ProviderGateway` or the reserved file | **Rejected** — reserved identity stands |

**Owner package identity:** `ProviderGateway` only.

**Additive capability name:** KB Open API broker-adapter path.

**Not created by this document:** the `ProviderGateway` package, any sibling
ops package, any FactStore file, any Market\* file, any
`MarketSnapshotProducer` file.

### 4.2 Ownership table

| Concern | Owner |
| --- | --- |
| This architecture document | JOO `docs/provider/` |
| KB Open API Adapter (first-slice broker path) | `ProviderGateway` (additive) |
| Provider Interface intent (frozen PF-M1; collect request union justified here) | `ProviderGateway` |
| Immutable provider payload envelope (frozen field model) | `ProviderGateway` |
| `source_class = broker_fact` on KB success-path envelopes | `ProviderGateway` |
| `provider_id = "kb_open_api"` on the broker path | `ProviderGateway` |
| Broker-path health / failure / outage signals | `ProviderGateway` |
| Authentication **use** at the broker-path edge | `ProviderGateway` (secrets **supply** remains operator/config outside package invention) |
| Market API Adapter / market binding / market transport | `ProviderGateway` (frozen market path; **not redesigned here**) |
| Fact Store append / eligibility / retrieval | **Not this freeze** (`FactStore`) |
| Portfolio Snapshot production | **Not this freeze** (PF-M3) |
| Market Snapshot composition | **Not this freeze** (PF-M4) |
| Market\* models / validators / invariants | **Not this freeze** |
| Market Watch, IRO, Evidence, trading, Human Approval | **Not this package** |

### 4.3 Non-package rule

The broker-adapter path must not create sibling operational packages for
“BrokerAdapter,” “BrokerGateway,” “KbGateway,” “BrokerFactStore,”
“BrokerEnvelope,” or “BrokerHealth.” Internal modules of `ProviderGateway`
only.

### 4.4 Layout intent (additive; not a scaffold)

PF-M1 §3.5 layout remains the package-structure intent. This freeze occupies
only the reserved broker-adapter slot and the additive broker types required
to attach it:

```text
ProviderGateway/
  adapters/
    kb_open_api.py        # THIS freeze occupies the reserved slot
    market_api.py         # frozen market path; unchanged
    ports.py              # additive BrokerTransport; MarketTransport unchanged
```

This document does **not** create any of those files.

---

## 5. Provider Interface attachment ruling

### 5.1 Frozen intent versus current implementation artifact

PF-M1 §5 froze the **common adapter intent**:

- stable nonblank `provider_id`;
- explicit `declared_source_class`;
- `collect` returns either a successful immutable envelope or a first-class
  failure / outage signal;
- `health` returns a provider-path health snapshot;
- no domain mutation and no FactStore write.

PF-M1 §5.4 exists so later adapters can plug in without redesigning the
envelope or source-class model.

The accepted implementation specialized that intent to the market path
because only the market path existed:

```text
ProviderInterface
  provider_id -> str
  declared_source_class -> str
  collect(request: ExplicitCollectRequest) -> ExplicitCollectOutcome
  health() -> ExplicitProviderHealthSnapshot

ExplicitCollectRequest.binding : ExplicitMarketAdapterBinding
```

That specialization is a **market-path implementation artifact**. It is not
the frozen PF-M1 interface intent. It cannot carry broker traffic without
either dummy market fields or a second interface.

### 5.2 Candidate designs and verdicts

These are the four designs identified by the previous independent review.

| # | Design | Verdict |
| --- | --- | --- |
| 1 | Generalize `ExplicitCollectRequest.binding` so one request type carries either market or broker bindings | **Rejected** — collapses request semantics into one market-named type; risks dummy or unused market fields on broker traffic |
| 2 | Add broker-only request / binding types and widen `ProviderInterface.collect` to the union of path-specific request types | **Selected and frozen** |
| 3 | Add a second interface or a broker-only collect path outside `ProviderInterface` | **Rejected** — conflicts with PF-M1 “one common interface”; invents a second ingress contract |
| 4 | Reuse `ExplicitMarketAdapterBinding` with dummy venue / session / timezone / calendar values | **Rejected** — path collapse; forbidden by this freeze and by the previous review |

### 5.3 Selected attachment model

The KB adapter attaches through the **same Provider Interface intent**.

The collect **request type is path-specific**. The collect **outcome type
remains shared**.

```text
ProviderInterface
  provider_id -> str
  declared_source_class -> str
  collect(request: ExplicitCollectRequest | ExplicitBrokerCollectRequest)
      -> ExplicitCollectOutcome
  health() -> ExplicitProviderHealthSnapshot
```

| Path | Adapter | Request type accepted | Declared source class |
| --- | --- | --- | --- |
| Market | `MarketApiAdapter` | `ExplicitCollectRequest` only | `"market_fact"` |
| Broker | `KbOpenApiAdapter` | `ExplicitBrokerCollectRequest` only | `"broker_fact"` |

### 5.4 Justified Provider Interface change

This is the **only** authorized Provider Interface mutation.

**Justification:** `collect(request: ExplicitCollectRequest)` currently
requires a market binding. Occupying the reserved broker slot without that
change would force one of the rejected designs (dummy market fields, a second
interface, or silent request-semantic collapse). Constitution requires an
explicit architectural milestone before an accepted public contract changes.
This freeze is that milestone. Downstream convenience is not the reason.

**Authorized change, exactly:**

- `ProviderInterface.collect` request annotation widens from
  `ExplicitCollectRequest` to
  `ExplicitCollectRequest | ExplicitBrokerCollectRequest`.
- Method name, outcome type, `provider_id`, `declared_source_class`, and
  `health()` remain unchanged.

**Not authorized:**

- renaming `ProviderInterface`;
- adding a second collect method;
- adding a second interface;
- renaming `ExplicitCollectRequest`;
- changing `ExplicitCollectRequest.binding` away from
  `ExplicitMarketAdapterBinding`;
- changing `MarketApiAdapter.collect` to accept broker requests;
- changing `health()` or envelope fields.

### 5.5 Cross-path collect rule

1. `MarketApiAdapter.collect` continues to require exact
   `ExplicitCollectRequest` and continues to validate through
   `validate_explicit_collect_request`.
2. `KbOpenApiAdapter.collect` requires exact
   `ExplicitBrokerCollectRequest` and validates through
   `validate_explicit_broker_collect_request`.
3. Passing a broker request to `MarketApiAdapter` remains a structural
   exact-type failure. That market-path behavior is **not** redesigned into a
   new failure envelope.
4. Passing a market request to `KbOpenApiAdapter` is a structural exact-type
   failure of the broker request validator.
5. Neither adapter coerces, projects, or fills dummy fields to accept the
   other path’s request.

### 5.6 Interface non-goals retained

The Provider Interface still does **not**:

- schedule 24/7 jobs;
- decide IRO run starts;
- place, cancel, or modify broker orders;
- abstract research AI committee completion;
- define Fact Store append APIs;
- define Portfolio Snapshot or Market Snapshot composition.

---

## 6. Broker request model

### 6.1 Authorized type

| Field | Decision |
| --- | --- |
| **Name** | `ExplicitBrokerCollectRequest` |
| **Kind** | Frozen immutable dataclass; no defaults |
| **Owner** | `ProviderGateway.models` |
| **Used by** | `KbOpenApiAdapter.collect` only |
| **Not used by** | `MarketApiAdapter`, `validate_explicit_collect_request`, `MarketTransport` |

### 6.2 Field contract

| Field | Type | Rule |
| --- | --- | --- |
| `envelope_id` | `str` | Caller-supplied opaque nonblank identity of this ingress capture. Gateway does not generate it. |
| `request_correlation_id` | `str \| None` | Optional opaque nonblank correlation id. Must not contain secrets. |
| `binding` | `ExplicitBrokerAdapterBinding` | Exact broker binding. Never `ExplicitMarketAdapterBinding`. |
| `request_kind` | `str` | Exactly one authorized first-slice kind from §9. Must be a member of the binding’s `request_set`. |

`collected_at` is **not** a request field. It is assigned at Gateway
acceptance from the injected UTC clock.

### 6.3 One collect attempt, one kind, one envelope

| Rule | Statement |
| --- | --- |
| Granularity | One accepted success envelope maps **one** broker-provider wire response (or one structured mapping of that response) for **one** `request_kind` and **one** collection attempt |
| No multi-kind merge | Gateway does not collect holdings, balances, and account-state in one `collect()` and merge them into one invented envelope |
| No multi-account merge | Distinct `account_selector` values require distinct bindings and distinct collect attempts |
| No multi-book merge | Distinct broker books / inquiry scopes require distinct bindings. Transport must not concatenate multiple inquiry scopes into one body |
| Provider-native batching | If the provider returns a batched body for that one kind and one selector (for example a list of holdings), the batch remains opaque payload content of that one envelope |

A caller who wants all three authorized kinds issues three `collect()` calls
and receives three envelopes or three first-class failures.

### 6.4 Why `request_kind` is on the request

The market path can leave endpoint selection inside a market `request_set`
because that path productizes only last/reference price and market-status
observation as captured content.

The previous review forbade leaving broker request content to
“implementation selection.” `request_kind` makes the first-slice surface
explicit at collect time. A binding may authorize one, two, or all three
kinds. Each attempt still names exactly one kind.

`request_kind` is **not** added to the envelope field model.

### 6.5 Request non-responsibilities

`ExplicitBrokerCollectRequest` must **not**:

- carry venue, session, timezone, or calendar selectors;
- reuse `ExplicitMarketAdapterBinding` or `ExplicitMarketParameterProfile`;
- name order-placement, cancel, or modify operations;
- name read-only orders or fills in this first slice;
- carry secrets, tokens, or passwords;
- carry Portfolio\* or Market\* objects.

---

## 7. Broker binding model

### 7.1 Authorized types

Two additive types. Neither is a market type.

```text
ExplicitBrokerParameterProfile
  profile_id: str
  account_selector: str
  request_set: tuple[str, ...]

ExplicitBrokerAdapterBinding
  provider_id: str
  credential_ref: str
  parameter_profile: ExplicitBrokerParameterProfile
```

Both are frozen immutable dataclasses with no defaults.

### 7.2 Profile field rules

| Field | Rule |
| --- | --- |
| `profile_id` | Opaque nonblank caller-supplied identity of this parameter profile. Not a Portfolio\* or Market\* id. |
| `account_selector` | Opaque nonblank operator-supplied inquiry-target selector for the broker account / book / inquiry scope this binding may read. Gateway does not parse, normalize, or resolve it to a JOO subject. |
| `request_set` | Non-empty tuple. Every element is a nonblank string and a member of `BROKER_REQUEST_KIND_VALUES` from §9. Caller order is preserved. Gateway does not sort or deduplicate. |

`account_selector` is the **sole** inquiry-target selector. Distinct accounts
or distinct broker books are distinct bindings with distinct
`account_selector` values. This field is **not** `venue_target`,
`session_selector`, `timezone_selector`, or `calendar_selector`.

### 7.3 Binding field rules

| Field | Rule |
| --- | --- |
| `provider_id` | Exact nonblank string. On this first slice it **must** be `RESERVED_KB_OPEN_API_PROVIDER_ID` (`"kb_open_api"`). |
| `credential_ref` | Opaque nonblank operator-supplied credential reference. It is not the secret. |
| `parameter_profile` | Exact `ExplicitBrokerParameterProfile`. |

### 7.4 Validation intent

Validators are type / nonblank / membership / required-presence only. First
failure wins. Upstream exception objects propagate unchanged. Surrounding
whitespace on otherwise nonblank strings is accepted and preserved.
Validators do not trim, sort, convert, copy, or reconstruct.

`validate_explicit_broker_parameter_profile` and
`validate_explicit_broker_adapter_binding` are **new**. They must not be
implemented by calling market-profile or market-binding validators.

`validate_explicit_broker_collect_request` additionally requires:

1. exact `ExplicitBrokerCollectRequest`;
2. `request_kind` is a member of `BROKER_REQUEST_KIND_VALUES`;
3. `request_kind` is a member of
   `binding.parameter_profile.request_set`.

A `request_kind` outside the binding’s `request_set` is a structural request
error, not a provider outage.

### 7.5 Forbidden binding designs

| Design | Verdict |
| --- | --- |
| Reuse `ExplicitMarketAdapterBinding` | Forbidden |
| Reuse `ExplicitMarketParameterProfile` | Forbidden |
| Add dummy `venue_target` / session / timezone / calendar to the broker profile so one type can serve both paths | Forbidden |
| Share one binding object across `MarketApiAdapter` and `KbOpenApiAdapter` | Forbidden |
| Allow `provider_id != "kb_open_api"` on this first-slice broker binding | Forbidden |
| Encode JOO portfolio subject ids in `account_selector` as a resolution product | Forbidden |

---

## 8. Broker transport boundary

### 8.1 Authorized protocol

Add `BrokerTransport`. Do **not** reuse `MarketTransport`.

```text
BrokerTransport
  read(binding: ExplicitBrokerAdapterBinding,
       credential: str,
       request: ExplicitBrokerCollectRequest)
      -> ExplicitTransportSuccess | ExplicitTransportFailure
  probe(binding: ExplicitBrokerAdapterBinding)
      -> ExplicitHealthProbe | ExplicitTransportFailure
```

`read` is one collection attempt for the request’s `request_kind` and
binding. It returns one structured success body or one structured failure.
`probe` is a health/availability observation for that broker binding.

### 8.2 What may be reused

These existing types are path-neutral result / port shapes. Reusing them is
**not** market-path collapse:

| Reused surface | Reason it is reusable |
| --- | --- |
| `ExplicitTransportSuccess` | Body-only success result. No market fields. |
| `ExplicitTransportFailure` | Failure class + optional detail. No market fields. |
| `ExplicitHealthProbe` | Availability + optional detail. No market fields. |
| `CredentialSupplier` | `credential_ref -> object`. No market fields. |
| `UtcClock` | Returns UTC `datetime`. No market fields. |

### 8.3 What must not be reused

| Surface | Reason |
| --- | --- |
| `MarketTransport` | Signature is bound to `ExplicitMarketAdapterBinding` and `ExplicitCollectRequest` |
| `ExplicitMarketAdapterBinding` | Market binding |
| `ExplicitMarketParameterProfile` | Market parameterization |
| `collect_market_attempt` | Market ingress orchestration |
| `observe_market_health` | Market health orchestration |
| Any Market\* type | Domain ownership |

### 8.4 Transport non-product rules

1. Exact HTTP client, SDK, or vendor URL map is **not** frozen here.
   Transport is an injected port.
2. Transport may perform the vendor reads required to obtain **one**
   `request_kind` for **one** `account_selector`. It must not fan out into
   other kinds or other selectors and merge the results.
3. Transport must not place, cancel, or modify orders.
4. Transport must not persist secrets to disk, envelopes, diagnostics, or
   FactStore.
5. No exclusive commercial HTTP library is frozen.
6. Additional named brokers are not authorized by this transport port.

### 8.5 Additive broker ingress orchestration

`KbOpenApiAdapter` uses additive broker ingress functions parallel to the
market functions:

- `collect_broker_attempt(...)`
- `observe_broker_health(...)`

These may live in `ProviderGateway/ingress.py` as **additive** functions.
`collect_market_attempt` and `observe_market_health` observable behavior
remains unchanged.

`read_utc_clock` may be reused because it is path-neutral.

Private helpers may be shared only when they are path-neutral (clock read,
known failure-class mapping, secret sanitization) **and** market-path
observable behavior remains identical. A helper that currently requires
`ExplicitMarketAdapterBinding` must not be widened in a way that changes
market collect outcomes.

---

## 9. Exact KB first-slice read surface

### 9.1 Closed vocabulary

```text
BROKER_REQUEST_KIND_VALUES = (
    "holdings",
    "balances",
    "account_state",
)
```

This vocabulary is additive in `ProviderGateway.models.vocabularies`.
Implementation must not invent additional first-slice kinds.

### 9.2 Inclusion status (normative)

| Surface | First-slice status | Meaning |
| --- | --- | --- |
| **holdings** | **IN** | Read-only capture of provider-reported holding positions as the broker exposes them |
| **balances** | **IN** | Read-only capture of provider-reported cash / balance / deposit observations as the broker exposes them |
| **account-state observations** | **IN** as `account_state` | Read-only capture of provider-reported account usability / status / constraint observations as the broker exposes them |
| **read-only orders** | **OUT** | Deferred. Not a first-slice `request_kind`. Not “related facts selected by implementation.” |
| **read-only fills** | **OUT** | Deferred. Not a first-slice `request_kind`. Not “related facts selected by implementation.” |

There is no residual “related broker-reported facts” clause in this slice.

### 9.3 Why this inclusion set

1. Original PF-M1 §6.2 named holdings, balances, and account-state
   observations as the explicit broker read intent.
2. Product architecture names orders and fills as Layer 2 **lifetime** broker
   facts. Lifetime membership is not a first-slice implementation license.
3. PF-M3 later consumes stored holdings, and treats balances as retrieved
   broker facts rather than snapshot domain fields. It does not consume an
   order book or fill tape.
4. Constitution requires the minimum responsibility owned by the current
   milestone.
5. Market first-slice precedent productized last/reference price and
   market-status only, even though Layer 2 lifetime market facts are broader.

### 9.4 Kind meanings (architecture-level, not domain types)

| `request_kind` | Captured content | Not |
| --- | --- | --- |
| `holdings` | Provider-native positions, quantities, and broker instrument / symbol codes as returned | `PortfolioHoldingObservation`, `PortfolioPosition`, valuation, marks |
| `balances` | Provider-native cash / balance / deposit figures and currencies as returned | dedicated cash domain type, NAV, buying-power product |
| `account_state` | Provider-native account status / restriction / usability strings as returned | Gateway health snapshot, Portfolio\* membership, invented “account healthy” |

Broker-native identifiers in the payload remain **opaque captured content**.
Mapping them to JOO portfolio subjects is not this slice.

### 9.5 Extra wire fields are not first-slice products

If a holdings, balances, or account-state wire body also includes
orderable quantity, pending settlement, buying power, order lists, fill
lists, or similar extra fields, those bytes/fields may remain opaque
captured content of that one envelope.

This freeze does **not**:

- authorize orders or fills as first-slice kinds;
- authorize those extra fields as Gateway products;
- require later PF-M3 or FactStore to interpret them.

### 9.6 Explicitly out of the first-slice read surface

The adapter must **not** issue first-slice collect attempts for:

- order placement, cancellation, or modification;
- read-only orders;
- read-only fills;
- prices, quotes, calendars, or market status;
- news, research, or alternative data;
- any class outside `BROKER_REQUEST_KIND_VALUES`.

---

## 10. Authentication boundary

### 10.1 Credential supplier reuse

**Decision: reuse `CredentialSupplier`.** Do not invent a broker-specific
credential protocol or a secrets-vault product.

| Question | Decision |
| --- | --- |
| Credential supplier | **Reuse** the existing injected `CredentialSupplier` (`credential_ref -> object`) |
| Broker-specific credential protocol | **Rejected** — second secrets product |
| Secret storage / vault | **Forbidden** |
| UTC clock | **Reuse** existing injected `UtcClock` and `read_utc_clock` |
| Credential helpers | **Reuse** `resolve_outbound_credential`, `apply_outbound_credential`, `project_opaque_payload`, `payload_contains_secret`, `sanitize_detail`, and `SECRET_FIELD_NAMES` without redesign |
| Broker `credential_ref` | Distinct field on `ExplicitBrokerAdapterBinding`. Operator may choose distinct refs for broker and market. Architecture does not share secrets across adapters. |

`ProviderGateway/auth/credentials.py` has **no required mutation**.

### 10.2 Boundary rules (normative)

1. Gateway **uses** credentials. It does not invent secret storage.
   Operator-supplied configuration, environment, or external secret injection
   provides the broker credential referenced by `credential_ref`.
2. Authentication material must **not** appear in envelope `payload`,
   `error_diagnostics`, health `detail`, or stored FactStore content.
3. Authenticated access is a Layer 2 responsibility. The KB adapter
   constructs authenticated read requests through `BrokerTransport`.
4. Auth failure is a provider failure class, not a research, CIO, Market
   Watch, or capital event.
5. Write / trading credentials are out of this slice. Even if the same
   broker later serves BX-M1, capital write paths remain Broker Execution
   ownership.
6. No credential sharing into IRO, Market\*, Portfolio\*, FactStore, or
   `MarketSnapshotProducer`. Those consumers must not receive broker secrets
   through envelopes.

### 10.3 Token / authentication failure behavior

| Condition | Signal |
| --- | --- |
| Missing credential, supplier exception, non-`str` secret, or blank secret at call time | `AUTH_FAILURE`; no synthetic holdings, balances, or account state |
| Auth rejected by KB Open API / expired or invalid token reported by transport | `AUTH_FAILURE`; envelope status is failure, not success |
| Transport timeout during auth or request | `TRANSPORT_FAILURE` or `UNAVAILABLE` as reported / mapped; no invented facts |
| Provider error body after auth succeeded | `PROVIDER_ERROR` |
| Rate limit observed | `RATE_LIMITED` |
| Body cannot be mapped without repair, empty after secret projection, or residual secret leakage | `VALIDATION_FAILURE` |

**Token refresh is not a Gateway product.** Transport may use the supplied
secret to obtain an ephemeral access token for that one read or probe. That
ephemeral token is process-local transport state at most. It is not
persisted by `ProviderGateway` modules to disk, envelopes, diagnostics,
logs-as-facts, or FactStore.

Gateway does not implement a token cache API, refresh scheduler, or vault.

### 10.4 Secret non-persistence rules

1. Secrets are outbound-only.
2. `project_opaque_payload` continues to drop forbidden secret field names.
3. If the projected payload still contains the outbound secret value, the
   attempt is `VALIDATION_FAILURE`, not a success envelope.
4. Diagnostics and health detail are sanitized with the same non-secret
   rules already used on the market path.
5. No new secret-field vocabulary is required unless implementation later
   proves a KB-specific secret key that is not already in
   `SECRET_FIELD_NAMES`. Adding a name is an implementation-authorization
   detail, not a new secrets product. It is not authorized by this document
   alone.

---

## 11. broker_fact envelope construction

### 11.1 Envelope type reuse

Reuse the frozen PF-M1 immutable provider payload envelope
`ExplicitProviderPayloadEnvelope`.

Do **not** create a second broker envelope type. No constitutional conflict
requires one. The existing fields remain exactly:

- `envelope_id`
- `provider_id`
- `source_class`
- `collected_at`
- `status`
- `payload`
- `error_diagnostics`
- `request_correlation_id`

Do not add `request_kind` to the envelope. Do not drop any frozen field.

### 11.2 Mapping rule (normative)

```text
External KB Open API wire response (or structured error)
        │
        ▼
KbOpenApiAdapter / collect_broker_attempt maps fields (no semantic repair)
        │
        ▼
Immutable Provider Payload Envelope
  provider_id  = "kb_open_api"
  source_class = "broker_fact"   (success-path fact envelopes)
  (frozen after acceptance; no in-place rewrite)
```

### 11.3 Success-path construction

On a mapped provider success response:

| Field | Rule |
| --- | --- |
| `envelope_id` | Caller-supplied from the request. Not generated. |
| `provider_id` | Binding `provider_id`, which is exactly `"kb_open_api"` |
| `source_class` | Exactly `"broker_fact"`. Literal at construction. Never inferred. |
| `collected_at` | UTC time at Gateway acceptance from the injected clock |
| `status` | `"success"` |
| `payload` | Opaque projected broker content (`dict`). Non-empty after secret projection. |
| `error_diagnostics` | `None` |
| `request_correlation_id` | From the request |

`validate_broker_fact_success_envelope` is a **new** extra-rule validator
parallel to `validate_market_fact_success_envelope`:

1. generic envelope validator accepts the envelope;
2. `status` is `"success"`;
3. `source_class` is exactly `"broker_fact"`;
4. `provider_id` is exactly `RESERVED_KB_OPEN_API_PROVIDER_ID`.

`validate_market_fact_success_envelope` remains unchanged and continues to
**reject** `provider_id == "kb_open_api"`.

### 11.4 Failure-path construction

Failure / outage produces `ExplicitCollectOutcome` with
`result_kind = "failure"`, `envelope = None`, and a first-class
`ExplicitProviderFailureSignal`. That is the existing outcome model.

A pure failure path must **not** emit a success envelope with an empty or
invented holdings / balances / account-state body.

### 11.5 Allowed mapping / forbidden repair

**Allowed:** copy / project provider wire fields into the frozen envelope
shape.

**Forbidden under any “normalization,” “enrichment,” or “convenience” name:**

- semantic extraction;
- ticker / entity / alias resolution into JOO subject ids;
- construction of Portfolio\* or Market\* models;
- inventing missing holdings, balances, account state, orders, fills,
  prices, or market status;
- converting research AI text into `broker_fact`;
- retagging market payloads as `broker_fact` or broker payloads as
  `market_fact`;
- applying EvidenceProvenance `primary | secondary | unknown`;
- unit conversion, timezone conversion as semantic repair, or identifier
  trimming that invents identity.

### 11.6 Immutability invariants (reused)

1. Accepted envelopes are immutable value records.
2. Payload body after acceptance is not rewritten.
3. Source class is explicit at construction; never inferred later.
4. Gateway does not append envelopes to FactStore.
5. Gateway does not delete or revise prior handed-off envelopes.

---

## 12. Provider identity rules

### 12.1 Broker path

| Rule | Statement |
| --- | --- |
| Adapter class | `KbOpenApiAdapter` |
| File | `ProviderGateway/adapters/kb_open_api.py` |
| `provider_id` | Exactly `"kb_open_api"` |
| Constant | `RESERVED_KB_OPEN_API_PROVIDER_ID` |
| `declared_source_class` | Literal `"broker_fact"` |
| Binding `provider_id` | Must equal `"kb_open_api"` or the broker binding validator fails |
| Other broker ids | Not authorized in this first slice |

`KbOpenApiAdapter.provider_id` is the binding’s `provider_id`. After
validation that value is `"kb_open_api"`.

### 12.2 Market path (unchanged)

| Rule | Statement |
| --- | --- |
| `MarketApiAdapter` | Unchanged |
| `ExplicitMarketAdapterBinding.provider_id` | Must **not** be `"kb_open_api"` |
| `validate_market_fact_success_envelope` | Continues to reject `"kb_open_api"` |
| Market `declared_source_class` | Remains literal `"market_fact"` |

### 12.3 Isolation

1. `"kb_open_api"` is authorized on the broker path only.
2. The market path continues to reject `"kb_open_api"`.
3. Sharing a commercial vendor family, if that ever occurs later, does
   **not** collapse adapter identity, source class, or health path.
4. `provider_id` is Gateway-owned. It is not a Portfolio\* id, Market\* id,
   or broker account number.
5. `provider_id` is never inferred from payload text.

---

## 13. Failure / health / outage behavior

### 13.1 Reused failure-class intent

Reuse the existing closed vocabulary. Do not invent a second failure plane.

```text
AUTH_FAILURE
TRANSPORT_FAILURE
PROVIDER_ERROR
UNAVAILABLE
RATE_LIMITED
VALIDATION_FAILURE
```

Reuse `ExplicitProviderFailureSignal`, `ExplicitCollectOutcome`,
`build_provider_failure_signal`, and `build_failure_outcome`.
`ProviderGateway/signaling.py` has **no required mutation**.

### 13.2 Reused health snapshot intent

Reuse `ExplicitProviderHealthSnapshot` and
`build_provider_health_snapshot`.

| Field | Rule on the broker path |
| --- | --- |
| `provider_id` | `"kb_open_api"` |
| `observed_at` | UTC observation time from the injected clock |
| `availability` | `available` / `degraded` / `unavailable` |
| `detail` | Optional non-secret diagnostic summary |

Health is **per broker binding**, not a merged “broker and market are both
up” product. Market-path health remains a separate signal.

`ProviderGateway/health.py` has **no required mutation**.

### 13.3 Probe-to-availability mapping

Reuse the market-path intent:

| Probe failure class | Availability |
| --- | --- |
| `RATE_LIMITED`, `PROVIDER_ERROR` | `degraded` |
| Other probe failures / unknown probe result / probe exception | `unavailable` |

### 13.4 Fail-closed posture (normative)

Broker failure / outage must **not** invent:

- holdings
- balances
- account state
- orders
- fills
- prices
- market status

Additional posture rules:

1. No elevation of partial garbage to success by silent repair.
2. Failure signals are first-class outputs. Consumers must not need to parse
   free-text logs to detect outage.
3. Health checks must not fabricate success envelopes on “available.”
4. Health must not trigger IRO, Market Watch, PF-M3 production, or trading.
5. Failures are not CIO events, evidence findings, or human capital
   approvals.
6. Downstream FactStore and snapshot planes treat missing / failed ingress
   as staleness / fail-closed inputs. This freeze supplies the signals. It
   does not implement those downstream policies.

### 13.5 Success vs failure semantics (broker path)

| Outcome | Status | `source_class` | `payload` | May later be treated as a holdings / balance / account-state fact? |
| --- | --- | --- | --- | --- |
| Mapped provider success response | Success | `broker_fact` | Opaque captured broker content | **Candidate only** — FactStore already decides eligibility; Gateway does not append |
| Auth / transport / provider / unavailable / rate-limit / validation failure | Failure | Not a success-path fact tag | No success payload | **No** — must not be treated as invented holdings, balances, or account state |

---

## 14. FactStore handoff

### 14.1 Ownership

ProviderGateway **emits** immutable `broker_fact` envelopes. It does **not**
append, retrieve, or call FactStore.

FactStore remains the sole persistence owner. It already accepts a
structurally valid success envelope with `source_class = "broker_fact"`.
This freeze requires **no FactStore mutation**.

### 14.2 Handoff object

The sole success-path handoff object is the frozen PF-M1 envelope produced
by `KbOpenApiAdapter`.

FactStore does not receive Portfolio\* objects from Gateway. FactStore does
not receive Market\* objects from Gateway. FactStore does not receive PF-M3
or PF-M4 snapshots from Gateway.

### 14.3 Success-path constraints a later caller may rely on

When Gateway emits a success-path broker fact envelope:

1. the envelope is immutable after acceptance;
2. `source_class` is exactly `"broker_fact"`;
3. `provider_id` is exactly `"kb_open_api"`;
4. `collected_at` is the Gateway-boundary UTC collection time;
5. `envelope_id` is the caller-supplied opaque id;
6. `status` is `"success"`;
7. `payload` is opaque captured broker content, not Portfolio\* / Market\*
   structure;
8. payload and diagnostics contain no secrets;
9. source class was explicit at construction, not inferred.

The rightful later caller / orchestration boundary may construct a FactStore
append request from that envelope. That caller is **not** this adapter and
**not** this freeze.

### 14.4 Failure / outage constraints FactStore already honors

1. Failure / outage signals are not append inputs.
2. Health snapshots are not facts.
3. FactStore must not invent holdings, balances, or account state when
   Gateway emits only outage / failure.
4. FactStore must not re-call KB Open API as a second Gateway.

### 14.5 Direction

```text
external KB Open API
        │
        ▼
ProviderGateway broker adapter
        │
        ▼
immutable broker_fact envelope
        │
        │  handoff only — no append, no store call
        ▼
later FactStore append by the rightful caller / orchestration boundary
        │
        │  later; not this milestone
        ▼
[PF-M3 PortfolioSnapshotProducer — composition only]
```

Gateway does **not** require FactStore to exist at runtime to **construct**
envelopes. Gateway must **not** implement FactStore persistence to complete
this freeze.

---

## 15. Market-path isolation

### 15.1 Isolation rules (normative)

1. `MarketApiAdapter` behavior is unchanged.
2. `ExplicitMarketAdapterBinding` semantics are unchanged.
3. `ExplicitMarketParameterProfile` semantics are unchanged.
4. `validate_market_fact_success_envelope` is unchanged.
5. `MarketTransport` is unchanged.
6. `ExplicitCollectRequest` remains the market collect request.
7. Market success envelopes remain `source_class = "market_fact"`.
8. Broker success envelopes remain `source_class = "broker_fact"`.
9. Neither path retags the other.
10. Broker types do not use dummy venue / session / timezone / calendar
    values.
11. Broker ingress does not import or construct Market\* structures.
12. Broker ingress does not call or modify `MarketSnapshotProducer`.
13. Broker ingress is not a Market Snapshot responsibility.
14. Market collect tests that reject `provider_id == "kb_open_api"` remain
    valid and must continue to pass.

### 15.2 Shared surfaces that are not isolation breaches

Sharing the following does **not** collapse the two paths:

- `ProviderInterface` intent and the justified collect union;
- `ExplicitProviderPayloadEnvelope` field model;
- `ExplicitCollectOutcome`;
- `ExplicitProviderHealthSnapshot` / `ExplicitProviderFailureSignal`;
- failure-class and availability vocabularies;
- `CredentialSupplier`, `UtcClock`, and secret-projection helpers;
- `ExplicitTransportSuccess` / `ExplicitTransportFailure` /
  `ExplicitHealthProbe`.

Those surfaces are path-neutral. Request, binding, transport protocol, source
class, and reserved provider id remain path-specific.

---

## 16. Exact mutation allowlist

### 16.1 New production file authorized at later implementation

| Path | Role |
| --- | --- |
| `ProviderGateway/adapters/kb_open_api.py` | `KbOpenApiAdapter` occupying the reserved slot |

### 16.2 Existing ProviderGateway files that may be modified

Only additive mutations. Market-path observable contracts stay intact.

| Path | Authorized mutation |
| --- | --- |
| `ProviderGateway/provider_interface.py` | Widen `collect` request type to `ExplicitCollectRequest \| ExplicitBrokerCollectRequest`. Nothing else. |
| `ProviderGateway/models/types.py` | Add `ExplicitBrokerParameterProfile`, `ExplicitBrokerAdapterBinding`, `ExplicitBrokerCollectRequest` |
| `ProviderGateway/models/vocabularies.py` | Add `BROKER_REQUEST_KIND_VALUES` |
| `ProviderGateway/models/__init__.py` | Export the additive types / vocabulary |
| `ProviderGateway/validation/validators.py` | Add broker validators and `validate_broker_fact_success_envelope`. Do **not** change market validator rules. |
| `ProviderGateway/validation/__init__.py` | Export additive validators |
| `ProviderGateway/adapters/ports.py` | Add `BrokerTransport`. Leave `MarketTransport` unchanged. |
| `ProviderGateway/ingress.py` | Add `collect_broker_attempt` and `observe_broker_health`. Market collect / health behavior unchanged. |
| `ProviderGateway/README.md` | Document the occupied broker slot beside the frozen market path |
| `ProviderGateway/tests/test_boundary.py` | Invert `kb_open_api.py` absence; add broker isolation / interface assertions |
| `ProviderGateway/tests/test_adapter.py` | Additive `KbOpenApiAdapter` tests. Existing market rejection of `"kb_open_api"` remains. |
| `ProviderGateway/tests/test_models.py` | Additive broker model contracts |
| `ProviderGateway/tests/test_validation.py` | Additive broker validators |
| `ProviderGateway/tests/builders.py` | Additive broker builders |

### 16.3 Existing ProviderGateway files that should remain unchanged

No contract-level reason to modify these:

| Path | Reason |
| --- | --- |
| `ProviderGateway/adapters/market_api.py` | Frozen market adapter behavior |
| `ProviderGateway/auth/credentials.py` | Reused as-is |
| `ProviderGateway/auth/__init__.py` | Reused as-is |
| `ProviderGateway/health.py` | Reused as-is |
| `ProviderGateway/signaling.py` | Reused as-is |
| `ProviderGateway/validation/common.py` | Reused as-is |
| `ProviderGateway/adapters/__init__.py` | Empty; no export module is required |

### 16.4 Must remain unchanged

Unless a later architecture proves an unavoidable contract-level reason —
and this freeze does **not** prove one:

- `MarketApiAdapter` behavior
- `ExplicitMarketAdapterBinding` semantics
- `ExplicitMarketParameterProfile` semantics
- `market_fact` success rules
- FactStore (entire package)
- MarketSnapshotProducer (entire package)
- Market\* packages
- IRO / IRO-M1 / IRO-M2
- Automation runtime architecture
- Existing architecture documents other than the creation of this file
- Out-of-boundary untracked documents listed in §1

### 16.5 Tests that currently freeze absence

`ProviderGateway/tests/test_boundary.py::test_kb_open_api_adapter_file_is_absent`
is authorized to invert at implementation time to require the reserved file
to exist and to export `KbOpenApiAdapter`.

README tests that currently describe a reserved/omitted file are authorized
to describe occupation of that file. Market-path README fragments should be
preserved so existing market assertions need not be loosened.

---

## 17. Dependency direction

### 17.1 Normative direction

```text
external KB Open API
        │
        ▼
ProviderGateway broker adapter
        │
        ▼
immutable broker_fact envelope
        │
        ▼
later FactStore append by the rightful caller / orchestration boundary
```

ProviderGateway must not own persistence.

### 17.2 Forbidden edges

| Forbidden edge | Reason |
| --- | --- |
| `ProviderGateway` → FactStore append / retrieve / runtime call | Store is PF-M2 |
| FactStore → KB Open API re-fetch | No second Gateway |
| `ProviderGateway` → `MarketSnapshotProducer` | PF-M4 ownership |
| `MarketSnapshotProducer` → broker ingress | Broker ingress is not Market Snapshot |
| `ProviderGateway` → Market\* import / construct | Domain ownership |
| `ProviderGateway` → Portfolio\* construct as ingress success | Domain ownership; PF-M3 later |
| `ProviderGateway` → IRO run coordination | Plane separation |
| `ProviderGateway` → Evidence Store | Research artifacts ≠ provider facts |
| `ProviderGateway` → Human Approval / Broker Execution trading | Capital plane |
| Broker path → retag `market_fact` | Path isolation |
| Market path → retag `broker_fact` | Path isolation |
| Broker path → dummy market binding fields | Path collapse |
| `research_ai` → FactStore as primary fact | Hard product rule |
| `ProviderGateway` → news ingest without amendment | PF-M1 R1 retained |
| `ProviderGateway` → `joo_auto` runtime dependency | Automation is development-only |

### 17.3 Internal broker-path order

```text
Provider Interface
    ▲
    │ implements
KbOpenApiAdapter
    │ uses
BrokerTransport + reused CredentialSupplier + reused UtcClock
    │ produces
Immutable envelope (broker_fact, provider_id = kb_open_api)
    │ and/or
Health / Failure / Outage signals
```

---

## 18. Deferred responsibilities

| Deferred responsibility | Until |
| --- | --- |
| Production implementation of this freeze | Separate implementation authorization after architecture review |
| PF-M3 Portfolio Snapshot production | **PF-M3** implementation authorization |
| Read-only orders observation | Later authorized broker-observation slice |
| Read-only fills observation | Later authorized broker-observation slice |
| Additional broker adapters beyond KB Open API | Later PF gateway milestones |
| Trading writes / order placement / cancel / modify | **BX-M1** + Human Approval |
| Token vault / secret-management product | Never this package |
| Research AI transport classification runtime under Gateway | Explicit later freeze; Stage 1/2 retain invocation |
| News / alternative non-frozen source classes | Architecture amendment required first |
| Ticker / entity / alias resolution | Permanently outside Gateway |
| Entity resolution of broker symbols to JOO subjects | Later snapshot / domain linking — never Gateway |
| Market Watch | **PF-M5** |
| Exact vendor URL map / HTTP client / SDK selection | Implementation authorization |
| Full rate-limit control plane / 24/7 scheduler topology | Later ops freezes |
| Durable recording of health / outage signals inside FactStore | Explicit later store contract if ever needed |
| IRO-M2 implementation | Separate plane; not ranked by this freeze |

---

## 19. Forbidden responsibilities

The PF-M1 KB Open API broker first slice **must not**:

1. Create a new package (`BrokerAdapter`, `BrokerGateway`, `KbGateway`,
   `BrokerFactStore`, sibling envelope / health packages).
2. Recreate or rename `ProviderGateway`.
3. Redesign frozen PF-M1 envelope / source-class identity.
4. Redesign `MarketApiAdapter`, `ExplicitMarketAdapterBinding`,
   `ExplicitMarketParameterProfile`, `MarketTransport`, or
   `validate_market_fact_success_envelope`.
5. Force broker traffic through market binding types or dummy
   venue / session / timezone / calendar values.
6. Collapse broker and market request semantics into one request type.
7. Own FactStore append, eligibility, persistence, or retrieval.
8. Call FactStore.
9. Begin PF-M3 Portfolio Snapshot production.
10. Modify `MarketSnapshotProducer` or begin PF-M5 Market Watch.
11. Import or construct Market\* structures.
12. Import or construct Portfolio\* structures as ingress success products.
13. Retag broker envelopes as `market_fact` or market envelopes as
    `broker_fact`.
14. Infer `source_class` from payload text.
15. Invent holdings, balances, account state, orders, fills, prices, or
    market status on failure / outage.
16. Include read-only orders or fills as first-slice `request_kind` values.
17. Place, cancel, or modify orders; perform real capital actions; execute
    automatically; or bypass Human Approval.
18. Treat research AI as broker truth or produce `research_ai` envelopes on
    this path.
19. Ingest news / alternative data without architecture amendment.
20. Resolve tickers, entities, or aliases into JOO subject ids.
21. Invent a secrets-vault product or persist tokens in envelopes.
22. Share secrets into payloads, IRO, domain packages, or producers.
23. Absorb Automation M1–M3 as a runtime dependency.
24. Modify IRO or Automation runtime architecture.
25. Authorize implementation, commit, tag, or push by the existence of this
    document.

---

## 20. Implementation authorization status

### 20.1 Architecture questions (explicitly decided)

| # | Question | Decision |
| --- | --- | --- |
| 1 | Additive or greenfield? | **Additive** occupation of reserved `kb_open_api.py` inside existing `ProviderGateway` |
| 2 | Provider Interface attachment | One interface intent; path-specific request types; justified `collect` union; no second interface; no dummy market fields |
| 3 | Broker request / binding / transport | `ExplicitBrokerCollectRequest`, `ExplicitBrokerAdapterBinding`, `ExplicitBrokerParameterProfile`, `BrokerTransport` |
| 4 | First-slice read surface | **IN:** `holdings`, `balances`, `account_state`. **OUT:** read-only orders, read-only fills |
| 5 | Envelope | Reuse `ExplicitProviderPayloadEnvelope`. No second envelope type. No new required fields. |
| 6 | Source class | Broker success = `broker_fact`. Market success = `market_fact`. No retagging. |
| 7 | Provider id | Broker = `"kb_open_api"` only. Market continues to reject that id. |
| 8 | Auth / clock / secrets | Reuse `CredentialSupplier` and `UtcClock`. No vault. Auth failure = `AUTH_FAILURE`. No secret persistence. |
| 9 | Transport | New `BrokerTransport`. Do not reuse `MarketTransport`. Reuse path-neutral result types. |
| 10 | Health / failure | Reuse existing classes and builders. No invented broker or market facts. |
| 11 | FactStore | Handoff only. No Gateway append. No FactStore code change. |
| 12 | Market / PF-M4 / Market\* | Isolated and unchanged. |
| 13 | Mutation allowlist | §16. Occupies reserved adapter file plus listed additive files. |
| 14 | Trading writes | Forbidden. This slice is read-only ingress. |
| 15 | Implementation authorization | **Not authorized** |

### 20.2 This document does NOT authorize

- `KbOpenApiAdapter` production code or tests
- any mutation listed in §16
- FactStore changes
- MarketSnapshotProducer changes
- Market\* changes
- PF-M3 production
- PF-M5
- IRO or Automation changes
- commit / tag / push
- credentials vaults or run artifacts
- any change to committed files
- any change to the two out-of-boundary untracked documents listed in §1

**Implementation authorization status: NOT AUTHORIZED.**

---

## 21. Residual risks

| Risk | Severity | Mitigation in this freeze |
| --- | --- | --- |
| Treat original PF-M1 as a greenfield implementation license | High | §2.4 / §4 additive ruling |
| Reuse `ExplicitMarketAdapterBinding` with dummy venue fields | High | §5 design 4 rejected; §7.5 |
| Add a second interface or package | High | §5 design 3 rejected; §4.3 |
| Leave first-slice kinds to implementation | High | §9 closed vocabulary and inclusion table |
| Include orders / fills silently as “related facts” | High | §9.2 explicitly OUT |
| Merge multiple kinds, accounts, or books into one envelope | High | §6.3 / §7.2 / §8.4 |
| Retag `broker_fact` / `market_fact` | High | §11 / §12 / §15 |
| Change `MarketApiAdapter` to accept the union at runtime | High | §5.5; market adapter unchanged |
| Gateway appends to FactStore | High | §14 |
| Begin PF-M3 or PF-M5 inside this slice | High | §18 / §19 |
| Invent holdings / balances / account state on outage | High | §13 |
| Persist tokens or invent a vault | High | §10 |
| Import Market\* or construct Portfolio\* at ingress | High | §15 / §19 |
| Treat this document as implementation license | High | §20 |
| Extra wire fields treated as first-slice products | Medium | §9.5 |
| Private ingress helper widened in a way that changes market outcomes | Medium | §8.5 / §16.3 |
| README / absence tests inverted without preserving market assertions | Medium | §16.5 |
| Later caller infers holdings vs balances from payload shape | Medium | `request_kind` is explicit at collect; later PF-M3 must use explicit bindings, not Gateway inference |

No architecture conflict was found with frozen PF-M1 identity, the frozen
market-adapter path, FactStore `broker_fact` eligibility, PF-M3, PF-M4, or
Market\*.

This document is created as **exactly one new untracked file**:

`docs/provider/PF_M1_KB_OPENAPI_BROKER_FIRST_SLICE_ADDITIVE_ARCHITECTURE.md`

- Do **not** commit.
- Do **not** stage.
- Do **not** tag.
- Do **not** push.
- Do **not** modify any other path.

Leave this architecture file untracked pending a later, separately authorized
commit review.

---

**PF-M1 KB OPEN API BROKER FIRST SLICE ADDITIVE ARCHITECTURE AUTHORED**
