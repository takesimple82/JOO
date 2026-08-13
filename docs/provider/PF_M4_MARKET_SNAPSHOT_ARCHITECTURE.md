# PF-M4 Market Snapshot Architecture

## Status and milestone

- Status: Architecture authored for independent review; first Market Snapshot
  **operational production** architecture freeze
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Provider & Fact** (Layer 5 — Market Snapshot operational
  production) + **consume-only** accepted Market\* domain structure
  (**hard prerequisite** — not yet present in repository at this freeze)
- Milestone: **PF-M4**
- Production package (future, not created by this document):
  `MarketSnapshotProducer`
- Architecture sources of truth (frozen; must not be redesigned):
  - `JOO_CONSTITUTION.md`
  - `docs/JOO_PRODUCT_ARCHITECTURE.md` (Layer 5 / PF-M4; product composition)
  - `docs/provider/PF_M1_PROVIDER_GATEWAY_ARCHITECTURE.md` (market API
    ingress ownership; not a PF-M4 fact upstream)
  - `docs/provider/PF_M2_FACT_STORE_ARCHITECTURE.md` (sole fact upstream
    retrieval)
  - `docs/provider/PF_M3_PORTFOLIO_SNAPSHOT_ARCHITECTURE.md` (adjacent Layer 4
    ops; not a structure owner for Market Snapshot)
  - Accepted Market\* domain packages (structure ownership — **hard
    prerequisite**; freeze structure before PF-M4 production implementation)
  - `docs/INVESTMENT_RESEARCH_ORCHESTRATOR_ARCHITECTURE.md` (IRO product plane)
  - `docs/iro/IRO_M1_ARCHITECTURE.md`
  - `docs/iro/IRO_M2_ARCHITECTURE.md`
  - Automation M1–M3 architecture under `docs/automation/`
- Candidate boundary review input (remediation-bearing):
  Independent PF-M4 Market Snapshot Candidate Boundary Review
  (decision: **REMEDIATION REQUIRED**; all ten remediations **R1–R10** are
  incorporated in this freeze text)
- Repository boundary for this document: architecture authoring only; this
  document alone authorizes no production code, test, package scaffold,
  schema module, configuration, run artifact, domain package invention, or
  Git history mutation

This document freezes the **first implementation architecture** for PF-M4.

It does **not** redesign the approved JOO product architecture.

It does **not** redesign PF-M1 Provider Gateway, PF-M2 Fact Store, or PF-M3
Portfolio Snapshot architectures.

It does **not** invent or silently implement accepted Market\* domain packages
in this freeze; it records them as a **hard prerequisite** and freezes only
the **structural boundary** they must own.

It does **not** redesign the Investment Research Orchestrator product
architecture, IRO-M1, or IRO-M2.

It does **not** redesign Automation M1–M3 or the Stage 1/2 research execution
stack.

Implementation requires separate authorization after architecture review,
**and** after hard prerequisites A–C (§4) are satisfied. No production package
is created by this document.

---

## Normative PF-M4 surface (must remain explicit)

### PF-M4 first implementation supports ONLY

| # | Responsibility |
| --- | --- |
| 1 | **Read-only Fact Store retrieval** of stored `market_fact` records required for market composition |
| 2 | **Subject coverage composition** from **explicit caller-supplied bindings only** (one session profile per emission) |
| 3 | **Market observation composition** into accepted Market\* structures for that session profile |
| 4 | **Immutable market state within one session context** as accepted Market Snapshot domain product(s) |
| 5 | **Validation-first production** via accepted Market\* validators (exact types, declared order, exception propagation) |
| 6 | **Emission of a validated immutable market snapshot** for authorized downstream consumers |
| 7 | **Fail-closed emission** under explicit production policy when required facts are missing or stale |

### PF-M4 first implementation composition content (remediation R5)

| Content | PF-M4 first implementation |
| --- | --- |
| Explicit market / venue identity | **Yes** |
| Explicit instrument identity | **Yes** |
| Explicit index identity | **Only where required by accepted Market\* structure** — not a free-form index product |
| Explicit session context | **Yes** (one session profile per emission) |
| Last price | **Yes** |
| Market status | **Yes** |
| Source provenance | **Yes** (fact identity / `collected_at` / source identity from Fact Store) |
| Validation-first immutable emission | **Yes** |
| OHLC | **No** (package lifetime) |
| Bid / ask | **No** (package lifetime) |
| Volume | **No** (package lifetime) |
| Turnover | **No** (package lifetime) |
| Richer quote state | **No** (package lifetime) |
| Index observations (as a first-slice product surface) | **No** (package lifetime) |
| Native FX instrument observations | **No** (package lifetime) |
| FX conversion | **No** (later domain milestone) |
| Sector state | **No** (later domain milestone) |
| Futures / options | **No** (later domain milestone) |
| Institutional / foreign / program trading flow | **No** (later domain milestone) |

### PF-M4 does NOT implement

| Concern | Owner (elsewhere) |
| --- | --- |
| **Provider Gateway** ingress / envelopes / health / market API adapters | PF-M1 / Layer 2 (market-adapter path is a **hard prerequisite**, not producer ownership) |
| **Fact Store** persistence / append / supersession | PF-M2 / Layer 3 |
| **Market\*** structural model definitions | Accepted domain packages (R1) — **hard prerequisite** |
| **Portfolio Snapshot** production | PF-M3 |
| **Market Watch** Engine | PF-M5 (downstream only) |
| **Portfolio valuation** / PnL / NAV | Outside PF-M4 permanently for this package |
| **Evidence Store** / research evidence | IRO (frozen) |
| **IRO** lifecycle | IRO / IRO-M1 / IRO-M2 (frozen) |
| **Operational Memory** | IRO (frozen) |
| **Contradiction** Engine | IRO (frozen) |
| **Expected Value** Engine | IRO (later milestones) |
| **CIO** Engine | IRO (later milestones) |
| **Trading** / Broker Execution | Layer 15 BX-M1 |
| **Human Approval** (capital) | Layer 14 Human Authority |
| Semantic normalization / entity resolution / AI inference | Outside PF-M4 permanently |
| Automatic ticker / alias / open-world subject resolution | Outside PF-M4 permanently (R7) |
| Synthetic prices / synthetic flows / silent stale carry-forward | Forbidden permanently (R8) |

---

## 1. Purpose

### 1.1 Purpose

**PF-M4** is the first implementable slice of **Market Snapshot operational
production** in the Provider & Fact plane.

Its purpose is to produce a **validated, immutable market snapshot** —
**immutable market observation state within one session context** — by:

1. **retrieving** provider-originated `market_fact` records from Fact Store
   (read-only);
2. **composing** first-slice market observation content using accepted
   Market\* contracts and **explicit caller-supplied subject bindings**;
3. **validating** the composed snapshot with accepted domain validators before
   emission;
4. **emitting** an immutable accepted Market Snapshot domain product suitable
   for Market Watch (PF-M5), Reporting, and other authorized read-only
   consumers.

PF-M4 maximizes **composition integrity and plane separation**. It does not
ingest from market APIs, persist facts, own Market\* structure, value
portfolios, resolve tickers, run research, trigger Market Watch, or execute
capital actions.

### 1.2 Structure vs operational production (remediation R1, R2)

| Plane of ownership | Owner | What it owns |
| --- | --- | --- |
| **Structure** | Accepted Market\* domain packages | Models, validators, structural invariants for Market Snapshot and nested market observation objects (venue, instrument, session, status, last price, provenance fields as domain structure requires) |
| **Operational production** | `MarketSnapshotProducer` (PF-M4) | Fact Store retrieval, composition orchestration, validation-first assembly, fail-closed policy application, emission of accepted domain instances |

