# PF-M3 Portfolio Snapshot Architecture

## Status and milestone

- Status: Architecture authored for independent review; first Portfolio Snapshot
  **operational production** architecture freeze
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Provider & Fact** (Layer 4 — Portfolio Snapshot operational
  production) + **consume-only** accepted Portfolio\* domain structure
- Milestone: **PF-M3**
- Production package (future, not created by this document):
  `PortfolioSnapshotProducer`
- Architecture sources of truth (frozen; must not be redesigned):
  - `JOO_CONSTITUTION.md`
  - `docs/JOO_PRODUCT_ARCHITECTURE.md` (Layer 4 / PF-M3; product composition)
  - `docs/provider/PF_M1_PROVIDER_GATEWAY_ARCHITECTURE.md` (ingress only;
    not a PF-M3 upstream)
  - `docs/provider/PF_M2_FACT_STORE_ARCHITECTURE.md` (sole upstream retrieval)
  - Accepted Portfolio\* domain packages (structure ownership remains with
    those packages)
  - `docs/INVESTMENT_RESEARCH_ORCHESTRATOR_ARCHITECTURE.md` (IRO product plane)
  - `docs/iro/IRO_M1_ARCHITECTURE.md`
  - `docs/iro/IRO_M2_ARCHITECTURE.md`
  - Automation M1–M3 architecture under `docs/automation/`
- Candidate boundary review input (remediation-bearing):
  Independent PF-M3 Portfolio Snapshot Candidate Boundary Review
  (decision: **REMEDIATION REQUIRED**; all eight remediations **R1–R8** are
  incorporated in this freeze text)
- Repository boundary for this document: architecture authoring only; this
  document alone authorizes no production code, test, package scaffold,
  schema module, configuration, run artifact, or Git history mutation

This document freezes the **first implementation architecture** for PF-M3.

It does **not** redesign the approved JOO product architecture.

It does **not** redesign PF-M1 Provider Gateway or PF-M2 Fact Store
architectures.

It does **not** redesign accepted Portfolio\* domain packages, the Investment
Research Orchestrator product architecture, IRO-M1, or IRO-M2.

It does **not** redesign Automation M1–M3 or the Stage 1/2 research execution
stack.

Implementation requires separate authorization after architecture review.
No production package is created by this document.

---

## Normative PF-M3 surface (must remain explicit)

### PF-M3 first implementation supports ONLY

| # | Responsibility |
| --- | --- |
| 1 | **Read-only Fact Store retrieval** of stored broker facts required for portfolio composition |
| 2 | **Holdings composition** into accepted holding observation / holding snapshot structures |
| 3 | **Watchlist composition** into accepted watchlist entry structures |
| 4 | **Immutable portfolio state within one observation context** as an accepted `ExplicitPortfolioSnapshot` |
| 5 | **Validation-first production** via accepted Portfolio\* validators (exact types, declared order, exception propagation) |
| 6 | **Emission of a validated immutable portfolio snapshot** for authorized downstream consumers |

### PF-M3 first implementation composition content

| Content | PF-M3 first implementation |
| --- | --- |
| Observation Context (timeless structural ids) | **Yes** |
| Holdings composition | **Yes** |
| Watchlist composition | **Yes** (empty ordered tuple is valid partial state) |
| Cash balance as a Portfolio Snapshot domain field | **No** (R3) |
| Portfolio valuation / market value / P&L | **No** (R2) |
| Snapshot timestamp field | **No** (R4) |
| Multi-account aggregation / synthesized quantities | **No** (R5) |

### PF-M3 does NOT implement

| Concern | Owner (elsewhere) |
| --- | --- |
| **Provider Gateway** ingress / envelopes / health | PF-M1 / Layer 2 |
| **Fact Store** persistence / append / supersession | PF-M2 / Layer 3 |
| **Portfolio\*** structural model definitions | Accepted domain packages (R1) |
| **Market Snapshot** production | PF-M4 |
| **Market Watch** Engine | PF-M5 |
| **Cash domain** (dedicated balances ownership) | Deferred dedicated domain — not PF-M3 |
| **Market valuation** / prices as portfolio truth | Market plane / PF-M4 direction — not PF-M3 |
| **Evidence Store** / research evidence | IRO (frozen) |
| **IRO** lifecycle | IRO / IRO-M1 / IRO-M2 (frozen) |
| **Operational Memory** | IRO (frozen) |
| **Contradiction** Engine | IRO (frozen) |
| **Expected Value** Engine | IRO (later milestones) |
| **CIO** Engine | IRO (later milestones) |
| **Trading** / Broker Execution | Layer 15 BX-M1 |
| **Human Approval** (capital) | Layer 14 Human Authority |
| Semantic normalization / entity resolution / AI inference | Outside PF-M3 permanently |

---

## 1. Purpose

### 1.1 Purpose

**PF-M3** is the first implementable slice of **Portfolio Snapshot operational
production** in the Provider & Fact plane.

Its purpose is to produce a **validated, immutable portfolio snapshot** —
**immutable portfolio state within one observation context** — by:

1. **retrieving** provider-originated facts from Fact Store (read-only);
2. **composing** holdings and watchlist structural content using accepted
   Portfolio\* contracts;
3. **validating** the composed snapshot with accepted domain validators before
   emission;
4. **emitting** an immutable `ExplicitPortfolioSnapshot` (and nested accepted
   objects) suitable for IRO Portfolio Scanner consumption and human review.

PF-M3 maximizes **composition integrity and plane separation**. It does not
ingest from providers, persist facts, value portfolios, own cash, run research,
or execute capital actions.

### 1.2 Structure vs operational production (remediation R1)

