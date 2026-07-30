# BaselineCurrentPropositionPair

BaselineCurrentPropositionPair owns one explicit, directed assignment of
baseline and current roles to two accepted proposition IDs.

`ExplicitBaselineCurrentPropositionPair` contains exactly these fields in
order:

1. `baseline_proposition_id: str`
2. `current_proposition_id: str`

The model is frozen, hashable, has no defaults, custom methods, slots, or
separate pair identity. It stores both supplied identifier objects directly.

`validate_explicit_baseline_current_proposition_pair()` performs structural
validation only. It requires the exact pair model type, validates the baseline
ID before the current ID, and then requires the two IDs to differ. Both values
must be exact nonblank built-in strings. Validation returns `None` on success.

The different-ID rule rejects assigning both roles to the same proposition
endpoint. It is a structural role conflict only; it does not validate endpoint
existence or temporal applicability.

The validator does not trim, case fold, normalize Unicode, convert, copy,
reconstruct, or infer time from either identifier. Surrounding whitespace on
an otherwise nonblank identifier is accepted and preserved. Equality is exact
structural equality and preserves baseline-to-current direction.

## Boundaries

Baseline and current roles are explicitly supplied by the caller. This package
does not include or validate proposition objects, effective-context observed
dates, context identity equality, or temporal ordering. Duplicate pairs and
shared endpoints across different valid pairs are structurally permitted.

This package does not own endpoint lookup, registries, global uniqueness,
collections, pairing applicability, numeric compatibility, date distance,
material change, semantic proposition production, Signal, Hypothesis, Thesis,
portfolio impact, materiality, scoring, confidence, runtime execution,
persistence, migration, orchestration, recommendations, CIO judgment, or
capital allocation.

Production code depends only on the Python standard library and this package.
EvidenceProposition and all existing packages remain independent and
unchanged.
