# Numeric Signal to Hypothesis Link

This package defines one explicit structural link from an accepted exact
numeric Signal classification object to a semantically produced Hypothesis.

`ExplicitNumericSignalHypothesisLink` is a frozen dataclass containing:

1. `signal: ExactNumericDeltaSignalClassification`
2. `hypothesis: SemanticallyProducedHypothesis`

There is no canonical Signal ID in the repository. The link therefore
preserves the complete immutable Signal result object rather than inventing an
ID, hashing contextual fields, or treating proposition IDs and threshold as a
composite identity. The full object retains proposition endpoints, unit,
delta, policy, direction, materiality, and Signal status.

The validator requires the exact link type, exact Signal result type, and
exact semantic Hypothesis wrapper type in that order. It then validates the
semantic Hypothesis wrapper exactly once and propagates its exception
unchanged. The Signal field is treated as an accepted classifier result; this
link does not reclassify it.

The same Signal object may participate in multiple links and the same
Hypothesis may participate in multiple links. Duplicate links are
structurally allowed. The model has no separate association identity and
preserves both supplied object identities.

This boundary does not generate Hypotheses, infer statement meaning, certify
causality or evidence sufficiency, aggregate Signals, enforce uniqueness,
perform lookup or persistence, implement lifecycle, Thesis, Expected Value,
Portfolio impact, CIO decisions, runtime, registry, graph execution, or
orchestration.
