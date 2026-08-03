# ADR-0001: Portfolio Allocation Proposal Content Ownership and Semantics

- Status: Proposed
- Stage: 5
- Milestone: M46

## Context

The accepted Portfolio Allocation Proposal chain establishes identity,
association, and applicability, but it deliberately owns no measurable
allocation content. Before such content can be implemented, JOO must identify
an unambiguous content owner and freeze the first measurable meaning without
silently narrowing accepted multiplicity or inventing valuation state.

The accepted baseline is:

- M43 `ExplicitPortfolioAllocationProposalEndpoint` owns only
  `allocation_proposal_id` and its one `recommendation_id` association.
- M44 `ExplicitPortfolioAllocationProposalPositionLink` owns only the
  `allocation_proposal_id`/`position_id` structural pair. Many links may share
  either endpoint, exact duplicate pairs are structurally accepted, and the
  package owns no collection, uniqueness, ordering, or single-target policy.
- M45 classifies the supplied Link, Proposal, Recommendation, Snapshot, and
  Position chain in its frozen comparison order. It owns structural endpoint
  matching and Position-to-Snapshot Portfolio alignment only.

`ExplicitPortfolioHoldingObservation.quantity` is an observed-state precedent
only. It is not proposed state and must not own or be reused as proposed
allocation content. A Portfolio Snapshot may also be partial and contains no
accepted Portfolio NAV, market value, or allocation denominator.

## Decision

### Content owner and multiplicity

JOO will introduce a separate **Portfolio Allocation Leg** identity as the
primary owner of independently measurable Allocation Proposal content.

One Allocation Proposal may own many Allocation Legs and may continue to
target multiple Portfolio Positions. This preserves M44. No single-target
policy is introduced. Each Leg identifies one distinct occurrence of an
Allocation-Proposal-to-Position target, so measurable content for a
multi-Position Proposal is attached independently to the corresponding Leg.

At architecture level, a Portfolio Allocation Leg has exactly these
responsibilities:

1. own one caller-supplied opaque `allocation_leg_id` canonical only within the
   Portfolio Allocation Leg namespace; and
2. retain one exact accepted
   `ExplicitPortfolioAllocationProposalPositionLink` as its structural
   Proposal/Position relation.

The first Leg milestone must therefore be capable of freezing the exact model
fields, in order, as:

1. `allocation_leg_id: str`
2. `link: ExplicitPortfolioAllocationProposalPositionLink`

The Leg does not duplicate `allocation_proposal_id`, `position_id`, Portfolio,
Snapshot, Recommendation, Capital Bucket, or Risk Budget identifiers. One
Proposal may own many Legs. Multiple Legs may retain structurally equal Links,
including the duplicate exact Proposal/Position pairs accepted by M44. The Leg
boundary owns no collection, ordering, uniqueness, or endpoint existence
proof.

The Leg is not an empty identity shell. Its identity distinguishes target
occurrences that M44 intentionally permits to have the same structural pair,
and it is the stable owner for exactly one measurable content record and for
later optional constraint or funding associations. Its existence does not by
itself assert that content has already been supplied.

### First measurable content

The first measurable content kind is **proposed absolute quantity**. Here,
“absolute” means a caller-supplied, base-independent proposed quantity for one
Allocation Leg. It does not mean mathematical absolute value and does not
force a non-negative sign.

This value is not:

- an observed holding quantity;
- a target post-proposal holding quantity;
- a delta from a current holding;
- a monetary amount; or
- a portfolio weight or weight delta.

It is intentionally independent of whether the supplied Snapshot contains a
Holding Observation for the Position. It therefore does not calculate from,
copy, update, or reinterpret
`ExplicitPortfolioHoldingObservation.quantity`. Observed state remains owned
by Portfolio Holding Observation; proposed state remains owned by the
Allocation Leg content boundary.

The later proposed-quantity model must be capable of freezing exactly these
fields, in order:

1. `allocation_leg_id: str`
2. `unit_id: str`
3. `value: Decimal`

The content references only its owning Leg identity. Proposal and Position
identifiers are reached through the Leg's accepted Link and are not
denormalized onto content.

