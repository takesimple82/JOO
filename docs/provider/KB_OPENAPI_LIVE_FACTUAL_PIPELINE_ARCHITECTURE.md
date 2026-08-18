# KB OpenAPI Live Factual Pipeline Architecture

## Status and identity

- Status: Architecture remediations after KB sample-package TR mapping
  review; first-slice operational-value freeze only; ready for
  independent re-review
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Provider & Fact** (Layer 2 live transport occupying the already
  accepted `BrokerTransport` port)
- Opaque unnumbered identity: **KB OpenAPI Live Factual Pipeline**
- Owner package: **`ProviderGateway`**
- This document does **not** invent or assign `PF-M6`, `KB-M1`, `M55+`,
  `Automation-M4`, `Autopilot-M1`, `PF-M5`, `Automation-M3`, `IRO-M3`,
  `IRO-M4`, Architecture State Resolver, or any other manufactured
  successor identity
- Authorizing previous decisions:
  - `~/JOO-Automation/results/catalog_identity_grant_membership_authorization_review/latest.md`
    — **FINAL DECISION: ZERO-IDENTITY CIA REMAINS CORRECT**
  - `~/JOO-Automation/results/kb_openapi_sample_package_tr_mapping_review/latest.md`
    — **FINAL DECISION: KB SAMPLE MAPPING VERIFIED — ARCHITECTURE
    REMEDIATION REQUIRED**. Remediations R1–R10 from that review and the
    authorized remediations prompt are incorporated in this freeze text
- This document is a **JOO-scoped** operational architecture. It is **not**
  a `JOO_AUTOMATION` catalog grant, not a selector/catalog/CIA change, and
  not an Autopilot membership action
- Repository boundary for this document: architecture remediations only;
  this document alone authorizes no production code, test, package change,
  schema module, configuration, secret file, live KB call, live Autopilot
  run, or Git history mutation

This document freezes the **smallest lawful production path** that converts
already-accepted JOO Provider / Fact infrastructure from injected / fake
transport capability into a real KB Securities Open API read path:

```text
operator-supplied KB credentials
        │
        ▼
ephemeral OAuth Access Token
        │
        ▼
SSQM2952  (domestic holdings / valuation inquiry; READ-ONLY)
        │
        ▼
existing BrokerTransport result
        │
        ▼
existing KbOpenApiAdapter / Provider Gateway envelope
        │
        ▼
existing FactStore append by a rightful caller
        │
        ▼
later additive normalization  (OUT OF THIS SLICE)
        │
        ▼
already-accepted Snapshot producers  (unchanged; not raw-KB consumers)
```

```text
FIRST LIVE FACT:
SSQM2952
```

It does **not** create more selector, catalog, or CIA infrastructure.

It does **not** redesign accepted Gateway, FactStore, or Snapshot public
contracts.

It does **not** claim that the raw SSQM2952 envelope is
PortfolioSnapshot-ready.

Implementation requires a separate authorization after independent
re-review of this remediations text. This remediations does **not**
authorize that implementation.

---

## Normative first-slice surface (must remain explicit)

### This freeze implements ONLY

| # | Responsibility |
| --- | --- |
| 1 | **Concrete live `BrokerTransport`** for KB Securities Open API |
| 2 | **Official OAuth Client Credentials** token acquisition and one lawful re-issuance path |
| 3 | **Injectable live HTTP** behind the already-accepted transport port |
| 4 | **Read-only mapping** of one accepted `request_kind` (`holdings`) plus one `account_selector` onto the verified first live fact **SSQM2952** (`POST /api/v1/ssqm2952`) |
| 5 | **Reuse** of `KbOpenApiAdapter`, the immutable `broker_fact` envelope, and existing failure / health classes |
| 6 | **Secret redaction** so `appKey`, `appSecret`, Access Tokens, and other SECRET names never enter envelopes, FactStore, Snapshots, logs, or AI |
| 7 | **Fake-HTTP testability** so CI never requires real KB credentials |
| 8 | **Documented FactStore handoff recipe** for a rightful later caller; transport does not become the store |
| 9 | **Raw KB evidence preservation** inside the existing `broker_fact` envelope; OAuth/token responses are never stored as facts |
| 10 | **KB business-error handling** via `processFlag` / process code / business message; HTTP success alone is insufficient |

### This freeze does NOT implement

| Concern | Owner (elsewhere) |
| --- | --- |
| **Provider Interface / KbOpenApiAdapter public collect contract** | Frozen PF-M1 broker-first slice — reused, not redesigned |
| **FactStore append / eligibility / retrieval** | Frozen PF-M2 / `FactStore` — caller appends |
| **Portfolio Snapshot production** | Frozen PF-M3 / `PortfolioSnapshotProducer` — unchanged |
| **Raw SSQM2952 → PF-M3 holdings projection** | Later additive normalization slice — **not this transport slice** |
| **Market Snapshot production** | Frozen PF-M4 / `MarketSnapshotProducer` — unchanged |
| **Market API Adapter / `MarketTransport` live client** | Later live-market slice, if separately authorized |
| **Selector / catalog / CIA / Autopilot / Supervisor** | JOO_AUTOMATION plane — not this work |
| **Architecture State Resolver** | Deferred; not a prerequisite |
| **PF-M5 Market Watch** | Not a substitute for live facts |
| **IRO-M3 / IRO-M4 / CIO capital allocation** | Later research / capital planes |
| **Order placement / modify / cancel / autonomous trading** | Layer 15 BX-M1 + Human Approval |
| **Secret-management platform / token vault** | Never this slice |
| **Third-party brokers** | Not authorized |
| **Domestic cash / buying-power / overseas / realized-P&L TRs** | Later additive slices; documented only |
| **OAuth token-request serialization variant** | Source-conflicted; Implementation Boundary Review must resolve |

---

## 1. Repository checkpoint

Verified immediately before remediations. Remediation does not proceed from
an unverified checkpoint.

### JOO

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| Path | `/Users/takesimple/Projects/JOO` | `/Users/takesimple/Projects/JOO` | Match |
| Branch | `feature/stage2-provider-runtime` | `feature/stage2-provider-runtime` | Match |
| HEAD | `3f8b0ffa8f7eb12fdad1dd3d07c92e56e1af973a` | Exact | Match |
| Exact tag at HEAD | `v7.18-stage5-catalog-identity-authorization-architecture` | Lightweight tag at HEAD (`git tag --points-at HEAD`; `git describe --tags --exact-match HEAD`) | Match |
| Subject | `Add Catalog Identity Authorization architecture` | Exact | Match |
| Tracked tree | Clean | Clean | Match |
| Staged set | Empty | Empty | Match |
| Authorized mutation | this architecture file only | Exact this file | Match |

**Preserved out-of-boundary untracked files (read-only; not modified, not
staged):**

- `docs/JOO_PRODUCT_ARCHITECTURE.md`
- `docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md`

**Authorized remediations target (untracked; the only JOO file this
remediations may modify):**

- `docs/provider/KB_OPENAPI_LIVE_FACTUAL_PIPELINE_ARCHITECTURE.md`

### JOO-Automation

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| Path | `/Users/takesimple/JOO-Automation` | Exact | Match |
| Branch | `main` | Exact | Match |
| HEAD | `4e227411080276a71e5a9af0870618b7d391772e` | Exact | Match |
| This document | Must not modify JOO-Automation | Not modified | Match |

Checkpoint status: **Pass**. Not REVIEW BLOCKED.

---

## 2. Previous decisions consumed

### 2.1 Catalog Identity Grant / Membership Authorization Review

That review ended:

**ZERO-IDENTITY CIA REMAINS CORRECT**

That review is consumed here as sequencing authority only. It is **not** a
JOO_AUTOMATION membership grant and does **not** authorize Autopilot,
catalog overwrite, implementation, commit, tag, or push.

Consumed conclusions that this freeze obeys:

1. The missing operational capability is JOO-scoped live authenticated KB
   fact collection.
2. No additional JOO_AUTOMATION selector / catalog / CIA work is required
   first.
3. Architecture State Resolver is not required first.
4. PF-M5 is not the correct substitute.
5. Automation-M3 is not the correct substitute.
6. The next architecture belongs in JOO.
7. Use an unnumbered operational identity. Do not invent `PF-M6` /
   `KB-M1` / `M55+`.

### 2.2 KB Sample Package TR Mapping Review

That review ended:

**KB SAMPLE MAPPING VERIFIED — ARCHITECTURE REMEDIATION REQUIRED**

It is consumed here as the authoritative factual-surface review. The
operator-supplied sample package contained **95 JSON files** and, together
with the official Excel catalog, proved the holdings / cash / buying-power
/ valuation / P&L / domestic-overseas / order surface.

Consumed conclusions that this remediations incorporates:

1. **FIRST LIVE FACT is `SSQM2952`.** The prior `UNRESOLVED` freeze is
   closed and must not remain in this text.
2. `SSQM1802` is a **READ** (매수주문가능금액). It is **not** an order
   mutation and must not be forbidden as if it executed an order.
3. `SSAM1802` is the domestic **BUY MUTATION**. `SSAM*` and `SSQM*`
   families must not be blurred.
