# IRO-M2 Architecture

## Status and milestone

- Status: Architecture authored for independent review; second implementation
  architecture freeze
- Product: Investment Research Orchestrator (IRO)
- Milestone: **IRO-M2**
- Production package (existing, frozen by IRO-M1): `InvestmentResearchOrchestrator`
- Must not use package name: `ResearchOrchestrator` (frozen M22 identity)
- Architecture source of truth (product plane):
  `docs/INVESTMENT_RESEARCH_ORCHESTRATOR_ARCHITECTURE.md`
- Architecture source of truth (prior milestone, frozen):
  `docs/iro/IRO_M1_ARCHITECTURE.md`
- Approved product architecture decision:
  **INVESTMENT RESEARCH ORCHESTRATOR ARCHITECTURE APPROVED**
- Approved prior milestone:
  **IRO-M1** architecture + implementation (tag
  `v6.6-stage5-iro-m1-implementation`)
- Product-plane illustrative milestone mapping (source §31):
  **IRO-M2 — Memory + Contradiction loop (beyond M1 stub)**
- Repository boundary for this document: architecture authoring only; this
  document alone authorizes no production code, test, package scaffold,
  schema module, configuration, run artifact, or Git history mutation

This document freezes the **second implementation architecture** for IRO-M2.

It does **not** redesign the approved Investment Research Orchestrator product
architecture.

It does **not** redesign frozen IRO-M1 architecture or implementation.

It maps the product-plane Memory Comparison, Operational Contradiction
Engine, and bounded re-research loop into a single normative implementation
architecture that **extends** the existing one-package M1 surface.

Implementation requires separate authorization after architecture review.
No production code is created by this document.

---

## 1. Package purpose

### 1.1 Purpose

**IRO-M2** is the second implementable slice of the Investment Research
Orchestrator operational plane.

Its purpose is to extend the frozen IRO-M1 sequential research run with three
and only three new operational responsibilities:

1. **Operational Memory Comparison** — diff today’s stored research evidence
   against prior stored evidence for the same subject/context and surface only
   **meaningful** operational deltas (beyond the M1 presence/statement-identity
   stub);
2. **Operational Contradiction Engine** — detect conflicting evidence using
   accepted domain classifiers where applicable, emit contradiction cases and
   an explicit unresolved set, and request re-research when confidence is
   insufficient — without majority-vote truth selection;
3. **Bounded Re-research Loop** — when the Contradiction Engine requests
   re-research, return to the Research Planner with a **finite** per-run depth
   budget; when budget is exhausted, escalate an explicit human-review marker
   rather than looping unboundedly.

IRO-M2 maximizes research-process quality on the allowed M2 surface. It does
not maximize trade volume, invent missing committee answers, resolve truth by
vote, assemble Expected Value, produce CIO capital postures as a decision
engine, or emit capital actions.

### 1.2 Explicit non-identity

IRO-M2 is **not**:

- a redesign of IRO-M1 (Scanner, Planner M1 path, Static Router, Prompt Freeze,
  M22 Adapter, Collector, Evidence Store, Memory Stub contract as history);
- the full ten-component IRO product lifecycle (EV Engine and CIO Engine remain
  deferred);
- M22 `ResearchOrchestrator` (thin one-task execution boundary);
- Stage-1 scaffold package `ResearchPlanner/` (different product shape;
  remains untouched);
- Automation M1–M3 / `joo_auto` (development plane);
- capital execution, broker integration, rebalancing, or automatic trading;
- domain package `EvidenceContradiction` ownership (consume-only classifier);
- Expected Value Engine or CIO Engine.

### 1.3 Product plane position

IRO-M2 implements a **superset of the M1 operational slice** and a **subset**
of the full IRO operational plane:

```text
Human Authority (out of M2 production enforcement; escalation markers only)
        ▲
        │  (deferred: CIO report / human gate records as M4 surface)
Investment Research Orchestrator — IRO-M2 slice
  [IRO-M1 path frozen]
  Scanner → Planner → Static Router → Prompt Freeze
    → M22 Adapter → Collector → Store
    → Operational Memory Comparison
    → Operational Contradiction Engine
    → Bounded Re-research Loop ──► Planner (budgeted)
        │
        ├── consume: PortfolioSnapshot, ResearchDomain, Evidence* classifiers
        └── invoke once/unit/attempt: ResearchOrchestrator (M22) + PipelineRuntime
Development Automation (joo_auto) — builds milestones; not a runtime dep
Capital execution — permanently out of IRO
```

### 1.4 Relationship to IRO-M1 (non-redesign rule)

| Concern | Rule |
| --- | --- |
| M1 package identity | Preserved: `InvestmentResearchOrchestrator` |
| M1 components | Remain; not redesigned |
| M1 linear path | Preserved when no re-research is required |
| M1 empty-scan short-circuit | Preserved |
| M1 Memory Stub | Remains the historical M1 surface; M2 **adds** Operational Memory Comparison as the M2 runtime comparison component |
| M1 one-execution-per-planned-unit | Preserved **per attempt**; re-research creates new planned units/attempts, not silent retries of the same frozen attempt |
| M1 append-only store | Preserved and required by M2 loops |
| M1 public contracts | Not silently rewritten; M2 adds contracts and may extend enums/modules |

IRO-M2 may **extend** models, phases, modules, and the run coordinator. It may
**not** collapse, rename, or re-own frozen M1 responsibilities into EV/CIO or
capital planes.

---

## 2. Ownership

| Asset / concern | Owner | Consumer |
| --- | --- | --- |
| This architecture document | JOO `docs/iro/` | Architecture freeze only |
| IRO-M2 production code (future) | Package `InvestmentResearchOrchestrator` | Authorized implementation only |
| IRO run state machine / `IRORun` (M2-extended) | IRO package | Run coordinator, components |
| Operational Memory Comparison | IRO-M2 module(s) in package | Planner awareness, Contradiction Engine, later EV/CIO |
| Operational Contradiction Engine | IRO-M2 module(s) in package | Re-research loop, unresolved set, audit |
| Bounded re-research budget and loop control | IRO-M2 run coordinator + budget contract | Planner re-entry |
| Portfolio holdings / snapshot identity | Portfolio domain packages | Portfolio Scanner (unchanged M1 consume) |
| `ResearchDomain.ResearchTask` / Finding / Report validation | `ResearchDomain` | Planner assembly, Collector |
| Thin one-task execution | M22 `ResearchOrchestrator` + `PipelineRuntime` | M22 Adapter (invoke only; once per unit per attempt) |
| Provider invocation | `AIAdapter` / `ExecutionEngine` | Committee runtime (unchanged) |
| Committee aggregate structure | `Committee` contracts | Completeness checklist structure |
| Prompt **template** identity | Prompt Library identity (or caller-supplied template bytes + id/version) | Prompt Freeze |
| Prompt **instance** bytes + hash for a run/attempt | Prompt Freeze + run-local store | Execution adapter, audit |
| Research evidence persistence (ops memory) | Evidence Store (M1, reused) | Memory Comparison, Contradiction, re-research audit |
| Pairwise numeric contradiction **candidate** classification | `EvidenceContradiction` (+ `EvidenceComparison`) | Operational Contradiction Engine (**consume only**) |
| Exact numeric comparison identity | `EvidenceComparison` | Domain classifier path only |
| Exact observed numeric propositions | `EvidenceProposition` / accepted producers | Contradiction domain path when present |
| Domain Evidence* / EV math / CIO stance semantics | Accepted domain packages / later IRO milestones | **Not** reimplemented by M2 |
| CIO stance production as decision engine | Deferred (IRO-M4 direction) | Not M2 |
| Allocation / broker / orders | Stage 5 / capital plane | **Never** IRO |
| Git / review / Codex development runs | Automation M1–M3 | Humans / `joo_auto` only |

### 2.1 Ownership rules (normative)

1. IRO-M2 owns **operational run coordination extensions** for Memory
   Comparison, Contradiction Engine, and the bounded re-research loop only.
2. IRO-M2 **consumes** accepted domain public contracts; it does not redefine
   them.
3. IRO-M2 **invokes** M22 for execution of each planned unit attempt; it does
   not absorb M22 package identity or reimplement the provider/pipeline stack.
4. Responsibilities are not silently transferred from accepted packages into
   IRO “god” logic.
