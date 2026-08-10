# Investment Research Orchestrator Architecture

## 1. Status and milestone

- Status: Frozen
- Product: Investment Research Orchestrator (IRO)
- Architecture source of truth: this document
- Architecture review source:
  `/Users/takesimple/JOO-Automation/results/investment_research_orchestrator_architecture_review/20260810_093410_attempt_00.md`
- Review decision: INVESTMENT RESEARCH ORCHESTRATOR ARCHITECTURE APPROVED
- First implementation milestone: **IRO-M1** (not authorized by this document alone)
- Production package: not created by this document; future name must be distinct
  from M22 `ResearchOrchestrator` (for example `InvestmentResearchOrchestrator`)
- Repository boundary: architecture authoring only; no production implementation

This document freezes the canonical JOO architecture for the Investment
Research Orchestrator. It creates no production code, test, package, schema
module, configuration, run artifact, or Git mutation. A separate
implementation authorization is required before IRO-M1 code work begins.

This document does **not** redesign the approved architecture. It freezes the
approved multi-plane, loop-capable operational architecture with the ten named
IRO components, reuse of Stage 1/2 research execution infrastructure, consume-
only use of accepted JOO domain contracts, development via frozen Automation
M1–M3, and permanent exclusion of capital execution.

---

## 2. Purpose

### 2.1 Product definition

**Investment Research Orchestrator (IRO)** is the first **operational**
architecture for JOO’s portfolio-first research lifecycle.

Its objective is to **maximize research quality and improve long-term
investment decisions** by:

1. researching only what can change portfolio expected value;
2. routing work to independent committees with adaptive, frozen prompts;
3. persisting evidence with provenance;
4. detecting contradictions and meaningful memory deltas;
5. estimating thesis-level expected-value impact;
6. producing a **human-reviewable CIO research posture report** — never an
   order.

### 2.2 Explicit non-identity

IRO is **not**:

- a prompt-runner or chat wrapper;
- the existing Stage-1 package `ResearchOrchestrator` (M22 thin
  `ResearchTask` → `PipelineRuntime` boundary);
- Automation-M1/M2/M3 (`joo_auto` development pipeline);
- capital execution, broker integration, portfolio rebalancing, or automatic
  trading.

---

## 3. Scope

### 3.1 In scope (architecture)

This architecture freezes:

- the five-plane model (Development Automation, Human Authority, IRO
  operational, JOO domain-contract, Research execution infrastructure);
- the ten-component IRO lifecycle and ownership boundaries;
- data flow, control loops, state ownership, and provenance rules;
- CIO research-posture vocabulary as research / portfolio-decision postures;
- human authority boundary and fail-closed committee completeness;
- first implementation milestone **IRO-M1** and its exclusions;
- deferred and explicitly rejected responsibilities.

### 3.2 Out of scope (this document and IRO product)

- Automation M1–M3 redesign, import into JOO domain packages, or research
  runtime coupling;
- silent transfer or redefinition of accepted domain package responsibilities;
- capital execution plane (broker, orders, rebalancing, risk sizing as
  execution);
- semantic invention outside accepted JOO contracts;
- production package implementation, schemas as code, or tests in this
  authoring step.

---

## 4. Architectural position inside JOO

IRO is an **operational layer** above frozen domain contracts. JOO
Constitution domain packages remain structural/calculation contracts without
runtime, persistence, or orchestration ownership. IRO **assembles and
coordinates**; domain packages **validate and calculate**.

IRO sits between:

- **above**: Human Authority (approval of material capital-relevant outcomes);
- **beside**: Development Automation (how IRO milestones are built, not how
  research runs);
- **below / beside**: Research execution infrastructure (how one planned task
  runs committees);
- **below**: accepted JOO domain-contract plane (identity, evidence, thesis,
  EV math, portfolio structure).

Capital execution remains a permanently separate, out-of-scope plane.

---

## 5. Relationship to Automation M1–M3

Automation M1–M3 are **development infrastructure** in the independent
`joo_auto` product. They freeze manifests, review/Codex phases, artifacts,
human gates, and (M3) optional local Git mutation for **building JOO**.

| Plane | Owner | Role relative to IRO |
| --- | --- | --- |
| Development Automation | Automation M1–M3 / `joo_auto` | How IRO milestones are designed, implemented, reviewed, and committed |
| Domain contracts | JOO packages | Immutable structural/calculation contracts IRO **consumes** |
| Research execution infrastructure | Committee, ExecutionEngine, AIAdapter, PipelineRuntime, M22 `ResearchOrchestrator` | How one planned task runs committees |
| **Investment Research Orchestrator** | **New operational product boundary** | Full research lifecycle control plane |
| Human authority | Operator | Approval of material capital-relevant outcomes |
| Capital execution | Out of scope | Broker, orders, rebalancing |

**Hard rules**

- Do not redesign or import Automation M1–M3 into JOO domain packages.
- Do not implement investment research inside `joo_auto`.
- IRO milestones must be shippable as ordinary Automation manifests
  (human-authored prompts, path bounds, human gates).
- IRO must not self-approve architecture, product policy, or capital actions.
- IRO must not depend on Automation runtime for research execution.

Development Automation and Investment Research Orchestration are different
products on different planes. Conflating them is a high-severity architectural
defect and is rejected.

---

## 6. Relationship to existing M22 ResearchOrchestrator

