# Evidence Proposition

## Purpose

Evidence Proposition owns accepted atomic semantic proposition contracts and
their structural validation. M1 supports only one family: one exact observed
finite numeric value for one canonical subject, single-valued predicate, unit,
and effective context.

## ExactObservedNumericProposition

The model contains, in order:

- `proposition_id`
- `finding_id`
- `subject_id`
- `predicate_id`
- `value`
- `unit_id`
- `effective_context_id`

The model is frozen, has no defaults, and stores every supplied value directly.
`value` is an exact `decimal.Decimal`.

## Validation

`validate_exact_observed_numeric_proposition()` performs structural validation
only. It requires the exact proposition model type, exact built-in `str`
identifier values with non-whitespace content, and an exact finite `Decimal`.
It returns `None` on success.

Validation does not trim, case-fold, normalize, quantize, round, copy, parse,
or convert values. Surrounding whitespace on an otherwise nonblank identifier
is accepted and preserved. Decimal exponent, trailing zeros, and signed-zero
representation remain unchanged.

Decimal equality is mathematical numeric equality. For example,
`Decimal("1.0")` equals `Decimal("1.00")`, and `Decimal("0")` equals
`Decimal("-0")`, while their supplied representations remain preserved.

## Producer Assumption

One authoritative future Knowledge Engine producer owns semantic extraction,
canonical identifiers, numeric exactness, unit and scale interpretation, and
effective-context interpretation. Semantic correctness is producer-owned and
is not established by this structural validator. Cross-producer comparison is
unsupported.

## Boundaries

A structurally valid proposition does not establish truth, extraction accuracy,
source reliability, freshness, authority, revision preference, compatibility,
numerical incompatibility, or contradiction.

This package does not support approximate values, estimates, forecasts,
guidance, targets, ranges, directional claims, tolerances, rounding
reconciliation, unit or currency conversion, comparison, or contradiction.
Extraction, finding-object linkage, aggregation-item linkage, comparison, and
contradiction remain deferred.

Production code depends only on the Python standard library and this package.
It does not execute providers or runtimes, parse source text, query registries,
or depend on Research Domain or Evidence Aggregation. Evidence Aggregation
remains independent and unchanged.
