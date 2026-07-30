# EffectiveContextObservedDate

EffectiveContextObservedDate owns one explicit structural association between
an existing opaque effective-context ID and its caller-supplied observed date.

`ExplicitEffectiveContextObservedDate` contains exactly these fields in order:

1. `effective_context_id: str`
2. `observed_on: str`

The model is frozen, hashable, has no defaults, custom methods, or slots, and
stores both supplied objects directly.

`validate_explicit_effective_context_observed_date()` validates the exact model
type, then `effective_context_id`, then `observed_on`. The context ID must be an
exact nonblank built-in `str`. The observed date must be an exact built-in
`str` containing a valid calendar date in strict ASCII `YYYY-MM-DD` format,
matching the accepted repository date rule. Validation returns `None` on
success.

The validator does not trim, case fold, normalize Unicode, convert, copy, or
reconstruct either value or the model. Surrounding whitespace on an otherwise
nonblank context ID is accepted and preserved. Date whitespace and non-ASCII
digits are invalid because the date representation is strict.

## Boundaries

This association is an explicit caller-supplied declaration. It does not infer
`observed_on` from a research finding's `event_date` or `publication_date`.
Structural validity does not validate endpoint existence, create a context
identity, certify semantic correctness, or establish authority.

This package does not own registries, uniqueness, duplicate handling,
collection behavior, or conflicts when one context ID is associated with
multiple dates. It does not implement temporal ordering, baseline/current
roles, semantic proposition production, Signal, Hypothesis, Thesis, portfolio
impact, materiality, scoring, confidence, runtime execution, persistence,
migration, orchestration, recommendations, CIO judgment, or capital
allocation.

Production code depends only on the Python standard library and this package.
EvidenceProposition and all existing packages remain independent and
unchanged.
