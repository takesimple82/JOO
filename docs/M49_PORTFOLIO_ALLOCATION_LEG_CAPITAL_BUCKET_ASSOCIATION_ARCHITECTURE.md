# M49 Frozen Architecture — Portfolio Allocation Leg to Capital Bucket Link

- Repository: `/Users/takesimple/Projects/JOO`
- Stage: 5
- Milestone: M49
- Status: Frozen
- Predecessor: M48 `PortfolioAllocationLegProposedAbsoluteQuantity`
- Architecture baseline: ADR-0001 and ADR-0002

## 1. Repository and milestone context

M43–M48 establish the accepted Recommendation, Allocation Proposal, Proposal
Position Link, Allocation Leg, and Leg proposed-absolute-quantity chain. M49
adds only the first optional post-content structural association selected by
ADR-0002: a directed relation from one Portfolio Allocation Leg identity to
one Portfolio Capital Bucket identity.

This is an architecture-document milestone only. It changes no accepted
package, roadmap, ADR, runtime, persistence, or operational responsibility.
The later Leg-to-Risk-Budget association and all constraint architecture remain
separate later milestones.

## 2. Package name

The exact package name is:

`PortfolioAllocationLegCapitalBucketLink`

This is a new domain-contract package. The `Link` suffix follows the accepted
foreign-ID association convention. It does not modify either endpoint package
or any M43–M48 package.

## 3. Responsibility

The package owns exactly one explicit, directed, caller-supplied structural
link from one Portfolio Allocation Leg identity to one Portfolio Capital
Bucket identity.

The association has Allocation Leg granularity, never Allocation Proposal
granularity. It records only the supplied identity pair. It does not establish
funding, reservation, allocation, Portfolio alignment, endpoint existence,
suitability, applicability, or any economic or operational meaning.

## 4. Public API

The complete and exact public API is:

- `ExplicitPortfolioAllocationLegCapitalBucketLink`
- `validate_explicit_portfolio_allocation_leg_capital_bucket_link()`

Callers import the model from
`PortfolioAllocationLegCapitalBucketLink.models` and the validator from
`PortfolioAllocationLegCapitalBucketLink.validation`. No package-root
re-export is required.

No other class, function, property, public method, enum, alias, protocol, or
constant is public API.

The validator signature has exactly one positional-or-keyword parameter named
`link`, annotated as `ExplicitPortfolioAllocationLegCapitalBucketLink`, and a
return annotation of `None`:

`validate_explicit_portfolio_allocation_leg_capital_bucket_link(link: ExplicitPortfolioAllocationLegCapitalBucketLink) -> None`

## 5. Model and field ownership

`ExplicitPortfolioAllocationLegCapitalBucketLink` is a standard
`@dataclass(frozen=True)` structural model containing exactly these required
fields in this order:

1. `allocation_leg_id: str`
2. `capital_bucket_id: str`

The model has no defaults, default factories, slots, `__post_init__`, custom
constructor, custom public methods, properties, derived fields, aliases,
metadata fields, retained endpoint objects, or additional fields. Construction
performs no validation.

`allocation_leg_id` is a foreign opaque identifier canonical only in the
Portfolio Allocation Leg namespace. `capital_bucket_id` is a foreign opaque
identifier canonical only in the Portfolio Capital Bucket namespace. The
package owns the relation, not either endpoint identity.

The model has no association identity, `link_id`, generated identity,
composite canonical identity, status, timestamp, label, or lifecycle field.
Pair equality does not create an identity.

## 6. Validation order

`validate_explicit_portfolio_allocation_leg_capital_bucket_link()` validates
exactly in this order:

1. `link` is the exact `ExplicitPortfolioAllocationLegCapitalBucketLink`
   model type;
2. `allocation_leg_id` is the exact built-in `str` type;
3. `allocation_leg_id` is not empty or whitespace-only;
4. `capital_bucket_id` is the exact built-in `str` type;
5. `capital_bucket_id` is not empty or whitespace-only; and
6. return `None`.

