# M48 Frozen Architecture — Portfolio Allocation Leg Proposed Absolute Quantity

- Stage: 5
- Milestone: M48
- Status: Frozen
- Predecessor: M47 `PortfolioAllocationLeg`

## 1. Package name

The exact package name is:

`PortfolioAllocationLegProposedAbsoluteQuantity`

This is a new domain-contract package. It does not modify M43–M47 or any
other accepted package.

## 2. Responsibility

This package owns one explicit proposed-absolute-quantity content record for
one Portfolio Allocation Leg identity.

“Proposed absolute quantity” means one caller-supplied, base-independent
proposed quantity attached to one Allocation Leg. “Absolute” does not mean
mathematical absolute value and does not impose a non-negative sign.

The record is proposed state only. It is not an observed holding quantity, a
target post-proposal holding quantity, a delta from current state, a monetary
amount, a portfolio weight, or a weight delta.

## 3. Public API

The complete and exact public API is:

- `ExplicitPortfolioAllocationLegProposedAbsoluteQuantity`
- `validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity()`

No package-root re-export is required. Callers import the model from
`PortfolioAllocationLegProposedAbsoluteQuantity.models` and the validator
from `PortfolioAllocationLegProposedAbsoluteQuantity.validation`.

No other class, function, property, public method, enum, alias, protocol, or
constant is public API.

The validator signature is exactly one positional-or-keyword parameter named
`content`, annotated as
`ExplicitPortfolioAllocationLegProposedAbsoluteQuantity`, with a return
annotation of `None`:

`validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity(content: ExplicitPortfolioAllocationLegProposedAbsoluteQuantity) -> None`

## 4. Model and field ownership

`ExplicitPortfolioAllocationLegProposedAbsoluteQuantity` is a standard
`@dataclass(frozen=True)` structural model containing exactly these fields in
this order:

1. `allocation_leg_id: str`
2. `unit_id: str`
3. `value: Decimal`

All three fields are required. The model has no defaults, default factories,
slots, `__post_init__`, custom constructors, custom public methods,
properties, derived fields, aliases, metadata fields, or additional fields.
Construction performs no validation.

`allocation_leg_id` is a foreign opaque identifier canonical only within the
Portfolio Allocation Leg namespace. The content model retains only that
identity; it does not retain an `ExplicitPortfolioAllocationLeg` object.

`unit_id` is an opaque identifier owned by this proposed-absolute-quantity
boundary. Identical field naming does not establish a shared namespace with
Expected Value, Exact Cross-Context Numeric Delta, Holding Observation, or
any other package.

`value` is the exact caller-supplied proposed quantity. It is not calculated
or interpreted by this package.

The model introduces no separate content identity. Its attachment is stated
only by `allocation_leg_id`.

## 5. Validation order

`validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity()`
validates exactly in this order:

1. `content` is the exact
   `ExplicitPortfolioAllocationLegProposedAbsoluteQuantity` model type;
2. `allocation_leg_id` is the exact built-in `str` type;
3. `allocation_leg_id` is not empty or whitespace-only;
4. `unit_id` is the exact built-in `str` type;
5. `unit_id` is not empty or whitespace-only;
6. `value` is the exact built-in `decimal.Decimal` type;
7. `value` is finite according to its exact Decimal value; and
8. return `None`.

Exact-type checks use exact type identity. Model, `str`, and `Decimal`
subclasses are rejected. The first failure in the declared order wins. No
later check is performed after a failure.

The finite check accepts every finite Decimal representation, including
positive values, negative values, positive zero, negative zero, and values
with any finite exponent or trailing zeros. It rejects positive infinity,
negative infinity, quiet NaN, and signaling NaN. The check must not perform
arithmetic and must not read or change the active Decimal context.

## 6. Exception contract

Local validation failures raise exactly the following exception types and
messages:

| Failure | Exception | Exact message |
|---|---|---|
| wrong `content` type | `TypeError` | `content must be ExplicitPortfolioAllocationLegProposedAbsoluteQuantity` |
| wrong `allocation_leg_id` type | `TypeError` | `allocation_leg_id must be str` |
| empty or whitespace-only `allocation_leg_id` | `ValueError` | `allocation_leg_id must not be blank` |
| wrong `unit_id` type | `TypeError` | `unit_id must be str` |
| empty or whitespace-only `unit_id` | `ValueError` | `unit_id must not be blank` |
| wrong `value` type | `TypeError` | `value must be Decimal` |
| non-finite `value` | `ValueError` | `value must be finite` |

Messages contain no prefix, suffix, field value, or chained explanatory text.

This package invokes no upstream validator. Therefore it has no upstream
exception to catch, wrap, translate, aggregate, suppress, or replace.
Unexpected exceptions from Python itself are not caught.

## 7. Preservation semantics

The model retains the exact caller-supplied objects for
`allocation_leg_id`, `unit_id`, and `value`.

Surrounding whitespace on an otherwise nonblank identifier is accepted and
preserved. Case, Unicode form, and every other character remain exact. The
Decimal object and its representation are preserved exactly, including sign,
coefficient, exponent, trailing zeros, and signed zero.

Construction and validation do not trim, case fold, Unicode-normalize,
canonicalize, quantize, round, convert, coerce, copy, reconstruct, derive,
generate, infer, look up, resolve, or perform arithmetic on any field. No
float conversion or implicit numeric conversion is permitted. The active
Decimal context is neither consulted for arithmetic nor modified.

## 8. Equality and hashability

Equality is the unmodified standard frozen-dataclass structural equality over
all three fields in their declared order. Hashability is the unmodified
standard frozen-dataclass hash contract.

Two independently constructed records with equal field values are equal and
have equal hashes. Any unequal field makes the records unequal under the
corresponding field type's standard equality. No identity-only, Leg-only,
numeric-normalized, unit-normalized, or custom equality is introduced.

Decimal equality and hashing remain Python Decimal behavior. The package does
not replace that behavior to distinguish representationally different but
numerically equal Decimal values. Representation preservation is a storage
and object-identity guarantee, not a custom equality rule.

## 9. Dependency and import boundary

Production code may depend only on:

- Python standard-library `dataclasses` in `models.py`;
- Python standard-library `decimal.Decimal` in `models.py` and
  `validation.py`; and
- this package's own `models` module in `validation.py`.

`models.py` imports exactly from `dataclasses` and `decimal`.
`validation.py` imports exactly from `decimal` and
`PortfolioAllocationLegProposedAbsoluteQuantity.models`.

Production code imports no existing JOO domain package, including
`PortfolioAllocationLeg`. It does not import a Leg model or Leg validator.
`allocation_leg_id` is a foreign-ID-only attachment: validation does not
prove that a Leg exists, is unique, is valid, or has content eligibility.

Production code imports no third-party package. Dependency direction does not
change any M43–M47 contract.

## 10. Multiplicity, cardinality, duplicates, and ordering

At the architecture policy level, one Allocation Leg owns exactly one
proposed-absolute-quantity content record. Additional independently
measurable intent requires another caller-identified Leg, even when the Legs
retain structurally equal Proposal Position Links.

This package is a single-record structural boundary and cannot enforce that
policy across records. It owns no collection, repository, registry, lookup,
global index, or persistence boundary. Consequently:

- an independently supplied exact duplicate content record is structurally
  accepted;
- two records with the same `allocation_leg_id` are each structurally
  accepted when validated independently;
- distinct Legs may carry equal `unit_id` and `value` fields;
- no uniqueness, deduplication, cross-record consistency, or endpoint
  existence is proven; and
- no collection or ordering semantics are owned.

Zero is explicit content, not absence. Positive, zero, negative, positive-zero,
and negative-zero values are structurally accepted. Sign does not establish
BUY, SELL, ADD, REDUCE, HOLD, WAIT, opening, closing, long, short, or execution
semantics.