| Plane of ownership | Owner | What it owns |
| --- | --- | --- |
| **Structure** | Accepted Portfolio\* domain packages | Models, validators, structural invariants for Portfolio Snapshot, Holding Snapshot, Holding Observation, Watchlist Entry, Membership, Position, Observation Context, Portfolio endpoint |
| **Operational production** | `PortfolioSnapshotProducer` (PF-M3) | Fact Store retrieval, composition orchestration, validation-first assembly, emission of accepted domain instances |

PF-M3 **uses** accepted Portfolio\* contracts. It does **not** redefine,
extend, or relocate structure ownership into the producer package.

Domain packages remain non-persistent, non-runtime, and non-orchestrating per
Constitution repository invariants.

### 1.3 Explicit non-identity

PF-M3 / `PortfolioSnapshotProducer` is **not**:

- Provider Gateway (Layer 2 / PF-M1);
- Fact Store (Layer 3 / PF-M2);
- a Portfolio\* domain package or a second copy of domain validators under a
  new name;
- Market Snapshot production or Market Watch Engine;
- IRO, Evidence Store, Operational Memory, Contradiction, Expected Value, or
  CIO;
- Stage 1/2 research provider invocation;
- Broker Execution or trading;
- Human Approval (capital) or Development Automation human gates;
- a valuation engine, cash ledger, or multi-account aggregator;
- a semantic normalizer, entity resolver, or AI inference surface;
- a second Provider Gateway that bypasses Fact Store (R8).

### 1.4 Product plane position

PF-M3 implements Layer 4 **operational production** between Fact Store
retrieval and snapshot consumers:

```text
External providers
        │
        ▼
Provider Gateway — PF-M1 (broker-first first slice)
  Immutable Provider Payload Envelope (broker_fact)
        │
        │  handoff of accepted eligible envelopes only
        ▼
Fact Store — PF-M2
  Append-only durable storage + retrieval API
        │
        │  read-only retrieval ONLY (sole PF-M3 upstream)
        ▼
Portfolio Snapshot production — PF-M3 slice
  PortfolioSnapshotProducer
    Read-only Fact Store retrieval
    Holdings composition
    Watchlist composition
    Validation-first assembly via accepted Portfolio* validators
    Immutable ExplicitPortfolioSnapshot emission
        │
        │  validated immutable snapshot
        ▼
  IRO Portfolio Scanner (frozen consumer)
  Reporting / Human Approval context / pre-trade read-only context (later)

IRO plane (frozen) ────────── research lifecycle; consumes snapshots
Capital plane ─────────────── Human Approval → Broker Execution (later BX-M1)
Development Automation ───── joo_auto; builds milestones; not a runtime dep
```

### 1.5 Relationship to frozen architectures (non-redesign)

| Frozen input | Rule for PF-M3 |
| --- | --- |
| `JOO_CONSTITUTION.md` | Identity, validation-first, immutable models, single-owner responsibilities; no automatic semantic ID generation |
| `JOO_PRODUCT_ARCHITECTURE.md` Layer 4 | Governing product definition of Portfolio Snapshot |
| `JOO_PRODUCT_ARCHITECTURE.md` PF-M3 row | Operational producer of validated portfolio snapshots from PF-M2 + Portfolio\* |
| PF-M1 architecture | Untouched; ingress remains Gateway; **not** a PF-M3 upstream (R8) |
| PF-M2 architecture | Sole upstream retrieval; no snapshot composition inside Fact Store |
| Accepted Portfolio\* packages | Structure ownership retained; producer consumes validators/models only (R1) |
| IRO product architecture | Untouched; Scanner consumes snapshots; IRO does not produce them |
| IRO-M1 / IRO-M2 | Untouched; scanner ordering (holdings then watchlist) remains consumer rule |
| Stage 1/2 research stack | Untouched; research AI never primary portfolio truth |
| Automation M1–M3 | Untouched; development-only; not a PF-M3 runtime dependency |

If any statement in this document appears to conflict with a frozen input, the
frozen input wins for its scope, and the conflict is an architecture defect
to remediate — not a silent override.

---

## 2. Scope

### 2.1 In scope (this architecture)

This architecture freezes:

1. **Purpose** and product-plane position of PF-M3 Portfolio Snapshot
   production.
2. **Structure vs operational production** split (remediation R1).
3. **Package ownership** and production package identity.
4. **Mandatory operational responsibilities** (retrieval, composition,
   validation-first emission).
5. **Holdings composition** vocabulary and rules (remediation R5).
6. **Watchlist composition** as first-implementation content (remediation R7).
7. **Immutable portfolio state within one observation context** as the
   product meaning of produced state (remediation R6).
8. **Provenance and time rules** (`collected_at` only; no snapshot timestamp;
   timeless Observation Context) (remediation R4).
9. **Cash non-ownership** (remediation R3) and **valuation exclusion**
   (remediation R2).
10. **Upstream** = Fact Store only; **no Provider Gateway bypass**
    (remediation R8).
11. **Downstream** edges for PF-M3.
12. **Dependency graph** and forbidden edges.
13. **Deferred responsibilities**.
14. **Forbidden responsibilities**.

### 2.2 Package lifetime vs PF-M3 first implementation

Layer 4 as a **product layer** may eventually support richer composition
sources (e.g. later fact classes once eligible in Fact Store). **PF-M3** is
narrower.

| Concern | Package lifetime (Layer 4 ops direction) | PF-M3 first implementation |
| --- | --- | --- |
| Operational production of `ExplicitPortfolioSnapshot` | Yes | **Yes** |
| Read-only Fact Store retrieval | Yes | **Yes** |
| Holdings composition | Yes | **Yes** |
| Watchlist composition | Yes | **Yes** |
| Validation-first via accepted Portfolio\* validators | Yes | **Yes** |
| Broker-fact-derived composition inputs | Yes | **Yes — first fact class** |
| Market-fact-derived portfolio fields | Never as portfolio valuation | **Never valuation** |
| Cash as Portfolio Snapshot domain field | Never until dedicated cash domain + architecture amendment | **No** |
| Multi-account aggregation / synthesized quantities | Never | **Never** |
| Provider Gateway direct calls | Never | **Never** (R8) |
| Domain structure redefinition | Never | **Never** (R1) |
| Market Snapshot / Market Watch / IRO / capital | Never | Never |

