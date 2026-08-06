# ADR-0003: Portfolio Allocation Constraint Plane Ownership, Subject, and Sequencing

- Status: Proposed
- Date: 2026-08-06
- Stage: 5
- Milestone: M54
- Decision scope: Portfolio Allocation constraint-plane ownership, initial
  subject, and sequencing
- Predecessor milestones: M48–M53

## Context

M48 establishes proposed absolute quantity for one Portfolio Allocation Leg.
M49 and M50 establish separate optional Leg-to-Capital-Bucket and
Leg-to-Risk-Budget foreign-ID associations. M51 classifies consistency among
one supplied M49 link, M50 link, and Risk Budget endpoint. M52 and M53
separately classify the complete Capital Bucket and Risk Budget paths for
caller-supplied sets.

These accepted boundaries establish the structural identities and path
applicability needed to begin deciding Portfolio Allocation constraint
architecture. They deliberately do not define a constraint, capacity, risk
limit, utilization, evaluation, breach, or operational decision. The
Constitution requires explicit ownership and prohibits resolving architecture
ambiguity through implementation. The Architecture Patterns require an
explicit model before applicability or calculation.

The authoritative M54 decision review therefore concludes that constraint
architecture may open, while no field-level constraint implementation is yet
safe. This ADR freezes only the minimum decisions required to prevent a later
constraint candidate from inventing its owner, initial subject, empty shell,
generic taxonomy, dependency direction, or sequencing.

## Decision

Portfolio Allocation constraints will be standalone explicit domain records.
The initial constraint plane will address exactly one
`ExplicitPortfolioAllocationLeg` subject per concrete record or accepted
subject association. It will not expand accepted endpoint shells or
association links.

This ADR accepts no general constraint taxonomy and selects no first concrete
constraint kind. The next concrete candidate must define exactly one narrowly
named kind with explicit, non-empty, reviewable responsibility and exact
minimum semantics, or remain blocked pending a separate product-policy
decision. No production package, class, validator, field set, enum, formula,
or implementation is authorized here.

## Constraint-plane readiness

M49–M53 satisfy the structural prerequisites fixed by ADR-0002 for opening
constraint architecture decision work. No additional non-constraint
structural prerequisite is required before this ADR. Capital capacity
content, Risk Budget limit content, shared unit or currency domains, and other
quantity kinds are not accepted mandatory predecessors to making this
ownership and sequencing decision.

Readiness to make architecture decisions does not authorize a concrete
constraint model or implementation. M51–M53 are applicability boundaries,
not general constraint definitions, and their existence does not supply the
missing product-policy semantics.

## Ownership

Portfolio Allocation constraints are new standalone explicit domain records.
They are not:

- fields added to `PortfolioCapitalBucket`;
- fields added to `PortfolioRiskBudget`;
- content owned by M48 proposed absolute quantity;
- responsibilities added to the M49 Capital Bucket link; or
- responsibilities added to the M50 Risk Budget link.

`PortfolioCapitalBucket` remains its accepted identity-only endpoint shell
with `capital_bucket_id` and `portfolio_id`. `PortfolioRiskBudget` remains its
accepted identity-only endpoint shell with `risk_budget_id` and
`capital_bucket_id`. Neither endpoint owns constraints or enumerates
downstream constraint records. M48, M49, and M50 retain their accepted narrow
content and association responsibilities.

## Initial subject

The first Portfolio Allocation constraint subject is exactly
`ExplicitPortfolioAllocationLeg`. Leg granularity follows ADR-0001's
occurrence-level measurable-content owner and ADR-0002's accepted resource
association attachment point.

The initial constraint plane rejects all of the following as its subject:

- Allocation Proposal;
- Portfolio Position;
- Portfolio;
- polymorphic subject identity;
- a generic subject-type enum; and
- a record spanning multiple subjects.

This decision does not prohibit future Proposal-, Position-, or
Portfolio-level constraints forever. They are outside the initial constraint
plane and require separate later architecture that owns their distinct
meaning, topology, and multiplicity.

## Empty-shell and taxonomy decision

A generic constraint model containing only `constraint_id` is prohibited. An
empty identity shell is not a sufficient domain responsibility. The first
concrete constraint record must own one explicit, non-empty, reviewable
responsibility in addition to any persistent opaque identity required by its
later accepted architecture.

No generic unresolved constraint-kind enum may be introduced merely to defer
meaning. This ADR accepts no general constraint taxonomy and authorizes no
open enum of capacity, risk, concentration, coverage, unit, or other kinds.
The first later concrete candidate must do exactly one of the following:

1. define one narrowly named constraint kind with exact semantics and the
   minimum fields necessary for that responsibility; or
2. remain blocked until a separate product-policy decision selects and
   defines that kind.

This ADR does not select the first kind.

## Quantitative-content decision

No capacity, amount, limit, threshold, utilization, or breach field is added
to `PortfolioCapitalBucket` or `PortfolioRiskBudget`. Accepted endpoint
models and public contracts remain unchanged.

Any later quantitative capital-capacity or risk-limit content must be owned
either by a separate accepted domain boundary or by a separately approved,
narrowly named constraint record. Selecting between those carriers is a later
product-policy decision. Whether resource-content packages must precede the
first concrete constraint model is also unresolved.

Unit, currency, denominator, sign, zero, exact `Decimal`, scale, comparison,
and compatibility semantics remain unresolved and must not be invented by
this ADR or an implementation. M48 `unit_id` remains opaque and local to the
proposed-absolute-quantity package. Identical spelling cannot establish a
shared namespace or compatibility rule.

## Sequencing

The safe Portfolio Allocation constraint sequence is:

1. this ADR;
2. one narrowly defined explicit constraint model with non-empty
   responsibility;
3. its validator;
4. a subject association shape, only if the model does not directly own the
   Allocation Leg foreign identity;
5. applicability;
6. quantitative resource content, if required by the selected constraint
   kind;
7. an evaluation or calculation result;
8. breach or satisfaction semantics;
9. explainability;
10. human approval and override;
11. audit; and
12. Stage 6 runtime and execution.

Applicability may not precede an accepted explicit model. Evaluation may not
precede the definition and all quantitative content required by the selected
kind. Breach or satisfaction semantics may not precede explicit evaluation
ownership. Explainability, approval, override, audit, runtime, and execution
may not precede the decision content they describe or govern.

This sequence is architectural responsibility ordering. It does not require
every numbered responsibility to share a package or assert that every
selected constraint kind needs quantitative resource content.

## Absence and multiplicity

Constraint absence, optionality, multiplicity, duplicate acceptance,
uniqueness-by-type, and collection ownership are not accepted by this ADR.
The M49 and M50 precedents of optional links, many records at either endpoint,
and independently accepted duplicates are informative structural precedents;
they do not automatically become constraint semantics.

No one-constraint-per-Leg rule and no many-constraints-per-Leg rule is
authorized. No global, per-Leg, per-kind, or composite uniqueness rule is
authorized. No collection, reverse collection, coverage, ordering,
aggregation, deduplication, or enforcement owner is authorized. The later
concrete constraint architecture must freeze its exact absence, optionality,
multiplicity, duplicate, uniqueness, and collection decisions before
implementation.

## Dependency boundary

A later first concrete constraint boundary may depend only on accepted domain
contracts explicitly named by its own frozen architecture. This ADR does not
automatically authorize dependencies on all of M48–M53, their results, or all
Portfolio endpoints. Each dependency must be necessary for the one selected
constraint responsibility and preserve downstream-to-upstream domain
layering.

No constraint boundary authorized by this sequence may perform hidden lookup,
registry access, repository access, resolution, persistence, runtime,
orchestration, service or API calls, automation, or financial calculation not
explicitly owned by a later accepted model. An opaque foreign identity is not
endpoint existence proof, and an applicability result is not constraint
satisfaction.

## Product-policy decisions still open

The following decisions remain unresolved and must not be inferred from this
ADR:

1. the first concrete constraint kind;
2. the numeric limit or capacity carrier;
3. whether resource-content packages precede the first concrete model;
4. whether and how M48 proposed absolute quantity participates, including
   unit compatibility;
5. constraint absence and optionality;
6. one-versus-many multiplicity per Leg;
7. duplicate acceptance, uniqueness-by-type, and collection policy;
8. prerequisite use of M49, M50, M51, M52, or M53;
9. evaluation result taxonomy;
10. breach, satisfaction, severity, and remediation semantics; and
11. later Proposal-, Position-, or Portfolio-level constraints.

These are product-policy decisions because accepted contracts do not select
their financial, decision, or cardinality meaning. Constitutionally, they
cannot be resolved inside implementation.

## Explicit non-responsibilities

This ADR does not define or authorize:

- an exact production package, class, validator, function, or public API
  name;
- exact fields or field order for the first concrete constraint;
- an exact enum or general taxonomy;
- formulas, operators, comparisons, limit values, tolerances, or thresholds;
- capacity calculation, risk utilization, funding sufficiency, reservation,
  allocation, or capital movement;
