# PF-M2 Fact Store Architecture

## Status and milestone

- Status: Architecture authored for independent review; first Fact Store
  implementation architecture freeze
- Product: JOO — 24/7 AI Investment Command Center (first consumer product)
- Plane: **Provider & Fact** (Layer 3 — Fact Store)
- Milestone: **PF-M2**
- Production package (future, not created by this document): `FactStore`
- Architecture sources of truth (frozen; must not be redesigned):
  - `JOO_CONSTITUTION.md`
  - `docs/JOO_PRODUCT_ARCHITECTURE.md` (Layer 3 / PF-M2; product composition)
  - `docs/provider/PF_M1_PROVIDER_GATEWAY_ARCHITECTURE.md` (ingress handoff)
  - `docs/INVESTMENT_RESEARCH_ORCHESTRATOR_ARCHITECTURE.md` (IRO product plane)
  - `docs/iro/IRO_M1_ARCHITECTURE.md`
  - `docs/iro/IRO_M2_ARCHITECTURE.md`
  - Automation M1–M3 architecture under `docs/automation/`
- Candidate boundary review input (remediation-bearing):
  Independent PF-M2 Fact Store Candidate Boundary Review
  (decision: **REMEDIATION REQUIRED**; all seven remediations **R1–R7** are
  incorporated in this freeze text)
- Repository boundary for this document: architecture authoring only; this
  document alone authorizes no production code, test, package scaffold,
  schema module, configuration, run artifact, or Git history mutation

This document freezes the **first implementation architecture** for PF-M2.

It does **not** redesign the approved JOO product architecture.

It does **not** redesign the Provider Gateway PF-M1 architecture.

It does **not** redesign the Investment Research Orchestrator product
architecture, IRO-M1, or IRO-M2.

It does **not** redesign Automation M1–M3, accepted domain packages, or the
Stage 1/2 research execution stack.

Implementation requires separate authorization after architecture review.
No production package is created by this document.

---

## Normative PF-M2 surface (must remain explicit)

### PF-M2 first implementation supports ONLY

| # | Responsibility |
| --- | --- |
| 1 | **Immutable append-only fact storage** of eligible Gateway envelopes |
| 2 | **Fact identity** for each stored fact record |
| 3 | **Source identity** preservation from the ingress envelope |
| 4 | **Source-class preservation** and **append eligibility enforcement** |
| 5 | **Collection timestamp preservation** from the Gateway envelope |
| 6 | **Explicit supersession linkage** (append-only version history) |
| 7 | **Retrieval API** for stored facts and history |
| 8 | **Structural integrity verification** only |

### PF-M2 first implementation source class

| Class | PF-M2 first implementation |
| --- | --- |
| `broker_fact` | **Only eligible primary-fact class** |
| `market_fact` | **Deferred** (package lifetime; not first slice) |
| `execution_fact` | **Deferred** (BX-M1 direction; not first slice) |
| `research_ai` | **Never** primary-fact append |

### PF-M2 does NOT implement

| Concern | Owner (elsewhere) |
| --- | --- |
| **Provider Gateway** ingress / envelopes | PF-M1 / Layer 2 |
| **Portfolio Snapshot** production | PF-M3 (+ accepted Portfolio\* contracts) |
| **Market Snapshot** production | PF-M4 |
| **Market Watch** Engine | PF-M5 |
| **Evidence Store** / research evidence | IRO (frozen) |
| **IRO** lifecycle | IRO / IRO-M1 / IRO-M2 (frozen) |
| **Operational Memory** | IRO (frozen) |
| **Contradiction** Engine | IRO (frozen) |
| **Expected Value** Engine | IRO (later milestones) |
| **CIO** Engine | IRO (later milestones) |
| **Trading** / Broker Execution | Layer 15 BX-M1 |
| **Human Approval** (capital) | Layer 14 Human Authority |
| Semantic normalization / entity resolution / AI inference | Outside Fact Store permanently |

---

## 1. Purpose

### 1.1 Purpose

**PF-M2** is the first implementable slice of the **Fact Store** layer in the
Provider & Fact plane.

Its purpose is to provide **universal, immutable, append-only persistence and
retrieval of provider-originated facts** that constitute primary operational
truth inputs for downstream composition and observability.

The Fact Store:

1. **stores** facts handed off from Provider Gateway;
2. **preserves** fact identity, source identity, source class, and collection
   timestamp without inventing or repairing them;
3. **records** explicit supersession / succession linkage when a newer fact
   supersedes an older one;
4. **retrieves** stored facts and their history for authorized consumers;
5. **verifies structural integrity** of stored records and append consistency.

The Fact Store does **not** create facts, interpret facts, calculate domain
meaning, perform research, or perform AI reasoning.

### 1.2 Universal platform component (package lifetime)

Fact Store is a **platform component**. At package lifetime it is intentionally
**application-agnostic**: storage and retrieval contracts are not owned by
investment-domain meaning.

Future applications (investment, brand research, product development, market
research, manufacturing, sales intelligence, and others) may **consume the
same package API** as generic provider-fact storage.

Universal reuse **does not** expand PF-M2 first-implementation scope. JOO
investment consumers are first consumers, not package owners of semantic
interpretation.

### 1.3 Explicit non-identity

PF-M2 / Fact Store is **not**:

- Provider Gateway (Layer 2 / PF-M1);
- Portfolio Snapshot or Market Snapshot production;
- Market Watch Engine;
- IRO, Evidence Store, Operational Memory, Contradiction, Expected Value, or
  CIO;
