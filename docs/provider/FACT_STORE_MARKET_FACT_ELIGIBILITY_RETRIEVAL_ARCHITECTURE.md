# FactStore market_fact Eligibility and Retrieval Architecture

## Status and milestone

- Status: Architecture authored for independent review; additive FactStore
  `market_fact` eligibility and retrieval freeze
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Provider & Fact** (Layer 3 — Fact Store)
- Milestone: **PF-M4 Prerequisite B / sequencing step S5**
- Owner package identity (frozen PF-M2; not created by this document):
  `FactStore`
- Additive capability: **`market_fact` append eligibility + retrieval**
  (PF-M2 deferred this class until market ingress **and** a later architecture
  freeze; this document is that later freeze)
- This document is **not** a new product-package milestone and **not** a
  redesign of PF-M1, PF-M2, PF-M3, PF-M4, Prerequisite A, or Market\*
- Repository boundary: architecture authoring only; this document alone
  authorizes no production code, test, package scaffold, schema module,
  configuration, run artifact, or Git history mutation

This document freezes **only** the additive FactStore `market_fact`
eligibility and retrieval capability required so later PF-M4 may consume
stored market facts by read-only retrieval.

It does **not** redesign frozen PF-M2 store / eligibility identity.

It does **not** rewrite the PF-M2 `broker_fact` first-slice meaning.

It does **not** create a new package.

It does **not** own ProviderGateway ingress, adapters, envelopes, or health.

It does **not** own Market\* models, validators, or structural invariants.

It does **not** authorize PF-M4 `MarketSnapshotProducer` production.

Implementation requires a separate authorization after architecture review.
The `FactStore` production package is currently absent. That absence does
not authorize a new package name.

---

## Normative first-slice surface (must remain explicit)

### This freeze implements ONLY

| # | Responsibility |
| --- | --- |
| 1 | **Append eligibility** for structurally valid Gateway envelopes with `source_class = market_fact` |
| 2 | **Preservation** of `source_class`, source identity, `collected_at`, and payload |
| 3 | **Store-owned `appended_at`** as distinct from `collected_at` |
| 4 | **Fact identity** for stored `market_fact` records |
| 5 | **Append-only immutability** and **explicit supersession linkage** using the same history model as frozen PF-M2 broker facts |
| 6 | **Retrieval** by `fact_id`, source identity, `source_class = market_fact`, `collected_at` window, and supersession navigation |
| 7 | **Structural integrity verification** for `market_fact` records |
| 8 | **Hard reject** of `research_ai` and non-envelope inventions |
| 9 | The later **PF-M4 read-only retrieval surface**, without composing snapshots |

### This freeze does NOT implement

| Concern | Owner (elsewhere) |
| --- | --- |
| **Provider Gateway** ingress / adapters / envelopes / health | Prerequisite A / frozen PF-M1 identity — already frozen at v7.4 |
| **Market\*** models / validators / structural invariants | Prerequisite C — already frozen at v7.2; consume-only sequencing fact |
| **Market Snapshot** composition | PF-M4 `MarketSnapshotProducer` |
| **Market Watch** Engine | PF-M5 |
| **`broker_fact` first-slice meaning** | Frozen PF-M2 — reused, not rewritten |
| **`execution_fact`** | BX-M1 direction |
| **Research AI** transport runtime | Stage 1/2 + later explicit freeze |
| **News / alternative data** | Architecture amendment required first |
| **Ticker / entity resolution** | Outside permanently |
| **Freshness / staleness policy** | Snapshot / watch / execution / Reporting |
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
| HEAD | `a3a1b61324062f24b02c5db53b2287c963432f93` | `a3a1b61324062f24b02c5db53b2287c963432f93` | Match |
| Exact tag at HEAD | `v7.4-stage5-provider-gateway-market-adapter-path-implementation` | Exact match (`git describe --exact-match --tags HEAD`) | Match |
| Prerequisite C tag | `v7.2-stage5-market-first-slice-domain-implementation` | Present; resolves to `8d193b2150606a0e72320f10e8b7ec24fdce9d47` | Match |
| Tracked tree | Clean | Clean (`git status --short` shows only expected untracked docs) | Match |
| Unexpected dirty tracked files | None | None | Match |
| Unexpected in-boundary untracked production files | None | None | Match |

**Preserved out-of-boundary untracked files (read-only; not modified, not
staged):**

- `docs/JOO_PRODUCT_ARCHITECTURE.md`
- `docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md`
- `docs/provider/PF_M4_MARKET_SNAPSHOT_ARCHITECTURE.md`

**Production package state at this freeze:**

| Package | Repository state at this freeze |
| --- | --- |
| `FactStore` | **Absent** — identity remains frozen PF-M2 name; this freeze must not create it |
| `ProviderGateway` | **Present and frozen** at HEAD tag `v7.4-stage5-provider-gateway-market-adapter-path-implementation` (Prerequisite A implementation / S4). Consume the frozen handoff only. Do not modify. |
| `MarketSnapshotProducer` | **Absent** — PF-M4 production remains blocked |
| Market\* domain packages | **Present and frozen** at tag `v7.2-stage5-market-first-slice-domain-implementation` (Prerequisite C). This freeze consumes their existence as a sequencing fact only and must not import or depend on them for append success. |
| Rejected names (`MarketFactStore`, `MarketAdapter`, `MarketGateway`, `QuoteIngress`) | **Absent** |

Checkpoint status: **Pass**. Not REVIEW BLOCKED.

---

## 2. Authority reviewed

Authority order is highest first. This freeze obeys and does not rewrite
higher authorities.

