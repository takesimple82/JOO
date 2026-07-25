# Research Logging

## Purpose

The Research Logging layer defines the Stage 1 contract for recording research execution events. It preserves execution identity, lifecycle state, provider and committee context, prompt references, payloads, and failures without implementing storage or serialization.

## Inputs

- Event, execution, and task identity
- Event type and status
- UTC occurrence timestamp
- Applicable provider and committee identity
- Prompt ID and prompt version
- Event payload
- Error text

## Outputs

- `ResearchEvent` records
- `ExecutionManifest` records
- `SourceReference` records
- Export-ready event and execution representations

## Responsibilities

- Define the event and execution-manifest data contracts.
- Preserve canonical identity across research events.
- Record events owned by execution, provider, and committee layers.
- Preserve failed and missing outcomes explicitly.
- Preserve source provenance independently from provider interpretation.
- Expose foundation boundaries for appending, finalizing, and exporting records.

## Logging Contract

Every research logger follows the `ResearchLogger` interface:

- `create_event()` defines the event-creation boundary.
- `append()` defines the append boundary.
- `finalize()` defines the execution-finalization boundary.
- `export()` defines the output boundary.

`ResearchLogger` records events supplied by their owning layers. It does not determine business outcomes or implement lifecycle transitions. This foundation contains no writing, serialization, persistence, ID generation, timestamp generation, or validation behavior.

## Event Identity

Stage 1 has three identity levels:

- `task_id` identifies the planned research task.
- `execution_id` identifies one execution attempt of that task.
- `event_id` identifies one event within that execution.

```text
task_id
→ execution_id
→ event_id
```

Identity generation is outside this foundation.

## Event Lifecycle

Stage 1 defines these event types:

- `execution_prepared`
- `provider_started`
- `provider_completed`
- `provider_failed`
- `committee_started`
- `committee_completed`
- `committee_failed`
- `execution_completed`
- `execution_failed`

Stage 1 defines these event statuses:

- `pending`
- `running`
- `completed`
- `failed`
- `missing`

Lifecycle transitions and status validation are not implemented in this foundation.

## Failure Preservation

- Failed provider calls must generate explicit failed events.
- Missing provider responses must generate explicit missing events or status.
- Provider failures must not be omitted from committee records.
- Failed or missing results must not be replaced with simulated output.
- Error text must remain attached to the corresponding event.
- CIO synthesis must not treat missing provider output as a successful committee response.

## Committee First Protocol

Committee events and results must be based on actual provider responses. Required responses must be available or explicitly marked failed or missing before committee completion can be treated as successful. Missing providers must not be silently substituted, predicted, invented, or simulated.

## Source Provenance Contract

Research outputs may reference one or more `SourceReference` records. Source provenance is preserved independently from provider interpretation.

- `event_date` records when the underlying event occurred.
- `publication_date` records when the source was published.
- These dates are distinct and must not be substituted for one another.
- Unverified sources remain explicit through `verification_status`.

This foundation does not fetch or verify sources and contains no network or parsing behavior.

## Future Expansion

Future approved tasks may define ID generation, UTC timestamp generation, serialization, append-only storage, lifecycle validation, and integration with event owners. Those capabilities remain outside this foundation.
