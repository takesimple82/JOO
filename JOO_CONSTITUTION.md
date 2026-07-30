# JOO Repository Constitution

This constitution is the highest-level architectural contract for JOO.
Roadmaps and milestone designs must remain consistent with it.

## 1. Repository Philosophy

- Define structural contracts before runtime behavior.
- Introduce explicit models before inference.
- Keep validation deterministic and validation-first.
- Separate identity, structure, applicability, semantics, calculation, and
  operation.
- Assign each architectural responsibility to exactly one explicit owner.
- Responsibilities never overlap. A later layer may consume an earlier layer
  but never assume its responsibility.
- Prefer frozen, hashable, immutable domain models.
- Add only the minimum responsibility owned by the current milestone.
- Keep accepted public contracts stable. Public APIs may change only through
  an explicitly approved architectural milestone.
- Downstream implementation convenience is never sufficient reason to modify
  an accepted public contract.
- When multiple valid architectural designs exist, stop implementation until
  one architecture is explicitly approved.
- Architecture ambiguity is never resolved through implementation.

## 2. Identity Rules

- Every persistent domain object owns an explicit caller-supplied opaque
  identity.
- IDs never encode semantics, timestamps, versions, endpoints, or state.
- IDs are never generated, derived, hashed, or inferred automatically.
- Identity validation does not establish global uniqueness or endpoint
  existence.

## 3. Validation Rules

- Require exact accepted models and exact built-in field types.
- Reject subclasses when an exact type is contracted.
- Preserve caller order and supplied model, collection, field, and value
  object identity.
- Invoke each upstream validator exactly once in the declared order.
- Propagate upstream exception objects unchanged.
- Do not normalize, trim, sort, convert, copy, or reconstruct inputs.
- Do not perform hidden inference or lookup.

## 4. Semantic Production Rules

- A semantic wrapper is only caller-supplied attestation that an accepted
  semantic producer accepted its wrapped object.
- Attestation never proves truth, correctness, causality, completeness, or
  suitability for action.
- Semantic wrappers do not add producer identity, provenance, confidence,
  probability, execution, persistence, or runtime behavior unless a later
  explicit contract separately owns that responsibility.

## 5. Applicability Rules

- Structural validation and applicability classification are separate
  responsibilities.
- A public classifier validates every upstream input exactly once before
  classification.
- A private unchecked classifier may contain only post-validation logic.
- Private unchecked classifiers may be reused only after the caller has
  completed the same required upstream validation.
- Private helpers are not public API and must not alter public observable
  behavior.

## 6. Exact Arithmetic Rules

- Decimal arithmetic is exact, deterministic, and independent of the active
  Decimal context.
- Arithmetic must not read or change context precision, rounding, traps, or
  flags.
- Exact calculations use Decimal tuples and Python integer coefficients when
  ordinary Decimal operators could apply context.
- Floating-point and implicit numeric conversion are forbidden.
- Arithmetic does not interpret domain meaning or convert units.

## 7. Calculation Rules

- Calculations consume validated semantic structures and explicit policies.
- Calculations are deterministic for the same supplied inputs.
- Calculations preserve traceability to their exact inputs.
- Calculations do not perform semantic inference, lookup, policy invention, or
  automatic identity generation.
- Non-applicable inputs remain explicit statuses or documented validation
  failures.

## 8. Repository Invariants

Domain-contract boundaries contain:

- no runtime behavior
- no persistence
- no registry
- no orchestration
- no hidden state
- no automatic ID generation
- no global singleton behavior

Any future operational layer must be separately approved, explicitly bounded,
and must not change accepted domain contracts.
