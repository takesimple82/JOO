# ADR-0002: Portfolio Allocation Leg Capital Bucket and Risk Budget Association Sequencing

- Status: Proposed
- Date: 2026-08-04
- Stage: 5
- Decision scope: First structural association responsibility after M48
- Predecessor milestones: M43–M45, M47, and M48

## Context

M43–M48 establish an accepted ownership chain from one Recommendation through
an Allocation Proposal and Proposal Position Link to an independently
identifiable Allocation Leg and its proposed absolute quantity. M48 completes
the first measurable Leg content but deliberately owns no Capital Bucket, Risk
Budget, funding, or constraint responsibility.

The next architecture question is which structural association, if any, must
follow that content. The decision must preserve the accepted chain, avoid
turning endpoint identity attachment into endpoint lookup, and avoid importing
funding or risk semantics into a structural record.

## Accepted baseline

- M43 owns an Allocation Proposal identity and its foreign Recommendation ID.
- M44 owns a foreign-ID-only Proposal-to-Position pair. It accepts many links
  at either endpoint and duplicate exact pairs.
- M45 classifies supplied Proposal/Position chain applicability without
  changing M43 or M44 multiplicity.
- M47 owns an Allocation Leg identity and retains one exact M44 Link. The Leg
  is the stable occurrence-level attachment point for measurable content and
  later optional funding or constraint associations.
- M48 owns only `allocation_leg_id`, `unit_id`, and `value`. It uses a
  foreign-ID-only Leg attachment and does not import, validate, look up, or
  prove the existence of a Leg.
- `PortfolioCapitalBucket` owns `capital_bucket_id` followed by `portfolio_id`.
  It owns no allocation content, amount, balance, constraint, utilization,
  execution, or Allocation Proposal identity.
- `PortfolioRiskBudget` owns `risk_budget_id` followed by
  `capital_bucket_id`. It owns no numerical limit, utilization, constraint,
  execution, Allocation Leg, or Allocation Proposal identity.
- ADR-0001 selects the Allocation Leg, rather than the Proposal or the M44
  Link, as the stable owner for measurable target occurrences and later
  optional funding or constraint associations.
- Accepted foreign-ID association precedents normally store the two endpoint
  IDs, add no association identity, accept independent duplicates, and own no
  collection, uniqueness, lookup, or existence proof. Retained objects are
  used only where an accepted object itself is the required structural
  substrate, as in M47.

## Problem

The repository must select the smallest structurally complete post-M48
responsibility and freeze its owner, endpoints, direction, shape,
multiplicity, optionality, sequence, dependencies, and boundaries. It must
also decide whether Capital Bucket and Risk Budget attachment are one or two
responsibilities and when constraint architecture may begin.

## Decision drivers

- Preserve Recommendation → Proposal → Proposal Position Link → Allocation
  Leg → Leg Proposed Absolute Quantity.
- Attach allocation-specific identities at the independently measurable Leg
  occurrence rather than at a potentially multi-Position Proposal.
- Introduce the nearest accepted upstream resource identity before an identity
  nested beneath it.
- Keep Capital Bucket identity attachment separate from funding calculation.
- Keep Risk Budget identity attachment separate from risk-limit semantics.
- Avoid identifier denormalization when identity is already reachable through
  an accepted retained structure.
- Keep single-record structural validation separate from cross-record policy.
- Avoid endpoint imports, runtime lookup, and existence claims.
- Prefer separate milestones where the endpoint dependencies and semantics are
  distinct.

## Alternatives considered

### A. Portfolio Allocation Leg to Capital Bucket association first

- Ownership clarity: Strong. The Leg is the accepted occurrence-level owner,
  and Capital Bucket is the nearest funding identity.
- Dependency direction: From a new downstream association to two accepted ID
  namespaces; neither endpoint changes.
- Denormalization risk: Low. Only the two endpoint IDs are stored; Proposal,
  Position, Portfolio, and Risk Budget IDs remain reachable elsewhere.
- Multiplicity implications: Many independent association records may share
  either endpoint; no collection policy is implied.
- Compatibility with M43–M48: Preserves the full chain and M44/M47 duplicate
  behavior.
