# M50 Frozen Architecture — Portfolio Allocation Leg to Risk Budget Link

- Repository: `/Users/takesimple/Projects/JOO`
- Stage: 5
- Milestone: M50
- Status: Frozen
- Predecessor: M49 `PortfolioAllocationLegCapitalBucketLink`
- Architecture baseline: ADR-0002 and the frozen M49 contract

## 1. Repository and milestone context

M43–M49 establish the accepted Recommendation, Allocation Proposal, Proposal
Position Link, Allocation Leg, proposed-absolute-quantity, and Leg-to-Capital-
Bucket structural chain. In the sequence fixed by ADR-0002, M50 adds only the
second optional resource-identity association: a directed relation from one
Portfolio Allocation Leg identity to one Portfolio Risk Budget identity.

This is an architecture-document milestone only. It changes no accepted
package, roadmap, ADR, runtime, persistence, or operational responsibility. It
does not implement M50, begin M51, or open constraint architecture.

## 2. Package name

The exact package name is:

`PortfolioAllocationLegRiskBudgetLink`

This is a new domain-contract package. It is separate from M49 and does not
modify the Allocation Leg, Capital Bucket, Risk Budget, or any M43–M49 package.

## 3. Responsibility

The package owns exactly one explicit, directed, caller-supplied structural
link from one Portfolio Allocation Leg identity to one Portfolio Risk Budget
identity.

The association operates at Allocation Leg granularity, never Allocation
Proposal granularity. It records only the supplied identity pair. It does not
establish funding, risk capacity, constraint applicability, endpoint
existence, Portfolio or Capital Bucket consistency, suitability, approval, or
any economic or operational meaning.

## 4. Public API

The complete and exact public API is:

- `ExplicitPortfolioAllocationLegRiskBudgetLink`
- `validate_explicit_portfolio_allocation_leg_risk_budget_link()`

Callers import the model from `PortfolioAllocationLegRiskBudgetLink.models`
and the validator from `PortfolioAllocationLegRiskBudgetLink.validation`. No
package-root re-export is required.

No other class, function, property, public method, enum, alias, protocol, or
constant is public API.

The validator signature has exactly one positional-or-keyword parameter named
`link`, annotated as `ExplicitPortfolioAllocationLegRiskBudgetLink`, and a
return annotation of `None`:

`validate_explicit_portfolio_allocation_leg_risk_budget_link(link: ExplicitPortfolioAllocationLegRiskBudgetLink) -> None`

## 5. Model and field ownership

`ExplicitPortfolioAllocationLegRiskBudgetLink` is a standard
`@dataclass(frozen=True)` structural model containing exactly these required
fields in this order:

1. `allocation_leg_id: str`
2. `risk_budget_id: str`

The model has no defaults, default factories, slots, `__post_init__`, custom
constructor, constructor validation, custom public methods, properties,
derived fields, aliases, metadata fields, or additional fields.

`allocation_leg_id` is a foreign opaque identifier canonical only in the
Portfolio Allocation Leg namespace. `risk_budget_id` is a foreign opaque
identifier canonical only in the Portfolio Risk Budget namespace. The package
owns the relation, not either endpoint identity.

The model has no association identity, `link_id`, generated or composite
identity, retained endpoint object, `capital_bucket_id`, `portfolio_id`,
Proposal, Position, Recommendation, unit, quantity, value, amount, limit,
status, timestamp, or lifecycle field.

## 6. Validation order

`validate_explicit_portfolio_allocation_leg_risk_budget_link()` validates
exactly in this order:

1. `link` is the exact `ExplicitPortfolioAllocationLegRiskBudgetLink` model
   type;
2. `allocation_leg_id` is the exact built-in `str` type;
3. `allocation_leg_id` is not empty or whitespace-only;
4. `risk_budget_id` is the exact built-in `str` type;
5. `risk_budget_id` is not empty or whitespace-only; and
6. return `None`.

Exact-type checks use exact type identity. Model subclasses and `str`
subclasses are rejected. The first failure in the declared order wins. No
later field access or check occurs after a failure.

