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

ChatGPT remains a Stage 1 contract placeholder. The M11 provider runtime implements Claude, Gemini, Grok, and Perplexity only.

## Inputs

- Provider name
- Prompt content
- Prompt ID
- Prompt version
- Research task ID

## Outputs

- Provider name
- Research task ID
- Prompt ID
- Prompt version
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
- `execute()` invokes one AI provider for an approved request.
- `normalize_response()` converts a provider result into the common response structure.
- `health_check()` reports whether the adapter is available.

The base adapter owns request validation, successful and failed response construction, and non-secret exception normalization. Each provider adapter owns its request construction, provider client invocation, and response text extraction.

## Stage 2 Provider Runtime

| Provider | Runtime | Required configuration | Optional package |
| --- | --- | --- | --- |
| Claude | Anthropic client | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | `anthropic` |
| Gemini | Google Gen AI client | `GEMINI_API_KEY`, `GEMINI_MODEL` | `google-genai` |
| Grok | Standard-library HTTP transport | `XAI_API_KEY`, `XAI_MODEL` | None |
| Perplexity | Standard-library HTTP transport | `PERPLEXITY_API_KEY`, `PERPLEXITY_MODEL` | None |

Provider clients and HTTP transports may be supplied directly for testing or configuration. The adapter never accepts a generic `AIRequest`-to-string invocation callable.

Optional SDK imports are isolated inside their provider modules. If a required key, model, or optional SDK is unavailable, the adapter returns a failed `AIResponse` with a stable diagnostic. Credential values are never included in response errors.

Health checks verify local client and configuration availability only. They do not make billable completion requests.

## Future Expansion

Future approved tasks may define method signatures, validation rules, response status values, provider configuration, authentication boundaries, error handling, and execution behavior. Those additions must preserve actual provider responses, explicitly identify missing responses, and comply with the Committee Layer contract.
