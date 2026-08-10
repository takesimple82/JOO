# IRO-M1 Architecture

## Status and milestone

- Status: Architecture authored for independent review; first implementation architecture freeze
- Product: Investment Research Orchestrator (IRO)
- Milestone: **IRO-M1**
- Production package (future, not created by this document): `InvestmentResearchOrchestrator`
- Must not use package name: `ResearchOrchestrator` (frozen M22 identity)
- Architecture source of truth (product plane):
  `docs/INVESTMENT_RESEARCH_ORCHESTRATOR_ARCHITECTURE.md`
- Approved product architecture decision:
  **INVESTMENT RESEARCH ORCHESTRATOR ARCHITECTURE APPROVED**
- Approved first implementation candidate boundary decision:
  **IRO-M1 CANDIDATE APPROVED**
  (source: JOO-Automation result
  `iro_m1_candidate_boundary_review`)
- Repository boundary for this document: architecture authoring only; this
  document alone authorizes no production code, test, package scaffold,
  schema module, configuration, run artifact, or Git history mutation

This document freezes the **first implementation architecture** for IRO-M1.
It does **not** redesign the approved Investment Research Orchestrator product
architecture. It does **not** redesign the approved IRO-M1 candidate boundary.
It maps those two approved inputs into a single normative implementation
architecture for one package and one linear M1 lifecycle.

Implementation requires separate authorization after architecture review.
No production package is created by this document.

---

## 1. Package purpose

### 1.1 Purpose

**IRO-M1** is the first implementable slice of the Investment Research
Orchestrator operational plane.

Its purpose is to coordinate a **portfolio-first, sequential research run**
that:

1. compares a current portfolio snapshot to a prior IRO baseline using
   **structural** subject deltas only;
2. plans zero or more research units from those deltas (or an empty plan with
   reasons);
3. routes each unit through a **static** committee allowlist;
4. freezes prompt instance bytes and content hash per planned unit;
5. executes each planned unit **exactly once** via existing M22
   `ResearchOrchestrator` / Stage 1–2 research-execution infrastructure;
6. collects findings from actual committee results without content invention;
7. appends provenance-linked evidence to a run-local store;
8. emits a **minimum memory stub** delta set (presence/absence and exact
   statement identity only).

IRO-M1 maximizes research-process quality for the allowed M1 surface. It does
not maximize trade volume, invent missing committee answers, or produce capital
actions.

### 1.2 Explicit non-identity

IRO-M1 is **not**:

- the full ten-component IRO product lifecycle (Contradiction loop, EV Engine,
  CIO Engine are deferred);
- M22 `ResearchOrchestrator` (thin one-task execution boundary);
- Stage-1 scaffold package `ResearchPlanner/` (different product shape;
  remains untouched);
- Automation M1–M3 / `joo_auto` (development plane);
- capital execution, broker integration, rebalancing, or automatic trading.

### 1.3 Product plane position

IRO-M1 implements a **subset** of the IRO operational plane above frozen
domain contracts and beside the research-execution infrastructure:

```text
Human Authority (out of M1 production enforcement)
        ▲
        │  (deferred: CIO report / human gate records)
Investment Research Orchestrator — IRO-M1 slice
  Scanner → Planner → Static Router → Prompt Freeze
    → M22 Adapter → Collector → Store → Memory Stub
        │
        ├── consume: PortfolioSnapshot, ResearchDomain, ...
        └── invoke once/unit: ResearchOrchestrator (M22) + PipelineRuntime chain
Development Automation (joo_auto) — builds milestones; not a runtime dep
Capital execution — permanently out of IRO
```

---

## 2. Ownership

| Asset / concern | Owner | Consumer |
| --- | --- | --- |
| This architecture document | JOO `docs/iro/` | Architecture freeze only |
| IRO-M1 production code (future) | Package `InvestmentResearchOrchestrator` | Authorized implementation only |
| IRO run state machine / `IRORun` | IRO-M1 package | Run coordinator, components |
| Portfolio holdings / snapshot identity | Portfolio domain packages | Portfolio Scanner (consume) |
| `ResearchDomain.ResearchTask` / Finding / Report validation | `ResearchDomain` | Planner assembly, Collector |
| Thin one-task execution | M22 `ResearchOrchestrator` + `PipelineRuntime` | M22 Adapter (invoke only) |
| Provider invocation | `AIAdapter` / `ExecutionEngine` | Committee runtime (unchanged) |
| Committee aggregate structure | `Committee` contracts | Completeness checklist structure |
| Prompt **template** identity | Prompt Library identity (or caller-supplied template bytes + id/version) | Prompt Freeze |
| Prompt **instance** bytes + hash for a run | IRO-M1 Prompt Freeze + run-local store | Execution adapter, audit |
| Research evidence persistence (ops memory) | IRO-M1 Evidence Store | Memory stub, later IRO milestones |
| Domain Evidence* / Contradiction / EV math | Accepted domain packages | **Not** owned or reimplemented by M1 |
| CIO stance semantics | Deferred (IRO-M4 direction) | Not M1 |
| Allocation / broker / orders | Stage 5 / capital plane | **Never** IRO |
| Git / review / Codex development runs | Automation M1–M3 | Humans / `joo_auto` only |

### 2.1 Ownership rules (normative)

1. IRO-M1 owns **operational run coordination** for the M1 lifecycle only.
2. IRO-M1 **consumes** accepted domain public contracts; it does not redefine
   them.