| Priority | Authority | Review result for this freeze |
| --- | --- | --- |
| 1 | `JOO_CONSTITUTION.md` | Explicit caller-supplied opaque identity; no automatic ID generation; validation-first; immutability; single-owner responsibilities; operational layers must be separately approved and bounded |
| 2 | Frozen / committed architecture documents | PF-M2 store / eligibility / history identity reused; PF-M1 envelope / source-class reused via A handoff; PF-M3 untouched; Market\* C structure consume-only; IRO / Automation untouched |
| 2 | `docs/JOO_PRODUCT_ARCHITECTURE.md` (present untracked; READ ONLY) | Layer 3 persists broker and market facts with provider identity, collection time, and provenance; dual-store vs Evidence Store; research AI never primary truth; append-only or explicit supersession; Fact Store does not compose snapshots |
| 2 | `docs/provider/PF_M1_PROVIDER_GATEWAY_ARCHITECTURE.md` | Frozen envelope field model and source-class taxonomy reused through the A handoff; Gateway produces, store persists; no dual write |
| 2 | `docs/provider/PF_M2_FACT_STORE_ARCHITECTURE.md` | Canonical FactStore identity. `market_fact` append deferred until market ingress **and** a later freeze. This document is that later freeze. Broker-fact first-slice meaning, dual-store rule, and package identity are not rewritten |
| 2 | `docs/provider/PF_M3_PORTFOLIO_SNAPSHOT_ARCHITECTURE.md` | Untouched; Portfolio Snapshot is not a market-fact owner |
| 2 | `docs/provider/PF_M4_MARKET_SNAPSHOT_ARCHITECTURE.md` (**APPROVED**; present untracked; READ ONLY) | Prerequisite B owned by `FactStore`; producer is composition-only; Fact Store is the sole later fact upstream; no Gateway bypass; this freeze supplies the read-only retrieval surface, not composition |
| 2 | `docs/provider/PROVIDER_GATEWAY_MARKET_ADAPTER_PATH_ARCHITECTURE.md` (frozen at v7.3; Prerequisite A handoff) | **Consume only.** Sole success-path handoff object is the frozen PF-M1 immutable envelope with `source_class = market_fact`. Do not reopen A |
| 2 | `docs/market/MARKET_FIRST_SLICE_DOMAIN_ARCHITECTURE.md` (frozen at v7.1) | C structure consume-only; Market\* must not own FactStore; venue/session/timezone/calendar are domain identities later, not store types now |
| 2 | Frozen IRO product / IRO-M1 / IRO-M2 | Untouched; Evidence Store remains IRO; research lifecycle remains IRO; no provider-fact persistence transferred into IRO |
| 2 | Frozen Automation M1–M3 | Untouched; development plane only; not a runtime dependency. M2 is committed under `docs/automation/`. M3 is present untracked and was read only. M1 is the accepted review-only `joo_auto` predecessor cited by M2/M3 and product/IRO/PF freezes; no M1 file exists under `docs/automation/` |
| 3 | Approved independent review results | See tokens below |
| 4 | Exact repository HEAD / tags | §1 |
| 5 | Existing milestone sequencing decisions | Locked **C → A → B → (A ∩ B ∩ C unlock) → PF-M4 production** |

**Required review tokens consumed:**

| Review | Token |
| --- | --- |
| `~/JOO-Automation/results/pf_m4_prerequisite_sequencing_review/latest.md` | **PF-M4 PREREQUISITE SEQUENCE APPROVED** |
| `~/JOO-Automation/results/pf_m4_market_snapshot_architecture_review/latest.md` | **PF-M4 ARCHITECTURE APPROVED** |
| `~/JOO-Automation/results/market_first_slice_domain_structure_architecture_review_v2/latest.md` | **MARKET FIRST-SLICE DOMAIN ARCHITECTURE APPROVED** |
| `~/JOO-Automation/results/market_first_slice_domain_structure_implementation_review/latest.md` | **MARKET FIRST-SLICE DOMAIN IMPLEMENTATION APPROVED** |
| `~/JOO-Automation/results/provider_gateway_market_adapter_path_architecture_review/latest.md` | **PROVIDER GATEWAY MARKET-ADAPTER PATH ARCHITECTURE APPROVED** |
| `~/JOO-Automation/results/provider_gateway_market_adapter_path_implementation_review/latest.md` | **PROVIDER GATEWAY MARKET-ADAPTER PATH IMPLEMENTATION APPROVED** |

**Locked sequencing consumed:**

```text
C → A → B → (A ∩ B ∩ C unlock) → PF-M4 production
```

- C may run with A.
- B implementation must not precede A handoff freeze.
- A handoff freeze is complete. A implementation is frozen at v7.4.
- C implementation is frozen at v7.2.
- This gate authors **B architecture only**.

If any statement in this document appears to conflict with a higher authority
in that authority’s scope, the higher authority wins and this document is
defective — not a silent override.

**Conflict-rule check (pre-authoring):** this freeze does not redesign the
frozen PF-M2 store / eligibility identity, create a new package, own Market\*
structure, own ProviderGateway, or start PF-M4 production. **No ARCHITECTURE
CONFLICT.**

---

## 3. Sequencing position (S5 / Prerequisite B only)

### 3.1 Locked sequence

```text
C → A → B → (A ∩ B ∩ C unlock) → PF-M4 production
```

| Step | Work | This document |
| --- | --- | --- |
| **S1 / S2** | Prerequisite **C** architecture + implementation | **Already frozen** at HEAD tag `v7.2-stage5-market-first-slice-domain-implementation`. Do not reopen C. |
| **S3 / S4** | Prerequisite **A** architecture + implementation | **Already frozen.** Architecture at v7.3; implementation at HEAD tag `v7.4-stage5-provider-gateway-market-adapter-path-implementation`. Do not reopen A. |
| **S5** | Prerequisite **B** architecture freeze | **This document** |
| **S6** | Prerequisite **B** implementation | **Not authorized** |
| **S7 / S8** | A ∩ B ∩ C unlock → PF-M4 production | **Not authorized** |

### 3.2 Parallelization retained from the sequencing board

| Pair | Allowed? | Status at this freeze |
| --- | --- | --- |
| C ∥ A | **Yes** | Both already accepted / frozen |
| C ∥ B architecture | **Yes** | C is already accepted; B architecture may proceed |
| B implementation before A handoff freeze | **No** | Satisfied: A handoff and A implementation are already frozen |
| B ∥ PF-M4 production | **No** | PF-M4 production remains blocked |
| Any prerequisite work inside `MarketSnapshotProducer` | **Forbidden** | Ownership collapse |

### 3.3 What “later freeze” means (non-redesign)

PF-M2 first-slice statement **“`market_fact` append is deferred until market
ingress and a later freeze”** is the **deferred first-slice scope** of the
broker-fact milestone. It is not a permanent ban on the package-lifetime
class, and it is not a license to invent a second store.

This S5 freeze is that **later architecture freeze**. It is not:

- a rewrite of PF-M2;
- a rewrite of the `broker_fact` first-slice meaning;
- FactStore package scaffold;
- PF-M4 production;
- Prerequisite A work.

PF-M4 unbundles the product-row language “Market API + Market Snapshot”:

- ingress remains `ProviderGateway` (A; already frozen);
- persistence / eligibility / retrieval remain `FactStore` (this freeze);
- composition alone is `MarketSnapshotProducer` (still blocked).

### 3.4 Scope of S5

This freeze owns **B architecture only**:

- `market_fact` append eligibility;
- stored-record field reuse;
- `fact_id` supply rule;
- `collected_at` preservation and `appended_at` assignment;
- explicit supersession for `market_fact` using the PF-M2 history model;
- retrieval required by later PF-M4;
- structural integrity bounds;
- failure / outage non-invention;
- hard rejects;
- upstream / downstream and forbidden edges.

This freeze does **not** own C (already frozen), A (already frozen), S6, or
PF-M4 production.

---

