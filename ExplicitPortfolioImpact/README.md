# Explicit Portfolio Impact

This package defines one immutable, caller-supplied Portfolio Impact
interpretation that is structurally applicable to accepted Thesis and
Portfolio Subject endpoints and allowed by an explicit interpretation policy.

`ExplicitPortfolioImpact` is a frozen, hashable dataclass containing exactly:

1. `impact_id: str`
2. `semantic_thesis: SemanticallyProducedThesis`
3. `link: ExplicitThesisPortfolioSubjectLink`
4. `portfolio_subject: PortfolioSubject`
5. `policy: PortfolioImpactInterpretationPolicy`
6. `direction: PortfolioImpactDirection`
7. `horizon_id: str`
8. `rationale: str`

The opaque `impact_id` does not encode endpoints, direction, horizon, policy
version, timestamps, scenarios, or revisions. Full immutable upstream objects
are retained without redundant endpoint or policy identity fields.

`validate_explicit_portfolio_impact()` requires the exact Impact model, exact
nonblank ID, and exact accepted upstream object types. It validates the
semantic Thesis, link, Portfolio Subject, and policy exactly once each, then
validates direction, horizon, and rationale. Endpoint and policy applicability
are classified without repeating upstream validation.

A valid Impact must name matching Thesis and Portfolio Subject endpoints and
must use a direction and horizon allowed by its policy. Its rationale may be
blank only when the policy does not require one. All supplied objects and
strings are preserved without mutation, copying, reconstruction, trimming,
normalization, conversion, or semantic inference.

Multiple records may share endpoints, policies, horizons, or directions.
Alternative and conflicting records are structurally allowed and remain
distinct through caller-supplied `impact_id` values.

## Non-responsibilities

Structural validity does not prove that the interpretation is correct, the
Thesis is true, causality exists, evidence is sufficient, or the Impact is
material. This package does not calculate Expected Value, make
recommendations, allocate capital, establish confidence, resolve conflicts,
manage lifecycle or supersession, perform lookup or uniqueness enforcement,
or own producer identity, human identity, provenance, approval, runtime,
registry, persistence, migration, or orchestration.
