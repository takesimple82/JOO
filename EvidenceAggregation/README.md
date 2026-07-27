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

## Batch Boundary

`EvidenceAggregationBatch` stores an explicit ordered tuple of `EvidenceAggregationItem` objects for possible future aggregation processing. It assigns no execution or aggregation semantics.

The supplied collection must be the exact built-in `tuple` type. Lists, tuple subclasses, generators, sequences, and other iterables are rejected rather than converted or consumed. The exact tuple and every item object are stored directly in caller-supplied order. No copying, reconstruction, normalization, sorting, grouping, or deduplication occurs.

An empty tuple is structurally valid. The batch validator returns `None` without invoking item validation.

Repeated structures are permitted, including the same item object, equal items, and items sharing finding IDs, aggregation keys, or source-reference IDs. Acceptance does not certify uniqueness or non-duplication.

`validate_evidence_aggregation_batch()` requires the exact batch type, requires an exact tuple, and delegates to `validate_evidence_aggregation_item()` exactly once per item in tuple order. It stops on the first failure and propagates the exact exception unchanged. It does not add an item index or produce a partial result.

Tuple order is deterministic caller-supplied order only. It does not imply ranking, priority, chronology, confidence, quality, or execution precedence.

The batch is frozen and its tuple prevents element reassignment. It is not transitively immutable because nested items contain mutable `ResearchFinding` objects. Validation guarantees state only at validation time.

A valid batch does not imply that items share an aggregation group, findings are unique, sources are independent, evidence is assessable or accepted, corroboration or contradiction exists, aggregation can execute, or a result will be produced.

## Group Boundary

`EvidenceAggregationGroup` stores an explicit nonempty ordered tuple of already-grouped items under one caller-supplied aggregation key. Every validated item metadata key must exactly equal the group key. The group does not derive items from a batch, partition collections, search by key, or perform grouping.

The group key must be the exact built-in `str` type and must contain non-whitespace content. String subclasses are rejected. The key is never trimmed, case-folded, normalized, rebuilt, or replaced. Consequently, `"group-001"` and `" group-001 "` are distinct valid keys, and item linkage uses their exact values.

The item collection must be the exact built-in `tuple` type and must not be empty. Lists, tuple subclasses, generators, sequences, and arbitrary iterables are rejected without conversion or consumption. The exact key, tuple, and item objects remain stored in caller-supplied order.

`validate_evidence_aggregation_group()` validates the group, key, tuple, and nonempty invariant before processing items. It then calls `validate_evidence_aggregation_item()` exactly once per item and checks that item’s aggregation key only after successful item validation. The first upstream exception or linkage mismatch stops processing. Upstream exceptions propagate unchanged without an index prefix.

Repeated object references, equal items, repeated finding IDs, and repeated source-reference IDs are structurally permitted when their aggregation keys match. Acceptance does not certify uniqueness or non-duplication.

Caller-supplied order is preserved without implying ranking, priority, chronology, confidence, quality, or execution precedence. No sorting, copying, normalization, grouping, or deduplication occurs.

The group is frozen and its tuple prevents element reassignment, but it is not transitively immutable because nested items contain mutable `ResearchFinding` objects. Aggregation metadata is frozen, and nested finding mutation does not change aggregation-key linkage. Validation guarantees state only at validation time.

A valid group does not imply item, finding, or source uniqueness; source independence; corroboration; contradiction; evidence acceptance; execution readiness; aggregate conclusions; or result production.

## Public API

Use module-qualified imports:

- `EvidenceAggregation.models.EvidenceAggregationMetadata`
- `EvidenceAggregation.models.EvidenceAggregationItem`
- `EvidenceAggregation.models.EvidenceAggregationBatch`
- `EvidenceAggregation.models.EvidenceAggregationGroup`
- `EvidenceAggregation.validation.validate_evidence_aggregation_metadata`
- `EvidenceAggregation.validation.validate_evidence_aggregation_item`
- `EvidenceAggregation.validation.validate_evidence_aggregation_batch`
- `EvidenceAggregation.validation.validate_evidence_aggregation_group`

The package does not provide package-root aliases.

## Boundaries

These contracts do not establish claim identity, semantic or factual equivalence, source independence, credibility, reliability, truth, corroboration, source diversity, contradiction, support, opposition, quality, scores, grades, confidence, ranking, or recommendations.

The package does not implement an aggregator, aggregation request or result models, accepted or rejected records, duplicate handling, grouping execution, corroboration, contradiction detection, or runtime behavior.
