# Portfolio Impact Applicability

This package deterministically classifies whether an accepted semantic Thesis,
an explicit Thesis-to-Portfolio-Subject link, and a canonical Portfolio Subject
name the same structural endpoints.

`classify_portfolio_impact_applicability()` accepts, in order:

1. `SemanticallyProducedThesis`
2. `ExplicitThesisPortfolioSubjectLink`
3. `PortfolioSubject`

It validates each input exactly once in that order and propagates the first
upstream exception unchanged. After all validation succeeds, it compares:

1. `semantic_thesis.thesis.thesis_id == link.thesis_id`
2. `portfolio_subject.subject_id == link.portfolio_subject_id`

The first mismatch determines the result. A Thesis mismatch therefore takes
precedence over a Portfolio Subject mismatch.

The classifier returns exactly one `PortfolioImpactApplicabilityStatus`:

- `APPLICABLE`
- `THESIS_ENDPOINT_MISMATCH`
- `PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH`

Exact identifier equality is used without trimming, case folding, Unicode
normalization, parsing, alias resolution, conversion, copying, reconstruction,
or mutation. Applicability means only that the supplied link names the supplied
endpoints.

## Non-responsibilities

This package does not establish semantic correctness or portfolio relevance,
parse a Thesis statement, interpret impact as beneficial, neutral, or adverse,
create an impact identity, apply a horizon or interpretation policy, require a
rationale, calculate Expected Value, perform portfolio membership lookup, or
own holdings, positions, allocation, recommendations, runtime, registries,
persistence, migration, or orchestration.
