# ProviderGateway Market-Adapter Path Architecture

## Status and milestone

- Status: Architecture authored for independent review; additive
  ProviderGateway market-adapter path freeze
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Provider & Fact** (Layer 2 — Provider Gateway)
- Milestone: **PF-M4 Prerequisite A / sequencing step S3**
- Owner package identity (frozen PF-M1; not created by this document):
  `ProviderGateway`
- Additive capability: **market-adapter path** (slot reserved by PF-M1;
  adapter selection, wire mapping, and market-path health frozen here)
- This document is **not** a new product-package milestone and **not** a
  redesign of PF-M1, PF-M2, PF-M3, PF-M4, or Market\*
- Repository boundary: architecture authoring only; this document alone
  authorizes no production code, test, package scaffold, schema module,
  configuration, run artifact, or Git history mutation

This document freezes **only** the additive ProviderGateway market-adapter
path required so later Prerequisite B may consume a `market_fact` envelope
handoff.

It does **not** redesign frozen PF-M1 envelope / source-class identity.

It does **not** create a new package.

It does **not** own FactStore append, eligibility, persistence, or retrieval.

It does **not** own Market\* models, validators, or structural invariants.

It does **not** authorize PF-M4 `MarketSnapshotProducer` production.

Implementation requires a separate authorization after architecture review.
The `ProviderGateway` production package is currently absent. That absence
does not authorize a new package name.

---

## Normative first-slice surface (must remain explicit)

### This freeze implements ONLY

| # | Responsibility |
| --- | --- |
| 1 | **Market API Adapter** selection and boundary for the first market-ingress slice |
| 2 | **Provider Interface attachment** of that adapter without a new plane |
| 3 | **Wire → immutable provider payload envelope** mapping for market responses |
| 4 | **`source_class = market_fact`** tagging on success-path fact envelopes |
| 5 | **Gateway-owned `provider_id` and `collected_at`** at the market-path boundary |
| 6 | **Market-path health / failure / outage signaling** without inventing facts |
| 7 | **Korea-capable and US-capable adapter parameterization** as configuration, not exclusive hard-coded branches |
| 8 | **Handoff surface** that later Prerequisite B may consume |

### This freeze does NOT implement

| Concern | Owner (elsewhere) |
| --- | --- |
| **Fact Store** append / eligibility / retrieval | Prerequisite B / PF-M2 package lifetime |
| **Market\*** structure / validators / invariants | Prerequisite C — already frozen; consume-only |
| **Market Snapshot** composition | PF-M4 `MarketSnapshotProducer` |
| **Market Watch** Engine | PF-M5 |
| **KB Open API broker path** redesign | Frozen PF-M1 first slice |
| **Research AI** transport runtime | Stage 1/2 + later explicit freeze |
| **News / alternative data** | Architecture amendment required first |
| **Ticker / entity resolution** | Outside permanently |
| **Trading / Broker Execution** | Layer 15 BX-M1 |
| **Human Approval** (capital) | Layer 14 Human Authority |

---

## 1. Repository checkpoint

Verified immediately before authoring. No authoring proceeds from an
unverified checkpoint.

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| Path | `/Users/takesimple/Projects/JOO` | `/Users/takesimple/Projects/JOO` | Match |
| Branch | `feature/stage2-provider-runtime` | `feature/stage2-provider-runtime` | Match |
| HEAD | `8d193b2150606a0e72320f10e8b7ec24fdce9d47` | `8d193b2150606a0e72320f10e8b7ec24fdce9d47` | Match |
| Exact tag at HEAD | `v7.2-stage5-market-first-slice-domain-implementation` | Exact match (`git describe --exact-match --tags HEAD`) | Match |
| Tracked tree | Clean | Clean (`git status --short` shows only expected untracked docs) | Match |
| Unexpected dirty tracked files | None | None | Match |
| Unexpected in-boundary untracked production files | None | None | Match |

**Preserved out-of-boundary untracked files (read-only; not modified, not
staged):**

- `docs/JOO_PRODUCT_ARCHITECTURE.md`
- `docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md`
- `docs/provider/PF_M4_MARKET_SNAPSHOT_ARCHITECTURE.md`

**Production package absence (recorded, not a license to rename):**

| Package | Repository state at this freeze |
| --- | --- |
| `ProviderGateway` | **Absent** — identity remains frozen PF-M1 name |
| `FactStore` | **Absent** — Prerequisite B remains unauthored |
| `MarketSnapshotProducer` | **Absent** — PF-M4 production remains blocked |
| Market\* domain packages | **Present and frozen** at HEAD tag `v7.2-stage5-market-first-slice-domain-implementation` (Prerequisite C). This freeze consumes their existence as a sequencing fact only and must not import or depend on them. |

Checkpoint status: **Pass**. Not REVIEW BLOCKED.

---

## 2. Authority reviewed

Authority order is highest first. This freeze obeys and does not rewrite
higher authorities.

| Priority | Authority | Review result for this freeze |
| --- | --- | --- |
| 1 | `JOO_CONSTITUTION.md` | Single-owner responsibilities; validation-first; immutability; no hidden inference; operational layers must be separately approved and bounded |
| 2 | Frozen / committed architecture documents | PF-M1 envelope / source-class / Provider Interface reused; PF-M2 `market_fact` append remains deferred until after this handoff + B freeze; PF-M3 untouched; Market\* C structure consume-only; IRO / Automation untouched |
| 2 | `docs/JOO_PRODUCT_ARCHITECTURE.md` (present untracked; READ ONLY) | Layer 2 owns market API ingress and source-class tagging; Market APIs are a primary fact source; research AI is never primary truth; PF-M4 product row is a plane delivery sequence, not one-package ownership of ingress + snapshot |
| 2 | `docs/provider/PF_M1_PROVIDER_GATEWAY_ARCHITECTURE.md` | Frozen identity reused: one package `ProviderGateway`; immutable envelope field model; source-class taxonomy; Provider Interface plug-in shape; market-adapter slot reserved; broker-first first slice not rewritten |
| 2 | `docs/provider/PF_M2_FACT_STORE_ARCHITECTURE.md` | `market_fact` append deferred until market ingress **and** a later freeze; Fact Store must not re-call providers; failure/outage signals alone never invent facts |
| 2 | `docs/provider/PF_M3_PORTFOLIO_SNAPSHOT_ARCHITECTURE.md` | Untouched; Portfolio Snapshot is not a market-ingress owner |
| 2 | `docs/provider/PF_M4_MARKET_SNAPSHOT_ARCHITECTURE.md` (**APPROVED**; present untracked; READ ONLY) | Prerequisite A owned by `ProviderGateway`; producer is composition-only; Fact Store is the sole later fact upstream; no Gateway bypass |
| 2 | `docs/market/MARKET_FIRST_SLICE_DOMAIN_ARCHITECTURE.md` (frozen at v7.1) | C structure consume-only; Market\* must not own Gateway; venue/session/timezone/calendar are domain identities later, not Gateway types now |
| 2 | Frozen IRO product / IRO-M1 / IRO-M2 | Untouched; research lifecycle remains IRO; capital remains out of IRO; no provider ingress transferred into IRO |
| 2 | Frozen Automation M1–M3 | Untouched; development plane only; not a runtime dependency. M2 is committed under `docs/automation/`. M3 is present untracked and was read only. M1 is the accepted review-only `joo_auto` predecessor cited by M2/M3 and product/IRO/PF freezes; no M1 file exists under `docs/automation/` |
| 3 | Approved independent review results | See tokens below |
| 4 | Exact repository HEAD / tag | §1 |
| 5 | Existing milestone sequencing decisions | Locked **C → A → B → (A ∩ B ∩ C unlock) → PF-M4 production** |

