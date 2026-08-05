# M52 Frozen Architecture — Portfolio Allocation Leg Capital Bucket Link Applicability

- Repository: `/Users/takesimple/Projects/JOO`
- Stage: 5
- Milestone: M52
- Status: Frozen
- Predecessor: M51 `PortfolioAllocationLegAssociationConsistencyApplicability`
- Approved domain: `PortfolioAllocationLegCapitalBucketLinkApplicability`

## 1. Status and milestone

M52 is an architecture-document milestone only. It freezes one downstream
applicability boundary for an explicitly supplied M49 Capital Bucket link and
its accepted Allocation Leg, Capital Bucket, and Position inputs.

This document creates no implementation, package, test, README, runtime,
orchestration, persistence, API service, or collection. It changes no accepted
contract.

## 2. Context and motivation

M49 records only a foreign-ID link from an Allocation Leg identity to a
Capital Bucket identity. It deliberately does not load either endpoint or
establish Portfolio alignment. The accepted Allocation Leg retains an M44
Proposal Position Link, the accepted Capital Bucket stores its Portfolio
identity, and the accepted Position retains membership carrying its Portfolio
identity.

M51 separately classifies consistency among one M49 link, one M50 link, and
one Risk Budget endpoint. It does not load an Allocation Leg, Capital Bucket,
Position, or Portfolio alignment. The approved M52 boundary fills only the
remaining M49 applicability gap: exact endpoint identity and Portfolio
alignment for one caller-supplied complete comparison set.

## 3. Architectural decision

The future package name is exactly:

`PortfolioAllocationLegCapitalBucketLinkApplicability`

It will own one deterministic classification of one caller-selected set
containing:

1. one accepted M49
   `ExplicitPortfolioAllocationLegCapitalBucketLink`;
2. one accepted `ExplicitPortfolioAllocationLeg`;
3. one accepted `ExplicitPortfolioCapitalBucket`; and
4. one accepted `ExplicitPortfolioPosition`.

After validating all four inputs, classification compares only their stored
identities in the frozen order in Section 10. It returns the first mismatch or
`APPLICABLE`.

## 4. Domain responsibility

M52 owns exactly:

- the status taxonomy for this one applicability classification;
- validation of each supplied upstream input exactly once in declared input
  order;
- ordered exact stored-string comparisons;
- first-mismatch precedence; and
- the narrow `APPLICABLE` result for identity and Portfolio alignment of the
  supplied set.

It evaluates one supplied set only. It does not prove that an association is
true, current, unique, complete, authorized, economically appropriate, or
suitable for action.

## 5. Ownership and identity boundary

M52 is a new downstream applicability owner. It does not own or modify the
M49 link, Allocation Leg, Capital Bucket, Position, Membership, M50 link, M51
classification, or any of their identities.

M52 has no persistent applicability identity, `applicability_id`, composite
identity, applicability record, result dataclass, retained result object, or
caller-supplied result identity. Classification returns only an enum status.

## 6. Required complete comparison set

The classifier has exactly four required positional-or-keyword inputs in this
declared order:

1. `capital_bucket_link: ExplicitPortfolioAllocationLegCapitalBucketLink`
2. `leg: ExplicitPortfolioAllocationLeg`
3. `capital_bucket: ExplicitPortfolioCapitalBucket`
4. `position: ExplicitPortfolioPosition`

All four inputs are required. There are no defaults, optional inputs,
keyword-only parameters, variadics, policies, callbacks, mappings, or
collections.

Absence is outside the classifier invocation contract. M49 remains optional
at its structural boundary, but M52 is invoked only when the caller supplies
one complete comparison set. Absence produces no status and is not represented
by `None`, a nullable field, blank value, sentinel, default, special object, or
missing-input record. Supplying such a substitute is malformed input handled
by the accepted upstream validator, not a mismatch classification.

## 7. Upstream accepted model dependencies

M52 depends downstream on exactly these accepted model and validator
contracts:

- `PortfolioAllocationLegCapitalBucketLink`;
- `PortfolioAllocationLeg`;
- `PortfolioCapitalBucket`; and
- `PortfolioPosition`, including its accepted retained
  `ExplicitPortfolioMembership` validation.

The accepted Allocation Leg exposes its retained Proposal Position Link's
`position_id`. The accepted Capital Bucket exposes `portfolio_id`. The
accepted Position exposes `position_id` and its retained Membership's
`portfolio_id`. M52 consumes those exact stored fields after upstream
validation; it does not duplicate, reconstruct, or validate them locally.