### 6.1 What M22 is

M22 `ResearchOrchestrator` is an accepted Stage-1 package. It provides **one
synchronous orchestration boundary** from a validated `ResearchTask` to its
existing `PipelineExecution`. It returns the `PipelineExecutionResult`
produced by the injected `PipelineRuntime` directly.

M22 does not:

- create `ResearchFinding` or `ResearchReport` objects;
- construct adaptive portfolio-scoped prompts;
- scan portfolios or plan multi-subject research programs;
- persist research memory, compare memory, detect operational contradictions;
- assemble expected-value assessments or produce CIO research postures;
- retry, branch, queue multi-task programs, or make portfolio decisions;
- issue BUY, HOLD, or SELL **orders** or allocate capital.

### 6.2 Why IRO does not duplicate M22

IRO and M22 solve different problems:

| Concern | M22 `ResearchOrchestrator` | Investment Research Orchestrator |
| --- | --- | --- |
| Product role | Thin **research-execution** boundary | **Operational research lifecycle** control plane |
| Input scope | One validated `ResearchTask` | Portfolio snapshot + prior IRO baseline + run context |
| Output scope | One `PipelineExecutionResult` | Evidence memory, deltas, EV assembly, CIO research report |
| Prompt ownership | Does not construct prompts | Prompt Planner freezes instance bytes + hash |
| Evidence ownership | None | Collector + append-only Evidence Store |
| Portfolio awareness | None | Portfolio Scanner + Research Planner |
| Multi-task program | None | Ordered task set, skip set, completeness gates |
| Memory / contradiction | None | Operational Memory Comparison + Contradiction Engine |
| EV / CIO | None | Operational EV Engine + CIO Engine |
| Package identity | Frozen name `ResearchOrchestrator` | Distinct product/package name (IRO / e.g. `InvestmentResearchOrchestrator`) |

**IRO owns operational research lifecycle coordination above the execution
layer.** M22 is treated as an existing research-execution capability where
applicable. IRO’s Research Execution Adapter invokes the accepted M22 /
`PipelineRuntime` path **once per planned unit**; it does not reimplement
provider stacks, committee runtime, or pipeline execution.

**Name collision is rejected.** IRO must not replace M22 by silently reusing
the package name `ResearchOrchestrator` for a different product. Future IRO
package naming must remain distinct.

### 6.3 Ownership freeze (execution vs operation)

- **Execution of one planned research unit** (task validation → pipeline run →
  exact result object preservation): owned by M22 + `PipelineRuntime` +
  Stage 1/2 committee/provider stack.
- **Lifecycle of a portfolio-first research run** (scan → plan → route → freeze
  prompts → collect → store → compare → contradict → EV → CIO → human gate):
  owned by IRO.

Responsibilities are not silently transferred from accepted packages into
IRO, and IRO does not reimplement domain math owned by accepted packages.

---

## 7. Layer / plane model

```text
╔══════════════════════════════════════════════════════════════════╗
║  DEVELOPMENT AUTOMATION PLANE (FROZEN — DO NOT MODIFY)           ║
║  Automation-M1 Review │ M2 Pipeline │ M3 Human-Gated Git         ║
║  Package: joo_auto — builds JOO; does not run research           ║
╚══════════════════════════════════════════════════════════════════╝
                              │ ships milestones
                              ▼
╔══════════════════════════════════════════════════════════════════╗
║  HUMAN AUTHORITY PLANE                                           ║
║  Approve material research conclusions / capital-relevant stance ║
║  Override · Hold · Request re-research · Reject                  ║
╚══════════════════════════════════════════════════════════════════╝
                              ▲ CIO report only (no orders)
╔══════════════════════════════════════════════════════════════════╗
║  INVESTMENT RESEARCH ORCHESTRATOR (NEW OPERATIONAL PLANE)        ║
║                                                                  ║
║  ┌─────────────────┐    meaningful deltas                         ║
║  │ Portfolio       │─────────────────────────────────────┐       ║
║  │ Scanner         │                                     │       ║
║  └────────┬────────┘                                     │       ║
║           ▼                                              │       ║
║  ┌─────────────────┐   re-research when confidence low   │       ║
║  │ Research        │◄──────────────┐                     │       ║
║  │ Planner         │               │                     │       ║
║  └────────┬────────┘               │                     │       ║
║           ▼                        │                     │       ║
║  ┌──────────────┐  ┌──────────────┐│                     │       ║
║  │ Committee    │  │ Prompt       ││                     │       ║
║  │ Manager      │  │ Planner      ││                     │       ║
║  └──────┬───────┘  └──────┬───────┘│                     │       ║
║         └────────┬────────┘        │                     │       ║
║                  ▼                 │                     │       ║
║  ┌────────────────────────────────┐│                     │       ║
║  │ Research Execution Adapter     ││  (uses M22 +       │       ║
║  │ → PipelineRuntime/Committees)  ││   Committee stack) │       ║
║  └───────────────┬────────────────┘│                     │       ║
║                  ▼                 │                     │       ║
║  ┌─────────────────┐               │                     │       ║
║  │ Evidence        │               │                     │       ║
║  │ Collector       │               │                     │       ║
║  └────────┬────────┘               │                     │       ║
║           ▼                        │                     │       ║
║  ┌─────────────────┐               │                     │       ║
║  │ Evidence Store  │◄── append-only research memory      │       ║
║  └────────┬────────┘                                     │       ║
║           ├──────────────► Contradiction Engine ─────────┘       ║
║           │                 (ops; triggers planner)              ║
║           ├──────────────► Memory Comparison                     ║
║           │                 (meaningful change only)             ║
║           ▼                                                      ║
║  ┌─────────────────┐                                             ║
║  │ Expected Value  │  thesis impact estimate (no trade)          ║
║  │ Engine (ops)    │                                             ║
║  └────────┬────────┘                                             ║
║           ▼                                                      ║
║  ┌─────────────────┐                                             ║
║  │ CIO Engine      │  HOLD | WAIT | MONITOR |                    ║
║  │                 │  AGGRESSIVE ADD | ADJUST + report           ║
║  └─────────────────┘                                             ║
╚══════════════════════════════════════════════════════════════════╝
                              │ reads / never mutates contracts
                              ▼
╔══════════════════════════════════════════════════════════════════╗
║  DOMAIN CONTRACT PLANE (ACCEPTED — CONSUME ONLY)                 ║
║  Portfolio* · ResearchDomain · Evidence* · Signal/Hypothesis/    ║
║  Thesis* · PortfolioImpact* · ExactExpectedValue* ·              ║
║  Recommendation endpoint · Allocation proposal (separate)        ║
╚══════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════╗
║  RESEARCH EXECUTION INFRASTRUCTURE (STAGE 1/2 — REUSE)           ║
║  Prompt Library · Queue · ExecutionEngine · AIAdapter ·          ║
║  Committee · PipelineRuntime · Logging · Versioning · Replay     ║
╚══════════════════════════════════════════════════════════════════╝

     Capital Execution / Broker / Orders / Rebalancing
     ═══════════════════════════════════════════════
     EXPLICITLY OUT OF SCOPE — never owned by IRO
```