- Compatibility with Capital Bucket and Risk Budget: Uses the Bucket's owned
  identity without changing it and prepares the explicit parent association
  needed before a separate Risk Budget attachment.
- Operational responsibility risk: Low if funding amount, balance, capacity,
  and lookup remain excluded.
- Verdict: Selected as the first milestone within Alternative E.

### B. Portfolio Allocation Leg to Risk Budget association first

- Ownership clarity: Leg-level ownership is correct, but it skips the Risk
  Budget's accepted Capital Bucket parent association at the Leg boundary.
- Dependency direction: Structurally possible as two IDs, but recovering the
  Bucket from the Budget would require a supplied endpoint or lookup later.
- Denormalization risk: Adding `capital_bucket_id` to compensate would
  denormalize the Risk Budget endpoint; omitting it leaves the funding identity
  unattached.
- Multiplicity implications: Many-to-many structural acceptance remains
  possible but does not resolve the missing parent association.
- Compatibility with M43–M48: Leg attachment is compatible.
- Compatibility with Capital Bucket and Risk Budget: Reverses the accepted
  Bucket-before-Budget dependency.
- Operational responsibility risk: Encourages premature risk-limit or
  constraint interpretation.
- Verdict: Rejected as the first responsibility.

### C. Portfolio Allocation Proposal to Capital Bucket association first

- Ownership clarity: Weak for a Proposal with multiple independently
  measurable Legs.
- Dependency direction: Does not violate endpoint layering, but bypasses the
  accepted occurrence-level content owner.
- Denormalization risk: Legs would inherit or recover Bucket identity through
  their Proposal, requiring traversal or lookup and preventing distinct Leg
  associations.
- Multiplicity implications: Silently applies one Proposal-level relation to
  all Legs or requires unresolved Proposal-level multiplicity policy.
- Compatibility with M43–M48: Conflicts with ADR-0001's Leg attachment point
  and M44's multi-Position topology.
- Compatibility with Capital Bucket and Risk Budget: Uses a valid Bucket ID at
  the wrong allocation granularity.
- Operational responsibility risk: Encourages proposal-wide funding inference.
- Verdict: Rejected.

### D. Portfolio Allocation Proposal to Risk Budget association first

- Ownership clarity: Combines the wrong allocation granularity with a skipped
  Bucket association.
- Dependency direction: Bypasses both the Leg owner and the Budget's Bucket
  parent at the allocation boundary.
- Denormalization risk: High when later Legs need distinct Bucket/Budget
  identity or consistency checks.
- Multiplicity implications: Ambiguous across multiple Legs and Positions.
- Compatibility with M43–M48: Conflicts with M44 multiplicity and ADR-0001.
- Compatibility with Capital Bucket and Risk Budget: Fails to make the parent
  Bucket attachment explicit first.
- Operational responsibility risk: High; invites proposal-wide risk policy.
- Verdict: Rejected.

### E. Ordered separate Capital Bucket and Risk Budget association milestones

- Ownership clarity: Strong. Each relation owns one distinct endpoint identity
  attachment at Leg granularity.
- Dependency direction: Leg-to-Bucket first, then Leg-to-Risk-Budget; accepted
  endpoints remain upstream and independent.
- Denormalization risk: Low. Each record has only its two endpoint IDs.
- Multiplicity implications: Each single-record boundary can accept duplicates
  and shared endpoints without inventing collection policy.
- Compatibility with M43–M48: Fully preserves the chain and Leg ownership.
- Compatibility with Capital Bucket and Risk Budget: Mirrors the accepted Risk
  Budget → Capital Bucket nesting while keeping the two relations distinct.
- Operational responsibility risk: Low because no numerical or evaluative
  semantics are needed.
- Verdict: Selected. Its first responsibility is Alternative A.

### F. A combined Capital Bucket and Risk Budget association milestone

- Ownership clarity: Weakens one-relation-per-owner separation by coupling two
  independently optional endpoint attachments.
- Dependency direction: A three-ID record would entangle Leg, Bucket, and
  Budget and require cross-endpoint consistency semantics.
