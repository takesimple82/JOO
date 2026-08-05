# M51 Frozen Architecture — Portfolio Allocation Leg Association Consistency Applicability

- Repository: `/Users/takesimple/Projects/JOO`
- Stage: 5
- Milestone: M51
- Status: Frozen
- Predecessor: M50 `PortfolioAllocationLegRiskBudgetLink`

## 1. Milestone identity and responsibility

M51 is the first minimal unit of the Portfolio Allocation constraint phase. It
owns exactly one deterministic applicability classification for one explicitly
supplied comparison set consisting of:

- one accepted M49 Portfolio Allocation Leg to Capital Bucket link;
- one accepted M50 Portfolio Allocation Leg to Risk Budget link; and
- one accepted Portfolio Risk Budget endpoint.

After validating all three records, M51 determines whether the two links refer
to the same Allocation Leg, whether the M50 Risk Budget identity names the
supplied Risk Budget endpoint, and whether the M49 Capital Bucket identity
matches the supplied Risk Budget endpoint's Capital Bucket identity.

M51 owns no general constraint, breach, funding, risk-limit, Portfolio,
selection, lookup, persistence, or execution responsibility. It evaluates one
caller-selected comparison set only.

## 2. Authoritative source hierarchy

This document is governed, in order, by:

1. `JOO_CONSTITUTION.md`;
2. `ARCHITECTURE_PATTERNS.md`;
3. the accepted Stage 5 roadmap boundary;
4. ADR-0002;
5. the frozen and implemented M49 contract;
6. the frozen and implemented M50 contract;
7. the accepted `PortfolioRiskBudget` endpoint contract; and
8. accepted repository applicability/status conventions, especially
   `PortfolioAllocationProposalPositionLinkApplicability`.

This document freezes M51 without modifying or reinterpreting any source.

## 3. Package name

The exact package name is:

`PortfolioAllocationLegAssociationConsistencyApplicability`

This is a new downstream applicability package. It does not change M49, M50,
Portfolio Risk Budget, or any accepted endpoint or link package.

## 4. Exact public API

The complete and exact public API is:

- `PortfolioAllocationLegAssociationConsistencyApplicabilityStatus`
- `classify_portfolio_allocation_leg_association_consistency_applicability()`

Callers import the status from
`PortfolioAllocationLegAssociationConsistencyApplicability.models` and the
classifier from
`PortfolioAllocationLegAssociationConsistencyApplicability.classification`.
No package-root re-export is required.

There is no public or private result dataclass, validator, unchecked
classifier, Boolean helper, exception class, protocol, policy object, endpoint,
collection, alias, or additional public API.

## 5. Status model

`PortfolioAllocationLegAssociationConsistencyApplicabilityStatus` is a
standard `enum.Enum`, not a dataclass. It contains exactly these members,
explicit string values, and declaration order:

1. `ALLOCATION_LEG_ENDPOINT_MISMATCH = "ALLOCATION_LEG_ENDPOINT_MISMATCH"`
2. `RISK_BUDGET_ENDPOINT_MISMATCH = "RISK_BUDGET_ENDPOINT_MISMATCH"`
3. `CAPITAL_BUCKET_ENDPOINT_MISMATCH = "CAPITAL_BUCKET_ENDPOINT_MISMATCH"`
4. `APPLICABLE = "APPLICABLE"`

Every value is exactly its member name. The enum has no aliases, defaults,
fields, dataclass behavior, custom constructor, custom methods, properties,
labels, descriptions, severity, ranking, truth conversion, metadata, or
persistent identity. Standard Enum identity, equality, and hash behavior is
unmodified.

The mismatch statuses are valid deterministic classification results, not
malformed-input exceptions. `APPLICABLE` means only that the three frozen
identity comparisons align for this supplied set. It does not mean a
constraint is satisfied, a trade is permitted, capital is available, risk is
within limits, or execution is eligible.

## 6. Classifier name and signature

The exact classifier signature is:

`classify_portfolio_allocation_leg_association_consistency_applicability(capital_bucket_link: ExplicitPortfolioAllocationLegCapitalBucketLink, risk_budget_link: ExplicitPortfolioAllocationLegRiskBudgetLink, risk_budget: ExplicitPortfolioRiskBudget) -> PortfolioAllocationLegAssociationConsistencyApplicabilityStatus`

It has exactly three required positional-or-keyword parameters in this order:

1. `capital_bucket_link: ExplicitPortfolioAllocationLegCapitalBucketLink`
2. `risk_budget_link: ExplicitPortfolioAllocationLegRiskBudgetLink`
3. `risk_budget: ExplicitPortfolioRiskBudget`

