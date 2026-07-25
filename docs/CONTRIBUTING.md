# Contributing

This document defines the standard development workflow for the JOO repository.

## 1. Branch Strategy

- `main` is the stable production branch and must remain deployable.
- Create active development branches from the latest `main`.
- Name feature branches `feature/<task-or-feature-name>`.
- Use a single branch for each focused task.
- Merge development branches only after review and validation.

## 2. Task Workflow

1. Confirm the task scope and acceptance criteria.
2. Create a focused development branch.
3. Plan the implementation before changing files.
4. Implement only the changes required by the task.
5. Run relevant checks and review the diff.
6. Submit the change for code review.
7. Commit approved changes.
8. Update applicable documentation.

The standard sequence is: Plan → Implement → Review → Commit → Document.

## 3. Code Review Process

- Every change should be reviewed before it is merged into `main`.
- Reviewers should verify correctness, scope, tests, documentation, security, and maintainability.
- Authors should provide a clear summary and evidence of validation.
- Resolve all blocking feedback before merging.
- Keep unrelated changes out of the review.

## 4. Commit Message Conventions

- Use an imperative, concise subject line.
- Describe one logical change per commit.
- Include the task identifier when one exists.
- Add a commit body when the reason or trade-offs are not clear from the subject.

Example:

```text
TASK-004 Document contribution workflow
```

## 5. Rules for Modifying Existing Files

- Modify an existing file only when the task explicitly requires it.
- Preserve unrelated content and user changes.
- Keep edits minimal and focused on the requested outcome.
- Review the diff before committing.
- Do not perform destructive rewrites without explicit authorization.
- Maintain backward compatibility unless the task documents an approved breaking change.

## 6. Rules for Adding New Features

- Do not skip project stages or begin implementation without defined acceptance criteria.
- Follow the documented architecture and engineering principles.
- Create focused, reviewable changes with clear boundaries.
- Add appropriate tests, documentation, and event records.
- Treat failures as data and preserve evidence needed for diagnosis.
- Avoid combining refactoring with feature work unless required for the feature.
- Confirm the feature meets its acceptance criteria before requesting review.
