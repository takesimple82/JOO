# Evidence Validation

## M23-1 Purpose

M23-1 establishes the domain-validation boundary for future evidence-quality validation. `EvidenceValidator.validate()` always delegates first to the existing `validate_research_finding()` function.

## Validation Ownership

ResearchDomain owns the `ResearchFinding` contract and all current field, type, blank-value, and verification-status validation. Evidence Validation does not duplicate or replace those rules.

Successful validation currently returns `None`. If domain validation raises, the exact exception propagates unchanged and validation stops immediately. No exception is caught, wrapped, or replaced, and no result is synthesized.

Validation does not normalize, transform, or mutate the finding or any field value.

## Runtime Boundary

M23-1 does not construct or execute research orchestration, pipeline, committee, execution-engine, adapter, or provider runtimes.

Later M23 steps will introduce structured evidence-validation results and date-quality rules. M23-1 does not parse or validate date formats or relationships, collect issues, score sources, aggregate findings, generate reports, rank, vote, form consensus, synthesize conclusions, make portfolio decisions, issue BUY, HOLD, or SELL recommendations, or allocate capital.