- Denormalization risk: High because `capital_bucket_id` is already reachable
  from a supplied Risk Budget endpoint.
- Multiplicity implications: Forces paired cardinality and optionality before
  either has been independently accepted.
- Compatibility with M43–M48: Leg granularity is compatible, combined shape is
  not required by the chain.
- Compatibility with Capital Bucket and Risk Budget: Blurs their separate
  accepted identities and responsibilities.
- Operational responsibility risk: Encourages lookup, consistency evaluation,
  funding, and risk-policy scope.
- Verdict: Rejected.

### G. Skip the optional association layer and open constraint architecture

- Ownership clarity: Constraints would lack explicit accepted identities for
  the resources they are expected eventually to reference.
- Dependency direction: Would force constraint design to invent, embed, or
  infer association topology.
- Denormalization risk: High in future constraint records.
- Multiplicity implications: Constraint design would prematurely decide
  Bucket/Budget association cardinality.
- Compatibility with M43–M48: M48 content exists, but ADR-0001 sequences
  optional associations before constraints.
- Compatibility with Capital Bucket and Risk Budget: Leaves both accepted
  endpoint namespaces structurally disconnected from allocation content.
- Operational responsibility risk: Highest; invites limits, thresholds, and
  utilization before structural prerequisites are fixed.
- Verdict: Rejected.

## Decision

Select **Alternative E: ordered separate Capital Bucket and Risk Budget
association milestones**. The exact first structural responsibility after M48
is **one directed, Leg-level, foreign-ID-only association from a Portfolio
Allocation Leg identity to a Portfolio Capital Bucket identity**. This first
responsibility is Alternative A.

After that association is accepted and implemented, a separate architecture
milestone may freeze a directed Leg-to-Risk-Budget foreign-ID association.
The two associations must not be combined.

## Exact architecture contract

1. Selected alternative: E, with A first.
2. Next responsibility: record one explicit Leg-to-Capital-Bucket identity
   association and nothing else.
3. Association owner: a new standalone association boundary, not the Leg,
   M48 content, Capital Bucket, Risk Budget, Proposal, or an endpoint package.
4. Left endpoint: Portfolio Allocation Leg identity.
5. Right endpoint: Portfolio Capital Bucket identity.
6. Direction: Allocation Leg → Capital Bucket.
7. Granularity: Leg-level, never Proposal-level.
8. Representation: foreign IDs only; no retained Leg or Bucket object.
9. Architecture fields, in order: `allocation_leg_id: str`, then
   `capital_bucket_id: str`.
10. Association identity: none; no link ID or generated/composite identity.
11. Cardinality policy: architecture permits many independent relations at
    either endpoint. One Leg may be associated with multiple Buckets and one
    Bucket with multiple Legs. No exclusive or one-to-one policy is frozen.
12. Duplicate acceptance: exact duplicate records are structurally accepted
    when independently supplied.
13. Uniqueness: not owned, either globally, per Leg, per Bucket, or per pair.
14. Collection: not owned.
15. Ordering: not owned.
16. Instance-level optionality: the association is optional for each Leg.
    Absence is not represented by `None`, a blank ID, or a sentinel; it is the
    absence of an association record.
17. Required coverage: not every Leg or Proposal requires an association.
18. Bucket and Budget associations: separate milestones and separate records.
19. Exact sequence: Leg→Capital Bucket association first; Leg→Risk Budget
    association second; constraint architecture only after both structural
    association packages have been accepted and implemented.
20. Risk Budget prerequisite: at architecture policy level, a Leg-to-Risk-
    Budget association requires that Leg to have a separate Leg-to-Capital-
    Bucket association. The later Risk Budget association's single-record
    structural validator must not prove or enforce that cross-record policy.
    Consistency between the associated Bucket and the Risk Budget's
    `capital_bucket_id` is a later applicability or constraint prerequisite,
    not part of either association's structural validation.
21. Constraint sequencing: constraints may not begin before both separate
    association packages exist. Their existence does not require every Leg to
    carry either optional association.