## 4. Package ownership and additive-vs-new-package ruling

### 4.1 Ruling

| Option | Verdict |
| --- | --- |
| **Additive capability of frozen `FactStore`** | **Selected and frozen** |
| New package (`MarketFactStore`, dual physical store for market vs broker as a separate product package, `MarketAdapter`, `MarketGateway`, `QuoteIngress`, `MarketSnapshotProducer`) | **Rejected** — invents a second store plane or relocates composition |
| Relocate `market_fact` persistence into `ProviderGateway` | **Rejected** — dual write; PF-M1 / A forbid Gateway append |
| Relocate `market_fact` persistence into `MarketSnapshotProducer` | **Rejected** — PF-M4 R3 / R9 / R10 |
| Relocate `market_fact` persistence into Market\* domain packages | **Rejected** — C is structure-only and already frozen |
| Make `market_fact` the only permanently eligible class because `broker_fact` code is absent | **Rejected** — absence is not a drop-class license |
| Rename `FactStore` because the production package is absent | **Rejected** — absence is not a rename license |

**Owner package identity:** `FactStore` only.

**Additive capability name:** `market_fact` append eligibility + retrieval.

**Not created by this document:** the `FactStore` package, any sibling ops
package, any Market\* file, any ProviderGateway file, any
`MarketSnapshotProducer` file.

### 4.2 Ownership table

| Concern | Owner |
| --- | --- |
| This architecture document | JOO `docs/provider/` |
| Fact Store production code (future) | Package `FactStore` |
| `market_fact` append eligibility | `FactStore` (additive; this freeze) |
| `broker_fact` append eligibility | `FactStore` (frozen PF-M2 first slice; **unchanged**) |
| Fact identity validation at store boundary | `FactStore` |
| Source identity / source class / `collected_at` preservation | `FactStore` (fields originate from Gateway envelopes) |
| Store-owned `appended_at` | `FactStore` |
| Explicit supersession linkage | `FactStore` (same history model as PF-M2) |
| Retrieval API, including `source_class = market_fact` | `FactStore` |
| Structural integrity verification | `FactStore` |
| Provider ingress / envelope construction / health | `ProviderGateway` (PF-M1 + frozen A) — **not** FactStore |
| Market\* models / validators / invariants | Prerequisite C — **not** this freeze |
| Market Snapshot composition | PF-M4 — **not** this freeze |
| Evidence Store / research evidence | IRO — **not** this package |
| Market Watch, trading, Human Approval | **Not this package** |

### 4.3 Universal platform store (retained)

FactStore remains a **universal platform store**. Eligibility expands **by
class**, not by inventing a second store plane.

Korea-capable and US-capable market facts are the **same class**
(`market_fact`). Eligibility is by frozen `source_class`, not by venue,
exchange, timezone, or calendar. Do not invent per-exchange store packages.

### 4.4 Absence rule

`FactStore` production code is currently absent. S5 architecture may
proceed. S6 implementation remains separately authorized. Absence of the
package is **not** authority to invent `MarketFactStore`, to drop
`broker_fact` from the store model, or to make `market_fact` the only
eligible class permanently.

If S6 is the first `FactStore` implementation in the repository, it must
still implement the frozen PF-M2 store model — including `broker_fact`
eligibility — and add this class expansion. That later implementation
authorization is **not** granted here.

### 4.5 Non-package rule

This freeze must not create sibling operational packages for
“MarketFactStore,” “MarketHistory,” “QuoteStore,” “MarketAdapter,”
“MarketGateway,” “QuoteIngress,” or “MarketSnapshotProducer.” Internal
modules of `FactStore` only, when a later implementation authorization
creates that package.

This document does **not** create those files and is **not** a scaffold.

---

## 5. Relationship to frozen PF-M2 broker_fact first slice

### 5.1 What remains frozen

PF-M2 remains the canonical Fact Store identity. This freeze reuses and does
not rewrite:

- one-package identity `FactStore`;
- immutable append-only storage; no in-place rewrite;
- explicit supersession / succession linkage; no inference from payload
  similarity, timestamps, or AI;
- stored-record field intent: `fact_id`, `envelope_id`, `provider_id` /
  source identity, `source_class`, `collected_at`, `appended_at`, status /
  content disposition, `payload`, optional `integrity_seal`;
- `collected_at` preserved from Gateway; `appended_at` is store-owned and
  must not replace `collected_at`;
- dual-store rule: FactStore ≠ Evidence Store;
- `research_ai` never primary-fact append;
- no provider re-fetch; no second Gateway; no fact invention on outage;
- structural integrity only; not economic / semantic / EV truth;
- retrieval-oriented public contract; no snapshot composition;
- universal platform store: eligibility expands by class, not by a second
  store plane;
- EvidenceProvenance `source_class` taxonomy (`primary | secondary |
  unknown`) as a **different plane** that must not be reused here.

### 5.2 How to read PF-M2’s deferred market sentence

PF-M2 first-slice statements:

- **“`market_fact` append is deferred until market ingress and a later
  freeze”**;
- **“For PF-M2 first implementation, eligible class = `broker_fact` only.”**

are the **deferred first-slice scope** of the broker-fact milestone. They
are not a permanent ban on package-lifetime `market_fact` eligibility.

This additive freeze **is that later freeze**. It does not:

- rewrite the `broker_fact` first-slice meaning;
- drop `broker_fact` from the store model;
- change PF-M2 package identity;
- reopen PF-M2 dual-store, history, integrity, or retrieval identity;
- make `market_fact` the only eligible class permanently.

### 5.3 Class table after this freeze (additive, not a PF-M2 rewrite)

| Class | PF-M2 first-slice meaning (unchanged) | This additive freeze |
| --- | --- | --- |
| `broker_fact` | **Only eligible primary-fact class** of PF-M2 first slice | **Unchanged — remains eligible** |
| `market_fact` | Deferred until market ingress and a later freeze | **Architecture authorized here; implementation not authorized** |
| `execution_fact` | Deferred (BX-M1 direction) | Still deferred |
| `research_ai` | **Never** | **Never** |

PF-M2 first implementation remains `broker_fact` only **as a PF-M2
first-slice statement**. This document adds package-lifetime eligibility for
`market_fact`. Both statements stand. The second does not erase the first.

### 5.4 Absence of broker_fact implementation

Absence of a `broker_fact` implementation in the repository is **not** a
license to:

- drop `broker_fact` from the store model;
- invent `MarketFactStore`;
- treat `market_fact` as the only eligible class permanently;
- redesign PF-M2 eligibility identity around market facts alone.

Later S6 / FactStore implementation must keep `broker_fact` eligibility as
frozen PF-M2 first-slice behavior and add `market_fact` beside it.

---

## 6. Consumed A handoff contract

