# Research Replay

## Purpose

The Research Replay layer defines the Stage 1 contract for reconstructing a previous research execution from immutable snapshots and event references. Replay provides a historical research view without performing new research.

## Inputs

- Snapshot ID
- Research task ID
- Execution ID
- Replay request time
- Replay requester
- Referenced research snapshot
- Referenced execution manifest
- Referenced event chain
- Referenced committee results

## Outputs

- `ReplayRequest` records
- `ReplayResult` records
- A reconstructed research view
- Export-ready replay representations

## Responsibilities

- Define the replay request and result contracts.
- Preserve existing task, execution, and snapshot identity.
- Establish read-only replay boundaries.
- Reference the historical artifacts required for reconstruction.
- Define the foundation boundary for reproducibility verification.

## Replay Contract

- Replay never performs new research.
- Replay never invokes providers.
- Replay reconstructs an existing execution.
- Replay consumes immutable snapshots.
- Replay consumes execution manifests.
- Replay consumes event chains.
- Replay produces a reconstructed research view.

This foundation defines contracts only and contains no loading, reconstruction, or validation behavior.

## Replay Identity

```text
task_id
↓
execution_id
↓
snapshot_id
↓
replay_request
```

Replay never creates new identities. Replay only references existing identities.

## Replay Boundaries

Replay is read-only.

Replay never modifies:

- Snapshots
- Manifests
- Events
- Committee results

Replay never generates new provider responses. Replay never synthesizes missing committee output.

## Replay Sources

Replay consumes these historical sources:

- Research Snapshot
- Execution Manifest
- Research Events
- Committee Results

Each source remains owned by its originating layer. Replay references them only to reconstruct and verify the historical research view.

## Future Expansion

Future approved tasks may define read-only artifact resolution, reconstruction rules, reproducibility checks, comparison reports, and export formats. Those capabilities remain outside this foundation.
