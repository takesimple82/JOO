# Market* First-Slice Domain Structure Architecture

## Status and milestone

- Status: Architecture authored for independent review; first Market\* domain
  structure freeze (Prerequisite C for PF-M4)
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Domain Contract Plane** — Market\* structural models, validators,
  and invariants only
- Milestone: Market\* first-slice domain structure (unlocks later PF-M4
  `MarketSnapshotProducer` implementation)
- Production packages (future, **not** created by this document):
  the seven Market\* domain-contract packages named below
- Architecture sources of truth (frozen; must not be redesigned):
  - `JOO_CONSTITUTION.md`
  - `docs/JOO_PRODUCT_ARCHITECTURE.md` (Layer 5 Market Snapshot product
    composition; residual open work: Market domain contracts)
  - `docs/provider/PF_M1_PROVIDER_GATEWAY_ARCHITECTURE.md`
  - `docs/provider/PF_M2_FACT_STORE_ARCHITECTURE.md`
  - `docs/provider/PF_M3_PORTFOLIO_SNAPSHOT_ARCHITECTURE.md`
  - `docs/provider/PF_M4_MARKET_SNAPSHOT_ARCHITECTURE.md` (**APPROVED** —
    operational production architecture; structure ownership remains Market\*)
  - PF-M4 Prerequisite Sequencing Review (**APPROVED** — hard prerequisites
    A–C; this document freezes **C only**)
  - Frozen IRO Product / IRO-M1 / IRO-M2
  - Frozen Automation M1–M3
  - Accepted Portfolio\* domain package patterns (structure-only precedent)
- Repository boundary for this document: **architecture authoring only**; this
  document alone authorizes no production code, test, package scaffold,
  schema module, configuration, run artifact, producer package, or Git history
  mutation

This document freezes the **minimum accepted Market\* domain structure**
required so PF-M4 may later consume models and validators without inventing
interim structure inside `MarketSnapshotProducer`.

It does **not** redesign JOO product architecture, PF-M1–M4 operational
architectures, IRO, or Automation.

It does **not** implement domain packages, MarketSnapshotProducer, Gateway,
Fact Store, Market Watch, Research, or Trading.

---

## Normative first-slice surface (must remain explicit)

### First-slice Market\* structure owns ONLY

| # | Responsibility |
| --- | --- |
| 1 | **Models** for market snapshot aggregate and nested first-slice objects |
| 2 | **Validators** with exact types, declared order, and exception propagation |
| 3 | **Structural invariants** (identity opacity, session parameterization, price Decimal semantics, provenance reference shape, collection order, empty/partial rules) |

### First-slice content (structure only)

| Content | First-slice Market\* |
| --- | --- |
| `market_snapshot_id` | **Yes** |
| Market identity (`market_id`) | **Yes** |
| Venue identity (`venue_id`) | **Yes** |
| Instrument identity (`instrument_id`) | **Yes** |
| Session context (parameterized) | **Yes** |
| Last price observation (`Decimal`) | **Yes** |
| Market status (closed vocabulary) | **Yes** |
| Provenance references (structural only) | **Yes** |
| Index identity | **No** (not mandatory; not included) |
| OHLC / bid / ask / volume / turnover | **No** |
| FX conversion / sector / futures / options / flows | **No** |
| Portfolio valuation / PnL / NAV | **No** |
| Market Watch materiality / research / trading | **No** |

### First-slice Market\* does NOT own

| Concern | Owner (elsewhere) |
| --- | --- |
| Provider Gateway ingress / envelopes / health | PF-M1 |
| Fact Store persistence / append / supersession / retrieval | PF-M2 |
| Market Snapshot operational production | PF-M4 `MarketSnapshotProducer` |
| Portfolio Snapshot structure or production | Portfolio\* / PF-M3 |
| Market Watch Engine | PF-M5 |
| Research / Evidence / Memory / Contradiction / EV / CIO | IRO (frozen) |
| Trading / Broker Execution | BX-M1 |
| Human Approval (capital) | Human Authority |
| Automatic ticker / entity / alias resolution | Outside permanently |

---

## 1. Purpose

### 1.1 Purpose

Define and freeze the **smallest coherent Market\* domain package set** that:

1. owns first-slice Market Snapshot **structure** (models, validators,
   invariants);
2. is consumable later by `MarketSnapshotProducer` under PF-M4 without
   structure invention in the producer (PF-M4 remediations R1, R2, R4.C);
3. supports **parameterized** Korea and US session profiles without hard-coding
   a single exchange, timezone, or calendar (R6);
4. preserves Constitution identity, validation-first, immutability, and exact
   Decimal rules;
5. keeps domain packages non-runtime, non-persistent, and non-orchestrating.

### 1.2 Structure vs operational production