**Required review tokens consumed:**

| Review | Token |
| --- | --- |
| `~/JOO-Automation/results/pf_m4_prerequisite_sequencing_review/latest.md` | **PF-M4 PREREQUISITE SEQUENCE APPROVED** |
| `~/JOO-Automation/results/pf_m4_market_snapshot_architecture_review/latest.md` | **PF-M4 ARCHITECTURE APPROVED** |
| `~/JOO-Automation/results/market_first_slice_domain_structure_architecture_review_v2/latest.md` | **MARKET FIRST-SLICE DOMAIN ARCHITECTURE APPROVED** |
| `~/JOO-Automation/results/market_first_slice_domain_structure_implementation_review/latest.md` | **MARKET FIRST-SLICE DOMAIN IMPLEMENTATION APPROVED** |

If any statement in this document appears to conflict with a higher authority
in that authority’s scope, the higher authority wins and this document is
defective — not a silent override.

**Conflict-rule check (pre-authoring):** this freeze does not redesign the
frozen PF-M1 envelope / source-class identity, create a new package, own
Market\* structure, own FactStore, or start PF-M4 production. **No
ARCHITECTURE CONFLICT.**

---

## 3. Sequencing position (S3 / Prerequisite A only)

### 3.1 Locked sequence

```text
C → A → B → (A ∩ B ∩ C unlock) → PF-M4 production
```

| Step | Work | This document |
| --- | --- | --- |
| **S1 / S2** | Prerequisite **C** architecture + implementation | **Already frozen** at HEAD tag `v7.2-stage5-market-first-slice-domain-implementation`. Do not reopen C. |
| **S3** | Prerequisite **A** architecture freeze | **This document** |
| **S4** | Prerequisite **A** implementation | **Not authorized** |
| **S5 / S6** | Prerequisite **B** architecture + implementation | **Not authorized**; B must not precede this A handoff freeze |
| **S7 / S8** | A ∩ B ∩ C unlock → PF-M4 production | **Not authorized** |

### 3.2 Parallelization retained from the sequencing board

| Pair | Allowed? | Status at this freeze |
| --- | --- | --- |
| C ∥ A | **Yes** | C is already accepted; A architecture may proceed |
| A architecture ∥ B architecture drafting | B may draft only **after** this handoff surface is specified | This document supplies that handoff surface; it does **not** author B |
| B implementation before A handoff freeze | **No** | Satisfied by authoring A first |
| A ∥ PF-M4 production | **No** | PF-M4 production remains blocked |
| Any prerequisite work inside `MarketSnapshotProducer` | **Forbidden** | Ownership collapse |

### 3.3 What “PF-M4 direction” means (non-redesign)

PF-M1 deferred market adapters to “PF-M4 direction.” PF-M2 deferred
`market_fact` append until market ingress **and** a later freeze. PF-M4
unbundles that product-row language:

- ingress remains `ProviderGateway`;
- persistence remains `FactStore`;
- composition alone is `MarketSnapshotProducer`.

This S3 freeze is the **A architecture** that PF-M1 reserved and PF-M4
Prerequisite A requires. It is not PF-M4 production and does not move ingress
into the producer.

### 3.4 Scope of S3

This freeze owns **A architecture only**:

- market API adapter selection for the first market-ingress slice;
- wire → immutable envelope mapping;
- `market_fact` tagging;
- Gateway-owned identity and collection time;
- market-path health / failure / outage signaling;
- Korea / US parameterization;
- the envelope handoff surface later B will consume.

This freeze does **not** own C (already frozen), B, or PF-M4 production.

---

## 4. Package ownership and additive-vs-new-package ruling

### 4.1 Ruling

| Option | Verdict |
| --- | --- |
| **Additive capability of frozen `ProviderGateway`** | **Selected and frozen** |
| New package (`MarketAdapter`, `MarketGateway`, `QuoteIngress`, `MarketFactStore`, sibling envelope package) | **Rejected** — invents a second ingress plane |
| Relocate market ingress into `FactStore` | **Rejected** — dual write / store-as-gateway |
| Relocate market ingress into `MarketSnapshotProducer` | **Rejected** — PF-M4 R3 / R9 / R10 |
| Relocate market ingress into Market\* domain packages | **Rejected** — C is structure-only and already frozen |
| Rename `ProviderGateway` because the production package is absent | **Rejected** — absence is not a rename license |

**Owner package identity:** `ProviderGateway` only.

**Additive capability name:** market-adapter path.

**Not created by this document:** the `ProviderGateway` package, any sibling
ops package, any Market\* file, any FactStore file.

### 4.2 Ownership table

