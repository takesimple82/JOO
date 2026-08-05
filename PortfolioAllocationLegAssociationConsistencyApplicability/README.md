# Portfolio Allocation Leg Association Consistency Applicability

## Responsibility and public API

`PortfolioAllocationLegAssociationConsistencyApplicability` deterministically
classifies one explicitly supplied comparison set containing one accepted M49
Leg-to-Capital-Bucket link, one accepted M50 Leg-to-Risk-Budget link, and one
accepted Portfolio Risk Budget endpoint. It checks only Allocation Leg, Risk
Budget, and Capital Bucket identity alignment in frozen order.

The complete and exact public API is:

- `PortfolioAllocationLegAssociationConsistencyApplicabilityStatus`
- `classify_portfolio_allocation_leg_association_consistency_applicability()`

The status is imported from `models` and the classifier from `classification`.
There is no package-root re-export, result dataclass, validator, unchecked
classifier, Boolean helper, or additional API.

## Status contract

`PortfolioAllocationLegAssociationConsistencyApplicabilityStatus` is a
standard `Enum` with exactly these members, explicit values, and order:

1. `ALLOCATION_LEG_ENDPOINT_MISMATCH = "ALLOCATION_LEG_ENDPOINT_MISMATCH"`
2. `RISK_BUDGET_ENDPOINT_MISMATCH = "RISK_BUDGET_ENDPOINT_MISMATCH"`
3. `CAPITAL_BUCKET_ENDPOINT_MISMATCH = "CAPITAL_BUCKET_ENDPOINT_MISMATCH"`
4. `APPLICABLE = "APPLICABLE"`

It has no aliases, fields, defaults, custom methods or properties, metadata,
ranking, severity, Boolean conversion, or persistent identity. Standard Enum
identity, equality, and hashing apply.

Mismatch statuses are valid results, not exceptions. `APPLICABLE` means only
that the three identity comparisons align for this set. It does not establish
general constraint satisfaction, capital availability, acceptable risk, trade
permission, or execution eligibility.

## Inputs, validation, and exceptions

The classifier accepts exactly three required positional-or-keyword inputs in
order:

1. `capital_bucket_link: ExplicitPortfolioAllocationLegCapitalBucketLink`
2. `risk_budget_link: ExplicitPortfolioAllocationLegRiskBudgetLink`
3. `risk_budget: ExplicitPortfolioRiskBudget`

Its return annotation is
`PortfolioAllocationLegAssociationConsistencyApplicabilityStatus`. There are
no defaults or optional inputs. Absence does not produce a status; `None` or a
substitute object is a malformed invocation.

Before comparing identities, the classifier calls exactly once and in order:

1. `validate_explicit_portfolio_allocation_leg_capital_bucket_link()`;
2. `validate_explicit_portfolio_allocation_leg_risk_budget_link()`; and
3. `validate_explicit_portfolio_risk_budget()`.

Each receives the exact supplied object. No later validator or comparison runs
after the first failure. The first upstream exception object propagates
unchanged with exact identity, type, and message. M51 defines no local
validation exception or missing-input status.

## Ordered classification

After all validation succeeds, exact stored string equality is evaluated in
this order; the first mismatch wins:

1. M49 `allocation_leg_id` versus M50 `allocation_leg_id` returns
   `ALLOCATION_LEG_ENDPOINT_MISMATCH` when unequal.
2. M50 `risk_budget_id` versus endpoint `risk_budget_id` returns
   `RISK_BUDGET_ENDPOINT_MISMATCH` when unequal.
3. M49 `capital_bucket_id` versus endpoint `capital_bucket_id` returns
   `CAPITAL_BUCKET_ENDPOINT_MISMATCH` when unequal.
4. Complete alignment returns `APPLICABLE`.

The classifier returns only an existing enum singleton. It constructs no
result, explanation, identifier, collection, wrapper, or metadata.

## Exact values and preservation

Comparison performs no trimming, case folding, Unicode normalization, aliasing,
canonicalization, conversion, coercion, copying, reconstruction, derivation,
hashing, generation, inference, or resolution. Case, whitespace, and composed
or decomposed Unicode differences remain significant.

Every supplied input and field object is preserved without mutation. Exact
string equality determines alignment; string object identity is retained but
does not replace equality comparison.

## Cardinality boundary

M51 evaluates one explicitly supplied comparison set per invocation. It does
not accept or search collections, mappings, registries, or repositories; select
preferred records; aggregate results; define collection cardinality; or create
reverse collections.

M49 and M50 duplicate and shared-endpoint structural contracts remain
unchanged. M51 does not detect duplicates, reject equal records, enforce
uniqueness or coverage, or enforce one M49 or M50 record per Leg. Duplicate or
structurally equal records can participate in independent calls.

## Dependency boundary

`models.py` imports only standard-library `enum`. `classification.py` imports
only this package's status model and the accepted M49, M50, and Portfolio Risk
Budget models and validators. Production code imports no Allocation Leg or
Capital Bucket endpoint, constraint, calculation, persistence, runtime,
registry, repository, resolver, database, mapping, API, CLI, automation, or
third-party package.

## Non-responsibilities

M51 does not own general Portfolio Allocation constraint taxonomy,
registration, orchestration, aggregation, policy, evaluation, enforcement,
satisfaction, breach, severity, amount, remediation, override, or priority.

It owns no capital capacity, balance, funding, reservation, cash, currency,
price, valuation, FX, NAV, capital movement, risk amount, limit, threshold,
tolerance, utilization, remaining capacity, concentration, ratio, percentage,
target weight, quantity interpretation, unit conversion, trade sizing,
rebalance, target holding, or allocation calculation.

It performs no Recommendation action interpretation, approval, rejection,
explainability, audit, execution, lifecycle decision, endpoint production,
existence proof, lookup, resolution, registry, repository, database access,
mapping, traversal, canonicalization, uniqueness, duplicate rejection,
deduplication, coverage, collection cardinality, reverse collection, record
selection, collection-level consistency, mutation, repair, normalization, or
persistence of M49, M50, or Risk Budget records.

It owns no persistence, migration, schema, API, CLI, runtime, orchestration,
workflow, automation, scheduling, monitoring, external integration, hidden
state, or third-party dependency. It does not prove an association true,
authorized, complete, current, unique, economically appropriate, or suitable
for action.
