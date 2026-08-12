# PF-M1 Provider Gateway Architecture

## Status and milestone

- Status: Architecture authored for independent review; first Provider & Fact
  plane implementation architecture freeze
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Provider & Fact** (Layer 2 — Provider Gateway)
- Milestone: **PF-M1**
- Production package (future, not created by this document): `ProviderGateway`
- Architecture sources of truth (frozen; must not be redesigned):
  - `docs/JOO_PRODUCT_ARCHITECTURE.md` (Layer 2 / PF-M1; product composition)
  - `docs/INVESTMENT_RESEARCH_ORCHESTRATOR_ARCHITECTURE.md` (IRO product plane)
  - `docs/iro/IRO_M1_ARCHITECTURE.md`
  - `docs/iro/IRO_M2_ARCHITECTURE.md`
- Candidate boundary review input (remediation-bearing):
  JOO-Automation result `provider_gateway_candidate_boundary_review`
  (decision: **REMEDIATION REQUIRED**; all five remediations are incorporated
  in this freeze text)
- Repository boundary for this document: architecture authoring only; this
  document alone authorizes no production code, test, package scaffold,
  schema module, configuration, run artifact, or Git history mutation

This document freezes the **first implementation architecture** for PF-M1.

It does **not** redesign the approved JOO product architecture.

It does **not** redesign the Investment Research Orchestrator product
architecture, IRO-M1, or IRO-M2.

It does **not** redesign Automation M1–M3, accepted domain packages, or the
Stage 1/2 research execution stack (`AIAdapter`, `ExecutionEngine`,
`Committee`, `PipelineRuntime`, M22 `ResearchOrchestrator`).

Implementation requires separate authorization after architecture review.
No production package is created by this document.

---

## Normative PF-M1 surface (must remain explicit)

### PF-M1 implements ONLY

| # | Responsibility |
| --- | --- |
| 1 | **KB Open API ingress** (first broker adapter only) |
| 2 | **Provider Interface** (common ingress contract for adapters) |
| 3 | **Immutable provider payload envelope** (wire → accepted ingress record) |
| 4 | **Source classification** (`broker_fact` on PF-M1 outputs) |
| 5 | **Provider health signaling** (availability, failure, outage for the KB path) |

### PF-M1 does NOT implement

| Concern | Owner (elsewhere) |
| --- | --- |
| **Fact Store** | PF-M2 / Layer 3 |
| **Portfolio Snapshot** production | PF-M3 (+ accepted Portfolio\* contracts) |
| **Market Snapshot** production | PF-M4 |
| **Market Watch** Engine | PF-M5 |
| **Evidence** Store / research evidence | IRO (frozen) |
| **IRO** lifecycle | IRO / IRO-M1 / IRO-M2 (frozen) |
| **CIO** Engine | IRO (deferred full surface IRO-M4 direction) |
| **Trading** / Broker Execution | Layer 15 BX-M1 (human-gated; uses broker channel later) |
| **Human Approval** (capital) | Layer 14 Human Authority |

---

## 1. Purpose

### 1.1 Purpose

**PF-M1** is the first implementable slice of the **Provider Gateway** layer
in the Provider & Fact plane.

Its purpose is to provide a **broker-first product ingress** that:

1. authenticates to and calls the **KB Open API** as the first broker fact
   source;
2. exposes a stable **Provider Interface** for adapter-shaped ingress;
3. captures every accepted provider response (or structured failure) as an
   **immutable provider payload envelope**;
4. tags every accepted envelope with a normative **source class**
   (`broker_fact` for PF-M1 broker path);
5. signals **health, availability, failure, and outage** for that broker path
   so downstream fact persistence and observability can fail closed or surface
   staleness without inventing data.

PF-M1 maximizes **ingress integrity and source-class separation**. It does not
persist facts, compose snapshots, run research, or execute capital actions.

### 1.2 Explicit non-identity

PF-M1 / Provider Gateway is **not**:

- the Fact Store (Layer 3 / PF-M2);
- Portfolio Snapshot or Market Snapshot production;
- Market Watch Engine;
- IRO, Evidence Store, Operational Memory, Contradiction, Expected Value, or
  CIO;
- Stage 1/2 research provider invocation (`AIAdapter` / `ExecutionEngine` /
  `Committee` / M22);
- Broker Execution or trading;
- Human Approval (capital) or Development Automation human gates;
- a domain package, Knowledge Engine normalizer, entity resolver, or semantic
  extractor;
- a news / alternative-media ingest layer (not a frozen Layer 2 source class).

### 1.3 Product plane position

PF-M1 implements a **subset** of Layer 2 (Provider Gateway) above external
broker connectivity and **beside** (not inside) IRO and capital planes:

```text
External KB Open API
        │
        ▼
Provider Gateway — PF-M1 slice
  Provider Interface
    → KB Open API Adapter
    → Authentication boundary
    → Immutable Provider Payload Envelope
    → Source Classification (broker_fact)
    → Health / Failure / Outage signaling
        │
        │  handoff only (no persistence ownership)
        ▼
  [PF-M2 Fact Store — deferred]
  [Observability consumers of health signals]

IRO plane (frozen) ────────── research lifecycle; consumes snapshots later
Capital plane ─────────────── Human Approval → Broker Execution (later BX-M1)
Development Automation ───── joo_auto; builds milestones; not a runtime dep
```