**Hard split rule:** Expanding production sources, cash domain projection, or
valuation requires a **later architecture freeze**. Silent expansion inside
PF-M3 implementation is forbidden.

### 2.3 Out of scope (this document and PF-M3)

- Production code, tests, package scaffold, configuration files, or Git
  history mutation authorized by this document alone.
- Provider ingress, authentication, envelopes, or health (PF-M1).
- Fact append, supersession, or store topology (PF-M2).
- Redefinition of Portfolio\* models or validators.
- Portfolio valuation, market pricing, cost basis, currency conversion, or
  P&L.
- Cash balance domain modeling inside Portfolio Snapshot.
- Snapshot wall-clock timestamp fields.
- Multi-account aggregation or quantity synthesis.
- Market Snapshot, Market Watch, IRO lifecycle, Evidence, CIO, trading,
  Human Approval ownership.
- Semantic normalization, entity resolution products, or AI inference.

### 2.4 Candidate review remediations incorporated

This freeze incorporates all eight required remediations from the independent
PF-M3 Portfolio Snapshot Candidate Boundary Review:

| # | Remediation | Where reflected |
| --- | --- | --- |
| **R1** | **Structure ownership remains accepted Portfolio\* domain packages**; PF-M3 owns **only operational production** | Normative surface, §1.2, §3, §4 |
| **R2** | **Remove portfolio valuation** from PF-M3 responsibilities | Normative surface, §4.3, §10, §11 |
| **R3** | **Do not own cash balance** as a Portfolio Snapshot domain field; balances remain retrieved broker facts until a dedicated cash domain exists | §5.4, §10, §11 |
| **R4** | **Do not introduce snapshot timestamp**; use fact provenance (`collected_at`) only; Observation Context remains timeless | §6, §5.2 |
| **R5** | Replace “holdings aggregation” with **“holdings composition”**; no multi-account aggregation; no synthesized quantities | §5.1, §5.3 |
| **R6** | Replace “current position state” with **“immutable portfolio state within one observation context”** | §1.1, §5, §5.5 |
| **R7** | Explicitly include **watchlist composition** (not holdings-only silent default) | Normative surface, §5.2, §5.3 |
| **R8** | **Fact Store is the only upstream**; no Provider Gateway bypass | §7, §9, §11 |

---

## 3. Package ownership

### 3.1 One-package architecture

**One package with internal components.**

| Option | Verdict |
| --- | --- |
| **A. One package** | **Selected and frozen** |
| B. Several packages (retrieval / holdings / watchlist as separate packages) | Rejected for PF-M3 — invents taxonomy beyond first production slice |
| C. Implement inside `FactStore` | Rejected — PF-M2 forbids snapshot composition ownership |
| D. Implement inside `ProviderGateway` | Rejected — plane collapse; bypasses Fact Store (R8) |
| E. Implement inside Portfolio\* domain packages | Rejected — domain contracts remain non-runtime / non-persistent (R1) |
| F. Implement inside IRO | Rejected — IRO consumes snapshots; does not produce live portfolio state |

### 3.2 Package identity

| Name | Role |
| --- | --- |
| `PortfolioSnapshotProducer` | **Only** allowed PF-M3 production package name |
| `FactStore` | Frozen PF-M2 package — **unchanged**; sole upstream retrieval source |
| `ProviderGateway` | Frozen PF-M1 package — **unchanged**; not a PF-M3 upstream |
| `InvestmentResearchOrchestrator` | Frozen IRO package — **unchanged**; consumes snapshots |
| `ResearchOrchestrator` | Frozen M22 package — **unchanged** |
| Portfolio\* domain packages | Accepted structure contracts — **not** operational production ownership |
| Stage 1/2 research stack | Unchanged; not PF-M3 |

### 3.3 Ownership table

| Concern | Owner |
| --- | --- |
| This architecture document | JOO `docs/provider/` |
| Portfolio Snapshot operational production (future) | Package `PortfolioSnapshotProducer` |
| Read-only Fact Store retrieval for composition | `PortfolioSnapshotProducer` |
| Holdings composition orchestration | `PortfolioSnapshotProducer` |
| Watchlist composition orchestration | `PortfolioSnapshotProducer` |
| Validation-first assembly / emission | `PortfolioSnapshotProducer` |
| `ExplicitPortfolioSnapshot` model + validator | **`PortfolioSnapshot` domain package** |
| Holding Snapshot / Holding Observation models + validators | **`PortfolioHoldingSnapshot` / `PortfolioHoldingObservation`** |
| Watchlist Entry / Membership / Position / Context / Portfolio models + validators | **Corresponding Portfolio\* domain packages** |
| Fact durable storage | `FactStore` (PF-M2) |
| Provider ingress / health | `ProviderGateway` (PF-M1) |
| Market Snapshot production | PF-M4 — **not** this package |
| Research lifecycle / Evidence / CIO | IRO — **not** this package |

### 3.4 Ownership rules (normative) — remediations R1 and R8

1. **Structure stays in Portfolio\*.** PF-M3 must not fork models, weaken
   validators, or invent parallel snapshot types “for ops convenience.”
2. **PF-M3 produces; Portfolio\* validates structure.** Production constructs
   exact accepted model instances and invokes accepted validators.
3. **Fact Store is the only fact upstream.** Producer must not call Provider
   Gateway, external broker APIs, or any second ingress path to obtain facts.