| Concern | Owner |
| --- | --- |
| This architecture document | JOO `docs/provider/` |
| Market API Adapter (first-slice market path) | `ProviderGateway` (additive) |
| Provider Interface (frozen PF-M1 contract) | `ProviderGateway` |
| Immutable provider payload envelope (frozen field model) | `ProviderGateway` |
| `source_class = market_fact` on market success-path envelopes | `ProviderGateway` |
| `provider_id` and `collected_at` at the Gateway boundary | `ProviderGateway` |
| Market-path health / failure / outage signals | `ProviderGateway` |
| Authentication **use** at the market-path edge | `ProviderGateway` (secrets **supply** remains operator/config outside package invention) |
| KB Open API broker path | `ProviderGateway` (frozen PF-M1 first slice; **not redesigned here**) |
| Fact Store append / eligibility / retrieval | **Not this freeze** (Prerequisite B / `FactStore`) |
| Market\* models / validators / invariants | **Not this freeze** (Prerequisite C; already frozen) |
| Market Snapshot composition | **Not this freeze** (PF-M4) |
| Market Watch, IRO, Evidence, trading, Human Approval | **Not this package** |

### 4.3 Non-package rule

The market-adapter path must not create sibling operational packages for
“MarketAdapter,” “MarketGateway,” “QuoteIngress,” “MarketFactStore,”
“MarketEnvelope,” or “MarketHealth.” Internal modules of `ProviderGateway`
only.

### 4.4 Layout intent (additive; not a scaffold)

PF-M1 §3.5 layout remains the package-structure intent. This freeze adds
only the reserved market-adapter slot:

```text
ProviderGateway/
  adapters/
    kb_open_api.py        # frozen PF-M1 broker adapter (identity unchanged)
    market_api.py         # additive first-slice Market API Adapter
```

Exact file splitting inside `adapters/` may vary at later implementation
without changing ownership. Additional later vendor modules may appear under
`adapters/` only if they implement the same Provider Interface, declare
`market_fact`, and remain inside `ProviderGateway`. This document does **not**
create any of those files.

### 4.5 Absence rule

`ProviderGateway` production code is currently absent. S3 architecture may
proceed. S3 implementation remains separately authorized. Absence of the
package is **not** authority to invent `MarketAdapter`, `MarketGateway`, or
any other production package name.

---

## 5. Relationship to frozen PF-M1 broker-first first slice

### 5.1 What remains frozen

PF-M1 remains the canonical Provider Gateway identity. This freeze reuses
and does not rewrite:

- one-package identity `ProviderGateway`;
- KB Open API as the broker-first first-slice adapter;
- `broker_fact` tagging on the KB success path;
- immutable envelope field model;
- source-class taxonomy `broker_fact | market_fact | research_ai`;
- ban on news / non-frozen classes without architecture amendment;
- Provider Interface plug-in shape;
- authentication uses operator-supplied credentials; no secrets in payloads;
- failure / outage signaling without inventing success facts;
- EvidenceProvenance `source_class` taxonomy (`primary | secondary | unknown`)
  as a **different plane** that must not be reused here.

### 5.2 How to read PF-M1’s deferred market sentence

PF-M1 first-slice statement **“PF-M1 does not produce `market_fact`
envelopes”** is the **deferred first-slice scope** of the broker-first
milestone. It is not a permanent ban on the reserved market-adapter slot.

This additive freeze **authorizes that reserved slot**. It does not:

- rewrite the KB broker-first first slice;
- retag KB envelopes as `market_fact`;
- change PF-M1 package identity;
- reopen PF-M1 broker authentication, broker health, or broker payload rules.

### 5.3 Broker-path isolation (normative)

1. The KB Open API Adapter remains a **broker** adapter. Successful KB
   envelopes remain `broker_fact`.
2. The Market API Adapter is a **distinct** adapter attachment. Successful
   market envelopes are `market_fact` only.
3. The market path **must not** retag as `broker_fact`.
4. The broker path **must not** retag as `market_fact`.
5. Sharing a commercial vendor family, if that ever occurs at implementation,
   does **not** collapse adapter identity, source class, or health path.
6. This freeze does **not** redesign KB Open API broker-path credentials,
   request surface, or trading-write exclusion.

### 5.4 Package-lifetime vs this additive freeze

| Concern | PF-M1 first implementation | This additive freeze |
| --- | --- | --- |
| KB Open API broker ingress | Yes — only broker adapter | Unchanged |
| Market API adapters | Slot reserved; not delivered | **Adapter selection + mapping + health frozen; implementation not authorized** |
| `broker_fact` production | Yes | Unchanged |
| `market_fact` production | No | **Architecture authorized; implementation not authorized** |
| `research_ai` runtime | Deferred | Still deferred |
| News / non-frozen classes | Forbidden | Still forbidden |

---

## 6. First-slice adapter selection

### 6.1 Authorized first-slice adapter

| Field | Decision |
| --- | --- |
| **Name** | **Market API Adapter** |
| **Package** | Internal component of `ProviderGateway` only |
| **Attachment** | Frozen PF-M1 Provider Interface |
| **Source-class declaration** | `market_fact` for successful fact-class payloads |
| **Boundary** | Read-oriented external market-provider request/response ingress |
| **Vendor monopoly** | **Not frozen.** Product architecture names “market data providers” / “Market APIs” without a single commercial vendor. This freeze therefore authorizes the **adapter class and boundary**, not an exclusive named vendor. |

### 6.2 Why no exclusive commercial vendor is frozen

PF-M1 could name **KB Open API** because product architecture names it as the
first broker. Product architecture does **not** name a first market vendor.

Freezing KRX, NYSE, Nasdaq, or one commercial quote vendor as the sole
permanent adapter would:

- invent a vendor without product authority;
- risk a single-exchange architecture;
- conflict with Korea/US parameterization without exclusive branches.

Concrete vendor binding is **operator-supplied adapter configuration** and is
fixed only by a later implementation authorization. Additional named vendor
adapters may later plug into the same Provider Interface inside
`ProviderGateway` without a new package and without redesigning the envelope
or source-class model.

### 6.3 First-slice authorized request surface

The Market API Adapter may issue **read-oriented** market-provider requests
whose captured content is intended to support later first-slice market
observation composition. Architecture-level request intent is limited to
provider-native:

- last / reference price observations as the provider exposes them;
- market-status / session-phase observations as the provider exposes them;
- venue / session / timezone / calendar labels as the provider exposes them;
- provider-native instrument or symbol codes as **opaque payload content**.

The adapter does **not** productize those fields into Market\* types.

### 6.4 First-slice adapter non-responsibilities

The Market API Adapter must **not**:

- place, cancel, or otherwise write broker/trading orders;
- call Fact Store or append facts;
- construct Market\* domain objects;
- resolve tickers or entities into JOO subject ids;
- request or productize OHLC, bid/ask, volume, turnover, FX, sector state,
  futures, options, or flow surfaces as Gateway extras;