### 1.4 Relationship to frozen architectures (non-redesign)

| Frozen input | Rule for PF-M1 |
| --- | --- |
| `JOO_PRODUCT_ARCHITECTURE.md` Layer 2 | Governing product definition of Provider Gateway; PF-M1 is the broker-first first slice |
| `JOO_PRODUCT_ARCHITECTURE.md` PF-M1 row | Delivers KB Open API ingress, source-class tagging, outage signaling |
| IRO product architecture | Untouched; research lifecycle remains IRO; capital remains out of IRO |
| IRO-M1 / IRO-M2 | Untouched; no provider/broker ingress ownership transferred into IRO |
| Stage 1/2 research stack | Retains research AI invocation ownership (product risk R5 mitigation) |
| Automation M1–M3 | Untouched; development-only; not a PF-M1 runtime dependency |
| Accepted domain packages | Consume-only if ever referenced; Gateway does not redefine them |

If any statement in this document appears to conflict with a frozen input, the
frozen input wins for its scope, and the conflict is an architecture defect
to remediate — not a silent override.

---

## 2. Scope

### 2.1 In scope (this architecture)

This architecture freezes:

1. **Purpose** and product-plane position of PF-M1 Provider Gateway.
2. **Scope** split: package lifetime (Layer 2 direction) vs **PF-M1 first
   implementation** deliverable.
3. **Package ownership** and production package identity.
4. **Package responsibilities** (lifetime vs PF-M1-only).
5. **Provider Interface** contract for adapters.
6. **KB Open API Adapter** as the sole PF-M1 adapter.
7. **Authentication boundary** for broker credentials and request signing.
8. **Immutable Provider Payload Envelope** (wire → envelope rule).
9. **Source Classification** normative classes and PF-M1 tagging rules.
10. **Health check / availability** observation for the KB path.
11. **Failure / outage signaling** fail-closed posture.
12. **Upstream / Downstream** edges for PF-M1 and package lifetime.
13. **Dependency graph** and forbidden edges.
14. **Deferred responsibilities** (including market adapters, Fact Store,
    research AI transport runtime, multi-broker, BX channel use).
15. **Forbidden responsibilities** (including news adapters without amendment).
16. **Future PF-M2 relationship** (ingress handoff only; no store ownership).

### 2.2 Package lifetime vs PF-M1 first implementation (remediation D3)

Layer 2 as a **product layer** may eventually host additional adapters.
**PF-M1** is narrower.

| Concern | Package lifetime (Layer 2 direction) | PF-M1 first implementation |
| --- | --- | --- |
| KB Open API broker ingress | Yes | **Yes — only broker adapter** |
| Additional broker adapters | Yes (later milestones) | **No** |
| Market API adapters | Yes (slot reserved) | **No — deferred to PF-M4 direction** |
| Research AI source class recorded | Yes (classification surface) | **Class recorded; runtime deferred** |
| Research AI invocation / committee | Never (Stage 1/2 ownership) | Never |
| Fact Store persistence | Never (PF-M2) | Never |
| News / non-frozen source classes | Only after architecture amendment | **No** |

### 2.3 Out of scope (this document and PF-M1)

- Production code, tests, package scaffold, configuration files, credentials
  vaults, or Git history mutation authorized by this document alone.
- Fact Store schema, retention, append/supersession implementation (PF-M2).
- Portfolio / Market snapshot composition and Market Watch.
- IRO run coordination, Evidence Store, memory, contradiction, EV, CIO.
- Broker order placement or capital execution.
- Market data providers as implementable PF-M1 adapters.
- News, alternative data, or any source class not frozen at Layer 2.
- Unconstrained “provider normalization,” entity resolution, semantic
  extraction, or domain identity mutation.

### 2.4 Candidate review remediations incorporated

This freeze incorporates all five required remediations from
`provider_gateway_candidate_boundary_review`:

| # | Remediation | Where reflected |
| --- | --- | --- |
| R1 | Remove **news provider adapters** from package responsibility | §2.3, §9, §15 |
| R2 | Replace unconstrained “provider normalization” with **wire → immutable envelope**; forbid semantic/entity/domain normalization | §8 |
| R3 | Split **package lifetime vs PF-M1**; market adapters deferred | §2.2, §6, §14 |
| R4 | Record **research AI** as Layer 2 source class **deferred for PF-M1**; Stage 1/2 retain invocation; ban research AI → Fact Store primary truth | §9, §14, §15 |
| R5 | Exclude Fact Store, snapshots, watch, IRO, EV, CIO, trading, human capital approval from Gateway ownership | Normative surface, §4, §12, §15 |

---

## 3. Package ownership

### 3.1 One-package architecture

**One package with internal components.**