### Numeric and sign semantics

`value` is an exact built-in `decimal.Decimal`, not a subclass, and must be
finite. The exact caller-supplied Decimal object and representation, including
exponent, trailing zeros, and signed zero, are preserved. Validation and
storage perform no float conversion, coercion, normalization, quantization,
rounding, arithmetic, or unit conversion.

Positive, zero, negative, positive-zero, and negative-zero values are all
structurally accepted. Zero remains an explicit proposed quantity rather than
absence of content. Negative values remain exact caller-supplied proposed
quantities. This boundary does not interpret a sign as BUY, SELL, ADD, REDUCE,
HOLD, WAIT, opening, closing, long, short, or any execution instruction. Sign
policy and action interpretation are deferred.

### Unit and currency

Proposed absolute quantity requires one opaque exact nonblank built-in
`unit_id: str`. The identifier is preserved exactly. No lookup, taxonomy,
aliasing, compatibility resolution, normalization, or conversion occurs.

This `unit_id` belongs to the Portfolio Allocation Leg proposed-quantity
boundary. It is not owned by Expected Value. Identical field naming does not
imply a shared namespace with `ExpectedValueAssumptionSet`,
`ExactCrossContextNumericDelta`, or any other package. A shared Unit domain is
not required for the first content milestone.

Currency architecture is deferred because monetary amount is not the selected
first content kind. No `currency_id`, Currency domain, FX lookup, conversion,
or normalization is introduced.

### Content cardinality, duplicates, and ordering

One Allocation Leg owns exactly one proposed-absolute-quantity content record.
Multiple measurable records for the same Leg are not part of this contract;
additional independently measurable intent requires another caller-identified
Leg, even when its Link is structurally equal. No content collection owner is
required.

Exact duplicate content records are structurally accepted when considered
independently; structural validation does not prove the Leg-level cardinality
policy or reject a second equal instance. Distinct Legs may also carry equal
`unit_id` and `value` fields. The package will not own a collection or enforce
global uniqueness, repository uniqueness, or cross-record deduplication.
Consequently it owns no ordering. Any future collection or persistence
boundary that enforces the one-record-per-Leg policy requires its own explicit
contract and must not silently change this domain multiplicity.

### Capital Bucket, Risk Budget, and constraints

Neither a Capital Bucket nor a Risk Budget association is required before the
Portfolio Allocation Leg or its proposed absolute quantity can be
implemented. Proposal/Leg-to-Capital-Bucket and Proposal/Leg-to-Risk-Budget
links are optional later structural milestones, allowed only after measurable
content is accepted. This ADR does not select their exact endpoint topology.
It defines no funding calculation, bucket amount, risk limit, utilization,
threshold, or allocation policy.

Constraint definition and constraint evaluation remain blocked until the
measurable allocation content package and its Leg owner are accepted. This ADR
does not design a constraint taxonomy.

### Weight basis

Target portfolio weight and weight delta are not implementation-ready. The
repository has no accepted owner for Portfolio NAV, Portfolio market value,
Capital Bucket amount, or another valid denominator. This ADR does not invent
such financial state. All weight-based content remains explicitly deferred
until a separate accepted architecture establishes an exact denominator and
its owner.

## Alternatives

### A. Proposal-owned content with single-target semantics — rejected

This would make content attachment simple and give it the Proposal's canonical
identity, but it conflicts with M44's accepted many-Position multiplicity
unless a future milestone explicitly amends M44. Under current multi-Position
Proposals, Proposal-owned quantities are ambiguous about which Position they
measure. Supporting many records would require repeated Position references
and denormalize the existing Link; supporting one record would silently impose
a single target. Constraint, Capital Bucket, and Risk Budget attachment would
inherit the same ambiguity. It avoids an empty-shell risk but only by placing
content on the wrong-granularity owner.

### B. Existing Proposal-to-Position Link as attachment key — rejected