| Plane | Owner | Owns |
| --- | --- | --- |
| **Structure** | Market\* domain packages (this freeze) | Models, validators, structural invariants |
| **Operational production** | `MarketSnapshotProducer` (PF-M4; later) | Fact Store retrieval, composition, fail-closed policy, emission |

Market\* defines **what** a valid market snapshot is structurally.

PF-M4 defines **how** accepted instances are assembled at runtime from Fact
Store `market_fact` records and explicit caller bindings.

### 1.3 Explicit non-identity

Market\* first-slice packages are **not**:

- Provider Gateway, Fact Store, or any operational producer;
- Market Watch, Reporting engines, IRO components, or Trading;
- a valuation, FX, OHLC, quote-book, or flow product;
- a ticker resolver, entity resolver, or open-world identity product;
- a session calendar database or timezone database product;
- a second copy of Fact Store provenance storage.

### 1.4 Relationship to PF-M4 Prerequisite C

PF-M4 hard prerequisite **C** requires accepted Market\* structure and
validators before producer implementation. This document is the architecture
freeze for that prerequisite’s **structural contracts**. Package
implementation remains a separate authorization after this architecture is
accepted.

---

## 2. Authority reviewed

| Authority | Review result for this freeze |
| --- | --- |
| `JOO_CONSTITUTION.md` | Identity opacity; validation-first; exact types; order preservation; no auto ID generation; Decimal exactness; domain packages non-runtime/non-persistent |
| `docs/JOO_PRODUCT_ARCHITECTURE.md` Layer 5 | Market Snapshot = immutable market observation composition; residual open work includes Market domain contracts — this document closes that residual for first slice |
| PF-M1 | Untouched; ingress not Market\* ownership |
| PF-M2 | Untouched; `market_fact` storage not Market\* ownership; domain may only **reference** fact identity / source identity / collection time |
| PF-M3 | Untouched; Portfolio\* remains separate plane; Portfolio patterns are **structure precedent only** |
| PF-M4 (APPROVED) | Structure boundary §6.1–§6.3; R1–R10 retained; producer not authorized by this document |
| PF-M4 Prerequisite Sequencing Review (APPROVED) | Locked sequence **C → A → B → (A ∩ B ∩ C unlock) → PF-M4 production** (A = Gateway market path; B = Fact Store `market_fact`; C = Market\* structure). This document freezes **Prerequisite C only**. **C may proceed in parallel with A**. **B must not precede A handoff freeze**. PF-M4 production remains blocked until **A ∩ B ∩ C**. Document not present as a repo file at authoring time; binding intent is taken from the approved review as cited by mission and from PF-M4 §4 / §13 |
| Frozen IRO / IRO-M1 / IRO-M2 | Untouched; research never owns market structure or price truth |
| Frozen Automation M1–M3 | Untouched; development plane only |
| Accepted Portfolio\* packages | Pattern source for package granularity, `Explicit*` models, validators, empty collections, alignment-by-stored-id, Decimal field rules |

If any statement here conflicts with a frozen higher authority in its scope, the
higher authority wins and this document must be remediated — not silently
overridden.

---

## 3. Package decomposition

### 3.1 Principle

Prefer the **minimum number of explicit domain packages** consistent with
existing Portfolio\* conventions:

- one package per distinct structural ownership boundary;
- identity endpoints separate from observation/context/aggregate packages;
- validators live with their models (`models.py` + `validation.py`);
- no operational packages;
- no package-root re-export requirement;
- no collapsing of unrelated identities into one mega-model.

### 3.2 Exact package set (seven packages)

| # | Exact package name | Owns |
| --- | --- | --- |
| 1 | `MarketEndpoint` | Market identity endpoint |
| 2 | `MarketVenue` | Venue identity endpoint |
| 3 | `MarketInstrument` | Instrument identity endpoint |
| 4 | `MarketSessionContext` | Parameterized session context structure |
| 5 | `MarketFactProvenanceReference` | Structural fact provenance reference |
| 6 | `MarketInstrumentObservation` | One instrument observation (last price + status + provenance) under one session context |
| 7 | `MarketSnapshot` | Immutable market-state composition root for one session context |

### 3.3 Dependency direction (normative)

```text
MarketEndpoint          (leaf)
MarketVenue             (leaf)
MarketInstrument        (leaf)
MarketFactProvenanceReference  (leaf)

MarketSessionContext    (leaf; foreign opaque market_id / venue_id strings only)

MarketInstrumentObservation
  ├── MarketInstrument
  ├── MarketSessionContext
  └── MarketFactProvenanceReference

MarketSnapshot
  ├── MarketSessionContext
  └── MarketInstrumentObservation
```

Rules:

1. Dependencies point only toward structure leaves / upstream structure.
2. No Market\* package imports Provider Gateway, Fact Store, PF-M3/M4 producers,
   IRO, Portfolio\* (except pattern precedent in architecture — **no code
   dependency**), Automation, or runtime packages.
3. No circular imports.
4. Endpoint packages do not import observation or snapshot packages.
5. `MarketSessionContext` retains foreign `market_id` and `venue_id` as opaque
   strings (Portfolio Observation Context pattern for `portfolio_id`); it does
   **not** embed endpoint objects and does **not** call endpoint validators.

### 3.4 Rejected package shapes

| Option | Verdict |
| --- | --- |
| One mega `MarketDomain` package for all models | Rejected — violates Portfolio\* separation of identity / context / observation / aggregate |
| Separate packages for last price, status, and observation | Rejected for first slice — over-fragments a single observation record |
| Index identity package | Rejected — index identity is **not** mandatory first-slice content |
| OHLC / quote / volume / flow packages | Rejected — first-slice exclusions |
| Operational `MarketSnapshotProducer` inside this freeze | Rejected — PF-M4 ownership; structure-only here |
| Embedding structure inside PF-M4 producer | Forbidden permanently (R1) |

### 3.5 Future package layout intent (implementation later)

When authorized, each package follows the accepted domain layout:

```text
<PackageName>/
  models.py
  validation.py
  README.md
  tests/                  # authorized only with package implementation
```

No package-root `__init__.py` re-export is required. Callers import models from
`<Package>.models` and validators from `<Package>.validation`.

---

## 4. Model definitions

All first-slice models are standard `@dataclass(frozen=True)` structural
models. Construction performs **no** validation. Models have no defaults,
default factories, slots, `__post_init__`, custom constructors, custom public
methods, properties, derived fields, aliases, or metadata fields unless listed
below.

### 4.1 `MarketEndpoint`

**Model:** `ExplicitMarket`

| Field order | Field | Type | Semantics |
| --- | --- | --- | --- |
| 1 | `market_id` | `str` | Opaque caller-supplied market identity; canonical only within the Market namespace |

**Public API:**

- `ExplicitMarket`
- `validate_explicit_market()`

### 4.2 `MarketVenue`

**Model:** `ExplicitMarketVenue`

| Field order | Field | Type | Semantics |
| --- | --- | --- | --- |
| 1 | `venue_id` | `str` | Opaque caller-supplied venue identity; canonical only within the Market Venue namespace |

**Public API:**

- `ExplicitMarketVenue`
- `validate_explicit_market_venue()`

**Market vs venue:** first slice keeps both identities distinct. A market is the
market namespace named by a snapshot session; a venue is the trading venue
namespace. Domain structure does not equate, map, or resolve them.

### 4.3 `MarketInstrument`

**Model:** `ExplicitMarketInstrument`

| Field order | Field | Type | Semantics |
| --- | --- | --- | --- |
| 1 | `instrument_id` | `str` | Opaque caller-supplied instrument identity; canonical only within the Market Instrument namespace |

**Public API:**

- `ExplicitMarketInstrument`
- `validate_explicit_market_instrument()`

**Non-fields (forbidden first slice):** ticker symbol fields, exchange codes as
identity encoding, ISIN/CUSIP parsing, display names, currency, asset class,
index membership, entity links.

### 4.4 `MarketSessionContext`

**Model:** `ExplicitMarketSessionContext`

| Field order | Field | Type | Semantics |
| --- | --- | --- | --- |
| 1 | `session_context_id` | `str` | Opaque identity of this session context instance |
| 2 | `market_id` | `str` | Foreign opaque Market identity |
| 3 | `venue_id` | `str` | Foreign opaque Venue identity |
| 4 | `session_profile_id` | `str` | Opaque session-profile identity (e.g. caller-chosen Korea regular or US regular profile id — **not** interpreted by domain) |
| 5 | `timezone_id` | `str` | Opaque timezone reference identity (parameterized; **not** a hard-coded single zone) |
| 6 | `calendar_id` | `str` | Opaque trading-calendar reference identity (parameterized; **not** a hard-coded single calendar) |

**Public API:**

- `ExplicitMarketSessionContext`
- `validate_explicit_market_session_context()`

**Session parameterization rule:** Korea and US support is achieved by
**different caller-supplied profile / timezone / calendar / venue / market
identities**, not by domain hard-coding of KRX, NYSE, Nasdaq, `Asia/Seoul`,
`America/New_York`, or a single trading calendar.

Domain does **not** own a profile catalog, holiday calendar product, or
timezone database. Those may be supplied operationally later; structure only
requires the opaque parameters to be present and nonblank.

### 4.5 `MarketFactProvenanceReference`

**Model:** `ExplicitMarketFactProvenanceReference`