- call research AI providers or treat research text as market truth;
- ingest news or alternative data;
- merge Korea and US wire responses into one synthetic global envelope;
- heal missing prices or statuses into success.

Extra fields that happen to appear on a provider wire response may remain
**opaque captured payload content**. Capturing them is not ownership of those
later products.

### 6.5 One collection attempt, one envelope

| Rule | Statement |
| --- | --- |
| Envelope granularity | One accepted success envelope maps **one** market-provider wire response (or one structured mapping of that response) for **one** collection attempt |
| No synthetic global board | Gateway does not merge multiple venue/session families into one invented “world quote” envelope |
| Cross-venue needs | Separate collection attempts / envelopes; later PF-M4 composes **one session profile per emission** |
| Provider-native batching | If a provider returns a batched wire body, the batch remains opaque payload content of that one envelope unless a later implementation freeze splits mapping without semantic repair |

### 6.6 Adapter identity vs venue identity

`provider_id` identifies the **Gateway adapter / provider path**.

Venue, market, session, timezone, and calendar values that appear in wire
responses are **opaque payload content**. They are not Gateway-owned
`MarketEndpoint`, `MarketVenue`, `MarketSessionContext`, or related types.

---

## 7. Provider interface attachment

### 7.1 Reuse, do not redesign

The Market API Adapter attaches through the **frozen PF-M1 Provider
Interface**. This freeze does not invent a second interface, a market-only
envelope type, or a parallel health plane.

PF-M1 §5.4 already exists so later market adapters can plug in without
redesigning the envelope or source-class model. This freeze **uses** that
slot.

### 7.2 Required interface capabilities (market-path binding)

An adapter implementation on this path must:

| Capability | Market-path rule |
| --- | --- |
| **Identity** | Expose a stable nonblank `provider_id` for that market-adapter binding |
| **Source class declaration** | Declare `market_fact` for successful fact-class payloads it produces. Declaration is explicit at construction / adapter identity — **never inferred** from payload text |
| **Fetch / collect** | Perform authenticated request(s) and return **either** a successful immutable envelope **or** a structured failure/outage signal — never a silent empty “success” with invented body |
| **Health** | Support a health/availability probe or last-known health snapshot for that market-provider path |
| **No domain mutation** | Not construct Market\* / Portfolio\* / Evidence\* objects; not write Fact Store |

### 7.3 Interface non-goals retained

The Provider Interface still does **not**:

- schedule 24/7 jobs;
- decide IRO run starts;
- place broker orders;
- abstract research AI committee completion;
- define Fact Store append APIs;
- define Market Snapshot composition.

### 7.4 Later adapters

Later named market-vendor adapters, if authorized, attach to the **same**
Provider Interface inside `ProviderGateway`. They do not justify a new
package, a new source class, or a new envelope field model.

Research AI adapters remain deferred. News adapters remain forbidden without
architecture amendment.

---

## 8. Wire → envelope mapping

### 8.1 Mapping rule (normative)

```text
External market-provider wire response (or structured error)
        │
        ▼
Market API Adapter maps fields (no semantic repair)
        │
        ▼
Immutable Provider Payload Envelope
  source_class = market_fact   (success-path fact envelopes)
  (frozen after acceptance; no in-place rewrite)
```

This is the PF-M1 wire → envelope rule applied to the market path. It is not
a new mapping plane.

### 8.2 Acceptance

**Acceptance** means the envelope object has been constructed and validated at
the type / nonblank / enum / required-presence level. After acceptance:

- field values must not be mutated in place;
- “corrections” require a **new** envelope (new collection identity / time),
  never silent overwrite of a prior accepted envelope’s body.

Validation is structural only. No identifier normalization, no trim policies
that invent identity, no unit conversion of economic quantities, no timezone
conversion that rewrites payload meaning, and no mapping into Market\* types.

### 8.3 Allowed mapping

**Allowed:** copy / project provider wire fields into the frozen envelope
shape:

- envelope identity and Gateway-owned provenance fields;
- explicit `source_class`;
- status;
- opaque `payload` body capturing provider-returned structured content;
- optional non-secret diagnostics / correlation id.

**Forbidden under any “normalization,” “enrichment,” or “convenience” name:**

- semantic extraction;
- ticker / entity / alias resolution into JOO subject ids;
- construction of Market\* models (`ExplicitMarket`, `ExplicitMarketVenue`,
  `ExplicitMarketInstrument`, `ExplicitMarketSessionContext`,
  `ExplicitMarketFactProvenanceReference`,
  `ExplicitMarketInstrumentObservation`, `ExplicitMarketSnapshot`);
- portfolio or market snapshot composition;
- research synthesis or opinion shaping;
- inventing missing prices, quotes, statuses, calendars, or sessions;
- converting research AI text into `market_fact`;
- retagging broker payloads as `market_fact` or market payloads as
  `broker_fact`;
- applying EvidenceProvenance `primary | secondary | unknown`.

### 8.4 Provider-native identifiers

Provider symbols, exchange codes, MIC-like strings, session names, timezone
labels, and calendar labels in the payload body are **opaque captured
content**. Mapping them to JOO market / venue / instrument / session
identities is **not** Gateway ownership (later Fact Store consumers / PF-M4
explicit bindings / Market\* structure).

---

## 9. Envelope field reuse and market-path tagging

### 9.1 Reused field model (exact)

Reuse the frozen PF-M1 immutable provider payload envelope. Do not add
market-only required fields and do not drop frozen fields.

| Field | Rule on the market path |
| --- | --- |
| `envelope_id` | Opaque nonblank string; identity of this ingress capture |
| `provider_id` | Nonblank; Gateway-owned adapter/provider identity for this market-path binding |
| `source_class` | Exactly one frozen class; market success-path fact envelopes = **`market_fact`** |
| `collected_at` | UTC collection timestamp at the **Gateway boundary** |
| `status` | Success or failure status enum (architecture-level; exact names at implementation freeze) |
| `payload` | Immutable body capturing market-provider structured content **or** empty/absent on pure failure paths as defined by status |
| `error_diagnostics` | Optional structured diagnostics on failure; must not contain secrets |
| Optional `request_correlation_id` | Opaque id linking attempt logs without embedding secrets |

### 9.2 `provider_id` assignment