22. Dependency direction: each new association depends conceptually on
    accepted endpoint identity namespaces; no accepted endpoint depends on the
    association. This is compile-time/domain layering, not runtime lookup.
23. Allowed upstream contracts for the first association architecture are the
    accepted Portfolio Allocation Leg and Portfolio Capital Bucket identity
    contracts. The later frozen implementation document must decide its exact
    import boundary without changing the foreign-ID-only decision.
24. Denormalization prohibitions: the first association must not add
    `allocation_proposal_id`, `position_id`, `recommendation_id`,
    `portfolio_id`, `risk_budget_id`, `unit_id`, or quantity value. The later
    Risk Budget association must contain only `allocation_leg_id` then
    `risk_budget_id`; it must not duplicate `capital_bucket_id` or any other
    reachable identifier.
25. Endpoint boundary: structural validation checks only the association
    record and its exact foreign-ID fields. It performs no endpoint lookup,
    endpoint validation, existence proof, resolution, registry access, or
    Portfolio/Bucket alignment proof.
26. Non-responsibilities are frozen in the dedicated section below.
27. Next architecture consequence: independent review and acceptance of this
    ADR enables a frozen M49 architecture document for only the Leg-to-Capital-
    Bucket association.
28. Alternatives B, C, D, F, and G are rejected for the reasons above; A is
    selected only as the first step of the ordered E decision.

## Multiplicity and optionality

Architecture policy and single-record structural validation are distinct. The
first association boundary accepts a valid pair without consulting any other
record. It therefore accepts equal duplicates, repeated Leg IDs, and repeated
Bucket IDs. It cannot prove uniqueness, exclusivity, coverage, or the presence
of the later Risk Budget association.

Instance-level optionality means a particular accepted Leg may have zero or
more supplied Bucket association records. It does not mean the future M49
package is optional once its milestone is approved, and it does not permit
nullable or blank endpoint fields. Proposal-level association is neither
required nor inferred from its Legs.

The later Risk Budget relation is independently optional per Leg, subject to
the architecture policy that any Leg using it also has a separate Bucket
association. Enforcing that policy requires a later collection, applicability,
or constraint contract; neither single-record association owns enforcement.

## Dependency boundary

The association points from downstream allocation intent to an accepted
resource identity. It does not reverse ownership: a Capital Bucket does not
own or enumerate Legs, and a Risk Budget does not own or enumerate Legs.
Neither accepted endpoint package imports a new association package.

Foreign-ID attachment is not endpoint existence proof. The first association
does not require a Leg or Bucket object, does not invoke their validators, and
does not prove that either ID was issued, is unique, belongs to a Portfolio,
or is suitable. Likewise, the later Risk Budget relation must not retrieve a
Risk Budget to discover its Bucket. Runtime lookup, repositories, registries,
resolvers, and orchestration remain outside this domain boundary.

## Identity and denormalization

The association owns a relation, not a new persistent entity identity. Its two
foreign identifiers remain canonical only in their endpoint namespaces. Pair
equality is structural and does not create a composite canonical ID.

Proposal and Position identities are already reachable through the accepted
Leg's retained Link. Recommendation, Snapshot, and Portfolio identities are
reachable through accepted upstream structures. The first association does
not duplicate them. A Risk Budget's Capital Bucket identity is reachable from
the accepted Risk Budget endpoint; the later Risk Budget association therefore
does not duplicate it. Reachability does not authorize hidden traversal or
lookup during structural validation.

## Non-responsibilities

This ADR and the associations it sequences do not own or perform:

- production, validation, lookup, resolution, or existence proof of any Leg,
  Proposal, Link, Position, Recommendation, Portfolio, Snapshot, Capital
  Bucket, or Risk Budget endpoint;
- association identity, automatic ID generation, composite identity, endpoint
  or pair uniqueness, deduplication, collections, ordering, aggregation, or
  completeness;
- Portfolio alignment, Bucket-to-Portfolio applicability, Leg-to-Proposal
  applicability, or Bucket/Risk-Budget consistency evaluation;
- funding amounts, available capital, committed capital, cash, balances,
  capacity, currency, price, valuation, NAV, capital movement, or routing;
