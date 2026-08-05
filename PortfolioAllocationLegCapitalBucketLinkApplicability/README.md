# Portfolio Allocation Leg Capital Bucket Link Applicability

## Responsibility and public API

`PortfolioAllocationLegCapitalBucketLinkApplicability` deterministically
classifies one explicitly supplied complete comparison set containing one
accepted M49 Leg-to-Capital-Bucket link, one accepted Allocation Leg, one
accepted Capital Bucket, and one accepted Position. It checks only endpoint
identity and Portfolio alignment in frozen order.

The complete and exact public API is:

- `PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus`
- `classify_portfolio_allocation_leg_capital_bucket_link_applicability()`

There is no package-root re-export, validator, unchecked classifier, result
dataclass, applicability record, persistent result identity, Boolean helper,
or additional API.

## Status contract

`PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus` is a standard
`Enum` with exactly these members, explicit string values, and order:

1. `ALLOCATION_LEG_ENDPOINT_MISMATCH`
2. `CAPITAL_BUCKET_ENDPOINT_MISMATCH`
3. `POSITION_ENDPOINT_MISMATCH`
4. `PORTFOLIO_ENDPOINT_MISMATCH`
5. `APPLICABLE`

Every value is exactly its member name. The enum has no aliases, custom
constructor, methods, properties, metadata, ranking, severity, Boolean
conversion, or persistent identity.

## Complete inputs, validation, and exceptions

The classifier accepts exactly four required positional-or-keyword inputs in
order:

1. `capital_bucket_link: ExplicitPortfolioAllocationLegCapitalBucketLink`
2. `leg: ExplicitPortfolioAllocationLeg`
3. `capital_bucket: ExplicitPortfolioCapitalBucket`
4. `position: ExplicitPortfolioPosition`

Absence is outside invocation. Before any comparison, the classifier invokes
the accepted validators exactly once each in that order with the exact supplied
objects. The first upstream failure stops processing; later validators and all
comparisons are skipped. Its exception object propagates unchanged without
catching, wrapping, translating, replacing, suppressing, or aggregating it.
This package duplicates no upstream field or retained-model validation.

## Ordered classification and exact equality

After every validator succeeds, exact stored string equality is evaluated in
this order, and the first mismatch wins:

1. link `allocation_leg_id` versus Leg `allocation_leg_id` returns
   `ALLOCATION_LEG_ENDPOINT_MISMATCH`;
2. link `capital_bucket_id` versus Capital Bucket `capital_bucket_id` returns
   `CAPITAL_BUCKET_ENDPOINT_MISMATCH`;
3. Leg retained Proposal Position Link `position_id` versus Position
   `position_id` returns `POSITION_ENDPOINT_MISMATCH`;
4. Capital Bucket `portfolio_id` versus Position Membership `portfolio_id`
   returns `PORTFOLIO_ENDPOINT_MISMATCH`; and
5. complete alignment returns `APPLICABLE`.

Comparison performs no trimming, case folding, Unicode normalization,
coercion, conversion, aliasing, canonicalization, copying, reconstruction,
lookup, traversal beyond supplied retained models, resolution, or inference.
Every supplied model, retained object, and stored field is preserved without
mutation or replacement.

`APPLICABLE` means only that the four exact identity comparisons align for the
supplied validated set. It does not establish endpoint existence outside the
supplied records, M45 applicability, uniqueness, funding sufficiency, risk
acceptance, constraint satisfaction, authorization, approval, trade
permission, or execution eligibility.

## Optionality, multiplicity, and collection boundary

M49 remains optional at its structural boundary. M52 is invoked only for a
caller-supplied complete set; absence creates no result or status. M49 permits
many links sharing either endpoint and independently supplied exact duplicates,
and M52 leaves that contract unchanged. Any such valid record can be
classified independently.

This package owns no collection, reverse collection, lookup, enumeration,
selection, ordering, aggregation, uniqueness, coverage, duplicate detection or
rejection, one-Bucket-per-Leg rule, or collection-level consistency.

## Dependency and non-responsibility boundary

`models.py` depends only on standard-library `enum`. `classification.py`
depends only on this package's status and the accepted M49 link, Allocation
Leg, Capital Bucket, and Position models and validators. Dependencies flow
only downstream from M52 to those accepted packages. M52 is independent of
M50 and M51 and neither requires nor infers their records or results.

This package does not own endpoint production, mutation, repair, persistence,
existence proof, registry, repository, resolver, service, mapping, automatic
entity resolution, or M45 chain reclassification. It owns no M48 quantity or
unit interpretation; amount, capital, cash, balance, capacity, funding,
reservation, currency, price, valuation, FX, NAV, risk, limit, utilization,
ratio, percentage, weight, target, delta, or rebalance calculation.

It performs no constraint taxonomy, policy, applicability, evaluation,
satisfaction, enforcement, breach handling, recommendation-action
interpretation, semantic production, inference, ranking, suitability,
approval, rejection, override, explainability, audit, execution, lifecycle,
runtime, orchestration, workflow, CLI, automation, scheduling, monitoring,
external API integration, hidden state, or third-party behavior.