| Field order | Field | Type | Semantics |
| --- | --- | --- | --- |
| 1 | `fact_id` | `str` | Opaque Fact Store fact identity reference |
| 2 | `source_identity` | `str` | Opaque source identity reference preserved from the fact path |
| 3 | `collected_at` | `str` | Opaque collection-time reference string preserved from the fact path |

**Public API:**

- `ExplicitMarketFactProvenanceReference`
- `validate_explicit_market_fact_provenance_reference()`

**Rules:**

1. Structural reference only — no Fact Store I/O, no retrieval, no append.
2. `collected_at` is an opaque nonblank `str`. Domain does **not** parse,
   normalize, timezone-convert, or validate ISO calendrical form.
3. Domain does **not** invent `collected_at` from wall clock.
4. Domain does **not** own `source_class`, payload bytes, supersession links, or
   store topology.
5. Presence of a provenance reference does **not** prove fact existence,
   freshness, or economic truth.

### 4.6 `MarketInstrumentObservation`

**Model:** `ExplicitMarketInstrumentObservation`

| Field order | Field | Type | Semantics |
| --- | --- | --- | --- |
| 1 | `instrument` | `ExplicitMarketInstrument` | Exact instrument identity object |
| 2 | `session_context` | `ExplicitMarketSessionContext` | Session context under which this observation is stated |
| 3 | `last_price` | `Decimal` | Exact last-price observation |
| 4 | `market_status` | `str` | One closed-vocabulary market status token |
| 5 | `provenance` | `ExplicitMarketFactProvenanceReference` | Structural provenance reference for the facts used to state this observation |

**Public constant (models module):**

```text
MARKET_STATUS_VALUES: tuple[str, ...] = (
    "pre_open",
    "open",
    "post_close",
    "closed",
    "halted",
    "unknown",
)
```

| Status | Structural intent (not exchange hard-coding) |
| --- | --- |
| `pre_open` | Pre-regular session (covers pre-open / pre-market style phases when mapped by caller/producer) |
| `open` | Regular continuous / open session phase |
| `post_close` | Post-regular session (covers post-close / after-hours style phases when mapped by caller/producer) |
| `closed` | Session closed / not trading under the selected profile |
| `halted` | Trading halt / suspension state |
| `unknown` | Status cannot be classified from accepted explicit inputs |

**Public API:**

- `MARKET_STATUS_VALUES`
- `ExplicitMarketInstrumentObservation`
- `validate_explicit_market_instrument_observation()`

**Non-fields (forbidden first slice):** OHLC, bid, ask, volume, turnover, size,
trade count, VWAP, currency amount objects, FX rates, index levels, flow
fields, timestamps as domain wall-clock ownership, observation identity field.

### 4.7 `MarketSnapshot`

**Model:** `ExplicitMarketSnapshot`

| Field order | Field | Type | Semantics |
| --- | --- | --- | --- |
| 1 | `market_snapshot_id` | `str` | Opaque caller-supplied snapshot identity; canonical only within the Market Snapshot namespace |
| 2 | `session_context` | `ExplicitMarketSessionContext` | Root session context for this emission/composition |
| 3 | `instrument_observations` | `tuple[ExplicitMarketInstrumentObservation, ...]` | Ordered instrument observations |

**Public API:**

- `ExplicitMarketSnapshot`
- `validate_explicit_market_snapshot()`

**Meaning of a valid snapshot:**

> Immutable market observation state for the named session context, composed of
> zero or more validated instrument observations with last price, market
> status, and structural provenance references.

It does **not** mean live exchange book truth, portfolio valuation
completeness, multi-session global board, or Market Watch materiality.

---

## 5. Validator definitions

### 5.1 Ownership

| Package | Exact validator name | Parameter name | Return |
| --- | --- | --- | --- |
| `MarketEndpoint` | `validate_explicit_market` | `market` | `None` |
| `MarketVenue` | `validate_explicit_market_venue` | `venue` | `None` |
| `MarketInstrument` | `validate_explicit_market_instrument` | `instrument` | `None` |
| `MarketSessionContext` | `validate_explicit_market_session_context` | `context` | `None` |
| `MarketFactProvenanceReference` | `validate_explicit_market_fact_provenance_reference` | `provenance` | `None` |
| `MarketInstrumentObservation` | `validate_explicit_market_instrument_observation` | `observation` | `None` |
| `MarketSnapshot` | `validate_explicit_market_snapshot` | `snapshot` | `None` |

### 5.2 Common validator rules (all packages)

1. Exact model type via `type(x) is Model` (subclasses rejected).
2. Exact built-in field types (`str`, `Decimal`, `tuple` as contracted).
3. Nonblank identity / reference strings: reject empty or whitespace-only via
   `strip() == ""` **without** mutating or trimming the stored value.