M52 has no dependency on M48, M50, M51, Risk Budget, Proposal endpoint,
Recommendation, Snapshot, calculation, semantic production, constraint,
persistence, or runtime packages.

## 8. Classification result taxonomy

The future status name is exactly:

`PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus`

It is a standard `enum.Enum` with exactly these members, explicit string
values, and declaration order:

1. `ALLOCATION_LEG_ENDPOINT_MISMATCH = "ALLOCATION_LEG_ENDPOINT_MISMATCH"`
2. `CAPITAL_BUCKET_ENDPOINT_MISMATCH = "CAPITAL_BUCKET_ENDPOINT_MISMATCH"`
3. `POSITION_ENDPOINT_MISMATCH = "POSITION_ENDPOINT_MISMATCH"`
4. `PORTFOLIO_ENDPOINT_MISMATCH = "PORTFOLIO_ENDPOINT_MISMATCH"`
5. `APPLICABLE = "APPLICABLE"`

Every value is exactly its member name. The enum has no aliases, fields,
defaults, custom constructor, custom methods, properties, labels,
descriptions, severity, ranking, Boolean conversion, metadata, or persistent
identity. Standard Enum identity, equality, and hashing remain unmodified.

Mismatch statuses are valid classification results, not malformed-input
exceptions. There is no generic `NOT_APPLICABLE`, `MISSING_INPUT`,
`INVALID_INPUT`, `UNKNOWN`, `ERROR`, combined-mismatch, constraint, breach, or
severity status.

## 9. Ordered validation contract

Before any comparison, the future classifier invokes these accepted
validators exactly once each, with the exact supplied object, in declared
input order:

1. `validate_explicit_portfolio_allocation_leg_capital_bucket_link(capital_bucket_link)`;
2. `validate_explicit_portfolio_allocation_leg(leg)`;
3. `validate_explicit_portfolio_capital_bucket(capital_bucket)`; and
4. `validate_explicit_portfolio_position(position)`.

Validation uses the accepted upstream validators. M52 performs no local
duplication of upstream model, exact-type, field-type, blank-string, retained
model, membership, or field-order validation.

No comparison occurs until all four validators succeed. The first upstream
failure stops processing; later validators and every comparison are skipped.
Each upstream input is validated exactly once, never zero or multiple times.

## 10. Ordered exact-identity comparison contract

After all validation succeeds, exact stored string equality is evaluated
exactly in this order:

1. Compare M49 link `allocation_leg_id` against Allocation Leg
   `allocation_leg_id`. If unequal, return
   `ALLOCATION_LEG_ENDPOINT_MISMATCH`.
2. Compare M49 link `capital_bucket_id` against Capital Bucket
   `capital_bucket_id`. If unequal, return
   `CAPITAL_BUCKET_ENDPOINT_MISMATCH`.
3. Compare Allocation Leg retained Proposal Position Link `position_id`
   against Position `position_id`. If unequal, return
   `POSITION_ENDPOINT_MISMATCH`.
4. Compare Capital Bucket `portfolio_id` against Position Membership
   `portfolio_id`. If unequal, return `PORTFOLIO_ENDPOINT_MISMATCH`.
5. Otherwise return `APPLICABLE`.

This is the complete comparison set and order. No comparison is inserted,
removed, reordered, combined, or inferred.

## 11. Exact equality and preservation semantics

Every comparison uses exact stored string equality only. String value equality
determines alignment; string object identity is preserved but is not the
comparison rule.

M52 performs no trimming, case folding, Unicode normalization, aliasing,
canonicalization, transformation, coercion, conversion, copying,
reconstruction, derivation, hashing, generation, lookup, traversal,
resolution, or inference. Surrounding whitespace, case, composed or
decomposed Unicode form, code points, and every other stored difference remain
significant under exact string equality.

No supplied model, retained model, or field object is mutated or replaced.

## 12. First-mismatch precedence

The first unequal comparison in Section 10 wins. Once a mismatch is found,
later fields are not compared and later mismatches are neither observed nor
combined. Complete alignment alone returns `APPLICABLE`.

Precedence is therefore, in order:

1. Allocation Leg endpoint mismatch;
2. Capital Bucket endpoint mismatch;
3. Position endpoint mismatch;
4. Portfolio endpoint mismatch; and
5. `APPLICABLE`.

## 13. Applicability semantics

`APPLICABLE` means only that, for this exact supplied validated set:

- the M49 link names the supplied Allocation Leg;
- the M49 link names the supplied Capital Bucket;
- the Allocation Leg's retained Proposal Position Link names the supplied
  Position; and
- the supplied Capital Bucket and Position Membership carry equal Portfolio
  identities.

It means only identity and Portfolio alignment for the supplied set. It does
not mean endpoint existence outside the supplied records, M45 chain
applicability, M49 uniqueness, funding availability or sufficiency, capacity,
risk acceptance, constraint satisfaction, authorization, approval, trade
permission, or execution eligibility.

## 14. Domain invariants

1. One classification consumes exactly one explicitly supplied complete set.
2. All four required inputs are accepted upstream models.
3. Absence has no representation within M52.
4. Each upstream validator is invoked exactly once in declared input order.
5. The first upstream exception propagates unchanged.
6. All validation completes before any comparison.
7. Comparison uses exact stored string equality only.
8. The first mismatch wins in the order frozen in Section 10.
9. Classification is deterministic, pure, and stateless for the same supplied
   validated fields.
10. The result is one existing enum singleton and no applicability record.
11. M49 multiplicity, optionality, shared-endpoint behavior, and duplicate
    acceptance remain unchanged.
12. M52 owns no collection, uniqueness, coverage, or selection rule.
13. M52 is independent of M50 and M51.

## 15. Dependency direction

Dependencies flow only from M52 applicability to its four accepted upstream
model and validator packages. No upstream package imports M52. The M52 status
model depends only on the Python standard library.

This direction is compile-time domain layering, not runtime lookup. M52 does
not cause an endpoint, association, membership, or Portfolio to enumerate or
own downstream classifications.

## 16. Multiplicity, duplicates, and collection boundary

M52 evaluates one caller-selected set per invocation. It does not search,
enumerate, rank, aggregate, or select among links, Legs, Buckets, Positions,
Memberships, or classifier results.

M49 multiplicity and duplicate acceptance remain unchanged. Multiple M49
links may share either endpoint identity, and independently supplied exact
duplicates remain structurally accepted. M52 does not reject duplicates,
enforce global, per-endpoint, or pair uniqueness, require one Bucket per Leg,
require one Leg per Bucket, impose coverage, or create collection ownership.
Any valid caller-selected M49 record may participate independently in a
complete M52 comparison set.

## 17. Error and exception propagation responsibilities

M52 defines no local validation exception type or message. Malformed inputs
remain the responsibility of the accepted upstream validators in Section 9.

The first upstream exception propagates unchanged. M52 does not catch, wrap,
translate, replace, suppress, aggregate, annotate, chain, or reconstruct it.
Its object identity, type, message, and traceback remain unchanged. Unexpected
Python exceptions are also not caught.

For structurally valid inputs, an identity mismatch is not exceptional. It
returns the corresponding ordered mismatch status.

## 18. Explicit non-responsibilities

M52 does not own or perform:

- production, mutation, repair, normalization, replacement, or persistence of
  M49 links, Allocation Legs, Capital Buckets, Positions, Memberships, or any
  other endpoint;
- endpoint lookup, resolution, existence proof, authoritative issuance,
  registry access, repository access, traversal, mapping, or automatic entity
  resolution;
- M45 Proposal/Position/Recommendation/Snapshot chain reclassification;
- M48 quantity or unit interpretation, trade sizing, target holding, delta,
  weight, denominator, or rebalance calculation;
- M50 Risk Budget association, M51 association-consistency classification,
  Risk Budget participation, or any prerequisite enforcement;
- association or applicability identity, applicability records, nullable or
  sentinel absence, collection ownership, reverse collections, uniqueness,
  duplicate detection or rejection, deduplication, coverage, completeness,
  aggregation, ordering, ranking, precedence beyond first mismatch, or
  automatic record selection;
- funding amount, available or committed capital, balance, cash, reservation,
  capacity, currency, price, valuation, FX, NAV, capital movement, routing, or
  funding-source selection;
- risk amount, risk limit, threshold, tolerance, utilization, remaining
  capacity, concentration, ratio, percentage, risk policy, or breach
  detection;
- constraint taxonomy, definition, registration, policy, applicability,
  evaluation, satisfaction, prioritization, enforcement, breach, severity,
  remediation, or exception workflow;
- Recommendation actions or directions including BUY, HOLD, SELL, ADD,
  REDUCE, or WAIT, or opening, closing, long, short, and execution meaning;
