# JOO Command Center Architecture

## Vision

Build an institutional-grade AI investment operating system that transforms research into repeatable capital allocation decisions.

---

## Stage 0 Objective

Establish a stable and reproducible engineering foundation before implementing new features.

Success criteria:

- Project structure is documented.
- Development workflow is standardized.
- Engineering principles are defined.
- Future implementations follow the documented architecture.

---

## System Architecture

Portfolio Database
        │
        ▼
Research Engine
        │
        ▼
Knowledge Engine
        │
        ▼
CIO Engine
        │
        ▼
Reports
        │
        ▼
Future Event Database

---

## Canonical Identity Contract

Stage 1 uses these canonical identity fields:

- `task_id`
- `provider`
- `committee`
- `prompt_id`
- `prompt_version`

Applicable identity fields must remain attached to downstream results. A layer may add its own context, but it must not discard identity received from an upstream request when that identity applies to its output.

---

## Execution Ownership

- `AIAdapter.execute()` invokes one AI provider.
- `Committee.execute()` processes committee-level research using actual provider responses.
- `ExecutionEngine.execute()` coordinates one end-to-end research execution boundary.

These definitions establish ownership boundaries only. They do not introduce orchestration or execution behavior.

---

## Committee Failure Preservation

Committee results must be based on actual provider responses. Missing or failed provider responses remain explicit, missing output is not simulated, and failed providers are not silently substituted. CIO synthesis must wait until required committee results are available or explicitly marked failed or missing.

---

## Result Continuity

AI provider, committee, and execution results preserve the applicable canonical identity fields from their requests. Status, output, summary, and error fields add result context without replacing identity. This continuity supports future logging, versioning, replay, and validation contracts.

---

## Research Logging Layer

The Research Logging layer defines research event and execution-manifest contracts. It records events supplied by the owning execution, provider, and committee layers without determining business outcomes or implementing cross-layer orchestration.

---

## Execution Correlation

Stage 1 correlates events through this identity hierarchy:

```text
task_id
→ execution_id
→ event_id
```

`task_id` identifies a planned research task, `execution_id` identifies one attempt of that task, and `event_id` identifies one event within that attempt. Applicable provider, committee, and prompt identity remains attached to correlated events.

---

## Event Ownership

- ExecutionEngine owns execution-level events.
- AIAdapter owns provider-level events.
- Committee owns committee-level events.
- ResearchLogger records events but does not determine business outcomes.

Event ownership defines contract boundaries only and does not introduce cross-layer orchestration.

---

## Engineering Principles

1. Evidence First
2. Append Only
3. Human View != Machine View
4. Failure is Data
5. No Stage Skipping

---

## Development Workflow

Plan

↓

Implement

↓

Review

↓

Commit

↓

Document

---

## Branch Strategy

main
- Stable production branch.

feature/*
- Active development branches.

---

## Stage Exit Criteria

Stage 0 is complete when:

- Architecture documentation exists.
- Development log exists.
- Development workflow is standardized.
- Repository foundation is stable.