There are no defaults, optional parameters, keyword-only parameters,
variadics, callbacks, policies, mappings, registries, repositories, or
collections.

## 7. Input model and optionality boundary

All three inputs are required exact accepted models. M49 and M50 associations
remain optional at their own Leg-level structural boundaries, but an M51
classification invocation represents an explicitly supplied complete
comparison set. M51 does not model association absence inside its status
taxonomy.

If an association or endpoint record is absent, the caller does not have a
complete M51 invocation. Passing `None`, a sentinel, an unrelated object, or a
substitute model is malformed input and fails upstream structural validation;
it is not a valid `NOT_APPLICABLE` or mismatch result.

This required-input design is the minimum accepted applicability pattern. It
avoids nullable fields, absence statuses, mappings, collection search, hidden
selection, lookup, and invented endpoint shells. M51 does not load an
Allocation Leg endpoint because the two accepted links already supply the only
Leg identities required for comparison.

## 8. Structural validation order

Before performing any identity comparison, the classifier invokes exactly
these accepted validators exactly once each, in this order, using the exact
supplied object:

1. `validate_explicit_portfolio_allocation_leg_capital_bucket_link(capital_bucket_link)`;
2. `validate_explicit_portfolio_allocation_leg_risk_budget_link(risk_budget_link)`;
3. `validate_explicit_portfolio_risk_budget(risk_budget)`.

The classifier does not duplicate their field checks locally. Exact model,
subclass, exact built-in `str`, blank-string, field-order, and preservation
rules remain owned by those upstream validators.

No comparison occurs until all three validators succeed. The first upstream
failure stops processing; later validators and all comparisons are skipped.
Each successful upstream input is validated once, never zero or multiple
times.

## 9. Exception contract

M51 defines no local validation exception type or message. Every malformed
input failure is the accepted exception produced by the first failing upstream
validator in Section 8.

The exact M49 validation failures available during the first call are:

| Failure | Exception | Exact message |
|---|---|---|
| wrong `capital_bucket_link` model type | `TypeError` | `link must be ExplicitPortfolioAllocationLegCapitalBucketLink` |
| wrong M49 `allocation_leg_id` type | `TypeError` | `allocation_leg_id must be str` |
| blank M49 `allocation_leg_id` | `ValueError` | `allocation_leg_id must not be blank` |
| wrong `capital_bucket_id` type | `TypeError` | `capital_bucket_id must be str` |
| blank `capital_bucket_id` | `ValueError` | `capital_bucket_id must not be blank` |

The exact M50 validation failures available during the second call are:

| Failure | Exception | Exact message |
|---|---|---|
| wrong `risk_budget_link` model type | `TypeError` | `link must be ExplicitPortfolioAllocationLegRiskBudgetLink` |
| wrong M50 `allocation_leg_id` type | `TypeError` | `allocation_leg_id must be str` |
| blank M50 `allocation_leg_id` | `ValueError` | `allocation_leg_id must not be blank` |
| wrong M50 `risk_budget_id` type | `TypeError` | `risk_budget_id must be str` |
| blank M50 `risk_budget_id` | `ValueError` | `risk_budget_id must not be blank` |

The exact Portfolio Risk Budget validation failures available during the third
call are:

| Failure | Exception | Exact message |
|---|---|---|
| wrong `risk_budget` model type | `TypeError` | `risk_budget must be ExplicitPortfolioRiskBudget` |
| wrong endpoint `risk_budget_id` type | `TypeError` | `risk_budget_id must be str` |
| blank endpoint `risk_budget_id` | `ValueError` | `risk_budget_id must not be blank` |
| wrong endpoint `capital_bucket_id` type | `TypeError` | `capital_bucket_id must be str` |
| blank endpoint `capital_bucket_id` | `ValueError` | `capital_bucket_id must not be blank` |

The classifier does not catch, wrap, translate, replace, suppress, aggregate,
annotate, or chain upstream exceptions. The exact upstream exception object
identity, type, message, and traceback propagation remain unchanged.

For valid upstream models, identity mismatch is never exceptional. It returns
the corresponding status in the frozen precedence order. Unexpected Python
exceptions are not caught.

## 10. Ordered identity comparisons and outcome taxonomy

After all structural validation succeeds, comparisons use exact stored string
equality and occur exactly in this order. The first mismatch wins:

1. Compare
   `capital_bucket_link.allocation_leg_id`
   with
   `risk_budget_link.allocation_leg_id`.
   If unequal, return `ALLOCATION_LEG_ENDPOINT_MISMATCH`.
