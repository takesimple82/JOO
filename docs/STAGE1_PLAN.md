# Stage 1 — Research Layer Implementation Plan

## 1. Goal

Stage 1 builds a reproducible, portfolio-driven research system that collects, validates, versions, and stores research from multiple AI committees.

The resulting Research Layer must turn portfolio priorities into traceable research tasks and preserve the inputs, outputs, execution context, and validation results required to reproduce each run.

## 2. Scope

### Included

- Portfolio Database input
- Research Planner
- External AI integration
- Committee Layer
- Research Engine
- Prompt Library
- Research Queue
- Research Logging
- Versioning
- Replay
- Validation

### Excluded

- Knowledge Engine
- Thesis Engine
- CIO Engine
- Dashboard
- Learning Engine

## 3. Milestones

### M1 — Prompt Library

#### Objective

Establish standardized, reusable, and versioned prompts for research tasks.

#### Deliverables

- Prompt directory and naming convention
- Prompt ID
- Prompt Version
- Prompt Hash
- Prompt metadata
- Prompt template content
- Initial research prompt set
- Prompt validation rules

Prompt ID identifies the logical prompt. Prompt Version identifies a specific revision. Prompt Hash verifies the exact prompt content used during execution.

#### Exit Criteria

- Prompts follow one documented format.
- Every prompt has a Prompt ID, Prompt Version, and Prompt Hash.
- Prompt hashes are deterministically generated from the stored prompt content.
- A research run can reference the exact prompt revision it used.
- Required variables and metadata can be validated.
- The initial prompt set passes validation.

#### Dependencies

- Stage 0 repository conventions
- Portfolio research requirements

### M2 — Portfolio Research Planner

#### Objective

Convert portfolio holdings, watchlists, constraints, objectives, and priorities into focused research tasks.

#### Deliverables

- Portfolio input contract
- Research prioritization rules
- Research task schema
- Planner output format
- Rules that reject irrelevant research

#### Exit Criteria

- Valid portfolio inputs produce prioritized research tasks.
- Every task links to a portfolio priority.
- Research outside portfolio relevance rules is rejected.
- Planner output conforms to the task schema.

#### Dependencies

- M1 — Prompt Library
- Available Portfolio Database input

### M3 — AI Adapter Layer

#### Objective

Provide a consistent interface for requesting and receiving independent research from supported external AI systems.

#### Deliverables

- Common AI adapter contract
- ChatGPT adapter
- Claude adapter
- Gemini adapter
- Grok adapter
- Perplexity adapter
- Request and response formats
- Timeout and error handling
- Provider response metadata

#### Exit Criteria

- Each supported provider uses the common contract.
- ChatGPT, Claude, Gemini, Grok, and Perplexity are represented by explicit adapters.
- Unsupported providers are outside the Stage 1 scope.
- Missing or unavailable provider responses are recorded without simulation.
- Raw provider outputs are returned without simulated content.
- Missing and failed responses are explicitly identified.
- Adapter behavior is covered by repeatable validation.

#### Dependencies

- M1 — Prompt Library
- Research task schema from M2

### M4 — Committee Layer

#### Objective

Collect and compare actual research outputs from multiple AI systems without inventing missing responses.

#### Deliverables

- Committee request format
- Committee response collection
- Missing-response representation
- Output comparison format
- Committee completeness rules

#### Exit Criteria

- Multiple independent AI outputs can be collected for one task.
- Each output retains its provider identity and metadata.
- Missing committee responses are clearly recorded.
- No missing response is predicted, invented, or simulated.

#### Dependencies

- M3 — AI Adapter Layer

### M5 — Research Queue

#### Objective

Manage prioritized research tasks through a defined and observable execution lifecycle.

#### Deliverables

- Queue record schema containing at least:
  - `task_id`
  - `priority`
  - `portfolio_entity`
  - `portfolio_relevance`
  - `committee_required`
  - `prompt_id`
  - `prompt_version`
  - `status`
  - `created_at`
  - `updated_at`
- Priority and ordering rules
- Task lifecycle states
- Retry eligibility rules
- Queue inspection interface

`task_id` uniquely identifies the research task. `priority` is derived from Portfolio Research Planner rules. `portfolio_entity` identifies the holding, watchlist company, competitor, supplier, customer, or sector leader connected to the task. `portfolio_relevance` explains why the task may affect portfolio expected value. `committee_required` identifies the required AI committee members. `status` must use a documented lifecycle state.

#### Exit Criteria

- Tasks enter the queue with deterministic priority.
- Every queued task contains all required queue fields.
- Queue records without portfolio relevance are rejected.
- Required committee members and prompt references are preserved.
- Every task has a valid lifecycle state.
- State transitions are validated and observable.
- Failed tasks remain identifiable for review or retry.

#### Dependencies

- Research task schema from M2
- Committee request format from M4

### M6 — Research Execution Engine

#### Objective

Execute queued committee research tasks consistently while preserving inputs, outputs, and execution context.

#### Deliverables

- Research execution workflow
- Queue-to-committee orchestration
- Execution configuration
- Success and failure handling
- Research result format

#### Exit Criteria

- A queued task can complete the defined research workflow.
- Successful runs preserve all actual committee outputs.
- Failed runs do not produce false completion states.
- Execution results conform to the documented format.

#### Dependencies

- M4 — Committee Layer
- M5 — Research Queue

### M7 — Research Logging

#### Objective

Create an append-only record of every research execution and its outcome.

