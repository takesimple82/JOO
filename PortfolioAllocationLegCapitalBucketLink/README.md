# Portfolio Allocation Leg to Capital Bucket Link

## Responsibility and public API

`PortfolioAllocationLegCapitalBucketLink` owns one explicit, directed,
caller-supplied structural link from one Portfolio Allocation Leg identity to
one Portfolio Capital Bucket identity. Its granularity is one Allocation Leg,
never an Allocation Proposal. The link records only the identity pair and is
not funding, reservation, alignment, applicability, or an actionable
allocation instruction.

The complete and exact public API is:

- `ExplicitPortfolioAllocationLegCapitalBucketLink`
- `validate_explicit_portfolio_allocation_leg_capital_bucket_link()`

The model is imported from `PortfolioAllocationLegCapitalBucketLink.models`
and the validator from `PortfolioAllocationLegCapitalBucketLink.validation`.
There is no package-root re-export and no other public API.

## Model

`ExplicitPortfolioAllocationLegCapitalBucketLink` is a standard frozen,
hashable `@dataclass(frozen=True)` with exactly two required fields in order:
`allocation_leg_id: str`, then `capital_bucket_id: str`. The first is foreign
to the Allocation Leg namespace and the second is foreign to the Capital
Bucket namespace.

The model has no defaults, factories, slots, `__post_init__`, constructor
validation, custom constructor, public methods, properties, derived or extra
fields, aliases, metadata, endpoint objects, association identity, `link_id`,
timestamps, status, or lifecycle fields.

## Validation and exceptions

The exact signature is
`validate_explicit_portfolio_allocation_leg_capital_bucket_link(link: ExplicitPortfolioAllocationLegCapitalBucketLink) -> None`.
Validation uses exact type identity and proceeds in this order:

1. exact `ExplicitPortfolioAllocationLegCapitalBucketLink` model type;
2. `allocation_leg_id` is the exact built-in `str` type;
3. `allocation_leg_id` is not empty or whitespace-only;
4. `capital_bucket_id` is the exact built-in `str` type;
5. `capital_bucket_id` is not empty or whitespace-only; and
6. return `None`.

Model and string subclasses are rejected. The first failure wins, and no later
check runs after a failure. Failures are exact:

| Failure | Exception | Message |
|---|---|---|
| link type | `TypeError` | `link must be ExplicitPortfolioAllocationLegCapitalBucketLink` |
| Leg ID type | `TypeError` | `allocation_leg_id must be str` |
| blank Leg ID | `ValueError` | `allocation_leg_id must not be blank` |
| Bucket ID type | `TypeError` | `capital_bucket_id must be str` |
| blank Bucket ID | `ValueError` | `capital_bucket_id must not be blank` |

Blank means empty or whitespace-only under validation-only `str.strip()`
detection. A nonblank identifier is never replaced with the stripped result.

## Preservation, equality, and hashability

Both exact caller-supplied string objects retain object identity and value.
Case, Unicode form, code points, and surrounding whitespace on an otherwise
nonblank value are accepted and preserved. Construction and validation do not
trim, normalize, case-fold, canonicalize, transform, coerce, convert, copy,
reconstruct, derive, hash, generate, infer, look up, resolve, sort, or mutate.

Equality is standard frozen-dataclass structural equality over both fields in
declared order. Hashability is the standard frozen-dataclass contract. There
is no custom, normalized, endpoint-only, or identity equality or hashing.

## Multiplicity and optionality

Many links may share one Leg ID, many may share one Bucket ID, and independent
exact duplicates are structurally accepted. Structurally equal independent
instances compare equal. The package owns no collection, uniqueness,
deduplication, exclusivity, one-to-one or one-Bucket-per-Leg cardinality,
ordering, aggregation, completeness, coverage, primary Bucket, or precedence.

The association is optional per Leg. Absence means only the absence of a link
record. It is not represented by `None`, a blank field, sentinel, default, or
special object. A supplied record always requires both exact nonblank IDs.

## Dependency and import boundary

Production dependencies are exact: `models.py` imports only standard-library
`dataclasses`; `validation.py` imports only this package's `models`. Production
code imports no endpoint package, existing JOO domain package, applicability,
semantic, calculation, persistence, runtime, or third-party package.

The link retains no Leg or Capital Bucket object and invokes no endpoint
validator. Structural validation performs no endpoint lookup or existence
proof. It does not establish issuance, validity, uniqueness, activity,
Portfolio ownership, Portfolio alignment, mutual applicability, or allocation
suitability.

## Denormalization prohibitions

The model contains and derives no Allocation Proposal, Position,
Recommendation, Portfolio, Portfolio Snapshot, Risk Budget, unit, quantity,
value, amount, currency, weight, ratio, or percentage identifier or field. It
retains no Proposal Position Link, Leg, Capital Bucket, Risk Budget, or other
endpoint object.

Risk Budget association remains deferred to a separate later milestone. The
constraint architecture remains deferred until both separate association
packages are accepted and implemented. This package does not enforce a later
Risk Budget prerequisite or cross-record consistency.

## Non-responsibilities

This package does not own or perform endpoint production, validation,
resolution, lookup, existence proof, Portfolio alignment, Bucket-to-Portfolio
applicability, Leg-to-Proposal applicability, endpoint consistency,
Bucket/Risk-Budget consistency, identity generation, uniqueness,
deduplication, collections, ordering, aggregation, completeness, or coverage.

It owns no proposed, observed, target, or delta quantity; unit semantics or
conversion; M48 reinterpretation; funding amount, available or committed
capital, cash, balance, capacity, reservation, currency, price, valuation, FX,
NAV, routing, capital movement, or funding-source selection; risk amount,
limit, tolerance, threshold, utilization, remaining capacity, ratio,
percentage, concentration, or breach detection; target holding, portfolio
weight, denominator, or rebalance calculation.

It owns no Capital Bucket or Risk Budget taxonomy, name, label, description,
kind, category, purpose, policy, state, or lifecycle; Risk Budget link;
constraint taxonomy, definition, applicability, evaluation, satisfaction,
prioritization, enforcement, limit, threshold, utilization, or breach
detection; Recommendation action or direction including BUY, HOLD, SELL, ADD,
REDUCE, or WAIT; opening, closing, long, short, or execution interpretation.

It performs no semantic production, inference, calculation, ranking,
confidence, priority, urgency, materiality, suitability, approval, rejection,
override, explainability, audit, execution, or lifecycle behavior. It owns no
persistence, migration, repository, registry, resolver, runtime,
orchestration, workflow, CLI, automation, scheduling, monitoring, hidden
state, external API integration, or third-party dependency.