| Option | Verdict |
| --- | --- |
| **A. One package** | **Selected and frozen** |
| B. Several packages (envelope / adapter / health as separate packages) | Rejected for PF-M1 — invents taxonomy beyond first ingress slice |
| C. Implement inside IRO, `AIAdapter`, or domain packages | Rejected — plane collapse and responsibility transfer |

### 3.2 Package identity

| Name | Role |
| --- | --- |
| `ProviderGateway` | **Only** allowed PF-M1 production package name |
| `InvestmentResearchOrchestrator` | Frozen IRO package — **unchanged**, not Gateway |
| `ResearchOrchestrator` | Frozen M22 package — **unchanged** |
| `AIAdapter` / `ExecutionEngine` / `Committee` | Stage 1/2 research execution — **unchanged**; not Gateway |
| Domain packages (Portfolio\*, Evidence\*, etc.) | Accepted contracts — not Gateway ownership |

### 3.3 Ownership table

| Concern | Owner |
| --- | --- |
| This architecture document | JOO `docs/provider/` |
| Provider Gateway production code (future) | Package `ProviderGateway` |
| Provider Interface | `ProviderGateway` |
| KB Open API Adapter (PF-M1) | `ProviderGateway` |
| Authentication boundary (credential use at edge) | `ProviderGateway` (secrets **supply** remains operator/config outside package invention) |
| Immutable provider payload envelope | `ProviderGateway` |
| Source identity + source-class tags on ingress records | `ProviderGateway` |
| Health / failure / outage signals for adapters it owns | `ProviderGateway` |
| Fact Store persistence / append semantics | **Not this package** (PF-M2 / Layer 3) |
| Portfolio / Market Snapshot production | **Not this package** (PF-M3 / PF-M4) |
| Market Watch, IRO lifecycle, Evidence Store | **Not this package** |
| Research AI one-call invocation & committee aggregation | **Stage 1/2** — unchanged |
| “When” research units run | **IRO Research Execution Adapter** — unchanged |
| Capital orders / fills as execution | **Broker Execution (Layer 15)** — may later use broker channel; not Gateway ownership of trading |
| Domain structure/math | **Accepted domain packages** — consume-only if referenced |
| Automation M1–M3 | **`joo_auto` only** — builds milestones; not runtime dependency |

### 3.4 Ownership rules (normative)

1. PF-M1 owns **ingress coordination** for the KB Open API path only.
2. PF-M1 **emits** immutable envelopes; it does **not** become the Fact Store.
3. PF-M1 does **not** absorb Stage 1/2 research provider packages or IRO.
4. Responsibilities are not silently transferred from accepted packages into
   Gateway “god” logic.
5. Live portfolio mutation, order placement, and capital approval are never
   owned by Gateway.
6. Secrets and broker credentials are **used** at the authentication boundary;
   PF-M1 does not invent a secret-management product.

### 3.5 Frozen package structure (normative layout intent)

```text
ProviderGateway/
  README.md
  models/                 # envelope, source class, health, failure signals
  validation/             # type/nonblank/enum validation; no semantic repair
  provider_interface.py   # common adapter contract
  adapters/
    kb_open_api.py        # PF-M1 sole adapter
  auth/                   # authentication boundary helpers (no secret invention)
  health.py               # availability / health check surface
  signaling.py            # failure / outage signal construction
  ingress.py              # wire → envelope orchestration for one call
  tests/                  # authorized only with implementation
```

Layout is normative for component boundaries and names. Exact file splitting
inside `models/` / `validation/` / `adapters/` may vary at implementation time
without changing ownership or public contract intent.

### 3.6 Non-package rule

PF-M1 must not create sibling operational packages for “Envelope,” “Health,”
“KB Adapter,” or “Fact Ingress.” Internal modules only.

---

## 4. Package responsibilities

### 4.1 Lifetime responsibilities (Layer 2 package direction)

**Provider Gateway** is the **Provider & Fact plane ingress boundary only**.

Over the package lifetime it is responsible for:

- External provider connectivity at the product edge (authenticated access,
  request/response boundary).
- **Source identity** (provider identity, collection timestamps, provenance
  fields required for fact ingress).
- **Source classification** / source-class tagging using only frozen classes
  (`broker_fact` | `market_fact` | `research_ai`) until architecture amends.
- **Immutable provider payloads**: capture provider responses into immutable
  ingress records (no in-place rewrite of payload bytes/fields after
  acceptance).
- Failure, outage, rate/availability signaling for providers it talks to.
- Adapter slots for broker and market providers over time.
- Strict separation so research AI transport, if later classified at this edge,
  **never** elevates research output to primary fact.

### 4.2 PF-M1-only responsibilities (first implementation)

PF-M1 implements **only**:

1. **KB Open API** broker ingress.
2. Provider Interface sufficient for that adapter (and future adapters without
   redesign of the interface intent).
3. Source-class tagging for produced broker ingress records as `broker_fact`.
4. Immutable broker provider payloads ready for **downstream Fact Store**
   consumption (Gateway does **not** own Fact Store).