Exact-type checks use exact type identity. Model subclasses and `str`
subclasses are rejected. The first failure in the declared order wins. No
later field access or check is performed after a failure.

The validator invokes no endpoint validator and performs no cross-record or
cross-field semantic check.

## 7. Exception contract

Local validation failures raise exactly these exception types and messages:

| Failure | Exception | Exact message |
|---|---|---|
| wrong `link` type | `TypeError` | `link must be ExplicitPortfolioAllocationLegCapitalBucketLink` |
| wrong `allocation_leg_id` type | `TypeError` | `allocation_leg_id must be str` |
| empty or whitespace-only `allocation_leg_id` | `ValueError` | `allocation_leg_id must not be blank` |
| wrong `capital_bucket_id` type | `TypeError` | `capital_bucket_id must be str` |
| empty or whitespace-only `capital_bucket_id` | `ValueError` | `capital_bucket_id must not be blank` |

Messages contain no prefix, suffix, supplied value, or chained explanatory
text. There is no upstream exception contract because no upstream validator is
called. Unexpected Python exceptions are not caught.

## 8. Preservation semantics

The model retains the exact caller-supplied `allocation_leg_id` and
`capital_bucket_id` string objects. Validation does not replace either object.

Surrounding whitespace on an otherwise nonblank identifier is accepted and
preserved. Case, Unicode form, code points, and all other characters remain
exact. Construction and validation do not trim, case-fold, Unicode-normalize,
canonicalize, transform, coerce, convert, copy, reconstruct, derive, hash,
generate, infer, look up, resolve, sort, or mutate either field or the link.

Blank means exactly an empty string or a string for which the built-in
`str.strip()` result is empty. A nonblank value is not replaced by the stripped
result.

## 9. Equality and hashability

Equality is unmodified standard frozen-dataclass structural equality over both
fields in declared order. Hashability is the unmodified standard
frozen-dataclass hash contract.

Independently constructed links with equal field values are equal and have
equal hashes. A difference in either field makes links unequal under standard
string equality. There is no identity-only, Leg-only, Bucket-only,
case-insensitive, normalized, or custom equality or hash behavior.

## 10. Multiplicity, duplicates, and optionality

Many independently supplied links may share one `allocation_leg_id`. Many may
share one `capital_bucket_id`. One Leg may therefore have zero or more supplied
Capital Bucket links, and one Capital Bucket may appear in zero or more links.
No one-to-one, exclusive, primary-Bucket, single-Bucket-per-Leg, or
single-Leg-per-Bucket policy is frozen.

Independent exact duplicate records are structurally accepted. The package
owns no collection, global or per-endpoint uniqueness, pair uniqueness,
deduplication, aggregation, completeness, coverage, precedence, or ordering.
Each record is validated independently.

The association is optional per Leg. Absence means that no link record was
supplied. Absence is not represented by `None`, a blank identifier, a sentinel,
a default, or a special link instance. A supplied link must contain both exact
nonblank identifiers. Not every Leg or Allocation Proposal requires a link.

The later Leg-to-Risk-Budget relation is a separate independently optional
record. This package neither contains nor proves its presence. ADR-0002's
cross-record prerequisite for a later Risk Budget link is not enforced here.

## 11. Dependency and import boundary

Production code may depend only on:

- Python standard-library `dataclasses` in `models.py`; and
- this package's own `models` module in `validation.py`.

`models.py` imports exactly from `dataclasses`.
`validation.py` imports exactly from
`PortfolioAllocationLegCapitalBucketLink.models`.

Production code imports no third-party package and no existing JOO domain
package. In particular, it must not import from `PortfolioAllocationLeg`,
`PortfolioCapitalBucket`, `PortfolioRiskBudget`, M48, M43–M45, endpoint,
applicability, semantic, calculation, persistence, or runtime packages.