4. **No dual ownership of composition.** Fact Store retrieves; producer
   composes; domain packages define structure.
5. Responsibilities are not silently transferred from frozen packages into
   the producer under alternate names.

### 3.5 Frozen package structure (normative layout intent)

```text
PortfolioSnapshotProducer/
  README.md
  models/                 # production request / result / provenance attach
                          # surfaces (not domain Portfolio* redefinitions)
  validation/             # producer-boundary structural checks only
  retrieval/              # read-only Fact Store client boundary
  composition/            # holdings + watchlist composition orchestration
  production.py           # validation-first assembly entrypoints
  tests/                  # authorized only with implementation
```

Layout is normative for component boundaries and names. Exact file splitting
may vary at implementation time without changing ownership or public contract
intent.

### 3.6 Non-package rule

PF-M3 must not create sibling operational packages for “HoldingsComposer,”
“WatchlistComposer,” “SnapshotFactory,” or “PortfolioValuator.” Internal
modules only.

---

## 4. Package responsibilities

### 4.1 Mandatory responsibilities (PF-M3)

| # | Responsibility | Rule |
| --- | --- | --- |
| 1 | **Read-only Fact Store retrieval** | Retrieve stored facts and history needed for composition; never append, supersede, or mutate Fact Store |
| 2 | **Holdings composition** | Compose holding observations into an accepted holding snapshot for one observation context without multi-account aggregation or quantity synthesis (R5) |
| 3 | **Watchlist composition** | Compose ordered watchlist entries for the same portfolio/context using accepted Watchlist Entry contracts (R7) |
| 4 | **Immutable portfolio state within one observation context** | Emit one immutable accepted portfolio snapshot for one observation context — not a mutable “current live book” object (R6) |
| 5 | **Validation-first production** | Construct exact accepted Portfolio\* instances and invoke accepted validators in declared order before successful emission |
| 6 | **Provenance attachment for facts used** | Preserve fact identity / `collected_at` (and related store provenance) for facts selected into the production attempt; do not invent a snapshot timestamp field (R4) |
| 7 | **Fail-closed emission** | On missing required facts, structural failure, or domain validation failure: do not invent holdings, watchlist rows, quantities, or “healed” state |

### 4.2 Operational production only (remediation R1)

`PortfolioSnapshotProducer` is responsible for **how** accepted domain
instances are assembled at runtime from retrieved facts and explicit
production inputs.

It is **not** responsible for **what** those domain contracts mean as
structure. Meaning and structural invariants remain Portfolio\* ownership.

### 4.3 Explicit non-valuation rule (remediation R2)

PF-M3 **must not**:

- compute market value, notional, or portfolio NAV;
- attach prices, quotes, or marks to holdings as valuation outputs;
- compute P&L, cost basis, returns, or concentration metrics;
- call Market Snapshot or market facts for the purpose of valuing the
  portfolio inside this package.

Valuation and market observation remain **outside** PF-M3 (Market Snapshot /
later planes). Portfolio Snapshot validity is **structural**, not economic
completeness or market truth beyond supplied facts.

### 4.4 Constitution alignment

| Constitution theme | PF-M3 application |
| --- | --- |
| Explicit identity | `portfolio_snapshot_id`, context ids, position ids, subject ids are explicit opaque nonblank strings supplied as production inputs — not auto-hashed from payloads |
| No automatic ID generation as semantic encoding | Producer does not derive domain identities from broker symbols via hashing/inference |
| Validation-first | Domain validators run before successful emission; exact types; declared order; exception propagation |
| Immutable models | Emitted snapshots and nested objects are frozen accepted models |
| Single responsibility owner | Operational production only; structure remains Portfolio\* |
| Minimum milestone responsibility | Broker-fact-backed holdings + watchlist composition only |
| Separate identity / structure / operation | Observation Context remains structural and timeless; operation does not smuggle timestamps into domain context |

---

## 5. Snapshot composition contract

### 5.1 Vocabulary (normative) — remediations R5 and R6

| Forbidden vocabulary (do not use as architecture meaning) | Required vocabulary |
| --- | --- |
| “Holdings aggregation” | **Holdings composition** |
| “Current position state” / “live book” as product meaning | **Immutable portfolio state within one observation context** |
| Multi-account rollup | Not owned; not performed |
| Synthesized / inferred quantities | Forbidden |

**Holdings composition** means: select and project retrieved broker holding
facts into ordered accepted holding observations for **one** portfolio under
**one** observation context, preserving explicit quantities and identities
without inventing missing legs or summing across accounts.

### 5.2 Accepted emission product (first implementation)

Successful PF-M3 emission produces an accepted
`ExplicitPortfolioSnapshot` with exactly the accepted fields:

1. `portfolio_snapshot_id: str` — opaque caller-/request-supplied identity
2. `observation_context: ExplicitPortfolioObservationContext`
3. `holding_snapshot: ExplicitPortfolioHoldingSnapshot`
4. `watchlist_entries: tuple[ExplicitPortfolioWatchlistEntry, ...]`

Nested accepted contracts remain as frozen by their packages, including:

- Observation Context: `observation_context_id`, `portfolio_id` only
  (**timeless**; no timestamp field — R4)
- Holding Snapshot: context + ordered holding observations
- Holding Observation: position + context + exact `Decimal` quantity
- Watchlist Entry: accepted membership only
- Membership / Position / Portfolio endpoint contracts as required by
  validators

Empty holding collections and empty watchlist tuples are **valid** partial
portfolio state (domain invariant retained).

### 5.3 Composition rules (normative)

1. **One observation context per produced snapshot.** Composition does not
   merge multiple observation contexts into one emission.