5. Outage / failure / health signaling for that broker path.

### 4.3 Wire-shape rule (replaces unconstrained “provider normalization”)

**Allowed:** map KB Open API wire responses into a common **immutable provider
payload envelope** (provider id, source class, collected_at, status, payload
body, error diagnostics).

**Forbidden under any “normalization” name:**

- semantic extraction;
- entity resolution;
- portfolio or market snapshot composition;
- research synthesis or opinion shaping;
- identity mutation of domain subjects;
- inventing missing holdings, balances, prices, or fills;
- converting research AI text into broker/market facts.

### 4.4 Explicit non-responsibilities (summary)

Gateway does **not**: plan research, store evidence, produce CIO stances,
approve capital, execute trades, persist Fact Store history, or replace
Stage 1/2 research execution ownership.

---

## 5. Provider Interface

### 5.1 Purpose

The **Provider Interface** is the common adapter contract at the Gateway edge.
Adapters implement it; PF-M1 ships one adapter (KB Open API).

### 5.2 Contract intent (architecture-level)

An adapter implementation must:

| Capability | Rule |
| --- | --- |
| **Identity** | Expose a stable nonblank `provider_id` (e.g. broker adapter identity for KB Open API) |
| **Source class declaration** | Declare the source class of successful fact-class payloads it produces (`broker_fact` for KB Open API) |
| **Fetch / collect** | Perform authenticated request(s) and return **either** a successful immutable envelope **or** a structured failure/outage signal — never a silent empty “success” with invented body |
| **Health** | Support a health/availability probe or last-known health snapshot for that provider path |
| **No domain mutation** | Not construct domain Portfolio\* / Evidence\* objects; not write Fact Store |

### 5.3 Interface non-goals

The Provider Interface does **not**:

- schedule 24/7 jobs (orchestration outside PF-M1);
- decide IRO run starts;
- place broker orders (Broker Execution);
- abstract research AI committee multi-call completion (Stage 1/2 / IRO);
- define Fact Store append APIs.

### 5.4 Multi-adapter readiness without PF-M1 multi-adapter delivery

The interface exists so later broker or market adapters can plug in without
redesigning the envelope or source-class model. **PF-M1 does not implement
those adapters.**

---

## 6. KB Open API Adapter

### 6.1 Purpose

The **KB Open API Adapter** is the sole PF-M1 adapter. It is the first broker
ingress path into JOO’s primary fact source class.

### 6.2 Responsibilities

- Authenticate to KB Open API using the authentication boundary (§7).
- Issue read-oriented broker fact requests required for later Fact Store /
  portfolio fact use (holdings, balances, account-state observations, and
  related broker-reported facts as exposed by the API and selected by
  authorized implementation).
- Map each wire response or transport failure into:
  - an **immutable provider payload envelope** (§8), or
  - a **failure / outage signal** (§11).
- Tag successful broker fact envelopes with source class `broker_fact`.
- Contribute health/availability observations for the KB path (§10).

### 6.3 Non-responsibilities

The KB Open API Adapter must **not**:

- place orders, cancel orders, or otherwise perform capital execution
  (Broker Execution / BX-M1);
- write to Fact Store;
- compose Portfolio Snapshot or mutate live portfolio domain objects;
- call research AI providers;
- “heal” partial outages by fabricating holdings or balances;
- perform entity resolution against JOO domain subjects beyond capturing
  broker-native identifiers **as opaque payload content**.

### 6.4 Broker-native identifiers

Broker symbols, account ids, and instrument codes in the payload body are
**opaque captured content**. Mapping them to JOO portfolio subjects is **not**
PF-M1 ownership (later Fact Store / snapshot production / domain linking).

### 6.5 Deferred adapters (explicit)

| Adapter class | PF-M1 | Deferred to |
| --- | --- | --- |
| Additional brokers | Out | Later PF gateway milestones |
| Market API adapters | Out | PF-M4 direction |
| Research AI adapters under Gateway | Out | Explicit later freeze only; Stage 1/2 retain invocation |
| News / alternative data | Out | Architecture amendment required first |

---

## 7. Authentication boundary

### 7.1 Purpose

Define where credentials and authenticated request construction live relative
to Gateway ownership — without inventing a secrets product or collapsing into
Broker Execution.

### 7.2 Boundary rules (normative)

1. **Gateway uses credentials; it does not invent secret storage.**
   Operator-supplied configuration, environment, or external secret injection
   provides broker credentials. PF-M1 architecture does not mandate a vault
   product.
2. **Authentication material must not appear in immutable payload bodies**
   intended for Fact Store handoff (no API keys, tokens, or passwords inside
   envelope `payload` or diagnostics that are stored as facts).
3. **Authenticated access is part of Layer 2 responsibility** (product
   architecture): the KB adapter constructs authenticated requests and
   observes auth failures as provider failures/outages, not as silent success.
4. **Auth failure is a provider failure class**, not a research or CIO event.
5. **Write/trading credentials** for order placement are **out of PF-M1**.
   Even if the same broker later serves BX-M1, capital write paths are Broker
   Execution ownership, not PF-M1 read-ingress ownership.