### 7.1 Five planes (normative distinction)

1. **Development Automation plane** — Automation M1–M3 / `joo_auto`; builds
   JOO; does not run investment research.
2. **Human Authority plane** — operator approval, override, hold, re-research
   request, reject; sole authority for capital-relevant action.
3. **Investment Research Orchestrator operational plane** — the ten-component
   lifecycle and run coordination defined here.
4. **Existing JOO domain-contract plane** — accepted immutable structural and
   calculation packages; IRO consumes, never redefines.
5. **Research execution infrastructure** — Stage 1/2 runtime stack including
   M22 `ResearchOrchestrator`; executes one planned unit when IRO delegates.

Capital execution is not a fifth plane of IRO ownership; it is permanently
outside IRO.

---

## 8. Component responsibilities (frozen ten-component lifecycle)

| # | Component | Responsibility | Primary outputs |
| --- | --- | --- | --- |
| 1 | **Portfolio Scanner** | Compare current portfolio observation (holdings, watchlist, constraints, thesis links, prior research coverage) to the **previous IRO run baseline**. Emit only **material subject deltas**. Ignore unchanged subjects. | `ScanDeltaSet` (subjects + change classes + materiality basis) |
| 2 | **Research Planner** | Decide **what research is required** from deltas + open contradictions + confidence gaps. Suppress non-material committee work. Assign priority (holdings → watchlist → competitors → suppliers → customers → sector leaders). | Ordered `ResearchTask` set; explicit skip set with reasons |
| 3 | **Committee Manager** | Map each task to required committees/providers. Allow **different committees to receive different work**. Enforce Committee First completeness (required / completed / failed / missing). Never simulate missing answers. | `CommitteeAssignmentPlan`; completeness gate |
| 4 | **Prompt Planner** | Build **adaptive prompts** from portfolio state + current evidence context. Start from versioned Prompt Library identities; inject only explicit context bindings. **Materialize immutable prompt bytes + hash** per attempt (reproducibility). | Frozen prompt artifacts per committee-task |
| 5 | **Evidence Collector** | Collect **structured outputs** from every committee result without inventing content. Map into `ResearchFinding` / report contracts; record verification and source timestamps. | Structured findings + missing/failed markers |
| 6 | **Evidence Store** | **Append-only** persistence of research artifacts with timestamps and provenance (run_id, task_id, committee, provider, prompt hash, source refs). | Durable research memory; query by subject/run |
| 7 | **Contradiction Engine (operational)** | Detect conflicting evidence using domain classifiers where applicable; escalate **re-research** when confidence is insufficient. Does not silently “resolve” by majority vote. | Contradiction cases; re-research requests; explicit unresolved set |
| 8 | **Memory Comparison** | Diff **today’s** stored evidence against **prior** stored evidence for the same subject/context. Surface only **meaningful** changes (not byte noise). | `MemoryDeltaSet` |
| 9 | **Expected Value Engine (operational)** | Assemble thesis-impact estimation inputs from accepted Portfolio Impact / assumption-set contracts; **delegate** exact math to `ExactExpectedValue`. Estimate effect on **long-term thesis**, not trades. | EV assessment bundle + applicability statuses |
| 10 | **CIO Engine** | Produce final **portfolio research report** and research **stance** recommendations. | Report + per-subject / portfolio stance |

### 8.1 Research Execution Adapter (supporting boundary)

The Research Execution Adapter is the IRO-owned boundary that invokes existing
M22 / `PipelineRuntime` / committee infrastructure for each planned unit. It
is not a substitute for M22 and does not own provider or pipeline internals.
It preserves order and exact response objects; it does not invent missing
committee content.