1. `provider_id` is **Gateway-owned**.
2. It identifies the market-adapter binding that performed the collection.
3. It is stable and nonblank for that binding.
4. It is **distinct** from the KB Open API broker adapter identity.
5. If later implementation authorizes multiple vendor bindings, each binding
   has its own `provider_id`.
6. It is **not** inferred from payload free text.
7. It is **not** a Market\* `market_id`, `venue_id`, `instrument_id`, or
   `session_profile_id`.

### 9.3 `collected_at` assignment

1. `collected_at` is the UTC time at which Gateway accepted the capture.
2. It is assigned at the Gateway boundary, not by Fact Store and not by
   Market\*.
3. Exchange transaction times, quote times, or session clocks that appear on
   the wire remain **opaque payload content**. They do not replace
   `collected_at`.
4. Later Fact Store `appended_at`, if any, must remain a different timestamp
   (PF-M2 rule; not authored here beyond the handoff constraint).
5. Gateway must not backdate, skew-correct, or invent `collected_at` to
   manufacture continuity.

### 9.4 `source_class` declaration

1. Source class is **explicit at construction**.
2. The Market API Adapter declares `market_fact` for successful fact-class
   envelopes.
3. Gateway must **never infer** class from payload text, filename, URL, venue
   string, or “it looks like a price.”
4. Success-path market fact envelopes use **exactly** `market_fact`.
5. Failure / outage outputs are not a license to emit a success envelope with
   an invented class or invented price body.
6. `research_ai` remains recorded on the Layer 2 taxonomy and is **not**
   produced by this path.
7. News or any class outside `broker_fact | market_fact | research_ai`
   remains forbidden without architecture amendment.

### 9.5 Immutability invariants (reused)

1. Accepted envelopes are immutable value records.
2. Payload body bytes/structure after acceptance are not rewritten.
3. Source class is explicit at construction; never inferred later.
4. Gateway does not append envelopes to durable Fact Store history.
5. Gateway does not delete or revise prior envelopes it has already handed
   off; consumers treat each envelope as an append **candidate**.

### 9.6 EvidenceProvenance non-collision (reused)

| Concept | Plane | Values |
| --- | --- | --- |
| Provider Gateway **source class** | Provider & Fact ingress | `broker_fact` \| `market_fact` \| `research_ai` |
| Evidence Provenance **source_class** | Research evidence | `primary` \| `secondary` \| `unknown` |

These taxonomies remain different. The market path must not reuse or redefine
`EvidenceProvenance` enums for provider-fact tagging.

---

## 10. Authentication boundary

### 10.1 Reuse PF-M1 boundary; apply it to the market path

1. **Gateway uses credentials; it does not invent secret storage.**
   Operator-supplied configuration, environment, or external secret injection
   provides market-provider credentials. This freeze does not mandate a vault
   product.
2. **Authentication material must not appear** in immutable payload bodies
   intended for later Fact Store handoff (no API keys, tokens, or passwords
   inside envelope `payload` or stored diagnostics).
3. **Authenticated access is part of Layer 2 responsibility.** The Market API
   Adapter constructs authenticated requests and observes auth failures as
   provider failures/outages, not as silent success.
4. **Auth failure is a provider failure class**, not a research, CIO, Market
   Watch, or capital event.
5. **Write / trading credentials are out of this path.** Even if a vendor
   later also hosts order APIs, capital write paths remain Broker Execution
   ownership.
6. **No credential sharing** into IRO, Market\*, Portfolio\*, Fact Store, or
   `MarketSnapshotProducer`. Those consumers must not receive market secrets
   through envelopes.

### 10.2 Failure posture for authentication

| Condition | Signal |
| --- | --- |
| Missing / invalid credentials at call time | Failure signal; no synthetic prices or statuses |
| Auth rejected by the market provider | Failure / outage class per §11; envelope status is failure, not success |
| Transport timeout during auth or request | Outage / unavailable signaling |

---

## 11. Health / failure / outage signaling

### 11.1 Purpose

The market path must **fail closed on inventing market facts** and must
**surface** provider problems explicitly. Health distinguishes “no new market
facts because none were requested” from “market provider unavailable.”

### 11.2 Health snapshot intent (reused; market-path scoped)

| Field | Rule |
| --- | --- |
| `provider_id` | Same identity as the market-adapter binding |
| `observed_at` | UTC observation time |
| `availability` | Available / degraded / unavailable (exact enum at implementation) |
| `detail` | Optional non-secret diagnostic summary |

Health is **per market-adapter binding**, not a merged synthetic “Korea and
US are both up” product. KB broker-path health remains a separate PF-M1
signal.

### 11.3 Health non-responsibilities

Health checks must **not**:

- trigger IRO runs or Market Watch;
- auto-execute broker orders;
- fabricate fact envelopes on “available”;
- invent last prices or market statuses;
- double as Fact Store freshness policy or PF-M4 fail-closed policy;
- import Market\* session calendars to decide availability.

### 11.4 Failure / outage signal classes (reused intent)

| Class | Meaning on the market path |
| --- | --- |
| `AUTH_FAILURE` | Credentials missing, invalid, or rejected |
| `TRANSPORT_FAILURE` | Network / timeout / TLS or equivalent transport error |
| `PROVIDER_ERROR` | HTTP/API error with provider error body (captured in diagnostics, not as success payload) |
| `UNAVAILABLE` / outage | Market-provider path not available for fact collection |
| `RATE_LIMITED` | Provider throttling observed (when detectable) |
| `VALIDATION_FAILURE` | Wire response could not be mapped into a valid envelope without repair |

Exact enum names may be fixed at implementation; the **class intent** is
frozen by PF-M1 and reused here.

### 11.5 Success vs failure semantics (market path)

| Outcome | Status | `source_class` | `payload` | May later be treated as a market price or market status fact? |
| --- | --- | --- | --- | --- |
| Mapped provider success response | Success | `market_fact` | Opaque captured market content | **Candidate only** — B decides eligibility later; Gateway does not append |
| Auth / transport / provider / unavailable / rate-limit / validation failure | Failure | Not a success-path fact tag | Empty/absent on pure failure, or diagnostics only | **No** — must not be treated as an invented price or invented market status |

### 11.6 Posture (normative)

1. **No synthetic last prices, quotes, statuses, calendars, or sessions** on
   failure.
2. **No elevation of partial garbage to success** by silent repair.
3. Failure signals are first-class outputs alongside envelopes; consumers must
   not need to parse free-text logs to detect outage.