6. **No credential sharing into IRO or domain packages.** Research runtime
   must not receive broker secrets through Gateway envelopes.

### 7.3 Failure posture for authentication

| Condition | Signal |
| --- | --- |
| Missing / invalid credentials at call time | Failure signal; no synthetic holdings |
| Auth rejected by KB Open API | Failure / outage class per §11; envelope status is failure, not success |
| Transport timeout during auth or request | Outage/unavailable signaling |

---

## 8. Immutable Provider Payload Envelope

### 8.1 Purpose

The **immutable provider payload envelope** is the sole PF-M1 success-path
handoff object from wire ingress to downstream consumers (ultimately Fact
Store in PF-M2). It freezes **what was received** with **who/when/class**, not
what JOO believes economically.

### 8.2 Wire → envelope rule (normative)

```text
KB Open API wire response (or structured error)
        │
        ▼
Adapter maps fields (no semantic repair)
        │
        ▼
Immutable Provider Payload Envelope
  (frozen after acceptance; no in-place rewrite)
```

**Acceptance** means the envelope object has been constructed and validated at
the type/nonblank/enum level. After acceptance:

- field values must not be mutated in place;
- “corrections” require a **new** envelope (new collection identity / time),
  never silent overwrite of a prior accepted envelope’s body.

### 8.3 Required envelope fields (architecture contract)

| Field | Rule |
| --- | --- |
| `envelope_id` | Opaque nonblank string; identity of this ingress capture |
| `provider_id` | Nonblank; adapter/provider identity (KB Open API adapter id) |
| `source_class` | Exactly one frozen class; PF-M1 success path = `broker_fact` |
| `collected_at` | UTC collection timestamp at Gateway boundary |
| `status` | Success or failure status enum (architecture-level; exact names at implementation freeze) |
| `payload` | Immutable body capturing broker-returned structured content **or** empty/absent on pure failure paths as defined by status |
| `error_diagnostics` | Optional structured diagnostics on failure; must not contain secrets |
| Optional `request_correlation_id` | Opaque id linking attempt logs without embedding secrets |

Validation is **type / nonblank / enum / required-presence** only. No
normalization of identifiers, no trimming policies that invent identity, no
unit conversion of economic quantities beyond preserving broker-reported
representation in the payload body as received mapping allows.

### 8.4 Immutability invariants

1. Accepted envelopes are immutable value records.
2. Payload body bytes/structure after acceptance are not rewritten.
3. Source class is explicit at construction; never inferred later from payload
   text.
4. Gateway does not append envelopes to durable Fact Store history (PF-M2).
5. Gateway does not delete or revise prior envelopes it has already handed off;
   consumers treat each envelope as an append candidate.

### 8.5 Explicit ban on semantic/entity/domain normalization (remediation R2)

The envelope path is **not**:

- Knowledge Engine normalization;
- entity resolution to JOO subject ids;
- Evidence provenance `primary`/`secondary`/`unknown` (that contract is
  research-evidence plane, not provider-fact ingress class);
- portfolio composition;
- research opinion shaping.

Those remain other planes’ responsibilities.

### 8.6 Relationship to Evidence Provenance (non-collision)

| Concept | Plane | Values |
| --- | --- | --- |
| Provider Gateway **source class** | Provider & Fact ingress | `broker_fact` \| `market_fact` \| `research_ai` |
| Evidence Provenance **source_class** | Research evidence | `primary` \| `secondary` \| `unknown` |

These are **different taxonomies**. PF-M1 must not reuse or redefine
`EvidenceProvenance` enums for provider-fact tagging.

---

## 9. Source Classification

### 9.1 Normative Layer 2 source classes

Until a separate architecture amendment freezes additional classes, Provider
Gateway may use **only**:

| Source class | Truth class | Enters Fact Store as primary fact? |
| --- | --- | --- |
| `broker_fact` | Primary operational fact source | **Yes** (downstream PF-M2) |
| `market_fact` | Primary operational fact source (market plane) | **Yes** (downstream; not PF-M1 produced) |
| `research_ai` | Research artifact transport/classification only | **Never** |

### 9.2 PF-M1 tagging rules

1. KB Open API successful broker fact envelopes **must** use `broker_fact`.
2. PF-M1 **does not produce** `market_fact` envelopes (no market adapter).
3. PF-M1 **does not produce** `research_ai` envelopes (runtime deferred).
4. Source class is caller/adapter-explicit at envelope construction; Gateway
   must not infer class from free text.
5. Mis-tagged research content as `broker_fact` is an architecture defect.

### 9.3 Research AI class (deferred runtime; recorded surface) — remediation R4

Layer 2 **records** `research_ai` as a source class for platform separation:

- **Runtime ownership of research AI invocation remains Stage 1/2**
  (`AIAdapter`, `ExecutionEngine`, `Committee`) and IRO’s “when to run”
  ownership.