- Stage 1/2 research provider invocation;
- Broker Execution or trading;
- Human Approval (capital) or Development Automation human gates;
- a domain package, Knowledge Engine normalizer, entity resolver, or semantic
  extractor;
- an in-place mutable “current state only” cache without history;
- a second copy of external provider APIs.

### 1.4 Product plane position

PF-M2 implements Layer 3 (Fact Store) between Gateway ingress and snapshot /
observability consumers:

```text
External providers
        │
        ▼
Provider Gateway — PF-M1 (broker-first first slice)
  Immutable Provider Payload Envelope (broker_fact)
  Health / Failure / Outage signals
        │
        │  handoff of accepted eligible envelopes only
        ▼
Fact Store — PF-M2 slice
  Append-only durable storage
  Fact identity + source identity + source class + collected_at
  Explicit supersession linkage
  Retrieval API
  Structural integrity verification
        │
        │  retrieval only (no snapshot ownership)
        ▼
  [PF-M3 Portfolio Snapshot production — deferred]
  [PF-M4 Market Snapshot production — deferred]
  [Audit / replay / Reporting consumers — read-only]

IRO plane (frozen) ────────── research lifecycle; Evidence Store separate
Capital plane ─────────────── Human Approval → Broker Execution (later BX-M1)
Development Automation ───── joo_auto; builds milestones; not a runtime dep
```

### 1.5 Relationship to frozen architectures (non-redesign)

| Frozen input | Rule for PF-M2 |
| --- | --- |
| `JOO_CONSTITUTION.md` | Identity, validation-first, immutable models, single-owner responsibilities |
| `JOO_PRODUCT_ARCHITECTURE.md` Layer 3 | Governing product definition of Fact Store |
| `JOO_PRODUCT_ARCHITECTURE.md` PF-M2 row | Append-oriented provider fact persistence + provenance (broker facts first) |
| PF-M1 architecture §16 | PF-M1 produces; PF-M2 persists; no dual write; no re-call of providers |
| IRO product architecture | Untouched; Evidence Store remains IRO-owned |
| IRO-M1 / IRO-M2 | Untouched; no research memory ownership transferred into Fact Store |
| Stage 1/2 research stack | Untouched; research AI never primary fact |
| Automation M1–M3 | Untouched; development-only; not a PF-M2 runtime dependency |
| Accepted domain packages | Consume-only if ever referenced; Fact Store does not redefine them |

If any statement in this document appears to conflict with a frozen input, the
frozen input wins for its scope, and the conflict is an architecture defect
to remediate — not a silent override.

---

## 2. Scope

### 2.1 In scope (this architecture)

This architecture freezes:

1. **Purpose** and product-plane position of PF-M2 Fact Store.
2. **Package lifetime vs PF-M2 first implementation** split (remediation R1).
3. **Package ownership** and production package identity.
4. **Mandatory responsibilities** (storage, identity, provenance fields,
   supersession, retrieval, structural integrity).
5. **Append eligibility gate** (`broker_fact` only for first implementation).
6. **Append-only version history** with explicit supersession linkage
   (remediation R2).
7. **Dual-store rule** vs IRO Evidence Store (remediation R4).
8. **Upstream / Downstream** edges for PF-M2 and package lifetime.
9. **Dependency graph** and forbidden edges.
10. **Deferred responsibilities** (market_fact, execution_fact, multi-provider
    topology, snapshot/watch ownership).
11. **Forbidden responsibilities** (including research, capital, semantics).
12. **Relationship to PF-M1** (consume handoff) and **future PF-M3+** (retrieval
    consumers only).

### 2.2 Package lifetime vs PF-M2 first implementation (remediation R1)

Layer 3 as a **product layer / package lifetime** may eventually persist
additional eligible provider-fact classes. **PF-M2** is narrower.

| Concern | Package lifetime (Layer 3 direction) | PF-M2 first implementation |
| --- | --- | --- |
| Immutable append-only storage API | Yes | **Yes** |
| Fact identity / source identity / source class / `collected_at` | Yes | **Yes** |
| Explicit supersession linkage | Yes | **Yes** |
| Retrieval API | Yes | **Yes** |
| Structural integrity verification | Yes | **Yes** |
| `broker_fact` primary-fact append | Yes | **Yes — only eligible class** |
| `market_fact` primary-fact append | Yes (later milestone; after market ingress) | **No — deferred** |
| `execution_fact` (BX fills/acks) append | Yes (later; BX-M1 direction) | **No — deferred** |
| Multi-provider physical topology / tenancy packaging | Later ops freezes | **No** |
| `research_ai` as primary fact | **Never** | **Never** |
| Snapshot / Watch / IRO / capital ownership | Never | Never |
| Semantic normalization / entity resolution / AI inference | Never | Never |

**Hard split rule:** Expanding package lifetime classes or topology requires a
**later architecture freeze**. Silent expansion inside PF-M2 implementation is
forbidden.

### 2.3 Out of scope (this document and PF-M2)

- Production code, tests, package scaffold, configuration files, storage
  engines, or Git history mutation authorized by this document alone.
- Exact on-disk schema-as-code, retention TTL tables, or compaction schedules
  (may be fixed at implementation freeze without changing this boundary).
- Portfolio / Market snapshot composition and Market Watch.
- IRO run coordination, Evidence Store, memory, contradiction, EV, CIO.
- Broker order placement or capital execution.
- Market data provider re-fetch or market_fact append in first slice.
- Multi-application product features beyond a consumer-agnostic storage API.
- Semantic normalization, entity resolution, AI inference, or research AI
  elevation to primary fact.