3. IRO-M1 **invokes** M22 for execution of one planned unit; it does not absorb
   M22 package identity or reimplement the provider/pipeline stack.
4. Responsibilities are not silently transferred from accepted packages into
   IRO “god” logic.
5. Live portfolio mutation is never owned by IRO.

---

## 3. One-package architecture

### 3.1 Decision

**One package with internal components** (candidate boundary option A).

| Option | Verdict |
| --- | --- |
| **A. One package** | **Selected and frozen** |
| B. Several packages with inter-package dependency order | Rejected for M1 — invents package taxonomy beyond approved IRO-M1 boundary |
| C. Implement inside M22 or Stage-1 scaffolds | Rejected — name collision and responsibility transfer |

### 3.2 Package identity

| Name | Role |
| --- | --- |
| `InvestmentResearchOrchestrator` | **Only** allowed IRO-M1 production package name |
| `ResearchOrchestrator` | Frozen M22 package — **unchanged**, not the IRO product |
| `ResearchPlanner/` (Stage-1 scaffold) | Untouched; not the IRO Planner component |
| `ResearchDomain` | Consumed research task/finding/report contracts |

### 3.3 Frozen package structure

```text
InvestmentResearchOrchestrator/
  README.md
  models/                 # run, scan, plan, assignment, prompt freeze,
                          # store records, memory stub, collection markers
  validation/             # type/nonblank/enum validation; no normalization
  scanner.py              # Portfolio Scanner (M1)
  planner.py              # Research Planner (M1)
  committee_manager.py    # Static Committee Router (M1)
  prompt_planner.py       # Prompt Freeze (M1)
  execution_adapter.py    # M22 Adapter
  evidence_collector.py   # Evidence Collector (M1)
  evidence_store.py       # Evidence Store (M1)
  memory_comparison_stub.py
  run_coordinator.py      # sequential M1 path + empty-scan short-circuit
  tests/                  # authorized only with implementation
```

Layout is normative for component boundaries and names. Exact file splitting
inside `models/` / `validation/` may vary at implementation time without
changing ownership or public contract intent.

### 3.4 Non-package rule

IRO-M1 must not create sibling operational packages for Scanner, Planner,
Store, or Memory. Internal modules only.

---

## 4. Internal component boundaries

IRO-M1 freezes **nine operational components** plus a thin sequential
coordinator. Full product components Contradiction Engine, Expected Value
Engine, and CIO Engine are **out of M1**.

| # | Component | Module (normative) | Responsibility (M1 only) | Primary outputs |
| --- | --- | --- | --- | --- |
| 1 | Portfolio Scanner | `scanner.py` | Structural subject deltas vs prior baseline | `ScanDeltaSet` |
| 2 | Research Planner | `planner.py` | Ordered planned units or empty plan + skips | `ResearchPlan` |
| 3 | Static Committee Router | `committee_manager.py` | Allowlisted task_type → committees; completeness structure | `CommitteeAssignmentPlan` |
| 4 | Prompt Freeze | `prompt_planner.py` | Bind template + explicit context; freeze bytes + hash | `PromptFreezeArtifact` |
| 5 | M22 Adapter | `execution_adapter.py` | Assemble validated `ResearchDomain.ResearchTask`; call M22 once per unit | Exact `PipelineExecutionResult` |
| 6 | Evidence Collector | `evidence_collector.py` | Map actual results + explicit bindings; missing/failed markers | `CollectedEvidence` |
| 7 | Evidence Store | `evidence_store.py` | Append-only JSONL/files with provenance | `EvidenceStoreRecord` |
| 8 | Memory Stub | `memory_comparison_stub.py` | Prior presence/absence + exact statement inequality | `MemoryDeltaSet` |
| 9 | Run Coordinator | `run_coordinator.py` | Sequential phase wiring + empty-scan short-circuit | Terminal `IRORun` status |

### 4.1 Cross-cutting run identity

All components share run-scoped identity carried on `IRORun`:

- opaque nonblank `run_id`
- current `portfolio_snapshot_id`
- prior baseline id **or explicit absence**
- phase enum and terminal status
- UTC created/updated timestamps

### 4.2 Component non-overlap (normative)

- Scanner does not plan tasks or call M22.
- Planner does not freeze prompts or execute.
- Static Router does not invent committees outside the injected allowlist.
- Prompt Freeze does not invoke providers.
- M22 Adapter does not collect findings or persist evidence.
- Collector does not rewrite store history or resolve contradictions.
- Store does not mutate portfolio state.
- Memory Stub does not perform semantic delta or contradiction loops.
- Coordinator does not own domain math or provider stacks.

---

## 5. Run contract

### 5.1 Owned object: `IRORun`

| Field | Rule |
| --- | --- |
| `run_id` | Opaque nonblank string; run namespace identity |
| `portfolio_snapshot_id` | Nonblank; identity of current snapshot only |
| `prior_baseline_id` | Nonblank string **or** `None` / explicit absence marker |
| `phase` | M1 phase enum (below) |
| `status` | Derived terminal or in-progress status consistent with phase |
| UTC timestamps | Created and updated timestamps on the run record |

Validation is type/nonblank/enum only. No normalization of ids. Invalid run
contract fails closed before scan.

### 5.2 Phase enum (M1)

Linear happy path plus short-circuit and failure terminals:

```text
INITIALIZED
  → SCANNED
  → PLANNED
  → ROUTED
  → PROMPTS_FROZEN
  → EXECUTED
  → COLLECTED
  → STORED
  → MEMORY_COMPARED
  → COMPLETED

Short-circuit (no material scan delta):
  INITIALIZED → SCANNED → SHORT_CIRCUITED_NO_MATERIAL_DELTA

Failure:
  any phase → FAILED
```