Any future boundary that enforces the one-record-per-Leg policy requires a
separate approved contract and must not change this package's structural
acceptance behavior.

## 11. Non-responsibilities

This package does not own or perform:

- Allocation Leg, Allocation Proposal, Proposal Position Link, Position,
  Recommendation, Portfolio, Snapshot, Membership, Capital Bucket, or Risk
  Budget production, validation, lookup, resolution, or existence proof;
- denormalized `allocation_proposal_id`, `position_id`, `recommendation_id`,
  `portfolio_id`, `portfolio_snapshot_id`, `capital_bucket_id`, or
  `risk_budget_id` fields;
- observed holding quantity, target post-proposal quantity, quantity delta,
  baseline selection, Snapshot scanning, or Holding Observation mutation;
- monetary amount, price, currency, Currency domain, cash state, market value,
  Portfolio NAV, valuation, FX lookup, conversion, or normalization;
- portfolio weight, target weight, current weight, weight delta, denominator,
  percentage, ratio, or rebalance calculation;
- unit taxonomy, shared Unit domain, aliasing, compatibility resolution,
  normalization, conversion, or lookup;
- generic content kinds, enums, unions, polymorphic payloads, or additional
  measurable content models;
- sign interpretation, Recommendation action or direction, including BUY,
  SELL, ADD, REDUCE, HOLD, or WAIT, or opening, closing, long, or short policy;
- Capital Bucket or Risk Budget association, funding calculation, bucket
  amount, limit, utilization, or allocation policy;
- constraint taxonomy, constraint evaluation, policy, limit, threshold,
  utilization, or breach detection;
- applicability, semantic production, calculation, ranking, prioritization,
  confidence, materiality, or suitability for action;
- approval, rejection, override, explainability, audit, execution, capital
  movement, or lifecycle state;
- endpoint or content uniqueness, one-record-per-Leg enforcement,
  deduplication, collection ownership, or ordering;
- repositories, registries, resolvers, persistence, migration, runtime,
  orchestration, workflow, CLI, automation, scheduling, or monitoring; or
- automatic identity generation, hidden state, inference, or external API
  integration.

## 12. README requirements

`PortfolioAllocationLegProposedAbsoluteQuantity/README.md` is required and
must be a normative package contract consistent with this document. It must
state, without weakening or extending them:

1. the package's single responsibility and exact public API;
2. the exact model name, frozen/hashable dataclass form, three fields, field
   order, field ownership, and absence of defaults or behavior;
3. the exact validator signature, validation order, first-failure rule,
   exception types, and exact messages;
4. exact-string, exact-Decimal, object-identity, representation, signed-zero,
   surrounding-whitespace, and no-normalization preservation semantics;
5. foreign-ID-only Leg attachment and the absence of Leg imports, Leg
   validation, endpoint lookup, and existence proof;
6. equality and hashability semantics, including standard Decimal equality;
7. one-record-per-Leg architecture policy, independent duplicate structural
   acceptance, lack of cross-record enforcement, and absence of ordering;
8. finite Decimal acceptance, non-finite rejection, zero-as-content, and no
   sign-to-action interpretation;
9. the exact production dependency boundary; and
10. the complete non-responsibilities in Section 11.

The README must not claim that this package validates a Leg, enforces
cardinality, establishes endpoint existence, shares a Unit namespace, or
produces an actionable allocation instruction.

## 13. Required unit-test contract

The implementation milestone must add `unittest` coverage that proves all of
the following without weakening existing tests:

### Model contract

- the model is a dataclass and is frozen;
- fields and type hints are exactly `allocation_leg_id: str`, `unit_id: str`,
  and `value: Decimal` in that order;
- every field has no default and no default factory;
- there are no slots, `__post_init__`, custom public methods, public
  properties, or extra fields;
