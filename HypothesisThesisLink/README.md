# Hypothesis to Thesis Link

This package defines one explicit structural link from a semantically produced
Hypothesis to a semantically produced Thesis.

`ExplicitHypothesisThesisLink` is a frozen, hashable dataclass containing:

1. `hypothesis: SemanticallyProducedHypothesis`
2. `thesis: SemanticallyProducedThesis`

The validator requires the exact link and endpoint wrapper types, validates
the Hypothesis first and Thesis second exactly once each, propagates the first
upstream exception unchanged, and returns `None` on success.

The link preserves both complete immutable semantic objects. It has no
separate identity. One Hypothesis may link to multiple Theses and one Thesis
may link to multiple Hypotheses; duplicates are structurally allowed.

A link establishes only an explicit supplied relationship. It does not prove
that the Hypothesis supports the Thesis, that evidence is sufficient, or that
either statement is true, causal, coherent, portfolio relevant, or suitable
for action.

This package does not aggregate Hypotheses, enforce cardinality or uniqueness,
manage lifecycle, confidence, conviction, catalysts, risks, Expected Value,
Portfolio impact, BUY/HOLD/SELL, allocation, CIO judgment, runtime,
persistence, registry, lookup, graph execution, or orchestration.