4. Surrounding whitespace on otherwise nonblank identities is **accepted and
   preserved** (Portfolio\* identity precedent).
5. Upstream validators are invoked **exactly once** in declared order.
6. Upstream exception objects propagate **unchanged**.
7. First failure wins; no later check after a failure.
8. No normalize, case fold, sort, convert, copy, reconstruct, infer, or
   lookup.
9. Success returns `None`.
10. No global uniqueness, registry, or endpoint-existence checks.

### 5.3 Local exception message pattern

Follow accepted Portfolio\* style messages, for example:

| Failure class | Exception | Message pattern |
| --- | --- | --- |
| Wrong root model | `TypeError` | `"<param> must be <ExactModelName>"` |
| Wrong field type | `TypeError` | `"<field> must be <type>"` |
| Blank identity/reference | `ValueError` | `"<field> must not be blank"` |
| Non-finite Decimal | `ValueError` | `"last_price must be finite"` |
| Unsupported status | `ValueError` | `"market_status must be one of MARKET_STATUS_VALUES"` |
| Alignment failure | `ValueError` | explicit field mismatch message |
| Duplicate instrument | `ValueError` | `"instrument_observations must not contain duplicate instrument_id"` |
| Wrong tuple element type | `TypeError` | collection element exact-type message |

Exact final message strings are fixed at package implementation time and must
remain stable once packages are accepted.

---

## 6. Validation order

### 6.1 `validate_explicit_market(market)`

1. exact `ExplicitMarket` type;
2. `market_id` exact `str`;
3. `market_id` nonblank;
4. return `None`.

### 6.2 `validate_explicit_market_venue(venue)`

1. exact `ExplicitMarketVenue` type;
2. `venue_id` exact `str`;
3. `venue_id` nonblank;
4. return `None`.

### 6.3 `validate_explicit_market_instrument(instrument)`

1. exact `ExplicitMarketInstrument` type;
2. `instrument_id` exact `str`;
3. `instrument_id` nonblank;
4. return `None`.

### 6.4 `validate_explicit_market_session_context(context)`

1. exact `ExplicitMarketSessionContext` type;
2. `session_context_id` exact `str` then nonblank;
3. `market_id` exact `str` then nonblank;
4. `venue_id` exact `str` then nonblank;
5. `session_profile_id` exact `str` then nonblank;
6. `timezone_id` exact `str` then nonblank;
7. `calendar_id` exact `str` then nonblank;
8. return `None`.

No validation against MarketEndpoint/MarketVenue packages. No interpretation of
profile/timezone/calendar meaning.

### 6.5 `validate_explicit_market_fact_provenance_reference(provenance)`

1. exact `ExplicitMarketFactProvenanceReference` type;
2. `fact_id` exact `str` then nonblank;
3. `source_identity` exact `str` then nonblank;
4. `collected_at` exact `str` then nonblank;
5. return `None`.

### 6.6 `validate_explicit_market_instrument_observation(observation)`

1. exact `ExplicitMarketInstrumentObservation` type;
2. exact `ExplicitMarketInstrument` type for `instrument`;
3. validate instrument once;
4. exact `ExplicitMarketSessionContext` type for `session_context`;
5. validate session context once;
6. `last_price` exact built-in `Decimal` type (subclasses rejected);
7. `last_price` is finite (`is_finite()`; no arithmetic; no context mutation);
8. `market_status` exact `str` type;
9. `market_status` is an exact member of `MARKET_STATUS_VALUES` (identity
   membership; no case folding);
10. exact `ExplicitMarketFactProvenanceReference` type for `provenance`;
11. validate provenance once;
12. return `None`.

### 6.7 `validate_explicit_market_snapshot(snapshot)`

1. exact `ExplicitMarketSnapshot` type;
2. `market_snapshot_id` exact `str` then nonblank;
3. exact `ExplicitMarketSessionContext` type for root `session_context`;
4. validate root session context once;
5. `instrument_observations` exact built-in `tuple`;
6. for each element in **caller order**:
   1. exact `ExplicitMarketInstrumentObservation` type;
   2. validate observation once;
   3. align observation session context to root by **exact stored field values**
      for all six session-context fields:
      `session_context_id`, `market_id`, `venue_id`, `session_profile_id`,
      `timezone_id`, `calendar_id`
      (Python object identity of nested context objects is **not** required);
   4. reject duplicate `instrument.instrument_id` within the tuple by exact
      stored string value;
7. return `None`.

### 6.8 Aggregate validation graph

```text
validate_explicit_market_snapshot
  → validate_explicit_market_session_context (root once)
  → for each observation in caller order:
        validate_explicit_market_instrument_observation
          → validate_explicit_market_instrument
          → validate_explicit_market_session_context
          → last_price Decimal/finite checks
          → market_status vocabulary check
          → validate_explicit_market_fact_provenance_reference
        → session-context field alignment to root
        → instrument_id uniqueness accumulation
```