- semantic production, inference, confidence, priority, urgency,
  materiality, suitability, approval, rejection, override, explainability,
  audit, execution, lifecycle, or operational decision behavior; or
- persistence, migration, schema, repositories, registries, resolvers,
  services, external APIs, runtime, orchestration, workflow, CLI, automation,
  scheduling, monitoring, hidden state, or third-party dependencies.

## 19. Relationship to M45, M49, M50, and M51

- **M45:** M52 follows the accepted validation-first, exact-comparison,
  ordered-status applicability pattern and its Portfolio-alignment precedent.
  M52 does not reclassify or imply the applicability of M45's Proposal,
  Recommendation, Snapshot, and Position chain.
- **M49:** M52 consumes one exact supplied M49 link and its validator without
  modifying the link's fields, optionality, many-at-either-endpoint
  multiplicity, duplicate acceptance, or structural non-responsibilities.
- **M50:** M52 has no M50 input or dependency. A Capital Bucket link may be
  classified without a Risk Budget link, and M52 neither establishes nor
  enforces M50 presence.
- **M51:** M52 has no M51 input or dependency. M51's Leg/Budget/Bucket
  consistency set and frozen comparisons remain separate and unchanged. An
  M51 result is neither required nor inferred by M52.

## 20. Future public and implementation boundary

The future complete public API is limited to:

- `PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus`; and
- `classify_portfolio_allocation_leg_capital_bucket_link_applicability()`.

The future classifier signature is exactly:

`classify_portfolio_allocation_leg_capital_bucket_link_applicability(capital_bucket_link: ExplicitPortfolioAllocationLegCapitalBucketLink, leg: ExplicitPortfolioAllocationLeg, capital_bucket: ExplicitPortfolioCapitalBucket, position: ExplicitPortfolioPosition) -> PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus`

After separate implementation authorization, implementation is bounded to one
new package with exactly:

```text
PortfolioAllocationLegCapitalBucketLinkApplicability/
├── README.md
├── models.py
├── classification.py
└── tests/
    ├── __init__.py
    └── test_applicability.py
```

`models.py` will contain exactly the one public status enum.
`classification.py` will contain exactly the one public classifier and no
private helper. No package-root `__init__.py`, `validation.py`, result model,
unchecked classifier, policy, constraint, calculation, persistence adapter,
repository, registry, resolver, service, API, runtime, CLI, configuration,
fixture, shared utility, collection, or third-party dependency belongs to the
future boundary.

This document does not authorize or introduce that implementation, package,
test, or README.

## 21. Acceptance criteria

M52 architecture is accepted only when:

1. this document alone freezes the milestone status, approved domain,
   responsibility, ownership, complete comparison set, upstream dependencies,
   status taxonomy, validation order, exact comparison order, mismatch
   precedence, applicability semantics, invariants, dependency direction,
   non-responsibilities, exception propagation, milestone relationships,
   future implementation boundary, and deferred work;
2. all four inputs are required and absence remains outside invocation;
3. each accepted upstream validator is called exactly once in declared input
   order, with unchanged first-exception propagation and no duplicated local
   validation;
4. the comparison order is exactly the five outcomes frozen in Section 10,
   using exact stored string equality, no normalization, lookup, or inference,
   and first mismatch wins;
5. `APPLICABLE` has only the narrow supplied-set identity and Portfolio
   alignment meaning;
6. M49 multiplicity and duplicate acceptance remain unchanged, M52 remains
   independent of M50 and M51, and no collection or uniqueness rule is added;
7. no implementation, package, test, README, runtime behavior, orchestration,
   repository, registry, resolver, service, API, persistence, collection,
   amount, capacity, risk-limit, constraint, approval, explainability, or
   audit artifact or responsibility is introduced;
8. exactly this one architecture document is untracked, no tracked file is
   modified, nothing is staged, and no implementation artifact exists; and
9. whitespace and final-newline verification pass.

## 22. Deferred work

Deferred responsibilities include all implementation and tests for M52; any
future Risk Budget path applicability; allocation constraint taxonomy,
definition, policy, applicability, and evaluation; capital amount and capacity
semantics; risk limits and utilization; collection ownership and uniqueness;
funding or trade calculation; explainability; human approval and override;
audit; persistence; runtime; orchestration; services and APIs; execution; and
Stage 6 automation.

No deferred responsibility is implied, designed, or authorized by this
document. Each requires its own later accepted architecture and authorization.