The validator invokes no endpoint or M49 validator and performs no collection,
cross-record, applicability, consistency, funding, risk, or constraint check.

## 7. Exception contract

Local validation failures raise exactly these exception types and messages:

| Failure | Exception | Exact message |
|---|---|---|
| wrong `link` type | `TypeError` | `link must be ExplicitPortfolioAllocationLegRiskBudgetLink` |
| wrong `allocation_leg_id` type | `TypeError` | `allocation_leg_id must be str` |
| empty or whitespace-only `allocation_leg_id` | `ValueError` | `allocation_leg_id must not be blank` |
| wrong `risk_budget_id` type | `TypeError` | `risk_budget_id must be str` |
| empty or whitespace-only `risk_budget_id` | `ValueError` | `risk_budget_id must not be blank` |

Messages contain no prefix, suffix, supplied value, or chained explanatory
text. There is no upstream exception contract because no upstream validator is
called. Unexpected Python exceptions are not caught.

## 8. Exact-string and preservation semantics

The model retains the exact caller-supplied `allocation_leg_id` and
`risk_budget_id` string objects. Validation does not replace either object.

Surrounding whitespace on an otherwise nonblank identifier is accepted and
preserved. Case, composed or decomposed Unicode form, code points, and all
other characters remain exact. Construction and validation do not trim,
case-fold, normalize Unicode, canonicalize, transform, coerce, convert, copy,
reconstruct, derive, hash, generate, infer, look up, resolve, sort, or mutate
either field or the link.

Blank means exactly an empty string or a string for which the built-in
`str.strip()` result is empty. Blank detection is validation-only. A nonblank
value is never replaced by its stripped result.

## 9. Equality and hashability

Equality is unmodified standard frozen-dataclass structural equality over both
fields in declared order. Hashability is the unmodified standard
frozen-dataclass hash contract.

Independently constructed links with equal field values are equal and have
equal hashes. A difference in either field makes links unequal under standard
string equality. There is no identity-only, Leg-only, Risk-Budget-only,
case-insensitive, normalized, or custom equality or hashing.

## 10. Multiplicity, duplicates, and optionality

The association is optional at Portfolio Allocation Leg granularity.
Optionality means that absence is represented only by absence of a record. It
is not represented by `None`, a blank identifier, sentinel, default, or
special instance. Every supplied record requires both exact nonblank
identifiers.

Single-record structural validation does not enforce collection cardinality.
When records are supplied and validated independently:

- zero or more records may share the same `allocation_leg_id`;
- zero or more records may share the same `risk_budget_id`;
- exact duplicate records are structurally accepted; and
- structurally equal independently constructed links are accepted.

The package owns no global, per-Leg, per-Risk-Budget, or pair uniqueness,
duplicate detection or rejection, deduplication, exclusivity, one-to-one
cardinality, one-to-many cardinality enforcement, collection, collection
cardinality, reverse collection, ordering, aggregation, completeness,
coverage, precedence, or cross-record consistency.

Any future uniqueness, coverage, or collection rule requires a separately
accepted architecture boundary with its own domain justification. M50 does not
anticipate or promise a future restriction on how many Risk Budget association
records may share one Leg or Risk Budget identity.

## 11. Cross-record policy and M49 relationship

Architecture sequencing expects a Leg carrying an M50 Risk Budget link also to
carry a separate M49 Leg-to-Capital-Bucket link. M50's single-record model and
validator must not require, retrieve, validate, or prove that prerequisite.

Consistency between the M49 `capital_bucket_id` and the accepted Portfolio
Risk Budget endpoint's own `capital_bucket_id` is deferred to a later
applicability or constraint architecture. M50 does not import either record,
look up the Risk Budget, traverse to its Bucket, compare identifiers, or
classify consistency.

M50 must not combine `allocation_leg_id`, `capital_bucket_id`, and
`risk_budget_id` in one record. M49 and M50 remain separate independently
supplied links with separate responsibilities.

## 12. Dependency and import boundary

Production code may depend only on:

- Python standard-library `dataclasses` in `models.py`; and
- this package's own `models` module in `validation.py`.