This section **consumes** frozen
`docs/provider/PROVIDER_GATEWAY_MARKET_ADAPTER_PATH_ARCHITECTURE.md` §14. It
does **not** redesign Prerequisite A.

### 6.1 Sole success-path handoff object

The sole success-path handoff object is the **frozen PF-M1 immutable
provider payload envelope** with `source_class = market_fact`.

B does **not** receive Market\* objects from Gateway.

B does **not** receive PF-M4 snapshots from Gateway.

### 6.2 Success-path constraints this freeze relies on

When Gateway emits a success-path market fact envelope, this freeze relies
on A’s guarantees:

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

### 6.3 Failure / outage constraints this freeze honors

1. Failure / outage envelopes or signals **must not** be treated as invented
   prices or invented market statuses.
2. A failure / outage output alone is **not** a license to append a synthetic
   last price or “closed/open” status as primary market truth.
3. Health snapshots are observability / fail-closed inputs, **not** facts.

This freeze does not weaken those constraints.

### 6.4 Ownership edges of the consumed handoff (normative)

| Actor | Must | Must not |
| --- | --- | --- |
| **Gateway (frozen A)** | Construct and emit envelopes / failure signals | Append to FactStore; call FactStore; persist store history; compose Market Snapshot |
| **FactStore (this freeze)** | Consume handed-off envelopes under this eligibility freeze | Re-fetch market APIs; become a second Gateway; repair `source_class`; invent facts from outage signals |
| **MarketSnapshotProducer (later PF-M4)** | Read stored facts from FactStore after A ∩ B ∩ C | Call Gateway as a fact upstream; call market HTTP |

### 6.5 Direction

```text
Market API Adapter (frozen A / v7.4)
        │
        ▼
Immutable envelope (source_class = market_fact)
        │
        │  handoff only — Gateway does not append or call store
        ▼
FactStore market_fact eligibility / retrieval (this freeze)
        │
        │  later PF-M4 read-only retrieval; composition not authored here
        ▼
[PF-M4 MarketSnapshotProducer — composition only; still blocked]
```

FactStore does **not** require PF-M4 to exist at runtime to **append**
eligible envelopes. FactStore must **not** implement Market Snapshot
composition to complete this freeze.

### 6.6 What A deliberately left to this freeze

A §14.6 left the following to Prerequisite B. This document freezes them:

- append eligibility tables beyond A’s handoff constraints;
- `fact_id` assignment;
- `appended_at`;
- supersession linkage;
- retrieval API;
- class-expansion implementation remains **not authorized** (S6).

Storage engine choice remains an implementation-freeze residual and is not
owned here.

---

## 7. market_fact append eligibility gate

### 7.1 Purpose

The append eligibility gate is the hard boundary that protects primary-fact
truth class while expanding eligible classes from PF-M2’s deferred
`market_fact` slot to this additive freeze.

This is the same gate family as PF-M2 §9. It is **not** a second eligibility
plane.

### 7.2 Normative gate for `market_fact` primary-fact append

An input may append as a **primary `market_fact`** only if **all** hold:

1. It is a **Provider Gateway immutable payload envelope** (the frozen PF-M1
   envelope consumed from A) — not free-form research text, committee output,
   CIO report, human opinion, Market\* structure, or a PF-M4 snapshot.
2. `source_class` is **exactly** `market_fact`.
3. `status` is **success**.
4. Required identity and provenance fields are structurally present and
   valid: `envelope_id`, `provider_id` / source identity, `source_class`,
   `collected_at`.
5. A caller/handoff-supplied opaque nonblank `fact_id` is present on the
   append request (§8.3).
6. `payload` is the opaque captured market content from the envelope, not
   Market\* structure, not secrets, and not synthesized by FactStore from
   outage signals.
7. Source class is accepted as declared. FactStore **must not repair**
   class.

`broker_fact` remains eligible under frozen PF-M2 first-slice rules. This
gate does not revoke that eligibility.

### 7.3 Exact accept / reject table

| Input | Append as primary fact? |
| --- | --- |
| Structurally valid success envelope with `source_class = broker_fact` | **Yes** — frozen PF-M2 first-slice eligibility, **unchanged** |
| Structurally valid success envelope with `source_class = market_fact` meeting §7.2 | **Yes** — this additive freeze |
| `market_fact` failure / outage envelope or signal | **Never** (no invention) |
| Gateway health snapshot alone | **Never** |
| `research_ai` envelope / research artifact | **Never** |
| Committee / Evidence / Memory / Contradiction / EV / CIO outputs | **Never** |
| Domain Market\* objects without a Gateway envelope | **Never** |
| PF-M4 Market Snapshot / producer output | **Never** |
| Portfolio\* / other domain objects invented without a Gateway envelope | **Never** |
| `execution_fact` | **No** — deferred (BX-M1) |
| News / alternative-data / non-frozen class | **Never** without architecture amendment |
| Object whose class was silently rewritten (`research_ai` → `market_fact`, `broker_fact` → `market_fact`, or any class repair) | **Never** |
| Non-envelope invention (free dict, wire body, HTTP result, fixture price) | **Never** |
| Same already-accepted `fact_id` presented again | **Never** (in-place rewrite) |
| Same already-accepted `envelope_id` presented as a second primary-fact append | **Never** (one envelope → at most one stored fact) |

### 7.4 Multi-venue / class rule (normative)

1. Eligibility is by frozen `source_class`, **not** by venue or exchange.
2. Korea-capable and US-capable market facts are the same class
   (`market_fact`).
3. Venue, session, timezone, and calendar values inside payload remain
   **opaque payload content**. They are not FactStore-owned Market\* types
   and are not eligibility keys.
4. Append success **must not** import or depend on `MarketEndpoint`,
   `MarketVenue`, `MarketInstrument`, `MarketSessionContext`,
   `MarketFactProvenanceReference`, `MarketInstrumentObservation`, or
   `MarketSnapshot`.

### 7.5 Hard rejects (normative)

| Reject class | Rule |
| --- | --- |
| **`research_ai`** | Never primary-fact append, under any alternate field name |
| **Non-envelope inventions** | Never. The only success-path append object is the frozen PF-M1 envelope |
| **Class repair** | Never rewrite `source_class`. Never promote `research_ai` → `market_fact`. Never retag `broker_fact` ↔ `market_fact` |
| **Failure / outage invention** | Never append synthetic prices or market statuses from failure / health signals |
| **Market\* / snapshot objects** | Never treat C structures or PF-M4 emissions as store append inputs |

Mis-tagged research content as `market_fact` is an architecture defect at
Gateway. FactStore rejects what it can detect structurally (wrong class,
failure status, missing required fields) and **must not** “repair” class.

### 7.6 research_ai ban (product hard rule, retained)

**Research AI is never the primary truth.** Research AI outputs enter
research execution / Evidence paths only. They must not append to FactStore
as primary portfolio or market facts.