PF-M4 **uses** accepted Market\* contracts. It does **not** redefine, extend,
or relocate structure ownership into the producer package.

Domain packages remain non-persistent, non-runtime, and non-orchestrating per
Constitution repository invariants.

**Hard rule (R1):** Market Snapshot structure ownership must be frozen in
accepted Market\* domain packages **before** PF-M4 production implementation.
This architecture document does **not** implement those packages and does
**not** invent silent interim structure inside the producer.

### 1.3 Unbundle market API ingress from Market Snapshot production (R3)

| Concern | Owner | Role |
| --- | --- | --- |
| **Market API ingress** | `ProviderGateway` (PF-M1 package lifetime; market-adapter path) | External market provider connectivity; wire → immutable `market_fact` envelopes; source-class tagging; health / outage signaling |
| **market_fact persistence and retrieval eligibility** | `FactStore` (PF-M2 package lifetime) | Append-only durable storage of eligible `market_fact` records; retrieval API |
| **Market Snapshot composition** | `MarketSnapshotProducer` (PF-M4) | **Composition only** from Fact Store retrieval + explicit bindings + Market\* validators |

Product architecture row **PF-M4 — Market API + Market Snapshot** is read as a
**plane delivery sequence**, not as a license for one package to own ingress,
persistence, and composition. Ingress remains Gateway; persistence remains
Fact Store; composition alone is PF-M4.

### 1.4 Explicit non-identity

PF-M4 / `MarketSnapshotProducer` is **not**:

- Provider Gateway (Layer 2 / PF-M1);
- Fact Store (Layer 3 / PF-M2);
- Portfolio Snapshot production (Layer 4 / PF-M3);
- a Market\* domain package or a second copy of domain validators under a new
  name;
- Market Watch Engine (PF-M5);
- IRO, Evidence Store, Operational Memory, Contradiction, Expected Value, or
  CIO;
- Stage 1/2 research provider invocation;
- Broker Execution or trading;
- Human Approval (capital) or Development Automation human gates;
- a valuation engine, FX conversion engine, or portfolio PnL/NAV calculator;
- a ticker resolver, entity resolver, alias matcher, or open-world semantic
  resolution product;
- a research AI price truth surface;
- a second Provider Gateway that bypasses Fact Store (R9);
- a sibling producer family (quote producer / price producer / flow producer)
  that fragments Market Snapshot composition (R10).

### 1.5 Product plane position

PF-M4 implements Layer 5 **operational production** between Fact Store
retrieval and market snapshot consumers:

```text
External market providers
        │
        ▼
Provider Gateway — PF-M1 package lifetime (market-adapter path; prerequisite A)
  Immutable Provider Payload Envelope (market_fact)
        │
        │  handoff of accepted eligible envelopes only
        ▼
Fact Store — PF-M2 package lifetime (market_fact append eligibility; prerequisite B)
  Append-only durable storage + retrieval API
        │
        │  read-only retrieval ONLY (sole PF-M4 fact upstream)
        ▼
Market Snapshot production — PF-M4 slice
  MarketSnapshotProducer
    Read-only Fact Store retrieval (market_fact)
    Explicit caller-supplied subject bindings
    One session profile per emission
    Composition of first-slice market content
    Validation-first assembly via accepted Market* validators (prerequisite C)
    Fail-closed under explicit production policy
    Immutable Market Snapshot emission
        │
        │  validated immutable snapshot
        ▼
  Market Watch Engine (PF-M5 — downstream only; not implemented here)
  Reporting / optional research-planning context (later; read-only)

IRO plane (frozen) ────────── research lifecycle; does not produce market snapshots
Capital plane ─────────────── Human Approval → Broker Execution (later BX-M1)
Development Automation ───── joo_auto; builds milestones; not a runtime dep
```

### 1.6 Relationship to frozen architectures (non-redesign)

| Frozen input | Rule for PF-M4 |
| --- | --- |
| `JOO_CONSTITUTION.md` | Identity, validation-first, immutable models, single-owner responsibilities; no automatic semantic ID generation |
| `JOO_PRODUCT_ARCHITECTURE.md` Layer 5 | Governing product definition of Market Snapshot |
| `JOO_PRODUCT_ARCHITECTURE.md` PF-M4 row | Plane intent: market facts → market snapshots; **unbundled** per R3 |
| PF-M1 architecture | Untouched; market API ingress remains Gateway ownership when enabled; **not** a PF-M4 fact upstream (R9) |
| PF-M2 architecture | Sole fact upstream retrieval; no snapshot composition inside Fact Store; `market_fact` eligibility is package lifetime (prerequisite B) |
| PF-M3 architecture | Untouched; Portfolio Snapshot remains separate; caller may **derive bindings** from portfolio subjects outside the producer |
| Accepted Market\* packages | Structure ownership retained; producer consumes validators/models only (R1) — **must exist before production implementation** |
| IRO product architecture | Untouched; IRO does not produce market snapshots |
| IRO-M1 / IRO-M2 | Untouched |
| Stage 1/2 research stack | Untouched; research AI never primary market price truth (R8) |
| Automation M1–M3 | Untouched; development-only; not a PF-M4 runtime dependency |

If any statement in this document appears to conflict with a frozen input, the
frozen input wins for its scope, and the conflict is an architecture defect
to remediate — not a silent override.

---

## 2. Scope

### 2.1 In scope (this architecture)

This architecture freezes:

1. **Purpose** and product-plane position of PF-M4 Market Snapshot production.
2. **Structure vs operational production** split (remediations R1, R2).
3. **Unbundle** of market API ingress / Fact Store / composition (R3).
4. **Hard prerequisites A–C** that block production implementation (R4).
5. **Package ownership** and production package identity (R10).
6. **Mandatory operational responsibilities** (retrieval, composition,
   validation-first emission, fail-closed policy).
7. **First implementation content boundary** (R5).
8. **Package lifetime vs first implementation** content split (R5).
9. **Parameterized multi-session architecture** for Korea and US at minimum
   (R6).
10. **Explicit caller-supplied subject bindings only** (R7).
11. **Fail-closed missing/stale fact policy posture** (R8).
12. **Upstream** = Fact Store only; **no Provider Gateway bypass** (R9).
13. **Downstream** edges for PF-M4 (Market Watch is PF-M5 only).
14. **Dependency graph** and forbidden edges.
15. **Deferred responsibilities**.
16. **Forbidden responsibilities**.

### 2.2 Package lifetime vs PF-M4 first implementation

Layer 5 as a **product layer** and `MarketSnapshotProducer` as a **package**
may eventually support richer market observation surfaces. **PF-M4 first
implementation** is narrower.

| Concern | Package lifetime (Layer 5 ops direction) | PF-M4 first implementation |
| --- | --- | --- |
| Operational production of accepted Market Snapshot domain product | Yes | **Yes** |
| Read-only Fact Store retrieval of `market_fact` | Yes | **Yes** |
| Explicit market / venue identity | Yes | **Yes** |
| Explicit instrument identity | Yes | **Yes** |
| Explicit index identity (only if Market\* requires) | Yes | **Yes, only if structure requires** |
| Explicit session context | Yes | **Yes** (one profile per emission) |
| Last price | Yes | **Yes** |
| Market status | Yes | **Yes** |
| Source provenance attachment | Yes | **Yes** |
| Validation-first via accepted Market\* validators | Yes | **Yes** |
| Parameterized multi-session (Korea + US minimum) | Yes | **Yes** (capability; one profile per emission) |
| Fail-closed missing/stale policy | Yes | **Yes** |
| OHLC | Yes (later freeze inside package lifetime) | **No** |
| Bid / ask | Yes (later) | **No** |
| Volume | Yes (later) | **No** |
| Turnover | Yes (later) | **No** |
| Richer quote state | Yes (later) | **No** |
| Index observations product surface | Yes (later) | **No** |
| Native FX instrument observations | Yes (later) | **No** |
| FX conversion | Never as silent producer math without domain milestone | **No** (later domain milestone) |
| Sector state / futures / options / flow products | Never without later domain milestones | **No** |
| Provider Gateway direct calls | Never | **Never** (R9) |
| Domain structure redefinition | Never | **Never** (R1) |
| Portfolio Snapshot / Market Watch / IRO / capital ownership | Never | Never |