4. Downstream Fact Store (later B) and snapshot / watch / execution planes
   are expected to treat missing/failed ingress as **staleness / fail-closed
   inputs**. This freeze supplies the signals; it does not implement those
   policies inside Gateway and does not author B.
5. Failures are **not** CIO events, evidence findings, Market Watch
   materiality events, or human capital approvals.

---

## 12. Korea / US parameterization

### 12.1 Required first-slice configurations

First-slice architecture must accept, as **adapter configuration
parameters**, at least:

| Configuration family | Intent |
| --- | --- |
| **Korea-capable** | Parameters sufficient to collect from a Korean-market-capable provider binding without hard-coding KRX as the only exchange |
| **US-capable** | Parameters sufficient to collect from a US-market-capable provider binding without hard-coding NYSE / Nasdaq as the only exchange |

Both families are required as **accepted parameter shapes**, not as two
exclusive permanent product forks.

### 12.2 What may be parameterized

Architecture-level parameter classes include:

| Parameter class | Intent |
| --- | --- |
| Provider binding | Which operator-supplied market-provider credential/config this adapter instance uses |
| Venue / market target | Opaque target identifiers or request selectors supplied as configuration — not Gateway-owned Market\* types |
| Session / window selectors | Opaque request selectors if the provider requires them |
| Timezone / calendar selectors | Opaque configuration or request selectors if the provider requires them — not a Gateway calendar database |
| Request set | Which first-slice read endpoints this binding may call |

Exact config schema is fixed at implementation authorization. **Intent** is
frozen: multi-venue / multi-session via parameters.

### 12.3 What must not be hard-coded as permanent architecture

The market-adapter path must **not** hard-code as the sole extension
mechanism:

- KRX as the only exchange;
- NYSE / Nasdaq as the only exchange;
- one timezone;
- one trading calendar;
- `if Korea then … else US …` exclusive branches as the only way to add a
  third venue/session family.

Additional venues/sessions attach by **additional parameter profiles** or
later Provider Interface adapter bindings inside `ProviderGateway`.

### 12.4 Opaque payload vs Gateway types

Venue, session, timezone, and calendar values that appear in wire responses
remain **opaque payload content**. Gateway must not:

- import or depend on `MarketEndpoint`, `MarketVenue`, `MarketInstrument`,
  `MarketSessionContext`, `MarketFactProvenanceReference`,
  `MarketInstrumentObservation`, or `MarketSnapshot`;
- construct those types;
- treat opaque payload strings as accepted Market\* identities;
- own an exchange trading-calendar or timezone-database product.

Market\* already owns parameterized session **structure** (Prerequisite C).
PF-M4 later owns session-profile **composition**. This freeze owns only
ingress parameterization and opaque capture.

### 12.5 No merged multi-session envelope

A Korea-capable collection and a US-capable collection are distinct
collection attempts. Gateway does not merge them into one synthetic envelope.
Later PF-M4 emits one session profile per snapshot; that rule is downstream
and is not re-owned here.

---

## 13. Payload opacity and non-normalization

### 13.1 What payload may contain

On a success-path `market_fact` envelope, `payload` may contain the
provider-returned structured content as mapping allows, including opaque:

- provider-native prices / reference prints;
- provider-native status or session-phase strings;
- provider-native venue, market, symbol, or instrument codes;
- provider-native timezone, calendar, or timestamp strings;
- other wire fields the provider included on that response.

Payload is **captured market content**, not Market\* structure.

### 13.2 What payload must not contain

| Forbidden payload content | Reason |
| --- | --- |
| API keys, tokens, passwords, signatures | Authentication boundary |
| Market\* domain objects or imported Market\* types | C / Gateway plane split |
| JOO subject ids invented by ticker / entity resolution | Resolution is outside Gateway |
| Research AI text presented as a price or status | Research is never market truth |
| Broker holdings / balances retagged as market content | Broker-path isolation |
| News / social / alternative-data bodies | Non-frozen class |
| Gateway-invented prices or statuses | Fail-closed |
| Fact Store append metadata (`appended_at`, store ids invented here) | Store is B / PF-M2 |

### 13.3 Extra wire fields are not first-slice products

If a provider wire body includes OHLC, bid, ask, volume, turnover, FX, or
flow-like fields, those bytes/fields may remain opaque captured content.
This freeze does **not**:

- authorize those surfaces as Gateway products;
- map them into first-slice Market\* observation fields;
- require later B or PF-M4 to interpret them.

Later domain / ops freezes may consume stored opaque content only under their
own authority.

### 13.4 Non-normalization restated

Gateway does not normalize, trim-to-invent-identity, sort, convert units,
convert timezones as semantic repair, resolve entities, or reconstruct
payloads into domain models. The envelope freezes **what was received** with
**who / when / class**, not what JOO believes economically.

---

## 14. Handoff contract for later Prerequisite B

This section freezes **only** the surface B may later consume. It does **not**
author Prerequisite B architecture, eligibility tables beyond this handoff
constraint, persistence, supersession, or retrieval.

### 14.1 Handoff object

The sole success-path handoff object is the **frozen PF-M1 immutable provider
payload envelope** produced by the Market API Adapter.

B does not receive Market\* objects from Gateway. B does not receive PF-M4
snapshots from Gateway.

### 14.2 Success-path constraints B may rely on

When Gateway emits a success-path market fact envelope:

1. the envelope is **immutable** after acceptance;
2. `source_class` is **exactly** `market_fact`;
3. `provider_id` is present, nonblank, and **Gateway-owned**;
4. `collected_at` is present and is the **Gateway-boundary** UTC collection
   time;
5. `envelope_id` is present and opaque;
6. `status` is success;
7. `payload` is opaque captured market content, **not** Market\* structure;
8. payload and diagnostics contain **no secrets**;
9. source class was **explicit at construction**, not inferred.

### 14.3 Failure / outage constraints B must honor

1. Failure / outage envelopes or signals **must not** be treated as invented
   prices or invented market statuses.
2. A failure / outage output alone is **not** a license to append a synthetic
   last price or “closed/open” status as primary market truth.
3. Health snapshots are observability / fail-closed inputs, not facts.

This restates the PF-M2 first-slice posture (“Gateway failure/outage signal
alone → never invent facts”) for the market path. B’s later freeze must not
weaken it.

### 14.4 Ownership edges of the handoff (normative)

