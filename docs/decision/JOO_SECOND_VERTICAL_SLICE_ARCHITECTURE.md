# JOO Second Vertical Slice Architecture

## Runtime

```text
fresh Portfolio Snapshot + factual provenance
  -> IRO committee evidence/completeness/contradiction
  -> immutable research evidence bundle
  -> qualitative and existing exact-numeric signals
  -> semantic Hypothesis / Thesis
  -> append-only thesis transition
  -> applicable Portfolio Impact
  -> research-derived probability/payoff assumptions
  -> existing ExactExpectedValue
  -> horizon-isolated strict opportunity comparison
  -> non-executable JOO CIO decision
  -> Human review boundary
```

## Authority

Provider facts remain factual truth. IRO and semantic-producer content remains
`research_ai`. Thesis, impact, EV, comparison, and CIO records are derived
decisions. AI may propose structured probabilities and payoffs after complete
committee evidence and resolved contradictions, but cannot calculate the
authoritative EV or invent evidence references.

The approved thesis states are strengthened, weakened, unchanged, invalidated,
and unresolved. Approved CIO postures are maintain, research more, consider
rotation, invalidate thesis, and no action unresolved. Neither invalidation nor
rotation consideration authorizes a trade.

Each configured Portfolio Impact horizon is an independent comparison plane.
Comparison additionally requires equal EV unit, probability policy, and
comparison policy. Exact strict Decimal ordering is used; incompatible inputs
are incomparable and missing EV is unresolved.

All decision artifacts are appended atomically to a local chained SQLite
journal. Startup verifies schema, mutation guards, every seal, and the entire
previous-seal chain. Deterministic replay reruns EV and comparison only and
never invokes the semantic AI producer.

Allocation sizing, constraints, approval, broker orders, execution, scheduling,
dashboard, and automation are outside this slice.