### 2.4 Candidate review remediations incorporated

This freeze incorporates all seven required remediations from the independent
PF-M2 Fact Store Candidate Boundary Review:

| # | Remediation | Where reflected |
| --- | --- | --- |
| **R1** | Split **package lifetime (universal provider-fact store)** vs **PF-M2 first implementation (`broker_fact` only)** | Normative surface, §2.2, §16 |
| **R2** | Define **version history** as **append-only + explicit supersession/succession linkage**; forbid in-place version mutation | §5, §8 |
| **R3** | Hard **append eligibility gate**: only eligible provider-fact classes; **`research_ai` never** primary-fact append | Normative surface, §6, §9 |
| **R4** | **Dual-store rule**: Fact Store ≠ IRO Evidence Store | §10, §15 |
| **R5** | Bound **integrity verification** to structural/identity/integrity seals only | §12 |
| **R6** | **Single package ownership**; **upstream = Gateway envelopes only**; **no provider re-fetch**; **no fact invention on outage** | §3, §5.4, §13, §15 |
| **R7** | **JOO first downstream = retrieval for PF-M3+** without owning snapshot/watch; multi-app reuse is consumer-agnostic API only | §14, §15 |

---

## 3. Package ownership

### 3.1 One-package architecture

**One package with internal components.**

| Option | Verdict |
| --- | --- |
| **A. One package** | **Selected and frozen** |
| B. Several packages (identity / history / retrieval as separate packages) | Rejected for PF-M2 — invents taxonomy beyond first store slice |
| C. Implement inside `ProviderGateway` | Rejected — dual write ownership; violates PF-M1 §16 |
| D. Implement inside IRO Evidence Store | Rejected — dual-store collapse (product risk R1) |
| E. Implement inside domain packages | Rejected — domain contracts remain non-persistent |

### 3.2 Package identity

| Name | Role |
| --- | --- |
| `FactStore` | **Only** allowed PF-M2 production package name |
| `ProviderGateway` | Frozen PF-M1 package — **unchanged**; produces envelopes; does not become the store |
| `InvestmentResearchOrchestrator` | Frozen IRO package — **unchanged**; owns Evidence Store, not Fact Store |
| `ResearchOrchestrator` | Frozen M22 package — **unchanged** |
| `AIAdapter` / `ExecutionEngine` / `Committee` | Stage 1/2 research execution — **unchanged**; not Fact Store |
| Domain packages (Portfolio\*, Evidence\*, etc.) | Accepted contracts — not Fact Store ownership |

### 3.3 Ownership table

| Concern | Owner |
| --- | --- |
| This architecture document | JOO `docs/provider/` |
| Fact Store production code (future) | Package `FactStore` |
| Durable append of eligible provider facts | `FactStore` |
| Fact identity validation at store boundary | `FactStore` |
| Source identity / source class / collection timestamp preservation | `FactStore` (fields originate from Gateway envelopes) |
| Explicit supersession linkage records | `FactStore` |
| Retrieval API | `FactStore` |
| Structural integrity verification | `FactStore` |
| Provider ingress / envelope construction | `ProviderGateway` (PF-M1) — **not** Fact Store |
| Snapshot composition | PF-M3 / PF-M4 — **not** Fact Store |
| Research evidence persistence | IRO Evidence Store — **not** Fact Store |
| Domain contract definitions | Accepted domain packages — **not** Fact Store |

### 3.4 Ownership rules (normative) — remediation R6

1. **PF-M1 produces; PF-M2 persists.** Gateway owns envelope construction and
   health/failure signals. Fact Store owns durable append (or explicit
   supersession linkage) of eligible envelopes.
2. **No dual write ownership.** `ProviderGateway` must not embed Fact Store
   persistence “for convenience.” `FactStore` must not re-call external
   provider APIs as a second Gateway.
3. **No dual store ownership with IRO.** Fact Store never absorbs Evidence
   Store; Evidence Store never becomes primary broker/market truth.
4. Responsibilities are not silently transferred from frozen packages into
   Fact Store under alternate names.

---

## 4. Package responsibilities

### 4.1 Mandatory responsibilities (PF-M2)

| # | Responsibility | Rule |
| --- | --- | --- |
| 1 | **Immutable append-only fact storage** | Accepted stored facts are never rewritten in place; corrections require new append (and optional supersession link) |
| 2 | **Fact identity** | Every stored fact record has an explicit, opaque, nonblank caller-supplied (or handoff-supplied) fact identity consistent with Constitution identity rules |
| 3 | **Source identity** | Provider / ingress source identity from the envelope is preserved without mutation, trim policies that invent identity, or alias resolution |
| 4 | **Source-class preservation** | Envelope `source_class` is preserved and enforced at append; PF-M2 first slice accepts only `broker_fact` |
| 5 | **Collection timestamp preservation** | Envelope `collected_at` is preserved; store does not invent, shift, or “heal” collection time |
| 6 | **Explicit supersession linkage** | When a newer fact is declared to supersede an older fact, the store records an explicit directed link; it does not silently overwrite history |
| 7 | **Retrieval API** | Read paths by fact identity, source identity, source class, collection time window, and supersession/history linkage |
| 8 | **Structural integrity verification** | Verify identity completeness, required-field presence, append consistency, and optional integrity seal/hash — **not** economic or semantic truth |

