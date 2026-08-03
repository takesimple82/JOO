# Portfolio Allocation Proposal Position Link Applicability

## Responsibility and public API

This package deterministically classifies whether one accepted Portfolio
Allocation Proposal Position Link is associated with the supplied Allocation
Proposal and Position endpoints, connected through the supplied Recommendation
and Portfolio Snapshot endpoints, and Portfolio-aligned between the supplied
Position and Snapshot. Its exact public API is:

- `PortfolioAllocationProposalPositionLinkApplicabilityStatus`
- `classify_portfolio_allocation_proposal_position_link_applicability()`

There is no public unchecked classifier, persistent identifier, endpoint, or
dataclass.

## Status contract

`PortfolioAllocationProposalPositionLinkApplicabilityStatus` is an `Enum` with
exactly these members, explicit string values, and order:

1. `ALLOCATION_PROPOSAL_ENDPOINT_MISMATCH`
2. `POSITION_ENDPOINT_MISMATCH`
3. `RECOMMENDATION_ENDPOINT_MISMATCH`
4. `PORTFOLIO_SNAPSHOT_ENDPOINT_MISMATCH`
5. `PORTFOLIO_ENDPOINT_MISMATCH`
6. `APPLICABLE`

Every value is exactly the corresponding member name. The enum has no aliases,
custom methods, properties, labels, descriptions, ranking, severity, or boolean
conversion.

## Inputs and validation

`classify_portfolio_allocation_proposal_position_link_applicability()` accepts,
in order:

1. `link: ExplicitPortfolioAllocationProposalPositionLink`
2. `proposal: ExplicitPortfolioAllocationProposalEndpoint`
3. `recommendation: ExplicitPortfolioRecommendationEndpoint`
4. `snapshot: ExplicitPortfolioSnapshot`
5. `position: ExplicitPortfolioPosition`

Before any comparison, it calls the accepted validators exactly once each in
that same order. The first upstream exception propagates unchanged; exceptions
are not caught, wrapped, translated, suppressed, or aggregated.

## Ordered classification

After all validation succeeds, the first unequal comparison determines the
result:

1. `link.allocation_proposal_id == proposal.allocation_proposal_id`
2. `link.position_id == position.position_id`
3. `proposal.recommendation_id == recommendation.recommendation_id`
4. `recommendation.portfolio_snapshot_id == snapshot.portfolio_snapshot_id`
5. `position.membership.portfolio_id == snapshot.observation_context.portfolio_id`

If all five comparisons match, the result is `APPLICABLE`. This order is
frozen, and the first mismatch wins.

Portfolio alignment means only the fifth exact equality. The classifier does
not inspect or search Snapshot holding observations, holding snapshots,
watchlist entries, or any other collection. A Position need not already be held
or watchlisted, and empty holdings and watchlist collections do not prevent an
otherwise applicable result.

## Exact-value, preservation, and multiplicity semantics

Comparisons use exact stored equality. The classifier does not trim, normalize
Unicode, case-fold, coerce, convert, copy, reconstruct, derive, hash, generate,
alias, canonicalize, or resolve identifiers. It preserves and does not mutate
every supplied object and field value and returns only an enum member.

The classifier is pure and stateless. It does not enforce uniqueness,
collection membership, duplicate rejection, one-to-one or one-to-many policy,
ordering, completeness, ranking, or precedence beyond the frozen mismatch
order. Duplicate structurally equal inputs and repeated calls produce the same
deterministic result.

## Dependency and responsibility boundaries

Production code depends only on the Python standard library, the accepted
PortfolioAllocationProposalPositionLink, PortfolioAllocationProposalEndpoint,
PortfolioRecommendationEndpoint, PortfolioSnapshot, and PortfolioPosition
models and validators, and this package.

This package does not own or perform endpoint production, existence proof,
lookup, repositories, registries, resolvers, persistence, migrations,
collection scans, holding-membership or watchlist checks, existing-position or
new-position policy, allocation content or completeness, quantity, amount,
currency, unit, percentage, ratio, weights, rebalance or capital movement,
Capital Bucket or Risk Budget association or application, recommendation action
or direction, Expected Value, Impact, Thesis, Evidence, Finding, assumption
linkage, constraints, policy or threshold evaluation, breach detection,
ranking, confidence, priority, urgency, materiality, approval, rejection,
override, execution, lifecycle, additional status, explainability, audit,
runtime, orchestration, CLI, automation, scheduling, monitoring, or workflow.
