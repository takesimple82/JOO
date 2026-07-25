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
- Result status
- Result summary

## Committee Contract

Every committee follows the `Committee` interface:

- `prepare()` defines the preparation boundary.
- `execute()` defines the execution boundary.
- `validate()` defines the validation boundary.
- `export()` defines the output boundary.

This foundation defines the contract only. It contains no committee behavior, AI provider calls, or workflow orchestration.

## Supported Committees

- Market Committee
- Memory Committee
- Institutional Capital Committee
- Portfolio Committee
- Risk Committee
- Contradiction Committee

## Future Expansion

Future approved tasks may define committee implementations, method signatures, validation rules, status values, result preservation, and integration boundaries. Expansion must retain actual committee results, explicitly record missing responses, and remain consistent with the Stage 1 Committee First Protocol.