2. **One portfolio identity** named by the observation context `portfolio_id`.
3. **Holdings composition** builds the holding snapshot from retrieved facts
   and explicit structural bindings; it does not aggregate multiple broker
   accounts into synthetic quantities (R5).
4. **Watchlist composition** is first-implementation content (R7). Watchlist
   rows are composed as accepted entries; absence is an empty tuple, not an
   implicit “holdings-only architecture.”
5. **Caller / production order is preserved** for ordered tuples. Producer
   must not silently sort for convenience after domain validation contracts
   forbid reconstruction that changes order semantics.
6. **Exact `Decimal` quantities** are preserved; no float conversion; no unit
   “cleanup” that invents economic meaning.
7. **No quantity synthesis:** missing quantity is not replaced with zero,
   prior snapshot quantity, or model-inferred quantity unless an explicit
   later architecture freeze authorizes a distinct rule (none in PF-M3).
8. **Domain alignment rules** (context id / portfolio id / membership
   alignment, position uniqueness, watchlist membership uniqueness) are
   enforced by invoking accepted validators — not by parallel producer
   heuristics.

### 5.4 Cash non-ownership (remediation R3)

| Topic | Rule |
| --- | --- |
| Cash balance as `ExplicitPortfolioSnapshot` field | **Forbidden** in PF-M3 |
| Cash as nested Portfolio\* field introduced by producer | **Forbidden** |
| Broker balance facts in Fact Store | Remain **retrieved broker facts** owned as Fact Store content |
| Dedicated cash domain | **Deferred** until an explicit cash domain architecture exists |
| Consumers needing balances | Read Fact Store (or a future cash domain product) — **not** Portfolio Snapshot fields |

Balances may be **observed as facts** by operational systems, but PF-M3 does
not project cash into the Portfolio Snapshot domain product.

### 5.5 Meaning of produced state (remediation R6)

A successful PF-M3 emission means:

> This is the **immutable portfolio state within one observation context**
> assembled from Fact Store retrieval and explicit production inputs, validated
> under accepted Portfolio\* contracts.

It does **not** mean:

- “the live broker book right now” via direct Gateway call;
- economic completeness;
- market-true valuation;
- that cash, constraints, capital buckets, or risk budgets are included;
- that research has confirmed the portfolio.

### 5.6 Production inputs (architecture-level)

A production attempt requires explicit inputs sufficient to construct accepted
models without automatic identity invention. Architecture-level required
intent:

| Input class | Intent |
| --- | --- |
| `portfolio_snapshot_id` | Opaque nonblank snapshot identity (caller-/request-supplied) |
| Observation context identities | Opaque nonblank `observation_context_id` + target `portfolio_id` |
| Fact selection criteria | How to retrieve relevant stored facts (e.g. source identity, fact ids, `collected_at` window) without re-fetching providers |
| Explicit structural bindings | Explicit mapping from selected fact content to Portfolio\* identities (membership / position / subject bindings as required) — **not** open-world entity resolution product ownership |
| Watchlist membership declarations | Explicit ordered watchlist memberships for composition (may be empty) |

Exact request object field names are fixed at implementation freeze. Input
**intent** is frozen here.

### 5.7 Explicit ban on open-world entity resolution

PF-M3 may **apply explicit caller-supplied structural bindings**. It must
**not**:

- invent a Knowledge Engine normalizer;
- resolve free-text company names to subjects via AI;
- silently alias broker symbols into portfolio subjects without explicit
  binding inputs;
- hash payload content into domain identities.

Broker-native identifiers inside fact payloads remain opaque content until
explicit bindings project them into Portfolio\* identities.

---

## 6. Time and provenance (remediation R4)

### 6.1 Normative rules

1. **Do not introduce a snapshot timestamp field** on
   `ExplicitPortfolioSnapshot` or Observation Context via PF-M3.
2. **Observation Context remains timeless** — only
   `observation_context_id` and `portfolio_id` as accepted.
3. **Fact provenance time** is `collected_at` (and related Fact Store
   provenance such as `fact_id`, source identity, optional `appended_at` for
   store operations). Producer may **record / attach which facts** (with their
   `collected_at`) were used for a production attempt.
4. Producer must **not** heal, shift, or invent `collected_at`.
5. Freshness / staleness **policy decisions** (whether facts are “too old” to
   emit a snapshot for execution or watch) may **fail closed** a production
   attempt when an explicit production policy is supplied, but PF-M3 does not
   own platform-wide freshness product policy for capital execution
   (downstream planes).
6. `appended_at` must not be substituted for `collected_at` when claiming
   collection freshness of composed inputs.

### 6.2 Production provenance surface (non-domain)

PF-M3 may emit an **operational production result** that pairs:

- the validated immutable `ExplicitPortfolioSnapshot` (domain product), and
- an operational provenance record listing fact ids / `collected_at` values
  used (producer operational concern — **not** a new domain timestamp field
  inside Portfolio Observation Context).

This operational provenance must not be smuggled into accepted domain models
as if it were structure ownership.

### 6.3 Non-responsibilities (time)

- Runtime clock as domain truth inside Observation Context.
- Snapshot “as_of” economic timestamp as a Portfolio\* field.
- Backdating composition to manufacture continuity.

---

## 7. Upstream (remediation R8)

### 7.1 Sole upstream for facts

| Upstream | Role | Rule |
| --- | --- | --- |
| **Fact Store (`FactStore`, PF-M2)** | **Only** source of provider-originated facts for composition | **Read-only retrieval** |

### 7.2 Upstream for structure

| Upstream | Role | Rule |
| --- | --- | --- |
| Accepted Portfolio\* domain packages | Models and validators | Consume-only; no redefinition |

### 7.3 Upstream for production request parameters