- PF-M1 does **not** implement research AI transport under Gateway.
- A later explicit freeze would be required to host research AI
  **connectivity classification** at the Gateway edge **without** absorbing
  Stage 1/2 packages.
- Hard rule retained: **research AI never enters Fact Store as primary
  portfolio or market truth.**

### 9.4 News and non-frozen classes — remediation R1

**News provider adapters are not authorized.**

News, social, alternative data, or any class outside
`broker_fact` | `market_fact` | `research_ai` requires a **separate
architecture amendment** that freezes source class and truth class. Silent
addition via PF-M1 is forbidden.

### 9.5 Primary-fact hard rule (from product architecture)

- Broker and market responses may enter Fact Store (when those classes are
  produced and PF-M2 exists).
- Research AI responses enter research execution / evidence paths only.
- IRO and committee paths may not invent portfolio or market state that the
  Fact Store does not support.

---

## 10. Health Check / Availability

### 10.1 Purpose

PF-M1 exposes **provider health / availability observation** for the KB Open
API path so command-center operations can distinguish “no new facts because
none requested” from “provider unavailable.”

### 10.2 Responsibilities

- Probe or record last-known availability for the KB adapter path.
- Expose a health snapshot suitable for observability consumers (read-only).
- Correlate health with recent failure/outage signals without inventing
  success.

### 10.3 Health snapshot intent (architecture-level)

| Field | Rule |
| --- | --- |
| `provider_id` | Same identity as adapter |
| `observed_at` | UTC observation time |
| `availability` | Available / degraded / unavailable (exact enum at implementation) |
| `detail` | Optional non-secret diagnostic summary |

### 10.4 Non-responsibilities

Health checks must **not**:

- trigger IRO runs;
- auto-execute broker orders;
- fabricate fact envelopes on “available”;
- double as Fact Store freshness policy (freshness policy is downstream;
  Gateway only signals provider path health).

### 10.5 Rate / availability observation

Layer 2 product responsibility includes rate/availability observation.
PF-M1 minimum is:

- record observable unavailability and auth/transport failures;
- not invent a full multi-tenant rate-limit control plane.

Broader rate-limit orchestration may extend later without redesigning the
envelope or source-class model.

---

## 11. Failure / Outage Signaling

### 11.1 Purpose

PF-M1 must **fail closed on inventing broker facts** and must **surface**
provider problems explicitly.

### 11.2 Signal classes (architecture-level)

| Class | Meaning |
| --- | --- |
| `AUTH_FAILURE` | Credentials missing, invalid, or rejected |
| `TRANSPORT_FAILURE` | Network/timeout/TLS or equivalent transport error |
| `PROVIDER_ERROR` | HTTP/API error with provider error body (captured in diagnostics, not as success payload) |
| `UNAVAILABLE` / outage | Provider path not available for fact collection |
| `RATE_LIMITED` | Provider throttling observed (when detectable) |
| `VALIDATION_FAILURE` | Wire response could not be mapped into a valid envelope without repair |

Exact enum names may be fixed at implementation; the **class intent** is
frozen.

### 11.3 Posture (normative)

1. **No synthetic holdings, balances, fills, or account state** on failure.
2. **No elevation of partial garbage to success** by silent repair.
3. Failure signals are first-class outputs alongside envelopes; consumers must
   not need to parse free-text logs to detect outage.
4. Downstream Fact Store (PF-M2) and execution planes are expected to treat
   missing/failed ingress as **staleness / fail-closed inputs**, consistent
   with product architecture failure posture — PF-M1 supplies the signals;
   it does not implement those policies inside Gateway.
5. Failures are **not** CIO events, evidence findings, or human capital
   approvals.

### 11.4 Mapping from product architecture

Platform posture: broker/market provider outage → fact freshness degrades;
Watch/Reporting surface stale/unavailable; fail closed on execution that
requires fresh facts. PF-M1 contributes the **ingress outage signal** that
makes that posture possible.

---

## 12. Upstream / Downstream

### 12.1 Upstream

**PF-M1 (first implementation):**

- External **KB Open API** (first broker)

**Package lifetime (not all PF-M1):**

- Additional broker APIs (future adapters)
- Market data providers (deferred implementation — PF-M4 direction)
- Research AI providers **only** as classified transport/connectivity edge if
  ever brought under this layer — **without** absorbing Stage 1/2 execution
  ownership

**Not upstream of Gateway:**

- IRO plans, evidence, CIO stances
- Human capital approvals
- Allocation proposals
- Development Automation manifests as runtime inputs
- News/alternative sources without architecture amendment

### 12.2 Downstream

**PF-M1 (first implementation):**

- **Fact Store consumers** of `broker_fact` immutable payloads (Fact Store
  itself is PF-M2; Gateway emits / hands off ingress records, does not become
  the store)
- **Observability** surfaces that need provider outage/freshness signals
  (read of gateway health/failure signals only)

**Package lifetime:**

- Fact Store: `broker_fact` and `market_fact` only
- Research execution infrastructure: research AI path **only** if/when
  `research_ai` is classified at this edge — **never** as Fact Store primary
  truth

