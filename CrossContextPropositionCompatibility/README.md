# Cross-Context Proposition Compatibility

This package deterministically classifies whether two semantically produced
exact numeric propositions represent the same numeric concept across
effective contexts.

## Public contract

`CrossContextPropositionCompatibilityStatus` has exactly four states, in
precedence order:

1. `SUBJECT_MISMATCH`
2. `PREDICATE_MISMATCH`
3. `UNIT_MISMATCH`
4. `COMPATIBLE`

`classify_cross_context_proposition_compatibility()` accepts baseline and
current `SemanticallyProducedNumericProposition` wrappers. It validates the
baseline first and current second, stops at the first failure, and propagates
upstream exceptions unchanged.

After validation, the classifier compares stored `subject_id`, `predicate_id`,
and `unit_id` fields exactly in that order. It performs no trimming, case
folding, Unicode normalization, conversion, copying, or reconstruction.

`effective_context_id` equality is not required and equal contexts are not
rejected. Proposition IDs, finding IDs, and numeric values do not participate
in compatibility. Every input wrapper, proposition, and field object remains
unchanged.

## Non-responsibilities

This package does not own pair endpoint applicability, temporal ordering,
baseline/current selection, numeric equality or delta, increase/decrease
direction, materiality, Signal production, unit conversion, confidence,
scoring, Hypothesis, Thesis, Portfolio impact, runtime, persistence,
orchestration, or CIO decisions.
