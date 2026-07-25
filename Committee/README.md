# Committee Layer

## Purpose

The Committee Layer defines a consistent foundation for collecting committee research results within the Stage 1 Research Layer. It establishes shared committee interfaces and data models without implementing execution, AI calls, or orchestration.

## Committee Responsibilities

- Accept a research task and its prompt identity.
- Preserve committee, task, and provider identity.
- Prepare work through a common interface.
- Validate committee results through a common interface.
- Export committee results in a consistent format.
- Identify unavailable or missing results without inventing or simulating responses.

## Inputs

- Committee name
- Research task ID
- AI provider name
- Prompt ID
- Prompt version

## Outputs

- Committee name
- Research task ID
- AI provider name
- Prompt ID
- Prompt version
- Result status
- Result summary
- Error information when a provider response is missing or failed

## Committee Contract

Every committee follows the `Committee` interface:

- `prepare()` defines the preparation boundary.
- `execute()` processes committee-level research using actual provider responses.
- `validate()` defines the validation boundary.
- `export()` defines the output boundary.

This foundation defines the contract only. It contains no committee behavior, AI provider calls, or workflow orchestration.

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

Future approved tasks may define committee implementations, method signatures, validation rules, status values, result preservation, and integration boundaries. Expansion must retain actual committee results, explicitly record missing responses, and remain consistent with the Stage 1 Committee First Protocol.