### 8.2 Cross-cutting responsibilities

- **Run identity**: opaque `run_id`, base portfolio snapshot id, prior-run
  baseline id, UTC timestamps.
- **Append-only history**: never rewrite prior evidence; supersession is
  explicit linkage, not delete.
- **Fail closed**: missing required committee → no CIO synthesis for that
  decision unit.
- **Human-in-the-loop**: IRO recommends; humans authorize capital-relevant
  action.
- **Reproducibility**: same frozen inputs + prompts + committee results → same
  orchestration outcomes (deterministic where pure; LLM content remains
  external evidence, not re-invented by IRO).

### 8.3 Design principles (normative)

1. **Portfolio First** — no broad research without material portfolio EV
   relevance.
2. **Evidence First** — claims require stored, provenance-linked findings.
3. **Committee First** — no CIO synthesis on simulated or missing required
   responses.
4. **Validation-first / immutable domain models** — IRO assembles and
   orchestrates; domain packages validate and calculate.
5. **Append-only research memory**.
6. **Human authority** for capital-relevant outcomes.
7. **Quality over automation volume** — planner may produce zero tasks.
8. **Separation of identity, structure, applicability, semantics,
   calculation, and operation** (JOO Constitution).

---

## 9. Ownership boundaries

| Asset / concern | Owner | Consumer |
| --- | --- | --- |
| Portfolio holdings / snapshot identity | Portfolio domain packages + portfolio data | Portfolio Scanner, Planner, CIO |
| Research task schema | `ResearchDomain` | Planner → execution adapter |
| Prompt template library identity | Prompt Library | Prompt Planner |
| Prompt **instance** bytes for a run | Prompt Planner / IRO run store | Execution, versioning, replay |
| Provider invocation | AIAdapter / ExecutionEngine | Committee runtime |
| Committee completeness structure | Committee aggregate contracts | Committee Manager, CIO gate |
| Numeric comparison / contradiction **candidate** classification | Evidence Comparison / Evidence Contradiction packages | Operational Contradiction Engine |
| Evidence persistence for research ops | **Evidence Store (IRO)** | Memory, Contradiction, CIO |
| Exact EV arithmetic | `ExactExpectedValue` | Operational EV Engine |
| Portfolio Impact structure | Explicit Portfolio Impact packages | EV Engine, CIO |
| Recommendation **endpoint identity** | `PortfolioRecommendationEndpoint` | CIO may link report ids |
| Recommendation **stance semantics** | **CIO Engine (new contract)** | Human gate |
| Allocation quantities / buckets / risk budgets | Stage 5 allocation plane | **Not IRO** |
| Git / review / Codex development runs | Automation M1–M3 | Humans / `joo_auto` |
| Broker / orders | N/A (out of scope) | — |

### 9.1 Relationship to accepted JOO contracts (consume-only)

| Concern | Existing contract (consume) | IRO role |
| --- | --- | --- |
| Research task / finding / report | `ResearchDomain` | Planner output / collector artifacts |
| Thin task execution | M22 `ResearchOrchestrator` + `PipelineRuntime` | Delegate single-task execution only |
| Committees | `Committee` + Committee First Protocol | Route and require completeness; never simulate |
| Numeric evidence / comparison / contradiction candidate | Evidence* packages | Consume classifiers; do not redefine |
| Supersession | `EvidenceSupersession*` | Memory / authority inputs |
| Thesis / impact / EV math | ExplicitThesis, PortfolioImpact*, ExactExpectedValue* | Assemble inputs; delegate calculation |
| Recommendation identity | `PortfolioRecommendationEndpoint` | Link report identity; **not** stance semantics |
| Allocation structure | Stage 5 allocation packages | **Separate plane** — not CIO research stance |

IRO must not collapse multiple domain packages into one “god orchestrator”
that reimplements EV math, evidence comparison, or portfolio identity.

---

## 10. Research lifecycle

### 10.1 Primary path (happy path)

1. Load **current portfolio snapshot** + **prior IRO baseline** from Evidence
   Store / portfolio observation contracts.
2. **Portfolio Scanner** → material `ScanDeltaSet` (empty ⇒ short-circuit: no
   committee work; optional MONITOR-only CIO summary).
3. **Research Planner** → required `ResearchTask[]` + skip reasons.
4. For each task: **Committee Manager** + **Prompt Planner** → assignment +
   frozen prompts.
5. **Research Execution Adapter** invokes existing M22 / `PipelineRuntime`
   path **once per planned unit**; preserves order and exact response objects.
6. **Evidence Collector** → findings; **Evidence Store** appends with
   provenance.
7. **Contradiction Engine** evaluates new vs existing evidence; if re-research
   required → return to Planner with bounded loop budget.
8. **Memory Comparison** → meaningful deltas vs prior store.
9. **Expected Value Engine** → thesis impact estimates via domain calculators.
10. **CIO Engine** → report + stances; stop at **Human Authority Gate**.

### 10.2 Control loops (not a pure linear pipeline)

| Loop | Trigger | Bound |
| --- | --- | --- |
| Contradiction re-research | Unresolved conflict / low confidence | Max re-research depth per run; then escalate WAIT/MONITOR to human |
| Empty scan short-circuit | No material portfolio/memory change | Skip committees; emit “no material research” report |
| Completeness gate | Missing/failed required committee | Block CIO synthesis for that unit; record explicit gaps |

