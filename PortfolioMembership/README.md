# Explicit Portfolio Membership

This package owns one explicit accepted membership relation from a canonical
Portfolio endpoint to a canonical Portfolio Subject endpoint.

`ExplicitPortfolioMembership` is a frozen, hashable dataclass containing:

1. `portfolio_id: str`
2. `portfolio_subject_id: str`

The fields refer respectively to `ExplicitPortfolio.portfolio_id` and
`PortfolioSubject.subject_id`. The relation stores the exact caller-supplied
endpoint references and creates no second identity namespace. It has no
independent membership identity.

`validate_explicit_portfolio_membership()` requires the exact membership model
and validates `portfolio_id` before `portfolio_subject_id`. Both fields must be
exact nonblank built-in strings. It returns `None` on success and preserves
each supplied string without trimming, normalization, conversion, copying, or
reconstruction.

Structural validity does not establish endpoint existence, global uniqueness,
or whether the membership is true. Duplicate relations and shared endpoints
are allowed.

## Non-responsibilities

This package does not own Portfolio or Portfolio Subject production, security
or ticker identity, positions, holding state, quantity, price, watchlists,
allocation, lifecycle, status, effective dates, accounts, strategies, lookup,
registries, persistence, migration, runtime, or orchestration.
