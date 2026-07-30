# Thesis to Portfolio Subject Link

This package owns one explicit, directed structural link from an accepted
Thesis ID to a canonical Portfolio Subject ID.

`ExplicitThesisPortfolioSubjectLink` is a frozen, hashable dataclass containing
exactly these fields in order:

1. `thesis_id: str`
2. `portfolio_subject_id: str`

`thesis_id` refers to `ExplicitThesis.models.ExplicitThesis.thesis_id`.
`portfolio_subject_id` refers to
`PortfolioDomain.models.PortfolioSubject.subject_id`.

`validate_explicit_thesis_portfolio_subject_link()` requires the exact link
model type, then validates `thesis_id` before `portfolio_subject_id`. Both
fields must be exact nonblank built-in strings. It returns `None` on success.

The model stores both supplied identifier objects directly. Validation does
not trim, case fold, normalize Unicode, convert, copy, or reconstruct either
identifier or the link. Surrounding whitespace on an otherwise nonblank value
is accepted and preserved.

The link has no separate identity. Duplicate links and shared endpoints are
structurally allowed. Structural validity does not validate endpoint
existence, prove that a Thesis affects a Portfolio Subject, establish semantic
correctness, or certify portfolio relevance.

## Non-responsibilities

This package does not own Thesis or Portfolio Subject production, endpoint
lookup, registries, membership, holdings or positions, watchlists, quantities,
prices, impact direction, beneficial or harmful interpretation, materiality,
confidence, Expected Value, constraints, scoring, allocation, recommendations,
CIO judgment, runtime, persistence, migration, graph execution, or
orchestration.

Production code depends only on the Python standard library and this package.
ExplicitThesis and PortfolioDomain remain independent and unchanged.