- currency, unit conversion, price, valuation, FX, NAV, weight, denominator,
  target, delta, or rebalance semantics;
- applicability status, evaluation result, breach, satisfaction, severity,
  remediation, or exception workflow;
- uniqueness, duplicate enforcement, collection, coverage, aggregation, or
  record selection;
- endpoint production, lookup, resolution, registry, repository, existence
  proof, persistence, schema, or migration;
- Recommendation action interpretation, including BUY, HOLD, SELL, ADD,
  REDUCE, or WAIT;
- semantic inference, ranking, suitability, or execution eligibility;
- runtime, orchestration, workflow, service, external API, CLI, automation,
  scheduling, monitoring, or execution;
- explainability schema, approval or override workflow, or audit schema; or
- any modification to M48–M53 or their accepted upstream endpoints.

## Consequences

The constraint plane now has an explicit owner category, one initial subject,
and a safe responsibility sequence. Later architecture cannot place
constraint fields on Capital Bucket or Risk Budget, attach the first
constraint at Proposal, Position, Portfolio, or polymorphic granularity, or
use an ID-only shell or unresolved kind enum to claim progress.

The cost is that no concrete constraint implementation follows automatically.
A product-policy decision must select one narrow kind and resolve its carrier,
fields, multiplicity, dependencies, and evaluation prerequisites. This delay
is intentional: it prevents structural applicability from being mistaken for
financial constraint satisfaction and preserves accepted endpoint contracts.

## Rejected alternatives

### Add constraint fields to Capital Bucket

Rejected because Capital Bucket is an accepted identity-only endpoint shell.
Capacity, amount, limit, utilization, and breach are separate responsibilities
and would change its public contract.

### Add risk-limit or constraint fields to Risk Budget

Rejected because Risk Budget owns only its identity and Capital Bucket foreign
identity. A risk-themed endpoint name does not authorize numerical limits,
policy, utilization, or breach semantics.

### Attach the initial constraint to Allocation Proposal

Rejected because accepted Allocation Proposals may contain multiple
independently measurable Legs. Proposal granularity would blur the
occurrence-level content and resource associations selected by ADR-0001 and
ADR-0002.

### Use Position or Portfolio as the initial subject

Rejected because those endpoints own structural portfolio context, not the
initial allocation-intent occurrence. Their future constraint meanings, if
any, require separate architecture.

### Use a polymorphic or multi-subject constraint

Rejected because it introduces unresolved subject topology and generic type
machinery before one exact initial responsibility exists.

### Introduce an ID-only generic constraint shell

Rejected because identity without a non-empty owned responsibility cannot
define, validate, classify, or evaluate a constraint.

### Introduce a generic constraint-kind enum now

Rejected because an open list of capacity, risk, concentration, coverage,
unit, or other labels would defer rather than define meaning, fields, units,
and evaluation prerequisites.

### Treat M51–M53 applicability as constraint evaluation

Rejected because those classifiers prove only ordered identity and Portfolio
alignment for supplied sets. They own no limit, capacity, policy,
satisfaction, breach, or execution meaning.

### Begin evaluation, explainability, approval, audit, or execution now

Rejected because no concrete constraint definition and required quantitative
decision content exists.

## Acceptance gate for later milestones

No M55 or later concrete Portfolio Allocation constraint implementation
architecture may be accepted until all of the following are true:

1. ADR-0003 is independently approved;
2. exactly one first constraint kind is selected;
3. that kind's minimum non-empty responsibility and exact semantics are
   explicit;
4. exact model identity, fields, field order, and ownership are frozen;
5. quantitative carrier requirements and their sequencing are resolved;
6. absence, optionality, multiplicity, duplicates, uniqueness, and collection
   ownership are resolved;
7. the dependency allowlist names every accepted upstream contract required
   and no others; and
8. applicability and evaluation prerequisites, inputs, and ownership are
   explicit.

Until every gate is satisfied, a concrete model, validator, applicability
classifier, evaluation, or implementation remains blocked. Approval of this
ADR alone does not satisfy the product-policy gates.

## Stage 5 continuation and closure implications

Stage 5 continues. M53 closes only the Risk Budget path-applicability gap and
does not close Stage 5. The next concrete implementation remains blocked until
this ADR and the required product-policy decisions are accepted.

Constraint definition and evaluation remain unfinished. Explainability,
human approval and override, and audit remain later Stage 5 responsibilities
after decision content exists. Runtime execution, workflow, monitoring,
persistence enforcement, and automation remain Stage 6 and are outside this
ADR.