---

## 8. Stored fact record reuse for market_fact

### 8.1 No new identity model

The durable unit remains the **PF-M2 stored fact record**. This freeze does
not invent a market-only record type, a second identity scheme, or a
payload-derived key.

### 8.2 Reused fields (exact intent from PF-M2 §5.2)

| Field | Rule on the `market_fact` path |
| --- | --- |
| `fact_id` | Opaque nonblank string; identity of this stored fact record; caller/handoff-supplied (§8.3) |
| `envelope_id` | Opaque nonblank string preserved from the Gateway envelope |
| `provider_id` / source identity | Nonblank; preserved from the envelope; not inferred from payload |
| `source_class` | Exactly one frozen class; this path’s success-path value = **`market_fact`** |
| `collected_at` | UTC collection timestamp **preserved from** the Gateway envelope |
| `appended_at` | UTC time of durable append acceptance at the FactStore boundary (store-owned; **not** a replacement for `collected_at`) |
| `status` / content disposition | Success-path fact content only for primary facts; store does not promote failure envelopes into synthetic success facts |
| `payload` | Immutable body as handed off from the eligible envelope; opaque captured market content |
| Optional `integrity_seal` | Structural seal/hash over stored bytes/fields if used by integrity verification |

Exact Python type names and enums are fixed at implementation freeze. Field
**intent** is frozen here and is the same intent PF-M2 already froze.

### 8.3 How `fact_id` is supplied

Constitution identity rules apply.

1. `fact_id` is an **explicit caller/handoff-supplied opaque identity**.
2. FactStore **must not** generate, derive, hash, or infer `fact_id` from
   payload, `envelope_id`, timestamps, venue strings, symbols, or AI.
3. `fact_id` must not encode semantics, timestamps, versions, endpoints, or
   state.
4. Gateway does **not** assign `fact_id`. A left `fact_id` to this freeze.
5. The authorized append caller supplies `fact_id` together with the eligible
   envelope.
6. `envelope_id` and `fact_id` are **different identities**. `envelope_id`
   identifies the ingress capture. `fact_id` identifies the stored fact
   record.
7. Identity validation does not establish a global uniqueness product or
   endpoint existence. Re-presentation of an already-accepted `fact_id` is
   rejected as an in-place rewrite attempt (§7.3, §9).

### 8.4 Append-request intent (architecture-level)

A `market_fact` append request requires:

| Input class | Intent |
| --- | --- |
| Eligible envelope | Frozen PF-M1 immutable success envelope with `source_class = market_fact` |
| `fact_id` | Caller/handoff-supplied opaque nonblank identity |
| Optional explicit supersession declaration | Directed link to a prior stored `fact_id`, if the caller declares succession |

Exact request object field names are fixed at implementation freeze. Input
**intent** is frozen here.

### 8.5 Immutability invariants (reused)

1. Accepted stored fact records are immutable after append acceptance.
2. Payload body after acceptance is not rewritten.
3. Source class is not reclassified after append.
4. `collected_at` is not adjusted to “improve freshness.”
5. `appended_at` is not later rewritten.
6. Deletion of prior history is out of this freeze; any future
   retention/compaction must not mutate retained records’ meaning and
   requires a separate freeze if it changes public contract.

### 8.6 Payload opacity at the store boundary

Store `payload` remains **opaque captured market content**.

FactStore must **not**:

- interpret venue / session / timezone / calendar / symbol strings as
  Market\* identities;
- construct or validate Market\* objects to accept an append;
- treat extra wire fields (OHLC, bid, ask, volume, FX, flow-like bytes) as
  first-slice store products;
- strip, normalize, or semantically repair payload to manufacture
  eligibility.

Capturing opaque extra wire fields is not ownership of those later products.

---

## 9. Append-only history and explicit supersession

### 9.1 Same history model as frozen PF-M2 broker facts

This freeze reuses PF-M2 §8. It does not invent a market-only versioning
scheme.

