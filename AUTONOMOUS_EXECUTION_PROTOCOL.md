# JOO Autonomous Execution Protocol

Autonomous execution applies only within an explicitly approved milestone and
the accepted repository contracts.

## Codex May

- inspect repository facts and architecture precedents
- implement approved milestones
- add focused tests and documentation
- run focused, affected, and accepted regression tests
- run compile and diff checks
- review every changed file
- commit an approved, fully verified milestone
- create its approved annotated tag
- prepare checkpoint and architecture reports

## Codex Must Not

- push or merge
- create or switch branches without approval
- expand milestone scope
- redesign approved architecture
- modify accepted public contracts
- add runtime, persistence, registry, or orchestration incidentally
- continue after architecture becomes blocked
- hide, skip, weaken, or accept failing tests
- rewrite history or amend accepted commits

## Preconditions for Autonomous Continuation

- The architecture is singular and approved.
- The repository checkpoint matches.
- The working tree is clean before the next milestone.
- The current milestone's focused and accepted regression tests pass.
- Commit and annotated-tag authority is explicit.

## Blocked Operation

When a stop condition occurs, stop implementation and produce:

```text
BLOCKED REPORT

Reason:
Evidence:
Possible solutions:
Recommendation:
```

The report must identify the exact unresolved responsibility or conflicting
contract. Codex resumes only after the blocker is resolved or a revised scope
is explicitly approved.