This is compatible with M44's many-to-many topology and avoids duplicating
Proposal and Position identifiers. However, M44 deliberately gives the Link no
canonical identity and accepts duplicate exact pairs. A pair key therefore
cannot distinguish two independently measurable target occurrences. One
record per pair would introduce uniqueness that M44 does not own; many records
would need another identity or an ordered collection and would remain
ambiguous for later constraints. Attaching Capital Bucket or Risk Budget
associations to the pair would have the same collision. Adding content or an
identity to M44 would improperly expand an accepted structural package.

### C. Separate Allocation Leg identity — accepted

This preserves M44 multiplicity and duplicate behavior while supplying a
canonical identity for each measurable target occurrence. It supports many
Legs per Proposal, one content record per Leg, and equal Proposal/Position
pairs without ambiguity. It avoids identifier denormalization by retaining the
accepted Link object. It also provides a stable later attachment point for
constraints and optional Capital Bucket or Risk Budget links. Its principal
risk is becoming an empty identity shell; that risk is bounded by its exact
role as the occurrence identity and owner of one measurable content record,
with the structural Leg milestone immediately followed by that content
milestone.

## First-content alternatives

- **Proposed absolute quantity — accepted.** It is directly attributable to
  one Leg, requires only an exact Decimal and opaque unit, and does not depend
  on a complete observed holding or valuation denominator.
- **Target quantity — deferred.** It would assert desired post-proposal
  Portfolio state and needs a separately accepted target-state meaning,
  replacement/completeness semantics, and relationship to partial Snapshots.
- **Quantity delta — deferred.** It requires an exact accepted baseline
  Holding Observation selection and applicability rule. M45 Portfolio
  alignment does not prove that such an observation exists or is current.
- **Monetary amount — deferred.** It requires currency ownership and may
  require price, valuation, cash, or FX architecture not accepted here.
- **Target portfolio weight — blocked.** It requires an accepted denominator
  and target-state semantics.
- **Weight delta — blocked.** It requires both an accepted denominator and an
  exact baseline-weight derivation or observation.

No inseparable pair is required. The ADR rejects a generic content-kind enum,
union, and polymorphic payload because one exact first semantic meaning is
sufficient and such abstractions would admit unresolved meanings.

## Consequences and sequencing

Acceptance freezes this architectural order:

1. implement the structural `PortfolioAllocationLeg` package;
2. implement one Leg-owned proposed-absolute-quantity content package;
3. optionally introduce separately accepted Leg/Proposal-to-Capital-Bucket or
   Risk-Budget associations;
4. define and evaluate allocation constraints;
5. add explainability;
6. add human approval or override;
7. add audit contracts; and
8. defer execution and runtime to Stage 6.

The exact next implementation milestone enabled by acceptance is the
**Explicit Portfolio Allocation Leg structural boundary**: one frozen,
hashable model with `allocation_leg_id` followed by the exact accepted
Proposal Position Link, validation-first exact-type and preservation
semantics, many Legs per Proposal, duplicate equal Links accepted, and no
content or operational responsibility. The immediately following measurable
milestone is the **Portfolio Allocation Leg Proposed Absolute Quantity**
boundary with the three fields and semantics frozen above.

## Non-responsibilities

This ADR implements no production package or future-package tests. It does not
modify M43, M44, M45, or any accepted domain package. It does not own or
perform:

- endpoint lookup or existence proof, repositories, registries, or resolvers;
- persistence, migrations, lifecycle, or storage uniqueness;
- runtime, orchestration, CLI, automation, scheduling, monitoring, or
  workflow;
- market prices, Portfolio NAV, market value, valuation, cash state, or FX
  conversion;
- Recommendation action taxonomy, including BUY, SELL, ADD, REDUCE, HOLD, or
  WAIT;
- constraint taxonomy, constraint evaluation details, policy, limits,
  thresholds, utilization, or breach detection;
- approval, rejection, or override workflow;
- explainability narrative schema;
- audit event schema;
- execution semantics or capital movement;
- Capital Bucket amount calculation; or
- Risk Budget limit or utilization calculation.

Proposal, Recommendation, Snapshot, Portfolio, Position, Membership, Capital
Bucket, and Risk Budget identifiers are not denormalized onto the Leg content.
All implementation field validation order, exception messages, and public API
names beyond the architecture frozen here remain for their respective
implementation milestones to specify without changing this decision.
