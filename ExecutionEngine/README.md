# Execution Engine

## Purpose

The Execution Engine owns the synchronous Stage 2 boundary for resolving one configured provider adapter and executing one `AIRequest` exactly once.

## Inputs

- One `AIRequest`
- Explicitly configured `AIAdapter` instances

## Outputs

- One valid `AIResponse`

## Responsibilities

- Own an instance-local provider adapter registry.
- Resolve providers case-insensitively.
- Execute one resolved adapter exactly once.
- Preserve valid adapter responses unchanged.
- Normalize unsupported providers, invalid adapter responses, and unexpected adapter exceptions into failed responses.
- Record provider-independent execution start, success, and failure events.

## Execution Contract

`ExecutionEngine.execute(request)` accepts one `AIRequest` and returns one `AIResponse`. It does not mutate the request.

Configured adapters are injected during engine construction or registered explicitly. ExecutionEngine does not instantiate provider adapters, load credentials, import provider SDKs, or construct provider requests.

If an adapter unexpectedly raises, the engine returns a failed response containing only a stable diagnostic and the exception type. If an adapter returns a non-`AIResponse`, the engine returns a failed response without interpreting that object.

Objects that are not `AIRequest` raise `TypeError` before provider resolution. Non-string identity fields also raise `TypeError` because the `AIResponse` contract cannot safely preserve them. Blank string fields, including whitespace-only strings, produce a failed `AIResponse`.

## Execution Logging

Each valid `AIRequest` records a `start` event followed by exactly one `success` or `failure` event. A completed adapter response records success; unsupported providers, invalid requests, adapter exceptions, invalid adapter responses, and non-completed adapter responses record failure.

`ExecutionLog` preserves task, provider, prompt, event, timestamp, and error information without storing prompt or response content. Timestamps use UTC ISO 8601 format. Non-`AIRequest` objects and requests with non-string identity fields are rejected before logging because their identities cannot be safely represented.

`ExecutionLogger` defines the provider-independent recording boundary. `MemoryExecutionLogger` stores immutable log entries in one logger instance and exposes them as a tuple. It does not write files or use a database.

The logger is explicitly injectable. If none is supplied, the engine creates an instance-local `MemoryExecutionLogger`. Logging exceptions are contained so logging cannot change the M12 `AIResponse` behavior.

## Adapter Registry

- Registry state belongs to one engine instance.
- Provider lookup is case-insensitive.
- Duplicate provider registration is rejected.
- Blank provider identifiers are rejected.
- Only concrete `AIAdapter` instances may be registered.
- No global registry, plugin discovery, or provider auto-construction is used.

## M12 Scope

M12 is synchronous and executes one request only.

The Stage 1 `prepare()`, `finalize()`, and `export()` methods remain intentionally unimplemented in M12 and raise `NotImplementedError`.

It does not implement:

- Retries
- Committee orchestration
- Parallelism or batch execution
- Queue processing
- Persistence
- Replay or versioning runtime
- Scheduling
- Provider fallback, priority, or load balancing