The model does not import its validator. Neither endpoint package imports this
package. Dependency direction and every accepted endpoint remain unchanged.

## 12. Endpoint and existence-proof boundary

This foreign-ID-only link retains no `ExplicitPortfolioAllocationLeg`,
`ExplicitPortfolioCapitalBucket`, or other endpoint object. It invokes no Leg,
Capital Bucket, Link, Proposal, Position, Recommendation, Portfolio, Snapshot,
Risk Budget, or other upstream validator.

Structural validation proves only the exact link model and the exact nonblank
string shapes of its two stored fields. It does not prove that either endpoint
exists, was authoritatively issued, is valid, is unique, is active, belongs to
a particular Portfolio, is mutually aligned, or is suitable for allocation.
It performs no lookup, traversal, registry or repository access, resolution,
membership check, or endpoint consistency check.

## 13. Denormalization prohibitions

The model must not contain or derive:

- `allocation_proposal_id`;
- `position_id`;
- `recommendation_id`;
- `portfolio_id` or `portfolio_snapshot_id`;
- `risk_budget_id`;
- `unit_id`;
- quantity, amount, value, currency, weight, ratio, or percentage fields; or
- a retained Proposal Position Link, Allocation Leg, Capital Bucket, Risk
  Budget, or any other endpoint object.

Proposal and Position identity remain reachable only through the accepted
Leg's retained Link. Portfolio identity remains owned by the accepted Capital
Bucket endpoint. Reachability does not authorize hidden lookup or traversal.

## 14. Non-responsibilities

This package does not own or perform:

- Allocation Leg, Allocation Proposal, Proposal Position Link, Position,
  Recommendation, Portfolio, Snapshot, Membership, Capital Bucket, or Risk
  Budget production, validation, lookup, resolution, or existence proof;
- association identity, automatic or composite identity generation, endpoint
  or pair uniqueness, deduplication, collections, ordering, aggregation,
  completeness, required coverage, or cross-record enforcement;
- Portfolio alignment, Bucket-to-Portfolio applicability, Leg-to-Proposal
  applicability, endpoint consistency, or Bucket/Risk-Budget consistency;
- proposed, observed, target, or delta quantity; unit semantics or conversion;
  reinterpretation, mutation, or calculation of M48 content;
- funding amount, available or committed capital, cash, balance, capacity,
  currency, price, valuation, NAV, capital movement, routing, reservation, or
  funding-source selection;
- risk amount, limit, tolerance, threshold, utilization, remaining capacity,
  ratio, percentage, concentration, or breach detection;
- target holding, portfolio weight, weight delta, denominator, rebalance, or
  any other allocation calculation;
- Capital Bucket or Risk Budget taxonomy, name, label, description, kind,
  category, purpose, policy, state, or lifecycle;
- the later Leg-to-Risk-Budget link or its prerequisite enforcement;
- constraint taxonomy, definition, policy, applicability, evaluation,
  satisfaction, prioritization, enforcement, limit, threshold, utilization, or
  breach detection;
- Recommendation action or direction, including BUY, HOLD, SELL, ADD, REDUCE,
  or WAIT, or opening, closing, long, short, or execution interpretation;
- semantic production, inference, calculation, ranking, confidence, priority,
  urgency, materiality, suitability, approval, rejection, override,
  explainability, audit, execution, capital movement, or lifecycle behavior;
- repositories, registries, resolvers, persistence, migrations, runtime,
  orchestration, workflow, CLI, automation, scheduling, monitoring, external
  APIs, hidden state, or third-party dependencies.

## 15. README requirements

`PortfolioAllocationLegCapitalBucketLink/README.md` is required and must be a
normative package contract consistent with this document. It must state,
without weakening or extending them:

1. the exact single responsibility, direction, Leg granularity, package name,
   and complete public API;
2. the exact model name, standard frozen/hashable dataclass form, two required
   fields, field types and order, foreign ownership, and absence of defaults,
   behavior, endpoint objects, and association identity;
