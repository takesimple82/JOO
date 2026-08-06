# M53 Frozen Architecture — Portfolio Allocation Leg Risk Budget Link Applicability

- Repository: `/Users/takesimple/Projects/JOO`
- Stage: 5
- Milestone: M53
- Status: Frozen
- Predecessor: M52 `PortfolioAllocationLegCapitalBucketLinkApplicability`
- Approved domain: `PortfolioAllocationLegRiskBudgetLinkApplicability`

## 1. Status and milestone

M53 is an architecture-document milestone only. It freezes one downstream
applicability boundary for an explicitly supplied M50 Risk Budget link and its
accepted Allocation Leg, Risk Budget, Capital Bucket, and Position inputs.

This document creates no implementation, package, test, README, runtime,
orchestration, persistence, API service, or collection. It changes no accepted
contract.

## 2. Context and motivation

M50 records only a foreign-ID link from an Allocation Leg identity to a Risk
Budget identity. It deliberately does not load either endpoint or establish
the Risk Budget's Capital Bucket and Portfolio path. The accepted Risk Budget
stores its Capital Bucket identity, the accepted Capital Bucket stores its
Portfolio identity, the accepted Allocation Leg retains an M44 Proposal
Position Link, and the accepted Position retains Membership carrying its
Portfolio identity.

M51 separately classifies consistency among one M49 link, one M50 link, and
one Risk Budget endpoint. M52 separately classifies the M49 Capital Bucket
path. Neither loads or classifies the complete M50 Risk Budget path frozen
here. M53 fills only that deferred gap: exact endpoint identity and Portfolio
alignment for one caller-supplied complete comparison set.

## 3. Architectural decision

The future package name is exactly:

`PortfolioAllocationLegRiskBudgetLinkApplicability`

It will own one deterministic classification of one caller-selected set
containing:

1. one accepted M50 `ExplicitPortfolioAllocationLegRiskBudgetLink`;
2. one accepted `ExplicitPortfolioAllocationLeg`;
3. one accepted `ExplicitPortfolioRiskBudget`;
4. one accepted `ExplicitPortfolioCapitalBucket`; and
5. one accepted `ExplicitPortfolioPosition`.

After validating all five inputs, classification compares only their stored
identities in the frozen order in Section 10. It returns the first mismatch or
`APPLICABLE`.

## 4. Responsibility boundary

M53 owns exactly:

- the status taxonomy for this one applicability classification;
- validation of each supplied upstream input exactly once in declared input
  order;
- ordered exact stored-string comparisons;
- first-mismatch precedence; and
- the narrow `APPLICABLE` result for endpoint identity and Portfolio alignment
  of the supplied set.

It evaluates one supplied set only. It does not prove that an association is
true, current, unique, complete, authorized, economically appropriate, or
suitable for action.

## 5. Ownership and identity

M53 is a new downstream applicability owner. It does not own or modify the M50
link, Allocation Leg, Risk Budget, Capital Bucket, Position, Membership, M49
link, M51 classification, M52 classification, or any of their identities.

M53 has no persistent applicability identity, `applicability_id`, composite
identity, applicability record, result dataclass, retained result object, or
caller-supplied result identity. Classification returns only an enum status.

## 6. Complete comparison set

The classifier has exactly five required positional-or-keyword inputs in this
declared order:

1. `risk_budget_link: ExplicitPortfolioAllocationLegRiskBudgetLink`
2. `leg: ExplicitPortfolioAllocationLeg`
3. `risk_budget: ExplicitPortfolioRiskBudget`
4. `capital_bucket: ExplicitPortfolioCapitalBucket`
5. `position: ExplicitPortfolioPosition`

All five inputs are required. There are no defaults, optional inputs,
keyword-only parameters, variadics, policies, callbacks, mappings, or
collections.