IRO is loop-capable. A pure linear “ten boxes” pipeline without re-research
or short-circuit is rejected.

---

## 11. Data flow

### 11.1 Evidence flow (ownership of facts)

```text
Committee AIResponse (raw, exact)
        → Evidence Collector (structure, no invention)
        → ResearchFinding / ResearchReport
        → Evidence Store (append, timestamp, provenance)
        → [optional later] Semantic Knowledge producer (OUTSIDE first IRO core;
              not free-form → ExactObservedNumericProposition inside Collector)
        → Domain Evidence / Signal / Thesis chain (consume when present)
        → Memory Comparison + Contradiction (ops)
        → EV assembly + CIO report
```

### 11.2 Control data

- Portfolio snapshots and observation contracts feed the Scanner.
- Scan deltas and open contradiction/confidence gaps feed the Planner.
- Frozen prompt artifacts and assignment plans feed the execution adapter.
- Completeness markers and stored findings feed Memory Comparison,
  Contradiction Engine, EV Engine, and CIO Engine.
- CIO report is the sole IRO output to the Human Authority plane for
  capital-relevant posture.

---

## 12. State ownership

| State | Owner |
| --- | --- |
| Mutable live portfolio positions | Human / external portfolio source (IRO reads snapshots) |
| IRO run state machine | IRO orchestrator |
| Append-only evidence history | Evidence Store |
| Frozen domain model instances | Caller-supplied; never mutated by IRO |
| Human approvals | Human Authority records (append-only) |
| Prompt library template identities | Prompt Library (accepted) |
| Frozen prompt instance bytes for a run | Prompt Planner / IRO run store |
| M22 / pipeline execution result objects | Research execution infrastructure (exact preservation) |

IRO owns **run state only**. It does not mutate live portfolio positions or
rewrite historical evidence.

---

## 13. Evidence provenance requirements

Every stored research artifact MUST carry provenance sufficient for audit and
replay of orchestration decisions, including at minimum:

- `run_id`
- `task_id` (when applicable)
- committee identity
- provider identity (when applicable)
- prompt identity and **prompt instance hash**
- source references / collection timestamps
- UTC timestamps for store append events

Evidence Store is **append-only**. Prior records are never rewritten.
Supersession, when applicable, is explicit linkage (consuming accepted
`EvidenceSupersession*` contracts), not delete-in-place.

Collector maps **actual** committee outputs only. It does not invent content
to fill gaps. Missing and failed committees are recorded as explicit markers.

---

## 14. Committee interaction rules

1. **Committee First**: no investment research conclusion for a decision unit
   is based on a single simulated committee answer.
2. Committee Manager maps tasks to required committees/providers and may
   assign **different work to different committees**.
3. Completeness is tracked as required / completed / failed / missing.
4. The system **must not** predict, invent, or simulate missing committee
   answers.
5. Missing or failed **required** committees block CIO synthesis for that
   decision unit (fail closed).
6. Execution of committee work reuses Stage 1/2 infrastructure via the
   Research Execution Adapter and M22 path; IRO does not replace Committee /
   AIAdapter / ExecutionEngine ownership.

---

## 15. Prompt freeze responsibility

**Prompt Planner** owns prompt **instance** materialization for a run:

1. Start from versioned Prompt Library identities (`prompt_id` /
   `prompt_version`).
2. Inject only **explicit** context bindings from portfolio state and evidence
   context (no silent policy rewriting by a live model).
3. Materialize **immutable prompt bytes** and a content hash (for example
   SHA-256) **per attempt**.
4. Persist frozen prompt artifacts with the run for reproducibility, versioning,
   and replay.

Adaptive prompts without freeze/hash are rejected. Prompt Library continues
to own template identity; IRO owns the frozen instance for the run.

---

## 16. Research execution boundary

| Layer | Responsibility |
| --- | --- |
| IRO Research Execution Adapter | Bind planned unit + frozen prompts to accepted execution path; invoke once per planned unit; preserve exact results |
| M22 `ResearchOrchestrator` | Validate `ResearchTask`; delegate to injected `PipelineRuntime` exactly once; return exact result |
| `PipelineRuntime` / Committee / ExecutionEngine / AIAdapter | Stage 1/2 execution ownership unchanged |

IRO must not:

- invent a parallel provider stack for IRO-M1;
- wrap M22 results into synthesized committee answers;
- retry or fan-out beyond the adapter’s authorized behavior for the current
  milestone;
- treat M22 package identity as the IRO product.

---

## 17. Evidence collection responsibility

**Evidence Collector** owns:

- structured collection of every committee result without content invention;
- mapping into accepted `ResearchFinding` / `ResearchReport` (or equivalent
  ResearchDomain) validation contracts;
- recording verification status and source timestamps;
- explicit missing/failed markers.

**Evidence Collector does not own:**

- free-text → `ExactObservedNumericProposition` semantic production (deferred
  outside first IRO core);
- contradiction resolution;
- CIO synthesis;
- mutation of domain evidence packages’ public contracts.

---

## 18. Evidence storage responsibility

**Evidence Store** owns:

- append-only persistence of research artifacts for operational research
  memory;
- timestamps and provenance hashes/fields required by §13;
- queryability by subject/run as needed by Memory Comparison, Contradiction,
  EV, and CIO.

