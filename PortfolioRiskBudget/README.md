# Explicit Portfolio Risk Budget

## Responsibility and public API

This package owns one persistent Portfolio Risk Budget structural endpoint
associated with one Portfolio Capital Bucket identity. Its exact public API is:

- `ExplicitPortfolioRiskBudget`
- `validate_explicit_portfolio_risk_budget()`

## Model

`ExplicitPortfolioRiskBudget` is a frozen, hashable structural dataclass
containing exactly these fields in order:

1. `risk_budget_id: str`
2. `capital_bucket_id: str`

The model has no defaults, `__post_init__`, slots, custom methods, or
additional fields. Structural equality uses the two exact stored values.

## Identity and association

`risk_budget_id` is an opaque caller-supplied identifier canonical only within
the Portfolio Risk Budget namespace. It encodes no amount, limit, threshold,
policy, meaning, state, or lifecycle.

`capital_bucket_id` is a caller-supplied foreign opaque identifier referencing
the accepted Portfolio Capital Bucket identity namespace. The model stores the
identifier directly and does not retain an `ExplicitPortfolioCapitalBucket`
object or duplicate its `portfolio_id` association.

Neither identifier is generated, derived, hashed, normalized, trimmed, case
folded, converted, copied, or reconstructed.

## Validation order

`validate_explicit_portfolio_risk_budget()` validates exactly:

1. the exact `ExplicitPortfolioRiskBudget` model type;
2. `risk_budget_id` as an exact nonblank built-in `str`;
3. `capital_bucket_id` as an exact nonblank built-in `str`; and
4. returns `None`.

## Preservation and structural invariants

Both fields remain the exact caller-supplied string objects and values.
Surrounding whitespace on an otherwise nonblank value is accepted and
preserved. String subclasses are rejected.

Structural validity establishes only the exact model and identifier shapes. It
does not prove uniqueness, Portfolio or Capital Bucket existence, economic
meaning, risk capacity, or suitability for allocation. Multiple Risk Budget
identities may reference the same exact `capital_bucket_id`.

## Non-responsibilities

This package does not own Portfolio or Capital Bucket production or existence,
Portfolio Membership, Portfolio Position, holdings, watchlists, Portfolio
snapshots, risk amounts, limits, thresholds, tolerances, utilization,
remaining capacity, ratios, percentages, target weights, concentration
metrics, currencies, quantity units, cash, prices, cost basis, valuation, P&L,
observation contexts, timestamps, names, labels, descriptions, kinds,
categories, purposes, taxonomy, policy, applicability, semantic production,
calculation, breach detection, monitoring, recommendations, allocation,
constraints, execution, Portfolio Impact, Expected Value, lookup, registries,
uniqueness enforcement, persistence, migration, runtime, orchestration, CLI,
automation, approval, override, or audit.
