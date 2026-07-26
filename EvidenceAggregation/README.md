# Evidence Aggregation Identity

## Purpose

Evidence Aggregation owns the explicit association metadata required by a future aggregation-input boundary. M23-5A-1 defines identity metadata only; it does not aggregate evidence.

## Model

`EvidenceAggregationMetadata` contains:

- `finding_id`: an opaque linkage ID for one existing finding. Evidence Aggregation does not generate or change it.
- `aggregation_key`: an opaque grouping identifier explicitly supplied by a caller. Equal values mean only that the caller intends the records to participate in the same aggregation group.
- `source_reference_id`: an opaque identifier for an accepted source reference. Equal values mean only that records explicitly reference the same source-reference ID.

An aggregation key does not prove claim, factual, semantic, event, question, or thesis identity. It must not be inferred from statement text, category, research ID, committee ID, source text, provider identity, or runtime data.

A source-reference ID does not prove source independence, distinct original material, independent reporting, corroboration, or source diversity. It must not be inferred from source text, URLs, providers, committees, or runtime behavior.

## Validation

`validate_evidence_aggregation_metadata()` requires the exact accepted model type and validates each field in model order. Every field must be a nonblank string. Incorrect Python types raise `TypeError`; blank strings raise `ValueError`.

The validator does not mutate, copy, convert, infer, or normalize values. Whitespace-only strings are invalid. Leading or trailing whitespace around nonblank content is accepted as part of the opaque value and remains exactly unchanged. For example, `"group-001"` and `" group-001 "` are distinct accepted values.

Actual linkage against a `ResearchFinding` belongs to a future aggregation-input boundary.

## Public API

Use module-qualified imports:

- `EvidenceAggregation.models.EvidenceAggregationMetadata`
- `EvidenceAggregation.validation.validate_evidence_aggregation_metadata`

The package does not provide package-root aliases.

## Boundaries

This contract does not establish claim identity, semantic or factual equivalence, source independence, credibility, reliability, truth, corroboration, source diversity, contradiction, support, opposition, quality, scores, grades, confidence, ranking, or recommendations.

M23-5A-1 does not implement an aggregator, aggregation request or result models, input envelopes, accepted or rejected records, duplicate handling, corroboration, contradiction detection, or runtime behavior.