**Hard split rule:** Expanding first-slice content (OHLC, bid/ask, volume,
flows, FX conversion, etc.) requires a **later architecture freeze**. Silent
expansion inside PF-M4 first implementation is forbidden.

### 2.3 Out of scope (this document and PF-M4 production package)

- Production code, tests, package scaffold, configuration files, domain
  package creation, or Git history mutation authorized by this document alone.
- Provider ingress, authentication, market adapters, envelopes, or health
  (PF-M1 ownership — prerequisite path, not PF-M4 package body).
- Fact append, supersession, or store topology (PF-M2).
- Invention of Market\* models or validators as an interim producer-owned
  structure.
- Portfolio Snapshot production (PF-M3).
- Market Watch triggering or materiality engine (PF-M5).
- Portfolio valuation, PnL, NAV, cost basis.
- FX conversion as economic product, sector state, futures, options,
  institutional / foreign / program trading flow products.
- IRO lifecycle, Evidence, Memory, Contradiction, EV, CIO.
- Trading, Human Approval ownership.
- Semantic normalization, entity resolution products, or AI inference.
- Automatic ticker resolution, alias matching, open-world subject resolution.
- Synthetic prices, synthetic flows, silent stale carry-forward, automatic
  provider truth repair.

### 2.4 Candidate review remediations incorporated

This freeze incorporates all ten required remediations from the independent
PF-M4 Market Snapshot Candidate Boundary Review:

| # | Remediation | Where reflected |
| --- | --- | --- |
| **R1** | Freeze Market Snapshot **structure ownership** in accepted Market\* packages **before** PF-M4 production implementation | Normative surface, §1.2, §3, §4.C, §6 |
| **R2** | Explicit **structure vs operational production** split: Market\* = models/validators/invariants; producer = ops only | §1.2, §3, §5 |
| **R3** | Unbundle market API ingress from Market Snapshot production: Gateway / Fact Store / producer composition-only | §1.3, §4.A–B, §8, §9 |
| **R4** | Record hard prerequisites A–C; production implementation must not bypass them | §4 |
| **R5** | First implementation content only (venue, instrument, session, last price, status, provenance, validation-first); package lifetime and later domain milestones separated | Normative surface, §2.2, §6 |
| **R6** | Parameterized multi-session architecture; Korea + US minimum; no hard-coded single exchange/timezone/session model; one session profile per emission | §7 |
| **R7** | Subject coverage via **explicit caller-supplied bindings only**; no automatic ticker/entity/alias/open-world resolution | §6.4, §6.5, §12 |
| **R8** | Missing or stale required facts **fail closed** under explicit production policy; never synthesize prices/flows, silent stale carry-forward, auto truth repair, or research AI as price truth | §6.6, §11, §12 |
| **R9** | Fact upstream is **Fact Store only**; no Provider Gateway bypass; no direct provider HTTP/API | §8, §10, §12 |
| **R10** | **One** operational package: `MarketSnapshotProducer`; do not embed composition in Gateway, Fact Store, PortfolioSnapshotProducer, IRO, Evidence, or sibling quote/price/flow producers | §3 |

---

## 3. Package ownership

### 3.1 One-package architecture (remediation R10)

**One package with internal components.**

| Option | Verdict |
| --- | --- |
| **A. One package** | **Selected and frozen** |
| B. Several packages (quote / price / flow / session as separate producers) | Rejected for PF-M4 — invents sibling taxonomy beyond first production slice (R10) |
| C. Implement inside `FactStore` | Rejected — PF-M2 forbids snapshot composition ownership |
| D. Implement inside `ProviderGateway` | Rejected — plane collapse; bypasses Fact Store (R3, R9) |
| E. Implement inside Market\* domain packages | Rejected — domain contracts remain non-runtime / non-persistent (R1, R2) |
| F. Implement inside `PortfolioSnapshotProducer` | Rejected — Layer 4 remains portfolio composition only |
| G. Implement inside IRO / Evidence | Rejected — research plane does not produce primary market state |
| H. Embed Market Watch trigger inside producer | Rejected — PF-M5 ownership |

### 3.2 Package identity

| Name | Role |
| --- | --- |
| `MarketSnapshotProducer` | **Only** allowed PF-M4 production package name |
| `FactStore` | Frozen PF-M2 package — **unchanged**; sole fact upstream retrieval source |
| `ProviderGateway` | Frozen PF-M1 package — **unchanged** as architecture identity; market-adapter path is package-lifetime prerequisite A, **not** a PF-M4 upstream for facts |
| `PortfolioSnapshotProducer` | Frozen PF-M3 package — **unchanged**; may inform caller-side binding derivation only outside this package |
| `InvestmentResearchOrchestrator` | Frozen IRO package — **unchanged** |
| `ResearchOrchestrator` | Frozen M22 package — **unchanged** |
| Market\* domain packages | Structure contracts — **hard prerequisite**; **not** operational production ownership |
| Stage 1/2 research stack | Unchanged; not PF-M4 |

### 3.3 Ownership table

| Concern | Owner |
| --- | --- |
| This architecture document | JOO `docs/provider/` |
| Market Snapshot operational production (future) | Package `MarketSnapshotProducer` |
| Read-only Fact Store retrieval for composition | `MarketSnapshotProducer` |
| Subject coverage composition orchestration (from explicit bindings) | `MarketSnapshotProducer` |
| Session-profile-parameterized composition orchestration | `MarketSnapshotProducer` |
| Validation-first assembly / emission | `MarketSnapshotProducer` |
| Fail-closed application of explicit production freshness/presence policy | `MarketSnapshotProducer` |
| Market Snapshot model + validator | **Accepted Market\* domain package(s)** (R1) |
| Nested venue / instrument / session / observation models + validators | **Corresponding Market\* domain packages** (R1) |
| Fact durable storage / `market_fact` eligibility | `FactStore` (PF-M2) |
| Market API ingress / health / envelopes | `ProviderGateway` (PF-M1) |
| Portfolio Snapshot production | `PortfolioSnapshotProducer` (PF-M3) |
| Market Watch | PF-M5 — **not** this package |
| Research lifecycle / Evidence / CIO | IRO — **not** this package |

### 3.4 Ownership rules (normative) — remediations R1, R2, R3, R9, R10

1. **Structure stays in Market\*.** PF-M4 must not fork models, weaken
   validators, or invent parallel snapshot types “for ops convenience.”
2. **PF-M4 produces; Market\* validates structure.** Production constructs
   exact accepted model instances and invokes accepted validators.
3. **Fact Store is the only fact upstream.** Producer must not call Provider
   Gateway, external market APIs, or any second ingress path to obtain facts
   (R9).
4. **No dual ownership of composition.** Fact Store retrieves; producer
   composes; domain packages define structure; Gateway never composes (R3).
5. **One operational package only.** No quote/price/flow sibling producers
   for Market Snapshot composition (R10).
6. Responsibilities are not silently transferred from frozen packages into
   the producer under alternate names.