### 5.3 Terminal statuses

| Terminal | Meaning |
| --- | --- |
| `COMPLETED` | Full M1 path finished; memory stub emitted |
| `SHORT_CIRCUITED_NO_MATERIAL_DELTA` | Empty material scan; no committee work |
| `FAILED` | Fail-closed stop; no invented success |

### 5.4 Run ownership and multiplicity

- Exactly one `IRORun` object per invocation identity.
- Run does not rewrite prior evidence store records.
- Phases advance only along the M1 linear path or empty-scan short-circuit.
- Human approvals, CIO stance, and capital actions are not part of the M1 run
  contract.

### 5.5 Run coordinator wiring (M1 only)

1. Validate `IRORun` inputs.
2. Scan → if no material deltas, terminalize
   `SHORT_CIRCUITED_NO_MATERIAL_DELTA`.
3. Plan → route → freeze prompts → execute each planned unit sequentially
   (once each via M22 Adapter).
4. Collect → store appends → memory stub compare.
5. Terminalize `COMPLETED` or `FAILED`.

Contradiction re-research loops, EV assembly, and CIO synthesis are not
coordinated in M1.

---

## 6. Portfolio Scanner

### 6.1 Purpose

Detect **subject-level structural** changes between the current portfolio
observation and the prior IRO baseline. Emit only material-for-M1 deltas.
Unchanged subjects are skipped.

### 6.2 Inputs

- Current accepted portfolio snapshot
  (`ExplicitPortfolioSnapshot` and nested holding/watchlist/membership/
  position/context contracts as required by accepted validators).
- Prior baseline snapshot **or explicit absence**.

### 6.3 M1 delta classes only

| Change class | Meaning |
| --- | --- |
| `MEMBERSHIP_ADDED` | Subject present now, absent in baseline |
| `MEMBERSHIP_REMOVED` | Subject present in baseline, absent now |
| `QUANTITY_CHANGED` | Same subject membership; holding quantity differs by exact `Decimal` inequality |
| `BASELINE_ABSENT_SUBJECT` | No prior baseline; current subject treated as presence under absent baseline |

Materiality basis for M1 is the structural class itself. No EV-relevance
scoring, thesis-coverage intelligence, competitor graphs, or constraint/risk
limit evaluation.

### 6.4 Output: `ScanDeltaSet`

Ordered deltas:

```text
{ subject_id, change_class, materiality_basis }
```

- Zero or more subject deltas.
- Order: **caller subject encounter order** from current snapshot holdings,
  then watchlist (do not invent an alternate product ordering).
- Empty delta set is valid and triggers empty-scan short-circuit.

### 6.5 Absence

- No prior baseline → all current subjects are presence deltas under
  `BASELINE_ABSENT_SUBJECT` (or equivalent explicit baseline-absent class).
- Empty current snapshot with baseline present may yield removals only.
- Empty delta set means “no M1 structural change,” not “research invented
  empty success.”

### 6.6 Failure

Invalid snapshot types or validation failures propagate / fail closed. Scanner
does not invent corrected portfolio content.

### 6.7 Non-responsibilities

- Materiality thresholds beyond structural identity/membership/quantity
- Competitor / supplier / customer / sector expansion
- Thesis-link intelligence
- EV materiality packages
- Task planning or committee routing

---

## 7. Research Planner

### 7.1 Purpose

Convert `ScanDeltaSet` into an ordered set of research units **or** an empty
plan with explicit skip reasons. Suppress free-form “research everything.”

### 7.2 Ownership and name collision

- Owned by IRO-M1 `planner.py` inside `InvestmentResearchOrchestrator`.
- **Must not** implement IRO Planner inside Stage-1 scaffold
  `ResearchPlanner/` (different `ResearchTask` shape; leave package
  untouched).

### 7.3 Output: `ResearchPlan`

| Field | Rule |
| --- | --- |
| `run_id` | Exact run identity |
| Ordered `PlannedUnit[]` | Zero or more |
| `skips` | `{ subject_id, reason }[]` (may be the only content of an empty plan) |

### 7.4 `PlannedUnit` (M1)

| Field | Rule |
| --- | --- |
| `research_id` | Opaque nonblank unit identity under the run |
| `subject_id` | Exact portfolio subject id from the delta |
| `task_type` | Allowlisted static type used by routing table |
| `priority` | Target `P0` \| `P1` \| `P2` for later `ResearchDomain.ResearchTask` |
| title / objective | Nonblank strings from structural templates + subject id only |

### 7.5 Priority mapping (architecture-derived)

| Subject class | Priority |
| --- | --- |
| Holding-class work | `P0` |
| Watchlist-class work | `P1` |

M1 does not emit competitor / supplier / customer / sector expansion classes.
If only one class is present, still use that mapping.

### 7.6 Planning invariants

- Default **1:1** subject delta → planned unit for M1.
- Empty scan → empty plan + reasons; no invented tasks.
- No free-form research-everything mode.
- No dynamic prioritization AI.
- No contradiction re-open (deferred).
- Does not call M22; produces assembly intents for Router + Prompt Freeze +
  Adapter.

### 7.7 Failure

- Corrupt inputs → fail closed.
- Non-allowlisted / unknown change class → **skip with reason** preferred;
  corrupt structure → fail.