2. Compare
   `risk_budget_link.risk_budget_id`
   with
   `risk_budget.risk_budget_id`.
   If unequal, return `RISK_BUDGET_ENDPOINT_MISMATCH`.
3. Compare
   `capital_bucket_link.capital_bucket_id`
   with
   `risk_budget.capital_bucket_id`.
   If unequal, return `CAPITAL_BUCKET_ENDPOINT_MISMATCH`.
4. If all three comparisons are equal, return `APPLICABLE`.

This order is exhaustive and deterministic. Allocation Leg alignment is
checked first because M51 evaluates records relevant to one Leg. Risk Budget
endpoint alignment is checked before reading that endpoint's Capital Bucket
identity for the final consistency comparison. A later mismatch is not
examined after an earlier mismatch.

The taxonomy contains no generic `NOT_APPLICABLE`, `MISSING_INPUT`,
`INVALID_INPUT`, `INCONSISTENT`, `UNKNOWN`, `ERROR`, Boolean result, combined
mismatch, breach, or severity status. Malformed invocation remains an
exception; valid inconsistency remains an ordered mismatch enum.

## 11. Result construction and observability

The classifier returns exactly one existing enum singleton from Section 5. It
constructs no result object, wrapper, explanation, record, collection, error,
identifier, metadata, or derived value.

The same validated field values always produce the same status. Repeated calls
are pure and stateless. The classifier records no comparison trace and exposes
no secondary result. Mismatch precedence is the only ordering it owns.

## 12. Equality, hashing, and preservation

Status equality and hashing are unmodified standard Enum identity semantics.
No custom equality or hash is implemented.

M51 retains no input in a result and does not mutate any supplied object or
field. It compares exact stored strings without trimming, case folding,
Unicode normalization, aliasing, canonicalization, conversion, coercion,
copying, reconstruction, derivation, hashing, generation, inference, or
resolution.

Surrounding whitespace, case, composed/decomposed Unicode, and all other code
points remain significant according to the accepted upstream string contracts.
String equality, not string object identity, determines comparison results;
the exact supplied string objects nevertheless remain unchanged.

## 13. Cardinality and supplied-set boundary

M51 evaluates exactly one caller-selected `capital_bucket_link`, one
caller-selected `risk_budget_link`, and one caller-selected `risk_budget`
endpoint per invocation.

It does not search multiple links, enumerate endpoints, accept a collection,
mapping, registry, or repository, select a preferred record, detect duplicates,
enforce uniqueness or coverage, enforce one M49 or M50 link per Leg, aggregate
statuses, define collection cardinality, or create reverse collections.

M49 and M50 continue to structurally accept independently supplied records
sharing either endpoint and exact duplicates. M51 neither revokes nor narrows
those contracts. Callers may invoke M51 independently for any explicitly
selected valid set; duplicate or structurally equal supplied records do not
cause rejection.

## 14. Dependency and exact import boundary

Production code may depend only on:

- Python standard-library `enum.Enum` in `models.py`;
- `PortfolioAllocationLegCapitalBucketLink.models` and `.validation` in
  `classification.py`;
- `PortfolioAllocationLegRiskBudgetLink.models` and `.validation` in
  `classification.py`;
- `PortfolioRiskBudget.models` and `.validation` in `classification.py`; and
- this package's own `models` module in `classification.py`.

`models.py` imports exactly from `enum`.
`classification.py` imports exactly from:

- `PortfolioAllocationLegAssociationConsistencyApplicability.models`;
- `PortfolioAllocationLegCapitalBucketLink.models`;
- `PortfolioAllocationLegCapitalBucketLink.validation`;
- `PortfolioAllocationLegRiskBudgetLink.models`;
- `PortfolioAllocationLegRiskBudgetLink.validation`;
- `PortfolioRiskBudget.models`; and
- `PortfolioRiskBudget.validation`.

Production code imports no Allocation Leg endpoint, Capital Bucket endpoint,
Proposal, Position, Recommendation, Portfolio, Snapshot, M48 content,
constraint, policy, calculation, persistence, runtime, third-party, collection,
registry, repository, resolver, database, API, CLI, or automation package.

No upstream package imports M51. Dependency direction remains downstream from
applicability to accepted structural contracts.

## 15. README requirements

The future
`PortfolioAllocationLegAssociationConsistencyApplicability/README.md` must be
a normative contract consistent with this document. It must state, without
weakening or extending:

1. the exact minimal responsibility and supplied-set boundary;
2. the exact package and complete public API;
3. the exact enum name, member names, values, order, and standard Enum
   equality/hash behavior;