**Evidence Store does not own:**

- live portfolio mutation;
- domain Evidence package redefinition;
- silent overwrite of prior runs;
- capital execution records.

---

## 19. Memory comparison responsibility

**Memory Comparison** owns:

- diffing **today’s** stored evidence against **prior** stored evidence for
  the same subject/context;
- surfacing only **meaningful** changes (not byte noise);
- emitting `MemoryDeltaSet` for planner and CIO awareness.

Full supersession-policy wiring and deep semantic delta materiality may
consume accepted domain contracts later; first architecture freezes the
operational role. IRO-M1 uses only a **minimum stub** (see §33).

---

## 20. Contradiction responsibility

**Operational Contradiction Engine** owns:

- detecting conflicting evidence, using domain classifiers where applicable
  (`EvidenceContradiction` and related packages remain frozen classifiers);
- escalating **re-research** when confidence is insufficient;
- emitting contradiction cases, re-research requests, and an explicit
  unresolved set;
- respecting a **bounded** re-research depth per run, then escalating
  WAIT/MONITOR to human.

It does **not**:

- silently resolve by majority vote;
- perform final “truth selection”;
- reimplement or replace the `EvidenceContradiction` domain package;
- bypass the Research Planner when re-research is required.

---

## 21. Expected Value responsibility

**Operational Expected Value Engine** owns:

- assembling thesis-impact estimation inputs from accepted Portfolio Impact /
  assumption-set contracts;
- **delegating** exact arithmetic to `ExactExpectedValue`;
- estimating effect on **long-term thesis**, not trades;
- emitting EV assessment bundles and applicability statuses.

It does **not**:

- reimplement ExactExpectedValue math;
- produce order tickets, risk sizing for execution, or allocation quantities;
- treat EV output as broker instructions.

---

## 22. CIO responsibility

**CIO Engine** owns:

- final **portfolio research report** production;
- research **stance** recommendations per subject and/or portfolio;
- optional linkage of report identity to
  `PortfolioRecommendationEndpoint` identity fields (identity only, not stance
  semantics);
- stop at the Human Authority Gate (report in; no order out).

CIO does **not** own allocation quantities, buckets, risk budgets, order
routing, or broker calls. Stage 5 allocation proposal plane remains separate
from CIO research stance.

---

## 23. CIO research-posture vocabulary

| Stance | Meaning |
| --- | --- |
| **HOLD** | No material research-driven change to current posture; maintain position thesis as-is pending human review. |
| **WAIT** | Evidence insufficient or catalyst pending; do not act on incomplete research. |
| **MONITOR** | Material watch items; elevate attention without recommending capital change. |
| **AGGRESSIVE ADD** | Research concludes long-term thesis EV improved **enough to warrant human consideration of adding** — still not an order. |
| **ADJUST** | Material thesis/risk/invalidations imply portfolio review (size, structure, or thesis status) — still not an order. |

These stances **must not** be conflated with Stage 5 allocation proposals
(quantities, buckets, risk budgets) or with future broker instructions.

---

## 24. Research postures are not broker instructions

**Normative statement:** HOLD, WAIT, MONITOR, AGGRESSIVE ADD, and ADJUST are
**research / portfolio-decision postures** for human review. They are:

- **not** broker instructions;
- **not** order execution intents;
- **not** BUY/SELL/REBALANCE commands;
- **not** automatic capital allocation;
- **not** substitutes for Stage 5 allocation proposal content.

IRO may generate research, analysis, and recommended postures. Only the human
operator may approve material capital allocation actions, override portfolio
rules, or authorize execution. Execution of capital actions is outside IRO.

---

## 25. Human authority boundary

Human Authority plane owns:

- approval of material research conclusions and capital-relevant stance;
- override;
- hold;
- request re-research;
- reject.

IRO:

- stops at the Human Authority Gate after CIO report emission;
- must not self-approve architecture, product policy, or capital actions;
- must not bypass human authority for capital-relevant recommendations;
- may record human decisions as append-only authority records when that
  recording surface is later implemented (not required for IRO-M1).

---

## 26. Failure behavior

| Failure class | Behavior |
| --- | --- |
| Missing/failed required committee | Completeness gate blocks CIO synthesis for that decision unit; record explicit gaps |
| Validation failure on accepted domain inputs | Propagate / fail closed; do not invent corrected content |
| Execution adapter / M22 / pipeline exception | Preserve exception semantics of the execution layer; do not synthesize success results |
| Unresolved contradiction after depth budget | Escalate WAIT/MONITOR (or equivalent incomplete posture) to human; do not majority-vote |
| Empty material scan | Short-circuit: no committee work; “no material research” / optional MONITOR-only summary |
| Incomplete evidence for EV assembly | Record applicability / absence; do not fabricate EV |

Fail closed is the default for capital-relevant synthesis under incomplete
required committees.

---

## 27. Absence semantics

Absence is first-class:

- **No material scan delta** means no committee work is required, not that
  research “succeeded with empty invention.”
- **Missing required committee** means incomplete; not fillable by simulation.
- **No prior baseline** / no prior findings (Memory Comparison) must be
  represented explicitly (presence/absence), not as silent equality.
- **Unresolved contradiction** remains in an explicit unresolved set.
- **Inapplicable EV assembly** is reported as applicability status, not as a
  zero-impact trade signal.