Absence is outside the classifier invocation contract. M50 remains optional
at its structural boundary, but M53 is invoked only when the caller supplies
one complete comparison set. Absence produces no status and is not represented
by `None`, a nullable field, blank value, sentinel, default, special object,
missing-input status, collection, or optional parameter. A substitute is
malformed input handled by the accepted upstream validator, not a mismatch
classification.

## 7. Upstream dependencies

M53 depends downstream on exactly these accepted model and validator
contracts:

- `PortfolioAllocationLegRiskBudgetLink`;
- `PortfolioAllocationLeg`;
- `PortfolioRiskBudget`;
- `PortfolioCapitalBucket`; and
- `PortfolioPosition`, including its accepted retained
  `ExplicitPortfolioMembership` validation.

The accepted Allocation Leg exposes `position_id` through its retained
Proposal Position Link. The accepted Risk Budget exposes `capital_bucket_id`.
The accepted Capital Bucket exposes `capital_bucket_id` and `portfolio_id`.
The accepted Position exposes `position_id` and its retained Membership's
`portfolio_id`. M53 consumes those exact stored fields after upstream
validation; it does not duplicate, reconstruct, or validate them locally.

M53 has no dependency on M48, M49, M51, M52, Proposal, Recommendation,
Snapshot, calculation, semantic production, constraint, persistence, runtime,
repository, registry, resolver, service, API, orchestration, or automation
packages.

## 8. Status taxonomy

The future status name is exactly:

`PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus`

It is a standard `enum.Enum` with exactly these members, explicit string
values, and declaration order:

1. `ALLOCATION_LEG_ENDPOINT_MISMATCH = "ALLOCATION_LEG_ENDPOINT_MISMATCH"`
2. `RISK_BUDGET_ENDPOINT_MISMATCH = "RISK_BUDGET_ENDPOINT_MISMATCH"`
3. `CAPITAL_BUCKET_ENDPOINT_MISMATCH = "CAPITAL_BUCKET_ENDPOINT_MISMATCH"`
4. `POSITION_ENDPOINT_MISMATCH = "POSITION_ENDPOINT_MISMATCH"`
5. `PORTFOLIO_ENDPOINT_MISMATCH = "PORTFOLIO_ENDPOINT_MISMATCH"`
6. `APPLICABLE = "APPLICABLE"`

Every value is exactly its member name. The enum has no aliases, fields,
defaults, custom constructor, custom methods, properties, labels,
descriptions, metadata, severity, ranking, Boolean semantics, custom equality,
custom hashing, ordering, or persistent identity.

Mismatch statuses are valid classification results, not malformed-input
exceptions. There is no generic `NOT_APPLICABLE`, `MISSING_INPUT`,
`INVALID_INPUT`, `UNKNOWN`, `ERROR`, combined-mismatch, constraint, breach, or
severity status.

## 9. Validation order

Before any comparison, the future classifier invokes these accepted validators
exactly once each, with the exact supplied object, in declared input order:

1. `validate_explicit_portfolio_allocation_leg_risk_budget_link(risk_budget_link)`;
2. `validate_explicit_portfolio_allocation_leg(leg)`;
3. `validate_explicit_portfolio_risk_budget(risk_budget)`;
4. `validate_explicit_portfolio_capital_bucket(capital_bucket)`; and
5. `validate_explicit_portfolio_position(position)`.

Validation uses only accepted upstream validators. M53 performs no local
duplication of upstream model, exact-type, field-type, blank-string, retained
model, Membership, or field-order validation.

All five validations complete before any comparison. The first upstream
failure stops processing; later validators and every comparison are skipped.
Each upstream input is validated exactly once, never zero or multiple times.

## 10. Comparison order

After all validation succeeds, exact stored string equality is evaluated
exactly in this order:

1. Compare M50 link `allocation_leg_id` against Allocation Leg
   `allocation_leg_id`. If unequal, return
   `ALLOCATION_LEG_ENDPOINT_MISMATCH`.
