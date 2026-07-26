# Committee Layer

## Purpose

The Committee Layer defines committee research boundaries and provides a synchronous Stage 2 runtime for executing an ordered collection of `AIRequest` objects through the existing `ExecutionEngine`.

## Committee Responsibilities

- Accept a research task and its prompt identity.
- Preserve committee, task, and provider identity.
- Prepare work through a common interface.
- Validate committee results through a common interface.
- Export committee results in a consistent format.
- Identify unavailable or missing results without inventing or simulating responses.
- Execute committee requests sequentially without interpreting responses.
- Preserve request order and return the exact `AIResponse` objects produced by the Execution Engine.

## Runtime Inputs

- A `CommitteeExecution` containing `committee_id`, `name`, and `requests: list[AIRequest]`
- An explicitly supplied `ExecutionEngine`

## Runtime Output

- A `CommitteeExecutionResult` containing the original `committee_id`
- `responses: list[AIResponse]` in request order

## Committee Contract

The Stage 1 `Committee.base.Committee` interface remains unchanged:

- `prepare()` defines the preparation boundary.
- `execute()` processes committee-level research using actual provider responses.
- `validate()` defines the validation boundary.
- `export()` defines the output boundary.

## Committee Runtime

`CommitteeExecution` and `CommitteeExecutionResult` are distinct Stage 2 runtime contracts. They do not replace the Stage 1 `Committee` interface or `CommitteeResult` model.

`CommitteeRuntime.run(committee)` validates a `CommitteeExecution` and then calls `ExecutionEngine.execute()` once for each request, sequentially and in list order. It returns a `CommitteeExecutionResult` with a new response list containing the exact response objects returned by the engine.

The runtime does not mutate committees, requests, or responses. Provider selection, invocation, error normalization, and execution logging remain owned by `ExecutionEngine` and `AIAdapter`.

An empty request list is valid and produces an empty response list.

## Committee Completeness Aggregate

`CommitteeAggregate` preserves committee completeness without calculating it:

- `required_providers` identifies the expected provider set.
- `completed_providers` preserves successful responses.
- `failed_providers` preserves explicit failures.
- `missing_providers` preserves absent responses.
- `status` represents aggregate completeness.

The four provider-group fields are provider collections, and each uses `list[str]`. No string parsing or serialization convention is required. `failed_providers` and `missing_providers` remain distinct.

Failed or missing providers must never be treated as completed. Provider output must never be simulated. Completeness calculation is not implemented in this foundation.

## Committee First Protocol

- Committee results must be based on actual provider responses.
- Missing or failed provider responses must remain explicit.
- Missing provider output must not be simulated.
- Failed providers must not be silently substituted.
- CIO synthesis must not occur before required committee results are available or explicitly marked failed or missing.

## Supported Committees

- Market Committee
- Memory Committee
- Institutional Capital Committee
- Portfolio Committee
- Risk Committee
- Contradiction Committee

## Future Expansion

Future approved tasks may define committee preparation, validation, completeness calculation, and export behavior. Expansion must retain actual committee results, explicitly record missing responses, and remain consistent with the Stage 1 Committee First Protocol.

M14 does not implement asynchronous or parallel execution, retries, fallback, voting, ranking, synthesis, planning, scheduling, queues, persistence, or provider-specific behavior.
