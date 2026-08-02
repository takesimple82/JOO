# Explicit Portfolio Recommendation Endpoint

## Responsibility and public API

This package owns one persistent Portfolio Recommendation structural endpoint
associated with one Portfolio Snapshot identity. Its exact public API is:

- `ExplicitPortfolioRecommendationEndpoint`
- `validate_explicit_portfolio_recommendation_endpoint()`

## Model

`ExplicitPortfolioRecommendationEndpoint` is a frozen, hashable structural
dataclass containing exactly these fields in order:

1. `recommendation_id: str`
2. `portfolio_snapshot_id: str`

The model has no defaults, `__post_init__`, slots, custom methods, or
additional fields. Structural equality uses the two exact stored values.

## Identity and association

`recommendation_id` is an opaque caller-supplied identifier canonical only
within the Portfolio Recommendation namespace. It encodes no action, target,
direction, rationale, confidence, priority, allocation, policy, state, or
lifecycle.

`portfolio_snapshot_id` is a caller-supplied foreign opaque identifier
referencing the accepted Portfolio Snapshot identity namespace. The model
stores the identifier directly and does not retain an
`ExplicitPortfolioSnapshot` object or duplicate its Portfolio association.
Multiple Recommendation identities may reference the same exact
`portfolio_snapshot_id`.

Neither identifier is generated, derived, hashed, normalized, trimmed, case
folded, transformed, coerced, converted, copied, reconstructed, or inferred.

## Validation order

`validate_explicit_portfolio_recommendation_endpoint()` validates exactly:

1. the exact `ExplicitPortfolioRecommendationEndpoint` model type;
2. `recommendation_id` as an exact nonblank built-in `str`;
3. `portfolio_snapshot_id` as an exact nonblank built-in `str`; and
4. returns `None`.

## Preservation and structural invariants

Both fields remain the exact caller-supplied string objects and values.
Surrounding whitespace on an otherwise nonblank value is accepted and
preserved. String subclasses are rejected.

Structural validity establishes only the exact model and identifier shapes. It
does not prove uniqueness, Portfolio Snapshot existence, recommendation truth,
semantic suitability, or suitability for action.

## Non-responsibilities

This package does not own recommendation action or direction, BUY, HOLD, SELL,
trade instructions, recommendation targets, Portfolio Subject, instrument,
Position, Membership, Capital Bucket, or Risk Budget selection, rationale,
confidence, priority, ranking, conviction, urgency, materiality, Portfolio
Impact, Expected Value, Evidence, Thesis, Hypothesis, Signal, source
traceability, allocation proposals, capital movement, quantity, amount,
currency, unit, percentage, target weight, cash routing, risk-budget
application, risk limits, thresholds, constraint definition or evaluation,
policy, breach detection, approval, rejection, override, execution, audit
events, timestamps, labels, descriptions, categories, taxonomies, endpoint
lookup, registries, repositories, resolvers, mappings, uniqueness enforcement,
persistence, migration, runtime, orchestration, CLI, automation, or scheduling.