#### Deliverables

- Research event types
- Execution logging integration
- Success, failure, and validation events
- Correlation identifiers
- Log validation checks

#### Exit Criteria

- Every execution produces the required events.
- Events link to the relevant task and execution.
- Logs use valid append-only records.
- Successful and failed executions are distinguishable.

#### Dependencies

- M6 — Research Execution Engine
- Stage 0 event logging foundation

### M8 — Research Versioning

#### Objective

Version all artifacts needed to identify and reproduce a research run.

#### Deliverables

- Research version identifier
- Versioned input and prompt references
- Versioned configuration and output records
- Immutable run manifest preserving `prompt_id`, `prompt_version`, and `prompt_hash`
- Version lookup convention

#### Exit Criteria

- Every completed run has a unique version identifier.
- Inputs, prompts, configuration, and outputs are linked by the run manifest.
- A run manifest resolves to the exact prompt content used for that run.
- Prompt identity and integrity can be verified during replay.
- Prior versions remain available and unchanged.
- A version can be resolved without ambiguity.

#### Dependencies

- M1 — Prompt Library
- M6 — Research Execution Engine
- M7 — Research Logging

### M9 — Replay & Validation

#### Objective

Replay versioned research runs and validate their structure, provenance, completeness, and reproducibility.

#### Deliverables

- Replay command or workflow
- Research artifact validators
- Committee completeness validation
- Replay comparison report
- Validation result records

#### Exit Criteria

- A stored run can be replayed from its manifest.
- Required research artifacts pass schema validation.
- Committee outputs and missing responses are preserved correctly.
- Replay differences are reported explicitly.
- Validation results are logged.

#### Dependencies

- M8 — Research Versioning
- M7 — Research Logging

### M10 — Stage Review

#### Objective

Confirm that Stage 1 satisfies its scope, deliverables, governance rules, and Definition of Done.

#### Deliverables

- Stage validation report
- Milestone exit-criteria checklist
- End-to-end research demonstration
- Open-issue and backlog record
- Stage approval record
- Lessons Learned record capturing:
  - What worked
  - What failed
  - What should be retained
  - What should change in the next stage
  - Unresolved technical debt
  - Deferred backlog items

#### Exit Criteria

- All prior milestone exit criteria are satisfied.
- The end-to-end research workflow passes validation.
- Stage 1 Definition of Done is verified.
- Out-of-scope requests are recorded in the backlog.
- Lessons Learned are documented before Stage 1 approval.
- Technical debt and deferred items are explicitly recorded.
- Lessons Learned do not automatically modify the approved product roadmap.
- Stage review is approved.

#### Dependencies

- M1 through M9 complete and approved

## 4. Deliverables

Stage 1 produces:

- A standardized, versioned Prompt Library
- A Portfolio Research Planner and portfolio input contract
- A research task schema and prioritization rules
- A common External AI adapter interface and supported adapters
- A Committee Layer that preserves actual and missing responses
- A prioritized Research Queue with observable lifecycle states
- A Research Execution Engine and documented result format
- Append-only research execution logs and event definitions
- Immutable research run manifests and versioned artifacts
- A replay workflow and research validators
- Replay comparison and validation reports
- A Stage 1 validation and approval record

## 5. Definition of Done

Stage 1 is complete only if:

- Research is reproducible.
- Research is versioned.
- Committee outputs are preserved.
- Portfolio priorities drive research.
- Research can be replayed.
- All executions are logged.
- Validation passes.

## 6. Out of Scope

The following capabilities are intentionally postponed to Stage 2 or later:

- Knowledge normalization and durable knowledge management
- Investment thesis creation and lifecycle management
- Portfolio-level capital allocation recommendations
- CIO synthesis and decision workflows
- Human approval workflows for material portfolio actions
- User-facing operational dashboards
- Outcome-based learning and automated improvement
- Capital execution and autonomous trading

Stage 1 may preserve research artifacts for later use, but it does not implement these capabilities.

## 7. Stage Governance

- Every task must belong to one milestone.
- Milestones must be approved before coding.
- Exit Criteria must be satisfied before the next milestone begins.
- Features outside Stage 1 go to the backlog.

### Milestone Branch Strategy

- Each implementation milestone uses its own Git branch.
- Branch format: `feature/stage1-m<NUMBER>-<SHORT-NAME>`
- Approved branch names:
  - `feature/stage1-m1-prompt-library`
  - `feature/stage1-m2-research-planner`
  - `feature/stage1-m3-ai-adapter`
  - `feature/stage1-m4-committee-layer`
  - `feature/stage1-m5-research-queue`
  - `feature/stage1-m6-execution-engine`
  - `feature/stage1-m7-research-logging`
  - `feature/stage1-m8-research-versioning`
  - `feature/stage1-m9-replay-validation`
  - `feature/stage1-m10-stage-review`
- A milestone branch must begin from the latest approved Stage 1 baseline.
- Only work belonging to that milestone may be committed to its branch.
- Review findings must be resolved before the milestone is approved.
- The milestone must satisfy its Exit Criteria before merge.
- Unrelated features must be moved to the backlog.
- Do not begin the next milestone before the current milestone is approved and merged unless the dependency plan explicitly permits parallel work.

#### Milestone Development Cycle

Plan  
→ Create Branch  
→ Implement  
→ Test  
→ Review  
→ Fix  
→ Approve  
→ Commit  
→ Merge  
→ Begin Next Milestone