### 3.5 Frozen package structure (normative layout intent)

```text
MarketSnapshotProducer/
  README.md
  models/                 # production request / result / provenance attach
                          # surfaces (not domain Market* redefinitions)
  validation/             # producer-boundary structural checks only
  retrieval/              # read-only Fact Store client boundary
  composition/            # session-parameterized composition orchestration
  policy/                 # explicit fail-closed production policy surfaces
  production.py           # validation-first assembly entrypoints
  tests/                  # authorized only with implementation
```

Layout is normative for component boundaries and names. Exact file splitting
may vary at implementation time without changing ownership or public contract
intent.

### 3.6 Non-package rule

PF-M4 must not create sibling operational packages for “QuoteComposer,”
“PriceProducer,” “FlowProducer,” “SessionComposer,” “MarketValuator,” or
“TickerResolver.” Internal modules only.

---

## 4. Hard prerequisites (remediation R4)

PF-M4 **production implementation** is blocked until **all** of the following
are satisfied. Architecture authoring of this document does **not** satisfy
them. Silent interim bypass (inventing structure in the producer, calling
market APIs from the producer, or composing without `market_fact` storage) is
**forbidden**.

### 4.A Prerequisite A — Provider Gateway market-adapter path

| Field | Definition |
| --- | --- |
| **What** | A Provider Gateway market-adapter path that produces immutable `market_fact` envelopes consistent with PF-M1 envelope / source-class contracts |
| **Owner** | `ProviderGateway` (PF-M1 package lifetime; market API adapters were reserved and deferred in PF-M1 first slice) |
| **Must deliver** | Authenticated market provider ingress; wire → immutable envelope; `source_class = market_fact`; provider identity; `collected_at`; failure/outage signaling without inventing facts |
| **Must not deliver** | Market Snapshot composition; Fact Store ownership; domain Market\* structure ownership |

### 4.B Prerequisite B — Fact Store market_fact append eligibility and retrieval

| Field | Definition |
| --- | --- |
| **What** | Fact Store accepts eligible `market_fact` envelopes for append-only persistence and exposes retrieval of stored market facts and history |
| **Owner** | `FactStore` (PF-M2 package lifetime; `market_fact` was deferred in PF-M2 first slice) |
| **Must deliver** | Append eligibility for `market_fact`; fact identity; source identity/class preservation; `collected_at` preservation; retrieval API usable by producers |
| **Must not deliver** | Snapshot composition; Gateway ingress; research AI as primary fact |

### 4.C Prerequisite C — Accepted Market\* structure and validators

| Field | Definition |
| --- | --- |
| **What** | Accepted Market\* domain packages that own Market Snapshot structure, nested observation structure, models, validators, and structural invariants required by first-slice content |
| **Owner** | Domain Contract Plane — Market\* packages (to be frozen via separate domain architecture / acceptance milestones) |
| **Must deliver** | Exact models and validators sufficient for first-slice content (venue/market identity, instrument identity, session context, last price, market status, source provenance fields as domain structure requires); validation-first contracts consistent with Constitution |
| **Must not deliver** | Runtime production, Fact Store I/O, provider HTTP, Market Watch, valuation products |

**Repository state at this architecture freeze:** No accepted Market\* domain
packages are present. Prerequisite C is therefore **open** and is recorded as
a **hard blocker** for PF-M4 production implementation. This document defines
the **required structural boundary** only (§6.1–§6.3) without implementing or
silently inventing the domain package.

### 4.1 Prerequisite enforcement rule (normative)

1. PF-M4 production implementation authorization **must** cite evidence that
   A, B, and C are met (or are being implemented under their own authorized
   freezes without collapsing ownership into `MarketSnapshotProducer`).
2. Partial satisfaction (e.g. Gateway market adapter without Fact Store
   eligibility) is **not** sufficient to implement composition.
3. Temporary “direct API composition” for demos is **not** authorized (R9).
4. Temporary “producer-owned market models” are **not** authorized (R1).

---

## 5. Package responsibilities

### 5.1 Mandatory responsibilities (PF-M4)

| # | Responsibility | Rule |
| --- | --- | --- |
| 1 | **Read-only Fact Store retrieval** | Retrieve stored `market_fact` records and history needed for composition; never append, supersede, or mutate Fact Store |
| 2 | **Explicit-binding subject coverage** | Compose only subjects named by caller-supplied bindings; never auto-resolve tickers, entities, or aliases (R7) |
| 3 | **Session-parameterized composition** | Compose under an explicit session profile for the emission; support multi-session parameterization without hard-coding a single market (R6) |
| 4 | **First-slice observation composition** | Project retrieved facts into accepted Market\* observation structure for venue, instrument, session, last price, market status, and provenance (R5) |
| 5 | **Immutable market state within one session context** | Emit one immutable accepted market snapshot for one session profile / production attempt — not a mutable “live quote board” |
| 6 | **Validation-first production** | Construct exact accepted Market\* instances and invoke accepted validators in declared order before successful emission |
| 7 | **Provenance attachment for facts used** | Preserve fact identity / `collected_at` / source identity for facts selected into the production attempt; do not invent domain wall-clock fields that rewrite Market\* structure ownership |
| 8 | **Fail-closed emission** | On missing required facts, stale facts under explicit policy, structural failure, or domain validation failure: do not invent prices, statuses, subjects, or “healed” market state (R8) |

### 5.2 Operational production only (remediation R2)

`MarketSnapshotProducer` is responsible for **how** accepted domain instances
are assembled at runtime from retrieved facts and explicit production inputs.

It is **not** responsible for **what** those domain contracts mean as
structure. Meaning and structural invariants remain Market\* ownership.

### 5.3 Explicit non-valuation / non-portfolio rule

PF-M4 **must not**:

- compute portfolio market value, notional, or NAV;
- attach portfolio holdings valuation as a Market Snapshot product purpose;
- compute P&L, cost basis, returns, or concentration metrics;
- perform FX conversion into a portfolio base currency as an economic product
  (later domain milestone — not first slice);
- own Portfolio Snapshot fields or mutate portfolio state.

Market Snapshot validity is **structural and compositional** under accepted
Market\* contracts and explicit production policy — not portfolio economic
completeness.

### 5.4 Constitution alignment

| Constitution theme | PF-M4 application |
| --- | --- |
| Explicit identity | Snapshot ids, venue ids, instrument ids, session ids are explicit opaque nonblank strings supplied as production inputs / bindings — not auto-hashed from payloads |
| No automatic ID generation as semantic encoding | Producer does not derive domain identities from tickers via hashing/inference |
| Validation-first | Domain validators run before successful emission; exact types; declared order; exception propagation |
| Immutable models | Emitted snapshots and nested objects are frozen accepted models |
| Single responsibility owner | Operational production only; structure remains Market\*; ingress remains Gateway; persistence remains Fact Store |
| Minimum milestone responsibility | First-slice last price + market status + session context + identities + provenance only |
| Separate identity / structure / operation | Session context structure is Market\*; multi-session parameters are operational inputs; composition does not invent domain meaning |

---

## 6. Structure ownership and first implementation boundary

### 6.1 Required structural boundary (Market\* ownership — prerequisite C)

Until Market\* packages are accepted, the following is the **required
structural boundary** that those packages must own. PF-M4 does **not**
implement these models here.

Market\* domain ownership must cover at minimum:

1. **Market Snapshot aggregate** — immutable validated composition root for
   one production emission under accepted domain rules.
2. **Market / venue identity** — explicit opaque identity for the market or
   venue named by the emission.
3. **Instrument identity** — explicit opaque identity for each instrument
   observation included.
