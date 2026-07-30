# EffectiveContextTemporalOrdering

EffectiveContextTemporalOrdering deterministically classifies the temporal
relationship between two accepted
`ExplicitEffectiveContextObservedDate` associations.

`classify_effective_context_temporal_ordering()` accepts the left association
and the right association. It validates the left input first and the right
input second. Upstream exceptions propagate unchanged.

After validation, classification follows this exact order:

1. If both effective-context IDs are exactly equal but their `observed_on`
   values differ, return `CONTEXT_DATE_CONFLICT`.
2. If the left observed date is earlier, return `BEFORE`.
3. If both observed dates are equal, return `SAME_DATE`.
4. Otherwise, return `AFTER`.

`EffectiveContextTemporalOrderingStatus` contains exactly:

- `CONTEXT_DATE_CONFLICT`
- `BEFORE`
- `SAME_DATE`
- `AFTER`

Strict fixed-width `YYYY-MM-DD` values have chronological string order, so the
classifier compares the validated stored strings directly. Equal context IDs
with equal dates return `SAME_DATE`. Different context IDs with equal dates
also return `SAME_DATE`.

The classifier uses exact context-ID equality only. It does not trim, case
fold, normalize Unicode, parse, rank, or otherwise interpret context IDs. It
does not mutate, copy, reconstruct, or replace either association or any field
object.

## Boundaries

A context-date conflict is reported but not resolved. The classifier does not
select an authoritative date or change either input. It does not use research
finding `event_date` or `publication_date`.

This package does not own baseline/current roles, proposition linkage or
pairing, context registries, global uniqueness, date-distance calculation,
semantic proposition production, material change, Signal, Hypothesis, Thesis,
portfolio impact, materiality, scoring, confidence, runtime execution,
persistence, migration, orchestration, recommendations, CIO judgment, or
capital allocation.

Production code depends only on EffectiveContextObservedDate, this package,
and the Python standard library. The upstream package remains independent and
unchanged.
