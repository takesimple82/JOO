# Explicit Portfolio Capital Bucket

## Responsibility and public API

This package owns one persistent capital-bucket structural endpoint associated
with one caller-supplied Portfolio identity. Its exact public API is:

- `ExplicitPortfolioCapitalBucket`
- `validate_explicit_portfolio_capital_bucket()`

## Model

`ExplicitPortfolioCapitalBucket` is a frozen, hashable structural dataclass
containing exactly these fields in order:

1. `capital_bucket_id: str`
2. `portfolio_id: str`

The model has no defaults, `__post_init__`, slots, custom methods, or
additional fields. Structural equality uses the two exact stored values.

## Identity namespace

`capital_bucket_id` is an opaque caller-supplied identity canonical only
within the Portfolio Capital Bucket namespace. It is required and does not
encode a name, label, description, kind, category, purpose, taxonomy, capital
amount, or lifecycle. It is not generated, derived, hashed, or normalized.

`portfolio_id` is stored directly as the associated Portfolio identity. The
model does not retain an `ExplicitPortfolio` object. Multiple Capital Buckets
may share the same exact `portfolio_id`.

## Validation order

`validate_explicit_portfolio_capital_bucket()` validates exactly:

1. the exact `ExplicitPortfolioCapitalBucket` model type;
2. `capital_bucket_id` as an exact nonblank built-in `str`;
3. `portfolio_id` as an exact nonblank built-in `str`; and
4. returns `None`.

## Preservation and structural invariants

Both identifiers remain the exact caller-supplied string objects and values.
Validation does not trim, normalize, case fold, convert, copy, or reconstruct
them. Surrounding whitespace on an otherwise nonblank value is accepted and
preserved.

Structural validity establishes only the exact model and identifier shapes. It
does not prove endpoint existence, global or per-Portfolio uniqueness,
economic meaning, capital-amount truth, or allocation suitability.

## Non-responsibilities

This package does not own Portfolio endpoint production or existence,
Portfolio Membership, Portfolio Position, holdings, watchlists, Portfolio
snapshots, observed capital amounts, cash balances, quantity units, currency,
prices, cost basis, valuation, profit or loss, percentages, target weights,
concentration metrics, risk budgets, constraints, recommendations, allocation,
execution, bucket names, labels, descriptions, kinds, categories, purposes,
taxonomy, observation contexts, timestamps, applicability, semantic
production, calculations, lookup, registries, persistence, migration, runtime,
orchestration, CLI, automation, human approval, override, or audit.