4. **Index identity** — only if accepted structure requires an index subject
   type for some first-slice cases; not a license for a free-form index
   product surface in PF-M4 first implementation.
5. **Session context** — explicit session identity / profile binding as domain
   structure requires (distinct from producer operational request parameters
   that select which profile to compose).
6. **Last price observation** — exact numeric type per domain contract
   (expected: exact `Decimal` if price is a domain numeric field; float
   forbidden if Constitution exact-arithmetic rules apply).
7. **Market status** — explicit status vocabulary owned by domain contracts
   (not free-text invention by the producer).
8. **Source provenance fields** — as domain structure requires for attaching
   or referencing provider-fact provenance (fact identity / source identity /
   collection time references without relocating Fact Store ownership).
9. **Validators** — validation-first, exact types, declared order, exception
   propagation, order preservation, no hidden inference.

Exact field names, nested package splits, and type identities are fixed by
the future Market\* acceptance freeze(s). PF-M4 production must consume those
contracts without forking them.

### 6.2 First implementation content (remediation R5)

Successful PF-M4 first implementation emission produces an accepted Market
Snapshot domain product whose **compositional content intent** includes only:

| Content | Rule |
| --- | --- |
| Explicit market / venue identity | Required |
| Explicit instrument identity | Required for each included instrument observation |
| Explicit index identity | Only if Market\* structure requires it for that observation class |
| Explicit session context | Required; one session profile per emission |
| Last price | Required when policy marks price as required for the subject; missing required price fails closed (R8) |
| Market status | Required when policy/structure requires it; missing required status fails closed |
| Source provenance | Required attachment/reference for facts used |
| Validation-first immutable emission | Required |

### 6.3 Package lifetime content (not first implementation)

The following may become package-lifetime content of `MarketSnapshotProducer`
**only after separate architecture freezes** that also extend Market\*
structure as needed:

- OHLC
- bid / ask
- volume
- turnover
- richer quote state
- index observations as a product surface
- native FX instrument observations

### 6.4 Later domain milestones (not PF-M4 package work alone)

The following are **later domain milestones** (and corresponding ops freezes
if needed). They are **not** PF-M4 first implementation and must not be
smuggled in as “producer helpers”:

- FX conversion
- sector state
- futures
- options
- institutional flow
- foreign investor flow
- program trading flow

### 6.5 Subject coverage and bindings (remediation R7)

Subject coverage for a production attempt is defined **only** by explicit
caller-supplied bindings.

| Rule | Statement |
| --- | --- |
| Caller-supplied only | Producer composes only subjects present in the production request bindings |
| Portfolio derivation is caller-side | A caller **may** derive bindings from a Portfolio Snapshot (holdings + watchlist subjects) **before** invoking the producer |
| Producer must not auto-resolve | No automatic ticker resolution |
| Producer must not entity-resolve | No automatic entity resolution |
| Producer must not alias-match | No symbol alias tables as hidden producer product ownership |
| Producer must not open-world resolve | No free-text / AI / Knowledge Engine resolution product inside PF-M4 |

Broker- or venue-native codes inside `market_fact` payloads remain opaque
content until **explicit bindings** project them into Market\* identities.

### 6.6 Missing or stale required facts (remediation R8)

Under an **explicit production policy** supplied with the production attempt
(or an authorized fixed policy object for the runtime), PF-M4 must **fail
closed** when required facts are missing or stale.

**Never:**

- synthesize prices;
- synthesize flows;
- carry forward stale truth **silently**;
- repair provider truth automatically;
- use research AI as price truth.

**May:**

- fail the production attempt with a structured failure;
- emit a partial result **only if** accepted Market\* structure and the
  explicit production policy both authorize partial emission **and** missing
  subjects are not silently filled with invented values;
- surface which bindings lacked eligible facts (operational result), without
  inventing market observations for them.

Stale **silent** acceptance is forbidden. If policy allows composition with
explicitly aged facts, that allowance must be **explicit in policy and
provenance**, not implicit last-known-good repair.

### 6.7 Production inputs (architecture-level)

A production attempt requires explicit inputs sufficient to construct accepted
models without automatic identity invention. Architecture-level required
intent:

| Input class | Intent |
| --- | --- |
| Market snapshot identity | Opaque nonblank snapshot identity (caller-/request-supplied) |
| Session profile selection | Explicit session profile for this emission (R6); one profile per first-slice emission |
| Subject bindings | Explicit ordered bindings from caller-chosen subjects to Market\* / fact selection keys |
| Fact selection criteria | How to retrieve relevant stored `market_fact` records (fact ids, source identity, `collected_at` window, etc.) without re-fetching providers |
| Production policy | Explicit presence/freshness fail-closed rules for required facts (R8) |
| Structural identities | Venue/market, instrument, and session identities required by Market\* construction |

Exact request object field names are fixed at implementation freeze. Input
**intent** is frozen here.

### 6.8 Meaning of produced state

A successful PF-M4 emission means:

> This is the **immutable market observation state within one session context**
> assembled from Fact Store `market_fact` retrieval and explicit production
> inputs, validated under accepted Market\* contracts, under an explicit
> production policy.

It does **not** mean:

- “the live exchange book right now” via direct Gateway or HTTP call;
- portfolio valuation completeness;
- that OHLC/bid-ask/volume/flows are included;
- that research has confirmed prices;
- that missing subjects were healed;
- that Market Watch has evaluated materiality.

---

## 7. Korea / US session model (remediation R6)

### 7.1 Parameterized multi-session architecture

`MarketSnapshotProducer` is a **generic** producer. It **must not** hard-code:

- one exchange;
- one timezone;
- one session calendar;
- one market-status state machine.

Session behavior is supplied through **explicit session profiles** (operational
parameters) whose structural counterparts, if any, are owned by Market\*
contracts.

### 7.2 Minimum session coverage

First-slice architecture must support at minimum:

| Session family | Intent |
| --- | --- |
| **Korean market** | At least one session profile suitable for Korean equity market observation composition (venue/session parameters explicit — not hard-coded producer branches as the only extension mechanism) |
| **US market** | At least one session profile suitable for US equity market observation composition |

Additional venues/sessions may be added later by **parameterization** and
accepted structure extension — not by forking a second producer package.

### 7.3 One session profile per first-slice emission

| Rule | Statement |
| --- | --- |
| Single profile per emission | A first-slice successful emission composes under **exactly one** selected session profile |
| No multi-session merge | Producer does not merge Korea and US sessions into one synthetic “global board” snapshot |
| Cross-session needs | Require multiple production attempts (one per session profile) or a later architecture freeze that explicitly owns multi-session aggregates |

### 7.4 Session profile parameters (architecture-level intent)

A session profile is an explicit production parameter set. Architecture-level
intent includes:

| Parameter class | Intent |
| --- | --- |
| Market / venue binding | Which market/venue identity this profile targets |
| Timezone / calendar reference | Explicit session timezone and calendar identity as opaque parameters (not hard-coded constants inside composition logic as the sole model) |
| Session window semantics | How the profile defines the session for presence/status composition (structure remains Market\*) |
| Status vocabulary mapping inputs | Explicit mapping inputs if required — not open-world inference |
| Freshness policy hooks | Optional binding to production policy thresholds for this session family |

Exact profile schema is fixed at implementation freeze after Market\* session
structure is accepted. **Intent** is frozen: multi-session via parameters, not
via hard-coded single-market producer.

### 7.5 Non-responsibilities (session)

- Owning exchange trading calendars as a global product database inside the
  producer without explicit inputs.
- Auto-detecting “which market this ticker belongs to.”
- Converting all sessions into one UTC “as of” domain field that rewrites
  Market\* structure without acceptance.
