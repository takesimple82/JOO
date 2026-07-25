# AI Adapter Layer

## Purpose

The AI Adapter Layer defines a consistent boundary between the JOO Research Layer and external AI providers. It provides shared request and response models plus a common adapter interface while keeping provider integrations isolated.

## Supported Providers

- ChatGPT
- Claude
- Gemini
- Grok
- Perplexity

No other providers are included in the Stage 1 scope.

## Inputs

- Provider name
- Prompt content
- Prompt ID
- Prompt version
- Research task ID

## Outputs

- Provider name
- Research task ID
- Provider response content
- Response status
- Error information when a response is missing or unavailable

## Responsibilities

- Validate requests before provider execution.
- Execute requests through the selected provider adapter.
- Normalize provider results into a common response model.
- Report adapter health.
- Preserve provider and task identity.
- Record unavailable responses without inventing or simulating content.

## Adapter Contract

Every provider adapter inherits from `AIAdapter` and follows the same four-operation contract:

- `validate_request()` validates the common request structure.
- `execute()` submits an approved request to the provider.
- `normalize_response()` converts a provider result into the common response structure.
- `health_check()` reports whether the adapter is available.

The foundation defines interfaces only. It contains no API clients or provider execution behavior.

## Future Expansion

Future approved tasks may define method signatures, validation rules, response status values, provider configuration, authentication boundaries, error handling, and execution behavior. Those additions must preserve actual provider responses, explicitly identify missing responses, and comply with the Committee Layer contract.
