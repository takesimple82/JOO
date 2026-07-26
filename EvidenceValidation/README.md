# Evidence Validation

## M23-3 Purpose

M23-3 adds strict event and publication date-quality rules while preserving the domain-validation boundary established in M23-1. `EvidenceValidator.validate()` always delegates first to the existing `validate_research_finding()` function.

## Validation Ownership

ResearchDomain owns the `ResearchFinding` contract and all current field, type, blank-value, and verification-status validation. Evidence Validation does not duplicate or replace those rules.

After successful domain validation, M23-3 accepts dates only in strict `YYYY-MM-DD` calendar format. It records issues in this deterministic order:

1. `INVALID_EVENT_DATE`
2. `INVALID_PUBLICATION_DATE`
3. `PUBLICATION_BEFORE_EVENT`

The relationship rule runs only when both dates are valid. Publication may equal or follow the event date, but it must not precede it. Evidence-quality failures are returned as issues and do not raise exceptions.

`EvidenceValidationResult.valid` is true exactly when `issues` is empty.

`EvidenceValidationIssue` contains `code` and `message`. `EvidenceValidationResult` contains `valid` and an immutable tuple of issues. Both models are frozen, immutable, and hashable.

If domain validation raises, the exact exception propagates unchanged and validation stops before result construction. No exception is caught, wrapped, or replaced, and no result is synthesized.

Validation does not normalize, transform, or mutate the finding or any field value.

## Runtime Boundary

M23-3 does not construct or execute research orchestration, pipeline, committee, execution-engine, adapter, or provider runtimes.

M23-3 does not validate dates against the current date, handle timezones, validate source URLs or credibility, detect duplicates, score or weight evidence, aggregate findings, generate reports, rank, vote, form consensus, synthesize conclusions, make portfolio decisions, issue BUY, HOLD, or SELL recommendations, or allocate capital.