Planner may produce an **empty task set with reasons**. Quality over volume.

---

## 28. Re-run / retry semantics

- Contradiction-driven re-research returns to **Research Planner** with a
  **bounded** re-research depth per run.
- Exceeding depth escalates to human (WAIT/MONITOR), not unbounded looping.
- Retry of external LLM content is not an excuse to rewrite frozen prompt
  policy or to invent missing committees.
- Re-runs create new append-only evidence; they do not rewrite prior store
  records.
- M22 itself does not own IRO-level multi-task retry policy; IRO owns run-
  level loop budgets.

Detailed attempt/run state schemas are implementation concerns under
authorized milestones; architecture freezes the bounded-loop rule.

---

## 29. Auditability and provenance

IRO must support audit of:

- which portfolio snapshot and prior baseline a run used;
- which subjects were researched or skipped and why;
- which committees were required, completed, failed, or missing;
- which prompt instance bytes/hashes were executed;
- which raw/structured findings were stored when;
- which contradictions and memory deltas were raised;
- which EV assemblies and CIO stances were produced;
- that no capital order was emitted by IRO.

Append-only Evidence Store + frozen prompt artifacts + run identity form the
minimum audit substrate. Development Automation audit (manifests, Git) is a
separate plane.

---

## 30. Compatibility with existing JOO contracts

- IRO **consumes** accepted domain public contracts; it does not redesign them
  for IRO-M1.
- M22 `ResearchOrchestrator`, `PipelineRuntime`, Committee, AIAdapter,
  ExecutionEngine, Prompt Library, ResearchDomain, Evidence*, Thesis*,
  Portfolio*, ExactExpectedValue*, and Stage 5 allocation packages retain
  their accepted meanings.
- Recommendation **endpoint identity** remains separate from CIO **stance
  semantics**.
- Allocation proposal structure remains a separate plane from research
  posture.
- No JOO domain package import of `joo_auto` for research execution.
- No silent transfer of responsibilities from accepted packages into IRO
  “god” logic.

---

## 31. Deferred responsibilities

These are intentionally not first-architecture implementation targets:

1. Semantic production from free-text committee output →
   `ExactObservedNumericProposition` (Knowledge/Semantic producer; separate
   boundary).
2. Full Signal → Hypothesis → Thesis **authoring** automation (structural
   chain exists; operational production is later).
3. Learning Engine (prompt improvement from outcomes) — Stage 6; may **read**
   IRO history later, not rewrite rules autonomously.
4. Dashboard / UI.
5. Scheduling / multi-tenant SaaS runtime.
6. Parallel committee execution / async fan-out (sequential reuse of existing
   runtime first).
7. Portfolio allocation proposal generation and constraint evaluation (Stage 5
   plane; separate from CIO stance).
8. Risk sizing, order tickets, broker APIs.
9. News scraping implementation.
10. Automatic entity/ticker resolution beyond caller-supplied portfolio
    identities.
11. Final “truth selection” / contradiction **resolution** (only detection +
    re-research + human escalation).
12. Redesign of Automation M1–M3 or of accepted domain public contracts.

Illustrative later milestones after IRO-M1:

- **IRO-M2** — Memory + Contradiction loop (beyond M1 stub);
- **IRO-M3** — EV assembly;
- **IRO-M4** — CIO report + human gate records.

---

## 32. Explicitly rejected responsibilities

IRO **must never**:

- execute trades, route orders, rebalance, or call brokers;
- issue BUY/SELL **orders** or treat stances as executable instructions;
- simulate, invent, or fill missing committee responses;
- collapse multiple domain packages into one orchestrator that reimplements
  EV math, evidence comparison, or portfolio identity;
- live inside `joo_auto` or depend on Automation runtime for research
  execution;
- mutate Git history or approve its own milestones;
- rewrite append-only evidence;
- predict prices as a primary objective;
- perform risk sizing implementation for execution;
- bypass human authority for capital-relevant recommendations;
- replace M22 `ResearchOrchestrator` by silently reusing its package name for
  a different product (name collision rejected);
- implement investment research inside Development Automation;
- redesign Automation M1–M3 as part of IRO work.

---

## 33. Long-term scalability

- Keep the **Research Execution Adapter** swappable so later parallel/schedule
  execution can be introduced without redesigning domain contracts.
- First path is **sequential** reuse of existing Stage 1/2 runtime.
- Planner skip sets + scanner gates + priority order control committee cost.
- Append-only memory and frozen prompts support replay and audit at scale.
- Dual-plane stance vs allocation keeps research scale independent of
  execution/broker integration timelines.
- Development Automation remains the substrate for shipping IRO milestones,
  not for running research.

---

## 34. First implementation boundary (IRO-M1)

**Architecture is frozen by this document. Implementation requires separate
authorization.**

### 34.1 IRO-M1 may include only

1. **Explicit IRO run contract**: `run_id`, portfolio snapshot id, prior
   baseline id, phase enum, terminal statuses.
2. **Portfolio Scanner (M1)**: detect subject-level membership/holding
   observation changes vs prior baseline only; emit skip-for-unchanged.
3. **Research Planner (M1)**: convert scan deltas to `ResearchTask` list **or**
   empty plan with reasons; no free-form “research everything.”
4. **Committee Manager (M1)**: static allowlisted routing table
   task-type → required committees; completeness checklist structure.