| Upstream | Role | Rule |
| --- | --- | --- |
| Authorized caller / orchestrator | Supplies opaque identities, selection criteria, explicit bindings, watchlist declarations | Must not require PF-M3 to invent missing structural inputs |

### 7.4 Never upstream for PF-M3 facts

- **Provider Gateway** direct calls (bypass forbidden — R8)
- External broker / market HTTP from inside the producer
- Research AI / Committee / Evidence Store records as portfolio ground truth
- Operational Memory deltas
- Contradiction / EV / CIO outputs
- Human free-text portfolio opinions
- Development Automation manifests as runtime portfolio state
- Prior IRO baseline as a substitute for Fact Store holdings truth

### 7.5 No Provider Gateway bypass rule (normative)

1. `PortfolioSnapshotProducer` **must not** authenticate to KB Open API or
   any external provider to obtain holdings.
2. `PortfolioSnapshotProducer` **must not** embed Provider Gateway.
3. `PortfolioSnapshotProducer` **must not** read Gateway envelopes that have
   not been stored via Fact Store as a side channel around PF-M2.
4. Missing facts remain missing; producer fails closed or emits only what
   explicit inputs + retrieved facts support under validation — never synthetic
   completeness.

### 7.6 Relationship to PF-M2 retrieval

PF-M3 is the first JOO operational consumer named by PF-M2 downstream rules:

```text
FactStore retrieval ──► PortfolioSnapshotProducer (PF-M3)
```

PF-M3 does not own Fact Store. PF-M2 does not own composition.

---

## 8. Downstream

### 8.1 PF-M3 first implementation downstream

| Downstream | Role | Rule |
| --- | --- | --- |
| **IRO Portfolio Scanner** | Primary research consumer of portfolio snapshot structure | Consumes validated immutable snapshot; does not produce it |
| **Reporting** (later) | Command-center presentation of portfolio state | Read-only consumer; not system of record for structure |
| **Human Approval context** (later) | Capital-relevant human review context | Read-only snapshot context; approval authority remains human plane |
| **Broker Execution pre-trade context** (later) | Read-only portfolio context before authorized execution | Not execution ownership |

### 8.2 Downstream ordering note (IRO consumer contract retained)

Frozen IRO-M1 Scanner subject encounter order remains:

1. holdings order from current snapshot, then
2. watchlist order

PF-M3 must not invent an alternate product ordering that forces IRO redesign.
Preserving caller/production order on ordered tuples supports this consumer
contract.

### 8.3 Not PF-M3 downstream ownership

The following may **consume** snapshots only through later explicit contracts;
PF-M3 **must not implement** them:

- Market Snapshot production
- Market Watch materiality engine
- IRO run coordination / Planner / Committee execution
- Evidence Store / Operational Memory / Contradiction / EV / CIO
- Human Approval decisioning
- Trading / Broker Execution command path
- Portfolio valuation services
- Cash ledger products

### 8.4 Emission immutability for consumers

Consumers treat emitted snapshots as **immutable historical composition
results** for the named observation context and snapshot identity. “Update”
means a **new** production attempt with a new snapshot identity (and
typically new fact selection / provenance), never in-place mutation of a prior
accepted snapshot.

---

## 9. Dependency graph

### 9.1 Normative dependency direction

Dependencies point **downstream consumption** (A → B means B consumes A).

```text
[Development Automation / joo_auto]
        │ ships milestones only
        ▼
External providers ──► ProviderGateway (PF-M1)
                              │
                              └── broker_fact envelopes ──► FactStore (PF-M2)

Accepted Portfolio* domain packages
        │ structure / validators only
        ▼
FactStore ──read-only retrieval──► PortfolioSnapshotProducer (PF-M3)
                                        │
                                        └── validated ExplicitPortfolioSnapshot
                                                │
                                                ├──► IRO Portfolio Scanner
                                                ├──► Reporting (later)
                                                ├──► Human Approval context (later)
                                                └──► Broker Execution pre-trade read (later)

Stage 1/2 AIAdapter/Committee ──► research path (not portfolio ground truth)
IRO ──► Evidence Store / Memory / Contradiction / (later EV / CIO)
CIO ──► Reporting / Human Approval ──► Broker Execution (BX-M1)
Broker Execution ── (later) execution facts ──► FactStore ──► next PF-M3 cycle
```

### 9.2 PF-M3 internal dependency order

```text
Production request validation (identities / selection / bindings)
    │
Read-only Fact Store retrieval
    │
Holdings composition ──► accepted Holding Snapshot instances
Watchlist composition ──► accepted Watchlist Entry instances
    │
Assemble ExplicitPortfolioSnapshot (exact accepted models)
    │
Invoke accepted Portfolio* validators (declared order)
    │ success
Emit immutable snapshot (+ operational fact provenance attachment)
```

### 9.3 Forbidden edges (normative)

| Forbidden edge | Reason |
| --- | --- |
| `PortfolioSnapshotProducer` → external provider re-fetch | No second Gateway (R8) |
| `PortfolioSnapshotProducer` → `ProviderGateway` as fact upstream | Fact Store only (R8) |
| `PortfolioSnapshotProducer` → Fact Store append/mutate | Read-only retrieval |
| `PortfolioSnapshotProducer` → redefine Portfolio\* models | Structure ownership (R1) |
| `PortfolioSnapshotProducer` → portfolio valuation / pricing engine | R2 |
| `PortfolioSnapshotProducer` → cash domain field on snapshot | R3 |
| `PortfolioSnapshotProducer` → snapshot timestamp on domain models | R4 |
| `PortfolioSnapshotProducer` → multi-account quantity synthesis | R5 |
| `PortfolioSnapshotProducer` → mutable live book ownership | R6 |
| `PortfolioSnapshotProducer` → holdings-only silent omission of watchlist contract | R7 (watchlist composition is in scope; empty is valid) |
| `PortfolioSnapshotProducer` → IRO lifecycle ownership | Plane separation |
| `PortfolioSnapshotProducer` → Evidence / Memory / Contradiction / EV / CIO | Not producer |
| `PortfolioSnapshotProducer` → Human Approval authority | Capital authority elsewhere |
| `PortfolioSnapshotProducer` → trading / order placement | Capital plane |
| `PortfolioSnapshotProducer` → semantic normalization / entity resolution product / AI inference | Forbidden permanently |
| `PortfolioSnapshotProducer` → `joo_auto` runtime dependency | Automation is development-only |
| `FactStore` → snapshot composition | Remains PF-M3 (PF-M2 freeze retained) |
| Research AI → portfolio ground truth via producer | Research never primary truth |

