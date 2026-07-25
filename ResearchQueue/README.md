# Research Queue

## Purpose

The Research Queue defines the Stage 1 foundation for receiving portfolio-driven research tasks and representing their ordered execution lifecycle. This foundation provides a common interface and data models without implementing queue behavior.

## Inputs

- Research task ID
- Numeric priority
- Portfolio entity
- Portfolio relevance
- Required committee members
- Prompt ID and version
- Queue status
- Creation and update timestamps

## Outputs

- Queue task records
- Dequeued task records
- Status update results
- Exportable queue representations

## Responsibilities

- Accept research tasks that conform to the queue contract.
- Expose tasks for later execution.
- Define a boundary for status updates.
- Preserve portfolio relevance, committee requirements, and prompt references.
- Export queue information through a consistent interface.

## Queue Contract

Every queue implementation follows the `ResearchQueue` interface:

- `enqueue()` defines the task-entry boundary.
- `dequeue()` defines the task-retrieval boundary.
- `update_status()` defines the lifecycle-update boundary.
- `export()` defines the queue-output boundary.

A queue task carries its identity, priority, portfolio context, committee requirements, prompt reference, lifecycle status, and timestamps. This foundation defines the contract only and contains no persistence, execution, scheduling, or validation behavior.

## Planner-to-Queue Contract

`QueueTask` receives the authoritative planning fields from `ResearchTask`:

| `ResearchTask` | `QueueTask` | Contract |
| --- | --- | --- |
| `task_id` | `task_id` | Preserve the planned task identity. |
| `prompt_id` | `prompt_id` | Preserve the logical prompt identity. |
| `prompt_version` | `prompt_version` | Preserve the selected prompt revision. |
| `committee_required` | `committee_required` | Preserve the committee requirements. |
| `priority` | `priority` | Preserve the numeric task priority. |

`ResearchTask` and `QueueTask` preserve the same shared-field types. In both models, `committee_required` is `list[str]`, so no string parsing or conversion is required.

Field mapping must be explicit by name. Positional construction must not be relied upon for planner-to-queue conversion. No conversion or queue-processing behavior is implemented by this contract.

## Queue Status Lifecycle

Stage 1 defines these status values:

- `pending`
- `ready`
- `running`
- `completed`
- `failed`
- `blocked`

Status validation and transition rules are not implemented in this foundation.

## Priority Model

Lower numeric values represent higher priority. Priorities will be assigned from Portfolio Research Planner rules in a future approved task.

Prioritization logic is not implemented in this foundation.

## Future Expansion

Future approved tasks may define method signatures, queue operations, lifecycle transition rules, field validation, export formats, and integration boundaries. Persistence, scheduling, concurrency, retries, orchestration, committee execution, and provider execution remain outside this foundation.
