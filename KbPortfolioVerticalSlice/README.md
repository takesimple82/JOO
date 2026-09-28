# KB Portfolio Vertical Slice

`KbPortfolioVerticalSlice` is the narrow application seam for one factual
product path:

```text
KB SSQM2952 -> raw broker fact -> canonical position facts
  -> PortfolioSnapshotProducer -> exact change admission -> existing IRO
```

It composes existing product components. It does not replace or become
ProviderGateway, FactStore, PortfolioSnapshotProducer, PortfolioSnapshot,
PortfolioScanner, or InvestmentResearchOrchestrator.

## Contracts

- The complete successful SSQM2952 payload is appended before projection.
- Every `Record1` row requires an exact caller-supplied account, provider
  symbol, position-class, currency, portfolio-subject, position, fact, and
  envelope binding.
- `SSQM2952` is the verified domestic holdings path. `Record1.crncy_cd` is
  fixed-width `String(3)`; the official sample is three ASCII spaces. Exact
  raw `crncy_cd` is preserved without strip/overwrite. Semantic blank means
  `raw.strip() == ""` (empty or whitespace-only). Semantic blank or exact
  raw `KRW` is canonicalized to `KRW` only when the row has exactly one
  explicit caller-supplied `KRW` binding for the same account, position
  class, and provider symbol. Blank currency with an absent, ambiguous,
  unknown, or non-KRW binding fails closed. Any other nonblank currency
  fails closed; overseas schemas remain separate. Currency is never inferred
  from ticker, symbol, company, blank alone, account nationality, or AI.
- Quantities are unsigned finite decimal text. `float` is never accepted.
- One malformed, duplicate, missing, ambiguous, or unused binding rejects
  the complete canonical batch.
- Canonical position facts retain raw fact and envelope identities plus the
  exact provider quantity and currency text.
- Canonical facts are accepted in one durable FactStore transaction.
- Zero-quantity rows remain canonical facts but are omitted from active
  snapshot holding membership.
- `freshness_max_age` is a required caller policy. No default SLA exists.
- Stale, incomplete, unavailable, and no-change cycles never invoke IRO.
- A nonempty valid initial baseline or exact structural snapshot change may
  produce an immutable IRO ingress artifact and invoke the existing
  `RunCoordinator`.
- Broker facts remain distinct from `research_ai` outputs.

## Non-responsibilities

This package owns no HTTP, OAuth, generic scheduler, Controller, Bridge,
state machine, market-price watch, Expected Value, CIO, opportunity ranking,
capital allocation, human investment approval, broker order, execution, or
JOO-Automation integration.