### 4.2 Explicit non-creation rule

Fact Store **stores** facts. It **does not**:

- create facts from health/outage signals alone;
- invent holdings, balances, prices, fills, or account state;
- interpret payload meaning;
- calculate domain quantities or materiality;
- perform research, committee execution, or AI inference;
- normalize, entity-resolve, or map free text to domain subjects.

### 4.3 Constitution alignment

| Constitution theme | PF-M2 application |
| --- | --- |
| Explicit identity | Fact identity and source identity are explicit, opaque, nonblank |
| No automatic ID generation as semantic encoding | Store does not hash payload into semantic domain IDs; any store-local technical keys remain non-semantic and architecture-bounded |
| Validation-first | Append validates structural eligibility before persistence |
| Immutable models | Stored fact records and supersession links are immutable after acceptance |
| Single responsibility owner | Persistence only; no snapshot/research/capital ownership |
| Minimum milestone responsibility | `broker_fact` first slice only |

---

## 5. Stored fact record (architecture contract)

### 5.1 Purpose

The **stored fact record** is the durable unit of Fact Store history. It is the
downstream durable form of an accepted Provider Gateway immutable envelope
that passed append eligibility.

### 5.2 Required fields (architecture-level)

| Field | Rule |
| --- | --- |
| `fact_id` | Opaque nonblank string; identity of this stored fact record |
| `envelope_id` | Opaque nonblank string linking to the Gateway envelope identity when present on handoff |
| `provider_id` / source identity | Nonblank; preserved from envelope |
| `source_class` | Exactly one frozen class; PF-M2 success path = `broker_fact` |
| `collected_at` | UTC collection timestamp preserved from Gateway envelope |
| `appended_at` | UTC time of durable append acceptance at Fact Store boundary (store-owned operational time; **not** a replacement for `collected_at`) |
| `status` / content disposition | Success-path fact content only for primary facts; store does not promote failure envelopes into synthetic success facts |
| `payload` | Immutable body as handed off from eligible envelope mapping |
| Optional `integrity_seal` | Structural seal/hash over stored bytes/fields if used by integrity verification |

Exact Python type names and enums are fixed at implementation freeze. Field
**intent** is frozen here.

### 5.3 Immutability invariants

1. Accepted stored fact records are immutable after append acceptance.
2. Payload body after acceptance is not rewritten.
3. Source class is not reclassified after append.
4. `collected_at` is not adjusted to “improve freshness.”
5. Deletion of prior history is out of PF-M2 first implementation; any future
   retention/compaction must not mutate retained records’ meaning and requires
   a separate freeze if it changes public contract.

### 5.4 Failure and outage non-invention (remediation R6)

When Gateway emits only health/failure/outage signals **without** an accepted
eligible fact envelope:

- Fact Store **must not invent** substitute facts;
- Fact Store **may** optionally record **non-fact operational signals** only if
  a later explicit contract freezes that surface — **not required for PF-M2
  first implementation**;
- absence of new facts is **not** success content.

---

## 6. Source identity and source class

### 6.1 Source identity

Source identity identifies **which provider/ingress path** produced the fact
(e.g. PF-M1 KB Open API adapter identity). Rules:

1. Preserved from Gateway envelope without semantic rewrite.
2. Not inferred from payload free text.
3. Not used as a license to re-authenticate to external providers from inside
   Fact Store.

### 6.2 Source classes (handoff taxonomy)

Provider Gateway source classes remain:

| Source class | Truth class | Enters Fact Store as primary fact? |
| --- | --- | --- |
| `broker_fact` | Primary operational fact source | **Yes — PF-M2 first implementation** |
| `market_fact` | Primary operational fact source (market plane) | **Yes later; not PF-M2 first slice** |
| `research_ai` | Research artifact transport/classification only | **Never** |

These are **different** from IRO Evidence Provenance enums
(`primary` / `secondary` / `unknown`). Fact Store must not reuse or redefine
Evidence provenance taxonomy for provider-fact storage.

### 6.3 PF-M2 first-implementation tagging / eligibility

1. Only envelopes with `source_class = broker_fact` may append as primary facts
   in PF-M2.
2. `market_fact` append is deferred until market ingress and a later freeze.
3. `research_ai` is **never** eligible for primary-fact append.
4. Mis-tagged research content as `broker_fact` is an architecture defect at
   Gateway; Fact Store rejects non-eligible classes and must not “repair” class.

---

## 7. Collection timestamp preservation

### 7.1 Rules (normative)

1. `collected_at` is the Gateway boundary collection time of the fact.
2. Fact Store preserves `collected_at` exactly as supplied on the eligible
   handoff object (subject only to structural type/presence validation).
3. Fact Store may record `appended_at` as its own append-acceptance time.
4. `appended_at` must not be substituted for `collected_at` in retrieval
   semantics that claim collection freshness.
5. Freshness / staleness **policy decisions** (when facts are “too old” for
   execution or watch) are **downstream** (snapshot / watch / execution /
   Reporting). Fact Store exposes timestamps; it does not own policy.

### 7.2 Non-responsibilities

- Clock skew correction that invents a different collection time.
- Backdating to manufacture continuity.
- Using research timestamps as broker collection times.

---

## 8. Append-only storage and version history (remediation R2)

### 8.1 Append-only rule (normative)

```text
Eligible Gateway envelope
        │
        ▼
Structural append validation + eligibility gate
        │
        ▼
Append NEW immutable stored fact record
        │
        optional explicit supersession linkage
        ▼
History = prior records + new record (+ link)
```

