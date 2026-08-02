# Portfolio Recommendation to Impact Link

## Responsibility and public API

This package owns one explicit directed structural link from one accepted
Portfolio Recommendation identity to one accepted Portfolio Impact identity.
Its exact public API is:

- `ExplicitPortfolioRecommendationImpactLink`
- `validate_explicit_portfolio_recommendation_impact_link()`

## Model

`ExplicitPortfolioRecommendationImpactLink` is a frozen, hashable structural
dataclass containing exactly these fields in order:

1. `recommendation_id: str`
2. `impact_id: str`

The model has no defaults, `__post_init__`, slots, custom methods, additional
fields, `link_id`, or independent identity. Structural equality and hashing
use the two exact stored identifier values.

## Foreign identities and relation semantics

`recommendation_id` is a foreign opaque identifier owned by the accepted
Portfolio Recommendation Endpoint namespace. `impact_id` is a foreign opaque
identifier owned by the accepted Explicit Portfolio Impact namespace. The link
stores both identifiers directly and retains no upstream object.

The relation records only that the Recommendation identity is explicitly
associated with the Portfolio Impact identity for structural traceability. It
does not prove that the Impact caused, justified, supports, is necessary for,
or is sufficient for the Recommendation. It does not establish a complete
source set.

## Validation order

`validate_explicit_portfolio_recommendation_impact_link()` validates exactly:

1. the exact `ExplicitPortfolioRecommendationImpactLink` model type;
2. `recommendation_id` as an exact nonblank built-in `str`;
3. `impact_id` as an exact nonblank built-in `str`; and
4. returns `None`.

## Preservation and multiplicity

Both fields remain the exact caller-supplied string objects and values.
Surrounding whitespace on an otherwise nonblank value is accepted and
preserved. Validation does not trim, normalize, case fold, transform, coerce,
convert, copy, reconstruct, derive, hash, generate, or infer identifiers.

Multiple Impact links per Recommendation and multiple Recommendation links per
Impact are allowed. Duplicate exact pairs are structurally accepted. This
package owns no collection, ordering, uniqueness, lookup, existence, or
applicability contract.

## Non-responsibilities

This package does not own Recommendation or Portfolio Impact production or
existence, endpoint applicability, semantic proof, causal support, source
sufficiency, completeness, ranking, precedence, recommendation action,
direction, target, rationale, confidence, priority, urgency, conviction,
materiality, Thesis, Expected Value, assumption-set, Proposition, Finding, or
Evidence linkage, semantic production, allocation proposals, capital movement,
quantity, amount, currency, unit, percentage, weight, Capital Bucket or Risk
Budget application, constraints, policy, thresholds, breach detection,
recommendation lifecycle or status, approval, rejection, override, execution,
explainability narrative, audit events, registries, repositories, resolvers,
persistence, migration, orchestration, CLI, automation, scheduling, or runtime.
