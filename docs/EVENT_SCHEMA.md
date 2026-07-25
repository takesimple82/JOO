# Event Schema

`data/events.jsonl` uses JSON Lines format. Each line contains one complete JSON object representing an event.

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `timestamp` | string | Event timestamp in ISO-8601 format. |
| `stage` | string | Workflow or system stage in which the event occurred. |
| `source` | string | System, process, or actor that produced the event. |
| `event_type` | string | Classification of the event. |
| `entity` | string | Primary entity associated with the event. |
| `summary` | string | Concise human-readable description of the event. |
| `metadata` | object | Additional structured context for the event. |

## Example

```json
{"timestamp":"2026-07-25T09:00:00+09:00","stage":"research","source":"research-engine","event_type":"analysis_completed","entity":"ACME","summary":"Completed the initial company analysis.","metadata":{"analyst":"system","confidence":0.92}}
```

---

## Stage 1 Research Logging

Stage 1 introduces research-specific event and execution-manifest contracts. These contracts supplement and do not replace the Stage 0 JSON Lines schema above.

### ResearchEvent

| Field | Type | Semantics |
| --- | --- | --- |
| `event_id` | string | Identifies one event within an execution. |
| `execution_id` | string | Identifies one execution attempt of a research task. |
| `task_id` | string | Identifies the planned research task. |
| `event_type` | string | Identifies the lifecycle event that occurred. |
| `status` | string | Records the event outcome or current state. |
| `occurred_at` | string | Records when the event occurred in UTC ISO 8601 format. |
| `provider` | string | Preserves the applicable AI provider identity. |
| `committee` | string | Preserves the applicable committee identity. |
| `prompt_id` | string | Identifies the logical prompt. |
| `prompt_version` | string | Identifies the prompt revision used. |
| `payload` | string | Carries event-specific context without replacing identity fields. |
| `error` | string | Preserves error text for the corresponding failed or missing event. |

### ExecutionManifest

| Field | Type | Semantics |
| --- | --- | --- |
| `execution_id` | string | Identifies one execution attempt. |
| `task_id` | string | Identifies the planned research task. |
| `started_at` | string | Records the UTC ISO 8601 execution start time. |
| `completed_at` | string | Records the UTC ISO 8601 execution completion time. |
| `status` | string | Records the execution outcome or current state. |
| `provider` | string | Preserves the applicable AI provider identity. |
| `committee` | string | Preserves the applicable committee identity. |
| `prompt_id` | string | Identifies the logical prompt. |
| `prompt_version` | string | Identifies the prompt revision used. |

### Identity Hierarchy

```text
task_id
→ execution_id
→ event_id
```

- `task_id` identifies the planned research task.
- `execution_id` identifies one execution attempt of that task.
- `event_id` identifies one event within that execution.

### Event Types

- `execution_prepared`
- `provider_started`
- `provider_completed`
- `provider_failed`
- `committee_started`
- `committee_completed`
- `committee_failed`
- `execution_completed`
- `execution_failed`

### Statuses

- `pending`
- `running`
- `completed`
- `failed`
- `missing`

### Payload Semantics

`payload` is a string containing event-specific context. It supplements the named identity and lifecycle fields and must not be used to hide or replace them.

### Error Semantics

`error` preserves error text on the event to which the failure or missing response belongs. Provider failures must remain present in committee records, and failed or missing results must not be replaced by simulated output.

### Timestamp Format

Stage 1 timestamps use UTC ISO 8601 format:

```text
2026-07-25T12:34:56Z
```

Timestamp generation is outside the Stage 1 logging foundation.

### SourceReference

Research outputs may reference one or more `SourceReference` records.

| Field | Type | Semantics |
| --- | --- | --- |
| `source_id` | string | Identifies the source reference. |
| `source_type` | string | Identifies the source category. |
| `source_uri` | string | Preserves the source location reference. |
| `title` | string | Preserves the source title. |
| `publisher` | string | Preserves the source publisher. |
| `event_date` | string | Records when the underlying event occurred. |
| `publication_date` | string | Records when the source was published. |
| `retrieved_at` | string | Records when the source reference was retrieved. |
| `verification_status` | string | Preserves whether the source is verified or remains unverified. |

Source provenance is preserved independently from provider interpretation. Event date and publication date are distinct. Unverified sources remain explicit. No source fetching or verification is implemented by this contract.

### Shared Timestamp Contract

All `*_at` fields use UTC ISO 8601 timestamps unless a future contract explicitly states otherwise.

```text
2026-07-25T12:34:56Z
```

This contract does not implement timestamp generation or validation.