5. Live portfolio mutation is never owned by IRO.
6. Domain `EvidenceContradiction` remains a frozen **classifier**; operational
   loop policy (when to re-research, budgets, unresolved sets) is owned by
   IRO-M2.
7. IRO-M1 ownership rules remain in force for all frozen M1 components.

---

## 3. One-package architecture (M1 preserved)

### 3.1 Decision

**One package with internal components** (IRO-M1 option A remains frozen).

| Option | Verdict |
| --- | --- |
| **A. One package** (`InvestmentResearchOrchestrator`) | **Selected and frozen** — M2 extends the same package |
| B. New sibling packages for Memory / Contradiction / Loop | Rejected — invents package taxonomy beyond approved product packaging |
| C. Implement inside M22 or Stage-1 scaffolds | Rejected — name collision and responsibility transfer |
| D. Redesign M1 into multiple packages | Rejected — redesigns frozen IRO-M1 |

### 3.2 Package identity

| Name | Role |
| --- | --- |
| `InvestmentResearchOrchestrator` | **Only** allowed IRO production package name (M1 + M2) |
| `ResearchOrchestrator` | Frozen M22 package — **unchanged**, not the IRO product |
| `ResearchPlanner/` (Stage-1 scaffold) | Untouched; not the IRO Planner component |
| `ResearchDomain` | Consumed research task/finding/report contracts |
| `EvidenceContradiction` / `EvidenceComparison` | Consumed domain classifiers when numeric path applies |

### 3.3 Frozen package structure (M2 extension)

```text
InvestmentResearchOrchestrator/
  README.md
  models/                   # M1 models + M2 memory/contradiction/loop models
  validation/               # M1 validators + M2 validators
  scanner.py                # Portfolio Scanner (M1 — frozen responsibility)
  planner.py                # Research Planner (M1 + M2 re-research inputs)
  committee_manager.py      # Static Committee Router (M1 — frozen)
  prompt_planner.py         # Prompt Freeze (M1; attempt index used by M2 loop)
  execution_adapter.py      # M22 Adapter (M1; once per unit per attempt)
  evidence_collector.py     # Evidence Collector (M1 — frozen responsibility)
  evidence_store.py         # Evidence Store (M1 — frozen append-only rules)
  memory_comparison_stub.py # M1 stub (historical; retained)
  memory_comparison.py      # Operational Memory Comparison (M2)
  contradiction_engine.py   # Operational Contradiction Engine (M2)
  re_research.py            # Budget + re-research request contracts/helpers (M2)
  run_coordinator.py        # Sequential M1 path + M2 loop + short-circuit
  tests/                    # authorized only with implementation
```

Layout is normative for component boundaries and names. Exact file splitting
inside `models/` / `validation/` / thin helpers may vary at implementation time
without changing ownership or public contract intent.

### 3.4 Non-package rule

IRO-M2 must not create sibling operational packages for Memory Comparison,
Contradiction Engine, or Re-research Loop. Internal modules only.

### 3.5 M1 module freeze rule

M1 modules keep their M1 responsibilities. M2 may:

- add call sites from the coordinator;
- extend Planner inputs for re-research;
- extend Prompt Freeze attempt indexing already anticipated by M1
  (`attempt index`; M1 used `0`);
- add new modules listed above.

M2 must not:

- rewrite Scanner materiality into EV relevance;
- replace Static Router with dynamic intelligence;
- invent collector semantics;
- rewrite append-only store history;
- rename the package to collide with M22.

---

## 4. Internal component boundaries

IRO-M2 freezes **twelve operational components** (nine M1 + three M2) plus the
extended sequential/looping coordinator. Full product components Expected
Value Engine and CIO Engine remain **out of M2**.

| # | Component | Module (normative) | Responsibility (milestone) | Primary outputs |
| --- | --- | --- | --- | --- |
| 1 | Portfolio Scanner | `scanner.py` | M1 structural subject deltas vs prior baseline | `ScanDeltaSet` |
| 2 | Research Planner | `planner.py` | M1 plan from scan deltas; **M2** also plan from re-research requests | `ResearchPlan` |
| 3 | Static Committee Router | `committee_manager.py` | M1 allowlisted task_type → committees | `CommitteeAssignmentPlan` |
| 4 | Prompt Freeze | `prompt_planner.py` | M1 freeze bytes + hash; **M2** distinct attempt index per re-research attempt | `PromptFreezeArtifact` |
| 5 | M22 Adapter | `execution_adapter.py` | M1 assemble task; call M22 once per unit **per attempt** | Exact `PipelineExecutionResult` |
| 6 | Evidence Collector | `evidence_collector.py` | M1 map actual results + explicit bindings | `CollectedEvidence` |
| 7 | Evidence Store | `evidence_store.py` | M1 append-only JSONL/files with provenance | `EvidenceStoreRecord` |
| 8 | Memory Stub | `memory_comparison_stub.py` | M1 presence/statement identity (historical) | `MemoryDeltaSet` (M1 classes) |
| 9 | **Operational Memory Comparison** | `memory_comparison.py` | **M2** meaningful prior-vs-current store deltas | `MemoryDeltaSet` (M2-extended) |
| 10 | **Operational Contradiction Engine** | `contradiction_engine.py` | **M2** detect conflicts; emit cases + unresolved + re-research requests | `ContradictionEvaluation` |
| 11 | **Re-research budget / requests** | `re_research.py` (+ coordinator) | **M2** bound loop depth; materialize planner re-entry intents | `ReResearchBudget`, `ReResearchRequestSet` |
| 12 | Run Coordinator | `run_coordinator.py` | M1 path + M2 memory/contradiction/loop + short-circuit | Terminal `IRORun` status |

### 4.1 Cross-cutting run identity

All components share run-scoped identity carried on `IRORun`:

- opaque nonblank `run_id`
- current `portfolio_snapshot_id`
- prior baseline id **or explicit absence**
- phase enum and terminal status (M2-extended)
- UTC created/updated timestamps
- **M2:** re-research attempt counter / budget remaining (run-local control
  state; may live on run result/control record adjacent to `IRORun` if the
  frozen `IRORun` field set is extended carefully without breaking M1
  validation meaning)

### 4.2 Component non-overlap (normative)

- Scanner does not plan tasks, compare memory, or call M22.
- Planner does not freeze prompts, execute, or resolve contradictions.
- Static Router does not invent committees outside the injected allowlist.
- Prompt Freeze does not invoke providers.
- M22 Adapter does not collect findings, persist evidence, or own multi-task
  retry policy.
- Collector does not rewrite store history or resolve contradictions.
- Store does not mutate portfolio state.
- Memory Stub does not own the M2 operational comparison policy.
- **Operational Memory Comparison** does not own contradiction resolution,
  re-research budgeting, EV, or CIO.
- **Contradiction Engine** does not own domain classifier math, majority-vote
  truth, capital posture, or direct M22 invocation; it emits requests that
  re-enter Planner.
- **Re-research loop control** does not invent tasks outside Planner, rewrite
  prior prompt freezes, or exceed the budget.
- Coordinator does not own domain math or provider stacks.

### 4.3 M1 Memory Stub vs M2 Operational Memory Comparison

| Surface | Milestone | Role in M2 |
| --- | --- | --- |
| `MemoryComparisonStub` | M1 | Historical minimum stub; may remain callable for M1-compat tests and as a building block |
| `MemoryComparison` (operational) | M2 | **Normative runtime comparison** for M2 runs |

M2 runs **must** produce the operational `MemoryDeltaSet` from Operational
Memory Comparison before contradiction evaluation. They must not pretend that
the M1 stub alone satisfies M2 product responsibility.

---

## 5. Run contract (M2-extended)

### 5.1 Owned object: `IRORun` (base) + run control

M1 `IRORun` fields remain:

| Field | Rule |
| --- | --- |
| `run_id` | Opaque nonblank string; run namespace identity |
| `portfolio_snapshot_id` | Nonblank; identity of current snapshot only |
| `prior_baseline_id` | Nonblank string **or** `None` / explicit absence marker |
| `phase` | M2 phase enum (below) |
| `status` | Derived terminal or in-progress status consistent with phase |
| UTC timestamps | Created and updated timestamps on the run record |

M2 **adds** run-control fields (on `IRORun` or adjacent immutable control
record owned by the package — exact placement is an implementation choice
that must preserve validation-first immutability):

