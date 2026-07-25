# Research Planner

## Purpose

The Research Planner converts portfolio priorities into focused research tasks. This directory provides the Stage 1 foundation for defining portfolio inputs, research tasks, priorities, and the planner interface.

## Inputs

- Current portfolio holdings
- Watchlist companies
- Portfolio constraints and risk limits
- Investment objectives
- Portfolio research priorities
- Related competitors, suppliers, customers, and sector leaders

## Outputs

- Portfolio-linked research tasks
- Task priority assignments
- Explanations of portfolio relevance
- Prompt identity and version
- Committee requirements
- Exportable planner results

## Responsibilities

- Load portfolio information.
- Generate research tasks from portfolio priorities.
- Reject research without material portfolio relevance.
- Prioritize tasks using documented planning rules.
- Export tasks in a consistent format for downstream Stage 1 components.

## Planner-to-Queue Contract

`ResearchTask` is the authoritative planning output consumed by `QueueTask`. The transition preserves:

| `ResearchTask` | `QueueTask` | Contract |
| --- | --- | --- |
| `task_id` | `task_id` | Preserve the planned task identity. |
| `prompt_id` | `prompt_id` | Preserve the logical prompt identity. |
| `prompt_version` | `prompt_version` | Preserve the selected prompt revision. |
| `committee_required` | `committee_required` | Preserve the committee requirements. |
| `priority` | `priority` | Preserve the numeric task priority. |

`ResearchTask` and `QueueTask` preserve the same shared-field types. In both models, `committee_required` is `list[str]`, so no string parsing or conversion is required.

Field mapping must be explicit by name. Positional construction must not be relied upon for planner-to-queue conversion. This section defines field continuity only and does not implement conversion or queue processing.

## Future Expansion

Future milestones will define the portfolio input contract, research task schema, prioritization rules, planner output format, validation, queue integration, and prompt assignment. Implementation logic will be added only after those designs and milestone exit criteria are approved.