### 9.4 Consistency with frozen planes

| Plane | Result |
| --- | --- |
| Automation M1–M3 | Untouched — development-only |
| IRO product architecture | Untouched — research lifecycle remains IRO; Scanner consumes |
| IRO-M1 / IRO-M2 | Untouched — no snapshot production transferred into IRO |
| PF-M1 Provider Gateway | Untouched — not a PF-M3 upstream |
| PF-M2 Fact Store | Untouched — sole fact upstream; retrieval only |
| JOO Product Architecture Layer 4 / PF-M3 | Governing authority for this freeze |
| Accepted Portfolio\* packages | Structure retained; producer is operational only |
| Stage 1/2 research stack | Retains research execution; never portfolio ground truth |

---

## 10. Deferred responsibilities

| Deferred responsibility | Until |
| --- | --- |
| Dedicated **cash domain** and any cash projection product | Explicit cash domain architecture (not PF-M3) |
| Portfolio **valuation** / market marks on holdings | Market plane / PF-M4+ and/or separate valuation architecture — **not** PF-M3 |
| Market Snapshot production | **PF-M4** |
| Market Watch Engine / materiality policy | **PF-M5** |
| Composition from `market_fact` (if ever for non-valuation structural uses) | Only after market facts exist in Fact Store **and** a later freeze — never as valuation smuggling |
| Execution-fact-aware reconciliation composition rules | **BX-M1** direction + later freeze |
| Multi-portfolio batch orchestration topology | Later ops freezes |
| Platform-wide freshness policy for capital fail-closed thresholds | Snapshot/watch/execution/Reporting policy freezes |
| Automated open-world entity resolution product | Outside PF-M3 permanently (explicit bindings only here) |
| IRO Evidence / Memory / Contradiction / EV / CIO | Frozen IRO plane / later IRO milestones |
| Human capital Approval recording | HA-M1 direction |
| 24/7 supervisor process topology | Stage 6 / ops architecture freezes |
| Exact production request schema-as-code and storage of production provenance | Implementation freeze / residual open work |

### Deferred classes of work (explicit)

PF-M3 first implementation supports:

- **Operational production of holdings + watchlist composition** into
  accepted `ExplicitPortfolioSnapshot` from **Fact Store broker facts**

Deferred / excluded:

- **Cash-as-snapshot-field**
- **Valuation**
- **Snapshot domain timestamps**
- **Gateway bypass retrieval**
- **Market Snapshot / Market Watch**

---

## 11. Forbidden responsibilities

`PortfolioSnapshotProducer` / PF-M3 **must not**:

1. **Provider Gateway** ingress, envelope construction, authentication, or
   health ownership.
2. **Fact Store** append, supersession, history mutation, or store ownership.
3. **Bypass Fact Store** by calling providers or Gateway for composition inputs
   (R8).
4. **Redefine or relocate** Portfolio\* structural ownership (R1).
5. **Portfolio valuation**, NAV, marks, P&L, cost basis, or currency conversion
   ownership (R2).
6. **Own cash balance** as a Portfolio Snapshot domain field (R3).
7. **Introduce snapshot timestamp** fields into accepted domain models;
   Observation Context remains timeless (R4).
8. Perform **multi-account aggregation** or **synthesize quantities** (R5).
9. Present produced state as a mutable “**current live position book**” product
   rather than **immutable portfolio state within one observation context**
   (R6).
10. Silently redefine first slice as **holdings-only** while omitting watchlist
    composition contract (R7) — empty watchlist is valid; omission of the
    concept is not.
11. **Market Snapshot** production or market plane ownership.
12. **Market Watch** / materiality engine ownership.
13. **IRO** lifecycle ownership or run coordination.
14. **Evidence Store** ownership or research-as-portfolio-truth.
15. **Operational Memory** ownership.
16. **Contradiction** resolution or majority-vote truth.
17. **Expected Value** assembly.
18. **CIO** synthesis or research posture reports.
19. **Human Approval** (capital) or Development Automation human gates.
20. **Trading**, order routing, rebalancing, or any capital action.
21. **Semantic normalization**, free-text → structured meaning, Knowledge
    Engine normalization, or **entity resolution product** ownership.
22. **AI inference** as portfolio ground truth.
23. Invent holdings, watchlist rows, quantities, or cash to heal missing facts.
24. Absorb Automation M1–M3 as a runtime dependency.
25. Redesign PF-M1, PF-M2, IRO, IRO-M1, IRO-M2, Automation M1–M3, accepted
    Portfolio\* contracts, or product architecture under a “platform cleanup”
    label.

---

## 12. Relationship to PF-M1, PF-M2, and future milestones

### 12.1 Sequencing (from product architecture)

| ID | Focus | Depends on | Delivers |
| --- | --- | --- | --- |
| **PF-M1** | Provider Gateway (broker-first) | Platform arch | KB Open API ingress, source-class tagging, outage signaling, immutable envelopes |
| **PF-M2** | Fact Store (broker facts) | **PF-M1** | Append-oriented provider fact persistence + provenance + retrieval |
| **PF-M3** | Portfolio Snapshot production | **PF-M2 + accepted Portfolio\*** | Operational producer of validated portfolio snapshots |
| **PF-M4** | Market API + Market Snapshot | PF-M1/M2 | Market facts → market snapshots |
| **PF-M5** | Market Watch Engine | PF-M3/M4 | Material watch events |

