# Portfolio Allocation Proposal Position Link

## Responsibility and public API

This package records one explicit structural association between one Portfolio
Allocation Proposal identity and one Portfolio Position identity. Its exact
public API is:

- `ExplicitPortfolioAllocationProposalPositionLink`
- `validate_explicit_portfolio_allocation_proposal_position_link()`

## Model, field order, and ownership

`ExplicitPortfolioAllocationProposalPositionLink` is a frozen, hashable
dataclass containing exactly these fields in order:

1. `allocation_proposal_id: str`
2. `position_id: str`

`allocation_proposal_id` is a foreign opaque identifier owned by the Portfolio
Allocation Proposal namespace. `position_id` is a foreign opaque identifier
owned by the Portfolio Position namespace. The model has no defaults, default
factories, slots, `__post_init__`, custom methods, `link_id`, timestamps,
labels, status fields, extra fields, or embedded upstream objects.

## Validation order

`validate_explicit_portfolio_allocation_proposal_position_link()` validates
exactly:

1. the exact `ExplicitPortfolioAllocationProposalPositionLink` model type;
2. `allocation_proposal_id` as an exact built-in `str`;
3. that `allocation_proposal_id` is not empty or whitespace-only;
4. `position_id` as an exact built-in `str`;
5. that `position_id` is not empty or whitespace-only; and
6. returns `None`.

Model subclasses and string subclasses are rejected. Surrounding whitespace on
an otherwise nonblank identifier is accepted.

## Exact-string and preservation semantics

Each field preserves the exact caller-supplied string object and value.
Validation performs no trimming, normalization, case folding, coercion,
conversion, copying, reconstruction, generation, or inference. Equality is
exact structural equality over both stored strings.

## Foreign-ID-only boundary

The link retains only the two foreign identifiers. It does not retain an
Allocation Proposal or Position object, import either production package,
invoke upstream validators, look up either endpoint, or prove endpoint
existence. Structural validity does not prove portfolio alignment,
applicability, uniqueness, completeness, suitability, or execution readiness.

## Multiplicity and duplicate behavior

Many Position links may share one `allocation_proposal_id`.
Many Allocation Proposal links may share one `position_id`; duplicate exact pairs are
structurally accepted. This package owns no uniqueness enforcement, collection,
ordering contract, or single-target policy.

## Dependency boundary

Production code depends only on the Python standard library and this package's
own model. It imports no existing JOO domain package.

## Non-responsibilities

This package does not own or perform Allocation Proposal, Position, or
Recommendation production or existence; Portfolio or Portfolio Snapshot
production; Membership or Portfolio Subject production; endpoint lookup or
registries; uniqueness enforcement; portfolio alignment or applicability;
position or snapshot membership validation; target completeness, ranking, or
precedence; quantity, amount, currency, unit, percentage, ratio, current,
proposed, or target weight, weight delta, rebalance amount, capital movement,
cash routing, or funding source; Capital Bucket or Risk Budget association or
application; Expected Value calculation or storage; Impact, Thesis, Evidence,
Finding, or assumption linkage; recommendation action or direction, including
BUY, HOLD, SELL, ADD, and REDUCE; constraint definition or evaluation; policy,
threshold, or breach detection; ranking, confidence, priority, urgency, or
materiality; approval, rejection, override, execution, lifecycle, status,
explainability narrative, or audit events; or repositories, resolvers,
persistence, migration, runtime, orchestration, CLI, automation, or scheduling.