3. the exact validator signature, validation order, first-failure rule,
   subclass rejection, exception types, and exact messages;
4. exact-string object identity, surrounding-whitespace, case, Unicode, and
   no-normalization preservation semantics;
5. standard structural equality and hashability;
6. many-at-either-endpoint and duplicate acceptance, no collection,
   uniqueness, deduplication, or ordering, and exact per-Leg optionality;
7. absence-as-no-record semantics and rejection of nullable, blank, sentinel,
   or default endpoint representations;
8. the exact production dependency/import allowlist and endpoint-import and
   endpoint-validator prohibitions;
9. foreign-ID-only endpoint and existence-proof boundaries;
10. every denormalization prohibition in Section 13;
11. separation from the later Risk Budget link and all constraints; and
12. the complete non-responsibilities in Section 14.

The README must not claim that the link validates endpoints, proves existence
or Portfolio alignment, reserves or assigns capital, enforces cardinality or
coverage, requires every Leg to have a Bucket, selects a primary Bucket,
contains Risk Budget association, or is an actionable allocation instruction.

## 16. Required unit-test contract

The implementation milestone must add `unittest` coverage proving all of the
following without changing or weakening existing tests.

### Model contract

- the model is a dataclass and is frozen;
- fields and type hints are exactly `allocation_leg_id: str` followed by
  `capital_bucket_id: str`;
- both fields have no default and no default factory;
- there are no slots, `__post_init__`, custom constructors, custom public
  methods, public properties, association identity, or extra fields;
- mutation of either field raises `FrozenInstanceError`; and
- structural equality and hashing cover both fields, with equal independently
  constructed links equal and equally hashed and each unequal field tested.

### Exact model and identifier validation

- `None`, unrelated objects, collections, and a model subclass fail the first
  exact-model check with the exact exception contract;
- each identifier independently rejects `None`, integers, bytes, and a `str`
  subclass with its exact type error;
- each identifier independently rejects empty and representative
  whitespace-only strings with its exact blank-value error;
- otherwise nonblank strings with surrounding whitespace, distinct case, and
  composed and decomposed Unicode are accepted and preserved exactly; and
- successful validation returns `None`.

### Validation order and preservation

- multi-invalid inputs prove every first-failure transition in the declared
  order, including type-before-blank and Leg-before-Bucket precedence;
- every failure asserts its exact exception type and fully anchored message;
- both exact supplied string objects remain retained before and after
  validation; and
- no normalization, conversion, coercion, copying, reconstruction, endpoint
  import, endpoint validator call, lookup, traversal, or hidden inference
  occurs.

### Multiplicity, optionality, and boundary

- independent duplicate links validate successfully;
- links sharing one `allocation_leg_id` validate independently;
- links sharing one `capital_bucket_id` validate independently;
- many links at either endpoint require no ordering and are accepted one at a
  time;
- optionality is represented by supplying no record, while `None`, blank IDs,
  sentinels, and defaults are not introduced as valid absence forms;
- the validator signature, production class/function definitions, and exact
  import allowlists match Sections 4 and 11;
- production source contains no endpoint import or validator call,
  denormalized identifier, forbidden field or responsibility, third-party
  import, collection, uniqueness, ordering, or hidden state behavior; and
- the README contains stable fragments for every Section 15 requirement and
  no contradictory claim.

After focused package tests pass, the complete repository `unittest`
regression suite must pass unchanged. Compilation and whitespace verification
must also pass.

## 17. Implementation file boundary

M49 implementation is limited to creating exactly:

```text
PortfolioAllocationLegCapitalBucketLink/
├── README.md
├── models.py
├── validation.py
└── tests/
    ├── __init__.py
    └── test_link.py
```

`models.py` contains exactly the one public model class.
`validation.py` contains exactly the one public validator function. Test-only
helpers and subclasses remain in `tests/test_link.py`.