`models.py` imports exactly from `dataclasses`.
`validation.py` imports exactly from
`PortfolioAllocationLegRiskBudgetLink.models`.

Production code imports no third-party package and no existing JOO domain
package. In particular, it must not import from `PortfolioAllocationLeg`,
`PortfolioRiskBudget`, `PortfolioCapitalBucket`,
`PortfolioAllocationLegCapitalBucketLink`, M43–M49, endpoint validators,
applicability, semantic, calculation, constraint, persistence, or runtime
packages.

The model does not import its validator. No accepted endpoint or M49 package
imports this package. Dependency direction and all accepted contracts remain
unchanged.

## 13. Endpoint and existence-proof boundary

This foreign-ID-only link retains no `ExplicitPortfolioAllocationLeg`,
`ExplicitPortfolioRiskBudget`, `ExplicitPortfolioCapitalBucket`, M49 link, or
other endpoint object. It invokes no endpoint, association, or upstream
validator.

Structural validation proves only the exact M50 link model and exact nonblank
string shapes of its two fields. It does not prove that either endpoint exists,
was authoritatively issued, is valid, is unique, is active, belongs to a
particular Portfolio or Capital Bucket, is mutually aligned, or is suitable.
It performs no lookup, resolution, registry or repository access, traversal,
membership check, endpoint consistency check, or existence proof.

## 14. Denormalization prohibitions

The model must not contain, retain, look up, or derive:

- `capital_bucket_id`;
- `allocation_proposal_id`;
- `position_id`;
- `recommendation_id`;
- `portfolio_id` or `portfolio_snapshot_id`;
- `unit_id`;
- quantity, value, amount, limit, balance, capacity, currency, weight, ratio,
  percentage, status, or timestamp fields; or
- a retained Proposal Position Link, Allocation Leg, Capital Bucket, Risk
  Budget, M49 link, or any other endpoint object.

Proposal and Position identities remain reachable only through the accepted
Leg's retained Link. A Risk Budget's Capital Bucket identity remains owned by
the accepted Risk Budget endpoint. Reachability does not authorize hidden
lookup, traversal, copying, or denormalization.

## 15. Non-responsibilities and explicit exclusions

This package does not own or perform:

- Allocation Leg, Allocation Proposal, Proposal Position Link, Position,
  Recommendation, Portfolio, Snapshot, Membership, Capital Bucket, Risk
  Budget, or M49 link production, validation, lookup, resolution, registry
  access, or existence proof;
- endpoint validity, endpoint uniqueness, Portfolio alignment,
  Bucket-to-Portfolio applicability, Leg-to-Proposal applicability, or Capital
  Bucket/Risk-Budget consistency checking;
- the M49 prerequisite's lookup, validation, applicability, or enforcement;
- association identity, automatic or composite identity generation, link or
  endpoint uniqueness, duplicate detection or rejection, deduplication,
  exclusivity, one-to-one cardinality, one-to-many cardinality enforcement,
  collections, collection cardinality, reverse collections, ordering,
  aggregation, completeness, coverage, precedence, or cross-record
  consistency;
- Proposal-level association or a combined Leg-Bucket-Budget record;
- funding amounts, available or committed capital, cash, balances, capacity,
  reservation, currency, price, valuation, FX, NAV, routing, or capital
  movement;
- risk amounts, limits, thresholds, tolerances, utilization, remaining
  capacity, ratios, percentages, concentration, policy, or breach detection;
- allocation quantity, unit, target holding, delta, portfolio weight,
  denominator, rebalance, or any quantity or weight interpretation;
- constraint definition, taxonomy, applicability, evaluation, satisfaction,
  prioritization, enforcement, limits, thresholds, utilization, or breach;
- Recommendation action or semantics, including BUY, SELL, ADD, REDUCE, HOLD,
  or WAIT, or opening, closing, long, short, or execution direction;
- semantic production, inference, calculation, ranking, confidence, priority,
  urgency, materiality, suitability, approval, rejection, override,
  explainability, audit, execution, or lifecycle behavior;