1. History is **append-only**.
2. “Update,” “correct,” or “replace” means **append a new fact record**, never
   mutate a prior accepted record in place.
3. There is no silent last-write-wins destruction of prior versions.

### 8.2 Version history meaning

**Version history** in PF-M2 means:

- the ordered (or link-navigable) set of immutable stored fact records that
  share an explicit succession/supersession relationship or a caller-defined
  retrieval key family;
- **not** an in-place mutable version field that overwrites prior content;
- **not** automatic inference that two payloads “mean the same subject” via
  entity resolution.

### 8.3 Explicit supersession linkage

When a caller (or authorized append path) declares that fact B supersedes
fact A:

| Property | Rule |
| --- | --- |
| Direction | Explicit directed link from superseded `fact_id` → superseding `fact_id` |
| Storage | Link is itself an immutable recorded relation (or immutable fields on the new record pointing to the prior `fact_id`) |
| Validation | Structural only: nonblank ids, no direct self-supersession, referenced ids present or reject per implementation contract |
| Non-inference | Store does **not** infer supersession from timestamps, payload similarity, or AI |
| Non-deletion | Supersession does **not** delete or rewrite the superseded record |
| Non-truth | Supersession is not economic truth, materiality, or research resolution |

This is intentionally aligned with JOO history principles and with the domain
pattern of **explicit supersession relations** (structural declaration, not
semantic judgment). Fact Store supersession is a **provider-fact history**
mechanism; it is not IRO `EvidenceSupersession` package ownership and does not
import research proposition semantics.

### 8.4 Forbidden history behaviors

- In-place rewrite of payload or provenance fields.
- Silent deletion of superseded facts in PF-M2 first implementation.
- Compaction that rewrites meaning of retained records without architecture
  amendment.
- Using supersession as contradiction resolution or majority-vote truth.

---

## 9. Append eligibility gate (remediation R3)

### 9.1 Purpose

The append eligibility gate is the hard boundary that protects primary-fact
truth class.

### 9.2 Normative gate

An input may append as a **primary fact** only if **all** hold:

1. It is a **Provider Gateway immutable payload envelope** (or the
   architecture-frozen durable handoff projection of one) — not free-form
   research text, committee output, CIO report, or human opinion.
2. `source_class` is an **eligible primary-fact class**.
3. For **PF-M2 first implementation**, eligible class = **`broker_fact` only**.
4. Required identity and provenance fields are structurally present and valid.
5. Payload is not synthesized by Fact Store from outage signals.

### 9.3 Hard rejects

| Input | Append as primary fact? |
| --- | --- |
| `broker_fact` success envelope (PF-M2) | **Yes** (if structurally valid) |
| `market_fact` envelope | **No** in PF-M2 first slice (deferred) |
| `research_ai` envelope / research artifact | **Never** |
| Committee / Evidence / Memory / Contradiction / EV / CIO outputs | **Never** |
| Gateway failure/outage signal alone | **Never** (no invention) |
| Domain Portfolio\* objects invented without Gateway envelope | **Never** |

### 9.4 research_ai ban (product hard rule)

**Research AI is never the primary truth.** Research AI outputs enter research
execution / Evidence paths only. They must not append to Fact Store as primary
portfolio or market facts under any alternate field name.

---

## 10. Dual-store rule (remediation R4)

### 10.1 Normative distinction

| Store | Content | Truth class | Owner |
| --- | --- | --- | --- |
| **Fact Store** (`FactStore`) | Broker/market (and later execution) **provider facts** | Primary operational truth inputs | Provider & Fact plane / PF-M2 |
| **Evidence Store** (IRO) | Research findings/reports with committee provenance | Research artifacts — **not** primary market/portfolio truth | IRO (frozen) |

### 10.2 Hard dual-store invariants

1. Fact Store ≠ Evidence Store.
2. Research opinions never overwrite or become broker/market positions via
   Fact Store.
3. Evidence Store never claims primary broker holdings/prices by renaming
   itself Fact Store.
4. Cross-plane reads (if ever) are explicit consumer contracts; they do not
   merge ownership.
5. Product architecture forbidden edge retained: **Evidence Store → overwrite
   Fact Store positions** is forbidden.

### 10.3 Why this exists

Product risk **R1** (conflating Fact Store and Evidence Store) is High.
PF-M2 freezes the store side of that mitigation without redesigning IRO.

---

## 11. Retrieval API

### 11.1 Purpose

Provide **read-only retrieval** of stored facts and history for authorized
downstream consumers without granting them write/semantic ownership.

### 11.2 Architecture-level retrieval capabilities

| Capability | Intent |
| --- | --- |
| Get by `fact_id` | Exact record fetch |
| List/filter by source identity | Provider-scoped history |
| List/filter by `source_class` | Class-scoped history (`broker_fact` in PF-M2) |
| List/filter by `collected_at` window | Time-scoped history |
| Navigate supersession / succession | Prior/next explicit links |
| Integrity check entry points | Structural verification on stored records |

Exact method names, pagination, and storage backend are implementation freeze
details. Public contract must remain retrieval-oriented and validation-first.

### 11.3 Retrieval non-responsibilities

Retrieval API must **not**:

- compose Portfolio Snapshot or Market Snapshot objects as domain products;
- apply materiality or EV calculations;
- resolve entities to JOO subjects;
- call external providers to “fill gaps”;
- rewrite history on read;
- expose secrets that must never have been stored (credentials).