- Hard-coding KRX-only or NYSE-only branches as the permanent architecture.

---

## 8. Upstream (remediation R9)

### 8.1 Sole upstream for facts

| Upstream | Role | Rule |
| --- | --- | --- |
| **Fact Store (`FactStore`, PF-M2)** | **Only** source of provider-originated facts for composition | **Read-only retrieval** of `market_fact` (and only after prerequisite B) |

### 8.2 Upstream for structure

| Upstream | Role | Rule |
| --- | --- | --- |
| Accepted Market\* domain packages | Models and validators | Consume-only; no redefinition (prerequisite C) |

### 8.3 Upstream for production request parameters

| Upstream | Role | Rule |
| --- | --- | --- |
| Authorized caller / orchestrator | Supplies opaque identities, session profile selection, selection criteria, explicit subject bindings, production policy | Must not require PF-M4 to invent missing structural inputs |
| Optional caller-side Portfolio Snapshot | May inform **caller** binding derivation | Producer does **not** retrieve portfolio snapshots as a hidden entity resolver (R7) |

### 8.4 Never upstream for PF-M4 facts

- **Provider Gateway** direct calls (bypass forbidden — R9)
- External market HTTP/API from inside the producer
- Research AI / Committee / Evidence Store records as market price truth
- Operational Memory deltas
- Contradiction / EV / CIO outputs
- Human free-text price opinions
- Development Automation manifests as runtime market state
- Broker facts used as synthetic market prices without an accepted separate
  contract (not first-slice; not a silent bridge)
- Prior Market Snapshot used as silent carry-forward truth repair (R8)

### 8.5 No Provider Gateway bypass rule (normative)

1. `MarketSnapshotProducer` **must not** authenticate to market data providers
   or any external HTTP/API to obtain prices or status.
2. `MarketSnapshotProducer` **must not** embed Provider Gateway.
3. `MarketSnapshotProducer` **must not** read Gateway envelopes that have not
   been stored via Fact Store as a side channel around PF-M2.
4. Missing facts remain missing; producer fails closed under policy — never
   synthetic completeness.

### 8.6 Relationship to PF-M1 and PF-M2

```text
ProviderGateway market adapter ──market_fact envelopes──► FactStore append
FactStore retrieval ──► MarketSnapshotProducer (PF-M4)
```

- PF-M1 owns ingress (prerequisite A path).
- PF-M2 owns persistence/retrieval eligibility (prerequisite B).
- PF-M4 owns composition only.
- None of the three absorbs the others’ ownership.

---

## 9. Downstream

### 9.1 PF-M4 first implementation downstream

| Downstream | Role | Rule |
| --- | --- | --- |
| **Market Watch Engine (PF-M5)** | Primary operational consumer of successive market snapshots for material change detection | Downstream only; **not implemented by PF-M4**; producer must not trigger watch |
| **Reporting** (later) | Command-center presentation of market state | Read-only consumer; not system of record for structure |
| **Optional research-planning context** (later) | Materiality / attention context inputs | Must not elevate market narrative into Fact Store research truth; must not make producer an IRO component |

### 9.2 Not PF-M4 downstream ownership

The following may **consume** market snapshots only through later explicit
contracts; PF-M4 **must not implement** them:

- Market Watch materiality engine / IRO wake triggers (PF-M5)
- IRO run coordination / Planner / Committee execution
- Evidence Store / Operational Memory / Contradiction / EV / CIO
- Human Approval decisioning
- Trading / Broker Execution command path
- Portfolio valuation services
- FX conversion / flow analytics products

### 9.3 Emission immutability for consumers

Consumers treat emitted snapshots as **immutable historical composition
results** for the named session context and snapshot identity. “Update” means
a **new** production attempt with a new snapshot identity (and typically new
fact selection / provenance), never in-place mutation of a prior accepted
snapshot.

---

## 10. Dependency graph

### 10.1 Normative dependency direction

Dependencies point **downstream consumption** (A → B means B consumes A).

```text
[Development Automation / joo_auto]
        │ ships milestones only
        ▼
External market providers ──► ProviderGateway (PF-M1; market-adapter path; prereq A)
                              │
                              └── market_fact envelopes ──► FactStore (PF-M2; prereq B)

Accepted Market* domain packages (prereq C)
        │ structure / validators only
        ▼
FactStore ──read-only retrieval──► MarketSnapshotProducer (PF-M4)
                                        │
                                        └── validated Market Snapshot domain product
                                                │
                                                ├──► Market Watch Engine (PF-M5; later)
                                                ├──► Reporting (later)
                                                └──► optional research-planning context (later)

PortfolioSnapshotProducer (PF-M3) ── may inform caller-side bindings only ──► caller
caller ── explicit bindings ──► MarketSnapshotProducer

Stage 1/2 AIAdapter/Committee ──► research path (never market price truth)
IRO ──► Evidence Store / Memory / Contradiction / (later EV / CIO)
```

### 10.2 PF-M4 internal dependency order

```text
Production request validation (identities / session profile / bindings / policy)
    │
Read-only Fact Store retrieval (market_fact)
    │
Apply explicit production policy (presence / freshness) — fail closed if required
    │
Compose market observations for bound subjects under one session profile
    │
Assemble accepted Market Snapshot domain instances
    │
Invoke accepted Market* validators (declared order)
    │ success
Emit immutable snapshot (+ operational fact provenance attachment)
```

### 10.3 Forbidden edges (normative)

| Forbidden edge | Reason |
| --- | --- |
| `MarketSnapshotProducer` → external market re-fetch | No second Gateway (R9) |
| `MarketSnapshotProducer` → `ProviderGateway` as fact upstream | Fact Store only (R9) |
| `MarketSnapshotProducer` → Fact Store append/mutate | Read-only retrieval |
| `MarketSnapshotProducer` → redefine Market\* models | Structure ownership (R1) |
| `MarketSnapshotProducer` → invent interim Market\* structure | Prerequisite C (R4) |
| `MarketSnapshotProducer` → portfolio valuation / PnL / NAV | Forbidden permanently for this package |
| `MarketSnapshotProducer` → FX conversion product | Later domain milestone |
| `MarketSnapshotProducer` → auto ticker/entity/alias resolution | R7 |
| `MarketSnapshotProducer` → silent stale carry-forward / synthetic prices | R8 |
| `MarketSnapshotProducer` → research AI as price truth | R8 |
| `MarketSnapshotProducer` → Market Watch ownership / trigger | PF-M5 |
| `MarketSnapshotProducer` → IRO lifecycle ownership | Plane separation |
| `MarketSnapshotProducer` → Evidence / Memory / Contradiction / EV / CIO | Not producer |
| `MarketSnapshotProducer` → Human Approval authority | Capital authority elsewhere |
| `MarketSnapshotProducer` → trading / order placement | Capital plane |
| `MarketSnapshotProducer` → semantic normalization / entity resolution product / AI inference | Forbidden permanently |
| `MarketSnapshotProducer` → `joo_auto` runtime dependency | Automation is development-only |
| `MarketSnapshotProducer` → hard-coded single-market-only architecture | R6 |
| `ProviderGateway` → Market Snapshot composition | R3, R10 |
| `FactStore` → Market Snapshot composition | R3, R10 |
| `PortfolioSnapshotProducer` → Market Snapshot composition | R10 |
| Sibling quote/price/flow producers for snapshot composition | R10 |
| Research AI → market ground truth via producer | Research never primary truth |

### 10.4 Consistency with frozen planes