- risk amounts, limits, tolerances, thresholds, utilization, remaining
  capacity, ratios, percentages, concentration, or breach detection;
- quantity calculation, unit conversion, target holdings, deltas, weights,
  rebalance calculation, or reinterpretation of M48 content;
- constraint taxonomy, definition, policy, applicability, evaluation,
  satisfaction, prioritization, or enforcement;
- Recommendation actions or directions, including BUY, HOLD, SELL, ADD,
  REDUCE, or WAIT;
- semantic production, inference, ranking, confidence, priority, materiality,
  suitability, approval, rejection, override, explainability, audit, execution,
  or lifecycle;
- persistence, migrations, repositories, registries, resolvers, runtime,
  orchestration, workflow, CLI, automation, scheduling, monitoring, external
  APIs, or third-party dependencies.

## Compatibility

- **M43:** No Proposal field or Recommendation association changes.
- **M44:** Many-position and duplicate-pair behavior remains unchanged; the
  new relation does not attach at the Proposal Position Link.
- **M45:** Applicability classification and its ordered comparisons remain
  unchanged; no Bucket/Budget comparison is added.
- **M47:** The Allocation Leg remains the occurrence-level owner and stable
  attachment point. Its retained Link and public contract do not change.
- **M48:** Proposed quantity fields, foreign-ID-only Leg attachment,
  multiplicity, and non-responsibilities remain unchanged.
- **PortfolioCapitalBucket:** Its `capital_bucket_id` is referenced without
  importing allocation content or adding a reverse collection. Its
  `portfolio_id` is not duplicated.
- **PortfolioRiskBudget:** Its `risk_budget_id` is reserved for the second
  separate association. Its `capital_bucket_id` is not duplicated there.
- **ADR-0001:** Implements its sequence of optional Leg funding/risk
  associations before constraints and preserves its Leg-level attachment
  decision.
- **Constitution:** Keeps identity, structure, applicability, evaluation, and
  operation separate; adds the minimum responsibility and no hidden lookup.
- **Architecture Patterns:** Uses a frozen structural association boundary and
  preserves downstream-to-upstream dependency direction without changing
  accepted endpoints.
- **Stage 5 roadmap:** Advances Recommendation and Allocation Proposal toward
  later Constraint Evaluation while leaving approval, explainability, audit,
  execution, persistence, and runtime to their planned boundaries.

## Consequences

The first post-M48 association is unambiguous and independently reviewable.
Capital Bucket and Risk Budget identity attachments can evolve without a
three-way record, Proposal-level ambiguity, or operational semantics. The
cost is two explicit records for a Leg that uses a Risk Budget and a deferred
cross-record consistency check. That duplication is relational structure, not
denormalization: each record states a different association, while neither
duplicates an identifier reachable inside its own right endpoint.

Because no collection exists, architecture cardinality and prerequisite
policies are not enforced by either structural validator. A later accepted
boundary must own any needed Bucket/Budget consistency and constraint
applicability without changing the associations' structural acceptance.

## Rejected alternatives

B is rejected because it skips the explicit parent Bucket relation. C and D
are rejected because Proposal granularity conflicts with independently
measurable Legs and multi-Position Proposals. F is rejected because it couples
distinct optional relations and denormalizes the Budget's Bucket identity. G
is rejected because constraint design would otherwise have to invent or infer
the missing identity topology. A is not a complete sequence by itself; it is
accepted as the exact first milestone under E.

## Follow-up milestone boundary

The next step is **a frozen M49 architecture document** for only the directed
Portfolio Allocation Leg to Portfolio Capital Bucket association specified
here. It is not another topology ADR and is not direct implementation
readiness. This ADR remains Proposed until independent review and explicit
acceptance. No M49 production code or tests may begin from this Proposed ADR.

The subsequent order is: accept and implement the frozen M49 Leg-to-Capital-
Bucket contract; freeze, accept, and implement a separate Leg-to-Risk-Budget
association milestone; then open constraint architecture. Exact package names,
public class and validator names, exception messages, complete validation
order, README wording, tests, and implementation file boundaries are deferred
to their respective frozen architecture documents.
