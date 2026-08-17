# Investment Research Orchestrator (IRO-M1 + IRO-M2)

## Purpose

`InvestmentResearchOrchestrator` is the operational Investment Research
Orchestrator package. IRO-M1 coordinates a portfolio-first sequential
research run. IRO-M2 is an additive same-package extension that adds three
and only three new operational responsibilities:

1. **Operational Memory Comparison** — structured prior-vs-current store
   diffs;
2. **Operational Contradiction Engine** — Path B exact-statement conflicts
   and optional Path A numeric candidate classification;
3. **Bounded re-research** — finite per-run admissions back through the
   Research Planner, then escalate to human review.

Architecture sources of truth:

- `docs/iro/IRO_M1_ARCHITECTURE.md`
- `docs/iro/IRO_M2_ARCHITECTURE.md`

## Package identity

| Name | Role |
| --- | --- |
| `InvestmentResearchOrchestrator` | **Only** IRO production package name |
| `ResearchOrchestrator` | Frozen M22 package — **unchanged**, not the IRO product |

IRO is **not** M22, not Stage-1 `ResearchPlanner/`, not Automation M1–M3,
not PortfolioSnapshotProducer, not ProviderGateway, not FactStore, not
MarketSnapshotProducer, and not capital execution.

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
  memory_comparison_stub.py   # historical M1 stub
  memory_comparison.py        # M2 operational comparison
  contradiction_engine.py     # M2 contradiction engine
  re_research.py              # M2 budget + admission helpers
  run_coordinator.py
  README.md
  tests/
```

## Public API

| Component | Entry |
| --- | --- |
| Run contract | `IRORun`, `IRORunPhase`, `IRORunStatus` + `validate_iro_run` |
| Portfolio Scanner | `PortfolioScanner.scan(...)` → `ScanDeltaSet` |
| Research Planner | `ResearchPlanner.plan(...)` and `plan_re_research(...)` |
| Static Committee Router | `StaticCommitteeRouter.route(...)` |
| Prompt Freeze | `PromptFreeze.freeze(...)` / `verify_hash(...)` |
| M22 Adapter | `M22Adapter.execute(...)` → `ExecutionRecord` |
| Evidence Collector | `EvidenceCollector.collect(...)` |
| Evidence Store | `EvidenceStore.append` / `list_for_run` (append-only JSONL) |
| Memory Stub | `MemoryComparisonStub.compare(...)` (historical) |
| Memory Comparison | `MemoryComparison.compare(...)` → `MemoryDeltaSet` |
| Contradiction Engine | `ContradictionEngine.evaluate(...)` → `ContradictionEvaluation` |
| Re-research helpers | `make_re_research_budget`, `should_admit_re_research`, `is_exact_non_progress` |
| Run Coordinator | `RunCoordinator.run(...)` → `IRORunResult` |

`IRORunResult` keeps the M1 fields and additively exposes
`re_research_attempt`, `budget`, `contradiction`, and `escalation`.

## Run lifecycle

Linear happy path (no re-research):

```text
INITIALIZED → SCANNED → PLANNED → ROUTED → PROMPTS_FROZEN
  → EXECUTED → COLLECTED → STORED → MEMORY_COMPARED
  → CONTRADICTION_EVALUATED → COMPLETED
```

Empty material scan short-circuit:

```text
INITIALIZED → SCANNED → SHORT_CIRCUITED_NO_MATERIAL_DELTA
```

Re-research (budget remaining and progress):

```text
CONTRADICTION_EVALUATED → RE_RESEARCH_ADMITTED → PLANNED
  → ROUTED → PROMPTS_FROZEN → EXECUTED → COLLECTED → STORED
  → MEMORY_COMPARED → CONTRADICTION_EVALUATED
```

Budget exhausted / exact non-progress / unplanable requests:

```text
CONTRADICTION_EVALUATED → ESCALATED_HUMAN_REVIEW
```

Failure:

```text
any phase → FAILED
```

## M2 operational rules

- Statement equality is exact. No trim, case-fold, paraphrase, or embedding.
- Memory Comparison never synthesizes `UNCHANGED` on invalid input.
- Contradiction Engine does not select truth, vote, or call M22.
- Path A consumes only caller-supplied
  `ExactObservedNumericProposition` pairs via
  `EvidenceContradiction.classify_exact_observed_numeric_contradiction_candidate`.
- Initial wave `attempt=0` does not consume re-research budget.
- Each admitted re-research wave consumes exactly one remaining unit.
- Exact non-progress (identical unresolved case-id set and reason codes)
  escalates immediately without consuming remaining budget.
- Empty admitted re-research plan escalates `UNPLANABLE_REQUESTS` without
  executing M22.
- Re-research `research_id` family:
  `{run_id}:attempt:{attempt}:unit:{index}:{subject_id}`.
- Prompt freeze `attempt_index >= 0`. Each wave materializes a new freeze.

## Dependency injection

- M22: inject `ResearchOrchestrator`.
- Routing: inject `StaticRoutingTable`.
- Store: inject filesystem root path.
- Templates / bindings / providers: caller-supplied per committee.
- Collection: optional `CollectionBinding`.
- M2: inject `MemoryComparison`, `ContradictionEngine`, and
  `ReResearchBudget`.
- Optional Path A pairs: caller-supplied on `RunCoordinator.run`.

## Allowed production dependencies

- `ResearchDomain`, injected `ResearchOrchestrator` / `PipelineRuntime`
- Committee / AIAdapter models as pipeline assembly fields
- Portfolio snapshot family (`ExplicitPortfolioSnapshot`)
- `EvidenceContradiction` / `EvidenceProposition` for optional Path A
- Python stdlib

## Forbidden production dependencies

IRO-M2 production code must **not** import or call:

- `ProviderGateway`
- `FactStore`
- `PortfolioSnapshotProducer`
- `MarketSnapshotProducer` / `Market*`
- Automation / `joo_auto`

## Explicit non-responsibilities

IRO does **not**:

- compute Expected Value or wire `ExactExpectedValue`
- run a CIO Engine or emit capital postures as orders
- trade, rebalance, call brokers, or size risk for execution
- perform majority-vote or LLM-as-judge truth selection
- invent missing committee answers or free-text numeric propositions
- own snapshot production, FactStore persistence, or market HTTP
- operate PF-M5 Market Watch, Automation scheduling, or polling
- mutate live portfolio state or rewrite append-only evidence
- replace or rename M22 `ResearchOrchestrator`
- own the Human Approval product surface. IRO-M2 may only emit
  `ESCALATED_HUMAN_REVIEW` together with `WAIT` or `MONITOR`
  markers. Those markers are not a Human Approval product
  implementation
- rewrite or own the frozen architecture documents
  `docs/iro/IRO_M1_ARCHITECTURE.md` and
  `docs/iro/IRO_M2_ARCHITECTURE.md`

## Invariants

1. Portfolio First (structural scan) — empty deltas short-circuit.
2. Evidence First — findings from actual results + explicit bindings only.
3. Committee First structure — required / completed / failed / missing recorded.
4. Validation-first — type / nonblank / enum / range only; first failure wins.
5. Append-only research memory, including M2 audit kinds.
6. Prompt freeze (bytes + SHA-256) before each attempt's execution.
7. Exact M22 result preservation; one sequential execution per planned unit
   per attempt.
8. Baseline absence is first-class.
9. Static routing only; unknown `task_type` fails closed.
10. Unresolved contradictions remain explicit.
11. Re-research is finite and Planner-mediated.
12. Development plane isolation from Automation.