- persistence, migration, repositories, registries, resolvers, external API,
  CLI, runtime, orchestration, workflow, automation, scheduling, monitoring,
  hidden state, or third-party dependencies.

## 16. README requirements

`PortfolioAllocationLegRiskBudgetLink/README.md` is required for the later
implementation and must be a normative package contract consistent with this
document. It must state, without weakening or extending them:

1. the exact responsibility, direction, Leg granularity, package name, and
   complete public API;
2. the exact model name, standard frozen/hashable dataclass form, two required
   fields, field types and order, foreign ownership, and absence of defaults,
   behavior, endpoint objects, association identity, and denormalized Bucket;
3. the exact validator signature, validation order, first-failure rule,
   subclass rejection, exception types, and exact messages;
4. exact-string object identity, surrounding-whitespace, case, composed and
   decomposed Unicode, and no-normalization preservation semantics;
5. standard structural equality and hashability;
6. optionality at Leg granularity, zero-or-more records sharing either
   endpoint, independent duplicate acceptance, lack of single-record
   collection-cardinality enforcement, and absence of uniqueness, duplicate
   rejection, exclusivity, one-to-one policy, one-to-many enforcement,
   collection ownership, cross-record consistency, or ordering;
7. absence-as-no-record semantics and rejection of `None`, blank, sentinel,
   default, or special-object absence representations;
8. the M49 prerequisite architecture policy, its non-enforcement by M50, and
   deferral of Bucket/Risk-Budget consistency to later applicability or
   constraint architecture;
9. the exact dependency/import allowlist and endpoint, M49, and endpoint-
   validator import prohibitions;
10. foreign-ID-only endpoint and existence-proof boundaries;
11. every denormalization prohibition in Section 14; and
12. the complete non-responsibilities and exclusions in Section 15.

The README must not claim that M50 validates endpoints, proves existence or
alignment, enforces the M49 prerequisite, checks Bucket/Budget consistency,
restricts how many records may share a Leg or Risk Budget, rejects duplicates,
enforces uniqueness or collection cardinality, reserves funding, owns risk
limits, defines constraints, contains `capital_bucket_id`, operates at
Proposal granularity, or produces an actionable instruction.

## 17. Required implementation unit-test contract

The later implementation milestone must add `unittest` coverage proving all
of the following without changing or weakening existing tests.

### Model contract

- the model is a dataclass and is frozen;
- fields and annotations are exactly `allocation_leg_id: str` followed by
  `risk_budget_id: str`;
- both fields have no default and no default factory;
- there are no slots, `__post_init__`, custom constructors, custom public
  methods, public properties, association identity, endpoint objects,
  denormalized Bucket, or extra fields;
- mutation of each field raises `FrozenInstanceError`; and
- structural equality and hashing cover both fields, including equal
  independently constructed records and each unequal-field transition.

### Exact model and string validation

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

- multi-invalid inputs prove every first-failure transition, including
  type-before-blank and Leg-before-Risk-Budget precedence;
- every failure asserts its exact exception type and full anchored message;
- both exact supplied string objects remain identical before and after
  validation; and
- no trimming, normalization, case folding, conversion, coercion, copying,
  reconstruction, endpoint or M49 import, validator call, lookup, traversal,
  consistency comparison, or hidden inference occurs.

### Multiplicity, optionality, cross-record policy, and boundary

- independently supplied records sharing one `allocation_leg_id` validate;
- independently supplied records sharing one `risk_budget_id` validate;
- exact duplicate and structurally equal independent records validate;
- optionality is represented by supplying no record, while `None`, blank IDs,
  sentinels, and defaults are not introduced as valid absence forms;
- multiple records sharing one `allocation_leg_id`, multiple records sharing
  one `risk_budget_id`, and exact duplicates are accepted without uniqueness,
  exclusivity, duplicate rejection, or collection-cardinality enforcement;
- the single-record validator does not require an M49 record or compare any
  Capital Bucket identifier;
- the validator signature, production class/function definitions, and exact
  import allowlists match Sections 4 and 12;
