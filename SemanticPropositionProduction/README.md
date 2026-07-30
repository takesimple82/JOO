# Semantic Proposition Production

This package defines the minimum structural acceptance boundary for an exact
numeric proposition that a caller attests was semantically produced by an
authoritative external or future Knowledge producer.

## Public contract

`SemanticallyProducedNumericProposition` is a frozen dataclass with exactly
one field:

1. `proposition: ExactObservedNumericProposition`

`validate_semantically_produced_numeric_proposition()` requires the exact
production model type and the exact `ExactObservedNumericProposition` field
type, rejecting subclasses of either. It then invokes
`validate_exact_observed_numeric_proposition()` exactly once and propagates
its exception unchanged. Validation returns `None` on success.

The wrapper stores the supplied proposition object directly. It does not copy,
convert, reconstruct, normalize, or mutate the proposition or any field.
Structural equality and hashing follow the wrapped proposition.

## Attestation meaning

The wrapper records only a caller-supplied declaration that the proposition
was produced semantically by the authoritative upstream producer assumed by
the repository contract. It does not execute or prove production, identify
the producer, prove provenance, or establish semantic accuracy or truth.
Duplicate wrappers around the same proposition are allowed.

## Non-responsibilities

This package does not parse natural language, extract numeric values, infer or
normalize units, invoke an LLM, link a Finding object or source reference,
create provenance or producer identities, generate proposition IDs, associate
observed dates, select or pair baseline/current propositions, or implement
runtime, persistence, orchestration, confidence, scoring, materiality, Signal,
Hypothesis, Thesis, or Portfolio impact.
