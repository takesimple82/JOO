# Portfolio Allocation Leg Proposed Absolute Quantity

## Contract

This package owns one explicit caller-supplied, base-independent proposed
absolute quantity content record attached to one Portfolio Allocation Leg
identity. Absolute does not mean mathematical absolute value. This is proposed
state only and is not an observed holding, target holding, delta, monetary
amount, portfolio weight, or actionable allocation instruction.

The complete public API is
`ExplicitPortfolioAllocationLegProposedAbsoluteQuantity` from `models` and
`validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity()` from
`validation`. There is no package-root re-export and no other public API.

## Model

`ExplicitPortfolioAllocationLegProposedAbsoluteQuantity` is a standard frozen,
hashable `@dataclass(frozen=True)` with exactly these required fields in order:
`allocation_leg_id: str`, `unit_id: str`, `value: Decimal`. There are no
defaults, factories, slots, post-init processing, custom constructors, public
methods or properties, derived or extra fields, and construction performs no
validation or behavior.

`allocation_leg_id` is a foreign-ID-only attachment canonical only in the
Portfolio Allocation Leg namespace. The package retains no Leg object, imports
no Leg package, invokes no Leg validation, and performs no endpoint lookup or
existence proof. `unit_id` is an opaque identifier owned by this boundary and
does not share a namespace with another package. `value` is the exact supplied
quantity and is neither calculated nor interpreted. The model has no separate
content identity.

Standard frozen-dataclass structural equality and hashing apply to all fields
in order. Decimal values retain standard Decimal equality and hashing; therefore
representationally distinct but numerically equal Decimals compare and hash as
standard Decimal equality specifies. Representation preservation does not add
custom equality.

## Validation and preservation

The exact signature is
`validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity(content: ExplicitPortfolioAllocationLegProposedAbsoluteQuantity) -> None`.
Validation uses exact type identity, rejects subclasses, and proceeds in this
order: exact content model; exact built-in `str` allocation Leg ID; nonblank Leg
ID; exact built-in `str` unit ID; nonblank unit ID; exact built-in `Decimal`
value; finite exact Decimal value; then return `None`. The first failure wins
and later checks do not run.

Failures are exact:

| Failure | Exception | Message |
| --- | --- | --- |
| content type | `TypeError` | `content must be ExplicitPortfolioAllocationLegProposedAbsoluteQuantity` |
| Leg ID type | `TypeError` | `allocation_leg_id must be str` |
| blank Leg ID | `ValueError` | `allocation_leg_id must not be blank` |
| unit ID type | `TypeError` | `unit_id must be str` |
| blank unit ID | `ValueError` | `unit_id must not be blank` |
| value type | `TypeError` | `value must be Decimal` |
| non-finite value | `ValueError` | `value must be finite` |

Every finite Decimal is accepted, including positive, negative, ordinary zero,
positive zero, signed zero, arbitrary finite exponents, and trailing zeros.
Infinity, negative infinity, quiet NaN, and signaling NaN are rejected. zero is
explicit content. This package does not interpret sign as BUY, SELL, ADD,
REDUCE, HOLD, WAIT, opening, closing, long, short, or execution semantics.

All exact caller-supplied string and Decimal objects retain object identity.
Case, Unicode form, surrounding whitespace on nonblank identifiers, Decimal
sign, coefficient, exponent, trailing zeros, representation, and signed zero
remain exact. Construction and validation never trim, normalize, case-fold,
quantize, round, convert, coerce, copy, reconstruct, derive, infer, resolve,
look up, or perform arithmetic. Decimal context precision, rounding, traps, and
flags are neither read for arithmetic nor changed.

## Multiplicity and dependency boundary

Architecture policy assigns one record per Allocation Leg, but this
single-record boundary cannot enforce cross-record cardinality. Independent
duplicates are structurally accepted, records sharing one Leg ID validate
independently, and distinct Legs may have equal unit IDs and values. It owns no
collection, uniqueness, deduplication, cross-record consistency, or endpoint
existence enforcement and owns no ordering.

Dependency boundary: `models.py` imports exactly standard-library `dataclasses`
and `decimal`; `validation.py` imports exactly standard-library `decimal` and
this package's `models`. Production code imports no existing JOO domain package
and no third-party dependency.

## Non-responsibilities

This package does not own Allocation Leg, Allocation Proposal, Proposal
Position Link, Position, Recommendation, Portfolio, Snapshot, Membership,
Capital Bucket, or Risk Budget production, validation, lookup, resolution, or
existence proof. It owns no denormalized proposal, position, recommendation,
portfolio, snapshot, bucket, or budget identifiers.

It does not own observed or target holding quantity, quantity delta, baseline
selection, Snapshot scanning, Holding Observation mutation, monetary amount,
price, currency, cash state, market value, NAV, valuation, FX, conversion,
portfolio weight, current or target weight, weight delta, denominator,
percentage, ratio, or rebalance calculation. It owns no unit taxonomy, shared
Unit domain, aliasing, compatibility, normalization, conversion, or lookup.

It defines no generic content kind, enum, union, polymorphic payload, additional
measurable model, sign interpretation, Recommendation action or direction,
Capital Bucket or Risk Budget association, funding calculation, amount, limit,
utilization, allocation policy, constraint taxonomy, constraint evaluation,
policy, threshold, or breach detection.

It performs no applicability, semantic production, calculation, ranking,
prioritization, confidence, materiality, suitability for action, approval,
rejection, override, explainability, audit, execution, capital movement, or
lifecycle state. It does not enforce endpoint or content uniqueness,
one-record-per-Leg cardinality, deduplication, collections, or ordering.

It owns no repository, registry, resolver, persistence, migration, runtime,
orchestration, workflow, CLI, automation, scheduling, monitoring, automatic
identity generation, hidden state, inference, or external API integration.
