# PortfolioPropositionLinkApplicability

PortfolioPropositionLinkApplicability classifies whether one accepted explicit
proposition-to-Portfolio-Subject link names the supplied proposition and
Portfolio Subject endpoints.

`classify_explicit_proposition_portfolio_subject_link_applicability()` accepts,
in order:

1. `ExactObservedNumericProposition`
2. `PortfolioSubject`
3. `ExplicitPropositionPortfolioSubjectLink`

It validates the link first, the proposition second, and the Portfolio Subject
third. Upstream exceptions propagate unchanged. After all three inputs are
valid, endpoint identifiers are compared in this order:

1. `link.proposition_id == proposition.proposition_id`
2. `link.portfolio_subject_id == subject.subject_id`

The function returns exactly one
`PortfolioPropositionLinkApplicabilityStatus`:

- `PROPOSITION_ENDPOINT_MISMATCH`
- `PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH`
- `APPLICABLE`

The first mismatch determines the result. Exact string equality is used
without trimming, case folding, Unicode normalization, alias resolution, or
conversion. The function preserves all supplied objects and field objects
without mutation, copying, or reconstruction.

## Boundaries

Applicability means only that the explicit link names the supplied endpoints.
It does not compare an Evidence Proposition's own `subject_id` with the
Portfolio Subject ID. It does not prove that the link is true, authoritative,
trusted, unique, persistent, or semantically correct.

This package does not own proposition extraction, entity or security
certification, ticker or alias semantics, entity resolution, registries,
collections, duplicate handling, membership, holdings, positions, quantity,
price, persistence, migration, runtime orchestration, impact direction,
materiality, confidence, expected value, scoring, priority, CIO queues,
recommendations, or capital allocation.

Production code depends only on EvidenceProposition, PortfolioDomain,
PortfolioPropositionLink, this package, and the Python standard library. Those
upstream packages remain independent and unchanged.