### 7.8 Non-responsibilities

- Dynamic AI prioritization
- Queue persistence (`ResearchQueue` scaffold)
- Contradiction-driven re-planning loops
- Provider or committee execution

---

## 8. Static Committee Router

### 8.1 Purpose

Map each planned unit to required committees via a **static allowlist**.
Produce completeness checklist structure. Never simulate missing answers.

### 8.2 Identity and output

- `CommitteeAssignmentPlan` per planned unit:
  - `research_id`
  - `required_committees: list[str]`
  - completeness buckets structure: required / completed / failed / missing
    (align with Committee aggregate semantics; do not invent a parallel
    completeness calculator)

### 8.3 Static routing table

```text
StaticRoutingTable = injected Mapping[task_type, list[committee_id]]
```

- **Caller-supplied or package-constant allowlist** only.
- M1 may ship an empty default map that forces injection.
- Unknown `task_type` not in allowlist → **fail closed** (no invented route).
- Different committees may receive different work **only via the static map**,
  not via adaptive model selection.

### 8.4 Invariants

- No dynamic committee intelligence.
- No majority vote.
- No simulation of missing committee answers.
- Completeness structure is recorded; fail-closed synthesis rules for CIO are
  deferred, but M1 still records missing/failed markers after execution for
  collector/store.

### 8.5 Relationship to M22

Assignments become committee content on the `PipelineExecution` assembled
upstream of M22. Router does not invoke M22 itself.

### 8.6 Non-responsibilities

- Adaptive model/provider selection
- Provider stack ownership
- Completeness-driven CIO synthesis (deferred product component)

---

## 9. Prompt Freeze

### 9.1 Purpose

Materialize **immutable prompt instance bytes** and a content hash for each
planned unit attempt so adaptive context cannot break reproducibility.

### 9.2 Ownership split

| Concern | Owner |
| --- | --- |
| Template identity (`prompt_id` / `prompt_version`) | Prompt Library identity or caller-supplied template |
| Explicit context bindings map | IRO-M1 Prompt Freeze (caller-supplied bindings) |
| Frozen instance bytes + hash | IRO-M1 Prompt Freeze + run-local store |

### 9.3 Output: `PromptFreezeArtifact`

| Field | Rule |
| --- | --- |
| `research_id` | Planned unit identity |
| `committee_id` | Assignment committee |
| `prompt_id` | Template identity |
| `prompt_version` | Template version |
| `frozen_prompt_bytes` | Exact UTF-8 bytes after explicit substitution |
| `prompt_hash` | Content hash of exact bytes (e.g. SHA-256) |
| attempt index | M1: single attempt per planned unit (`0`) |

### 9.4 Freeze rules

1. Start from versioned template identity + template bytes
   (caller-supplied or loaded by **explicit path**).
2. Inject only **explicit named** context bindings (no live model rewriting of
   policy).
3. Materialize immutable bytes and hash **per attempt**.
4. Persist freeze artifacts with the run for audit/replay.

Current Prompt Library registry emptiness is non-blocking: M1 accepts injected
template bytes + id/version.

### 9.5 Failure

- Missing template or required binding → fail closed before execution.
- Hash mismatch on re-read → fail closed.

### 9.6 Relationship to M22

Frozen bytes become `AIRequest.prompt` content for the assembled task. Prompt
Freeze does not call M22 or providers.

### 9.7 Non-responsibilities

- Learning Engine / prompt improvement
- Adaptive selection of templates by model
- Silent policy rewrite by a live LLM

---

## 10. M22 Adapter

### 10.1 Purpose

Bind one planned unit + assignment + frozen prompt into a validated
`ResearchDomain.ResearchTask` and invoke M22
`ResearchOrchestrator.run(task)` **exactly once per planned unit**.

### 10.2 Contract

1. Build validated `ResearchDomain.ResearchTask` with:
   - `research_id`, `title`, `objective`
   - `priority ∈ {P0, P1, P2}`
   - `pipeline: PipelineExecution` carrying committees and requests
2. Call injected `ResearchOrchestrator.run(task)` exactly once.
3. Preserve exact `PipelineExecutionResult` object identity/order.
4. Do not wrap results into synthesized committee answers.
5. Do not invent a parallel provider stack.

### 10.3 Dependency injection

- Injected `ResearchOrchestrator` instance (with its injected
  `PipelineRuntime` chain).
- Adapter does not construct provider registries or rewrite M22 internals.

### 10.4 Identity continuity

```text
AIRequest.task_id := exact ResearchTask.research_id string
```

Same value, different field name; no second invented identity.

### 10.5 Multiplicity and order

- Sequential execution only.
- No parallel fan-out in M1.
- Order of planned units is preserved from `ResearchPlan`.

### 10.6 Failure

- Propagate validation and pipeline exceptions as original objects.
- No M1 retry policy inside the adapter (see §19).
- Do not synthesize success results on failure.

### 10.7 Ownership freeze vs M22

| Concern | M22 | IRO-M1 Adapter |
| --- | --- | --- |
| Role | Thin execution boundary | Lifecycle invoke boundary |
| Input | One validated `ResearchTask` | Planned unit + freeze + assignment |
| Output | One `PipelineExecutionResult` | Exact preserved result |
| Package name | `ResearchOrchestrator` | Must remain distinct product package |

### 10.8 Non-responsibilities

- Provider registration
- CommitteeRuntime / ExecutionEngine / AIAdapter internals
- Evidence collection and store append
- Multi-task retry or contradiction loops

---