4. OAuth **path**, Client Credentials, Bearer, and `expires_in` are
   agreed. Token **request serialization is source-conflicted** and must
   not be frozen to the public-guide example alone.
5. The raw SSQM2952 body is valid factual evidence and is **not**
   PF-M3-ready. `dataBody.Record1[].hld_q` is nested; PF-M3
   `quantity_payload_key` is top-level and one stored fact per holding
   binding.
6. Domestic and overseas are payload-proven as distinct TR families.
7. Order mutations remain forbidden for the first slice.
8. Do not implement. Re-review this remediations text before any
   implementation authorization.

---

## 3. Official KB documentation and sample-package verification

Official sources inspected before any endpoint or authentication field was
frozen, plus the sample package that closed the prior UNRESOLVED TR gap:

| Source | URL / locator | Use in this freeze |
| --- | --- | --- |
| KB Open API development guide | https://openapi.kbsec.com/guide_b2c | Authoritative for protocol, token lifecycle, error classes, production host, and the **public-guide** token-request example. **Not** sole authority for token-request serialization |
| KB Open API document catalog | https://openapi.kbsec.com/apidoc_b2c | Authoritative for official family split (`OAuth인증`, `국내주식`, `해외주식`) and for the existence of Excel / JSON specification downloads |
| KB Open API service introduction | https://openapi.kbsec.com/about_b2c | Authoritative that the service includes 시세, 종목, 계좌, 잔고, 주문, 체결 |
| KB Open API howto | https://openapi.kbsec.com/howto_b2c | Authoritative that a KB account, Open API application, and `appKey` / `appSecret` issuance are prerequisites |
| Operator-supplied KB sample package | 95 JSON samples independently reviewed; not stored in this repository | Authoritative for proven TR paths, request/response envelopes, `SSQM2952` as first live fact, `SSQM1802` as buying-power READ, and `SSAM*` as domestic order mutations |
| Official Excel catalog (field names / Korean titles) | operator-supplied companion to the sample package | Second witness for TR titles and field names; not used to invent semantics absent from JSON |

Independent news confirmation that the personal Open API open-beta includes
domestic / overseas quote inquiry, order / modify / cancel, balance inquiry,
and fill inquiry is **not** used to invent TR codes. It only corroborates
that official account-fact and market-fact families exist as separate later
bindings.

### 3.1 Independently agreed authentication and transport facts

The official development guide **and** the sample package independently
agree on all of the following:

| Fact | Independently agreed value |
| --- | --- |
| Protocol | HTTPS |
| Body format | JSON |
| Character set | UTF-8 |
| Content-Type | `application/json` |
| Authentication | Bearer Token |
| Client credentials | `appKey` and `appSecret` |
| OAuth grant | OAuth Client Credentials |
| Token path | `POST /oauth2/token` |
| Token logical inputs | `appKey`, `appSecret`, client-credentials grant |
| Token response fields | `access_token`, `token_type = Bearer`, `expires_in` |
| Documented `expires_in` example | `86400` |
| Authenticated call header | `Authorization: Bearer <access_token>` |
| Token expiry rule | Access Token has a validity period; on expiry it must be re-issued and then used. One bounded re-issuance + one retry, then fail closed. No refresh-token product |
| Production host | `https://developer.kbsec.com:32484` |
| Documented API-call shape for TR reads | `POST /api/v1/{tr_code}` with JSON `dataHeader` / `dataBody` |
| First live fact | **`SSQM2952`** — 잔고현황 조회(체결기준) — `POST /api/v1/ssqm2952` — **READ-ONLY** |

Official token-issuance validation items include: `appKey` validity,
`appSecret` match, API-use application, app usability, API authority,
account authority, call-limit policy, and service-termination status.

Official error-handling classes include:

| Official class | Official guidance | JOO mapping |
| --- | --- | --- |
| Token 만료 | Re-issue token, then retry the call | One lawful re-issuance + one retry; then fail closed |
| 권한 없음 | Confirm API application scope and app state | `AUTH_FAILURE` or `PROVIDER_ERROR`; no invented facts |
| 계좌 권한 없음 | Confirm account and account-link state | `AUTH_FAILURE` or `PROVIDER_ERROR`; no invented facts |
| 호출 제한 초과 | Retry after a wait or inspect call volume | `RATE_LIMITED`; **no automatic retry storm** |
| 필수값 누락 | Confirm request header and body | `VALIDATION_FAILURE` or `PROVIDER_ERROR` |
| 주문 불가 | Orderable amount / quantity / instrument state | **Out of this slice.** This freeze is read-only |

### 3.2 Independently verified catalog split

The official API document page groups APIs into at least:

- `OAuth인증`
- `국내주식`
- `해외주식`

The sample package independently confirms the same split at the TR-family
level (`SSQM*` / `SWQ*` domestic account; `SPQM*` / `SPQO*` / `SKQM*`
overseas account; `IVU*` / `IVS*` domestic market; `GS*` overseas market;
`SSAM*` domestic order mutations). This freeze therefore treats
**domestic and overseas** as separate official API families. One endpoint
is **not** assumed to cover both.

### 3.3 Token request serialization — SOURCE-CONFLICTED

```text
TOKEN REQUEST SERIALIZATION:
SOURCE-CONFLICTED — IMPLEMENTATION BOUNDARY MUST RESOLVE
```

Public guide and operator-supplied KB samples **disagree** on token
request serialization. This remediations does **not** freeze one variant
as unquestionably authoritative.