### 11.4 Consumer posture

Consumers treat retrieved facts as **immutable historical records**. Snapshot
producers (PF-M3+) select and compose; they do not ask Fact Store to mean
“the current portfolio object.”

---

## 12. Structural integrity verification (remediation R5)

### 12.1 Purpose

Integrity verification protects **storage structural honesty**: that records
are complete, consistent with append rules, and optionally sealed against
silent bit-level corruption.

### 12.2 In scope (structural only)

| Check class | Examples |
| --- | --- |
| Identity completeness | Required ids nonblank exact strings |
| Required field presence | `source_class`, `collected_at`, payload presence rules |
| Append consistency | No in-place mutation detected; supersession link endpoints valid structurally |
| Optional integrity seal | Hash/seal verify over stored bytes/fields if implemented |
| Eligibility re-check on read (optional) | Reject serving records that violate frozen class rules if corrupted/miswritten |

### 12.3 Explicitly out of scope (not “integrity”)

Integrity verification must **not** mean:

- economic correctness of holdings or prices;
- materiality of change;
- investment suitability;
- semantic validity of free text;
- entity resolution success;
- Expected Value or CIO posture correctness;
- research contradiction resolution;
- “this fact is true about the market.”

Using “integrity” as a cover name for calculation, research, or AI inference
is an architecture defect.

### 12.4 Failure posture

| Condition | Posture |
| --- | --- |
| Structural validation failure on append | Reject append; do not store partial garbage as success |
| Integrity seal mismatch on read | Fail closed for that record; do not silently “repair” payload |
| Missing supersession endpoint (if required by contract) | Reject link or fail closed per implementation contract — no invented endpoints |

---

## 13. Upstream (remediation R6)

### 13.1 PF-M2 first implementation upstream

| Upstream | Role | Rule |
| --- | --- | --- |
| **Provider Gateway (PF-M1)** | Sole first-slice ingress of durable primary facts | Consumes **immutable provider payload envelopes** |
| Eligible class | `broker_fact` only | Product PF-M2 row: broker facts first |

### 13.2 Package lifetime upstream (not all PF-M2)

| Upstream | When |
| --- | --- |
| Gateway `market_fact` envelopes | After market ingress / later freeze (PF-M4 direction) |
| Broker Execution execution facts | BX-M1 direction (later) |
| Additional broker adapters via Gateway | Later gateway milestones — still **via Gateway**, not direct re-fetch |

### 13.3 Never upstream for primary fact

- `research_ai` outputs
- Committee / AIAdapter research payloads as primary truth
- Evidence Store records
- Operational Memory deltas
- Contradiction / EV / CIO outputs
- Human free-text opinions or approvals
- Development Automation manifests
- Direct external provider HTTP from inside Fact Store

### 13.4 No provider re-fetch rule (normative)

1. Fact Store **must not** authenticate to KB Open API (or any external
   provider) to obtain or “heal” facts.
2. Fact Store **must not** embed a second Provider Gateway.
3. Missing data remains missing; consumers observe absence/staleness.
4. Health/outage signals from Gateway inform fail-closed consumers; they do
   not authorize synthetic fact append.

---

## 14. Downstream (remediation R7)

### 14.1 PF-M2 first implementation downstream

| Downstream | Role | Rule |
| --- | --- | --- |
| **Portfolio Snapshot production (PF-M3)** | First JOO operational consumer of broker facts | **Retrieval only**; Fact Store does not compose snapshots |
| **Audit / replay** | History consumers | Read-only |
| **Reporting** (later) | Observability of fact state / freshness inputs | Read-only; Reporting is not system of record |

### 14.2 Package lifetime downstream (not PF-M2 ownership)

| Downstream | Rule |
| --- | --- |
| Market Snapshot production (PF-M4) | Later consumer of market facts |
| Market Watch (PF-M5) | May read facts/timestamps indirectly; does not live inside Fact Store |
| Future non-investment applications | May consume the same storage/retrieval API; must not force investment-only semantic ownership into the package |
| Broker Execution reconciliation (later) | May append execution facts later; trading ownership stays capital plane |

### 14.3 Not Fact Store downstream ownership

The following may **consume** facts only through later explicit contracts or
via snapshots; Fact Store **must not implement** them:

- Portfolio Snapshot composition logic
- Market Snapshot composition logic
- Market Watch materiality engine
- IRO lifecycle
- Evidence Store
- Operational Memory
- Contradiction Engine
- Expected Value Engine
- CIO Engine
- Human Approval
- Trading / Broker Execution command path

### 14.4 Snapshot consumers only (JOO first product path)

JOO’s first product path is:

```text
Fact Store retrieval ──► PF-M3 Portfolio Snapshot production
Fact Store retrieval ──► (later) PF-M4 Market Snapshot production
```

PF-M2 freezes **retrieval for those consumers**. It does not pull PF-M3/PF-M5
responsibilities forward.

### 14.5 Universal reuse constraint

Reuse means **consumer-agnostic storage/retrieval**. It does **not** mean:

- multi-app product features inside PF-M2;
- semantic models for brand/manufacturing/etc. inside Fact Store;
- research pipelines embedded in the store.

---

## 15. Dependency graph

### 15.1 Normative dependency direction

Dependencies point **downstream consumption** (A → B means B consumes A).