| Field | Rule |
| --- | --- |
| `re_research_attempt` | Non-negative int; `0` on first execution wave; increments only on authorized re-research re-entry |
| `re_research_budget_max` | Positive int injected/configured per run; hard ceiling for re-research waves after the initial wave |
| `re_research_budget_remaining` | Non-negative int; decrements when a re-research wave is admitted |

Validation is type/nonblank/enum/range only. No normalization of ids. Invalid
run contract fails closed before scan.

### 5.2 Phase enum (M2)

M1 phases are preserved. M2 adds contradiction and re-research control phases.

```text
Happy path (no re-research):
INITIALIZED
  → SCANNED
  → PLANNED
  → ROUTED
  → PROMPTS_FROZEN
  → EXECUTED
  → COLLECTED
  → STORED
  → MEMORY_COMPARED
  → CONTRADICTION_EVALUATED
  → COMPLETED

Empty-scan short-circuit (M1 preserved):
INITIALIZED → SCANNED → SHORT_CIRCUITED_NO_MATERIAL_DELTA

Re-research path (budget remaining):
  ... → CONTRADICTION_EVALUATED
      → RE_RESEARCH_ADMITTED
      → PLANNED                 # re-entry; attempt increments
      → ROUTED → PROMPTS_FROZEN → EXECUTED → COLLECTED → STORED
      → MEMORY_COMPARED → CONTRADICTION_EVALUATED
      → (loop or terminal)

Budget exhausted with unresolved contradictions:
  ... → CONTRADICTION_EVALUATED
      → ESCALATED_HUMAN_REVIEW

Failure:
  any phase → FAILED
```

Phase names above are normative intent. Implementation may use exact enum
member names matching this vocabulary. M1 phases must retain their M1 string
values where already implemented.

### 5.3 Terminal statuses (M2)

| Terminal | Meaning |
| --- | --- |
| `COMPLETED` | M2 path finished; memory + contradiction evaluation done; no open re-research required (unresolved set empty **or** no re-research requested) |
| `SHORT_CIRCUITED_NO_MATERIAL_DELTA` | Empty material scan; no committee work (M1 preserved) |
| `ESCALATED_HUMAN_REVIEW` | Re-research budget exhausted (or policy forbids further re-research) while unresolved contradictions remain; human review required |
| `FAILED` | Fail-closed stop; no invented success |

`ESCALATED_HUMAN_REVIEW` is a **research-process escalation terminal**. It is
**not** a CIO Engine decision report, not a capital posture order, and not
broker-bound. It may carry posture **markers** `WAIT` / `MONITOR` as
escalation labels only (see §12.6). Full CIO stance enforcement and report
production remain IRO-M4.

### 5.4 Run ownership and multiplicity

- Exactly one `IRORun` identity per invocation namespace.
- Run does not rewrite prior evidence store records.
- Phases advance only along the M2 graph above.
- Human approvals, full CIO stance engine, and capital actions are not part of
  the M2 production decision surface.
- Multiple re-research waves share the same `run_id` and append evidence under
  that run; they do not create silent overwrites.

### 5.5 Run coordinator wiring (M2)

1. Validate `IRORun` + M2 budget fields.
2. Scan → if no material deltas, terminalize
   `SHORT_CIRCUITED_NO_MATERIAL_DELTA` (M1 preserved; **no** contradiction
   loop on empty scan).
3. Plan (scan-derived and/or re-research-derived) → route → freeze prompts
   (attempt index) → execute each planned unit sequentially once via M22
   Adapter → collect → store appends.
4. Operational Memory Comparison → `MemoryDeltaSet`.
5. Operational Contradiction Engine → `ContradictionEvaluation`.
6. If re-research requested **and** budget remaining → admit re-research,
   decrement budget, increment attempt, return to Planner with
   `ReResearchRequestSet` (+ memory deltas as awareness inputs).
7. If re-research requested **and** budget exhausted → terminalize
   `ESCALATED_HUMAN_REVIEW` with explicit unresolved set preserved in store
   and result.
8. If no re-research requested → terminalize `COMPLETED`.
9. On any fail-closed condition → `FAILED`.

EV assembly and CIO synthesis are not coordinated in M2.

---

## 6. IRO-M1 components (frozen; not redesigned)

The following remain governed by `docs/iro/IRO_M1_ARCHITECTURE.md` and the
M1 implementation. M2 restates only the **consume/extension** surface.

### 6.1 Portfolio Scanner

Unchanged M1 structural deltas only. No EV materiality, no contradiction
inputs, no competitor expansion.

### 6.2 Research Planner — M1 base + M2 inputs

**M1 base preserved:**

- convert `ScanDeltaSet` → ordered planned units or empty plan with reasons;
- 1:1 default subject delta → unit for initial wave;
- holding `P0` / watchlist `P1`;
- no free-form “research everything.”

**M2 extension (normative):**

Planner **additionally** accepts:

| Input | Use |
| --- | --- |
| `ReResearchRequestSet` | Primary driver of re-research wave units |
| `MemoryDeltaSet` (awareness) | Optional suppress/emit reasons; must not invent free-form tasks |
| `ContradictionEvaluation.unresolved` (awareness) | Correlate requests; must not majority-resolve |

Re-research planning rules:

1. Each admitted `ReResearchRequest` maps to **zero or more** planned units
   under explicit, static mapping from request reason/task_type allowlist —
   never open-ended research.
2. Default M2 mapping: **1:1** request → planned unit when `task_type` is
   known to the static routing table; unknown `task_type` fails closed.
3. Planner may skip a request with an explicit reason (e.g. subject no longer
   in portfolio snapshot scope) without inventing substitute work.
4. Empty re-research plan with reasons is valid; coordinator then treats “no
   executable re-research” as non-progress and must not infinite-loop (see
   §12.4).
5. Title/objective for re-research units are nonblank structural templates +
   subject id + request reason code only — **no semantic invention** of
   thesis text.

### 6.3 Static Committee Router

Unchanged static allowlist. Unknown `task_type` fails closed. No dynamic
committee intelligence in M2.

### 6.4 Prompt Freeze

Unchanged freeze bytes + hash rules. M2 **requires**:

- `attempt_index` (or equivalent) on `PromptFreezeArtifact` equals the current
  re-research attempt;
- re-research waves **must** materialize new frozen prompt instances (new
  bytes/hash allowed when context bindings change; hash stored per attempt);
- prior attempt freezes remain append-only history; never rewritten.

### 6.5 M22 Adapter

Unchanged: assemble validated `ResearchDomain.ResearchTask`; invoke M22
**exactly once** per planned unit **per attempt**; preserve exact
`PipelineExecutionResult`; propagate exceptions; no synthesized success.

### 6.6 Evidence Collector

Unchanged: no invention; explicit bindings for non-defaultable fields;
missing/failed markers. Still **not** a semantic free-text → numeric
proposition producer.

### 6.7 Evidence Store

Unchanged append-only provenance rules. M2 **requires** store queryability
sufficient for:

- prior vs current finding sets by subject/context key;
- contradiction evaluation inputs;
- re-research attempt provenance (run_id, research_id, attempt, prompt hash).

M2 may append additional payload kinds for contradiction cases, re-research
admissions, and escalation records (see §13). Supersession-as-delete remains
forbidden.

---

## 7. Operational Memory Comparison (M2)

### 7.1 Purpose

Own the product-plane **Memory Comparison** responsibility for M2:

- diff **today’s** stored evidence against **prior** stored evidence for the
  same subject/context;
- surface only **meaningful** operational changes (not byte noise);
- emit `MemoryDeltaSet` for planner awareness, contradiction inputs, and later
  EV/CIO milestones.

### 7.2 Ownership

Owned by `memory_comparison.py` inside `InvestmentResearchOrchestrator`.

Does **not** own:

- domain Evidence package public contracts;
- contradiction resolution or truth selection;
- re-research budget policy;
- EV assembly or CIO stance;
- live portfolio mutation;
- supersession policy wiring as delete-in-place.

### 7.3 Inputs

| Input | Rule |
| --- | --- |
| Current run Evidence Store + `run_id` | Required |
| Prior store + prior run id **or** explicit absence | Required as first-class absence |
| Subject/context keys in scope | From scan subjects, planned subjects, and/or stored finding keys; order preserved from caller/scan encounter order where applicable |

### 7.4 Meaningful change classes (M2)

M1 classes remain valid and form the minimum:

