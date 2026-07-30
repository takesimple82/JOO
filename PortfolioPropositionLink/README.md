# PortfolioPropositionLink

PortfolioPropositionLink owns one explicit, directed linkage from an accepted
Evidence Proposition ID to a canonical Portfolio Subject ID.

`ExplicitPropositionPortfolioSubjectLink` contains exactly these fields in
order:

1. `proposition_id: str`
2. `portfolio_subject_id: str`

`proposition_id` refers to the accepted opaque identifier carried by
`EvidenceProposition.models.ExactObservedNumericProposition`.
`portfolio_subject_id` refers to
`PortfolioDomain.models.PortfolioSubject.subject_id`. It is named distinctly
from an Evidence Proposition's own `subject_id`; this package does not treat
those two subject identifiers as the same namespace.

The model is frozen, hashable, has no defaults, custom methods, or slots, and
stores both supplied identifier objects directly.

`validate_explicit_proposition_portfolio_subject_link()` performs structural
validation only. It requires the exact link model type and validates
`proposition_id` before `portfolio_subject_id`. Both values must be exact
nonblank built-in strings. Validation returns `None` on success.

The validator does not trim, case fold, normalize Unicode, convert, copy, or
reconstruct the link or either identifier. Surrounding whitespace on an
otherwise nonblank identifier is accepted and preserved. Equality is exact
structural equality over both stored identifiers.

## Boundaries

The link is an explicit caller-supplied declaration. Structural validity does
not validate endpoint existence, certify that either ID was authoritatively
issued, prove semantic correctness, or establish trust or applicability. It
does not compare `portfolio_subject_id` with an Evidence Proposition's
`subject_id`.

This package does not own proposition extraction, finding or source linkage,
portfolio membership, holdings or positions, quantity or price, ticker or
alias semantics, entity or security certification, entity resolution,
registries, uniqueness, duplicate handling, collections, lookup, persistence,
migration, runtime orchestration, impact direction, materiality, confidence,
expected value, scoring, priority, CIO queues, recommendations, or capital
allocation.

Production code depends only on the Python standard library and this package.
EvidenceProposition and PortfolioDomain remain independent and unchanged.
