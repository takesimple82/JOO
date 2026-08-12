# Market Fact Provenance Reference

This package owns the structural fact provenance reference shape used by
first-slice market instrument observations.

`ExplicitMarketFactProvenanceReference` is a frozen, hashable dataclass
containing exactly:

1. `fact_id: str`
2. `source_identity: str`
3. `collected_at: str`

All three fields are opaque, caller-supplied nonblank strings. They are
structural references only. `collected_at` is not parsed, normalized,
timezone-converted, or validated as ISO calendrical form. Domain does not
invent `collected_at` from wall clock.

`validate_explicit_market_fact_provenance_reference()` requires the exact
model type, then validates `fact_id`, `source_identity`, and `collected_at` in
declaration order as exact nonblank built-in strings. It returns `None` on
success and preserves each supplied string without trimming, normalization,
conversion, copying, or reconstruction.

Presence of a provenance reference does not prove fact existence, freshness,
or economic truth.

## Non-responsibilities

This package does not own Fact Store I/O, append, retrieve, supersession,
source_class, payload bytes, store topology, Provider Gateway, market adapters,
MarketSnapshotProducer, Market Watch, research AI provenance, portfolio
valuation, trading, registries, persistence, migration, runtime, or
orchestration.
