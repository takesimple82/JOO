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

## Execution Contract

`ExecutionEngine.execute(request)` accepts one `AIRequest` and returns one `AIResponse`. It does not mutate the request.

Configured adapters are injected during engine construction or registered explicitly. ExecutionEngine does not instantiate provider adapters, load credentials, import provider SDKs, or construct provider requests.

If an adapter unexpectedly raises, the engine returns a failed response containing only a stable diagnostic and the exception type. If an adapter returns a non-`AIResponse`, the engine returns a failed response without interpreting that object.

Objects that are not `AIRequest` raise `TypeError` before provider resolution. Non-string identity fields also raise `TypeError` because the `AIResponse` contract cannot safely preserve them. Blank string fields, including whitespace-only strings, produce a failed `AIResponse`.

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
- Logging runtime or event emission
- Replay or versioning runtime
- Scheduling
- Provider fallback, priority, or load balancing
