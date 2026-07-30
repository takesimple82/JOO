# Exact Cross-Context Numeric Delta Applicability

This package classifies whether supplied baseline/current semantic proposition
inputs are structurally and semantically eligible for exact numeric delta
calculation.

## Public contract

`ExactCrossContextNumericDeltaApplicabilityStatus` has these states in outcome
precedence order:

1. `BASELINE_PROPOSITION_ENDPOINT_MISMATCH`
2. `CURRENT_PROPOSITION_ENDPOINT_MISMATCH`
3. `BASELINE_CONTEXT_ENDPOINT_MISMATCH`
4. `CURRENT_CONTEXT_ENDPOINT_MISMATCH`
5. `CONTEXT_DATE_CONFLICT`
6. `SAME_DATE`
7. `BASELINE_AFTER_CURRENT`
8. `SUBJECT_MISMATCH`
9. `PREDICATE_MISMATCH`
10. `UNIT_MISMATCH`
11. `CALCULABLE`

`classify_exact_cross_context_numeric_delta_applicability()` validates, in
order, the explicit pair, baseline semantic production, current semantic
production, baseline context-date association, and current context-date
association. The first upstream failure stops processing and its exception
object propagates unchanged.

After validation, classification delegates to the accepted private unchecked
logic beneath pair applicability using the original wrapped proposition
objects. Pair and temporal invalidity takes precedence. Only an `APPLICABLE`
pair proceeds to the private unchecked cross-context compatibility logic.
`COMPATIBLE` maps to `CALCULABLE`; all other statuses map one-to-one.

The public upstream classifiers remain independently validation-first. Their
private unchecked helpers are internal implementation details and are not
public API.

## Boundaries

The classifier does not subtract or inspect numeric values, construct a delta,
convert units, select baseline/current inputs, normalize or copy data, or
implement direction, materiality, Signal, endpoint lookup, runtime,
persistence, orchestration, Hypothesis, Thesis, or Portfolio impact.
