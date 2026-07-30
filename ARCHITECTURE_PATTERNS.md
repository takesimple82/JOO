# JOO Architecture Patterns

JOO uses small, composable boundaries. Not every milestone needs every layer,
but responsibilities must remain separate.

```text
Explicit Model
    ↓
Validator
    ↓
Applicability
    ↓
Semantic Production
    ↓
Calculation
```

## Explicit Model

Purpose: store caller-supplied structure and identity without behavior.

Responsibilities:

- frozen, hashable structural data
- exact field order and types
- opaque identity where the object is persistent

Allowed dependencies:

- accepted upstream immutable models
- Python standard-library value types

Forbidden:

- validation in constructors
- inference, lookup, generated IDs, runtime, persistence

## Validator

Purpose: enforce one model's structural and cross-field invariants.

Responsibilities:

- exact model and field validation in declared order
- upstream validation exactly once
- stable exception types and messages
- object identity and representation preservation

Allowed dependencies:

- the owned model
- accepted upstream validators
- private unchecked classifiers after validation

Forbidden:

- normalization, repair, reconstruction, hidden lookup, policy invention

## Applicability

Purpose: classify whether structurally valid inputs may participate in a
specific relation or calculation.

Responsibilities:

- validate public inputs exactly once
- deterministic ordered classification
- explicit mismatch status and precedence

Allowed dependencies:

- accepted models and validators
- exact arithmetic where required
- private post-validation helpers

Forbidden:

- semantic truth claims, automatic conflict resolution, mutation, runtime

## Semantic Production

Purpose: attest that an authoritative external or future semantic producer
accepted one explicit object.

Responsibilities:

- one immutable wrapped object
- exact wrapper and field types
- wrapped-object validation exactly once
- unchanged upstream exception propagation

Allowed dependencies:

- the explicit model and validator being wrapped

Forbidden:

- producer execution or identity, provenance, confidence, inference,
  calculation

## Calculation

Purpose: derive a deterministic result from validated semantic inputs.

Responsibilities:

- validation-first execution
- explicit applicability handling
- exact ordered arithmetic
- immutable result and input traceability

Allowed dependencies:

- accepted semantic structures
- accepted policies and applicability helpers
- exact domain-independent arithmetic

Forbidden:

- semantic interpretation, market lookup, unit conversion, recommendation,
  allocation, runtime state

## Dependency Direction

Dependencies flow from later responsibilities to earlier accepted contracts.
Explicit models do not depend on their validators, classifiers, semantic
wrappers, calculations, or operational consumers. Public behavior is never
changed solely to make a downstream implementation convenient.