2. Compare M50 link `risk_budget_id` against Risk Budget `risk_budget_id`. If
   unequal, return `RISK_BUDGET_ENDPOINT_MISMATCH`.
3. Compare Risk Budget `capital_bucket_id` against Capital Bucket
   `capital_bucket_id`. If unequal, return
   `CAPITAL_BUCKET_ENDPOINT_MISMATCH`.
4. Compare Allocation Leg retained Link `position_id` through
   `leg.link.position_id` against Position `position_id`. If unequal, return
   `POSITION_ENDPOINT_MISMATCH`.
5. Compare Capital Bucket `portfolio_id` against Position retained Membership
   `portfolio_id` through `position.membership.portfolio_id`. If unequal,
   return `PORTFOLIO_ENDPOINT_MISMATCH`.
6. Otherwise return `APPLICABLE`.

This is the complete comparison set and order. No comparison is inserted,
removed, reordered, combined, or inferred.

## 11. Exact equality semantics

Every comparison uses exact stored string equality only. String value equality
determines alignment; string object identity is preserved but is not the
comparison rule.

M53 performs no trimming, case folding, Unicode normalization, aliasing,
canonicalization, transformation, coercion, conversion, copying,
reconstruction, derivation, hashing, generation, lookup, resolution,
inference, or automatic endpoint discovery. It performs no traversal outside
the exact supplied retained models. Surrounding whitespace, case, composed or
decomposed Unicode form, code points, and every other stored difference remain
significant under exact string equality.

No supplied model, retained model, or field object is mutated, replaced, or
reconstructed.

## 12. First-mismatch precedence

The first unequal comparison in Section 10 wins. Once a mismatch is found,
later fields are not compared and later mismatches are neither observed nor
combined. Complete alignment alone returns `APPLICABLE`.

Precedence is therefore, in order:

1. Allocation Leg endpoint mismatch;
2. Risk Budget endpoint mismatch;
3. Capital Bucket endpoint mismatch;
4. Position endpoint mismatch;
5. Portfolio endpoint mismatch; and
6. `APPLICABLE`.

## 13. APPLICABLE semantics

`APPLICABLE` means only that, for this exact supplied validated set:

- the M50 link names the supplied Allocation Leg;
- the M50 link names the supplied Risk Budget;
- the supplied Risk Budget names the supplied Capital Bucket;
- the Allocation Leg's retained Link names the supplied Position; and
- the supplied Capital Bucket and Position Membership carry equal Portfolio
  identities.

It means only endpoint identity and Portfolio alignment for the supplied set.
It does not mean endpoint existence outside the supplied objects, M49
presence, M45 applicability, M51 consistency, M52 applicability, uniqueness,
completeness, funding availability or sufficiency, risk capacity or risk-limit
acceptance, constraint satisfaction, authorization, approval, or execution
eligibility.

## 14. Domain invariants

1. One classification consumes exactly one explicitly supplied complete set.
2. All five required inputs are accepted upstream models.
3. Absence has no representation within M53.
4. Each upstream validator is invoked exactly once in declared input order.
5. The first upstream exception propagates unchanged.
6. All validation completes before any comparison.
7. Comparison uses exact stored string equality only.
8. The first mismatch wins in the order frozen in Section 10.
9. Classification is deterministic, pure, and stateless for the same supplied
   validated fields.
10. The result is one existing enum singleton and no applicability record.
11. M50 multiplicity, optionality, shared-endpoint behavior, and duplicate
    acceptance remain unchanged.
12. M53 owns no collection, uniqueness, coverage, aggregation, or selection
    rule.
13. M53 is independent of M49, M51, and M52.

## 15. Dependency direction

Dependencies flow only from M53 applicability to its five accepted upstream
model and validator packages. No upstream package imports M53. The future M53
status model depends only on Python standard-library `enum`.

