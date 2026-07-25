# Research Versioning

## Purpose

The Research Versioning layer defines immutable snapshot contracts for reproducible Stage 1 research. A snapshot identifies the complete research environment associated with one execution.

## Inputs

- Research task identity
- Execution identity
- Portfolio version
- Prompt ID
- Prompt version
- Committee version
- Event manifest reference
- Snapshot creation time
- Snapshot status

## Outputs

- `ResearchSnapshot` records
- `VersionManifest` records
- Export-ready snapshot representations

## Responsibilities

- Define the immutable research snapshot boundary.
- Preserve references to the complete research environment.
- Associate snapshots with their task and execution identities.
- Define version-manifest records.
- Provide foundation boundaries for creating, loading, exporting, and validating snapshots.
- Own the reproducibility contract consumed by replay.

## Snapshot Contract

A snapshot preserves the complete research environment. It does not preserve only prompts.

A snapshot references:

- Portfolio
- Prompts
- Committees
- Execution
- Events

The execution reference connects the snapshot to its execution manifest. The event manifest reference connects it to the corresponding event chain. Loading behavior is not implemented in this foundation.

## Version Contract

Each snapshot records the portfolio, prompt, and committee versions applicable to its execution. Prompt versions are scoped to a logical prompt identity, so `prompt_id` and `prompt_version` remain paired in both snapshots and version manifests. A snapshot is immutable after creation; a changed research environment requires a distinct snapshot. Version generation and integrity verification are outside this foundation.

## Identity Contract

```text
task_id
↓
execution_id
↓
snapshot_id
```

- `task_id` identifies the planned research task.
- `execution_id` identifies one execution attempt of that task.
- `snapshot_id` identifies the immutable research snapshot for the captured environment.

The snapshot references the execution's event chain through `event_manifest`. ID generation is not implemented in this foundation.

## Future Expansion

Future approved tasks may define version generation, persistence boundaries, snapshot loading, integrity verification, and replay integration. Those capabilities remain outside this foundation.
