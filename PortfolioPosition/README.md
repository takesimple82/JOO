# Explicit Portfolio Position

This package owns one persistent Portfolio Position endpoint associated with
one accepted Portfolio Membership.

`ExplicitPortfolioPosition` is a frozen, hashable dataclass containing:

1. `position_id: str`
2. `membership: ExplicitPortfolioMembership`

`position_id` is an opaque caller-supplied identity canonical only within the
Portfolio Position namespace. It does not encode Portfolio or Portfolio
Subject endpoints, quantities, prices, state, or lifecycle. The exact supplied
membership object is retained because membership has no separate identity.

`validate_explicit_portfolio_position()` requires the exact Position model,
validates the exact nonblank built-in string identity, requires the exact
membership model, and validates that membership exactly once. Upstream
exceptions propagate unchanged. Validation preserves all supplied objects
without trimming, normalization, conversion, copying, or reconstruction.

Structural validity does not establish endpoint existence or global
uniqueness. Multiple Position identities may refer to structurally equal
memberships.

## Non-responsibilities

This package does not own membership production, holdings, shares, quantity,
price, cost basis, currency, valuation, P&L, observation context, snapshots,
lifecycle, target weight, allocation, recommendations, execution, lookup,
registries, persistence, migration, runtime, or orchestration.