4. the exact classifier signature, required parameter names, types, and order;
5. required-input optionality semantics and absence-as-malformed-invocation;
6. the exact upstream validator calls, once-only order, and unchanged
   exception-object propagation;
7. the exact comparison order, first-mismatch precedence, and all result
   meanings, including the narrow meaning of `APPLICABLE`;
8. exact-string comparison and preservation/no-normalization semantics;
9. the one-explicit-set cardinality boundary and preservation of M49/M50
   duplicate/shared-endpoint acceptance;
10. exact production dependency and import allowlists;
11. every explicit non-responsibility in Section 17; and
12. the exact future implementation file boundary and absence of runtime or
   constraint-engine behavior.

The README must not claim that M51 accepts optional `None` inputs, looks up or
selects records, validates endpoint existence, establishes general constraint
satisfaction, evaluates risk limits or funding, detects duplicates, enforces
uniqueness, proves execution eligibility, or modifies M49/M50 multiplicity.

## 16. Required future unit-test contract

The later implementation must add `unittest` coverage proving all of the
following without changing or weakening accepted tests.

### Public API and status model

- the public API contains exactly the status enum and classifier;
- the status is an `Enum`, not a dataclass;
- member names, explicit uppercase string values, declaration order, and count
  are exact;
- there are no aliases, custom public methods, properties, metadata, Boolean
  conversion, extra statuses, or result dataclass;
- mutation is unavailable under standard Enum behavior; and
- identity, equality, and hashes are standard Enum behavior.

### Signature, validation, and exception propagation

- the classifier signature has exactly the three required annotated
  positional-or-keyword parameters and return annotation from Section 6, with
  no defaults;
- each upstream validator is called exactly once with the exact supplied
  object and in the frozen order before comparison;
- `None`, unrelated objects, collections, and subclasses rejected by each
  upstream contract produce the exact upstream exception type and anchored
  message;
- every first-failure transition proves later validators and all comparisons
  do not run;
- the first upstream exception object propagates with exact identity; and
- the classifier defines no local validation exception or missing-input
  status.

### Ordered classification

- M49/M50 Allocation Leg mismatch returns
  `ALLOCATION_LEG_ENDPOINT_MISMATCH`;
- after Leg alignment, M50/Risk Budget identity mismatch returns
  `RISK_BUDGET_ENDPOINT_MISMATCH`;
- after Leg and Risk Budget alignment, M49/Risk Budget Capital Bucket mismatch
  returns `CAPITAL_BUCKET_ENDPOINT_MISMATCH`;
- complete alignment returns `APPLICABLE`;
- multi-mismatch cases prove exact first-mismatch precedence for every
  transition; and
- valid mismatch outcomes return statuses and do not raise exceptions.

### Exact strings and preservation

- equal independently supplied string objects compare equal;
- case differences, surrounding-whitespace differences, and composed versus
  decomposed Unicode differences produce the appropriate first mismatch;
- validation and classification retain every exact input and field object;
- no input or field is mutated; and
- production performs no normalization, aliasing, conversion, copying,
  reconstruction, lookup, or hidden inference.

### Cardinality, imports, and boundaries

- one explicitly supplied comparison set is evaluated without collection
  search or automatic record selection;
- structurally valid duplicate/equal M49 or M50 records can participate in
  independent calls without duplicate rejection or uniqueness enforcement;
- there is no registry, repository, mapping, reverse collection, collection
  cardinality, coverage, or aggregation behavior;
- exact production import allowlists match Section 14;
- production contains exactly one enum class and one public classifier
  function, with no validator, unchecked helper, result dataclass, or other
  production definition;
- forbidden imports, constraint responsibilities, risk/funding calculation,
  persistence, API, CLI, runtime, and orchestration are absent; and
- README stable fragments cover every Section 15 requirement and contain no
  contradictory claims.

Focused package tests must pass first, followed by the complete repository
per-tests-directory `unittest` regression unchanged. The package must compile
using an isolated external `PYTHONPYCACHEPREFIX`; the temporary cache must be
removed; no generated artifact may remain; and trailing-whitespace, tab, CRLF,
and final-newline checks must pass.

## 17. Explicit non-responsibilities

M51 does not own or perform:

- general Portfolio Allocation constraint taxonomy, registration,
  orchestration, aggregation, policy, evaluation, enforcement, satisfaction,
  or breach determination;
- breach severity, breach amount, remediation, exception handling, override,
  or prioritization;
- capital capacity, available or committed balance, funding amount,
  reservation, cash, currency, price, valuation, FX, NAV, or capital movement;
