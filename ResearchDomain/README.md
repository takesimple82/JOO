# Research Domain

## Purpose

Research Domain defines stable application-level data contracts for future JOO research orchestration. M21 contains models and explicit validation only; it does not execute any runtime.

## Models

### ResearchTask

`ResearchTask` identifies a research objective, its priority, and the `PipelineExecution` definition assigned to it.

Allowed priority values:

- `P0`
- `P1`
- `P2`

### ResearchFinding

`ResearchFinding` preserves one sourced research statement, its committee identity, source dates, and verification state.

Allowed verification statuses:

- `verified`
- `partially_verified`
- `unverified`

### ResearchReport

`ResearchReport` groups findings for one research task and records the report outcome.

Allowed statuses:

- `completed`
- `failed`

A completed report must have `error == ""`. A failed report must have a nonblank error. Completed and failed reports may contain an empty findings list.

## Validation Ownership

Validation is explicit and owned by:

- `validate_research_task()`
- `validate_research_finding()`
- `validate_research_report()`

Validators raise `TypeError` for incorrect Python types and `ValueError` for blank strings, unsupported enum values, or invalid report status/error state. They return `None` for valid objects and never normalize, copy, or mutate input values.

## M21 Boundaries

M21 does not execute `PipelineRuntime`, `CommitteeRuntime`, `ExecutionEngine`, or provider adapters. It does not construct prompts, generate reports, serialize or persist data, or export files.

M21 does not synthesize, rank, vote, form consensus, make portfolio decisions, issue BUY, HOLD, or SELL recommendations, or allocate capital.
