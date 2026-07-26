# Pipeline Runtime

## Purpose

The Pipeline Runtime provides a synchronous, provider-independent boundary for executing an ordered collection of `CommitteeExecution` objects through an injected `CommitteeRuntime`.

## Models

`PipelineExecution` contains:

- `pipeline_id`
- `name`
- `committees: list[CommitteeExecution]`

`PipelineExecutionResult` contains:

- `pipeline_id`
- `committee_results: list[CommitteeExecutionResult]`

## Runtime Contract

`PipelineRuntime.run(pipeline)` validates the complete pipeline container before executing any committee. It calls `CommitteeRuntime.run()` exactly once for each committee, sequentially and in list order.

The result contains a new committee-result list in the same order. Every `CommitteeExecutionResult` is preserved as the exact object returned by the Committee Runtime.

The runtime does not modify pipelines, committees, committee results, requests, or AI responses. Committee and provider behavior remains owned by the existing lower runtime layers.

If `CommitteeRuntime.run()` raises an exception, Pipeline Runtime stops immediately and propagates the same exception object unchanged. It does not retry, execute any remaining committees, or create a replacement result.

An empty committee list is valid and returns an empty result list.

## Exclusions

M15 does not implement asynchronous or parallel execution, retries, fallback, branching, conditional execution, workflow engines, DAGs, planning, scheduling, queues, persistence, provider logic, voting, ranking, consensus, or synthesis.