This direction is compile-time domain layering, not runtime lookup. M53 does
not cause an endpoint, association, Membership, or Portfolio to enumerate or
own downstream classifications.

## 16. Multiplicity and collection boundary

M53 evaluates one caller-selected set per invocation. It does not search,
scan, enumerate, rank, aggregate, or select among links, Legs, Risk Budgets,
Capital Buckets, Positions, Memberships, or classifier results.

M50 remains optional at its structural boundary. Its many-at-either-endpoint
behavior, shared endpoints, and independently supplied exact duplicate
acceptance remain unchanged. M53 does not reject duplicates; enforce global,
per-endpoint, or pair uniqueness; require one link per Leg or Risk Budget;
impose coverage; create collection ownership or a reverse index; or perform
automatic record selection. Any valid caller-selected M50 record may
participate independently in a complete M53 comparison set.

## 17. Exception propagation

M53 defines no local validation exception type or message. Malformed inputs
remain the responsibility of the accepted upstream validators in Section 9.

The first upstream exception propagates unchanged. M53 does not catch, wrap,
translate, replace, suppress, aggregate, annotate, chain, or reconstruct it.
Its object identity, type, message, and traceback remain unchanged. Unexpected
Python exceptions are also not caught.

For structurally valid inputs, an identity mismatch is not exceptional. It
returns the corresponding ordered mismatch status.

## 18. Explicit non-responsibilities

M53 does not own or perform:

- production, mutation, repair, normalization, replacement, persistence, or
  existence proof of M50 links, Allocation Legs, Risk Budgets, Capital
  Buckets, Positions, Memberships, or any other endpoint;
- endpoint lookup, registry access, repository access, resolution, traversal,
  mapping, authoritative issuance, or automatic entity resolution;
- M49 presence or prerequisite enforcement, M51 reclassification, M52
  reclassification, or consumption or inference of either result;
- M45 Proposal/Position/Recommendation/Snapshot chain reclassification;
- M48 quantity or unit interpretation, trade sizing, target holding, delta,
  weight, denominator, or rebalance calculation;
- association or applicability identity, applicability records, nullable or
  sentinel absence, collection ownership, reverse indexes, uniqueness,
  duplicate detection or rejection, deduplication, coverage, completeness,
  scanning, aggregation, ordering, ranking, precedence beyond first mismatch,
  or automatic record selection;
- funding amount, available or committed capital, balance, cash, reservation,
  capacity, currency, price, valuation, FX, NAV, capital movement, routing, or
  funding-source selection;
- risk amount, risk limit, threshold, tolerance, utilization, remaining
  capacity, concentration, ratio, percentage, risk policy, breach, severity,
  or remediation;
- constraint taxonomy, definition, registration, policy, applicability,
  evaluation, satisfaction, prioritization, enforcement, breach, severity,
  remediation, or exception workflow;
- Recommendation actions or directions including BUY, HOLD, SELL, ADD,
  REDUCE, or WAIT, or opening, closing, long, short, and execution meaning;
- semantic production, inference, confidence, priority, urgency, materiality,
  suitability, approval, rejection, override, explainability, audit,
  execution, lifecycle, or operational decision behavior; or
- migration, schema, repositories, registries, resolvers, services, external
  APIs, runtime, orchestration, workflow, CLI, automation, scheduling,
  monitoring, hidden state, or third-party dependencies.

## 19. Relationship to M49–M52

- **M49:** M49 is not an input or prerequisite enforced by M53. The supplied
  Capital Bucket is the accepted Risk Budget parent needed for Portfolio
  alignment, not an M49 association record.
- **M50:** M53 consumes one exact supplied M50 link and its validator without
  modifying the link's fields, optionality, many-at-either-endpoint
  multiplicity, shared-endpoint behavior, duplicate acceptance, or structural
  non-responsibilities.
- **M51:** M51 remains the separate M49/M50/Risk Budget
  association-consistency classifier. M53 does not consume or infer an M51
  result and does not replace or reclassify M51.