| Actor | Must | Must not |
| --- | --- | --- |
| **Gateway** | Construct and emit envelopes / failure signals | Append to Fact Store; call Fact Store; persist store history; compose Market Snapshot |
| **Fact Store (later B)** | Consume handed-off envelopes under its own later eligibility freeze | Re-fetch market APIs; become a second Gateway; repair `source_class`; invent facts from outage signals |
| **MarketSnapshotProducer (later PF-M4)** | Read stored facts from Fact Store after A ∩ B ∩ C | Call Gateway as a fact upstream; call market HTTP |

### 14.5 Direction

```text
Market API Adapter
        │
        ▼
Immutable envelope (source_class = market_fact)
        │
        │  handoff only — no append, no store call
        ▼
[Prerequisite B — FactStore market_fact eligibility / retrieval]
        │
        │  later; not authored here
        ▼
[PF-M4 MarketSnapshotProducer — composition only]
```

Gateway does **not** require Fact Store to exist at runtime to **construct**
envelopes. Gateway must **not** implement Fact Store persistence to complete
this freeze.

### 14.6 What this section deliberately does not freeze

- append eligibility tables beyond the handoff constraints above;
- `fact_id` assignment;
- `appended_at`;
- supersession linkage;
- retrieval API;
- storage engine;
- class-expansion implementation.

Those remain Prerequisite B.

---

## 15. Upstream / downstream edges and forbidden edges

### 15.1 Upstream of the market-adapter path

**In scope**

- External market data providers, through operator-supplied Market API
  Adapter configuration (Korea-capable and US-capable bindings required as
  parameters)

**Not upstream**

- IRO plans, evidence, CIO stances
- Human capital approvals
- Allocation proposals
- Development Automation manifests as runtime market state
- News / alternative sources without architecture amendment
- Market\* packages as ingress types
- Fact Store as a source of live quotes
- Research AI / Committee outputs as prices
- KB Open API broker payloads as silently retagged market facts

### 15.2 Downstream of the market-adapter path

**In scope**

- Later Fact Store consumers of `market_fact` immutable payloads
  (Prerequisite B / PF-M2 package lifetime). Gateway emits / hands off; it
  does not become the store.
- Observability consumers of market-path health / failure / outage signals
  (read-only)

**Package-lifetime (not delivered by this freeze)**

- Fact Store: `broker_fact` and `market_fact` only
- PF-M4 composition **after** stored retrieval — never as a Gateway
  downstream that skips the store

**Not downstream ownership**

- Evidence Store
- Operational Memory
- Contradiction / Expected Value / CIO
- Human Approval
- Broker Execution command path
- Market Watch wake logic
- Market\* validators as a Gateway success-path dependency

### 15.3 Forbidden edges (normative)

| Forbidden edge | Reason |
| --- | --- |
| `ProviderGateway` → Fact Store ownership / append / retrieve | Store is PF-M2 / later B |
| `ProviderGateway` → Fact Store runtime call | Dual-plane collapse; this freeze emits only |
| Fact Store → market HTTP re-fetch | PF-M2 “no second Gateway” |
| `ProviderGateway` → Market\* import / construct | C is structure-only; Gateway must not own it |
| `ProviderGateway` → `MarketSnapshotProducer` composition | PF-M4 ownership |
| `MarketSnapshotProducer` → `ProviderGateway` as fact upstream | PF-M4 R9 |
| `ProviderGateway` → IRO run coordination | Plane separation |
| `ProviderGateway` → Evidence Store | Research artifacts ≠ provider facts |
| `ProviderGateway` → CIO / EV / Contradiction | Not ingress |
| `ProviderGateway` → Human Approval | Capital authority elsewhere |
| `ProviderGateway` → Broker Execution trading | Capital plane; BX-M1 later |
| Market path → retag `broker_fact` | Broker-path isolation |
| Broker path → retag `market_fact` | Broker-path isolation |
| `research_ai` → Fact Store as primary fact | Hard product rule |
| `ProviderGateway` → news ingest without amendment | PF-M1 R1 retained |
| `ProviderGateway` → `joo_auto` runtime dependency | Automation is development-only |
| `ProviderGateway` reimplements `AIAdapter` / `Committee` / M22 | Product risk R5 |

### 15.4 Consistency with frozen planes

| Plane | Result |
| --- | --- |
| Constitution | Single owner; no hidden inference; operational layer separately bounded |
| Product Architecture Layer 2 | Market API ingress remains Provider Gateway |
| PF-M1 | Additive slot used; broker-first first slice untouched |
| PF-M2 | Handoff only; `market_fact` eligibility remains B |
| PF-M3 | Untouched |
| PF-M4 | Prerequisite A architecture only; production still blocked |
| Market\* / C | Consume-only as a sequencing fact; no type dependency |
| IRO / IRO-M1 / IRO-M2 | Untouched |
| Automation M1–M3 | Untouched — development-only |

---

## 16. Deferred responsibilities

| Deferred responsibility | Until |
| --- | --- |
| `ProviderGateway` package scaffold and market-path production code | Separate **A implementation** authorization (S4) |
| Fact Store `market_fact` append eligibility and retrieval | Prerequisite **B** architecture + implementation (S5 / S6) |
| PF-M4 `MarketSnapshotProducer` production | A ∩ B ∩ C unlock **and** separate PF-M4 implementation authorization |
| Additional named commercial market-vendor adapters | Later Gateway adapter freeze inside `ProviderGateway` |
| Research AI transport classification runtime under Gateway | Explicit later freeze; Stage 1/2 retain invocation |
| News / alternative non-frozen source classes | Architecture amendment required first |
| OHLC / bid / ask / volume / turnover as product surfaces | Later domain + ops freezes |
| FX conversion, sector state, futures, options, flows | Later domain + ops milestones |
| Ticker / entity / alias resolution | Permanently outside Gateway |
| Market Watch materiality | **PF-M5** |
| Portfolio Snapshot / valuation / PnL / NAV | PF-M3 / separate valuation architecture |
| Broker Execution using any gateway channel | **BX-M1** + Human Approval |
| Exact adapter config schema / enum names as code | A implementation authorization |
| Full rate-limit control plane / 24/7 scheduler topology | Later ops freezes |
| Optional durable recording of health/outage signals inside Fact Store | Explicit later B/store contract if ever needed |

C implementation is **not deferred** — it is already frozen. This document
must not reopen it.