| Plane | Result |
| --- | --- |
| Automation M1–M3 | Untouched — development-only |
| IRO product architecture | Untouched — research lifecycle remains IRO |
| IRO-M1 / IRO-M2 | Untouched |
| PF-M1 Provider Gateway | Untouched identity; market-adapter path is prerequisite A under Gateway ownership |
| PF-M2 Fact Store | Untouched identity; `market_fact` eligibility is prerequisite B under Fact Store ownership |
| PF-M3 Portfolio Snapshot | Untouched — separate layer; bindings may be caller-derived from it |
| JOO Product Architecture Layer 5 / PF-M4 | Governing authority for this freeze (unbundled per R3) |
| Accepted Market\* packages | Structure retained when accepted; hard prerequisite until then |
| Stage 1/2 research stack | Retains research execution; never market price ground truth |

---

## 11. Deferred responsibilities

| Deferred responsibility | Until |
| --- | --- |
| Provider Gateway **market-adapter path** implementation | Prerequisite A authorization / implementation (Gateway ownership) |
| Fact Store **`market_fact` append eligibility** | Prerequisite B authorization / implementation (Fact Store ownership) |
| Accepted **Market\*** domain structure and validators | Prerequisite C domain architecture / acceptance freezes |
| PF-M4 **production code** for `MarketSnapshotProducer` | Architecture review + prerequisites A–C + separate implementation authorization |
| OHLC / bid-ask / volume / turnover / richer quotes | Package lifetime freezes after first slice |
| Index observations product surface | Package lifetime freeze |
| Native FX instrument observations | Package lifetime freeze |
| FX conversion / sector state / futures / options / flow products | Later domain milestones + ops freezes as needed |
| Market Watch Engine / materiality policy | **PF-M5** |
| Portfolio valuation using market marks | Separate valuation architecture — **not** PF-M4 ownership |
| Multi-session aggregate snapshot product | Later freeze (first slice = one session profile per emission) |
| Platform-wide freshness policy for capital fail-closed thresholds | Snapshot/watch/execution/Reporting policy freezes |
| Automated open-world entity resolution product | Outside PF-M4 permanently (explicit bindings only here) |
| IRO Evidence / Memory / Contradiction / EV / CIO | Frozen IRO plane / later IRO milestones |
| Human capital Approval recording | HA-M1 direction |
| 24/7 supervisor process topology | Stage 6 / ops architecture freezes |
| Exact production request schema-as-code and storage of production provenance | Implementation freeze / residual open work |

### Deferred classes of work (explicit)

PF-M4 first implementation supports:

- **Operational production** of first-slice market observation composition
  into accepted Market Snapshot domain products from **Fact Store
  `market_fact` records**, under **one session profile per emission**, with
  **explicit bindings** and **fail-closed policy**

Deferred / excluded:

- Market API ownership inside the producer
- Structure ownership inside the producer
- OHLC / bid-ask / volume / turnover / richer quotes
- Index / native FX observation product surfaces
- FX conversion / sector / futures / options / flows
- Market Watch / IRO / valuation / trading

---

## 12. Forbidden responsibilities

`MarketSnapshotProducer` / PF-M4 **must not**:

1. **Provider Gateway** ingress, envelope construction, authentication, market
   adapter ownership, or health ownership as composition responsibility.
2. **Fact Store** append, supersession, history mutation, or store ownership.
3. **Bypass Fact Store** by calling providers, Gateway, or direct HTTP/API for
   composition inputs (R9).
4. **Redefine or relocate** Market\* structural ownership, or invent interim
   structure inside the producer (R1, R4.C).
5. Embed Market Snapshot composition into Gateway, Fact Store,
   PortfolioSnapshotProducer, IRO, Evidence, or sibling quote/price/flow
   producers (R3, R10).
6. **Portfolio Snapshot** production or live portfolio mutation.
7. **Market Watch** ownership, materiality classification ownership, or IRO
   wake triggering (PF-M5).
8. **Portfolio valuation**, NAV, marks-as-portfolio-truth, P&L, cost basis.
9. **FX conversion**, sector state, futures, options, institutional flow,
   foreign investor flow, or program trading flow products in first slice
   (and not as silent producer helpers).
10. **Automatic ticker resolution**, entity resolution, alias matching, or
    open-world semantic resolution (R7).
11. **Synthesize prices** or **synthesize flows** (R8).
12. **Silently carry forward** stale truth as current truth (R8).
13. **Automatically repair** provider truth (R8).
14. Use **research AI** as price truth (R8).
15. **IRO** lifecycle ownership or run coordination.
16. **Evidence Store** ownership or research-as-market-truth.
17. **Operational Memory** ownership.
18. **Contradiction** resolution or majority-vote truth.
19. **Expected Value** assembly.
20. **CIO** synthesis or research posture reports.
21. **Human Approval** (capital) or Development Automation human gates.
22. **Trading**, order routing, rebalancing, or any capital action.
23. **Semantic normalization**, free-text → structured meaning, Knowledge
    Engine normalization, or **entity resolution product** ownership.
24. **AI inference** as market ground truth.
25. Hard-code a single exchange, single timezone, or single session model as
    the permanent producer architecture (R6).
26. Merge multiple session profiles into one first-slice emission.
27. Absorb Automation M1–M3 as a runtime dependency.
28. Redesign PF-M1, PF-M2, PF-M3, IRO, IRO-M1, IRO-M2, Automation M1–M3,
    accepted domain contracts, or product architecture under a “platform
    cleanup” label.

---

## 13. Relationship to PF-M1–M3 and future milestones

### 13.1 Sequencing (from product architecture; refined by R3)

| ID | Focus | Depends on | Delivers |
| --- | --- | --- | --- |
| **PF-M1** | Provider Gateway (broker-first first slice) | Platform arch | KB Open API ingress; envelope/source-class model; market-adapter slot reserved |
| **PF-M2** | Fact Store (broker facts first slice) | **PF-M1** | Append-oriented provider fact persistence + retrieval; `market_fact` deferred |
| **PF-M3** | Portfolio Snapshot production | **PF-M2 + accepted Portfolio\*** | Operational producer of validated portfolio snapshots |
| **PF-M4** | Market Snapshot operational production | **Prerequisites A–C** (Gateway market path + Fact Store `market_fact` + accepted Market\*) | Operational producer of validated market snapshots from stored market facts |
| **PF-M5** | Market Watch Engine | PF-M3/M4 | Material watch events |

### 13.2 Contract between Gateway, Fact Store, and PF-M4

1. **Gateway ingests; Fact Store stores; PF-M4 composes.**
2. **Read-only:** PF-M4 never appends facts.
3. **No dual composition ownership:** Fact Store and Gateway must not emit
   domain Market Snapshot products as their responsibility.
4. **No dual ingress ownership:** Producer must not re-implement Gateway.
5. **Provenance:** composition retains fact `collected_at` / fact identity /
   source identity references operationally; does not rewrite store history.
6. **Non-redesign:** this freeze extends product Layer 5 without reopening
   PF-M1/M2/M3, IRO-M1/M2, or Automation M1–M3.

### 13.3 Contract between Market\* structure and PF-M4

1. **Market\* owns structure; PF-M4 owns operational production** (R1, R2).
2. Successful emission requires accepted validators to pass.
3. Producer preserves exact types, order, and exception propagation rules.
4. Partial emissions are valid only when domain validators and explicit
   production policy both accept them — never via invented observations.
5. Domain non-responsibilities (valuation products, flow products, FX
   conversion products) remain non-responsibilities after PF-M4 first slice.

### 13.4 Contract with PF-M3 (caller-side only)

1. Portfolio Snapshot and Market Snapshot are **separate** products.
2. A caller may derive Market Snapshot subject bindings from Portfolio Snapshot
   holdings/watchlist subjects.