- **M52:** M52 remains the separate Capital Bucket path applicability
  classifier. M53 does not consume or infer an M52 result and does not replace
  or reclassify M52.

M53 completes only the Risk Budget path applicability gap deferred by M52. It
does not complete broader constraint, funding, risk, approval, audit, or
operational architecture.

## 20. Future implementation boundary

The future complete public API is limited to:

- `PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus`; and
- `classify_portfolio_allocation_leg_risk_budget_link_applicability()`.

The future classifier signature is exactly:

`classify_portfolio_allocation_leg_risk_budget_link_applicability(risk_budget_link: ExplicitPortfolioAllocationLegRiskBudgetLink, leg: ExplicitPortfolioAllocationLeg, risk_budget: ExplicitPortfolioRiskBudget, capital_bucket: ExplicitPortfolioCapitalBucket, position: ExplicitPortfolioPosition) -> PortfolioAllocationLegRiskBudgetLinkApplicabilityStatus`

All five parameters are required positional-or-keyword parameters in the
declared order. There are no defaults, keyword-only markers, optional
parameters, or variadics.

After separate implementation authorization, implementation is bounded to one
new package with exactly:

```text
PortfolioAllocationLegRiskBudgetLinkApplicability/
├── README.md
├── models.py
├── classification.py
└── tests/
    ├── __init__.py
    └── test_applicability.py
```

`models.py` will contain exactly the one public status enum.
`classification.py` will contain exactly the one public classifier and no
private helper. No package-root `__init__.py`, `validation.py`, additional
public API, result model, unchecked classifier, policy, constraint,
calculation, persistence adapter, repository, registry, resolver, service,
API, runtime, CLI, configuration, fixture, shared utility, collection, or
third-party dependency belongs to the future boundary.

This document does not authorize or introduce that implementation, package,
test, or README.

## 21. Acceptance criteria

M53 architecture is accepted only when:

1. this document alone freezes the milestone status, approved domain,
   responsibility, ownership, complete comparison set, upstream dependencies,
   status taxonomy, validation order, exact comparison order, mismatch
   precedence, applicability semantics, invariants, dependency direction,
   multiplicity, non-responsibilities, exception propagation, milestone
   relationships, future implementation boundary, and deferred work;
2. all five inputs are required and absence remains outside invocation;
3. each accepted upstream validator is called exactly once in declared input
   order, with unchanged first-exception propagation and no duplicated local
   validation;
4. the comparison order is exactly the six outcomes frozen in Section 10,
   using exact stored string equality, no normalization, lookup, resolution,
   or inference, and first mismatch wins;
5. `APPLICABLE` has only the narrow supplied-set endpoint identity and
   Portfolio alignment meaning;
6. M50 multiplicity, optionality, shared endpoints, and duplicate acceptance
   remain unchanged; M53 remains independent of M49, M51, and M52; and no
   collection, uniqueness, coverage, or prerequisite rule is added;
7. no implementation, package, test, README, runtime behavior, orchestration,
   repository, registry, resolver, service, API, persistence, collection,
   amount, capacity, risk-limit, constraint, approval, explainability, audit,
   or operational artifact or responsibility is introduced;
8. exactly this one architecture document is untracked, no tracked file is
   modified, nothing is staged, and no implementation artifact exists; and
9. whitespace and final-newline verification pass.

## 22. Deferred work

Deferred responsibilities include all implementation and tests for M53;
allocation constraint taxonomy, definition, policy, applicability, and
evaluation; capital amount and capacity semantics; risk limits and
utilization; collection ownership and uniqueness; M49 prerequisite
enforcement; funding or trade calculation; explainability; human approval and
override; audit; persistence; runtime; orchestration; services and APIs;
execution; and Stage 6 automation.

No deferred responsibility is implied, designed, or authorized by this
document. Each requires its own later accepted architecture and authorization.
