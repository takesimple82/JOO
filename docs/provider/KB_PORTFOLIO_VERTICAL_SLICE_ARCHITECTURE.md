# KB Portfolio Vertical Slice Architecture

## Accepted path

```text
KbOpenApiAdapter / SSQM2952
  -> immutable raw `broker_fact`
  -> explicit per-row canonical `broker_fact`
  -> durable SQLite FactStore
  -> PortfolioSnapshotProducer
  -> PortfolioScanner exact structural comparison
  -> immutable IRO ingress binding
  -> existing RunCoordinator
```

The application seam is `KbPortfolioVerticalSlice`. Existing component
dependency directions remain unchanged: the gateway does not store facts,
the snapshot producer does not call providers, and IRO does not import the
gateway, FactStore, or snapshot producer.

## Identity and provenance

The Gateway envelope identity and successful payload are stored without
interpretation. Each canonical row is identified by the exact tuple
`(account_selector, clsf, crncy_cd, is_cd)` and requires a closed-world
binding to caller-supplied fact, envelope, position, and portfolio-subject
identities. No provider symbol, ticker, account, or portfolio identity is
generated or resolved.

The canonical fact records `raw_fact_id`, `raw_envelope_id`, exact raw
quantity text, and a canonical decimal string. Provider prices and valuation
fields remain in the raw evidence and are not portfolio valuation inputs in
this slice.

## Durability

`SQLiteAppendOnlyFactEngine` is a single-file standard-library backend. WAL,
FULL synchronous commits, unique identities, foreign-key supersession,
immutable-row triggers, and transactional batch append provide local crash
safety. Startup replay verifies record structure, integrity seals, ordering,
and supersession history. Any mismatch prevents store use.

Raw evidence may remain after a normalization rejection. Canonical position
facts are all accepted or none are accepted.

## Snapshot and admission

Only complete canonical facts from the same collection time and provider are
bound to `PortfolioSnapshotProducer`. The operator must supply a nonnegative
`freshness_max_age`; absence fails before provider collection. Expired facts
remain history but cannot produce a current snapshot.

Zero-quantity rows remain stored canonical facts and are excluded from active
holding membership. Prior snapshots are comparison baselines only and are
never carried forward as current state.

`PortfolioScanner` owns structural comparison. A nonempty first baseline is
`BASELINE_ABSENT`; later exact membership or quantity deltas are `CHANGED`;
an empty delta set is `NO_CHANGE`. Only the first two classes may reach IRO.
The ingress artifact binds the IRO run, current/prior snapshot identities,
raw and normalized fact identities, producer provenance, provider, and
collection time before the existing coordinator is invoked.

## Exclusions

There is no AI factual inference, market-price watch, Expected Value, CIO,
allocation, approval, broker execution, scheduler, generic orchestration, or
JOO-Automation dependency in this slice.