3. `MarketSnapshotProducer` must not embed Portfolio Snapshot production or
   treat portfolio membership as implicit auto-resolution without explicit
   bindings (R7).
4. PF-M3 must not pull market valuation into Portfolio Snapshot (PF-M3 freeze
   retained).

### 13.5 What PF-M5+ must not pull backward into PF-M4

- Market Watch materiality ownership or IRO wake triggering
- Research AI as market truth
- Gateway bypass “for fresher quotes”
- Silent stale price carry-forward as watch convenience
- Structure invention inside the producer because Market\* was incomplete

### 13.6 Handoff semantics

```text
PF-M1 success (market path):  Immutable envelope (market_fact)
                    ──append eligible──► PF-M2 stored fact
PF-M2 retrieval ──► PF-M4 composition + domain validation
PF-M4 success:  Accepted Market Snapshot domain product
                (+ operational fact provenance)
PF-M4 failure:  Fail closed; no synthetic prices/status/subjects/flows
PF-M5 (later):  Consumes snapshots; does not produce them
```

PF-M4 does not require Market Watch or IRO to exist at runtime to **emit** a
market snapshot; it must not **implement** those layers to complete PF-M4
scope.

PF-M4 **does** require prerequisites A–C before production implementation.

---

## 14. Risk alignment

| Risk | Severity | PF-M4 mitigation |
| --- | --- | --- |
| Structure/ops ownership collapse; producer invents Market\* models | High | R1/R2; hard prerequisite C; structure boundary only in this freeze |
| Market API + snapshot composition collapsed into one package | High | R3 unbundle; Gateway/Fact Store/producer split |
| Production starts before market_fact path exists | High | R4 prerequisites A–B; no bypass demos |
| Scope creep into OHLC/flows/FX/options in first slice | High | R5 explicit first content vs package lifetime vs later domain |
| Hard-coded Korea-only or US-only producer | High | R6 parameterized multi-session; one profile per emission |
| Auto ticker/entity resolution invents false subjects | High | R7 explicit bindings only; permanent ban on open-world resolution |
| Missing/stale facts silently healed → false market truth | High | R8 fail closed; no synthetic prices/flows; no silent carry-forward |
| Producer re-calls market APIs → dual truth vs Fact Store | High | R9 sole upstream retrieval |
| Sibling quote/price/flow packages fragment ownership | Medium | R10 one package only |
| Research AI treated as price truth | High | Research never upstream for facts; dual-store retained |
| Valuation smuggled into “market snapshot completeness” | High | Explicit non-valuation; portfolio NAV/PnL forbidden |
| Market Watch / IRO ownership leaked into producer | High | Downstream-only PF-M5; forbidden responsibilities |
| Silent redesign of frozen PF-M1/M2/M3/IRO/Automation | High | Frozen-input supremacy; forbidden responsibilities |
| Prerequisite C incomplete → implementation invents structure | High | Implementation authorization blocked until Market\* accepted |

---

## 15. Document Authority

- This document is the **canonical PF-M4 implementation architecture** for
  Market Snapshot **operational production** (Layer 5 ops slice).
- It is subordinate to frozen component architectures within their scopes
  (Constitution, JOO product architecture, PF-M1, PF-M2, PF-M3, IRO, IRO-M1,
  IRO-M2, Automation M1–M3, and — once accepted — Market\* domain contracts).
- It incorporates all required remediations **R1–R10** from the independent
  PF-M4 Market Snapshot Candidate Boundary Review.
- It does not authorize production implementation, commit, tag, or push by
  itself.
- It does not authorize invention of Market\* domain packages, Gateway market
  adapters, or Fact Store `market_fact` eligibility as side effects of this
  freeze.
- Subsequent PF-M5+ milestones must cite this document and obtain their own
  architecture freezes before implementation.

---

## 16. Architecture freeze summary

**PF-M4 freezes:**

- one package `MarketSnapshotProducer`;
- **operational production only** (structure remains accepted Market\*);
- **unbundled** ownership: Gateway ingress, Fact Store persistence, producer
  composition;
- **hard prerequisites A–C** before production implementation;
- **read-only Fact Store retrieval** as the **sole fact upstream**;
- **first-slice content only**: market/venue identity, instrument identity,
  index identity only if structure requires, session context, last price,
  market status, source provenance, validation-first immutable emission;
- **parameterized multi-session** architecture (Korea + US minimum; one
  session profile per emission);
- **explicit caller-supplied bindings only** for subject coverage;
- **fail-closed** missing/stale required facts under explicit production
  policy;
- **no** Provider Gateway bypass, synthetic prices/flows, silent stale
  carry-forward, auto truth repair, research AI price truth, valuation, Market
  Watch ownership, or sibling composition packages.

**PF-M4 does not freeze:**

- production code or tests;
- Market\* domain package implementation (prerequisite C — separate freezes);
- Gateway market-adapter implementation (prerequisite A — Gateway ownership);
- Fact Store `market_fact` eligibility implementation (prerequisite B — Fact
  Store ownership);
- exact production request schema module layout;
- OHLC / bid-ask / volume / turnover / richer quotes;
- index / native FX observation product surfaces;
- FX conversion / sector / futures / options / flow products;
- Market Watch;
- research, evidence, memory, contradiction, EV, CIO, trading, human capital
  approval.

**Explicit first implementation support (after prerequisites):**

- Fact Store **`market_fact`** → session-parameterized composition of
  first-slice market observations → validated Market Snapshot domain product

**Explicit deferred / excluded:**

- producer-owned structure invention
- Gateway / HTTP bypass retrieval
- OHLC / bid-ask / volume / turnover / richer quotes
- flows / FX conversion / derivatives products
- Market Watch / valuation / IRO ownership

---

## 17. Implementation authorization status

| Item | Status |
| --- | --- |
| Architecture document authored | **Yes** (this document) |
| Independent architecture review | **Required before implementation** |
| Prerequisite A — Gateway market-adapter path | **Not satisfied by this document** |
| Prerequisite B — Fact Store `market_fact` eligibility | **Not satisfied by this document** |
| Prerequisite C — accepted Market\* structure/validators | **Not present in repository at this freeze; hard blocker** |
| Production package scaffold / code / tests | **Not authorized by this document** |
| Commit / tag / push | **Not authorized by this document** |

**Implementation authorization status: NOT AUTHORIZED**

Production implementation of `MarketSnapshotProducer` requires:

1. architecture review acceptance of this freeze;
2. satisfaction of hard prerequisites A–C under their correct owners;
3. a separate implementation authorization for the producer package.

---

## 18. Commit status

| Item | Status |
| --- | --- |
| Working tree change for this document | To be committed only with **explicit user approval** |
| Tag | Not created |
| Push | Not performed |
| Branch mutation | Not performed |

Per repository agent contract: architecture authoring may proceed; **commit
requires user approval**. This freeze does not auto-commit.

---

## Residual open work (not architecture defects)

These require later freezes or prerequisite work; they do not reopen frozen
PF-M1–M3, IRO, or Automation contracts:

1. Market\* domain architecture and package acceptance (prerequisite C).
2. Provider Gateway market-adapter implementation freeze/detail (prerequisite A).
3. Fact Store `market_fact` eligibility implementation freeze/detail
   (prerequisite B).
4. Exact Market Snapshot field names and nested package splits under Market\*.
5. Exact production request / result / policy schema-as-code.
6. Session profile catalog for Korea and US first profiles.
7. PF-M5 Market Watch materiality policy architecture.
8. Separate portfolio valuation architecture if/when marks are applied to
   holdings.

Absence of those details does not authorize bypass of R1–R10.