M49 must not add a package-root `__init__.py`, classifier, applicability
module, semantic wrapper, calculation, persistence adapter, registry,
repository, resolver, schema, migration, runtime, CLI, configuration, fixture,
shared utility, or third-party dependency. It must not modify ADR-0002, any
roadmap, ADR-0001, M43–M48, either endpoint package, PortfolioRiskBudget, or any
accepted public contract.

This architecture document is the only M49 artifact added before
implementation. Production code and tests are not part of this
architecture-document milestone.

## 18. Compatibility audit

- **M43:** Allocation Proposal identity and Recommendation association remain
  unchanged and are not denormalized.
- **M44:** Proposal-to-Position multiplicity and duplicate-pair acceptance
  remain unchanged; M49 does not attach at Link or Proposal granularity.
- **M45:** Its supplied-chain applicability inputs, validation calls,
  comparisons, status order, and public API remain unchanged. M49 adds no
  Bucket comparison.
- **M47:** Allocation Leg remains the occurrence-level attachment point. Its
  identity, retained Link, validation, multiplicity, and public API remain
  unchanged.
- **M48:** Proposed absolute quantity fields, exact Decimal semantics,
  foreign-ID-only Leg attachment, multiplicity, public API, and
  non-responsibilities remain unchanged. M49 does not retain or reinterpret
  M48 content.
- **PortfolioCapitalBucket:** M49 references only its owned
  `capital_bucket_id` namespace. It neither imports nor changes the endpoint,
  duplicates `portfolio_id`, creates a reverse Leg collection, or proves
  Bucket existence or Portfolio alignment.
- **PortfolioRiskBudget:** M49 contains no `risk_budget_id`, does not import or
  change Risk Budget, and does not implement the later separate association or
  Bucket/Budget consistency.
- **ADR-0001:** M49 follows the accepted sequence of optional Leg-level
  funding/risk identity associations after measurable content and before
  constraints.
- **ADR-0002:** M49 implements only its first selected responsibility:
  directed Leg-to-Capital-Bucket, foreign IDs only, two fields in order, no
  relation identity, many at either endpoint, duplicate acceptance, optional
  per Leg, and no lookup or existence proof. Risk Budget and constraints stay
  later.
- **Constitution and Architecture Patterns:** M49 adds one minimal frozen
  Explicit Model and deterministic Validator boundary. Identity, structure,
  applicability, evaluation, and operation remain separate; no hidden lookup,
  inference, normalization, persistence, or runtime is introduced.
- **Stage 5 roadmap:** M49 advances structural Allocation Proposal support
  toward later constraints while leaving runtime, persistence, workflow, and
  automation outside Stage 5.

## 19. Acceptance criteria

The M49 architecture-document milestone is accepted only when:

1. this document alone freezes the package and API names, single
   responsibility, direction, granularity, model form, exact fields and order,
   validation order, exact exceptions, string and subclass rules, blank rules,
   preservation, equality/hashability, multiplicity, duplicates, optionality,
   dependencies, import allowlists and prohibitions, endpoint boundary,
   denormalization prohibitions, non-responsibilities, README, tests, and file
   boundary without implementation inference;
2. it implements ADR-0002's accepted Leg-to-Capital-Bucket decision without
   reopening topology, adding Risk Budget, or beginning constraints;
3. it preserves every M43–M48, Portfolio Capital Bucket, and Portfolio Risk
   Budget accepted identity, multiplicity, applicability, semantic, public
   API, dependency, and non-responsibility contract;
4. it changes no existing file and adds only this architecture document;
5. no production code, tests, package directory, roadmap edit, ADR edit,
   configuration, migration, runtime, persistence, CLI, or automation artifact
   is included; and
6. a future implementation and its README/tests can be judged for complete
   conformance using only this document.

The later M49 implementation is accepted only when all rules in this document
are implemented exactly, the focused and full regression tests pass, compile
and whitespace checks pass, and no accepted expectation changes.