---

## 7. Identity invariants

1. All identities are **opaque** `str` values.
2. All identities are **caller-supplied**.
3. **No automatic ID generation**, hashing, derivation, or inference.
4. IDs **must not** encode timestamps, versions, endpoints, tickers, venues,
   sessions, or state as a hidden semantic scheme.
5. **No ticker inference**, entity resolution, exchange alias resolution, or
   open-world subject invention inside Market\*.
6. Identity validation establishes **local structural form only** — not global
   uniqueness, not registry presence, not real-world instrument existence.
7. Namespaces are distinct:
   - Market (`market_id`)
   - Market Venue (`venue_id`)
   - Market Instrument (`instrument_id`)
   - Market Session Context (`session_context_id`)
   - Market Snapshot (`market_snapshot_id`)
   - Fact reference (`fact_id`) and source reference (`source_identity`) are
     foreign opaque references, not Market\*-owned endpoints.
8. Equal string values across namespaces do **not** merge namespaces.
9. Index identity is **out of first slice** and is not required on any model.

---

## 8. Session invariants

1. Every Market Snapshot and every instrument observation is bound to an
   explicit `ExplicitMarketSessionContext`.
2. First-slice composition semantics (for later PF-M4) assume **one session
   profile per snapshot emission**. Domain structure therefore binds one root
   session context per snapshot; multi-session merge into one aggregate is
   **not** first-slice structure.
3. Session context is **parameterized** by opaque:
   - `market_id`
   - `venue_id`
   - `session_profile_id`
   - `timezone_id`
   - `calendar_id`
4. Domain **must not** hard-code:
   - KRX as universal default
   - NYSE / Nasdaq as universal default
   - one timezone
   - one trading calendar
   - one status state machine per exchange as domain code branches
5. Korea and US compatibility is structural: both are expressible as distinct
   caller-supplied parameter sets using the same models.
6. Session context is timeless structural binding: it does not claim that an
   observation “occurred now,” does not own runtime clocks, and does not
   require a snapshot wall-clock timestamp field.
7. Alignment of nested observation contexts to the root uses exact stored field
   equality for all six session-context fields.

---

## 9. Price invariants

1. `last_price` is exact built-in `decimal.Decimal` only.
2. Float, Fraction, int, str-encoded numbers, and Decimal subclasses are
   rejected.
3. `last_price` must be **finite** (rejects NaN and infinities).
4. Exact Decimal representation is preserved (exponent, trailing zeros,
   signed zero) — no quantization, rounding, or context-dependent rewrite.
5. **No implicit conversion** of units, currencies, lots, or notional.
6. **No valuation math** in Market\*: no mark-to-market, NAV, PnL, notional,
   FX conversion, or portfolio impact calculation.
7. Structural validity of a price is **not** economic reasonableness review.
   Sign policy is intentionally **not** constrained in first slice (finite
   only), matching Portfolio holding quantity’s finite-only posture for
   structural numerics.
8. Currency identity, price unit, and lot size are **deferred** (not first-slice
   fields).

---

## 10. Provenance invariants

1. Provenance is a **structural reference** object only.
2. Required reference fields: `fact_id`, `source_identity`, `collected_at`
   (all opaque nonblank `str`).
3. Market\* **must not**:
   - call Fact Store;
   - persist facts;
   - resolve source truth;
   - fetch providers;
   - supersede or mutate facts;
   - invent missing provenance;
   - use research AI outputs as market fact provenance.
4. Provenance does not prove freshness; freshness policy is PF-M4 operational
   production ownership.
5. One observation carries one provenance reference object in first slice
   (minimum). Multi-fact provenance graphs are deferred.
6. Operational producers may retain additional production provenance outside
   domain models; they must not redefine or fork these domain fields.

---

## 11. Snapshot aggregate invariants

1. Structural identity of a snapshot consists of:
   - `market_snapshot_id`
   - root `session_context`
   - ordered `instrument_observations` tuple
2. Caller order of observations is preserved and meaningful.
3. **Empty** `instrument_observations = ()` is **valid** structure (partial /
   empty market state).
4. Partial snapshots (subset of intended subjects) are structurally valid.
   Completeness is **not** a domain invariant.
5. Production fail-closed rules for missing/stale facts belong to PF-M4 policy,
   not to domain validators.
6. Duplicate `instrument_id` values within one snapshot are rejected.
7. Nested observation session contexts must align to the root by exact stored
   values of all six session-context fields.
8. Domain does not sort instruments, fill gaps, carry forward prior snapshot
   prices, or synthesize observations.
9. Structural validity ≠ market truth, quote completeness, or watch
   materiality.