## 11. Evidence Collector

### 11.1 Purpose

Collect **structured** outputs from actual committee/execution results without
inventing content. Map into accepted `ResearchFinding` / optional
`ResearchReport` validation contracts. Record missing/failed markers.

### 11.2 Inputs

- Exact `PipelineExecutionResult`
- Assignment and prompt provenance
- Planned unit identity
- Optional `CollectionBinding` for non-defaultable finding fields

### 11.3 Mapping rule (critical freeze)

Populate finding fields **only** from:

1. actual response/committee objects, or
2. **explicit nonblank bindings** supplied on the collection unit.

**Never invent** `category`, dates, verification status, or statement text.

| Field class | Rule |
| --- | --- |
| Defaultable without invention | `statement` ← successful `AIResponse.content`; `committee_id` ← execution committee id; `source` ← provider; `research_id` ← task id; `finding_id` ← opaque new id under run ownership |
| Non-defaultable without binding | `category`, `event_date`, `publication_date`, `verification_status` — require explicit bindings; if any missing → **collection failure marker**, not a fake finding |

### 11.4 Output: `CollectedEvidence`

- Zero or more validated `ResearchFinding` objects
- Optional `ResearchReport` only if accepted status/error rules are satisfied
- Explicit missing/failed markers for incomplete required committees

### 11.5 Invariants

- No free-text → `ExactObservedNumericProposition` semantic production.
- No contradiction resolution.
- No CIO synthesis.
- Partial map fails that unit’s findings; raw provenance may still be recorded
  if execution occurred.

### 11.6 Non-responsibilities

- Semantic numeric extraction
- Domain Evidence package redefinition
- Store rewrite
- Majority-vote truth selection

---

## 12. Evidence Store

### 12.1 Purpose

Provide **append-only** operational research memory for IRO runs with full
provenance for audit and for the Memory Stub.

### 12.2 Medium (M1)

- Run-local **JSONL/files** under an injected root path.
- stdlib filesystem only for M1.
- Exact on-disk byte layout may be fixed in an authorized implementation PR
  under the invariants below.

### 12.3 Provenance minimum (every record)

Every stored research artifact MUST carry at least:

- `run_id`
- `task_id` / `research_id` (when applicable)
- committee identity
- provider identity (when applicable)
- prompt identity and **prompt instance hash**
- source references / collection timestamps
- UTC timestamps for store append events
- payload kind + payload

### 12.4 Invariants

- Append-only: no rewrite of prior records.
- Supersession is **not** implemented in M1 (no delete-in-place).
- Empty store is valid.
- Query by `run_id` and subject/research id must be sufficient for Memory Stub.

### 12.5 Failure

IO failure → fail closed; do not claim stored.

### 12.6 Non-responsibilities

- Live portfolio mutation
- Domain Evidence* package redefinition
- Silent overwrite of prior runs
- Capital execution records
- Full supersession policy wiring (deferred)

---

## 13. Memory Stub

### 13.1 Purpose

Provide the **minimum** prior-evidence awareness required by the product
architecture for M1: presence/absence of prior findings and exact
statement-identity inequality. Full Memory Comparison is deferred.

### 13.2 Compare

Today’s stored findings vs prior-run findings for the same subject/context
key.

### 13.3 Meaningful classes (M1 only)

| Class | Meaning |
| --- | --- |
| `NO_PRIOR` | No prior baseline/findings for the key |
| `UNCHANGED` | Prior present; statement exact-equal |
| `STATEMENT_CHANGED` | Prior present; statement exact string inequality |
| `ADDED` | Finding present now, absent prior |
| `REMOVED` | Finding present prior, absent now |

No semantic delta, no numeric materiality, no supersession intelligence.

### 13.4 Output: `MemoryDeltaSet`

Subject/context key + prior presence + statement equality class set above.
Absence of prior baseline/findings is first-class (not silent equality).

### 13.5 Non-responsibilities

- Full Memory Comparison product behavior
- Contradiction Engine / re-research loop
- `ExactNumericDeltaMateriality`
- EV or CIO inputs beyond stub awareness

---

## 14. Dependency order

### 14.1 Implementation sequence (when authorized)

1. Package scaffold + README (plane, M22 distinction, non-responsibilities)
2. Run contract models + validation (phases, terminals, baseline absence)
3. Evidence Store (append-only JSONL) + provenance schema + tests
4. Memory Comparison stub against store + tests
5. Portfolio Scanner (structural deltas) + empty/unchanged/baseline-absent tests
6. Research Planner (empty plan + ordered intents + skips)
7. Static Committee Router (injected allowlist + completeness structure)
8. Prompt Freeze (materialize + hash + artifact persistence)
9. M22 Adapter (assemble `ResearchDomain.ResearchTask` → inject M22;
   exception propagation tests)
10. Evidence Collector (exact mapping + bindings + missing/failed markers)
11. Run coordinator (sequential path + empty-scan short-circuit)
12. Unit tests required by product architecture §34.1.10: scan skip, empty
    plan, completeness block structure, append-only store, prompt freeze hash
13. **No** domain public contract changes; **No** Automation / `joo_auto`
    changes

### 14.2 Runtime data/control dependency graph