| Class | Meaning |
| --- | --- |
| `NO_PRIOR` | No prior baseline/findings for the key |
| `UNCHANGED` | Prior present; compared payload **meaningfully equal** under M2 equality |
| `STATEMENT_CHANGED` | Prior present; statement exact string inequality (M1) or multi-statement set inequality under §7.5 |
| `ADDED` | Finding/evidence present now, absent prior |
| `REMOVED` | Finding/evidence present prior, absent now |

M2 **adds** operational classes (normative set; exact enum names stable at
implementation):

| Class | Meaning |
| --- | --- |
| `PROVENANCE_CHANGED` | Compared operational content equal, but provenance identity set changed (committee_id / provider / prompt_hash / source_reference material set inequality) — meaningful for audit, not “byte noise” of store metadata timestamps alone |
| `MULTI_FINDING_SET_CHANGED` | Ordered/set comparison of multiple findings for the same subject/context key changed beyond single-statement equality |
| `CONFIDENCE_GAP` | Required completeness still missing/failed for the subject after store appends (feeds contradiction/re-research awareness; does not invent findings) |

**Not meaningful (must ignore as delta drivers):**

- pure store `stored_at` timestamp inequality with identical payload+provenance
  identity;
- JSON serialization whitespace/key-order noise (compare on validated
  structured fields, not raw pretty-print bytes);
- run-local ephemeral paths.

### 7.5 Equality and comparison rules (validation-first)

1. Compare on structured fields extracted from stored FINDING (and optional
   completeness) payloads — not on entire raw JSONL line bytes.
2. Statement equality is **exact string equality** (M1 preserved). No
   case-fold, trim, or semantic paraphrase.
3. Multi-finding comparison uses **input-order-preserving** tuples of
   statements (and stable finding identity if present) per subject key.
4. Provenance identity uses exact string equality of nonblank identifiers.
5. Absence of prior baseline/findings is first-class (`NO_PRIOR`), never silent
   equality with empty.
6. No free-text interpretation as numeric materiality.
7. No consumption of `ExactNumericDeltaMateriality` as a required M2
   dependency (deferred deeper materiality remains later).

### 7.6 Output: `MemoryDeltaSet` (M2)

| Field | Rule |
| --- | --- |
| `run_id` | Exact current run |
| `deltas` | Ordered `MemoryDelta[]` |
| each `MemoryDelta` | `subject_key`; `prior_present: bool`; `delta_class`; optional structured detail payload for multi-finding/provenance classes (immutable) |

Empty delta set is valid (all in-scope keys unchanged or empty scope).

### 7.7 Invariants

1. Memory Comparison never invents findings.
2. Memory Comparison never rewrites the store.
3. Memory Comparison never majority-votes truth.
4. Memory Comparison never calls M22.
5. Baseline/prior absence is explicit.
6. Output order preserves subject key encounter order used as input scope,
   then any additional keys discovered in current store, then prior-only keys
   (same family of order rules as M1 stub).

### 7.8 Failure

Invalid store types, invalid run ids, or validator failures fail closed. Do
not emit a fake `UNCHANGED` covering validation failure.

### 7.9 Non-responsibilities

- Deep semantic delta materiality engines
- Supersession authority selection
- Contradiction resolution
- EV / CIO production
- Semantic invention

---

## 8. Operational Contradiction Engine (M2)

### 8.1 Purpose

Own the product-plane **Operational Contradiction Engine** responsibility:

- detect conflicting evidence for subjects in the current run scope;
- use domain classifiers where applicable;
- escalate **re-research** when confidence is insufficient;
- emit contradiction cases, re-research requests, and an **explicit
  unresolved set**;
- respect the bounded re-research depth owned by the loop controller.

### 8.2 Ownership

Owned by `contradiction_engine.py` inside `InvestmentResearchOrchestrator`.

Domain ownership remains:

| Concern | Owner |
| --- | --- |
| Pairwise numeric contradiction **candidate** classification | `EvidenceContradiction` |
| Numeric comparison identity | `EvidenceComparison` |
| Proposition structure | `EvidenceProposition` / accepted producers |
| Operational case assembly, unresolved set, re-research requests | **IRO-M2 Contradiction Engine** |

### 8.3 Detection paths (normative)

M2 freezes **two** detection paths. Both are operational; neither selects
final truth.

#### Path A — Domain numeric candidate classification (when applicable)

When the run has access to accepted `ExactObservedNumericProposition` pairs
(caller-supplied into the evaluation boundary and/or stored under an explicit
M2-allowed payload kind that carries validated proposition structure):

1. Form candidate pairs under product scope rules (same comparison identity
   family as domain: subject/predicate/unit/effective_context when using
   domain packages).
2. Invoke `EvidenceContradiction` classifier **consume-only**.
3. Map:
   - `CONTRADICTION_CANDIDATE` → operational contradiction case
     `NUMERIC_CANDIDATE`;
   - `NO_CONTRADICTION_CANDIDATE` → no case from that pair;
   - `NOT_ELIGIBLE` → explicit ineligible marker (not silent pass, not fake
     contradiction).
4. Propagate domain validation exceptions; do not invent corrected
   propositions.

If no numeric propositions are available, Path A emits **no** numeric cases
and records `NUMERIC_PATH_NOT_APPLICABLE` for audit — **not** a failure by
itself.

#### Path B — Operational research-finding conflict (M1 evidence surface)

Because IRO-M1 Collector stores `ResearchFinding` statements without semantic
numeric production, M2 must still detect **operational** conflicts on the
accepted finding surface:

| Trigger | Case class |
| --- | --- |
| Same `subject_key` / research scope has ≥2 successful findings whose statements are exact-string unequal across different `committee_id` values in the current run wave | `MULTI_COMMITTEE_STATEMENT_CONFLICT` |
| Current run finding statement exact-unequal to prior retained finding statement for same subject_key when prior was present and memory class is `STATEMENT_CHANGED` / `MULTI_FINDING_SET_CHANGED` | `PRIOR_VS_CURRENT_STATEMENT_CONFLICT` |
| Required completeness missing/failed for a subject that also has at least one conflict case or an explicit re-research policy flag | `CONFIDENCE_INSUFFICIENT` |

Rules:

1. Statement inequality is exact string inequality only — no paraphrase
   detection, embedding similarity, or LLM-as-judge.
2. Same committee repeating the same statement is not a conflict.
3. Missing committee answers are completeness gaps (`CONFIDENCE_INSUFFICIENT`
   when policy requires), never simulated answers.
4. Path B **must not** claim domain `EvidenceContradiction` status codes for
   non-proposition findings.
5. Path B **must not** invent numeric propositions from free text.

### 8.4 Confidence and re-research request rules

A contradiction case **requests re-research** when any of the following hold:

1. Case class is `NUMERIC_CANDIDATE` and no explicit caller-supplied
   “accept unresolved” directive exists for that case id (default: request
   re-research).
2. Case class is `MULTI_COMMITTEE_STATEMENT_CONFLICT`.
3. Case class is `PRIOR_VS_CURRENT_STATEMENT_CONFLICT` and the subject remains
   in portfolio/scan scope.
4. Case class is `CONFIDENCE_INSUFFICIENT` for a required completeness gap on
   a subject that already has open conflict or is in the current research
   scope with failed/missing required committees.

A case is placed in the **unresolved set** whenever it is detected and not
explicitly closed by a **new** successful re-research wave that removes the
triggering condition under §8.5. Closure is structural (trigger absent), not
truth selection.

### 8.5 Closure without truth selection (critical freeze)

A contradiction case may be marked `STRUCTURALLY_CLEARED` only when:

- a later attempt stores evidence such that the **exact triggering condition
  no longer holds** (e.g. missing committee now completed and statements
  exact-equal across required committees; or numeric path no longer yields
  `CONTRADICTION_CANDIDATE` for the same pair identity), **and**
- clearance is recorded with provenance (attempt, research_ids, prompt
  hashes).

The engine must **never**:

- pick a winning committee by majority;
- delete prior conflicting evidence;
- average statements;
- ask an LLM to “choose the truth” as an IRO-owned resolution step;
- collapse unresolved cases into silent success.

If triggers remain after evaluation, cases stay `UNRESOLVED`.

### 8.6 Output: `ContradictionEvaluation`