---

## 12. Korea / US compatibility

### 12.1 Requirement

First-slice structure **must support** at least:

- Korean market session profiles
- US market session profiles

### 12.2 How support is achieved (structure)

| Concern | Structural approach |
| --- | --- |
| Distinct markets | Distinct caller-supplied `market_id` values |
| Distinct venues | Distinct caller-supplied `venue_id` values |
| Session families | Distinct `session_profile_id` values |
| Timezone | Distinct `timezone_id` values (opaque) |
| Trading calendar | Distinct `calendar_id` values (opaque) |
| Status mapping | Map provider/session phases into `MARKET_STATUS_VALUES` at composition time (producer/caller), not via domain hard-coding |

### 12.3 Explicit non-hard-coding

Domain packages **must not** contain:

- default constants selecting KRX / NYSE / Nasdaq;
- default timezone constants as the only supported zone;
- default calendar constants as the only supported calendar;
- branching logic “if Korea then … else US …” inside validators;
- ticker suffix rules (`.KS`, exchange MIC inference, etc.).

### 12.4 One session context per snapshot

Cross-market / cross-session boards require **multiple snapshots** (or a later
architecture freeze for multi-session aggregates). First-slice
`ExplicitMarketSnapshot` is single-session-context.

### 12.5 Profile catalog ownership

A catalog of recommended Korea/US profile parameter sets (ids and opaque
reference strings) may be documented later for operators. That catalog is
**not** domain package code ownership in first slice.

---

## 13. Deferred responsibilities

| Deferred item | Until |
| --- | --- |
| Implementation of the seven Market\* packages | Separate implementation authorization after this architecture acceptance |
| Tests / README bodies as production artifacts | With package implementation authorization |
| PF-M4 `MarketSnapshotProducer` | Prerequisites A–C satisfied + PF-M4 implementation authorization |
| Provider Gateway market-adapter path | Prerequisite A (Gateway ownership) |
| Fact Store `market_fact` eligibility | Prerequisite B (Fact Store ownership) |
| Index identity / index observations | Later domain freeze if required |
| OHLC, bid, ask, volume, turnover, richer quotes | Later domain + ops freezes |
| Currency / unit fields on price | Later domain freeze |
| Multi-fact provenance graphs | Later domain freeze |
| Multi-session aggregate snapshot product | Later domain freeze |
| FX conversion, sector state, futures, options | Later domain milestones |
| Institutional / foreign / program trading flows | Later domain milestones |
| Market Watch materiality classifiers | PF-M5 |
| Portfolio valuation using market marks | Separate valuation architecture |
| Display names, tickers-as-fields, listing metadata | Later domain freeze if needed |
| Session profile operator catalog | Operational/docs freeze; not structure ownership transfer |

---

## 14. Forbidden responsibilities

Market\* first-slice domain packages **must not**:

1. Own or call **Provider Gateway**.
2. Own or call **Fact Store** (append, retrieve, supersede, mutate).
3. Own **MarketSnapshotProducer** runtime, composition orchestration, or
   fail-closed production policy execution.
4. Own **Market Watch** materiality or IRO wake triggering.
5. Own **Research**, Evidence Store, Operational Memory, Contradiction, EV, or
   CIO semantics.
6. Own **Trading**, orders, broker execution, or capital approval.
7. Perform **ticker / entity / alias / open-world resolution**.
8. Perform **valuation**, PnL, NAV, notional, or FX conversion math.
9. Include **OHLC, bid, ask, volume, turnover**, futures, options, sector, or
   flow fields in first-slice models.
10. Make **index identity** mandatory or introduce an index product surface.
11. Use **float** (or non-Decimal) domain price types.
12. **Auto-generate** identities or encode semantics/timestamps in IDs.
13. Hard-code **KRX / NYSE / Nasdaq / one timezone / one calendar** as universal
    defaults.
14. Normalize, sort, repair, synthesize, or carry-forward market observations.
15. Import operational, automation, IRO, or producer packages.
16. Persist, register, or orchestrate anything.
17. Redefine PF-M1–M4, IRO, Automation, or Portfolio\* accepted contracts.

---

## 15. Architecture questions (resolved)

