# Evidence Contradiction

## Purpose

Evidence Contradiction classifies whether two accepted
`ExactObservedNumericProposition` objects form a contradiction candidate. It
delegates comparison to the frozen Evidence Comparison contract and performs
no direct validation or proposition inspection.

## Status Mapping

The comparison function is called exactly once with the original left and
right objects. Its result maps directly:

- `NOT_COMPARABLE` becomes `NOT_ELIGIBLE`.
- `NUMERICALLY_COMPATIBLE` becomes `NO_CONTRADICTION_CANDIDATE`.
- `NUMERICALLY_INCOMPATIBLE` becomes `CONTRADICTION_CANDIDATE`.

`NOT_ELIGIBLE` means the pair could not be evaluated under the accepted
four-field comparison identity. `NO_CONTRADICTION_CANDIDATE` means this pair
does not form a candidate under the exact numeric M1 contract. These outcomes
are distinct.

A contradiction candidate is not a final contradiction, truth judgment,
source fault, evidence rejection, or resolution. Unknown comparison statuses
raise a stable `RuntimeError`.

## Validation and Symmetry

The frozen comparison function owns proposition validation and validates left
before right. Its exceptions propagate unchanged. Evidence Contradiction does
not validate either proposition directly or duplicate comparison behavior.

For valid inputs, classification status is symmetric when argument order is
reversed. The same proposition may occupy both positions and then produces
`NO_CONTRADICTION_CANDIDATE`.

## Boundaries

Source independence is not required. Comparable unequal propositions from the
same finding, source, provider, or source reference may still be candidates.
This package does not inspect proposition IDs, finding IDs, sources,
provenance, assessments, dates, chronology, freshness, corrections,
restatements, revisions, or supersession.

The classifier does not mutate, reconstruct, normalize, compare, log, persist,
or cache proposition data. It does not call providers or runtimes.

Production code depends only on Evidence Proposition, Evidence Comparison,
this package, and the Python standard library. Evidence Proposition, Evidence
Comparison, and Evidence Aggregation remain independent and unchanged.
Chronology, authority, revision, truth selection, and candidate resolution
belong to a future Evidence Resolution boundary.