| Field | Rule |
| --- | --- |
| `run_id` | Exact run |
| `attempt` | Current re-research attempt index |
| `cases` | Ordered `ContradictionCase[]` |
| `unresolved` | Ordered subset / ids still `UNRESOLVED` |
| `re_research_requests` | `ReResearchRequestSet` (possibly empty) |
| `numeric_path_status` | `APPLIED` \| `NOT_APPLICABLE` \| `PARTIAL` |

#### `ContradictionCase`

| Field | Rule |
| --- | --- |
| `case_id` | Opaque nonblank under run |
| `subject_key` | Nonblank |
| `case_class` | Enum from §8.3 |
| `status` | `UNRESOLVED` \| `STRUCTURALLY_CLEARED` \| `INELIGIBLE` |
| `evidence_refs` | Provenance references (research_id, committee_id, store offsets/ids, prompt_hash as available) |
| `domain_status` | Optional exact domain enum value when Path A applied |
| `notes_code` | Optional closed enum reason code — not free-form narrative invention |

#### `ReResearchRequest`

| Field | Rule |
| --- | --- |
| `request_id` | Opaque nonblank |
| `subject_key` | Nonblank |
| `reason_code` | Closed enum (`NUMERIC_CANDIDATE`, `MULTI_COMMITTEE_STATEMENT_CONFLICT`, `PRIOR_VS_CURRENT_STATEMENT_CONFLICT`, `CONFIDENCE_INSUFFICIENT`) |
| `task_type` | Allowlisted static type for Router |
| `source_case_ids` | One or more case ids |
| `priority` | `P0` \| `P1` \| `P2` (default: inherit subject class mapping; conflicts on holdings → `P0`) |

### 8.7 Invariants

1. No majority-vote truth selection.
2. No final “truth” field on cases.
3. No rewrite of append-only evidence.
4. No direct M22 invocation from the engine.
5. No reimplementation of `EvidenceContradiction` math.
6. Unresolved set is always explicit (possibly empty).
7. Empty evaluation (no cases) is valid and yields empty re-research requests.
8. Domain exceptions propagate; do not synthesize domain success.

### 8.8 Failure

Invalid inputs fail closed. Partial domain applicability is not failure.
Collector/store failures are handled upstream; the engine does not invent
evidence to evaluate.

### 8.9 Non-responsibilities

- Final contradiction **resolution** / authority selection
- Semantic invention / free-text numeric extraction
- EV Engine / CIO Engine
- Capital actions
- Replacing domain Evidence* packages
- Unbounded loops (owned by budget controller)

---

## 9. Bounded Re-research Loop (M2)

### 9.1 Purpose

Own the product-plane control loop:

> Contradiction-driven re-research returns to **Research Planner** with a
> **bounded** re-research depth per run. Exceeding depth escalates to human
> (WAIT/MONITOR markers), not unbounded looping.

### 9.2 Ownership

| Concern | Owner |
| --- | --- |
| Budget configuration and decrement | Run coordinator + `re_research.py` contracts |
| Admission of a re-research wave | Run coordinator |
| Task shaping for re-research | Research Planner |
| Execution of admitted units | Existing M1 path (route → freeze → M22 → collect → store) |
| Escalation terminal | Run coordinator |

### 9.3 Budget model

| Parameter | Rule |
| --- | --- |
| `re_research_budget_max` | Required positive int for M2 runs (injected). Architecture does not hardcode a single global number; implementation tests must cover 1 and N. |
| Initial wave | Attempt `0`; does **not** consume re-research budget |
| Re-research wave | Each admission consumes **1** budget unit and increments attempt by 1 |
| Budget remaining `0` | No further admission; if unresolved requests remain → `ESCALATED_HUMAN_REVIEW` |

Budget is per `run_id`, not per subject, unless a future milestone explicitly
splits budgets (out of M2).

### 9.4 Admission rules

Admit re-research only when **all** hold:

1. `ContradictionEvaluation.re_research_requests` is non-empty, **or**
   policy-equivalent non-empty request set after Planner skip filtering still
   had open unresolved cases requiring research;
2. `re_research_budget_remaining > 0`;
3. Previous wave made **progress eligibility** (see §9.5) or this is the first
   re-research admission after attempt `0`;
4. Run status is still in-progress (not terminal).

### 9.5 Non-progress and anti-infinite-loop rules

To prevent infinite loops even when budget is misconfigured:

1. If Planner returns an **empty** plan for an admitted request set, do not
   re-admit the same request set unchanged; mark requests
   `UNPLANABLE` and escalate if unresolved remain.
2. If a wave completes with **identical** unresolved case identity set and
   **identical** reason codes as the previous evaluation, treat as
   non-progress; do not burn the entire budget on pure repetition — escalate
   after at most one non-progress retry **or** immediately if budget policy
   is `strict` (implementation must pick one and test it; default
   architecture choice: **immediate escalate on exact non-progress**).
3. Never retry the same frozen prompt instance as a substitute for a new
   attempt; always new Prompt Freeze with new attempt index.
4. Never invent committees or findings to force progress.

### 9.6 Re-entry data flow

```text
ContradictionEvaluation
  → ReResearchRequestSet
  → (budget admit) → attempt += 1; budget_remaining -= 1
  → Research Planner (requests + memory awareness + scan context)
  → Static Router → Prompt Freeze (attempt_index)
  → M22 Adapter (once/unit) → Collector → Store (append)
  → Operational Memory Comparison
  → Operational Contradiction Engine
  → terminal or loop
```

### 9.7 Escalation markers (not CIO Engine)

On `ESCALATED_HUMAN_REVIEW`, the run result MUST include:

| Field | Rule |
| --- | --- |
| `unresolved_case_ids` | Explicit |
| `escalation_marker` | `WAIT` or `MONITOR` (closed enum) |
| `escalation_reason_code` | e.g. `RE_RESEARCH_BUDGET_EXHAUSTED`, `NON_PROGRESS`, `UNPLANABLE_REQUESTS` |
| provenance | last attempt, budget max/remaining |

Marker selection rule (deterministic, non-CIO):

- `MONITOR` — unresolved conflicts exist but required committees completed;
- `WAIT` — completeness gaps remain and/or confidence insufficient cases
  remain.

These markers are **research-process escalation labels** for humans. They are
not orders, not allocation proposals, and not a substitute for IRO-M4 CIO
report production.

### 9.8 Relationship to M22 retry

- M22 does not own IRO multi-task retry policy.
- Adapter-level provider retry remains out of scope (M1 rule preserved): no
  adapter-level retry of M22/pipeline/provider calls.
- Re-research is an **IRO-level** new planning wave, not an M22 internal
  retry.

### 9.9 Non-responsibilities

- Unbounded loops
- Silent success on unresolved contradictions
- Truth selection to exit the loop
- CIO full report engine
- Capital execution after escalation

---

## 10. Dependency direction

### 10.1 Runtime data/control dependency graph

```text
PortfolioSnapshot (+ nested portfolio contracts)
        │
        ▼
   Portfolio Scanner ──► ScanDeltaSet
        │
        ▼
   Research Planner ──► ResearchPlan / PlannedUnits
        │                 ▲
        │                 │  ReResearchRequestSet (M2 loop)
        │                 │
        ├──────────────► Static Committee Router + StaticRoutingTable
        │                       │
        └──────────────► Prompt Freeze + template/bindings (attempt_index)
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
                     Operational Memory Comparison ──► MemoryDeltaSet
                                │
                                ▼
                     Operational Contradiction Engine
                        ├── ContradictionEvaluation
                        ├── unresolved set
                        └── ReResearchRequestSet ──► (budget?) ──► Planner
                                                     └── else escalate human

IRORun coordinates phases + budget; does not own domain math or providers.
joo_auto / Automation M1–M3: build plane only — zero runtime dependency.
```

### 10.2 Internal build dependency order (package modules)

```text
models / validation
    → evidence_store
    → memory_comparison_stub          # M1 historical
    → memory_comparison               # M2 operational
    → re_research                     # budget + request contracts
    → contradiction_engine            # consumes memory + store + optional domain
    → scanner
    → planner                         # scan + re-research inputs
    → committee_manager
    → prompt_planner
    → execution_adapter
    → evidence_collector
    → run_coordinator                 # wires M1 path + M2 loop
```

### 10.3 Dependency direction rules

