# Evidence Aggregation Input Contracts

## Purpose

Evidence Aggregation owns the explicit association metadata and immutable input envelope required by a future aggregation runtime. It does not aggregate or classify evidence.

## Aggregation Metadata

`EvidenceAggregationMetadata` contains:

- `finding_id`: an opaque linkage ID for one existing finding. Evidence Aggregation does not generate or change it.
- `aggregation_key`: an opaque grouping identifier explicitly supplied by a caller. Equal values mean only that the caller intends the records to participate in the same aggregation group.
- `source_reference_id`: an opaque identifier for an accepted source reference. Equal values mean only that records explicitly reference the same source-reference ID.

An aggregation key does not prove claim, factual, semantic, event, question, or thesis identity. It must not be inferred from statement text, category, research ID, committee ID, source text, provider identity, or runtime data.

A source-reference ID does not prove source independence, distinct original material, independent reporting, corroboration, or source diversity. It must not be inferred from source text, URLs, providers, committees, or runtime behavior.

## Input Envelope

`EvidenceAggregationItem` associates:

- The exact `ResearchFinding`.
- The exact accepted `EvidenceProvenanceMetadata`.
- The exact accepted `EvidenceAssessmentResult`.
- The exact `EvidenceAggregationMetadata`.

The frozen envelope stores the supplied objects directly. It does not copy, reconstruct, normalize, serialize, mutate, or reassess them. It does not call `EvidenceAssessor` or create a replacement assessment.

The envelope is not transitively immutable because the accepted `ResearchFinding` model is mutable. Validation guarantees the associated state only at validation time.

A valid item does not imply that evidence is assessable, accepted by a future aggregator, unique, independent, corroborated, or noncontradictory.

## Validation

`validate_evidence_aggregation_metadata()` requires the exact accepted metadata type and validates each field in model order. Every field must be a nonblank string. Incorrect Python types raise `TypeError`; blank strings raise `ValueError`.

The metadata validator does not mutate, copy, convert, infer, or normalize values. Whitespace-only strings are invalid. Leading or trailing whitespace around nonblank content is accepted as part of the opaque value and remains exactly unchanged. For example, `"group-001"` and `" group-001 "` are distinct accepted values.

`validate_evidence_aggregation_item()`:

1. Requires the exact item and nested accepted model types.
2. Calls the finding, provenance, and aggregation-metadata validators in that order.
3. Validates the assessment finding-ID and policy-version types.
4. Validates provenance, assessment, and aggregation-metadata linkage to the finding, in that order.
5. Requires the assessment policy version exported by EvidenceAssessment.

Upstream exceptions propagate unchanged. Contract failures are not wrapped or converted into issues or result objects.

The item validator accepts structurally valid unassessable evidence. It does not require `assessable` or `validation.valid` to be true and does not recertify dimensions, rationales, or validation internals. The exact assessment and embedded validation objects remain unchanged.

## Public API

Use module-qualified imports:

- `EvidenceAggregation.models.EvidenceAggregationMetadata`
- `EvidenceAggregation.models.EvidenceAggregationItem`
- `EvidenceAggregation.validation.validate_evidence_aggregation_metadata`
- `EvidenceAggregation.validation.validate_evidence_aggregation_item`

The package does not provide package-root aliases.

## Boundaries

These contracts do not establish claim identity, semantic or factual equivalence, source independence, credibility, reliability, truth, corroboration, source diversity, contradiction, support, opposition, quality, scores, grades, confidence, ranking, or recommendations.

The package does not implement an aggregator, aggregation request or result models, accepted or rejected records, duplicate handling, grouping execution, corroboration, contradiction detection, or runtime behavior.
