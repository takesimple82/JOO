# Portfolio Allocation Leg Risk Budget Link Applicability

## Purpose and public API

`PortfolioAllocationLegRiskBudgetLinkApplicability` classifies one complete,
caller-supplied set containing one accepted Risk Budget Link, Allocation Leg,
Risk Budget, Capital Bucket, and Position. Its complete public API is:

- `PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus`
- `classify_portfolio_allocation_leg_risk_budget_link_applicability()`

The status is a standard `enum.Enum` with, in order,
`ALLOCATION_LEG_ENDPOINT_MISMATCH`, `RISK_BUDGET_ENDPOINT_MISMATCH`,
`CAPITAL_BUCKET_ENDPOINT_MISMATCH`, `POSITION_ENDPOINT_MISMATCH`,
`PORTFOLIO_ENDPOINT_MISMATCH`, and `APPLICABLE`. Classification returns only
one of these enum singletons. There is no persistent applicability identity,
applicability record, or result dataclass.

## Required inputs and validation

The classifier requires exactly five positional-or-keyword inputs in order:
`risk_budget_link`, `leg`, `risk_budget`, `capital_bucket`, and `position`.
Absence is outside invocation and has no `None`, sentinel, default, optional
parameter, or missing-input status representation.

Before comparison, the classifier validates the exact supplied objects once
each and in that order using their accepted upstream validators. All five
validations complete before any comparison. The first upstream failure stops
later validation and every comparison, and the exact exception object
propagates unchanged. This package duplicates no upstream type, field,
blankness, retained-model, Membership, or field-order validation.

## Ordered classification

After validation, exact stored string equality is compared in this order:

1. Link `allocation_leg_id` against Leg `allocation_leg_id`.
2. Link `risk_budget_id` against Risk Budget `risk_budget_id`.
3. Risk Budget `capital_bucket_id` against Capital Bucket
   `capital_bucket_id`.
4. `leg.link.position_id` against Position `position_id`.
5. Capital Bucket `portfolio_id` against
   `position.membership.portfolio_id`.

The corresponding mismatch status is returned and the first mismatch wins;
later comparisons do not run. Only full alignment returns `APPLICABLE`.
Equality is exact: there is no trimming, case folding, Unicode normalization,
coercion, canonicalization, alias handling, lookup, inference, mutation,
replacement, or reconstruction.

`APPLICABLE` means only endpoint identity and Portfolio alignment for this
exact supplied validated set. It does not prove endpoint existence, truth,
currency, uniqueness, completeness, economic suitability, authorization, or
execution eligibility.

## Multiplicity, independence, and dependency direction

M50 optionality, many-at-either-endpoint multiplicity, shared endpoints, and
acceptance of independently supplied exact duplicates remain unchanged. Each
complete set is classified independently. This package owns no collection,
uniqueness, coverage, aggregation, selection, reverse index, or deduplication.

Classification is independent of M49, M51, and M52: none is an input,
prerequisite, consumed result, or reclassification target. Dependencies flow
only from this applicability package to the five accepted upstream model and
validator packages; upstream packages do not depend on this package. The
status model depends only on standard-library `enum`.

## Non-responsibilities

This package does not create, persist, find, resolve, validate existence of,
or repair endpoints. It does not enforce M49, reclassify M51 or M52, interpret
M48 quantities, or own funding amounts, balances, capacity, cash, currency,
price, NAV, valuation, FX, risk amounts, limits, thresholds, utilization,
concentration, breaches, severity, or remediation.

It owns no constraint taxonomy, definition, policy, applicability,
evaluation, satisfaction, or enforcement; Recommendation action; approval,
override, explainability, audit, execution, lifecycle, runtime, orchestration,
service, API, CLI, scheduling, monitoring, or automation behavior.