| # | Question | Resolution |
| --- | --- | --- |
| 1 | Exact package decomposition | Seven packages: `MarketEndpoint`, `MarketVenue`, `MarketInstrument`, `MarketSessionContext`, `MarketFactProvenanceReference`, `MarketInstrumentObservation`, `MarketSnapshot` |
| 2 | Exact model ownership | One primary `Explicit*` model per package; status vocabulary constant owned by `MarketInstrumentObservation` |
| 3 | Exact validator ownership | One public validator per package co-located in `validation.py` |
| 4 | Validation order | Declared per §6; upstream once; first failure wins; exceptions propagate |
| 5 | Field minimums | Exactly the fields listed in §4; no optional first-slice fields |
| 6 | Collection ordering | Exact caller `tuple` order preserved; no sorting |
| 7 | Empty/partial snapshot rules | Empty observation tuple valid; partial coverage valid; completeness not domain-owned |
| 8 | Provenance reference shape | `fact_id` + `source_identity` + `collected_at` as opaque nonblank strings |
| 9 | Session-context shape | Six opaque fields: context id, market, venue, profile, timezone, calendar |
| 10 | Korea/US compatibility | Same structure; distinct opaque parameter sets; no hard-coded defaults |
| 11 | Deferred expansions | §13 |
| 12 | Forbidden responsibilities | §14 |

---

## 16. Risks

| ID | Risk | Severity | Mitigation |
| --- | --- | --- | --- |
| R1 | Producer invents interim Market\* models before packages exist | High | This freeze + PF-M4 R1/R4.C; implementation of producer blocked until packages accepted |
| R2 | Collapsing market and venue into one ambiguous identity | Medium | Separate endpoint packages and distinct session-context fields |
| R3 | Hard-coded Korea-only or US-only structure | High | Parameterized session context; forbidden defaults |
| R4 | Float price leakage | High | Exact `Decimal` type + finite check; float forbidden |
| R5 | Provenance becomes Fact Store ownership | High | Structural reference only; no I/O |
| R6 | Index / OHLC / flow scope creep into first slice | High | Explicit exclusions; deferred list |
| R7 | Session context gains wall-clock snapshot timestamp ownership | Medium | Timeless structural context; `collected_at` only as opaque provenance reference |
| R8 | Status vocabulary becomes free text | Medium | Closed `MARKET_STATUS_VALUES` membership check |
| R9 | Empty snapshot disallowed, forcing synthetic observations | High | Empty tuple explicitly valid; synthesis forbidden |
| R10 | Cross-namespace identity confusion with Portfolio subjects | Medium | Distinct Market\* namespaces; no Portfolio\* code dependency |
| R11 | Treating this architecture as producer implementation authorization | High | §17 explicit NOT AUTHORIZED for production code |
| R12 | Prerequisite Sequencing Review not checked into repo | Low | Binding intent recorded via mission + PF-M4 §4/§13; optional later doc check-in does not reopen this freeze |

---

## 17. Implementation authorization status

| Item | Status |
| --- | --- |
| Architecture document authored | **Yes** (this document) |
| Independent architecture review | **Required before package implementation** |
| Market\* package scaffold / production code / tests | **Not authorized by this document** |
| PF-M4 `MarketSnapshotProducer` implementation | **Not authorized by this document** (still requires A–C + PF-M4 implementation authorization) |
| Commit / tag / push | **Not authorized by this document** |

**Implementation authorization status: NOT AUTHORIZED**

This document freezes structure contracts only. Domain package implementation
requires:

1. acceptance of this architecture;
2. a separate implementation authorization for Market\* packages;
3. only then may PF-M4 production implementation proceed once prerequisites A
   and B are also satisfied under their owners.

---

## 18. Commit status

| Item | Status |
| --- | --- |
| Working tree change for this document | To be committed only with **explicit user approval** |
| Tag | Not created |
| Push | Not performed |
| Branch mutation | Not performed |
| Production code / tests | Not created |

Per repository agent contract and mission MODE: architecture authoring only;
**no commit, tag, push, stage, production code, or tests** in this task.

---

## 19. Architecture freeze summary

**This freeze defines:**

- seven Market\* domain packages and their ownership;
- exact first-slice models and field minimums;
- exact validators and validation order;
- identity, session, price, provenance, and snapshot aggregate invariants;
- Korea/US parameterized session compatibility without hard-coded defaults;
- empty/partial snapshot structural validity;
- non-ownership of Gateway, Fact Store, producer runtime, Market Watch,
  research, trading, valuation, and first-slice exclusions.

**This freeze does not:**

- implement packages or tests;
- authorize PF-M4 production code;
- introduce index identity as mandatory;
- redesign PF-M1–M4, IRO, Automation, or Portfolio\*.

**Prerequisite C structural boundary:** closed at architecture level by this
document. Package acceptance remains future implementation work.

---

## Residual open work (not defects in this freeze)

1. Architecture review acceptance of this document.
2. Authorized implementation of the seven packages + unit tests + READMEs.
3. Prerequisite A/B implementation under Gateway / Fact Store owners.
4. Operator session-profile parameter sets for first Korea and US profiles
   (non-domain catalog).
5. PF-M4 producer implementation authorization after A–C.
6. Later freezes for deferred market fields and products.

---

MARKET FIRST-SLICE DOMAIN ARCHITECTURE AUTHORED
