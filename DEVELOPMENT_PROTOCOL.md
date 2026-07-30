# JOO Development Protocol

Every approved milestone follows this sequence:

```text
Architecture
    ↓
Implementation
    ↓
Focused Tests
    ↓
Accepted Regression
    ↓
Diff Review
    ↓
Commit
    ↓
Annotated Tag
    ↓
Architecture Review
    ↓
Next Milestone
```

## 1. Architecture

- Verify repository path, branch, HEAD, exact tag, and working tree.
- Inspect the roadmap, accepted contracts, adjacent packages, and tests.
- Fix one minimum responsibility, public API, validation order, exceptions,
  dependencies, and non-responsibilities.

## 2. Implementation

- Implement only the approved boundary.
- Preserve accepted public contracts.
- Use immutable models, validation-first ordering, and existing naming and
  unittest conventions.

## 3. Verification

- Run focused tests first.
- Run affected accepted tests after internal refactoring.
- Run the full accepted regression.
- Run `py_compile`, `git diff --check`, and new/changed-file diff review.
- Fix failures without weakening tests or expanding scope, then rerun affected
  checks.

## 4. Checkpoint

- Stage only milestone files.
- Commit only after all checks pass and authorization exists.
- Create the approved annotated tag.
- Verify branch, HEAD, exact tag, commit stat, and clean working tree.
- Never push without separate explicit approval.

## Stop Conditions

Stop immediately and report when:

- architecture ambiguity appears
- a new responsibility is required
- an existing public contract must change
- an accepted regression fails and cannot be fixed within scope
- the repository checkpoint does not match
- the working tree is not clean before a new milestone

Do not continue to another milestone until the current checkpoint is complete
and clean.
