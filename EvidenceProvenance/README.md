# Evidence Provenance

## Purpose

Evidence Provenance defines the minimal immutable source-classification contract for one existing `ResearchFinding`. It does not modify or extend the finding itself.

## Contract

`EvidenceProvenanceMetadata` contains:

- `finding_id`
- `source_class`

Accepted source classes, in canonical order:

1. `primary`
2. `secondary`
3. `unknown`

`primary` identifies original material produced directly by an event participant, issuing organization, regulator, official system, or original data producer.

`secondary` identifies third-party material that reports, analyzes, summarizes, or republishes an event or primary material.

`unknown` identifies a source that cannot be classified from explicitly accepted information.

Source class expresses provenance distance only. Primary does not mean true, and secondary does not mean unreliable. The value must be supplied explicitly and is never inferred from source text, URLs, providers, committees, or runtime behavior.

## Validation

`validate_evidence_provenance()` validates the exact model type, a nonblank string `finding_id`, and one canonical source-class value. It raises `TypeError` for incorrect Python types and `ValueError` for blank or unsupported values.

Validation does not normalize, trim, convert, infer, copy, or mutate inputs. Provenance contract errors remain exceptions and are not converted into evidence-validation issues.

## Boundaries

This package does not depend on Research Logging or runtime packages. It does not implement linking services, scoring, confidence, corroboration, aggregation, source reputation, URL processing, freshness, reporting, thesis or portfolio logic, recommendations, or capital allocation.
