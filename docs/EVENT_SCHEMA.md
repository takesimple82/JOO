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