```text
[Development Automation / joo_auto]
        │ ships milestones only
        ▼
External providers ──► ProviderGateway (PF-M1)
                              │
                              ├── broker_fact envelopes ──► FactStore (PF-M2)
                              └── health/failure signals ──► Observability /
                                                            fail-closed consumers

FactStore ──retrieval──► Portfolio Snapshot production (PF-M3; deferred)
FactStore ──retrieval──► Market Snapshot production (PF-M4; deferred)
FactStore ──retrieval──► Audit / Reporting (read-only)

Stage 1/2 AIAdapter/Committee ──► research path (not Fact Store primary truth)
IRO ──► Evidence Store / Memory / Contradiction / (later EV / CIO)
CIO ──► Reporting / Human Approval ──► Broker Execution (BX-M1)
Broker Execution ── (later) execution facts ──► FactStore
```

### 15.2 PF-M2 internal dependency order

```text
Append eligibility gate
    │ accepts
Immutable stored fact record append
    │ optional
Explicit supersession linkage append
    │
Retrieval API  ←── Structural integrity verification
```

### 15.3 Forbidden edges (normative)

| Forbidden edge | Reason |
| --- | --- |
| `FactStore` → external provider re-fetch | No second Gateway (R6) |
| `FactStore` → invent facts on outage | PF-M1 §16.2 / R6 |
| `research_ai` → Fact Store primary-fact append | Product hard rule (R3) |
| Evidence Store → overwrite Fact Store positions | Dual-store (R4) |
| Fact Store → Evidence Store ownership | Dual-store (R4) |
| Fact Store → Portfolio Snapshot composition | PF-M3 (R7) |
| Fact Store → Market Snapshot composition | PF-M4 (R7) |
| Fact Store → Market Watch ownership | PF-M5 (R7) |
| Fact Store → IRO run coordination | Plane separation |
| Fact Store → CIO / EV / Contradiction | Not store |
| Fact Store → Human Approval | Capital authority elsewhere |
| Fact Store → Broker Execution trading | Capital plane |
| Fact Store → semantic normalization / entity resolution / AI inference | Forbidden permanently |
| Fact Store → `joo_auto` runtime dependency | Automation is development-only |
| `ProviderGateway` → Fact Store ownership / append implementation | Store is PF-M2 (PF-M1 freeze retained) |
| In-place history mutation disguised as “versioning” | Remediation R2 |

### 15.4 Consistency with frozen planes

| Plane | Result |
| --- | --- |
| Automation M1–M3 | Untouched — development-only |
| IRO product architecture | Untouched — research lifecycle remains IRO |
| IRO-M1 / IRO-M2 | Untouched — Evidence Store remains IRO |
| PF-M1 Provider Gateway | Untouched — produces envelopes; does not persist |
| JOO Product Architecture Layer 3 / PF-M2 | Governing authority for this freeze |
| Stage 1/2 research stack | Retains research execution; never primary fact |

---

## 16. Deferred responsibilities

| Deferred responsibility | Until |
| --- | --- |
| `market_fact` primary-fact append | Market ingress + later freeze (**PF-M4 direction**) |
| Portfolio Snapshot operational production | **PF-M3** |
| Market Snapshot operational production | **PF-M4** |
| Market Watch Engine / materiality policy | **PF-M5** |
| Execution facts from Broker Execution | **BX-M1** (+ Human Approval path) |
| Multi-provider physical topology / multi-broker store topology | Later PF / ops freezes |
| Cross-application tenancy packaging and multi-product deployment | Outside PF-M2 first slice |
| Exact schema-as-code, retention TTL, non-mutating compaction details | Implementation freeze / residual open work |
| Optional durable recording of non-fact health/outage signals inside store | Explicit later contract if ever needed |
| News / non-frozen source classes | Architecture amendment required first (Gateway + store) |
| Entity resolution, Knowledge Engine normalization, Signal/Hypothesis/Thesis | Roadmap / other planes — **never Fact Store** |
| Freshness policy decisions for execution fail-closed thresholds | Snapshot / watch / execution / Reporting planes |
| IRO Evidence / Memory / Contradiction / EV / CIO | Frozen IRO plane / later IRO milestones |
| Human capital Approval recording | HA-M1 direction |
| 24/7 supervisor process topology | Stage 6 / ops architecture freezes |

### Deferred classes (explicit)

PF-M2 first implementation supports:

- **`broker_fact` only**

Deferred:

- **`market_fact`**
- **`execution_fact`**
- **multi-provider topology**

---

## 17. Forbidden responsibilities

Fact Store / PF-M2 **must not**:

1. **Portfolio Snapshot** production or domain Portfolio\* composition.
2. **Market Snapshot** production.
3. **Market Watch** / materiality engine ownership.
4. **IRO** lifecycle ownership or run coordination.
5. **Evidence Store** ownership or research-evidence-as-primary-fact.
6. **Operational Memory** ownership.
7. **Contradiction** resolution or majority-vote truth.
8. **Expected Value** assembly.
9. **CIO** synthesis or research posture reports.
10. **Human Approval** (capital) or Development Automation human gates.
11. **Trading**, order routing, rebalancing, or any capital action.
12. **Semantic normalization**, entity resolution, free-text → structured
    meaning, or Knowledge Engine normalization.
13. **AI inference** / research AI elevation to primary fact.
14. Create, invent, heal, or synthesize facts on provider outage.
15. Re-call external provider APIs as a second Gateway.
16. In-place rewrite or silent history mutation.
17. Absorb Automation M1–M3 as a runtime dependency.
18. Redesign PF-M1, IRO, IRO-M1, IRO-M2, Automation M1–M3, or product
    architecture under a “platform cleanup” label.
