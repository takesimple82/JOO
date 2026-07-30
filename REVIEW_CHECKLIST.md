# JOO Milestone Review Checklist

Every milestone review verifies each item below.

## Architecture

- [ ] The milestone owns one explicit minimum responsibility.
- [ ] Repository evidence and roadmap support the design.
- [ ] Dependencies follow accepted direction.
- [ ] Non-responsibilities are documented.

## Contract

- [ ] Public models, functions, enums, and field order are exact.
- [ ] Identity is opaque, caller-supplied, and preserved.
- [ ] Object and collection ownership is explicit.
- [ ] Models are immutable where contracted.
- [ ] No hidden inference, normalization, conversion, or generated identity
      exists.

## Validation

- [ ] Validation order is documented and tested.
- [ ] Exact types and subclass rejection are covered.
- [ ] Upstream validators run exactly once.
- [ ] Upstream exceptions propagate unchanged.
- [ ] Applicability precedence and exception mapping are exact.
- [ ] Caller order and object identity are preserved.

## Boundaries

- [ ] Structural, applicability, semantic, calculation, and operational
      responsibilities remain separate.
- [ ] Private unchecked helpers are used only after equivalent validation.
- [ ] Runtime, persistence, registry, orchestration, and future scope are not
      introduced.

## Verification

- [ ] Focused tests pass.
- [ ] Affected tests pass.
- [ ] Full accepted regression passes.
- [ ] `py_compile` passes.
- [ ] `git diff --check` passes.
- [ ] Every changed and new file has been reviewed.
- [ ] Existing public API remains stable.

## Git Checkpoint

- [ ] Repository path and branch are correct.
- [ ] Starting HEAD and exact tag are verified.
- [ ] Only milestone files are staged.
- [ ] Commit message is approved.
- [ ] Annotated tag points to the intended commit.
- [ ] `git status --short` is clean at completion.
- [ ] No push occurred without explicit approval.
