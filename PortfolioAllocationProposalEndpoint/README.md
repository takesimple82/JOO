# Explicit Portfolio Allocation Proposal Endpoint

## Responsibility and public API

This package owns one explicit Portfolio Allocation Proposal structural
endpoint associated with one Portfolio Recommendation identity. Its exact
public API is:

- `ExplicitPortfolioAllocationProposalEndpoint`
- `validate_explicit_portfolio_allocation_proposal_endpoint()`

## Model and field ownership

`ExplicitPortfolioAllocationProposalEndpoint` is a frozen, hashable structural
dataclass containing exactly these fields in order:

1. `allocation_proposal_id: str`
2. `recommendation_id: str`

`allocation_proposal_id` is owned by this package.
`recommendation_id` is a foreign opaque identifier owned by the Portfolio
Recommendation namespace. The model has no defaults, `__post_init__`, slots,
custom methods, additional fields, content, lifecycle fields, timestamps,
labels, `link_id`, or target, Portfolio, Portfolio Snapshot, Capital Bucket,
or Risk Budget identifiers.

## Validation order

`validate_explicit_portfolio_allocation_proposal_endpoint()` validates exactly:

1. the exact `ExplicitPortfolioAllocationProposalEndpoint` model type;
2. `allocation_proposal_id` as an exact nonblank built-in `str`;
3. `recommendation_id` as an exact nonblank built-in `str`; and
4. returns `None`.

## Exact-string and preservation semantics

String subclasses, empty strings, and whitespace-only strings are rejected.
Surrounding whitespace on an otherwise nonblank value is accepted. Both fields
preserve the exact caller-supplied string object and value. Validation does not
trim, normalize, case fold, convert, coerce, copy, reconstruct, derive,
generate, or infer either identifier.

## Foreign-ID-only, multiplicity, and duplicate behavior

The endpoint stores only the foreign `recommendation_id`; it does not retain an
`ExplicitPortfolioRecommendationEndpoint` object, import Portfolio
Recommendation production code, or invoke an upstream validator. Each proposal
stores exactly one Recommendation identity. Multiple Allocation Proposals may
share the same `recommendation_id`, and duplicate exact
`allocation_proposal_id` and `recommendation_id` pairs are structurally
accepted. The package owns no collection, ordering, uniqueness, lookup, or
existence behavior.

Structural validation does not prove Recommendation existence or uniqueness,
Proposal uniqueness, endpoint applicability, or semantic suitability.

## Dependency boundary

Production code depends only on the Python standard library and this package's
own model. It imports no existing JOO domain package.

## Non-responsibilities

This package does not own or perform Recommendation, Portfolio Snapshot,
Portfolio, Membership, Position, Capital Bucket, or Risk Budget production or
existence; endpoint lookup or existence proof; uniqueness enforcement; target
asset, membership, position, instrument, or subject selection; recommendation
action or direction; quantity, amount, currency, unit, percentage, ratio,
current weight, target weight, proposed weight, weight delta, rebalance amount,
capital movement, cash routing, or funding source; Expected Value calculation
or storage; Impact, Thesis, Evidence, Finding, assumption, Capital Bucket, or
Risk Budget linkage or application; constraint definition, evaluation, policy,
threshold evaluation, or breach detection; recommendation or proposal ranking;
confidence, priority, urgency, or materiality; approval, rejection, override,
execution, lifecycle status, explainability narrative, or audit events; or
registries, repositories, resolvers, persistence, migration, runtime,
orchestration, CLI, automation, or scheduling.