**Not downstream of Gateway:**

- Evidence Store
- Operational Memory
- Contradiction Engine
- Expected Value Engine
- CIO Engine
- Human Approval
- Order tickets / Broker Execution command path as a Gateway feature
  (BX-M1 may later **use** the broker channel; trading ownership stays Layer 15)

### 12.3 Handoff semantics

```text
PF-M1 success:  Immutable envelope (broker_fact)  ──handoff──► PF-M2 Fact Store
PF-M1 failure:  Failure/outage signal             ──handoff──► Observability /
                                                              fail-closed consumers
```

PF-M1 does not require PF-M2 to exist at runtime to **construct** envelopes;
it must not **implement** PF-M2 persistence to complete PF-M1 scope.

---

## 13. Dependency Graph

### 13.1 Normative dependency direction

Dependencies point **downstream consumption** (A → B means B consumes A).

```text
[Development Automation / joo_auto]
        │ ships milestones only
        ▼
External KB Open API ──► ProviderGateway (PF-M1)
                              │
                              ├── broker_fact envelopes ──► Fact Store (PF-M2; deferred)
                              └── health/failure signals ──► Observability consumers

Fact Store ──► Portfolio Snapshot (PF-M3) ──► IRO Scanner (frozen IRO)
Fact Store ──► Market Snapshot (PF-M4) ──► Market Watch (PF-M5) ──triggers──► IRO

Stage 1/2 AIAdapter/Committee ──► research path (not Fact Store primary truth)
IRO ──► Evidence Store / Memory / Contradiction / (later EV / CIO)
CIO ──► Reporting / Human Approval ──► Broker Execution (BX-M1)
Broker Execution ── may use broker channel ──► (not PF-M1 ownership of trading)
```

### 13.2 PF-M1 internal dependency order

```text
Provider Interface
    ▲
    │ implements
KB Open API Adapter
    │ uses
Authentication boundary
    │ produces
Immutable envelope + Source class tag
    │ and/or
Health / Failure / Outage signals
```

### 13.3 Forbidden edges (normative)

| Forbidden edge | Reason |
| --- | --- |
| ProviderGateway → Fact Store ownership / append implementation | Store is PF-M2 |
| ProviderGateway → IRO run coordination | Plane separation |
| ProviderGateway → Evidence Store | Research artifacts ≠ provider facts |
| ProviderGateway → CIO / EV / Contradiction | Not ingress |
| ProviderGateway → Human Approval | Capital authority elsewhere |
| ProviderGateway → Broker Execution trading | Capital plane; BX-M1 later |
| `research_ai` envelope → Fact Store as primary fact | Hard product rule |
| IRO → ProviderGateway for inventing portfolio state | Research AI never primary truth |
| ProviderGateway → redefine domain Portfolio\*/Evidence\* contracts | Domain ownership |
| ProviderGateway → `joo_auto` runtime dependency | Automation is development-only |
| ProviderGateway → news ingest without amendment | Remediation R1 |
| ProviderGateway reimplements `AIAdapter`/`Committee`/M22 | Risk R5 |

### 13.4 Consistency with frozen planes

| Plane | Result |
| --- | --- |
| Automation M1–M3 | Untouched — development-only |
| IRO product architecture | Untouched — research lifecycle remains IRO |
| IRO-M1 / IRO-M2 | Untouched — no provider/broker scope transferred into IRO |
| JOO Product Architecture Layer 2 / PF-M1 | Governing authority for this freeze |
| Stage 1/2 research stack | Retains research provider execution ownership |

---

## 14. Deferred Responsibilities

| Deferred responsibility | Until |
| --- | --- |
| Fact Store append/persist implementation | **PF-M2** |
| Portfolio Snapshot operational production | **PF-M3** |
| Market API adapters + market facts + Market Snapshot | **PF-M4** |
| Market Watch Engine | **PF-M5** |
| Multi-broker adapters beyond KB Open API | Later PF gateway milestones |
| Research AI transport classification runtime under Gateway (without reimplementing AIAdapter) | Explicit later freeze; **not PF-M1** |
| Broker Execution using gateway broker channel | **BX-M1** + Human Approval |
| News / alternative non-frozen source classes | **Architecture amendment required first** |
| Entity resolution, Knowledge Engine normalization, Signal/Hypothesis/Thesis production | Roadmap / other planes — **never Gateway** |
| Semantic free-text → domain proposition production | Outside Provider Gateway |
| Full rate-limit control plane / multi-provider scheduling | Later ops milestones as needed |
| Order placement, cancels, trading write APIs | Broker Execution — never PF-M1 |
| IRO Evidence / Memory / Contradiction / EV / CIO | Frozen IRO plane / later IRO milestones |
| Human capital Approval recording | HA-M1 direction |
| 24/7 supervisor process topology | Stage 6 / ops architecture freezes |

---

## 15. Forbidden Responsibilities

Provider Gateway / PF-M1 **must not**:

1. Research planning, committee simulation, evidence authoring/scoring, or
   Evidence Store ownership.