19. Claim news/alternative non-frozen source classes without architecture
    amendment.
20. Use “integrity verification” as a cover for semantic or investment
    correctness checks.

---

## 18. Relationship to PF-M1 and future milestones

### 18.1 Sequencing (from product architecture)

| ID | Focus | Depends on | Delivers |
| --- | --- | --- | --- |
| **PF-M1** | Provider Gateway (broker-first) | Platform arch | KB Open API ingress, source-class tagging, outage signaling, immutable envelopes |
| **PF-M2** | Fact Store (broker facts) | **PF-M1** | Append-oriented provider fact persistence + provenance |
| **PF-M3** | Portfolio Snapshot production | PF-M2 + Portfolio\* contracts | Operational producer from retrieved facts |
| **PF-M4** | Market API + Market Snapshot | PF-M1/M2 | Market facts → market snapshots |
| **PF-M5** | Market Watch Engine | PF-M3/M4 | Material watch events |

### 18.2 Contract between PF-M1 and PF-M2 (retained and bound)

1. **PF-M1 produces; PF-M2 persists.**
2. **Truth class handoff:** only eligible provider-fact classes; PF-M2 first
   slice = `broker_fact` only; `research_ai` never.
3. **No dual write ownership.**
4. **Failure propagation:** no fact invention on outage-only signals.
5. **Evidence Store remains separate.**
6. **Non-redesign:** this freeze extends PF-M1 and product Layer 3 without
   reopening IRO-M1/M2 or Automation M1–M3.

### 18.3 What PF-M3+ must not pull backward into PF-M2

- Snapshot field composition and domain validation ownership
- Watch materiality policy
- IRO triggering
- Capital execution reconciliation policy (beyond later execution-fact append)
- Entity resolution required for storage

### 18.4 Handoff semantics

```text
PF-M1 success:  Immutable envelope (broker_fact)
                    ──append eligible──► PF-M2 stored fact (+ optional supersession link)
PF-M1 failure:  Failure/outage signal
                    ──no synthetic fact──► Observability / fail-closed consumers

PF-M2 retrieval ──► PF-M3+ snapshot producers / audit / Reporting
```

PF-M2 does not require PF-M3 to exist at runtime to **append** facts; it must
not **implement** PF-M3 composition to complete PF-M2 scope.

---

## 19. Risk alignment

| Risk | Severity | PF-M2 mitigation |
| --- | --- | --- |
| Product R1 Fact Store vs Evidence Store conflation | High | Dual-store rule (R4); separate package; research never primary fact (R3) |
| In-place “versioning” destroys audit history | High | Append-only + explicit supersession only (R2) |
| Scope collapse: lifetime vs first slice | High | R1 split; `broker_fact` only for PF-M2 |
| Second Gateway / provider re-fetch from store | High | R6 upstream rule |
| Synthetic facts during outage → bad snapshots/execution | High | Non-invention rule; timestamps preserved not healed |
| “Integrity” becomes semantic/EV engine | Medium | R5 structural-only bound |
| Snapshot/Watch pull-forward into store | High | R7 retrieval-only downstream |
| Silent redesign of frozen IRO/Automation | High | Frozen-input supremacy; forbidden responsibilities |
| Universal reuse misread as multi-product feature dump | Medium | Consumer-agnostic API only; no extra product features in PF-M2 |

---

## 20. Document Authority

- This document is the **canonical PF-M2 implementation architecture** for
  Fact Store (broker-fact first slice of Layer 3).
- It is subordinate to frozen component architectures within their scopes
  (Constitution, JOO product architecture, PF-M1, IRO, IRO-M1, IRO-M2,
  Automation M1–M3, accepted domain contracts).
- It incorporates all required remediations **R1–R7** from the independent
  PF-M2 Fact Store Candidate Boundary Review.
- It does not authorize production implementation, commit, tag, or push by
  itself.
- Subsequent PF-M3+ milestones must cite this document and obtain their own
  architecture freezes before implementation.

---

## 21. Architecture freeze summary

**PF-M2 freezes:**

- one package `FactStore`;
- immutable append-only storage of eligible Gateway envelopes;
- fact identity, source identity, source-class preservation, collection
  timestamp preservation;
- explicit supersession linkage as the only version-history mechanism;
- retrieval API;
- structural integrity verification only;
- first implementation eligibility = **`broker_fact` only**;
- dual-store separation from IRO Evidence Store;
- Gateway-only upstream with no provider re-fetch and no outage invention;
- snapshot/watch/IRO/capital as non-owned; JOO first consumers are retrieval
  consumers (PF-M3+).

**PF-M2 does not freeze:**

- production code or tests;
- exact storage engine or schema module layout;
- `market_fact` / `execution_fact` append;
- multi-provider topology;
- Portfolio Snapshot / Market Snapshot / Market Watch;
- research, evidence, memory, contradiction, EV, CIO, trading, human capital
  approval.

**Explicit first implementation support:**

- `broker_fact` only

**Explicit deferred:**

- `market_fact`
- `execution_fact`
- multi-provider topology

**Explicit forbidden:**

- Portfolio Snapshot, Market Snapshot, Market Watch, IRO, Evidence Store,
  Memory, Contradiction, Expected Value, CIO, Trading, Human Approval,
  semantic normalization, entity resolution, AI inference

---

**PF-M2 ARCHITECTURE AUTHORED**