1. Domain packages never import IRO.
2. IRO never reimplements domain classifier math.
3. M22 never imports IRO.
4. Automation never becomes a runtime dependency of IRO.
5. Contradiction Engine depends **inward** on store/memory outputs and
   optional domain classifiers; Planner depends on Contradiction outputs only
   via coordinator-mediated re-entry (no circular module import requiring
   engine to import planner).

---

## 11. Allowed and forbidden dependencies

### 11.1 Allowed dependencies (M2)

IRO-M2 may depend on (consume / inject) all M1 allowed dependencies, plus:

| Dependency | Use |
| --- | --- |
| `EvidenceContradiction` | Path A numeric candidate classification (consume-only) |
| `EvidenceComparison` | Only as required transitively by domain classifier ownership; IRO must not reimplement |
| `EvidenceProposition` / `ExactObservedNumericProposition` | Only when Path A inputs are present |
| M1 package modules / contracts | Frozen base |

M1 allowed set remains:

- `ResearchDomain`
- `ResearchOrchestrator` (M22) injected
- `PipelineRuntime` via M22 chain
- Committee / AIAdapter / ExecutionEngine models as pipeline assembly fields
- Portfolio snapshot family
- Prompt template bytes + id/version
- Python stdlib
- Injected configuration (`StaticRoutingTable`, bindings, store root, **M2
  budget**)

### 11.2 Forbidden dependencies (M2)

All M1 forbidden dependencies remain forbidden. M2 additionally forbids:

| Forbidden | Reason |
| --- | --- |
| Operational EV Engine / end-to-end `ExactExpectedValue` wiring as M2 feature | Deferred IRO-M3 |
| CIO Engine as production decision engine / report authority | Deferred IRO-M4 |
| Stage 5 allocation packages as runtime research dependency | Separate plane |
| Broker / order / rebalancing APIs | Capital execution permanently out |
| Semantic free-text → numeric proposition producers as required M2 path | Deferred; Collector remains non-semantic |
| Majority-vote / LLM-as-judge truth modules | Explicitly rejected |
| Automation / `joo_auto` runtime | Different plane |
| Parallel async fan-out frameworks | Sequential only in M2 |
| Redesign of accepted domain public contracts | Consume-only |

Optional note: M2 **may** consume `EvidenceContradiction` without requiring
`ExactExpectedValue`, Signal/Hypothesis/Thesis authoring, or Portfolio Impact
packages.

---

## 12. State transitions (normative)

### 12.1 Phase graph

See §5.2. Normative constraints:

1. `INITIALIZED` is the only legal start phase for `RunCoordinator.run`.
2. Empty material scan may go only to `SHORT_CIRCUITED_NO_MATERIAL_DELTA`.
3. `MEMORY_COMPARED` requires successful store phase for the current wave
   (including waves that collected only failures — store may hold failure
   markers; memory still runs).
4. `CONTRADICTION_EVALUATED` requires `MEMORY_COMPARED` for that wave.
5. `RE_RESEARCH_ADMITTED` only from `CONTRADICTION_EVALUATED` with budget and
   requests.
6. Re-entry always re-enters at `PLANNED` (not mid-execution).
7. Terminals are absorbing: `COMPLETED`,
   `SHORT_CIRCUITED_NO_MATERIAL_DELTA`, `ESCALATED_HUMAN_REVIEW`, `FAILED`.

### 12.2 Status mapping

| Phase / event | Status |
| --- | --- |
| Any non-terminal phase | `IN_PROGRESS` |
| `COMPLETED` phase | `COMPLETED` |
| Empty-scan terminal | `SHORT_CIRCUITED_NO_MATERIAL_DELTA` |
| Escalation terminal | `ESCALATED_HUMAN_REVIEW` |
| Failure | `FAILED` |

### 12.3 Attempt and budget transitions

```text
start: attempt=0, remaining=max
initial wave executes
evaluate contradictions
if requests and remaining>0 and progress rules pass:
    remaining -= 1
    attempt += 1
    re-enter plan
else if requests and (remaining==0 or non-progress):
    ESCALATED_HUMAN_REVIEW
else:
    COMPLETED
```

### 12.4 Empty plan on re-research

If re-research is admitted and Planner returns empty units with skips:

- do not execute M22;
- still allow Memory/Contradiction evaluation only if new evidence could have
  been stored (it was not) — architecture choice: **skip** memory/contradiction
  recompute and escalate as `UNPLANABLE_REQUESTS` when empty plan follows
  admission (deterministic, fail closed on non-progress).

### 12.5 Failure transitions

Any fail-closed condition from M1 (invalid run, unknown route, prompt
failure, M22 exception policy, store IO failure, etc.) transitions to
`FAILED`. M2 adds fail-closed for invalid budget values and invalid
contradiction/memory contracts.

### 12.6 Human escalation vs Human Authority plane

`ESCALATED_HUMAN_REVIEW` notifies the Human Authority plane that research is
incomplete or conflicted. M2 does **not** implement the full human gate record
product surface of IRO-M4. It only freezes the run terminal + markers +
append-only escalation record in the Evidence Store.

---

## 13. Data contracts (M2)

Normative field rules for authorized implementation (schemas as code are not
created by this document).

### 13.1 Preserved M1 contracts

All M1 contracts in `docs/iro/IRO_M1_ARCHITECTURE.md` §23 remain valid:

`IRORun` (base fields), `ScanDelta*`, `ResearchPlan`, `PlannedUnit`,
`CommitteeAssignmentPlan`, `StaticRoutingTable`, `PromptFreezeArtifact`,
`ExecutableResearchTask`, `ExecutionRecord`, `CollectionBinding`,
`CollectedEvidence`, `EvidenceStoreRecord`, M1 `MemoryDelta*`.

### 13.2 M2 contract additions

| Contract | Required fields / rules |
| --- | --- |
| `ReResearchBudget` | `max_attempts: int > 0`; `remaining: int >= 0`; `remaining <= max` |
| `ReResearchRequest` | §8.6 |
| `ReResearchRequestSet` | `run_id`; `attempt`; ordered requests |
| `ContradictionCase` | §8.6 |
| `ContradictionEvaluation` | §8.6 |
| `MemoryDelta` (M2) | M1 fields + extended `delta_class` enum + optional detail |
| `MemoryDeltaSet` | `run_id`; ordered deltas (M2 comparison output) |
| `EscalationRecord` | `run_id`; `marker ∈ {WAIT, MONITOR}`; `reason_code`; unresolved ids; budget snapshot; UTC timestamp |
| `IRORun` control extension | attempt + budget fields (§5.1) |
| `IRORunPhase` extension | `CONTRADICTION_EVALUATED`, `RE_RESEARCH_ADMITTED`, `ESCALATED_HUMAN_REVIEW` |
| `IRORunStatus` extension | `ESCALATED_HUMAN_REVIEW` |
| `EvidencePayloadKind` extension | `MEMORY_DELTA_SET`, `CONTRADICTION_EVALUATION`, `RE_RESEARCH_ADMISSION`, `ESCALATION` (append-only audit) |

### 13.3 Enum freezes (M2)

**Memory delta classes:** M1 set + `PROVENANCE_CHANGED` +
`MULTI_FINDING_SET_CHANGED` + `CONFIDENCE_GAP`.

**Contradiction case classes:** `NUMERIC_CANDIDATE`,
`MULTI_COMMITTEE_STATEMENT_CONFLICT`, `PRIOR_VS_CURRENT_STATEMENT_CONFLICT`,
`CONFIDENCE_INSUFFICIENT`.

**Case status:** `UNRESOLVED`, `STRUCTURALLY_CLEARED`, `INELIGIBLE`.

**Escalation markers:** `WAIT`, `MONITOR` only in M2 (not full CIO enum).

**Not in M2 production enforcement:** full CIO stance engine
(`HOLD|WAIT|MONITOR|AGGRESSIVE ADD|ADJUST` as decision report), EV assessment
bundles, allocation proposals.

### 13.4 Provenance minimum (M2 append kinds)

Every new store record kind MUST still satisfy M1 provenance minimum
(`run_id`, task/research id when applicable, committee/provider when
applicable, prompt identity/hash when applicable, timestamps, payload kind +
payload) and additionally for loop records:

- attempt index
- budget snapshot when relevant
- links to `case_id` / `request_id` when relevant

---

## 14. Domain invariants (M2)

All M1 domain invariants remain normative. M2 adds:

