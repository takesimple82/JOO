# PortfolioDomain

PortfolioDomain owns the minimum Portfolio Subject contract.

`PortfolioSubject` is a frozen, hashable structural model containing exactly
these fields in order:

1. `subject_id: str`
2. `display_name: str`

The model has no defaults, custom methods, or slots.

`validate_portfolio_subject()` performs structural validation only. It requires
the exact `PortfolioSubject` model type, then validates `subject_id` and
`display_name` in field order. Each field must be an exact nonblank built-in
`str`. Validation returns `None` on success.

The model and validator preserve the original model and field objects. They do
not trim, case fold, normalize Unicode, convert, copy, or reconstruct values.
Surrounding whitespace on an otherwise nonblank field is accepted and
preserved. Equality is structural over both exact stored field values.

The single-model validator does not check whether a `subject_id` is duplicated
by another subject. Structural validity does not certify that the subject is
an entity or security.

## Non-responsibilities

This package does not own:

- portfolio membership
- holdings or positions
- quantity or average price
- ticker, exchange, market, or currency semantics
- entity or security certification
- aliases
- proposition linkage
- impact direction
- materiality or confidence
- expected value
- priority or a CIO queue
- ticker lookup
- entity resolution
- a registry
- persistence
- migration

The package performs no I/O and production code depends only on the Python
standard library and its own model.