- mutation raises `FrozenInstanceError`;
- structural equality and hashing cover every field; and
- representationally distinct but Decimal-equal values follow standard
  Decimal equality and hashing while the supplied value object remains
  retained.

### Exact model and field validation

- `None`, unrelated objects, collections, and a model subclass fail the first
  exact-model check with the exact exception contract;
- each identifier rejects `None`, integers, bytes, and a `str` subclass with
  its exact type error;
- each identifier rejects empty and whitespace-only strings with its exact
  blank-value error;
- otherwise nonblank strings with surrounding whitespace, distinct case, and
  composed/decomposed Unicode are accepted and preserved exactly;
- `value` rejects `None`, integers, floats, strings, and a `Decimal` subclass
  with its exact type error;
- representative positive, negative, ordinary zero, positive zero, negative
  zero, exponent-bearing, and trailing-zero finite Decimals are accepted;
- positive infinity, negative infinity, quiet NaN, and signaling NaN are
  rejected with the exact finite-value error; and
- successful validation returns `None`.

### Validation order and preservation

- multi-invalid inputs prove every first-failure transition in the declared
  validation order;
- the exact first failure type and full anchored message are asserted;
- all three exact supplied field objects remain retained before and after
  validation;
- Decimal tuple/representation and signed zero remain unchanged;
- validation neither reads nor changes Decimal context precision, rounding,
  traps, or flags; and
- no conversion, coercion, normalization, reconstruction, arithmetic, unit
  conversion, lookup, or upstream validator call occurs.

### Multiplicity and boundary

- independent duplicate records validate successfully;
- records sharing one `allocation_leg_id` validate independently;
- distinct Leg IDs with equal `unit_id` and `value` validate successfully;
- zero remains present as a normal field value;
- the validator signature, production class/function definitions, and exact
  import allowlists match Sections 3 and 9;
- production source contains no Leg import, upstream validator call,
  denormalized identifier, forbidden responsibility, third-party import, or
  hidden collection behavior; and
- the README contains stable fragments covering every requirement in Section
  12 and contains no contradictory claim.

After the package tests pass, the complete repository `unittest` regression
suite must pass unchanged.

## 14. Implementation file boundary

M48 implementation is limited to creating exactly:

```text
PortfolioAllocationLegProposedAbsoluteQuantity/
├── README.md
├── models.py
├── validation.py
└── tests/
    ├── __init__.py
    └── test_proposed_absolute_quantity.py
```

`models.py` contains exactly the one public model class.
`validation.py` contains exactly the one public validator function. Test
helpers and test-only subclasses remain inside the test module.

M48 must not add a package-root `__init__.py`, classifier, semantic wrapper,
calculation, runtime, persistence adapter, registry, repository, resolver,
schema, migration, CLI, configuration, fixture data, shared utility, or
third-party dependency. It must not modify the roadmap, ADR-0001, M43–M47,
or any other existing production package or accepted public contract.

This architecture document is the only M48 architecture artifact added before
implementation. Production code and tests are not part of the architecture
document milestone.

## 15. Acceptance criteria

The M48 contract-document milestone is accepted when:

1. this document alone fixes the package name, responsibility, public API,
   model, field order, validation order, exception contract, preservation,
   equality/hashability, dependencies, imports, multiplicity,
   non-responsibilities, README, tests, and file boundary;
2. every decision remains within Stage 5 and ADR-0001's Leg-owned proposed
   absolute quantity semantics;
3. M43–M47 identities, multiplicity, applicability, public APIs, and
   responsibilities remain unchanged;
4. no implementation code, tests, roadmap changes, or ADR changes are
   included in this milestone; and
5. a future implementation can be judged for complete conformance using only
   this document, without resolving architectural ambiguity in code.

The later M48 implementation is accepted only when every rule in this
document is implemented exactly, the required README and tests exist within
the frozen file boundary, the focused package tests pass, and the full
repository regression suite passes without changing accepted expectations.