1. **Meaningful memory only** — operational comparison ignores pure byte noise.
2. **Explicit unresolved contradictions** — never silent drop.
3. **Bounded re-research** — finite budget; escalate, do not spin forever.
4. **No majority-vote truth** — structural clearance only.
5. **No semantic invention** — especially no free-text → numeric proposition
   production inside M2 to “enable” Path A.
6. **Path A consume-only** — domain classifiers unchanged.
7. **Attempt-scoped prompt freeze** — each attempt has its own immutable
   prompt artifact.
8. **Append-only under loops** — re-research appends; never rewrites.
9. **Planner-mediated re-entry** — Contradiction Engine does not bypass
   Planner.
10. **M1 short-circuit preserved** — empty scan does not enter contradiction
    loops.
11. **Sequential execution preserved** — no parallel fan-out in M2.
12. **Name separation preserved** — package ≠ M22.

---

## 15. Failure semantics

| Failure class | Behavior |
| --- | --- |
| All M1 failure classes | Unchanged fail-closed / propagate semantics |
| Invalid re-research budget | Fail closed before scan |
| Invalid memory comparison inputs | Fail closed; no fake UNCHANGED |
| Domain classifier validation exception (Path A) | Propagate; do not invent propositions |
| Contradiction evaluation contract invalid | Fail closed |
| Re-research non-progress / empty plan after admission | Escalate `ESCALATED_HUMAN_REVIEW` (not infinite retry) |
| Budget exhausted with unresolved cases | `ESCALATED_HUMAN_REVIEW` |
| Store IO during loop append | Fail closed; do not claim stored; do not rewrite prior lines |
| M22 exception on re-research unit | Propagate / fail closed per M1 adapter rules; do not synthesize success |

Fail closed remains the default for capital-relevant synthesis. M2 still
refuses to invent completeness or truth.

---

## 16. Retry semantics

1. **No adapter-level retry** of M22 / pipeline / provider calls (M1
   preserved).
2. **Contradiction-driven re-research** is the only multi-wave research loop
   in M2 and is **budgeted**.
3. **No rewrite of frozen prompts** as a retry strategy; new attempt → new
   freeze.
4. **No invention of missing committees** on retry or re-research.
5. A **new run** (new `run_id`) may be started by the caller after failure or
   escalation; prior Evidence Store records remain append-only history.
6. M22 does not own IRO multi-task retry policy; IRO-M2 owns run-level loop
   budgets.

---

## 17. Repository boundaries

### 17.1 Architecture host

Canonical architecture path for this milestone:

```text
docs/iro/IRO_M2_ARCHITECTURE.md
```

Related authoritative documents:

```text
docs/INVESTMENT_RESEARCH_ORCHESTRATOR_ARCHITECTURE.md
docs/iro/IRO_M1_ARCHITECTURE.md
```

### 17.2 What this document may do

- Freeze IRO-M2 implementation architecture under `docs/iro/`.
- Cite approved product architecture and frozen IRO-M1 architecture /
  implementation.
- Define M2 purpose, ownership, components, contracts, deps, invariants,
  state transitions, failure/retry, deferred and rejected responsibilities.

### 17.3 What this document must not do

- Create or modify production package code under
  `InvestmentResearchOrchestrator/` (beyond architecture text).
- Create or modify tests.
- Modify existing JOO domain packages, M22, Stage-1 scaffolds, Automation, or
  `joo_auto`.
- Stage, commit, tag, or push.
- Redesign IRO-M1 or the approved product architecture.
- Authorize capital execution, Automation redesign, or domain public contract
  changes.

### 17.4 Future implementation repository boundary (when authorized)

When (and only when) implementation is separately authorized:

- May extend package `InvestmentResearchOrchestrator/` and its tests/README
  within this M2 architecture.
- Must not modify accepted domain public contracts for M2.
- Must not modify Automation / `joo_auto`.
- Must not rename or replace M22 `ResearchOrchestrator`.
- Must not implement deferred or rejected responsibilities listed below.
- Must not redesign frozen M1 component responsibilities except for the
  explicit Planner input extension and coordinator loop wiring defined here.

### 17.5 Planes (normative distinction preserved)

1. Development Automation — `joo_auto` / M1–M3; builds JOO; does not run research.
2. Human Authority — operator; capital-relevant approval; receives M2
   escalation markers.
3. IRO operational — this milestone’s extended package slice.
4. JOO domain-contract — consume only.
5. Research execution infrastructure — M22 + PipelineRuntime + Committee stack.

Capital execution remains permanently outside IRO.

---

## 18. Compatibility matrix

| Dependency / peer | Compatibility rule |
| --- | --- |
| Automation M1–M3 | Development plane only; zero runtime dependency; no redesign as part of IRO-M2 |
| M22 `ResearchOrchestrator` | Injected once per planned unit per attempt; exact result preservation; name collision rejected |
| Investment Research Orchestrator Architecture | M2 implements product Memory + Contradiction loop subset; does not implement EV/CIO |
| IRO-M1 Architecture | Frozen input; extended not redesigned |
| IRO-M1 Implementation | Package and M1 modules remain base; M2 adds modules + coordinator/planner extensions |
| `EvidenceContradiction` | Consume-only Path A; no package replacement |
| Stage 5 allocation / recommendation endpoint | Separate planes; not M2 outputs |
| Stage-1 `ResearchPlanner` / `ResearchQueue` | Untouched; not IRO Planner |

---

## 19. Implementation boundary

### 19.1 IRO-M2 may include only

1. Operational Memory Comparison module and M2 memory contracts/enums.
2. Operational Contradiction Engine module and contradiction contracts.
3. Re-research budget/request contracts and coordinator loop admission.
4. Planner extension to accept re-research requests (+ memory awareness).
5. Phase/status extensions required by §5.
6. Evidence Store payload kinds for memory/contradiction/re-research/
   escalation audit records (append-only).
7. Prompt Freeze attempt indexing for re-research waves.
8. Run result surface exposing `MemoryDeltaSet`, `ContradictionEvaluation`,
   escalation markers.
9. README updates for M2 non-responsibilities and public API.
10. Unit tests (when implementation authorized) per §21.

### 19.2 IRO-M2 must not include

- Expected Value Engine / ExactExpectedValue end-to-end wiring
- CIO Engine decision report production / full stance enum enforcement as
  capital-relevant decision engine
- Automatic capital allocation
- Portfolio rebalancing
- Broker integration / order routing / buy-sell execution / autonomous trading
- Majority-vote or LLM-as-judge truth selection
- Semantic invention outside accepted JOO contracts
- Required free-text → `ExactObservedNumericProposition` production
- Signal / Hypothesis / Thesis authoring automation
- Learning Engine, dashboard/UI, scheduling/SaaS multi-tenant runtime
- Parallel / async committee fan-out
- Any Automation M1–M3 code change
- Redesign of accepted domain public contracts
- Redesign of frozen IRO-M1 Scanner/Router/Collector/Store core
  responsibilities
- Unbounded re-research loops

### 19.3 Implementation sequence (when authorized)

1. M2 models + validation (budget, requests, cases, phases/status, memory
   class extensions, store payload kinds)
2. Operational Memory Comparison + tests (meaningful classes, absence,
   noise rejection)
3. Contradiction Engine Path B + tests (no truth selection)
4. Contradiction Engine Path A wiring (optional inputs) + domain exception
   propagation tests
5. Re-research budget helpers + non-progress rules
6. Planner re-research input path + empty/unplanable tests
7. Prompt Freeze attempt index for re-research
8. Run coordinator loop + escalation terminal + short-circuit preservation
9. Append-only audit records for evaluation/admission/escalation
10. README + package API docs
11. **No** domain public contract changes; **No** Automation changes

---

## 20. Testing boundary

### 20.1 Architecture-authoring tests

This document creates **no** tests.

### 20.2 Required tests when implementation is authorized

Unit tests MUST cover at least:

**Preserved M1 expectations still green:**

1. Scan skip for unchanged subjects
2. Empty plan with reasons
3. Completeness block structure
4. Append-only Evidence Store behavior
5. Prompt freeze hash stability / mismatch fail-closed

**M2 additions:**

6. Memory Comparison: `NO_PRIOR` / `ADDED` / `REMOVED` / `UNCHANGED` /
   `STATEMENT_CHANGED`
7. Memory Comparison: ignores pure timestamp-only noise; emits
   `PROVENANCE_CHANGED` when provenance identity set changes with equal
   statements
