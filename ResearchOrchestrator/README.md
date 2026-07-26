# Research Orchestrator

## Purpose

M22 provides one synchronous orchestration boundary from a validated `ResearchTask` to its existing `PipelineExecution`. It returns the `PipelineExecutionResult` produced by the injected `PipelineRuntime` directly.

## Dependency Injection

`ResearchOrchestrator` requires an explicit `PipelineRuntime` instance. It preserves that exact instance and does not create a default runtime or construct committee, execution-engine, adapter, or provider dependencies.

## Validation and Delegation

`run(task)` calls the existing `validate_research_task()` before any execution. For a valid task, it passes `task.pipeline` directly to `PipelineRuntime.run()` exactly once.

The orchestrator preserves the identity of the pipeline and returned result. It does not copy, replace, reorder, or mutate the task, pipeline, committees, pipeline result, committee-results list, or nested committee results.

## Exception Behavior

Validation and pipeline exceptions propagate as the exact original exception objects. Validation failure occurs before pipeline delegation. Pipeline failure stops immediately with no retry, wrapping, replacement result, or synthesized result.

## M22 Boundaries

M22 does not create `ResearchFinding` or `ResearchReport` objects. Evidence extraction, evidence validation, aggregation, report generation, and summarization belong to later milestones.

M22 does not construct prompts, call providers, retry, fall back, run asynchronously or in parallel, branch, queue work, persist or serialize data, export files, rank, vote, form consensus, synthesize conclusions, make portfolio decisions, issue BUY, HOLD, or SELL recommendations, or allocate capital.