5. **Prompt Planner (M1)**: bind existing Prompt Library `prompt_id` /
   `prompt_version` + explicit context fields; write frozen prompt bytes +
   hash to run-local store (no live model rewriting of policy).
6. **Execution adapter**: call existing M22 `ResearchOrchestrator` / pipeline
   path only; no new provider stack.
7. **Evidence Collector (M1)**: map actual committee responses into
   `ResearchFinding` / `ResearchReport` validation contracts; mark
   missing/failed.
8. **Evidence Store (M1)**: append-only run-local (or agreed path) JSONL/files
   with timestamps and provenance hashes.
9. **Memory Comparison (stub)**: prior-run findings presence/absence +
   statement-identity inequality only (minimum stub required to identify prior
   evidence context).
10. **Tests** (when implementation is authorized): unit tests for scan skip,
    empty plan, completeness block, append-only store, prompt freeze hash.
11. **README / package boundary docs** for the future IRO package (name
    distinct from `ResearchOrchestrator`).

### 34.2 IRO-M1 must not include

- full contradiction-resolution loop;
- Expected Value calculation implementation / full ExactExpectedValue end-to-
  end wiring;
- CIO decision implementation / final report and stance enum enforcement as
  production decision engine;
- automatic capital allocation;
- portfolio rebalancing;
- broker integration;
- order routing;
- buy/sell execution;
- autonomous trading;
- semantic invention outside accepted JOO contracts;
- semantic numeric extraction;
- allocation proposals;
- scheduling, dashboard, Learning Engine;
- parallel execution;
- any Automation M1–M3 code change;
- redesign of accepted domain public contracts.

### 34.3 Naming freeze

| Name | Meaning |
| --- | --- |
| Investment Research Orchestrator (IRO) | This product architecture |
| `ResearchOrchestrator` (package) | Frozen M22 thin execution boundary — **unchanged** |
| Operational Contradiction Engine | IRO component |
| `EvidenceContradiction` package | Frozen pairwise candidate classifier — **unchanged** |
| Operational Expected Value Engine | IRO assembly/orchestration |
| `ExactExpectedValue` package | Frozen calculator — **unchanged** |

---

## 35. Risks and closed defects (architecture)

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Conflating Development Automation with Research Orchestration | High | Separate planes; no JOO domain imports of `joo_auto`; distinct product names |
| Name collision with M22 `ResearchOrchestrator` | High | Product name IRO; package later e.g. `InvestmentResearchOrchestrator` |
| Evidence Collector overclaiming semantic numeric evidence | High | Collector stops at ResearchFinding; semantic producer deferred |
| Unbounded contradiction re-research loops | High | Explicit depth budget; escalate WAIT/MONITOR |
| Adaptive prompts breaking reproducibility | High | Materialize prompt bytes + hash per attempt; store with run |
| CIO stance confused with allocation/execution | High | Stance enum separate from allocation proposal content |
| Portfolio Scanner “meaningful change” undefined | Medium | First boundary: identity/membership/quantity observation deltas + explicit materiality policy inputs; later ExactNumericDeltaMateriality |
| Committee cost explosion | Medium | Planner skip set + scanner gate + priority order |
| Premature CIO synthesis on incomplete committees | Medium | Hard completeness gate |
| Sequential multi-committee scale | Medium | Swappable execution adapter; first path sequential |

Under this architecture the following naive defects are **closed by design**:

| ID | Defect if left unaddressed | Status |
| --- | --- | --- |
| B1 | Treating Automation M1–M3 as research runtime | Closed — development plane only |
| B2 | Overwriting M22 `ResearchOrchestrator` meaning | Closed — distinct product/package name |
| B3 | Evidence Collector as semantic numeric producer | Closed — deferred; findings-only first |
| B4 | Pure linear pipeline (no re-research / short-circuit) | Closed — loops + empty-scan path |
| B5 | CIO stance = trade execution | Closed — research posture + human gate |
| B6 | Reimplementing ExactExpectedValue / EvidenceContradiction | Closed — consume-only domain ownership |
| B7 | Adaptive prompts without freeze/hash | Closed — materialize immutable prompt artifacts |

No residual blocking defect remains against freezing this first IRO
architecture as the implementation target, provided IRO-M1 respects §34.

---

## 36. Implementation prerequisites (not satisfied by architecture alone)

Before any **implementation** PR:

1. This frozen architecture document under `docs/` (this file) is the
   canonical target.
2. Reserve a package name distinct from `ResearchOrchestrator`.
3. Define normative schemas for: `ScanDeltaSet`, IRO run phases, CIO stance
   enum, re-research budget, prompt freeze artifact (in authorized
   implementation milestones).
4. Keep Automation M1–M3 docs and `joo_auto` untouched for IRO work.
5. Do not begin Signal/Hypothesis/Thesis **semantic production** inside
   IRO-M1.
6. Do not change accepted domain public contracts for IRO-M1.

No architecture redesign of M1–M3 is required. No domain public contract
change is required for IRO-M1.

---

## 37. Document authority

- This document is the **canonical JOO architecture document** for the
  Investment Research Orchestrator.
- It freezes the architecture approved by the independent architecture review
  dated attempt `20260810_093410_attempt_00`.
- It does not authorize production implementation, commit, tag, or push.
- Subsequent IRO implementation milestones must cite this document and must
  not expand beyond their authorized milestone boundaries without a new
  architecture amendment.