8. Memory Comparison: multi-finding set change class
9. Contradiction Path B: multi-committee unequal statements → case +
   re-research request
10. Contradiction: equal statements across committees → no conflict case
11. Contradiction: unresolved set explicit; no majority-vote API/field
12. Path A (when propositions supplied): domain `CONTRADICTION_CANDIDATE`
    maps to operational case; domain exceptions propagate
13. Path A absent: `NUMERIC_PATH_NOT_APPLICABLE` without failure
14. Budget: initial wave does not consume; each admission consumes one
15. Budget exhausted with unresolved → `ESCALATED_HUMAN_REVIEW` with WAIT or
    MONITOR marker
16. Non-progress / empty re-research plan → escalate, no infinite loop
17. Re-research re-enters Planner → new attempt_index on Prompt Freeze → M22
    once per new unit
18. Empty scan still short-circuits without contradiction loop
19. Append-only: contradiction/escalation records do not rewrite prior lines
20. Invalid types/blank ids fail closed for new contracts

Tests must use `unittest` style consistent with the repository. Failures must
not be hidden by weakening assertions.

---

## 21. Deferred responsibilities

Intentionally **not** in IRO-M2:

1. Operational Expected Value Engine / ExactExpectedValue end-to-end wiring
   (IRO-M3 direction).
2. CIO Engine, full stance enforcement
   (`HOLD|WAIT|MONITOR|AGGRESSIVE ADD|ADJUST` as decision report), and human
   gate records product surface (IRO-M4 direction).
3. Semantic free-text → `ExactObservedNumericProposition` production.
4. Signal → Hypothesis → Thesis **authoring** automation.
5. Learning Engine (prompt improvement from outcomes).
6. Dashboard / UI.
7. Scheduling / multi-tenant SaaS runtime.
8. Parallel / async committee fan-out.
9. Portfolio allocation proposal generation and constraint evaluation
   (Stage 5 plane).
10. Risk sizing, order tickets, broker APIs.
11. News scraping implementation.
12. Automatic entity/ticker resolution beyond caller-supplied portfolio
    identities.
13. Final truth selection / contradiction **resolution** beyond structural
    clearance + re-research + human escalation.
14. Full supersession policy wiring as authority selection.
15. Deep numeric materiality via `ExactNumericDeltaMateriality` as a required
    memory driver.
16. PromptLibrary full registry productization beyond identity + freeze.
17. Redesign of Automation M1–M3 or of accepted domain public contracts.
18. Competitor / supplier / customer / sector leader expansion classes in
    Scanner/Planner (beyond holdings and watchlist structural scope).
19. Dynamic committee intelligence / adaptive model selection.
20. Per-subject independent re-research budgets (global per-run budget only
    in M2).

---

## 22. Explicitly rejected responsibilities

IRO-M2 (and IRO product where listed as permanent) **must never**:

1. Execute trades, route orders, rebalance, or call brokers.
2. Issue BUY/SELL **orders** or treat research postures/markers as executable
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
10. Bypass human authority for capital-relevant recommendations.
11. Replace M22 `ResearchOrchestrator` by silently reusing its package name.
12. Implement investment research inside Development Automation.
13. Redesign Automation M1–M3 as part of IRO work.
14. Implement **Expected Value Engine** as an M2 feature.
15. Implement **CIO Engine** as an M2 feature.
16. Perform **majority-vote truth selection** or any silent contradiction
    “resolution.”
17. Perform **semantic invention** outside accepted JOO contracts.
18. Implement automatic capital allocation, portfolio rebalancing, broker
    integration, order routing, or autonomous trading.
19. Extend Stage-1 `ResearchPlanner.ResearchTask` as the M22 task type.
20. Run unbounded re-research loops.
21. Redesign frozen IRO-M1 architecture under the guise of M2.
22. Treat `ESCALATED_HUMAN_REVIEW` markers as broker or allocation commands.

---

## 23. Auditability and provenance (M2)

IRO-M2 must support audit of everything M1 supports, plus:

- which memory deltas were raised and under which meaningful classes;
- which contradiction cases were opened, cleared structurally, or left
  unresolved;
- whether numeric Path A was applied, partial, or not applicable;
- which re-research requests were admitted or skipped and why;
- attempt index and budget max/remaining at each admission/escalation;
- escalation marker (`WAIT`/`MONITOR`) and reason code;
- that no capital order was emitted by IRO.

Append-only Evidence Store + frozen prompt artifacts per attempt + run
identity form the minimum audit substrate.

---

## 24. Risks and closed defects (M2 architecture)

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Unbounded contradiction re-research loops | High | Hard budget + non-progress escalate |
| Majority-vote truth hidden in “resolution” helpers | High | Structural clearance only; explicit unresolved set; rejected responsibility |
| Semantic invention to feed Path A | High | Path A optional; Collector remains non-semantic; Path B exact-string only |
| Redesigning M1 under M2 | High | Non-redesign rule; M1 modules frozen in responsibility |
| Name collision with M22 | High | Package name unchanged and distinct |
| Escalation markers confused with CIO/orders | High | Markers only; CIO deferred; capital rejected |
| Empty scan entering contradiction loop | Medium | Short-circuit preserved before plan/loop |
| Budget thrash with empty plans | Medium | Unplanable → escalate |
| Provenance noise as false memory deltas | Medium | Meaningful-class rules ignore pure timestamps |
| Domain classifier reimplementation | High | Consume-only `EvidenceContradiction` |

Under this architecture the following defects are **closed by design**:

| ID | Defect if left unaddressed | Status |
| --- | --- | --- |
| M2-B1 | Pure linear M1 path without re-research when product requires loop | Closed — budgeted loop |
| M2-B2 | Memory stub treated as full Memory Comparison | Closed — operational comparison module |
| M2-B3 | Silent contradiction resolution | Closed — unresolved set + no majority vote |
| M2-B4 | Unbounded loops | Closed — budget + non-progress |
| M2-B5 | EV/CIO sneaking into M2 | Closed — deferred/rejected |
| M2-B6 | Automation/runtime coupling | Closed — plane isolation |
| M2-B7 | M22 identity collision | Closed — name separation |
| M2-B8 | Free-text numeric invention for contradictions | Closed — Path A optional; Path B non-semantic |

No residual blocking defect remains against freezing this IRO-M2 architecture
as the implementation target, provided implementation respects §19.

---

## 25. Document authority

- This document is the **canonical IRO-M2 implementation architecture**.
- It freezes architecture derived only from:
  1. Approved Investment Research Orchestrator Architecture
     (`docs/INVESTMENT_RESEARCH_ORCHESTRATOR_ARCHITECTURE.md`);
  2. Frozen IRO-M1 Architecture
     (`docs/iro/IRO_M1_ARCHITECTURE.md`);
  3. Frozen IRO-M1 Implementation
     (package `InvestmentResearchOrchestrator`, tag
     `v6.6-stage5-iro-m1-implementation`).
- It does not redesign those approved/frozen inputs.
- It does not authorize production implementation, commit, tag, or push.
- Subsequent IRO-M2 implementation work must cite this document and must not
  expand beyond its frozen boundary without a new architecture amendment.

---

## 26. Final architecture freeze statement

IRO-M2 is frozen as an **extension of the single package**
`InvestmentResearchOrchestrator` implementing only:

- Operational Memory Comparison (meaningful prior-vs-current store deltas);
- Operational Contradiction Engine (detect + unresolved set + re-research
  requests; consume domain classifiers when applicable; no majority-vote
  truth);
- Bounded Re-research Loop (Planner re-entry, finite budget, human escalation
  markers `WAIT`/`MONITOR`);
- Coordinator/phase/status/store audit extensions required to wire the above;
- Planner input extension for re-research requests;

while preserving:

- IRO-M1 components and empty-scan short-circuit;
- sequential once-per-unit-per-attempt M22 execution;
- append-only evidence;
- Automation M1–M3 isolation;
- permanent exclusion of capital execution.

All EV Engine, CIO Engine, capital allocation, trading, broker integration,
automatic execution, majority-vote truth selection, and semantic invention
remain excluded.

**No residual blocking gap remains against freezing this IRO-M2 architecture
as the implementation target**, subject to separate implementation
authorization.

---

## FINAL DECISION

**IRO-M2 ARCHITECTURE AUTHORED**
