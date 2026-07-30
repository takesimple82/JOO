# Baseline/Current Proposition Pair Applicability

This package classifies whether an accepted explicit baseline/current
proposition pair is structurally and temporally applicable to supplied
proposition and effective-context observed-date endpoints.

## Public contract

`BaselineCurrentPropositionPairApplicabilityStatus` has exactly these states:

- `BASELINE_PROPOSITION_ENDPOINT_MISMATCH`
- `CURRENT_PROPOSITION_ENDPOINT_MISMATCH`
- `BASELINE_CONTEXT_ENDPOINT_MISMATCH`
- `CURRENT_CONTEXT_ENDPOINT_MISMATCH`
- `CONTEXT_DATE_CONFLICT`
- `SAME_DATE`
- `BASELINE_AFTER_CURRENT`
- `APPLICABLE`

`classify_baseline_current_proposition_pair_applicability()` accepts, in
order, an `ExplicitBaselineCurrentPropositionPair`, the baseline and current
`ExactObservedNumericProposition` endpoints, and their respective
`ExplicitEffectiveContextObservedDate` associations.

The classifier validates those five inputs in that order and propagates the
first upstream exception unchanged. It then checks the baseline proposition,
current proposition, baseline context, and current context endpoints in that
order. Temporal ordering is classified only after all endpoints match.

`BEFORE` maps to `APPLICABLE`, `SAME_DATE` maps to `SAME_DATE`, `AFTER` maps
to `BASELINE_AFTER_CURRENT`, and `CONTEXT_DATE_CONFLICT` maps to
`CONTEXT_DATE_CONFLICT`.

The classifier compares identifiers exactly and preserves every input and
field object. It does not trim, normalize, copy, reconstruct, or infer time
from an identifier. It does not read or compare proposition numeric values or
units.

## Non-responsibilities

This package does not own numeric compatibility, contradiction, material
change, Signal or semantic proposition production. It does not select
baseline/current propositions, look up endpoints, maintain a context registry,
resolve duplicate identities, calculate date distances, or implement
Hypothesis, Thesis, Portfolio impact, runtime, persistence, orchestration,
scoring, or CIO decisions.