```text
Eligible Gateway envelope + caller-supplied fact_id
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
2. “Update,” “correct,” or “replace” means **append a new fact record**,
   never mutate a prior accepted record in place.
3. There is no silent last-write-wins destruction of prior versions.
4. Correction of market content requires a **new Gateway envelope** (new
   `envelope_id`, new `collected_at`) and a **new `fact_id`**, optionally
   linked by explicit supersession.

### 9.2 Version history meaning (reused)

**Version history** means:

- the ordered (or link-navigable) set of immutable stored fact records that
  share an explicit succession/supersession relationship or a caller-defined
  retrieval key family;
- **not** an in-place mutable version field that overwrites prior content;
- **not** automatic inference that two payloads “mean the same instrument /
  venue / session” via entity resolution, ticker matching, or AI.

### 9.3 Explicit supersession linkage for `market_fact`

When an authorized append path declares that fact B supersedes fact A:

| Property | Rule |
| --- | --- |
| Direction | Explicit directed link from superseded `fact_id` → superseding `fact_id` |
| Storage | Link is itself an immutable recorded relation (or immutable fields on the new record pointing to the prior `fact_id`) |
| Validation | Structural only: nonblank ids, no direct self-supersession, referenced id present or reject |
| Class bound | A `market_fact` may only explicitly supersede another stored `market_fact`. Cross-class supersession (`market_fact` ↔ `broker_fact`) is rejected. This is class-eligibility enforcement, not a new history model |
| Non-inference | Store does **not** infer supersession from timestamps, payload similarity, venue/session/symbol strings, or AI |
| Non-deletion | Supersession does **not** delete or rewrite the superseded record |
| Non-truth | Supersession is not economic truth, materiality, freshness policy, or research resolution |

FactStore supersession remains a **provider-fact history** mechanism. It is
not IRO `EvidenceSupersession` package ownership and does not import
research proposition semantics.

### 9.4 Forbidden history behaviors (retained and applied)

- In-place rewrite of payload or provenance fields.
- Silent deletion of superseded facts in this freeze.
- Compaction that rewrites meaning of retained records without architecture
  amendment.
- Using supersession as contradiction resolution or majority-vote truth.
- Inferring succession because two payloads “look like the same quote.”
- Using `appended_at` or `collected_at` order as implicit supersession.

---

## 10. Collection vs append timestamps

### 10.1 Rules (normative)

1. `collected_at` is the Gateway-boundary collection time of the fact. It is
   **preserved exactly** as supplied on the eligible handoff object, subject
   only to structural type/presence validation.
2. FactStore **must not** invent, shift, backdate, skew-correct, or “heal”
   `collected_at`.
3. Exchange transaction times, quote times, or session clocks that appear in
   payload remain **opaque payload content**. They do not replace
   `collected_at`.
4. FactStore assigns `appended_at` as the UTC time of durable append
   acceptance at the store boundary.
5. `appended_at` is **store-owned**. It is not copied from Gateway and is
   not taken from payload clocks.
6. `appended_at` **must not** be substituted for `collected_at` in retrieval
   semantics that claim collection freshness.
7. Freshness / staleness **policy decisions** (when facts are “too old” for
   snapshot emission, watch, or execution) remain **downstream** (PF-M4 /
   PF-M5 / execution / Reporting). FactStore exposes timestamps; it does not
   own policy.

### 10.2 Non-responsibilities

- Clock skew correction that invents a different collection time.
- Backdating to manufacture continuity.
- Using research timestamps as market collection times.
- Using `appended_at` as a silent last-known-good freshness repair.
- Owning PF-M4 fail-closed freshness thresholds.

---

## 11. Retrieval API for market_fact / history

### 11.1 Purpose

Provide **read-only retrieval** of stored `market_fact` records and history
for authorized downstream consumers without granting them write, semantic,
or composition ownership.

This is the later PF-M4 read-only retrieval surface. It is **not** snapshot
composition.

### 11.2 Required retrieval capabilities

| Capability | Intent |
| --- | --- |
| Get by `fact_id` | Exact record fetch |
| List/filter by source identity | Provider-scoped history |
| List/filter by `source_class = market_fact` | Class-scoped market history |
| List/filter by `collected_at` window | Time-scoped history using **collection** time, not `appended_at` as a substitute |
| Navigate supersession / succession | Prior/next explicit links only |
| Integrity check entry points | Structural verification on stored records |

Exact method names, pagination, and storage backend are implementation
freeze details. Public contract must remain retrieval-oriented and
validation-first.

`broker_fact` retrieval remains a frozen PF-M2 capability. This freeze adds
class-scoped `market_fact` retrieval beside it. It does not remove
`broker_fact` retrieval.

### 11.3 Retrieval non-responsibilities

Retrieval API must **not**:

- compose Market Snapshot or Portfolio Snapshot objects as domain products;
- import or return Market\* types as a condition of retrieval success;
- apply materiality, freshness policy thresholds, or EV calculations;
- resolve entities, tickers, or aliases to JOO subjects;
- call external providers or Gateway to “fill gaps”;
- rewrite history on read;
- silently serve a superseded record as if it replaced prior history
  without exposing the explicit link;
- expose secrets that must never have been stored (credentials);
- substitute `appended_at` windows for `collected_at` windows.

### 11.4 Consumer posture

Consumers treat retrieved facts as **immutable historical records**.

Later PF-M4 selects and composes. FactStore does not mean “the current
market object,” “the live quote,” or “the accepted Market Snapshot.”

---

## 12. Structural integrity verification

### 12.1 Purpose

Integrity verification protects **storage structural honesty**: that
`market_fact` records are complete, consistent with append rules, and
optionally sealed against silent bit-level corruption.

This reuses PF-M2 remediation R5. It is **not** a new integrity product.

### 12.2 In scope (structural only)

| Check class | Examples |
| --- | --- |
| Identity completeness | Required ids nonblank exact strings (`fact_id`, `envelope_id`, source identity) |
| Required field presence | `source_class = market_fact` on this path; `collected_at`; `appended_at`; payload presence rules for success-path facts |
| Append consistency | No in-place mutation detected; one envelope → at most one stored fact; supersession link endpoints valid structurally; no cross-class link |
| Optional integrity seal | Hash/seal verify over stored bytes/fields if implemented |
| Eligibility re-check on read (optional) | Reject serving records that violate frozen class rules if corrupted/miswritten |

### 12.3 Explicitly out of scope (not “integrity”)

Integrity verification must **not** mean:

- economic correctness of prices or statuses;
- Market\* structural validity of opaque payload content;
- materiality of change;
- investment suitability;
- semantic validity of free text;
- entity / ticker resolution success;
- Expected Value or CIO posture correctness;
- research contradiction resolution;
- “this fact is true about the market”;
- freshness / staleness policy.

Using “integrity” as a cover name for calculation, Market\* validation,
research, or AI inference is an architecture defect.

### 12.4 Failure posture

| Condition | Posture |
| --- | --- |
| Structural validation failure on append | Reject append; do not store partial garbage as success |
| Integrity seal mismatch on read | Fail closed for that record; do not silently “repair” payload |
| Missing supersession endpoint (if required by the declared link) | Reject the link; do not invent endpoints |
| Class / eligibility corruption detected on read | Fail closed for that record; do not repair `source_class` |

---

## 13. Failure / outage non-invention

### 13.1 Normative rule

When Gateway emits only health / failure / outage signals **without** an
accepted eligible success envelope:

- FactStore **must not invent** substitute market facts;
- FactStore **must not** append last prices, quotes, market statuses,
  calendars, or sessions synthesized from those signals;
- absence of new facts is **not** success content.

This restates PF-M2 §5.4 and honors A §14.3. It is not weakened for the
market path.

### 13.2 What may and must not be stored

| Input | Store as primary `market_fact`? |
| --- | --- |
| A §14.2 success envelope | **Yes**, if §7.2 holds |
| Failure / outage envelope or signal | **No** |
| Health snapshot | **No** |
| Missing collection / empty provider body elevated to success | **No** |

Optional durable recording of **non-fact operational signals** remains
deferred until an explicit later contract. It is **not** required by this
freeze and must not be smuggled in as primary-fact append.

### 13.3 Downstream consequence (not owned here)

Downstream snapshot / watch / execution planes are expected to treat
missing or failed ingress as **staleness / fail-closed inputs**. This freeze
preserves absence. It does not implement those policies inside FactStore.

---

## 14. Upstream / downstream edges and forbidden edges

### 14.1 Upstream of this freeze

**In scope**

| Upstream | Role | Rule |
| --- | --- | --- |
| **Provider Gateway market-adapter path (frozen A)** | Sole first-slice ingress of durable primary `market_fact`s | Consumes **immutable provider payload envelopes** with `source_class = market_fact` |
| Authorized append caller | Supplies opaque `fact_id` and optional explicit supersession declaration | Must not require FactStore to invent identity |

**Package-lifetime upstream retained from PF-M2 (not redesigned)**

| Upstream | When |
| --- | --- |
| Gateway `broker_fact` envelopes | Frozen PF-M2 first slice — remains eligible |
| Broker Execution execution facts | BX-M1 direction (later) |
| Additional market adapters via Gateway | Later gateway milestones — still **via Gateway**, not direct re-fetch |

**Never upstream for primary fact**

- `research_ai` outputs
- Committee / AIAdapter research payloads as primary truth
- Evidence Store records
- Operational Memory deltas
- Contradiction / EV / CIO outputs
- Human free-text opinions or approvals
- Development Automation manifests
- Market\* objects
- PF-M4 snapshots
- Direct external market-provider HTTP from inside FactStore
- Gateway failure / outage / health signals as invented prices or statuses

### 14.2 No provider re-fetch rule (normative)

1. FactStore **must not** authenticate to market APIs or any external
   provider to obtain or “heal” facts.
2. FactStore **must not** embed a second Provider Gateway.
3. FactStore **must not** call `ProviderGateway` to collect live quotes.
4. Missing data remains missing; consumers observe absence/staleness.
5. Health / outage signals from Gateway inform fail-closed consumers; they
   do not authorize synthetic fact append.

### 14.3 Downstream of this freeze

**In scope**

| Downstream | Role | Rule |
| --- | --- | --- |
| **Later PF-M4 Market Snapshot production** | First JOO operational consumer of stored `market_fact`s | **Retrieval only**; FactStore does not compose snapshots |
| **Audit / replay** | History consumers | Read-only |
| **Reporting** (later) | Observability of fact state / freshness inputs | Read-only; Reporting is not system of record |

**Not FactStore downstream ownership**

The following may **consume** facts only through later explicit contracts or
via snapshots; FactStore **must not implement** them:

- Market Snapshot composition logic
- Portfolio Snapshot composition logic
- Market Watch materiality engine
- IRO lifecycle
- Evidence Store
- Operational Memory
- Contradiction Engine
- Expected Value Engine
- CIO Engine
- Human Approval
- Trading / Broker Execution command path

### 14.4 Forbidden edges (normative)

| Forbidden edge | Reason |
| --- | --- |
| `FactStore` → external market re-fetch | No second Gateway (PF-M2 R6 / A §14.4) |
| `FactStore` → `ProviderGateway` collect/call | Dual-plane collapse; A emits only |
| `FactStore` → invent facts on outage | PF-M1 / PF-M2 / A non-invention |
| `research_ai` → FactStore primary-fact append | Product hard rule |
| Silent class repair into `market_fact` | Hard reject |
| Evidence Store → overwrite FactStore positions | Dual-store (PF-M2 R4) |
| FactStore → Evidence Store ownership | Dual-store |
| FactStore → Market Snapshot composition | PF-M4 |
| FactStore → Portfolio Snapshot composition | PF-M3 |
| FactStore → Market Watch ownership | PF-M5 |
| FactStore → Market\* import / construct for append success | C is structure-only; store must not own it |
| FactStore → IRO run coordination | Plane separation |
| FactStore → CIO / EV / Contradiction | Not store |
| FactStore → Human Approval | Capital authority elsewhere |
| FactStore → Broker Execution trading | Capital plane |
| FactStore → semantic normalization / entity resolution / AI inference | Forbidden permanently |
| FactStore → `joo_auto` runtime dependency | Automation is development-only |
| `ProviderGateway` → FactStore ownership / append implementation | Store is PF-M2 / this freeze; A already forbids Gateway append |
| `MarketSnapshotProducer` → Gateway as fact upstream | PF-M4 R9 |
| In-place history mutation disguised as “versioning” | PF-M2 R2 |
| Per-exchange store package / `MarketFactStore` | Universal store; class expansion only |

### 14.5 Consistency with frozen planes

| Plane | Result |
| --- | --- |
| Constitution | Single owner; caller-supplied opaque identity; no hidden inference |
| Product Architecture Layer 3 | Broker and market facts persist in one Fact Store |
| PF-M1 | Untouched; produces envelopes; does not persist |
| Prerequisite A | Consumed handoff only; not reopened |
| PF-M2 | Additive class expansion; broker-fact first slice untouched |
| PF-M3 | Untouched |
| PF-M4 | Prerequisite B architecture only; production still blocked |
| Market\* / C | Consume-only as a sequencing fact; no type dependency |
| IRO / IRO-M1 / IRO-M2 | Untouched |
| Automation M1–M3 | Untouched — development-only |

---

## 15. Relationship to later PF-M4 read-only retrieval

### 15.1 What this freeze supplies to PF-M4

Approved PF-M4 requires Prerequisite B:

> Fact Store accepts eligible `market_fact` envelopes for append-only
> persistence and exposes retrieval of stored market facts and history.

This freeze is that architecture. After a later S6 implementation, PF-M4 may
use **only**:

```text
FactStore retrieval ──► MarketSnapshotProducer
```

PF-M4 fact selection intent already names `fact_id`, source identity, and
`collected_at` window. This freeze makes those capabilities, plus
`source_class = market_fact` filter and supersession navigation, the
normative store surface.

### 15.2 What this freeze does not supply

- Composition of accepted Market\* snapshots
- Explicit caller-supplied subject bindings
- Session-profile selection
- Freshness / presence fail-closed **policy**
- Provenance **reference objects** as Market\* types
  (`ExplicitMarketFactProvenanceReference` remains C / PF-M4 consumption)
- Gateway bypass or live quote fill-in

PF-M4 attaches provenance references **after** retrieval. FactStore stores
and returns fact identity / source identity / `collected_at`. It does not
own Market\* provenance structure.

### 15.3 Unlock remains closed

A and C are already frozen. This document is B **architecture** only.

PF-M4 production implementation remains blocked until **all** of:

1. C accepted — already true;
2. A implemented — already true;
3. B **implemented** under a later S6 authorization — **not true**;
4. separate PF-M4 implementation authorization after A ∩ B ∩ C.

This document does **not** unlock S8.

---

## 16. Deferred responsibilities

| Deferred responsibility | Until |
| --- | --- |
| `FactStore` package scaffold and production code | Separate **B implementation** authorization (S6) |
| PF-M4 `MarketSnapshotProducer` production | A ∩ B ∩ C unlock **and** separate PF-M4 implementation authorization |
| `execution_fact` append | **BX-M1** (+ Human Approval path) |
| Additional source classes (news / alternative data) | Architecture amendment required first (Gateway + store) |
| Multi-provider physical topology / tenancy packaging | Later PF / ops freezes |
| Optional durable recording of non-fact health/outage signals | Explicit later contract if ever needed |
| Exact schema-as-code, retention TTL, non-mutating compaction | Implementation freeze / residual open work |
| Freshness policy thresholds | Snapshot / watch / execution / Reporting |
| OHLC / bid / ask / volume / turnover as products | Later domain + ops freezes — not store products |
| FX conversion, sector state, futures, options, flows | Later domain + ops milestones |
| Ticker / entity / alias resolution | Permanently outside FactStore |
| Market Watch materiality | **PF-M5** |
| Portfolio Snapshot / valuation / PnL / NAV | PF-M3 / separate valuation architecture |
| Research AI transport classification runtime | Explicit later freeze; Stage 1/2 retain invocation |

C implementation and A implementation are **not deferred** — they are
already frozen. This document must not reopen them.

---

## 17. Forbidden responsibilities

FactStore `market_fact` eligibility / retrieval **must not**:

1. Create a new package (`MarketFactStore`, dual market/broker product
   store, `MarketAdapter`, `MarketGateway`, `QuoteIngress`,
   `MarketSnapshotProducer`).
2. Rewrite PF-M1, PF-M2, PF-M3, PF-M4, A, or Market\* architecture
   documents.
3. Rewrite the PF-M2 `broker_fact` first-slice meaning or drop `broker_fact`
   from the store model.
4. Own ProviderGateway ingress, adapters, envelopes, or health.
5. Modify `ProviderGateway`.
6. Own or import Market\* models, validators, or structural invariants for
   append success.
7. Modify Market\* packages.
8. Compose Market Snapshot or Portfolio Snapshot.
9. Start PF-M4 production, Market Watch, valuation, or IRO.
10. Re-fetch market APIs or embed a second Gateway.
11. Repair `source_class` or silently promote `research_ai` → `market_fact`.
12. Infer class, identity, or supersession from payload, timestamps, or AI.
13. Generate `fact_id` automatically or encode semantics in identity.
14. Replace `collected_at` with `appended_at`.
15. Invent last prices, quotes, market statuses, calendars, or sessions on
    failure / outage.
16. Treat research AI as market truth.
17. Ingest news / alternative data without architecture amendment.
18. Resolve tickers, entities, or aliases into JOO subject ids.
19. Own freshness / staleness policy thresholds.
20. Productize OHLC, bid, ask, volume, turnover, FX, sector, futures,
    options, or flow surfaces.
21. Hard-code KRX-only, NYSE/Nasdaq-only, or per-exchange store packages.
22. Place, cancel, or otherwise execute broker orders.
23. Absorb Automation M1–M3 as a runtime dependency.
24. Provide a demo bypass from producer or domain packages to HTTP /
    Gateway.
25. Reuse EvidenceProvenance `primary | secondary | unknown` as
    provider-fact class.
26. Use “integrity verification” as a cover for semantic or investment
    correctness checks.
27. Authorize implementation, commit, tag, or push by the existence of this
    document.

---

## 18. Risks

| Risk | Severity | Mitigation in this freeze |
| --- | --- | --- |
| Invent `MarketFactStore` because `FactStore` is absent | High | §4 absence rule; additive-only ruling |
| Drop `broker_fact` because broker implementation is absent | High | §5.3–§5.4; eligibility table keeps PF-M2 first slice |
| Rewrite PF-M2 “broker_fact only” as if this document replaced PF-M2 | High | §5.2 reads it as deferred first-slice scope |
| Author PF-M4 composition or reopen A / C | High | §3 S5-only; §6 consume-only; §15 retrieval-only |
| Import Market\* types into append success | High | §7.4 / §8.6 / §17 |
| Infer supersession from payload similarity or timestamps | High | §9.3 non-inference |
| Auto-generate `fact_id` from envelope or payload | High | §8.3 Constitution identity |
| Substitute `appended_at` for `collected_at` | High | §10 |
| Invent prices/statuses on outage | High | §13 |
| `research_ai` or class repair into primary facts | High | §7.5–§7.6 |
| FactStore re-fetches market APIs / second Gateway | High | §14.2 |
| Producer / demo HTTP bypass around the store | High | §14.4; forbidden #24 |
| Per-exchange store packages / Korea vs US class split | High | §4.3 / §7.4 |
| EvidenceProvenance taxonomy collision | Medium | §5.1 |
| “Integrity” becomes semantic / Market\* / EV engine | Medium | §12.3 |
| Freshness policy pulled into the store | Medium | §10.1 / §11.3 |
| Treat this document as S6 implementation license | High | §19 |
| Treat B architecture as PF-M4 unlock | High | §15.3 |

No architecture conflict was found with frozen PF-M2 store identity,
frozen A handoff, frozen C structure, approved PF-M4, or the locked
prerequisite sequence.

---

## 19. Implementation authorization status

### 19.1 Architecture questions (explicitly decided)

| # | Question | Decision |
| --- | --- | --- |
| 1 | Exact `market_fact` append eligibility table | §7.3 — accept structurally valid success envelopes with `source_class = market_fact`; keep `broker_fact`; reject research, failure/outage, non-envelopes, class repair, Market\*, snapshots, `execution_fact` |
| 2 | Additive class expansion vs PF-M2 first slice | §5 — this is the later freeze PF-M2 required; `broker_fact` first-slice meaning is not rewritten |
| 3 | Stored-record fields | §8.2 — reuse PF-M2 field intent exactly; no new identity model |
| 4 | `fact_id` supply | §8.3 — caller/handoff-supplied opaque identity; no semantic auto-generation |
| 5 | `collected_at` / `appended_at` | §10 — preserve Gateway `collected_at`; assign store-owned `appended_at`; never substitute |
| 6 | Supersession | §9 — same PF-M2 explicit-link model; no payload-similarity inference; no cross-class links |
| 7 | Retrieval for later PF-M4 | §11 / §15 — `fact_id`, source identity, `source_class = market_fact`, `collected_at` window, supersession navigation; no composition |
| 8 | Structural integrity bounds | §12 — structural/identity/append-consistency/optional seal only |
| 9 | Failure / outage non-invention | §13 — honor A §14.3; no invented prices or statuses |
| 10 | Hard rejects | §7.5 — `research_ai`, non-envelope inventions, class repair |
| 11 | Upstream / downstream / forbidden edges | §14 |
| 12 | Deferred | §16 — S6, PF-M4 production, `execution_fact`, additional classes, topology, health-signal persistence |
| 13 | Forbidden | §17 |
| 14 | Implementation authorization | **Not authorized** |

### 19.2 This document does NOT authorize

- `FactStore` package scaffold or production code
- B implementation (S6)
- PF-M4 `MarketSnapshotProducer` production
- `ProviderGateway` modification
- Market\* modification
- commit / tag / push
- tests, configuration files, storage engines, or run artifacts
- any change to committed files
- any change to the three out-of-boundary untracked documents listed in §1

**Implementation authorization status: NOT AUTHORIZED.**

S6 (B implementation) and S8 (PF-M4 production) each require their own
later authorization.

---

## 20. Commit status

This document is created as **exactly one new untracked file**:

`docs/provider/FACT_STORE_MARKET_FACT_ELIGIBILITY_RETRIEVAL_ARCHITECTURE.md`

- Do **not** commit.
- Do **not** stage.
- Do **not** tag.
- Do **not** push.
- Do **not** modify any other path.

Leave this architecture file untracked pending a later, separately authorized
commit review.

---

**FACT STORE MARKET FACT ELIGIBILITY RETRIEVAL ARCHITECTURE AUTHORED**
