# Investment Research Orchestrator (IRO-M1)

## Purpose

`InvestmentResearchOrchestrator` is the first implementable slice of the
Investment Research Orchestrator operational plane (IRO-M1).

It coordinates a **portfolio-first, sequential research run** that:

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

Architecture source of truth: `docs/iro/IRO_M1_ARCHITECTURE.md`.

## Package identity

| Name | Role |
| --- | --- |
| `InvestmentResearchOrchestrator` | **Only** IRO-M1 production package name |
| `ResearchOrchestrator` | Frozen M22 package — **unchanged**, not the IRO product |

IRO-M1 is **not** M22, not Stage-1 `ResearchPlanner/`, not Automation M1–M3,
and not capital execution.

## Public layout

```text
InvestmentResearchOrchestrator/
  models/
  validation/
  scanner.py
  planner.py
  committee_manager.py
  prompt_planner.py
  execution_adapter.py
  evidence_collector.py
  evidence_store.py
  memory_comparison_stub.py
  run_coordinator.py
  README.md
  tests/
```

## Public API (M1)

| Component | Entry |
| --- | --- |
| Run contract | `IRORun`, `IRORunPhase`, `IRORunStatus` + `validate_iro_run` |
| Portfolio Scanner | `PortfolioScanner.scan(...)` → `ScanDeltaSet` |
| Research Planner | `ResearchPlanner.plan(...)` → `ResearchPlan` |
| Static Committee Router | `StaticCommitteeRouter.route(...)` → `CommitteeAssignmentPlan` |
| Prompt Freeze | `PromptFreeze.freeze(...)` / `verify_hash(...)` |
| M22 Adapter | `M22Adapter.execute(...)` → `ExecutionRecord` |
| Evidence Collector | `EvidenceCollector.collect(...)` → `CollectedEvidence` |
| Evidence Store | `EvidenceStore.append` / `list_for_run` (append-only JSONL) |
| Memory Stub | `MemoryComparisonStub.compare(...)` → `MemoryDeltaSet` |
| Run Coordinator | `RunCoordinator.run(...)` → `IRORunResult` |

## Run lifecycle

Linear happy path:

```text
INITIALIZED → SCANNED → PLANNED → ROUTED → PROMPTS_FROZEN
  → EXECUTED → COLLECTED → STORED → MEMORY_COMPARED → COMPLETED
```

Empty material scan short-circuit:

```text
INITIALIZED → SCANNED → SHORT_CIRCUITED_NO_MATERIAL_DELTA
```

Failure:

```text
any phase → FAILED
```

## Dependency injection

- M22: inject `ResearchOrchestrator` (with its injected `PipelineRuntime` chain).
- Routing: inject `StaticRoutingTable` (`task_type → committees`).
- Store: inject filesystem root path for run-local JSONL.
- Templates / bindings / providers: caller-supplied per committee.
- Collection: optional `CollectionBinding` for non-defaultable finding fields.

Domain packages are **consume-only**. IRO-M1 does not redesign their public
contracts.

## Allowed dependencies (consume / inject)

- `ResearchDomain` (`ResearchTask`, `ResearchFinding`, `ResearchReport`)
- `ResearchOrchestrator` (M22) — once per planned unit
- `PipelineRuntime` / `Committee` / `AIAdapter` models as pipeline assembly fields
- Portfolio snapshot family (`ExplicitPortfolioSnapshot` and nested contracts)
- Python stdlib (filesystem JSONL, hashing, UTC timestamps, unittest)

## Explicit non-responsibilities (M1)

IRO-M1 does **not**:

- compute Expected Value or wire `ExactExpectedValue`
- run a CIO Engine or produce capital postures as orders
- operate a Contradiction Engine or re-research loop
- trade, rebalance, call brokers, or size risk for execution
- perform adaptive routing, dynamic AI prioritization, or live prompt policy rewrite
- invent missing committee answers or semantic free-text → numeric propositions
- mutate live portfolio state or rewrite append-only evidence
- depend on Automation / `joo_auto` at research runtime
- replace or rename M22 `ResearchOrchestrator`
- implement competitor / supplier / customer / sector expansion scan classes

## Invariants

1. Portfolio First (structural scan) — empty deltas short-circuit.
2. Evidence First — findings from actual results + explicit bindings only.
3. Committee First structure — required / completed / failed / missing recorded.
4. Validation-first — type / nonblank / enum only; no identity normalization.
5. Append-only research memory.
6. Prompt freeze (bytes + SHA-256) before execution.
7. Exact M22 result preservation; one sequential execution per planned unit.
8. Baseline absence is first-class (not silent equality with empty).
9. Static routing only; unknown `task_type` fails closed.
10. Development plane isolation from Automation.
