# Explicit Portfolio Allocation Leg

## Responsibility and public API

This package owns one explicit Portfolio Allocation Leg structural boundary:
one caller-supplied opaque Leg identity retaining one exact accepted Portfolio
Allocation Proposal Position Link. Its exact public API is:

- `ExplicitPortfolioAllocationLeg`
- `validate_explicit_portfolio_allocation_leg()`

## Model contract

`ExplicitPortfolioAllocationLeg` is a frozen, hashable dataclass containing
exactly these fields in order:

1. `allocation_leg_id: str`
2. `link: ExplicitPortfolioAllocationProposalPositionLink`

The model has no defaults, default factories, slots, `__post_init__`, custom
public methods, properties, normalization, constructor validation, derived
fields, or denormalized identifiers. It retains the exact supplied Link
object rather than copying or reconstructing it.

## Validation order and exception semantics

`validate_explicit_portfolio_allocation_leg()` validates exactly:

1. the exact `ExplicitPortfolioAllocationLeg` model type;
2. `allocation_leg_id` as an exact built-in `str`;
3. that `allocation_leg_id` is not empty or whitespace-only;
4. `link` as the exact
   `ExplicitPortfolioAllocationProposalPositionLink` model type;
5. the Link by calling
   `validate_explicit_portfolio_allocation_proposal_position_link()` exactly
   once with the exact retained object; and
6. returns `None`.

The first local validation failure wins. The upstream Link validator is not
called until every local type and value check succeeds. Its exceptions
propagate unchanged with the exact exception object identity preserved; they
are not caught, wrapped, translated, suppressed, aggregated, or replaced.
Model subclasses, string subclasses, and Link subclasses are rejected.

## Preservation semantics

`allocation_leg_id` is preserved as the exact caller-supplied string object.
Surrounding whitespace on an otherwise nonblank value is accepted and
preserved. Validation does not trim, case fold, normalize Unicode, convert,
coerce, generate, derive, look up, canonicalize, copy, or reconstruct the ID
or Link. Case and Unicode form remain exact.

## Equality, hashability, multiplicity, and duplicates

Standard frozen-dataclass equality is structural over `allocation_leg_id` and
`link`, and hashability follows the frozen dataclass contract. Distinct Leg
instances with equal fields are equal and duplicate complete Leg values are
structurally accepted.

Many Legs may reference Links sharing one `allocation_proposal_id`, and many
may reference Links sharing one `position_id`. Multiple Legs may retain the
same Link object or structurally equal distinct Links. `allocation_leg_id`
uniqueness is not enforced. This package owns no collection, ordering,
deduplication, endpoint existence proof, or one-to-one or one-to-many policy.

## Dependency boundary

Production code depends only on the Python standard library, the accepted
`PortfolioAllocationProposalPositionLink.models` and
`PortfolioAllocationProposalPositionLink.validation` modules, and this
package. It imports no applicability, endpoint, Position, Snapshot,
Membership, Recommendation, Capital Bucket, Risk Budget, Expected Value,
runtime, persistence, or third-party production code.

## Non-responsibilities

This package does not own or perform proposed absolute quantity or any other
measurable allocation content; quantity, amount, currency, unit, weight,
target, delta, or observed holding state; Snapshot collection scanning;
Capital Bucket or Risk Budget association; constraints, policies, thresholds,
or breach detection; recommendation actions or directions including BUY,
SELL, ADD, REDUCE, HOLD, and WAIT; approval, rejection, override,
explainability, or audit; endpoint lookup, repository, registry, resolver, or
existence behavior; persistence or migrations; execution or capital movement;
runtime, CLI, automation, scheduling, monitoring, orchestration, or workflow;
M45 applicability classification; uniqueness, global deduplication,
collection, or ordering; or denormalized Proposal, Position, Recommendation,
Snapshot, Portfolio, Capital Bucket, or Risk Budget identifiers.