- production source contains no endpoint or M49 import or validator call,
  `capital_bucket_id`, other forbidden field or responsibility, third-party
  import, collection, reverse collection, uniqueness, duplicate rejection,
  ordering, prerequisite, or hidden-state behavior; and
- the README contains stable fragments for every Section 16 requirement and
  contains no contradictory ownership, consistency, risk, funding,
  constraint, or operational claim.

The implementation must run focused M50 tests, then the repository's complete
per-tests-directory `unittest` regression unchanged. It must compile the new
package using an isolated external `PYTHONPYCACHEPREFIX`, remove the temporary
cache, prove no generated artifacts remain, and pass trailing-whitespace, tab,
CRLF, and final-newline verification.

## 18. Future implementation file boundary

The later M50 implementation is limited to creating exactly:

```text
PortfolioAllocationLegRiskBudgetLink/
├── README.md
├── models.py
├── validation.py
└── tests/
    ├── __init__.py
    └── test_link.py
```

`models.py` will contain exactly the one public model class.
`validation.py` will contain exactly the one public validator function.
Test-only helpers and subclasses will remain in `tests/test_link.py`.

This implementation boundary is explicitly not authorized by the current M50
architecture-document task. No package directory, production code, test,
package-root `__init__.py`, classifier, applicability module, constraint,
semantic wrapper, calculation, persistence adapter, registry, repository,
resolver, schema, migration, runtime, API, CLI, configuration, fixture, shared
utility, automation, or third-party dependency may be created now.

## 19. Compatibility audit

- **ADR-0002:** M50 follows the required ordered second association, keeps M49
  and M50 separate, omits `capital_bucket_id`, does not enforce the M49
  prerequisite, and defers Bucket/Risk-Budget consistency and constraints.
- **M49:** Its fields, public API, multiplicity, optionality, endpoint boundary,
  and non-responsibilities remain unchanged. M50 neither imports nor embeds
  M49 and introduces no combined record.
- **Portfolio Allocation Leg:** It remains the occurrence-level attachment
  point. Its identity, retained Proposal Position Link, validation, and public
  API do not change.
- **Portfolio Risk Budget:** M50 references only its owned `risk_budget_id`
  namespace. It neither imports nor changes the endpoint, duplicates the
  endpoint's `capital_bucket_id`, proves existence, nor interprets risk.
- **Accepted Stage 5 conventions:** M50 uses the Explicit Model plus Validator
  separation, a frozen structural dataclass, exact built-in types,
  first-failure validation, stable messages, foreign IDs only, no endpoint
  imports, duplicate structural acceptance, and no collection or runtime.
- **Stage sequencing:** M50 freezes only the second structural association.
  M51 and all applicability, consistency, constraint, approval, execution,
  persistence, orchestration, and automation work remain unopened.

## 20. Acceptance criteria

The M50 architecture-document milestone is ready for review only when:

1. this document alone freezes the package and API names, responsibility,
   direction, granularity, model form, exact fields and order, validator
   signature and validation order, exact exceptions, string and subclass
   rules, blank rules, preservation, equality/hashability, zero-or-more
   structural multiplicity, duplicates, optionality, M49 prerequisite policy,
   non-enforcement and consistency deferral, dependencies, exact import
   allowlists and prohibitions, endpoint boundary, denormalization,
   non-responsibilities, README, tests, and future file boundary without
   implementation inference;
2. it is self-contained, deterministic, implementation-ready after approval,
   consistent with ADR-0002 and M49, and contains no speculative behavior;
3. it changes no existing file and adds only
   `docs/M50_PORTFOLIO_ALLOCATION_LEG_RISK_BUDGET_ASSOCIATION_ARCHITECTURE.md`;
4. it creates no implementation package, test, roadmap or ADR edit,
   configuration, migration, persistence, runtime, API, CLI, orchestration,
   automation, or M51 artifact;
5. the authorized document passes whitespace and final-newline verification,
   nothing is staged, and the repository otherwise remains clean; and
6. a future implementation, README, and tests can be judged for complete
   conformance using only this document.