| Source | Request grant key | Wrapper |
| --- | --- | --- |
| Public guide (https://openapi.kbsec.com/guide_b2c) | `grant_type` | flat JSON body |
| Official Excel field list | `grantType` | field list only; no `dataHeader` |
| JSON sample `token.json` | `grantType` | `dataHeader` / `dataBody` |

**Candidate A:** flat body + `grant_type`

**Candidate B:** `dataHeader` / `dataBody` + `grantType`

Independently agreed OAuth semantics remain frozen (§3.1, §10):

- `POST /oauth2/token`
- Client Credentials
- required logical inputs: `appKey`, `appSecret`, client-credentials grant
- response: `access_token`, `token_type = Bearer`, `expires_in`
- production host: `https://developer.kbsec.com:32484`
- `Authorization: Bearer <access_token>`
- token is process-local only
- on expiration: one bounded re-issuance + one retry, then fail closed
- no refresh-token product

Serialization detail **must** be frozen during Implementation Boundary
Review using, in this order:

1. operator-supplied KB sample package;
2. current official KB guide;
3. controlled fake-HTTP tests;
4. and if still necessary, a later controlled pilot.

Production code must **not** silently guess or fall back between Candidate
A and Candidate B unless a later implementation authorization explicitly
permits a bounded compatibility behavior.

### 3.4 SSAM vs SSQM — retracted guide-label error

The public guide labels `POST /api/v1/ssqm1802` as **주문 API 호출 예시**.
That label is **not** a mutation classification.

The sample request/response and the Excel title prove:

| Identifier | Official / proven meaning | Class | First-slice status |
| --- | --- | --- | --- |
| **SSQM1802** | 매수주문가능금액 — domestic buying-power / buy-orderable-amount inquiry | **READ** | Later `broker_fact` candidate. **Not** the first live fact. **Not** an order mutation |
| **SSAM1802** | 매수 — domestic buy order | **BUY MUTATION** | **Forbidden** for the read-only first slice |

Do **not** blur `SSAM*` and `SSQM*` families.

`SSQM1802` must **not** be described as an order mutation API and must
**not** be forbidden because it executes an order. It does not.

Typical `SSQM1802` factual fields include: `ordr_psbl_csh`,
`ordr_psbl_tl_amt`, `pcnt100_ordr_psbl_amt`, `mx_ordr_psbl_amt`, `tfnd`,
`do_psbl_csh`.

Actual domestic order mutations remain forbidden for this slice:

- `SSAM1801` (매도)
- `SSAM1802` (매수)
- `SSAM1805` (정정)
- `SSAM1806` (취소)
- `SSAM0831` (예약접수)
- `SSAM5762` / `SSAM5763` / `SSAM5764` (소수점)

### 3.5 What the sample package resolved

The prior architecture left the first account-fact TR **UNRESOLVED**
because interactive apidoc / Excel / JSON downloads were not retrieved
during the original authoring step. The subsequent sample-package review
closed that gap.

This remediations therefore:

1. **Freezes** `SSQM2952` as the first live fact. Path
   `POST /api/v1/ssqm2952`. Official meaning: 잔고현황 조회(체결기준) —
   domestic account holdings / valuation inquiry. It is READ-ONLY.
2. **Retracts** every statement that `SSQM1802` is an order mutation or
   must be forbidden because it executes an order.
3. **Does not invent** additional request fields for `SSQM2952` beyond
   the sample/catalog contract in §12.
4. **Does not** bind later cash, buying-power, overseas, market, realized
   P&L, or order TRs in this slice.
5. Leaves token-request **serialization** source-conflicted (§3.3).
6. Leaves the **test-environment host** UNRESOLVED (§3.6).

A later implementation authorization may bind **only** the frozen first
live read `SSQM2952` (plus the agreed OAuth token path, after
serialization is resolved). Until that separate implementation
authorization exists, no live account-fact HTTP call is authorized.

### 3.6 Test-environment host

The official guide states that operating and test environments are distinct
and that connection information may differ by environment. The public guide
page independently listed only the **operating** host
`https://developer.kbsec.com:32484`. The test-environment host remains
**UNRESOLVED** and must not be invented.

---

## 4. Existing JOO factual-pipeline inventory

Inspected accepted tracked implementation and accepted architectures. Tags
are implementation inventory only, not membership or completion
attestation.

| Capability | Accepted state | What it actually does |
| --- | --- | --- |
| PF-M1 Provider Gateway | Architecture accepted; package `ProviderGateway` present | Common Provider Interface, immutable envelope, source-class taxonomy, health / failure signaling |
| PF-M1 KB broker additive | Architecture + implementation accepted | `KbOpenApiAdapter` occupies `adapters/kb_open_api.py`. `provider_id = "kb_open_api"`. Success class = `broker_fact`. First-slice kinds = `holdings`, `balances`, `account_state` |
| Market adapter path | Architecture + implementation accepted | `MarketApiAdapter` + `MarketTransport`. Success class = `market_fact`. Rejects `provider_id == "kb_open_api"` |
| `BrokerTransport` | Accepted injected port | `read(binding, credential: str, request)` and `probe(binding)`. Tests use fakes. **No accepted live KB HTTP / OAuth client** |
| `MarketTransport` | Accepted injected port | Market-only. Not this slice |
| `CredentialSupplier` | Accepted injected port | `credential_ref -> object`; Gateway resolver requires nonblank `str`. Secrets are outbound-only. No vault. No token cache. No persisted OAuth product |
| Envelope | `ExplicitProviderPayloadEnvelope` | `envelope_id`, `provider_id`, `source_class`, `collected_at`, `status`, `payload`, `error_diagnostics`, `request_correlation_id` |
| Binding | `ExplicitBrokerAdapterBinding` | `provider_id`, `credential_ref`, `ExplicitBrokerParameterProfile(profile_id, account_selector, request_set)` |
| Collect request | `ExplicitBrokerCollectRequest` | One `request_kind` per attempt. One account selector per binding |
| PF-M2 FactStore | Architecture + implementation accepted | Append-only store. Eligible classes: `broker_fact`, `market_fact`. Does not call Gateway or HTTP |
| PF-M3 Portfolio Snapshot | Architecture + implementation accepted | Composes holdings / watchlist from **caller-named stored** `broker_fact` ids. Does not collect from KB. Cash / balances / `account_state` are out of first-slice composition. `quantity_payload_key` is a **top-level** payload key on **one stored fact per holding binding** |
| PF-M4 Market Snapshot | Architecture + implementation accepted | Same pattern for stored `market_fact`. Does not collect from market HTTP |
| IRO-M1 / IRO-M2 | Accepted | Coordinates research from a caller-supplied snapshot. Scanner does not retrieve live holdings |
| `AIAdapter` HTTP | Accepted research-AI transport | Completions only. **Not** KB factual truth and **not** reusable as the KB live client |

There is **no** accepted production caller that does:

```text
KB Open API → live collect → FactStore.append → Snapshot.produce
```

Current Snapshot producers consume already-stored facts. They must not be
redesigned by this freeze. They also must **not** be treated as consumers
of a raw `dataHeader` / `dataBody` / `Record1[]` KB envelope.

---

## 5. Exact operational gap

The structural JOO pipeline already exists:

```text
injected BrokerTransport
        │
        ▼
KbOpenApiAdapter / collect_broker_attempt
        │
        ▼
broker_fact envelope or first-class failure
        │
        ▼
FactStore.append by a rightful caller
        │
        ▼
PortfolioSnapshotProducer / MarketSnapshotProducer
```

The missing operational capability is the **live authenticated KB fact
source**:

1. authenticate to KB Securities Open API with operator-injected `appKey` /
   `appSecret`;
2. obtain an ephemeral Access Token;
3. perform the verified read-only first live fact `SSQM2952`
   (`POST /api/v1/ssqm2952`);
4. return a structured `BrokerTransport` success or a fail-closed
   business / transport / auth failure;
5. let the already-accepted adapter emit a `broker_fact` envelope that
   may preserve the raw KB response as evidence;
6. let a rightful caller append that envelope to FactStore.

This freeze occupies that gap. It does not reopen PF-M1 identity, does not
rebuild FactStore, and does not change Snapshot producers.

This freeze does **not** occupy the later additive gap of projecting
`dataBody.Record1[]` rows into Snapshot-compatible one-fact-per-holding
records.

---

## 6. Owner and opaque identity

### 6.1 Owner

| Field | Decision |
| --- | --- |
| Owner package | **`ProviderGateway`** |
| Plane | Provider & Fact |
| Additive capability | Live KB Open API `BrokerTransport` implementation |
| Not the owner | Milestone Selection Engine, Selector Input Supply, CIA, Supervisor, Autopilot, Architecture State Resolver, CIO, Research Committee, FactStore, Snapshot producers, Repository Target, Runtime Integration, COMMIT READY, `next_action` |

`ProviderGateway` already owns ingress, the KB adapter, the broker
transport **port**, and credential **use**. This freeze occupies the
already-accepted injected port. It does not move ownership to automation,
research, or capital planes.

Preferred later ownership of holdings-row normalization: a rightful-caller
or adapter-adjacent projection **before** KB vendor structure reaches
Portfolio Snapshot or CIO. **Do not** put `dataBody` / `Record1` parsing
into CIO. That later slice is **not** this remediations and is **not**
authorized now.

### 6.2 Opaque unnumbered identity

**Exact identity string:**

```text
KB OpenAPI Live Factual Pipeline
```

This identity names the operational capability, not a roadmap rank.

Rejected manufactured identities:

- `PF-M6`
- `KB-M1`
- `M55+`
- `Automation-M4`
- `Autopilot-M1`

### 6.3 Additive-versus-new-package ruling

| Option | Verdict |
| --- | --- |
| **Additive live transport inside existing `ProviderGateway`** | **Selected and frozen** |
| New package (`KbLiveTransport`, `BrokerGateway`, `KbGateway`, `FactualPipeline`, `LiveCollector`) | **Rejected** — second ingress / collection plane |
| Relocate live HTTP into `FactStore` | **Rejected** — store becomes a second Gateway |
| Relocate live HTTP into `PortfolioSnapshotProducer` | **Rejected** — PF-M3 does not collect |
| Relocate live HTTP into `AIAdapter` | **Rejected** — research-AI transport is not KB factual truth |
| Reopen PF-M1 as the live-HTTP identity | **Rejected** — live vendor HTTP was an explicit PF-M1 non-responsibility |

### 6.4 Layout intent (additive; not a scaffold)

```text
ProviderGateway/
  adapters/
    kb_open_api.py                         # frozen adapter; unchanged public collect
    kb_openapi_live_broker_transport.py    # THIS freeze occupies the live port
    ports.py                               # BrokerTransport unchanged
  auth/
    credentials.py                         # additive official secret field names only
```

This document does **not** create any of those files.

---

## 7. Required architecture questions

| # | Question | Decision |
| --- | --- | --- |
| 1 | What exact existing JOO port should the live KB transport implement? | **`BrokerTransport`** in `ProviderGateway.adapters.ports` |
| 2 | What exact accepted Gateway / Adapter is reused? | **`KbOpenApiAdapter`** plus `collect_broker_attempt` / `observe_broker_health` |
| 3 | What authentication boundary is needed? | Official OAuth Client Credentials **inside the live transport**. Gateway continues to supply one outbound credential string through `credential_ref` |
| 4 | Where do `appKey` / `appSecret` enter? | Runtime only, through the existing `CredentialSupplier` / `credential_ref` handle, decoded transport-locally into official token-request fields |
| 5 | Where may they never appear? | Git, architecture docs, prompts, fixtures as real secrets, logs, exceptions, selector input, envelope `payload`, diagnostics, FactStore, Snapshots, IRO, CIO, research AI |
| 6 | How is Access Token lifecycle handled? | Process-local ephemeral cache; official `expires_in`; one re-issue + one retry; fail closed; never persist |
| 7 | What is the smallest independently verified KB account endpoint for the pilot? | **`SSQM2952`.** Official 잔고현황 조회(체결기준). Path `POST /api/v1/ssqm2952`. READ-ONLY. Not an order TR |
| 8 | Which official KB document proves it? | Operator-supplied sample package (95 JSON) + official Excel catalog, independently reviewed in `kb_openapi_sample_package_tr_mapping_review`. Public guide proves OAuth path / Bearer / `expires_in` but is source-conflicted on token-request serialization |
| 9 | What exact response fields matter to Portfolio Facts? | Raw SSQM2952 body is opaque evidence inside `broker_fact`. Important fields are frozen in §12.5 for contract and audit. They are **not** PF-M3-ready. Do not invent JOO field names as Gateway products |
| 10 | Does domestic vs overseas require separate APIs? | **Yes.** Official catalog and sample package split `국내주식` / `해외주식`. Distinct TRs. Do not merge schemas |
| 11 | Is market fact retrieval in slice 1 or later? | **Later.** `MarketTransport` is a separate accepted port. Domestic `IVU*`; overseas `GS*` |
| 12 | Who appends to FactStore? | A **rightful later caller**, not the transport and not Gateway |
| 13 | Does any existing public API need to change? | **No.** `ProviderInterface.collect`, envelope fields, FactStore append, and Snapshot `produce` remain unchanged |
| 14 | What failure conditions are fail-closed? | Missing / invalid credentials, OAuth failure, token re-issue failure, KB HTTP errors, **KB `processFlag` business failure**, malformed JSON, rate limit, residual secret leakage. Do **not** return empty holdings on a KB business error |
| 15 | How is freshness represented? | Reuse envelope `collected_at` and FactStore `appended_at`. KB `processTime` may remain inside raw provider evidence. No new freshness schema. Token `expires_in` is not fact freshness |
| 16 | How is source identity represented? | Reuse `provider_id = "kb_open_api"` and `source_class = "broker_fact"` |
| 17 | How do we prevent AI interpretation from entering the factual path? | No LLM, no prose parsing, no research-AI transport reuse, `research_ai` never appends. Do not put `dataBody` / `Record1` parsing into CIO |
| 18 | How do we test without real secrets? | Fake HTTP + fake OAuth material. CI must not require real `appKey` / `appSecret` |
| 19 | What later controlled real-KB pilot is required? | Separately authorized, read-only, manual, bounded, **SSQM2952 only** for first live account proof. No order TR. No retries beyond the frozen bounded OAuth rule. No secret output. No automatic portfolio action. **Not authorized by this remediations** |
| 20 | What exact next implementation boundary follows if re-review accepts this text? | Concrete `KbOpenApiLiveBrokerTransport` + OAuth token client + **source-conflicted token serialization resolved before production** + SSQM2952 request/response binding + business-error handling + fakeable HTTP + injectable clock + additive secret redaction + fake-HTTP tests + raw `broker_fact` evidence handoff. **No** snapshot normalization, market transport, overseas transport, orders, CIO, or selector/catalog/CIA changes. **Do not implement now** |

---

## 8. Existing port and Gateway reuse

### 8.1 Port

The live implementation must satisfy the already-accepted port exactly:

```text
BrokerTransport
  read(binding: ExplicitBrokerAdapterBinding,
       credential: str,
       request: ExplicitBrokerCollectRequest)
      -> ExplicitTransportSuccess | ExplicitTransportFailure
  probe(binding: ExplicitBrokerAdapterBinding)
      -> ExplicitHealthProbe | ExplicitTransportFailure
```

Do **not** implement `MarketTransport` in this slice.

Do **not** change the port signature.

Do **not** add a second collect method on `ProviderInterface`.

### 8.2 Adapter reuse

`KbOpenApiAdapter.collect` remains the only public collect surface for the
KB broker path.

The already-accepted sequence stays intact:

```text
ExplicitBrokerCollectRequest
        │
        ▼
validate_explicit_broker_collect_request
        │
        ▼
resolve_outbound_credential(credential_ref)
        │
        ▼
BrokerTransport.read(...)
        │
        ▼
project_opaque_payload + secret leakage check
        │
        ▼
ExplicitProviderPayloadEnvelope
  provider_id  = "kb_open_api"
  source_class = "broker_fact"
  collected_at = injected UTC clock
```

This freeze occupies `BrokerTransport`. It does not rewrite
`collect_broker_attempt` control flow except where a later implementation
authorization proves that official secret-field names must be added to
`SECRET_FIELD_NAMES`.

`project_opaque_payload` is **top-level key only**. It does not recurse
into `dataBody`. Therefore:

- the raw SSQM2952 envelope `{dataHeader, dataBody}` is lawful evidence
  and is **not** a PF-M3 holding row;
- token responses must **never** be stored as facts, because a nested
  `access_token` would not be stripped.

### 8.3 Why the existing port is sufficient

PF-M1 already froze that exact HTTP client, SDK, and vendor URL map were
**not** Gateway products and that transport may use the supplied secret to
obtain an ephemeral access token for one read or probe. That deferred
responsibility is the entire point of this slice.

The accepted adapter already:

- fails closed on missing credentials (`AUTH_FAILURE`);
- maps transport failure classes through the existing vocabulary;
- projects secret field names out of payload;
- rejects residual secret leakage as `VALIDATION_FAILURE`;
- does not append to FactStore.

A new Gateway public API is therefore unnecessary.

---

## 9. OAuth / credential contract

### 9.1 Reuse, do not invent a secrets platform

| Question | Decision |
| --- | --- |
| Credential handle | Reuse `ExplicitBrokerAdapterBinding.credential_ref` |
| Supply port | Reuse `CredentialSupplier` |
| Gateway resolver | Reuse `resolve_outbound_credential` — still requires nonblank `str` |
| Vault / secret store | **Forbidden** |
| Access Token persistence | **Forbidden** in this slice |
| Write / trading credentials | **Out of this slice** |

### 9.2 Official client material versus Access Token

The outbound credential string supplied to `BrokerTransport.read` is
**OAuth client material**. It is **not** the Access Token.

Official token issuance requires two fields:

- `appKey`
- `appSecret`

The accepted port still passes one `str`. This freeze therefore authorizes a
**transport-local decoder** that extracts official `appKey` and `appSecret`
from that one outbound string.

Rules:

1. The decoder is local to the live transport. It is not a new Gateway
   collect field and not a FactStore field.
2. The decoder may understand only official field names `appKey` and
   `appSecret`.
3. Missing, blank, or unparseable material is `AUTH_FAILURE`.
4. The exact encoding of the two official fields into one injected string is
   an implementation-authorization detail. This architecture does **not**
   publish a secret example and does **not** put real values in fixtures.
5. Tests use fake material only.
6. Changing `BrokerTransport.read` to take a structured credential object is
   **not** authorized. The accepted port stays `credential: str`.

### 9.3 Where secrets enter

```text
operator runtime injection
  (environment / external secret injection / process start)
        │
        ▼
CredentialSupplier(credential_ref) -> nonblank str
        │
        ▼
collect_broker_attempt
        │
        ▼
live BrokerTransport decoder
        │
        ├── appKey     -> POST /oauth2/token only
        └── appSecret  -> POST /oauth2/token only
                │
                ▼
ephemeral Access Token
                │
                ▼
Authorization: Bearer <token>
```

`appKey` and `appSecret` are injected at runtime. They are never committed.

### 9.4 Where secrets may never appear

Real `appKey`, `appSecret`, Access Tokens, and decoded client material must
**never** be:

- committed to git;
- written into architecture documents;
- written into prompts;
- written into test fixtures as real values;
- written into logs;
- placed in selector input;
- placed in envelope `payload` or `error_diagnostics`;
- placed in FactStore records;
- placed in Portfolio Snapshot or Market Snapshot;
- sent to AI committees, IRO, CIO, or research execution;
- included in exception messages;
- included in raw request / response evidence retained as facts.

OAuth / token responses themselves must **never** be stored as facts.

### 9.5 Additive secret-field names

Existing `SECRET_FIELD_NAMES` / FactStore
`FORBIDDEN_PAYLOAD_SECRET_FIELD_NAMES` already include `token`,
`access_token`, `refresh_token`, `secret`, `authorization`, `api_key`, and
related names. They do **not** currently include the official KB field
names `appKey` and `appSecret`.

This freeze authorizes the smallest additive redaction extension:

```text
appKey
appSecret
```

If later TRs that carry `hts_pwd`, `ac_pwd`, or `hd_pin_no` are ever
touched — they must **not** be, in this slice — those names are also
SECRET (§18). This first slice must not call those TRs.

This is not a new secrets product. PF-M1 already allowed adding a proven
KB-specific secret key name as an implementation-authorization detail.

Gateway projection and FactStore eligibility must both reject those names
if they appear as payload keys.

---

## 10. Token lifecycle

### 10.1 Acquisition

The live transport acquires an Access Token only by the official path:

```text
POST /oauth2/token
Content-Type: application/json
```

against the independently verified production host
`https://developer.kbsec.com:32484`, or against a later-cited official
test host if one is independently documented.

Agreed logical request inputs:

- `appKey`
- `appSecret`
- client-credentials grant

```text
TOKEN REQUEST SERIALIZATION:
SOURCE-CONFLICTED — IMPLEMENTATION BOUNDARY MUST RESOLVE
```

**Candidate A** (public guide):

```text
{
  "grant_type": "client_credentials",
  "appKey": "{appKey}",
  "appSecret": "{appSecret}"
}
```

**Candidate B** (JSON sample / Excel `grantType`):

```text
{
  "dataHeader": {
    "ipAddr": "<operator-injected>",
    "macAddr": "<operator-injected>"
  },
  "dataBody": {
    "appKey": "{appKey}",
    "appSecret": "{appSecret}",
    "grantType": "client_credentials"
  }
}
```

This remediations freezes the **conflict**, not a winner. Implementation
must not ship Candidate A as the only legal key, must not ship a silent
A/B fallback, and must not treat the public-guide example as
unquestionably authoritative. Resolution belongs to Implementation
Boundary Review (§3.3).

### 10.2 Success token use

On a structurally valid token response:

| Field | Rule |
| --- | --- |
| `access_token` | Process-local only. Used solely as `Authorization: Bearer <token>` |
| `token_type` | Must be usable as Bearer. Unknown / non-Bearer type is `AUTH_FAILURE` |
| `expires_in` | Authoritative when present. Example value `86400` is **not** hard-coded as the only legal lifetime. **Not** fact freshness |

If `access_token` is missing, blank, or not a string, the attempt is
`AUTH_FAILURE`.

If `expires_in` is absent or not a usable integer, the token may be used
for **that one in-flight read or probe only** and must **not** be cached.

### 10.3 Process-local cache

Token cache is allowed **only** as process-local state inside the live
transport instance.

| Allowed | Forbidden |
| --- | --- |
| Remember token + expiry in memory for the transport instance | Persist token to disk, git, envelope, FactStore, logs, or config files |
| Reuse a non-expired token for a later `read` / `probe` on the same instance | Share the token into Gateway envelopes or other packages |
| Compute expiry from official `expires_in` and an injected clock | Invent a refresh-token product. Official first-slice token response does not document a refresh token |

A small safety skew before documented expiry is allowed so a token is
re-issued before the provider rejects it. The skew is implementation detail
and must be deterministic under the injected clock.

### 10.4 One lawful re-issuance path

There is exactly one refresh behavior:

```text
need token or token expired or provider reports token expiry / unauthorized
        │
        ▼
POST /oauth2/token once
        │
        ├── failure -> AUTH_FAILURE; stop
        └── success -> retry the original read or probe exactly once
                │
                ├── success -> return structured success
                └── failure -> return that failure; stop
```

Normative limits:

1. At most **one** re-issuance per original `read` / `probe`.
2. At most **one** retry of the original KB request after that re-issuance.
3. No infinite retry loop.
4. No retry storm on `RATE_LIMITED`.
5. Invalid `appKey` / `appSecret` or rejected client credentials are
   `AUTH_FAILURE` with **zero** further token attempts for that call.
6. Auth failure is fail-closed. No synthetic holdings, balances, or
   account state.

### 10.5 Injectable clock

The live transport must accept a deterministic injectable clock for expiry
tests. It may reuse the same `UtcClock` port already accepted by Gateway,
or take an equivalent injected callable. Tests must not depend on wall
clock.

---

## 11. Live HTTP transport contract

### 11.1 Smallest implementation

The concrete live type occupies `BrokerTransport` and no other public
surface.

Recommended later implementation name:

```text
KbOpenApiLiveBrokerTransport
```

Recommended later file:

```text
ProviderGateway/adapters/kb_openapi_live_broker_transport.py
```

Constructor ports, architecture-level:

| Port | Role |
| --- | --- |
| HTTP client | Injected. Fakeable. No exclusive commercial library is frozen |
| Clock | Injected. Deterministic in tests |
| Optional token state | Process-local only |
| Optional client-material decoder | Transport-local. Fakeable |

`AIAdapter.UrllibJSONTransport` must **not** be reused. That client is
research-AI completion transport, not KB factual truth.

### 11.2 HTTP rules

1. HTTPS only.
2. JSON request / response only.
3. UTF-8.
4. `Content-Type: application/json`.
5. Authenticated account-fact calls use `Authorization: Bearer <token>`.
6. One `read` issues at most the token call(s) allowed by §10 plus **one**
   official account-fact call for that `request_kind` and
   `account_selector` — for this slice, **SSQM2952 only** — plus at most
   the single retry in §10.4.
7. Transport must not fan out into other kinds, other accounts, market
   APIs, cash TRs, overseas TRs, or order APIs.
8. Transport must not follow redirects to non-HTTPS targets.
9. Timeouts are required. Timeout is `TRANSPORT_FAILURE`.
10. Malformed JSON is `VALIDATION_FAILURE`, not a success body.

### 11.3 Request serialization boundary

The first live account-fact TR is now cited: **SSQM2952**.

- the live transport may implement **OAuth** against the verified token
  path, after Implementation Boundary Review resolves the
  source-conflicted serialization;
- the live transport may serialize **only** the frozen SSQM2952 request
  in §12.4;
- the live transport must **not** invent additional SSQM2952 request
  fields;
- a `read` for any other `request_kind` whose official TR is not bound
  in this slice must return a first-class failure (`VALIDATION_FAILURE`
  or `UNAVAILABLE`), never a guessed URL.

`account_selector` is the opaque inquiry-target selector already accepted
by Gateway. The transport must not parse it into a JOO subject. The
SSQM2952 sample does **not** take an account number in the request.
Account authority is token-side.

`ipAddr` / `macAddr` appear on **every** TR sample, including SSQM2952.
They are operator-injected **transport configuration**, not envelope
fields and not secrets. They are required in the frozen SSQM2952 request
shape as operator-injected placeholders. They must not be invented from
JOO subjects.

### 11.4 Response normalization

Allowed:

- parse JSON into a `dict`;
- return that exact `dict` as `ExplicitTransportSuccess.body` when the
  KB **business** outcome is success;
- let already-accepted `project_opaque_payload` drop secret keys.

Forbidden:

- semantic extraction;
- ticker / entity resolution;
- unit conversion;
- silent numeric normalization of zero-padded strings;
- domestic / overseas merge;
- inventing missing positions or cash;
- LLM / prose parsing;
- treating HTTP success as business success;
- treating a KB business-error body as success;
- returning empty holdings on a KB business error.

HTTP success alone is **insufficient**.

Use KB business response fields:

- `processFlag` must be the documented success state;
- plus business message / process code evaluation
  (`processCode`, `processMessage`, `dataBody.o_msg`).

A `processFlag` business failure **must** become a visible fail-closed
`PROVIDER_ERROR`. Do **not** return empty holdings on a KB business
error.

Numeric values may be zero-padded strings. Transport must not convert
units or silently normalize values.

### 11.5 Replaceability

Automated tests continue to inject a fake `BrokerTransport`.

The live transport is a production occupancy of the same port. Fake
transport remains the default CI path.

---

## 12. First verified KB endpoint and account-fact boundary

### 12.1 First independently verified endpoints

| Kind | Identifier | Status |
| --- | --- | --- |
| OAuth token issuance | `POST /oauth2/token` on official production host `https://developer.kbsec.com:32484` | **Verified** (path, Client Credentials, Bearer, `expires_in`). Token-request **serialization is SOURCE-CONFLICTED** (§3.3) |
| Holdings read | **`SSQM2952`** `POST /api/v1/ssqm2952` | **FIRST LIVE FACT.** READ-ONLY. 잔고현황 조회(체결기준) |
| Domestic cash | `SSQM0004` / `SWQN2302` | Verified by sample; **later**. Not this slice |
| Domestic buying power | `SSQM1802` | Verified by sample as **READ** (매수주문가능금액). **Later** `broker_fact` candidate. Not the first live fact. Not an order mutation |
| Overseas holdings | `SPQM2226` / `SPQO2226` | Verified by sample; **later phase**. Do not merge with SSQM2952 |
| Overseas cash / buying power | `SKQM3350` / `SKQM2106` | Verified by sample; **later** |
| Domestic market | `IVU*` | Verified by sample; **later `MarketTransport` slice** |
| Overseas market | `GS*` | Verified by sample; **later `MarketTransport` slice** |
| Realized P&L | domestic `SSQM2442` / `SSQM2392`; overseas `SPQM2206` / `SPQM2207` | Verified by sample; **later** |
| Domestic order mutations | `SSAM1801`, `SSAM1802`, `SSAM1805`, `SSAM1806`, `SSAM0831`, `SSAM5762`, `SSAM5763`, `SSAM5764` | **Verified as mutations and forbidden** |
| PII-heavy account TRs | `SSQM0005`, `SSQM0009` | **Must not** be the first live read |

```text
FIRST LIVE FACT:
SSQM2952
```

### 12.2 First intended account-fact kind

The accepted broker vocabulary already prioritizes portfolio-management
facts:

```text
BROKER_REQUEST_KIND_VALUES = (
    "holdings",
    "balances",
    "account_state",
)
```

Phase 1 of this identity binds **`holdings`** to **`SSQM2952`**.

It does **not** bind `balances` or `account_state` in this slice.
Domestic cash (`SSQM0004` / `SWQN2302`) and buying power (`SSQM1802`)
remain later `broker_fact` candidates.

### 12.3 SSQM1802 / SSAM1802 correction

| Identifier | Meaning | READ / WRITE | First-slice role |
| --- | --- | --- | --- |
| `SSQM1802` | Domestic buying-power / buy-orderable-amount inquiry (매수주문가능금액) | **READ** | Later `broker_fact` candidate. Not first live fact |
| `SSAM1802` | Domestic buy order (매수) | **BUY MUTATION** | Forbidden |

Retracted prior statements:

- `SSQM1802` is an order mutation API — **false**
- `SSQM1802` must be forbidden because it executes an order — **false**
- `POST /api/v1/ssqm1802` is the official order example and therefore
  an order API — **guide-label only; payload-proven as READ**

Do not blur `SSAM` and `SSQM` families.

### 12.4 Frozen SSQM2952 request contract

```text
POST /api/v1/ssqm2952
Host: developer.kbsec.com:32484
Content-Type: application/json
Authorization: Bearer <access_token>
```

```text
{
  "dataHeader": {
    "ipAddr": "<operator-injected>",
    "macAddr": "<operator-injected>"
  },
  "dataBody": {
    "excg_mktpr_ccd": ""
  }
}
```

`excg_mktpr_ccd` is optional according to the sample/catalog:

- `A` = integrated
- `K` = KRX
- `N` = NXT

An empty string is a lawful sample form.

Do **not** invent additional request fields.

`account_selector` remains opaque and is not a request field on this TR.

`ipAddr` / `macAddr` are operator-injected transport configuration.

### 12.5 Frozen SSQM2952 response shape

Important `dataHeader` fields:

- `resultCode`
- `resultMessage`
- `processFlag`
- `processCode`
- `processMessage`
- `processTime`

Important `dataBody` fields:

- `o_clsf`
- `o_lngth`
- `o_msg`
- `grid_cnt1`
- `tl_data_cnt`
- `ndy_tfnd`
- `dy_tfnd`
- `nxt2_dy_tfnd`
- `nt_asts_val_amt`
- `scrts_nt_val_amt`
- `val_amt_sum`
- `val_pl_sum`
- `val_pl`
- `val_yld`
- `val_yld_sum`
- `byng_amt_sum`
- `nt_byng_amt`
- `ndy_o_amt_psbl_amt`
- `nxt2_dy_o_amt_psbl_amt`
- `fcrncy_tfnd_krw_exch_amt`
- `Record1[]`

Important `Record1` fields:

- `clsf`
- `crncy_cd`
- `is_cd`
- `is_nm`
- `hld_q`
- `ordr_psbl_q`
- `hld_q_p6`
- `ordr_psbl_q_p6`
- `nstmt_s_q`
- `nstmt_b_q`
- `ec_q`
- `byng_amt`
- `byng_avr_prc`
- `now_prc`
- `val_amt`
- `val_pl`
- `val_yld`
- `fnl_ccls_excg_cd`
- `nxtd_lstng_ccd`

Do **not** require every listed field for successful first-slice
ingestion unless the sample proves it is mandatory. The listed fields
are the important contract surface, not a mandatory-presence checklist
for transport success.

This TR sample has no `nxt_key`. Continuation is not part of this slice.

Numeric values may be zero-padded strings. Transport must not convert
units or silently normalize values.

### 12.6 Business success / failure interpretation

HTTP success alone is **insufficient**.

Use KB business response fields:

1. `processFlag` must be the documented success state;
2. plus business message / process code evaluation
   (`processCode`, `processMessage`, `dataBody.o_msg`).

A `processFlag` business failure must become a visible fail-closed
`PROVIDER_ERROR`.

Do **not** return empty holdings on a KB business error.

Sample business success is of the form `processFlag` success plus
`o_msg` inquiry-success prose. That prose is evidence, not a JOO
product string to parse with an LLM.

### 12.7 Raw evidence is not Snapshot-ready

The raw SSQM2952 response is valid factual evidence. It is **not**
directly PortfolioSnapshot-ready.

Current KB quantity is nested:

```text
dataBody.Record1[].hld_q
```

Current PF-M3 quantity projection expects a **top-level**
`quantity_payload_key` from **one stored fact per holding binding**.

Therefore this first live factual transport slice may:

- authenticate;
- read SSQM2952;
- return the exact KB payload in an existing `broker_fact` envelope;
- append that evidence to FactStore through the rightful caller.

This first slice must **not** claim that the raw SSQM2952 envelope can
directly produce PF-M3 holdings.

A later additive normalization / projection slice must convert
provider-specific holdings rows into Snapshot-compatible factual records
while preserving traceability to the original KB evidence.

Do **not** redesign `PortfolioSnapshotProducer` now.

Preferred ownership: normalization **before** KB vendor structure
reaches Portfolio Snapshot or CIO.

Do **not** put `dataBody` / `Record1` parsing into CIO.

### 12.8 Required account authority

Official token issuance validates API authority and account authority.
`account_selector` must name the operator-authorized inquiry target. A
provider rejection for missing account authority is fail-closed
(`AUTH_FAILURE` or `PROVIDER_ERROR`). The transport must not fall back to
another account.

---

## 13. Domestic / overseas scope

### 13.1 Official split

Domestic and overseas are separate official API families. The sample
package independently confirms that one TR does **not** cover both.

The user's portfolio includes both domestic and overseas securities. That
product fact authorizes a **phased path**. It does not authorize
implementing every KB API in the first slice.

Do **not** merge domestic and overseas schemas.

### 13.2 Phased path, now sample-supported

```text
Phase 1 — this identity, first implementation slice
  live OAuth
  + SSQM2952 domestic holdings / valuation read
  + existing Gateway envelope (raw evidence)
  + rightful-caller FactStore append
  + fake-HTTP automated tests

Phase 2 — later architecture, same identity or a later additive freeze
  additional independently verified domestic / overseas account-fact TRs
  + later live MarketTransport occupancy if separately authorized
  + later additive holdings-row normalization before Snapshot / CIO
```

Phase 1 proves the transport architecture. It does not implement every KB
API at once. It does **not** implement the later TRs listed below.

### 13.3 Later TR scope (documented only; do not implement now)

| Concern | Proven TRs | Slice |
| --- | --- | --- |
| Domestic holdings | **SSQM2952** | **This slice — first live fact** |
| Domestic holdings qty-only alt | SSQM1801 | Later; not selected (sell-context / qty-only) |
| Domestic cash | SSQM0004 / SWQN2302 | Later |
| Domestic buying power | SSQM1802 | Later READ. Not an order |
| Overseas holdings | SPQM2226 / SPQO2226 | Later phase |
| Overseas cash / buying power | SKQM3350 / SKQM2106 | Later |
| Domestic market | IVU* | Later `MarketTransport` |
| Overseas market | GS* | Later `MarketTransport` |
| Realized P&L | domestic SSQM2442 / SSQM2392; overseas SPQM2206 / SPQM2207 | Later |
| PII-heavy account | SSQM0005 / SSQM0009 | Do **not** choose as first live read |

Do not implement these later TRs now.

### 13.4 Isolation

1. Distinct official families require distinct collect attempts.
2. Distinct `account_selector` values require distinct bindings.
3. The live transport must not merge domestic and overseas bodies into one
   invented envelope.
4. `account_selector` remains opaque. It is not a venue_target and not a
   JOO subject id.
5. One `read` remains one TR. Do not fan out SSQM2952 + cash + overseas
   in the same `read`.

---

## 14. Market fact retrieval

### 14.1 Ruling

**Market-price retrieval is a later slice.**

| Option | Verdict |
| --- | --- |
| A. Same first slice | **Rejected** |
| B. Separate second slice after broker / account factual proof | **Selected** |

Sample-proven later market families, **not** bound now:

- domestic: `IVU*` (and related `IVS*` / `SZQM0771`)
- overseas: `GS*`

### 14.2 Tradeoff

Including market now would occupy two accepted ports, two official API
families, and two Snapshot downstreams in one implementation. That is
larger than the proven gap.

The existing contract already separates them:

- `BrokerTransport` / `KbOpenApiAdapter` / `broker_fact`
- `MarketTransport` / `MarketApiAdapter` / `market_fact`

PF-M3 first-slice holdings composition does not require live market prices.
PF-M4 already composes from stored `market_fact`s.

The two are **not** inseparable. The smaller architecture is therefore
correct.

A later live-market occupancy may reuse this slice's OAuth / HTTP / secret
lessons only through a separate architecture freeze. It must not retag
broker payloads as `market_fact`.

---

## 15. FactStore handoff

### 15.1 Ruling

**A. Return a Gateway envelope to an existing caller which appends to
FactStore.**

| Option | Verdict |
| --- | --- |
| **A. Caller appends** | **Selected and frozen** |
| B. This slice owns a narrow live-read → Gateway → FactStore function as a new owner | **Rejected** — collapses transport / Gateway / store ownership |

### 15.2 Ownership

| Actor | Must | Must not |
| --- | --- | --- |
| Live `BrokerTransport` | Authenticate, read SSQM2952, return structured success / failure | Append, retrieve, or import FactStore; normalize `Record1` into Snapshot rows |
| `KbOpenApiAdapter` / Gateway | Emit immutable envelope or first-class failure | Call FactStore; parse `dataBody` / `Record1` for CIO |
| FactStore | Append eligible success envelopes | Re-call KB, become a second Gateway; accept OAuth/token responses as facts |
| Rightful later caller / optional pilot | `collect` then, on success only, `FactStore.append` | Invent facts on failure; send secrets to the store; treat raw KB as PF-M3-ready |

This preserves the frozen PF-M1 / PF-M2 rule: **PF-M1 produces; PF-M2
persists.**

### 15.3 Handoff recipe

The production sequence this identity enables, without creating a new
package, is:

```text
KbOpenApiAdapter.collect(ExplicitBrokerCollectRequest)
        │
        ├── failure -> do not append; surface ExplicitProviderFailureSignal
        └── success envelope  (raw SSQM2952 evidence inside broker_fact)
                │
                ▼
FactStore.append(
  ExplicitFactAppendRequest(
    fact_id,                 # caller-supplied opaque id
    envelope,                # exact Gateway envelope
    superseded_fact_id,      # optional explicit link
  )
)
```

`fact_id` remains caller-supplied. This slice does not auto-generate it.

### 15.4 Evidence / auditability rule

Raw KB response evidence must remain traceable.

For this transport slice:

- raw provider response **may** be preserved inside the `broker_fact`
  envelope;
- OAuth / token responses must **never** be stored as facts;
- `access_token`, `appKey`, `appSecret`, and other SECRET names must
  **never** enter FactStore.

A later normalized `broker_fact` may coexist with the original evidence
fact if separately authorized.

Do **not** overwrite raw evidence with a normalized-only representation.

Compatible frozen strategy for this transport slice:

```text
C. retain raw vendor evidence inside the Gateway envelope payload,
   and do not treat that payload as a PF-M3-ready holding row.
```

| Option | Verdict |
| --- | --- |
| A. raw vendor payload stored directly | Lawful for audit of this slice. **Not** Snapshot-projectable |
| B. normalized only | **Rejected** — loses evidence |
| C. raw evidence + later normalized fact | Required before Snapshot / CIO consume holdings |

No FactStore public-API change is required now.

### 15.5 Why not a new orchestrator package

A convenience function that both collects and appends would become a third
owner sitting on top of two frozen single-owner packages. Tests may
exercise the sequence. Production orchestration remains a later rightful
caller or the separately authorized pilot. Transport itself must not grow
that function.

---

## 16. Fact metadata and freshness

### 16.1 Reused envelope metadata

| Concern | Existing field | Rule |
| --- | --- | --- |
| Provider identity | `provider_id` | Exactly `"kb_open_api"` |
| Source class | `source_class` | Exactly `"broker_fact"` on success |
| Collection time | `collected_at` | Gateway-boundary UTC from injected clock |
| Ingress identity | `envelope_id` | Caller-supplied |
| Correlation | `request_correlation_id` | Optional; no secrets |
| Account / book scope | `account_selector` on the binding | Not an envelope field. Distinct collects remain distinct |
| Request kind | `request_kind` on the request | Not an envelope field. Do not add it |
| Symbol | payload only (`Record1[].is_cd` / `is_nm`) | Opaque captured content |
| Provider-native timestamps | payload only (`dataHeader.processTime`) | Do not replace `collected_at`. Do not promote `processTime` to a first-class envelope field in this slice |

Do not add a parallel metadata schema.

Do not redesign the envelope to add provider-native as-of time now.

### 16.2 Store metadata

FactStore already records:

- preserved `collected_at`
- store-owned `appended_at`
- `fact_id`, `envelope_id`, `provider_id`, `source_class`

`appended_at` must not be substituted for `collected_at` when claiming
collection freshness.

### 16.3 Freshness policy remains downstream

PF-M3 already fail-closes on `STALE_REQUIRED_FACT` when
`freshness_max_age` is supplied and `collected_at` is too old. PF-M4 has
the same pattern for market facts.

This slice does **not** invent a new freshness field.

`collected_at` and `appended_at` are sufficient for this first transport
slice.

KB `processTime` may remain inside raw provider evidence.

Token `expires_in` is transport-local and is **not** fact freshness.

If a later architecture proves that provider-native observation time must
become a first-class field, that is a later additive freeze. It is not
required to close the live-transport gap.

---

## 17. Failure / retry contract

### 17.1 Reused failure classes

```text
AUTH_FAILURE
TRANSPORT_FAILURE
PROVIDER_ERROR
UNAVAILABLE
RATE_LIMITED
VALIDATION_FAILURE
```

No second failure plane.

### 17.2 Mapping

| Condition | Class | Retry |
| --- | --- | --- |
| Missing / blank / unparseable client material | `AUTH_FAILURE` | None |
| Invalid `appKey` / `appSecret` / client rejected | `AUTH_FAILURE` | None |
| Token success | continue | n/a |
| Token HTTP / JSON error | `AUTH_FAILURE` or `PROVIDER_ERROR` | No token retry loop |
| Token expired / provider unauthorized after a prior token | one re-issue + one request retry | Then fail closed |
| KB API HTTP error | `PROVIDER_ERROR` | None |
| KB `processFlag` business failure / non-success process code / business message | `PROVIDER_ERROR` | None. **Do not return empty holdings** |
| Malformed JSON | `VALIDATION_FAILURE` | None |
| Official rate-limit / 호출 제한 초과 | `RATE_LIMITED` | **No automatic retry storm** |
| Timeout / TLS / network | `TRANSPORT_FAILURE` | None |
| Unbound later TR used as if known (`balances`, overseas, market, orders) | `VALIDATION_FAILURE` or `UNAVAILABLE` | None |
| Residual secret in projected payload | `VALIDATION_FAILURE` | None |

### 17.3 Fail-closed invariants

1. No synthetic holdings, balances, account state, prices, orders, or fills.
2. No elevation of partial garbage to success.
3. Auth failure stops the collect. It does not degrade into empty success.
4. KB business failure stops the collect. It does **not** degrade into
   empty holdings success.
5. Rate-limit is visible as `RATE_LIMITED`, not silently delayed inside an
   unbounded loop.
6. Unknown / stale / failed KB reads remain explicit failure or absent
   facts. AI must never invent the missing KB fact.

---

## 18. Security / secret-redaction contract

### 18.1 Three vocabularies

**SECRET** — must never persist or enter AI:

- `appKey`
- `appSecret`
- `access_token`
- `token`
- `hts_pwd`
- `ac_pwd`
- `hd_pin_no`

**SENSITIVE_ACCOUNT_METADATA** — persist only if necessary; must not
enter AI unless separately and explicitly required:

- `ac_no`
- `gnl_ac_no`
- `gnl_ac_no1`
- `ac_nm`
- `rnmcno`
- `rsdnt_rno`
- `rprst_cs_no`
- `emp_no`

**LAWFUL_PORTFOLIO_FACT** — may lawfully flow into JOO factual layers:

- `is_cd`
- `is_nm`
- `hld_q`
- `now_prc`
- `val_amt`
- `val_pl`
- `tfnd`
- `do_psbl_csh`
- and equivalent portfolio factual values

Do **not** choose `SSQM0005`, `SSQM0009`, or other PII-heavy TRs as the
first live read. `SSQM2952` is the frozen first live fact because the
sample contains lawful portfolio facts and no resident-number field.

### 18.2 Handling rules

1. Real secrets are runtime-only.
2. No secret files are created by this architecture.
3. No live KB call is authorized by this document.
4. `project_opaque_payload` continues to drop forbidden keys.
5. `payload_contains_secret` continues to reject residual secret values.
6. `sanitize_detail` continues to drop details that contain the outbound
   secret or secret field names.
7. Official names `appKey` and `appSecret` are added to the redaction
   vocabularies.
8. Access Tokens are redacted by existing `access_token` / `token` /
   `authorization` names and by residual-value checks against the live
   token string.
9. Exceptions raised by the live transport must not interpolate secrets,
   tokens, or raw authenticated request bodies.
10. Test fixtures may use obviously fake material only
    (`test-app-key`, `test-app-secret`, `test-access-token` or equivalent).
    They must never contain real KB credentials.
11. OAuth / token responses must never be stored as facts.
12. Sensitive account identifiers must not enter AI unless separately and
    explicitly required.
13. Portfolio facts may lawfully flow into JOO factual layers. That
    lawful flow does **not** make the raw SSQM2952 envelope
    Snapshot-ready.

---

## 19. Test boundary

Automated tests use **fake HTTP**. Normal CI must not require real
credentials or a network path to `developer.kbsec.com`.

Required tests:

| # | Case |
| --- | --- |
| 1 | Missing credentials → `AUTH_FAILURE` |
| 2 | Invalid / rejected credentials → `AUTH_FAILURE` |
| 3 | Token success, then one SSQM2952 success body maps to transport success |
| 4 | Token expiry by injected clock causes re-issuance |
| 5 | Token re-issuance then one retry; no second retry |
| 6 | OAuth HTTP error → fail closed, no account-fact call |
| 7 | KB API HTTP error → `PROVIDER_ERROR` |
| 8 | Malformed JSON → `VALIDATION_FAILURE` |
| 9 | KB `processFlag` business-error response → `PROVIDER_ERROR`, not success, **not empty holdings** |
| 10 | Rate-limit response → `RATE_LIMITED`, no retry storm |
| 11 | Token request uses the **single serialization variant frozen at Implementation Boundary Review**. Tests must not silently accept both Candidate A and Candidate B unless a later authorization explicitly permits bounded compatibility. Path remains `/oauth2/token`. Logical inputs remain `appKey`, `appSecret`, client-credentials grant |
| 12 | SSQM2952 request is exactly the frozen §12.4 shape. No invented fields. Numeric response strings are returned without unit conversion |
| 13 | Response body is returned as opaque `dict` without semantic repair |
| 14 | Secret redaction of `appKey`, `appSecret`, `access_token` |
| 15 | No token leakage into envelope, diagnostics, exception text, or FactStore payload |
| 16 | Fake `BrokerTransport` remains supported by `KbOpenApiAdapter` |
| 17 | Gateway public collect / envelope / FactStore / Snapshot contracts remain unchanged |
| 18 | FactStore receives the **raw** `broker_fact` evidence envelope on a caller append. OAuth/token responses are never stored. No SECRET keys enter the store |
| 19 | No AI / LLM call on this path. No `dataBody` / `Record1` parsing in CIO |
| 20 | Domestic / overseas isolation: one binding / one kind / one body; no merge |
| 21 | `collected_at` comes from the injected clock; token expiry uses the injected clock. Token `expires_in` is not fact freshness |
| 22 | Deterministic repeated fake input produces the same envelope / failure class |
| 23 | Tests do **not** claim that a raw SSQM2952 envelope is PF-M3-producible |

A caller-sequence test may demonstrate
`collect` → `ExplicitFactAppendRequest` → `FactStore.append` using fake
HTTP and fake credentials. That test does not make transport the store
owner and does not produce a Portfolio Snapshot from the raw envelope.

---

## 20. Controlled pilot boundary

This remediations does **not** authorize a live pilot.

A later separately authorized pilot, if one is ever granted, must be:

- read-only;
- manual;
- bounded;
- one verified endpoint;
- **SSQM2952 only** for first live account proof;
- no order TR (`SSAM*` and overseas order families remain forbidden);
- no retries beyond the frozen bounded OAuth rule;
- no secret output;
- no automatic portfolio action;
- real credentials supplied outside git;
- no Autopilot;
- no Snapshot redesign;
- stop on first auth failure or first KB business failure.

This document does **not** authorize running that pilot.

---

## 21. Non-responsibilities

This identity / slice must **not**:

1. Do Milestone Selection Engine work.
2. Expand or overwrite any Autopilot catalog.
3. Change CIA or grant a `JOO_AUTOMATION` identity.
4. Implement Architecture State Resolver.
5. Implement Automation-M3.
6. Implement PF-M5 Market Watch unless a later independent architecture
   proves it necessary — this freeze does not.
7. Implement IRO-M3 / IRO-M4.
8. Perform CIO capital allocation.
9. Place, modify, cancel, or automatically execute orders.
10. Perform autonomous position changes or automated trading.
11. Build a secret-management platform or token vault.
12. Build a general-purpose scheduler or unbounded poller.
13. Add third-party broker support.
14. Add WebSocket / streaming unless a later architecture separately
    requires it.
15. Reuse `AIAdapter` HTTP as the KB client.
16. Invent additional unproven TR bindings beyond the sample-proven
    first live fact `SSQM2952`.
17. Change `ProviderInterface.collect`, envelope fields, FactStore public
    append / retrieval, or Snapshot `produce`.
18. Let transport append to FactStore.
19. Let FactStore call KB.
20. Merge domestic and overseas families.
21. Implement live `MarketTransport` in this first slice.
22. Send KB facts or secrets to research AI as primary truth.
23. Treat the raw SSQM2952 envelope as PF-M3-ready.
24. Put `dataBody` / `Record1` parsing into CIO.
25. Overwrite raw evidence with a normalized-only representation.
26. Store OAuth / token responses as facts.
27. Silently guess between OAuth serialization Candidate A and
    Candidate B.
28. Bind `SSQM0005`, `SSQM0009`, or other PII-heavy TRs as the first
    live read.
29. Classify `SSQM1802` as an order mutation or `SSAM1802` as a read.
30. Redesign Repository Target, Runtime Integration, COMMIT READY, or
    `next_action`.

---

## 22. First implementation slice

If this remediations text is independently re-reviewed and accepted, the
first implementation authorization is limited to:

1. Concrete `KbOpenApiLiveBrokerTransport` occupying `BrokerTransport`.
2. Official `POST /oauth2/token` client.
3. **Source-conflicted token serialization resolved before production**
   (§3.3). No silent A/B fallback unless a later implementation
   authorization explicitly permits bounded compatibility behavior.
4. SSQM2952 request / response binding (§12.4 / §12.5).
5. KB business-error handling via `processFlag` / process code /
   business message. No empty holdings on business error.
6. Process-local token cache + one re-issuance path.
7. Injected fakeable HTTP client and clock.
8. Additive `appKey` / `appSecret` redaction names.
9. Fake-HTTP unit tests listed in §19.
10. Raw `broker_fact` evidence handoff to a rightful caller.
11. README documentation of the occupied live-transport slot.

**Still out of the first implementation authorization:**

- snapshot normalization / PF-M3 holdings projection;
- market transport;
- overseas transport;
- cash / buying-power / realized-P&L TRs;
- any order API (`SSAM*`, overseas order families);
- CIO;
- selector / catalog / CIA changes;
- any live pilot;
- any live KB call authorized by this remediations document itself.

**DO NOT IMPLEMENT THIS NOW.**

### 22.1 Mutation allowlist for a later implementation authorization

| Path | Authorized mutation |
| --- | --- |
| `ProviderGateway/adapters/kb_openapi_live_broker_transport.py` | **New file.** Live `BrokerTransport` |
| `ProviderGateway/auth/credentials.py` | Additive official secret field names only |
| `ProviderGateway/README.md` | Document live-transport occupancy; do not rewrite frozen collect contracts |
| `ProviderGateway/tests/*` | Additive live-transport / redaction / fake-HTTP tests |
| `FactStore/models/vocabularies.py` | Additive official secret field names only, as defense in depth |

### 22.2 Must remain unchanged

- `ProviderInterface.collect` signature and request union
- `KbOpenApiAdapter` public collect / health behavior, except through the
  already-injected transport port
- `ExplicitProviderPayloadEnvelope` fields
- `ExplicitBrokerCollectRequest` / binding types
- `MarketApiAdapter` / `MarketTransport`
- FactStore append / retrieval semantics
- `PortfolioSnapshotProducer` / `MarketSnapshotProducer`
- IRO-M1 / IRO-M2
- Automation / CIA / selector documents and runtime
- Milestone Selection Engine, Repository Target, Runtime Integration,
  COMMIT READY, `next_action`
- Out-of-boundary untracked documents listed in §1

---

## 23. Strategic product position

JOO remains an operational investment command center. The factual hierarchy
this slice occupies is the bottom of that stack:

```text
KB Securities Open API
        │  raw verified facts (this slice: SSQM2952 evidence)
        ▼
later additive normalization  (OUT OF THIS SLICE)
        │  Snapshot-compatible holdings records
        ▼
FactStore
        ▼
Portfolio Snapshot / Market Snapshot
        ▼
AI research
        ▼
Evidence / Contradiction
        ▼
ChatGPT CIO
        ▼
capital-allocation decision
```

KB factual truth remains below AI interpretation.

AI must never invent missing KB facts.

Unknown / stale / failed KB reads remain explicit fail-closed states.

CIO must never parse `dataBody` / `Record1`.

---

## 24. Document authority

- This document is the canonical first-slice architecture for the
  unnumbered identity **KB OpenAPI Live Factual Pipeline**.
- It is subordinate to the Constitution and to accepted PF-M1, PF-M2,
  PF-M3, PF-M4, IRO-M1, and IRO-M2 contracts in those contracts' scopes.
- It consumes the previous ZERO-IDENTITY CIA decision as sequencing
  authority only.
- It consumes the KB sample-package TR mapping review as the
  authoritative factual-surface remediations source.
- It does not authorize implementation, live KB calls, live Autopilot,
  commit, tag, or push.
- A later **JOO** Catalog Identity Authorization review may consider
  granting this exact opaque string in a `repository_id = JOO` namespace.
  This document does not place it in `JOO_AUTOMATION`.

---

## 25. Architecture freeze summary

**This freeze decides:**

- owner = `ProviderGateway`;
- identity = `KB OpenAPI Live Factual Pipeline`;
- port = existing `BrokerTransport`;
- adapter = existing `KbOpenApiAdapter`;
- OAuth = official Client Credentials at `POST /oauth2/token`;
- token-request serialization = **SOURCE-CONFLICTED — IMPLEMENTATION
  BOUNDARY MUST RESOLVE** (Candidate A: flat + `grant_type`; Candidate B:
  `dataHeader`/`dataBody` + `grantType`);
- first account-fact TR =

```text
FIRST LIVE FACT:
SSQM2952
```

  path `POST /api/v1/ssqm2952`, READ-ONLY, 잔고현황 조회(체결기준);
- `SSQM1802` = buying-power **READ**, later candidate, not first live fact;
- `SSAM1802` = **BUY MUTATION**, forbidden;
- raw SSQM2952 payload = lawful `broker_fact` evidence, **not**
  PF-M3-ready;
- later normalization = additive, before Snapshot / CIO, not this slice;
- market live retrieval = later slice (`IVU*` / `GS*`);
- FactStore append = rightful caller, not transport;
- raw evidence must remain traceable; OAuth responses never stored;
- Gateway / FactStore / Snapshot public APIs = unchanged;
- secrets = runtime-only, redacted, never persisted, never enter AI;
- tests = fake HTTP;
- pilot = later, separately authorized, SSQM2952 only, not run now;
- implementation = **not authorized by this remediations**.

**This freeze does not decide:**

- a winner between OAuth serialization Candidate A and Candidate B;
- a test-environment host not listed on the official guide page;
- a new orchestration package;
- a JOO_AUTOMATION catalog grant;
- Snapshot-compatible holdings-row projection;
- any later cash / overseas / market / realized-P&L / order binding.

---

**KB OPENAPI LIVE FACTUAL PIPELINE ARCHITECTURE REMEDIATED**