```text
PortfolioSnapshot (+ nested portfolio contracts)
        │
        ▼
   Portfolio Scanner ──► ScanDeltaSet
        │
        ▼
   Research Planner ──► ResearchPlan / PlannedUnits
        │
        ├──────────────► Static Committee Router + StaticRoutingTable
        │                       │
        └──────────────► Prompt Freeze + template/bindings
                                │
                                ▼
                     PipelineExecution + AIRequest.prompt
                                │
                                ▼
                     ResearchDomain.ResearchTask
                                │
                                ▼
              ResearchOrchestrator (M22) ──► PipelineRuntime
                                │                 │
                                │                 ▼
                                │            Committee ──► ExecutionEngine ──► AIAdapter
                                ▼
                     PipelineExecutionResult (exact)
                                │
                                ▼
                     Evidence Collector (+ CollectionBinding)
                                │
                                ▼
                     Evidence Store (append-only)
                                │
                                ▼
                     Memory Stub ──► MemoryDeltaSet

IRORun coordinates phases; does not own domain math or providers.
joo_auto / Automation M1–M3: build plane only — zero runtime dependency.
```

### 14.3 Internal build dependency order (package modules)

```text
models / validation
    → evidence_store
    → memory_comparison_stub
    → scanner
    → planner
    → committee_manager
    → prompt_planner
    → execution_adapter
    → evidence_collector
    → run_coordinator
```

---

## 15. Allowed dependencies

IRO-M1 may depend on (consume / inject) only:

| Dependency | Use |
| --- | --- |
| `ResearchDomain` | Validate/assemble `ResearchTask`, `ResearchFinding`, `ResearchReport` |
| `ResearchOrchestrator` (M22) | Injected one-task execution boundary |
| `PipelineRuntime` | Via M22 injected chain only |
| `Committee` contracts / models | Committee ids and completeness structure alignment |
| `AIAdapter` / `ExecutionEngine` models as required by pipeline assembly | Structural fields only; no new provider stack |
| Portfolio snapshot family (`PortfolioSnapshot` / `ExplicitPortfolioSnapshot` and nested holding/watchlist/membership/position/context packages as accepted) | Scanner inputs |
| Prompt template bytes + `prompt_id` / `prompt_version` | Caller-supplied or explicit path load |
| Python stdlib | Filesystem JSONL store, hashing, UTC timestamps, unittest |
| Injected configuration | `StaticRoutingTable`, collection bindings, store root path |

All domain dependencies are **consume-only**. Public contracts of those
packages are not redesigned for M1.

---

## 16. Forbidden dependencies

IRO-M1 must **not** depend on, import, or wire as runtime requirements:

| Forbidden | Reason |
| --- | --- |
| `joo_auto` / Automation M1–M3 runtime | Different product plane |
| Operational Contradiction Engine loop | Deferred (IRO-M2 direction) |
| `EvidenceContradiction` as M1 operational loop dependency | Domain classifier may exist; M1 does not own ops loop |
| Operational EV Engine / `ExactExpectedValue` end-to-end wiring | Deferred (IRO-M3 direction) |
| CIO Engine / stance enforcement | Deferred (IRO-M4 direction) |
| Stage 5 allocation packages | Separate plane from research posture |
| Broker / order / rebalancing APIs | Capital execution permanently out |
| Semantic free-text → numeric proposition producers | Deferred outside first IRO core |
| Signal / Hypothesis / Thesis **authoring** automation packages as M1 deps | Deferred |
| Stage-1 `ResearchPlanner` / `ResearchQueue` scaffolds as execution task types | Wrong shape; leave untouched |
| Parallel async fan-out frameworks | Sequential only in M1 |
| Live model APIs for prompt policy rewrite | Freeze/hash only |

Forbidden also: any dependency that reimplements ExactExpectedValue math,
evidence comparison domain ownership, or portfolio identity ownership inside
IRO.

---

## 17. Domain invariants

The following invariants are normative for IRO-M1:

1. **Portfolio First (M1 structural form)** — committee work starts only from
   structural scan deltas; empty deltas short-circuit.
2. **Evidence First** — findings come from actual results + explicit bindings;
   never invented.
3. **Committee First structure** — completeness required/completed/failed/
   missing is recorded; missing answers are never simulated.
4. **Validation-first** — accepted domain validators run before use; no
   normalization that changes identity meaning.
5. **Immutable domain instances** — IRO does not mutate frozen domain model
   instances supplied by callers.
6. **Append-only research memory** — Evidence Store never rewrites history.
7. **Prompt freeze** — instance bytes + hash materialize before execution;
   adaptive prompts without freeze/hash are rejected.
8. **Exact M22 result preservation** — no synthesized success wrappers.
9. **Name separation** — package `InvestmentResearchOrchestrator` ≠ M22
   `ResearchOrchestrator`.
10. **Baseline absence is first-class** — no prior baseline is not silent
    equality with empty.
11. **One execution per planned unit** — adapter invokes M22 once per unit;
    sequential order preserved.
12. **Static routing only** — no dynamic committee intelligence in M1.
13. **Quality over volume** — empty plan with reasons is valid.
14. **Run owns orchestration state only** — not live portfolio positions.
15. **Consume-only domain contracts** — no public contract redesign for M1.
16. **Development plane isolation** — no runtime dependency on Automation.

---

## 18. Failure semantics

| Failure class | Behavior |
| --- | --- |
| Invalid `IRORun` contract | Fail closed before scan |
| Invalid portfolio snapshot / wrong types | Propagate / fail closed; no invented portfolio content |
| Empty material scan | Short-circuit terminal
  `SHORT_CIRCUITED_NO_MATERIAL_DELTA`; no committee work |
