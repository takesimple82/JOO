# Portfolio Allocation Leg to Risk Budget Link

## Responsibility and public API

`PortfolioAllocationLegRiskBudgetLink` owns one explicit, directed,
caller-supplied structural link from one Portfolio Allocation Leg identity to
one Portfolio Risk Budget identity. Its granularity is one Allocation Leg,
never an Allocation Proposal. The link records only the foreign identity pair
and is not funding, risk capacity, constraint applicability, endpoint proof,
or an actionable allocation instruction.

The complete and exact public API is:

- `ExplicitPortfolioAllocationLegRiskBudgetLink`
- `validate_explicit_portfolio_allocation_leg_risk_budget_link()`

The model is imported from `PortfolioAllocationLegRiskBudgetLink.models` and
the validator from `PortfolioAllocationLegRiskBudgetLink.validation`. There is
no package-root re-export and no other public API.

## Model

`ExplicitPortfolioAllocationLegRiskBudgetLink` is a standard frozen, hashable
`@dataclass(frozen=True)` with exactly two required fields in order:
`allocation_leg_id: str`, then `risk_budget_id: str`. The first is foreign to
the Allocation Leg namespace and the second is foreign to the Portfolio Risk
Budget namespace.

The model has no defaults, factories, slots, `__post_init__`, constructor
validation, custom constructor, public methods, properties, derived or extra
fields, aliases, metadata, endpoint objects, association identity, `link_id`,
timestamps, status, or lifecycle fields.

## Validation and exceptions

The exact signature is
`validate_explicit_portfolio_allocation_leg_risk_budget_link(link: ExplicitPortfolioAllocationLegRiskBudgetLink) -> None`.
Validation uses exact type identity and proceeds in this order:

1. exact `ExplicitPortfolioAllocationLegRiskBudgetLink` model type;
2. `allocation_leg_id` is the exact built-in `str` type;
3. `allocation_leg_id` is not empty or whitespace-only;
4. `risk_budget_id` is the exact built-in `str` type;
5. `risk_budget_id` is not empty or whitespace-only; and
6. return `None`.

Model and string subclasses are rejected. The first failure wins, and no later
check runs after a failure. Failures are exact:

| Failure | Exception | Message |
|---|---|---|
| link type | `TypeError` | `link must be ExplicitPortfolioAllocationLegRiskBudgetLink` |
| Leg ID type | `TypeError` | `allocation_leg_id must be str` |
| blank Leg ID | `ValueError` | `allocation_leg_id must not be blank` |
| Risk Budget ID type | `TypeError` | `risk_budget_id must be str` |
| blank Risk Budget ID | `ValueError` | `risk_budget_id must not be blank` |

Blank means empty or whitespace-only under validation-only `str.strip()`
detection. A nonblank identifier is never replaced by its stripped result.

## Preservation, equality, and hashability

Both exact caller-supplied string objects retain object identity and value.
Case, composed and decomposed Unicode form, code points, and surrounding
whitespace on an otherwise nonblank value are accepted and preserved.
Construction and validation do not trim, normalize, case-fold, canonicalize,
transform, coerce, convert, copy, reconstruct, derive, hash, generate, infer,
look up, resolve, sort, or mutate.

Equality is standard frozen-dataclass structural equality over both fields in
declared order. Hashability is the standard frozen-dataclass contract. There
is no custom, normalized, endpoint-only, or identity equality or hashing.

## Multiplicity and optionality

The association is optional at Allocation Leg granularity. Absence means only
the absence of a link record; it is not represented by `None`, a blank field,
sentinel, default, or special object. Every supplied record requires both exact
nonblank IDs.

Zero or more records may share one Leg ID, and zero or more records may share
one Risk Budget ID. Independent exact duplicates are structurally accepted.
The package owns no uniqueness, duplicate detection or rejection,
deduplication, exclusivity, one-to-one or one-to-many enforcement, collection,
collection cardinality, reverse collection, cross-record consistency,
ordering, aggregation, completeness, coverage, or precedence.

## M49 and cross-record boundary

Architecture sequencing expects a Leg carrying this link also to carry a
separate M49 Leg-to-Capital-Bucket link. This package does not enforce the M49
prerequisite and does not import, retrieve, validate, or prove an M49 record.

Bucket/Risk-Budget consistency remains deferred to later applicability or
constraint architecture. This package does not retrieve a Risk Budget,
compare a Bucket ID, or combine Leg, Bucket, and Risk Budget identifiers in one
record.

## Dependency and import boundary

Production dependencies are exact: `models.py` imports only standard-library
`dataclasses`; `validation.py` imports only this package's `models`. Production
code imports no endpoint, M49, existing JOO domain, applicability, semantic,
calculation, constraint, persistence, runtime, or third-party package.

The link retains no Leg, Risk Budget, Capital Bucket, M49 link, or other
endpoint object and invokes no endpoint or upstream validator. Structural
validation performs no endpoint lookup or existence proof. It establishes no
issuance, validity, uniqueness, activity, alignment, consistency, or
suitability.

## Denormalization prohibitions

The model contains and derives no `capital_bucket_id`, Allocation Proposal,
Position, Recommendation, Portfolio, Portfolio Snapshot, unit, quantity,
value, amount, limit, balance, capacity, currency, weight, ratio, percentage,
status, or timestamp identifier or field. It retains no Proposal Position
Link, Leg, Capital Bucket, Risk Budget, M49 link, or other endpoint object.

## Non-responsibilities

This package does not own or perform endpoint or M49 production, validation,
lookup, resolution, registry access, existence proof, endpoint validity,
endpoint uniqueness, Portfolio alignment, Bucket-to-Portfolio applicability,
Leg-to-Proposal applicability, Bucket/Risk-Budget consistency, or M49
prerequisite enforcement.

It owns no automatic or composite identity generation, uniqueness, duplicate
detection or rejection, deduplication, exclusivity, one-to-one or one-to-many
enforcement, collection or collection cardinality, reverse collection,
ordering, aggregation, completeness, coverage, precedence, or cross-record
consistency. It owns no Proposal-level association or combined
Leg-Bucket-Budget record.

It owns no funding amount, available or committed capital, cash, balance,
capacity, reservation, currency, price, valuation, FX, NAV, routing, or capital
movement; risk amount, limit, threshold, tolerance, utilization, remaining
capacity, ratio, percentage, concentration, policy, or breach detection;
allocation quantity, unit, target holding, delta, portfolio weight,
denominator, rebalance, or quantity or weight interpretation.

It owns no constraint definition, taxonomy, applicability, evaluation,
satisfaction, prioritization, enforcement, limit, threshold, utilization, or
breach; Recommendation action or semantics including BUY, SELL, ADD, REDUCE,
HOLD, or WAIT; opening, closing, long, short, or execution direction.

It performs no semantic production, inference, calculation, ranking,
confidence, priority, urgency, materiality, suitability, approval, rejection,
override, explainability, audit, execution, or lifecycle behavior. It owns no
persistence, migration, repository, registry, resolver, external API, CLI,
runtime, orchestration, workflow, automation, scheduling, monitoring, hidden
state, or third-party dependency.
