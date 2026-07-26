# Evidence Assessment

## Purpose

Evidence Assessment provides a deterministic, dimension-only representation of accepted evidence inputs. Version 1.0 preserves verification status and source class without combining them into a score, grade, confidence level, probability, rank, or recommendation.

## Policy Version

`ASSESSMENT_POLICY_VERSION = "1.0"` identifies the evidence-assessment policy. It is not a package, repository, model, or provider version.

## Execution Order

`EvidenceAssessor.assess()`:

1. Calls `EvidenceValidator.validate(finding)`. ResearchDomain validation executes first through that accepted contract.
2. Calls `validate_evidence_provenance(provenance)`.
3. Requires `provenance.finding_id == finding.finding_id`.
4. Returns an unassessable result with no dimensions when evidence validation has issues.
5. Otherwise returns `VERIFICATION_STATUS` followed by `SOURCE_CLASS`.

Domain and provenance exceptions propagate unchanged. A finding-ID mismatch is a contract `ValueError`. Contract failures are never converted into issues or assessment results.

## Dimensions

The canonical dimension order is:

1. `VERIFICATION_STATUS`
2. `SOURCE_CLASS`

Values are copied exactly from validated inputs. Rationales state only the accepted classification and do not infer credibility, reliability, strength, confidence, or truth.

The exact `EvidenceValidationResult` object is preserved in the assessment result.

## Boundaries

The assessment does not inspect source text, statement content, category, committee identity, provider identity, URLs, runtime state, current time, or external data.

It does not implement scores, weights, grades, confidence, probability, ranking, corroboration, deduplication, aggregation, contradiction detection, reputation, freshness, verification methods, materiality, relevance, thesis or portfolio logic, reporting, recommendations, BUY/HOLD/SELL, or capital allocation.