- risk amount, limit, threshold, tolerance, utilization, remaining capacity,
  concentration, ratio, percentage, or risk-policy evaluation;
- target weight, proposed quantity interpretation, unit conversion, trade
  sizing, rebalance logic, target holding, or allocation calculation;
- Recommendation action or semantics, including BUY, SELL, ADD, REDUCE, HOLD,
  or WAIT;
- approval, rejection, explainability, audit, execution, execution eligibility,
  lifecycle, or operational decision;
- endpoint production, endpoint existence proof, lookup, resolution, registry,
  repository, database access, mapping, traversal, or identity
  canonicalization;
- uniqueness, duplicate detection or rejection, deduplication, coverage,
  collection cardinality, reverse collections, automatic selection among
  multiple records, or collection-level consistency;
- mutation, repair, normalization, replacement, or persistence of M49, M50,
  or Portfolio Risk Budget records;
- persistence, migration, schema, API, CLI, runtime, orchestration, workflow,
  automation, scheduling, monitoring, external integration, hidden state, or
  third-party dependencies.

M51 does not prove that an association is true, authorized, complete, current,
unique, economically appropriate, or suitable for action. It proves only the
ordered exact-identity classification of one supplied validated set.

## 18. Future implementation file boundary

The later implementation is limited to exactly:

```text
PortfolioAllocationLegAssociationConsistencyApplicability/
├── README.md
├── models.py
├── classification.py
└── tests/
    ├── __init__.py
    └── test_applicability.py
```

`models.py` contains exactly the one public status enum.
`classification.py` contains exactly the one public classifier function and no
private helper. Test-only helpers and subclasses remain in
`tests/test_applicability.py`.

No package-root `__init__.py`, `validation.py`, evaluation module, result
dataclass, policy, constraint, classifier helper, runtime, persistence adapter,
repository, registry, resolver, mapping, schema, migration, API, CLI,
configuration, fixture, shared utility, or third-party dependency may be
added.

This future implementation boundary is explicitly not authorized by the
current architecture-document task.

## 19. Compatibility audit

- **ADR-0002:** M51 owns the deferred comparison between M49's Capital Bucket
  identity and the supplied Risk Budget endpoint's Capital Bucket identity,
  while preserving separate M49/M50 records and avoiding lookup.
- **M49:** Its foreign-ID structure, optionality, duplicates, shared endpoints,
  public API, validation, and non-responsibilities remain unchanged.
- **M50:** Its foreign-ID structure, optionality, duplicates, shared endpoints,
  M49 prerequisite non-enforcement, public API, validation, and
  non-responsibilities remain unchanged.
- **Portfolio Risk Budget:** Its `risk_budget_id` and `capital_bucket_id` are
  consumed only from the exact supplied validated endpoint. M51 does not change
  or reinterpret that endpoint.
- **Applicability conventions:** M51 uses an ordered Enum taxonomy, validates
  every required upstream input exactly once before comparison, propagates the
  first upstream exception unchanged, and returns the first mismatch or
  `APPLICABLE`.
- **Stage 5:** M51 is the smallest consistency applicability prerequisite. It
  does not open general constraint definition, aggregation, breach, funding,
  risk evaluation, approval, or execution.

## 20. Acceptance criteria and authorization status

The M51 architecture document is ready for review only when:

1. this document alone freezes responsibility, sources, package, complete
   public API, status representation, exact enum members/values/order,
   function signature, input types/order/defaults, optionality, upstream
   validation order, exception propagation, comparison order, outcome
   precedence, result construction, equality/hash behavior, preservation,
   cardinality, imports, README, tests, non-responsibilities, file boundary,
   compatibility, and authorization status without implementation inference;
2. malformed input is unambiguously separated from valid mismatch and
   `APPLICABLE` outcomes;
3. it remains minimal and consistent with ADR-0002, M49, M50, Portfolio Risk
   Budget, Constitution, Architecture Patterns, Stage 5, and accepted
   applicability conventions;
4. it adds only
   `docs/M51_PORTFOLIO_ALLOCATION_LEG_ASSOCIATION_CONSISTENCY_APPLICABILITY_ARCHITECTURE.md`
   and changes no existing file;
5. it creates no production package, test, implementation, roadmap or ADR
   edit, configuration, persistence, runtime, API, CLI, orchestration,
   automation, M52, or generated artifact; and
6. the document passes changed-boundary, whitespace, and final-newline
   verification with an empty staged state.

The current task authorizes only this frozen architecture document. M51
implementation is not authorized until separate review and approval. M52 and
all broader constraint architecture remain unauthorized.