### 12.2 Contract between PF-M2 and PF-M3

1. **PF-M2 stores and retrieves; PF-M3 composes.**
2. **Read-only:** PF-M3 never appends facts.
3. **No dual composition ownership:** Fact Store must not emit domain
   Portfolio Snapshot products as store responsibility.
4. **No dual ingress ownership:** Producer must not re-implement Gateway.
5. **Provenance:** composition retains fact `collected_at` / fact identity
   references operationally; does not rewrite store history.
6. **Non-redesign:** this freeze extends product Layer 4 without reopening
   PF-M1/M2, IRO-M1/M2, or Automation M1–M3.

### 12.3 Contract between Portfolio\* structure and PF-M3

1. **Portfolio\* owns structure; PF-M3 owns operational production** (R1).
2. Successful emission requires accepted validators to pass.
3. Producer preserves exact types, order, and exception propagation rules.
4. Partial snapshots (empty holdings and/or empty watchlist) remain valid when
   domain validators accept them.
5. Domain non-responsibilities (cash, prices, valuation, timestamps on
   Observation Context) remain non-responsibilities after PF-M3.

### 12.4 What PF-M4+ must not pull backward into PF-M3

- Market valuation as a Portfolio Snapshot field
- Market Watch materiality ownership
- IRO triggering ownership
- Cash domain invention inside Portfolio Snapshot without architecture
  amendment
- Gateway bypass “for fresher holdings”

### 12.5 Handoff semantics

```text
PF-M1 success:  Immutable envelope (broker_fact)
                    ──append eligible──► PF-M2 stored fact
PF-M2 retrieval ──► PF-M3 composition + domain validation
PF-M3 success:  ExplicitPortfolioSnapshot (+ operational fact provenance)
PF-M3 failure:  Fail closed; no synthetic holdings/watchlist/cash/valuation
```

PF-M3 does not require Market Snapshot, Market Watch, or IRO to exist at
runtime to **emit** a portfolio snapshot; it must not **implement** those
layers to complete PF-M3 scope.

---

## 13. Risk alignment

| Risk | Severity | PF-M3 mitigation |
| --- | --- | --- |
| Structure/ops ownership collapse into domain packages or god-producer | High | R1 split; one ops package; Portfolio\* retain structure |
| Valuation smuggled into “snapshot completeness” | High | R2 explicit ban; market marks out of scope |
| Cash treated as snapshot domain field without cash domain | High | R3; balances remain Fact Store broker facts |
| Snapshot timestamp rewrites timeless Observation Context | High | R4; `collected_at` provenance only |
| Multi-account aggregation invents false quantities | High | R5 composition-only; no synthesis |
| “Current state” language implies mutable live book / Gateway bypass | High | R6 immutable state within one context; R8 Fact Store only |
| Holdings-only silent scope hides watchlist consumer needs (IRO) | Medium | R7 watchlist composition in first slice (empty valid) |
| Producer re-calls providers → dual truth vs Fact Store | High | R8 sole upstream retrieval |
| Entity resolution / AI invents memberships | High | Explicit bindings only; permanent ban on open-world resolution product |
| Research AI treated as portfolio ground truth | High | Research never upstream for facts; dual-store retained upstream |
| Silent redesign of frozen PF-M1/M2/IRO/Automation | High | Frozen-input supremacy; forbidden responsibilities |
| Fail-open invention on missing facts → bad IRO/execution context | High | Fail-closed emission; no healed quantities |

---

## 14. Document Authority

- This document is the **canonical PF-M3 implementation architecture** for
  Portfolio Snapshot **operational production** (Layer 4 ops slice).
- It is subordinate to frozen component architectures within their scopes
  (Constitution, JOO product architecture, PF-M1, PF-M2, IRO, IRO-M1, IRO-M2,
  Automation M1–M3, accepted Portfolio\* domain contracts).
- It incorporates all required remediations **R1–R8** from the independent
  PF-M3 Portfolio Snapshot Candidate Boundary Review.
- It does not authorize production implementation, commit, tag, or push by
  itself.
- Subsequent PF-M4+ milestones must cite this document and obtain their own
  architecture freezes before implementation.

---

## 15. Architecture freeze summary

**PF-M3 freezes:**

- one package `PortfolioSnapshotProducer`;
- **operational production only** (structure remains accepted Portfolio\*);
- **read-only Fact Store retrieval** as the **sole fact upstream**;
- **holdings composition** and **watchlist composition**;
- emission of **immutable portfolio state within one observation context** as
  accepted `ExplicitPortfolioSnapshot`;
- **validation-first** production via accepted domain validators;
- fact provenance via **`collected_at` / fact identity** only — **no snapshot
  timestamp** and **timeless Observation Context**;
- **no valuation**, **no cash domain field**, **no multi-account aggregation**,
  **no synthesized quantities**, **no Provider Gateway bypass**.

**PF-M3 does not freeze:**

- production code or tests;
- exact production request schema module layout;
- cash domain product;
- portfolio valuation product;
- Market Snapshot / Market Watch;
- research, evidence, memory, contradiction, EV, CIO, trading, human capital
  approval.

**Explicit first implementation support:**

- Fact Store **broker facts** → holdings + watchlist composition → validated
  `ExplicitPortfolioSnapshot`

**Explicit deferred / excluded:**

- cash-as-snapshot-field
- valuation
- snapshot domain timestamps
- Gateway bypass
- market snapshot / watch ownership