| Unknown routing `task_type` | Fail closed (no invented route) |
| Missing prompt template / required binding | Fail closed before execution |
| Prompt hash mismatch on re-read | Fail closed |
| `ResearchDomain` / M22 / pipeline validation or execution exception | Propagate original exception semantics; do not synthesize success |
| Missing/failed required committee after execution | Explicit missing/failed markers; no simulated answers |
| Collection missing non-defaultable bindings | Collection failure marker; no fake finding |
| Evidence Store IO failure | Fail closed; do not claim stored |
| Partial mutation of append-only intent | Fail closed; no rewrite of prior lines |

Fail closed is the default. Capital-relevant synthesis under incomplete
committees is deferred with CIO; M1 still refuses to invent completeness.

---

## 19. Retry semantics

IRO-M1 retry policy is intentionally **minimal**:

1. **No adapter-level retry** of M22 / pipeline / provider calls.
2. **No contradiction-driven re-research loop** (deferred to later IRO
   milestone; product architecture bounds such loops only when that component
   exists).
3. **No rewrite of frozen prompts** as a retry strategy.
4. **No invention of missing committees** on retry or re-run.
5. A **new run** (new `run_id`) may be started by the caller after failure;
   prior Evidence Store records remain append-only history and are not
   rewritten.
6. M22 does not own IRO multi-task retry policy; M1 simply does not implement
   multi-task retry beyond sequential single-attempt execution.

Re-runs create new append-only evidence. They never delete or overwrite prior
store records.

---

## 20. Repository boundary

### 20.1 Architecture host

Canonical architecture path for this milestone:

```text
docs/iro/IRO_M1_ARCHITECTURE.md
```

Product-plane architecture remains:

```text
docs/INVESTMENT_RESEARCH_ORCHESTRATOR_ARCHITECTURE.md
```

### 20.2 What this document may do

- Freeze IRO-M1 implementation architecture under `docs/iro/`.
- Cite approved product architecture and approved IRO-M1 candidate boundary.
- Define package purpose, ownership, components, contracts, deps, invariants,
  failure/retry, deferred and rejected responsibilities.

### 20.3 What this document must not do

- Create production package `InvestmentResearchOrchestrator` or any code.
- Create or modify tests.
- Modify existing JOO packages (including M22, ResearchDomain, Portfolio*,
  Stage-1 scaffolds, Automation docs as product code).
- Stage, commit, tag, or push.
- Redesign the approved product architecture or the approved M1 candidate
  boundary.
- Authorize capital execution, Automation redesign, or domain public contract
  changes.

### 20.4 Future implementation repository boundary (when authorized)

When (and only when) implementation is separately authorized:

- May add package `InvestmentResearchOrchestrator/` and its tests/README.
- Must not modify accepted domain public contracts for M1.
- Must not modify Automation / `joo_auto`.
- Must not rename or replace M22 `ResearchOrchestrator`.
- Must not implement deferred or rejected responsibilities listed below.

### 20.5 Planes (normative distinction preserved)

1. Development Automation — `joo_auto` / M1–M3; builds JOO; does not run research.
2. Human Authority — operator; capital-relevant approval (out of M1 enforcement).
3. IRO operational — this milestone’s package (M1 subset).
4. JOO domain-contract — consume only.
5. Research execution infrastructure — M22 + PipelineRuntime + Committee stack.

Capital execution remains permanently outside IRO.

---

## 21. Deferred responsibilities

Intentionally **not** in IRO-M1 implementation:

1. Operational Contradiction Engine + bounded re-research loop
   (IRO-M2 direction).
2. Full Memory Comparison beyond presence/statement-identity stub.
3. Operational Expected Value Engine / ExactExpectedValue end-to-end wiring
   (IRO-M3 direction).
4. CIO Engine, stance enforcement
   (`HOLD|WAIT|MONITOR|AGGRESSIVE ADD|ADJUST`), and human gate records
   (IRO-M4 direction).
5. Semantic free-text → `ExactObservedNumericProposition` production.
6. Signal → Hypothesis → Thesis **authoring** automation.
7. Learning Engine (prompt improvement from outcomes).
8. Dashboard / UI.
9. Scheduling / multi-tenant SaaS runtime.
10. Parallel / async committee fan-out.
11. Portfolio allocation proposal generation and constraint evaluation
    (Stage 5 plane).
12. Risk sizing, order tickets, broker APIs.
13. News scraping implementation.
14. Automatic entity/ticker resolution beyond caller-supplied portfolio
    identities.
15. Final truth selection / contradiction **resolution** (only later
    detection + re-research + human escalation).
16. Supersession policy wiring; deep numeric materiality.
17. PromptLibrary full registry productization beyond identity + freeze.
18. Redesign of Automation M1–M3 or of accepted domain public contracts.
19. Competitor / supplier / customer / sector leader expansion classes in
    Scanner/Planner (beyond holdings and watchlist structural scope).

---

## 22. Explicitly rejected responsibilities

IRO-M1 (and IRO product where listed as permanent) **must never**:

1. Execute trades, route orders, rebalance, or call brokers.
2. Issue BUY/SELL **orders** or treat research postures as executable
   instructions.
3. Simulate, invent, or fill missing committee responses.
4. Collapse multiple domain packages into one orchestrator that reimplements
   EV math, evidence comparison, or portfolio identity.
5. Live inside `joo_auto` or depend on Automation runtime for research
   execution.
6. Mutate Git history or approve its own milestones.
7. Rewrite append-only evidence.
8. Predict prices as a primary objective.
9. Perform risk sizing for execution.
10. Bypass human authority for capital-relevant recommendations (when CIO
    exists later; M1 must not pre-claim that authority).
