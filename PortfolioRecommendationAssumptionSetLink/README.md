# Portfolio Recommendation to Expected Value Assumption Set Link

## Responsibility and public API

This package owns one explicit directed structural link from one accepted
Portfolio Recommendation identity to one accepted Expected Value Assumption
Set identity. Its exact public API is:

- `ExplicitPortfolioRecommendationAssumptionSetLink`
- `validate_explicit_portfolio_recommendation_assumption_set_link()`

## Model

`ExplicitPortfolioRecommendationAssumptionSetLink` is a frozen, hashable
structural dataclass containing exactly these fields in order:

1. `recommendation_id: str`
2. `assumption_set_id: str`

The model has no defaults, `__post_init__`, slots, custom methods, additional
fields, `link_id`, or independent identity. Structural equality and hashing
use the two exact stored identifier values.

## Foreign identities and relation semantics

`recommendation_id` is a foreign opaque identifier owned by the accepted
Portfolio Recommendation namespace. `assumption_set_id` is a foreign opaque
identifier owned by the accepted Expected Value Assumption Set namespace. The
link stores both identifiers directly and retains no upstream object.

The relation records only that the Recommendation identity is explicitly
associated with the Expected Value Assumption Set identity for structural
traceability. It does not prove that the assumption set caused, supports, or
justifies the Recommendation; is necessary, sufficient, or complete; is
correctly applicable; or corresponds to a linked Portfolio Impact.

## Validation order

`validate_explicit_portfolio_recommendation_assumption_set_link()` validates
exactly:

1. the exact `ExplicitPortfolioRecommendationAssumptionSetLink` model type;
2. `recommendation_id` as an exact nonblank built-in `str`;
3. `assumption_set_id` as an exact nonblank built-in `str`; and
4. returns `None`.

## Preservation and multiplicity

Both fields remain the exact caller-supplied string objects and values.
Surrounding whitespace on an otherwise nonblank value is accepted and
preserved. Validation does not trim, normalize, case fold, transform, coerce,
convert, copy, reconstruct, derive, hash, generate, or infer identifiers.

Multiple Assumption Set links per Recommendation and multiple Recommendation
links per Assumption Set are allowed. Duplicate exact pairs are structurally
accepted. This package owns no collection, ordering, uniqueness, lookup,
existence, or applicability contract.

## Dependency boundary

Production code depends only on the Python standard library and files inside
this package. It does not import or invoke any upstream domain model or
validator.

## Non-responsibilities

This package does not own Recommendation or Assumption Set production or
existence, endpoint lookup, registries, repositories, resolvers, persistence,
endpoint applicability, Impact consistency, probability-total applicability,
Expected Value calculation, result identity or numeric value, source
sufficiency, completeness, ranking, precedence, ordering, source-link
collections or aggregates, Thesis, Evidence, Finding, Proposition, Hypothesis,
or Signal linkage, recommendation action, direction, target, rationale,
confidence, priority, urgency, conviction, materiality, allocation proposals,
capital movement, quantity, amount, currency, unit, percentage, weight,
Capital Bucket or Risk Budget application, constraints, policies, thresholds,
breach detection, explainability narrative, approval, rejection, override,
execution, audit, lifecycle, status, timestamps, migration, runtime,
orchestration, CLI, automation, or scheduling.
