# Explicit Portfolio Endpoint

This package owns the minimum canonical Portfolio endpoint contract.

`ExplicitPortfolio` is a frozen, hashable structural model containing exactly:

1. `portfolio_id: str`

The identity is an opaque, caller-supplied identifier that is canonical only
within the Portfolio namespace. It does not encode an owner, account, strategy,
objective, currency, version, state, or lifecycle, and it is never generated
or inferred automatically.

`validate_explicit_portfolio()` requires the exact model type followed by an
exact nonblank built-in `str` identity. It returns `None` on success. The
validator does not trim, normalize, case fold, convert, copy, or reconstruct
the model or identity. Surrounding whitespace on an otherwise nonblank
identity is accepted and preserved.

Portfolio identity is distinct from `PortfolioSubject.subject_id`, ticker or
security identifiers, Evidence Proposition identifiers, Research Planner
entity fields, research snapshot identifiers, portfolio versions, names, and
file paths.

## Non-responsibilities

This package does not own Portfolio Subjects, membership, positions, holding
state or observations, watchlists, snapshots, accounts, owners, strategies,
objectives, currencies, capital, allocation, constraints, recommendations,
tickers, securities, lookup, normalization, uniqueness, registries,
persistence, migration, lifecycle, runtime, or orchestration.

Downstream membership, position, holding, watchlist, and snapshot contracts are
intentionally not present.
