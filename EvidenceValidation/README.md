# Evidence Validation

## M23-2 Purpose

M23-2 introduces an immutable structured validation result while preserving the domain-validation boundary established in M23-1. `EvidenceValidator.validate()` always delegates first to the existing `validate_research_finding()` function.

## Validation Ownership

ResearchDomain owns the `ResearchFinding` contract and all current field, type, blank-value, and verification-status validation. Evidence Validation does not duplicate or replace those rules.

After successful domain validation, M23-2 performs no additional evidence-quality checks and returns:

```python
EvidenceValidationResult(
    valid=True,
    issues=(),
)
```

`EvidenceValidationIssue` contains `code` and `message`. `EvidenceValidationResult` contains `valid` and an immutable tuple of issues. Both models are frozen, immutable, and hashable.

If domain validation raises, the exact exception propagates unchanged and validation stops before result construction. No exception is caught, wrapped, or replaced, and no result is synthesized.

Validation does not normalize, transform, or mutate the finding or any field value.

## Runtime Boundary

M23-2 does not construct or execute research orchestration, pipeline, committee, execution-engine, adapter, or provider runtimes.

Later M23 steps will introduce evidence-quality and date-quality rules. M23-2 does not parse or validate date formats or relationships, generate issues, score sources, aggregate findings, generate reports, rank, vote, form consensus, synthesize conclusions, make portfolio decisions, issue BUY, HOLD, or SELL recommendations, or allocate capital.