2. Operational Memory, Contradiction resolution, or Expected Value assembly.
3. CIO stances, portfolio allocation decisions, or capital recommendations.
4. Trading, order routing, rebalancing, or any capital action.
5. Human Approval (capital) or Development Automation human gates.
6. Treat research AI output as Fact Store / primary portfolio or market truth.
7. Reimplement or rename `AIAdapter`, `ExecutionEngine`, `Committee`, or M22
   `ResearchOrchestrator`.
8. Own or redefine accepted domain contracts / domain math.
9. Compose Portfolio Snapshot or Market Snapshot.
10. Collapse IRO or Broker Execution into Gateway.
11. Absorb Automation M1–M3 as a runtime dependency.
12. Invent missing provider data or “heal” outages into synthetic
    holdings/prices.
13. Claim **news provider** ownership without a frozen architecture amendment.
14. Perform unconstrained provider “normalization,” entity resolution, or
    semantic extraction under any name.
15. Persist append-only fact history (Fact Store) inside Gateway.
16. Implement Market Watch wake logic or IRO scanner deltas.

---

## 16. Future PF-M2 relationship

### 16.1 Sequencing (from product architecture)

| ID | Focus | Depends on | Delivers |
| --- | --- | --- | --- |
| **PF-M1** | Provider Gateway (broker-first) | Platform arch | KB Open API ingress, source-class tagging, outage signaling, immutable envelopes |
| **PF-M2** | Fact Store (broker facts) | **PF-M1** | Append-oriented provider fact persistence + provenance |

### 16.2 Contract between PF-M1 and PF-M2

1. **PF-M1 produces; PF-M2 persists.**
   - PF-M1 owns envelope construction and health/failure signals.
   - PF-M2 owns durable append (or explicit supersession linkage) of
     provider-originated facts with provider identity, collection time, and
     provenance.

2. **Truth class handoff**
   - Only `broker_fact` (and later `market_fact`) envelopes are eligible for
     Fact Store primary-fact persistence.
   - `research_ai` is never a PF-M2 primary-fact input.

3. **No dual write ownership**
   - PF-M1 must not grow an embedded Fact Store “for convenience.”
   - PF-M2 must not re-call KB Open API as a second Gateway (it consumes
     Gateway outputs / handoff APIs defined at implementation freeze).

4. **Failure propagation**
   - PF-M2 must not invent facts when PF-M1 emits only outage/failure signals.
   - Freshness/staleness policy is a Fact Store / snapshot / execution concern
     fed by PF-M1 signals — not a license for Gateway to synthesize data.

5. **Evidence Store remains separate**
   - IRO Evidence Store is not PF-M2 and is not a PF-M1 downstream.
   - Research opinions never become broker positions via store confusion.

6. **Non-redesign**
   - PF-M2 architecture (future freeze) must extend this PF-M1 freeze and the
     product architecture Layer 3 definition without reopening IRO-M1/M2 or
     Automation M1–M3.

### 16.3 What PF-M2 must not pull backward into PF-M1

- Snapshot composition
- Watch materiality
- IRO triggering
- Retention/compaction policies that require mutating accepted envelopes
- Capital execution reconciliation logic (execution facts may later enter Fact
  Store from BX-M1; still not PF-M1 scope)

---

## 17. Risk alignment (product architecture)

| Product risk | PF-M1 mitigation |
| --- | --- |
| R1 Fact Store vs Evidence Store conflation | Gateway emits provider-fact envelopes only; no Evidence Store |
| R5 Gateway reimplements AIAdapter/Committee | Explicit non-ownership; Stage 1/2 retain research execution |
| R8 Stale facts during broker outage | Explicit outage/failure signals; no synthetic facts |
| R10 Silent redesign via platform cleanup | Frozen-input supremacy; IRO/Automation closed |

---

## 18. Document Authority

- This document is the **canonical PF-M1 implementation architecture** for
  Provider Gateway (broker-first first slice).
- It is subordinate to frozen component architectures within their scopes
  (JOO product architecture, IRO, IRO-M1, IRO-M2, Automation M1–M3,
  Constitution, accepted domain contracts).
- It incorporates all required remediations from
  `provider_gateway_candidate_boundary_review`.
- It does not authorize production implementation, commit, tag, or push.
- Subsequent PF-M2+ milestones must cite this document and obtain their own
  architecture freezes before implementation.

---

## 19. Architecture freeze summary

**PF-M1 freezes:**

- one package `ProviderGateway`;
- KB Open API as sole first adapter;
- Provider Interface + auth boundary + immutable envelope + source class
  `broker_fact` + health/failure/outage signaling;
- explicit package-lifetime vs first-implementation split;
- hard exclusions of Fact Store, snapshots, watch, Evidence, IRO, CIO,
  trading, Human Approval, news adapters, and unconstrained normalization.

**PF-M1 does not freeze:**

- production code or tests;
- Fact Store schemas;
- market adapters;
- research AI Gateway runtime;
- Broker Execution.

---

**PF-M1 ARCHITECTURE AUTHORED**