---

## 17. Forbidden responsibilities

The ProviderGateway market-adapter path **must not**:

1. Create a new package (`MarketAdapter`, `MarketGateway`, `QuoteIngress`,
   `MarketFactStore`, sibling envelope / health packages).
2. Rewrite PF-M1, PF-M2, PF-M3, PF-M4, or Market\* architecture documents.
3. Own Fact Store append, eligibility, persistence, or retrieval.
4. Call Fact Store.
5. Own or import Market\* models, validators, or structural invariants.
6. Compose Market Snapshot or Portfolio Snapshot.
7. Start PF-M4 production, Market Watch, valuation, or IRO.
8. Retag market envelopes as `broker_fact` or broker envelopes as
   `market_fact`.
9. Redesign the KB Open API broker path.
10. Infer `source_class` from payload text.
11. Invent last prices, quotes, market statuses, calendars, or sessions on
    failure / outage.
12. Treat research AI as market truth or produce `research_ai` envelopes on
    this path.
13. Ingest news / alternative data without architecture amendment.
14. Resolve tickers, entities, or aliases into JOO subject ids.
15. Productize OHLC, bid, ask, volume, turnover, FX, sector, futures,
    options, or flow surfaces as first-slice Gateway extras.
16. Hard-code KRX-only, NYSE/Nasdaq-only, one timezone, or one calendar as
    the permanent architecture.
17. Place, cancel, or otherwise execute broker orders.
18. Share secrets into payloads, IRO, domain packages, or producers.
19. Absorb Automation M1–M3 as a runtime dependency.
20. Provide a demo bypass from producer or domain packages to HTTP / Gateway.
21. Reuse EvidenceProvenance `primary | secondary | unknown` as provider-fact
    class.
22. Authorize implementation, commit, tag, or push by the existence of this
    document.

---

## 18. Risks

| Risk | Severity | Mitigation in this freeze |
| --- | --- | --- |
| Invent a new package because `ProviderGateway` is absent | High | §4 absence rule; additive-only ruling |
| Rewrite PF-M1 “no market_fact in first slice” as a permanent ban | High | §5.2 reads it as deferred first-slice scope |
| Collapse market path into KB broker path / retag classes | High | §5.3 broker-path isolation; explicit `market_fact` |
| Author B or PF-M4 inside this document | High | §3 S3-only; §14 handoff surface only |
| Import Market\* types into Gateway mapping | High | §8 / §12 / §13 opacity; forbidden imports |
| Freeze KRX-only or NYSE-only adapter as exclusive architecture | High | §6 no vendor monopoly; §12 parameterization |
| `if Korea else US` as the only extension mechanism | High | §12.3 |
| Invent prices/statuses on outage | High | §11 fail-closed; §14.3 |
| Gateway appends or Fact Store re-fetches | High | §14.4 |
| Producer / demo HTTP bypass | High | §15.3; forbidden #20 |
| Research AI or news as market truth | High | Taxonomy + forbidden list |
| Secrets in payload | High | §10 |
| EvidenceProvenance taxonomy collision | Medium | §9.6 |
| Over-capture extra wire fields treated as first-slice products | Medium | §13.3 |
| Parallel B implementation before this handoff exists | Medium | This document is the A handoff freeze; B impl remains unauthorized |
| Treat this document as S4 implementation license | High | §19 |

No architecture conflict was found with frozen PF-M1 envelope identity,
PF-M2 deferred `market_fact`, PF-M3, approved PF-M4, or frozen C.

---

## 19. Implementation authorization status

### 19.1 Architecture questions (explicitly decided)

| # | Question | Decision |
| --- | --- | --- |
| 1 | First-slice adapter(s) | **Market API Adapter** inside `ProviderGateway`; boundary = read-oriented market-provider ingress; no exclusive commercial vendor frozen |
| 2 | Wire → envelope mapping | PF-M1 rule reused: map without semantic / entity / domain normalization; accept then freeze |
| 3 | Success vs failure / outage | Success = mapped provider body as `market_fact`; failure classes reused from PF-M1; no invented prices/statuses |
| 4 | Payload may / must not contain | Opaque captured market content only; no secrets, Market\* objects, JOO subject ids, research text, or invented facts |
| 5 | `provider_id` / `collected_at` | Gateway-owned; distinct market-binding id; UTC Gateway-boundary collection time; exchange clocks stay in payload |
| 6 | `source_class` | Explicit at construction; success path exactly `market_fact`; never inferred |
| 7 | Korea / US | Required parameter families; not exclusive hard-coded branches; venue/session/timezone/calendar remain opaque payload / config |
| 8 | Health / availability | Per market-adapter binding; PF-M1 health snapshot intent reused; must not fabricate envelopes |
| 9 | Authentication | Operator-supplied credentials; no secrets in payloads; auth failure is a provider failure |
| 10 | Broker-path isolation | Distinct adapter; no retag either direction; KB path not redesigned |
| 11 | Handoff object for B | Immutable PF-M1 envelope with `source_class = market_fact`; Gateway does not append or call store; store must not re-fetch |
| 12 | Deferred | Additional vendors; B; PF-M4 production; BX; research-AI runtime; news; richer quote products |
| 13 | Forbidden | New package; Market\* ownership; FactStore ownership; PF-M4 production; trading; resolution; invented facts |
| 14 | Implementation authorization | **Not authorized** |

### 19.2 This document does NOT authorize

- `ProviderGateway` package scaffold or production code
- FactStore `market_fact` eligibility / retrieval (Prerequisite B)
- PF-M4 `MarketSnapshotProducer` production
- commit / tag / push
- tests, configuration files, credentials vaults, or run artifacts
- any change to committed files
- any change to the three out-of-boundary untracked documents listed in §1

**Implementation authorization status: NOT AUTHORIZED.**

S4 (A implementation), S5/S6 (B), and S8 (PF-M4 production) each require
their own later authorization.

---

## 20. Commit status

This document is created as **exactly one new untracked file**:

`docs/provider/PROVIDER_GATEWAY_MARKET_ADAPTER_PATH_ARCHITECTURE.md`

- Do **not** commit.
- Do **not** stage.
- Do **not** tag.
- Do **not** push.
- Do **not** modify any other path.

Leave this architecture file untracked pending a later, separately authorized
commit review.

---

**PROVIDER GATEWAY MARKET-ADAPTER PATH ARCHITECTURE AUTHORED**