11. Replace M22 `ResearchOrchestrator` by silently reusing its package name.
12. Implement investment research inside Development Automation.
13. Redesign Automation M1–M3 as part of IRO work.
14. Implement dynamic committee intelligence / adaptive model selection in M1.
15. Implement contradiction-resolution loops or majority-vote truth selection
    in M1.
16. Implement Expected Value calculation as an M1 feature.
17. Implement CIO posture calculation as an M1 feature.
18. Extend Stage-1 `ResearchPlanner.ResearchTask` as the M22 task type
    (wrong shape; conflicts with `ResearchDomain.ResearchTask`).
19. Invent semantic content outside accepted JOO contracts.
20. Perform free-form “research everything” planning.

---

## 23. Frozen candidate contracts (implementation schemas)

Normative field rules for authorized implementation (schemas as code are not
created by this document):

| Contract | Required fields / rules |
| --- | --- |
| `IRORun` | `run_id: str`; `portfolio_snapshot_id: str`; `prior_baseline_id: str \| None`; `phase`; `status`; UTC timestamps |
| `ScanDelta` / `ScanDeltaSet` | ordered deltas; `subject_id`; `change_class ∈ {MEMBERSHIP_ADDED, MEMBERSHIP_REMOVED, QUANTITY_CHANGED, BASELINE_ABSENT_SUBJECT}`; `materiality_basis` = structural class only |
| `ResearchPlan` | `run_id`; ordered `PlannedUnit[]`; `skips: {subject_id, reason}[]` |
| `PlannedUnit` | `research_id`; `subject_id`; `task_type`; `priority` target `P0\|P1\|P2`; title/objective nonblank from structural templates + subject id |
| `CommitteeAssignmentPlan` | `research_id`; `required_committees: list[str]`; completeness buckets structure |
| `StaticRoutingTable` | injected `Mapping[task_type, list[committee_id]]`; unknown key fails |
| `PromptFreezeArtifact` | `research_id`; `committee_id`; `prompt_id`; `prompt_version`; `frozen_prompt_bytes`; `prompt_hash`; attempt index (M1: `0`) |
| `ExecutableResearchTask` | exact `ResearchDomain.ResearchTask` after validation |
| `ExecutionRecord` | `research_id`; exact preserved `PipelineExecutionResult` reference or serialized exact field projection for store |
| `CollectionBinding` | explicit values for any `ResearchFinding` field not present on `AIResponse` |
| `CollectedEvidence` | findings list and/or failure markers; optional `ResearchReport` only if rules satisfied |
| `EvidenceStoreRecord` | provenance set §12.3 + payload kind + payload |
| `MemoryDelta` / `MemoryDeltaSet` | subject key; prior presence; statement equality class |

**Enums not in M1 production enforcement:** CIO stance
(`HOLD|WAIT|MONITOR|AGGRESSIVE ADD|ADJUST`), re-research budget, full
contradiction case model, EV assessment bundle.

---

## 24. Compatibility with existing JOO contracts

- IRO-M1 **consumes** accepted domain public contracts; it does not redesign
  them.
- M22 `ResearchOrchestrator`, `PipelineRuntime`, Committee, AIAdapter,
  ExecutionEngine, ResearchDomain, Portfolio snapshot family retain accepted
  meanings.
- Recommendation endpoint identity and Stage 5 allocation structure remain
  separate planes (not M1 outputs).
- No JOO domain package import of `joo_auto` for research execution.
- No silent transfer of responsibilities from accepted packages into IRO.
- Stage-1 `ResearchPlanner` / `ResearchQueue` scaffolds remain untouched and
  are not the IRO Planner.

---

## 25. Test expectations (implementation authorization only)

When implementation is authorized, unit tests MUST cover at least product
architecture §34.1.10:

1. Scan skip for unchanged subjects
2. Empty plan with reasons
3. Completeness block structure (required/completed/failed/missing recording)
4. Append-only Evidence Store behavior
5. Prompt freeze hash stability / mismatch fail-closed

This architecture document does **not** create those tests.

---

## 26. Document authority

- This document is the **canonical IRO-M1 implementation architecture**.
- It freezes architecture derived only from:
  1. Approved Investment Research Orchestrator Architecture
     (`docs/INVESTMENT_RESEARCH_ORCHESTRATOR_ARCHITECTURE.md`);
  2. Approved IRO-M1 Candidate Boundary
     (`IRO-M1 CANDIDATE APPROVED`).
- It does not redesign either approved input.
- It does not authorize production implementation, commit, tag, or push.
- Subsequent IRO-M1 implementation work must cite this document and must not
  expand beyond its frozen boundary without a new architecture amendment.

---

## 27. Final architecture freeze statement

IRO-M1 is frozen as a **single new package**
`InvestmentResearchOrchestrator` implementing only:

- explicit run contract;
- structural Portfolio Scanner;
- Research Planner with empty-plan legality;
- Static Committee Router;
- Prompt Freeze (bytes + hash);
- M22 Adapter (once per planned unit);
- Evidence Collector without invention;
- append-only Evidence Store;
- Memory Stub (presence/statement identity);
- sequential run coordinator with empty-scan short-circuit.

All EV, CIO, contradiction loops, capital execution, Automation changes, and
domain-contract redesign remain excluded.

**No residual blocking gap remains against freezing this IRO-M1 architecture
as the implementation target**, subject to separate implementation
authorization.
