# Phase 8 real AI CIO decision pipeline

## Reused authority chain

```text
READ_ONLY_OBSERVATION (DecisionJournal append sequence)
  -> ObservationEvidencePackage (broker_fact IDs only)
  -> InvestmentResearchOrchestrator / Committee (actual providers only)
  -> OperationalCioCycle semantic admission
  -> ExactExpectedValue
  -> non-executable CioDecisionRecord
  -> CapitalAllocationCycle (valid EV + SSQM0004 orderable cash)
  -> Investment Human Approval required
  -> Command Center read-only projection
```

Phase 8 does not add another research, contradiction, EV, allocation, or
approval domain. Successful AI decisions continue to use the existing
`OperationalCioCycle`. Its requirements include complete independent
committee responses, prompt/provider/model provenance, resolved contradiction
audit, current evidence, exact Decimal assumptions, and a non-executable CIO
record.

## Publication and rebinding

DecisionJournal append sequence—not provider timestamps—selects the active
factual observation. An evidence package records that sequence and the exact
observation, PortfolioSnapshot, CapitalSnapshot, normalized fact, and raw-fact
identities. Orphan FactStore writes are never current. REAL decision artifacts
whose snapshot does not match the active observation are not projected.

## Current external-provider state

The operational host has no configured authorized AI provider key/model pair.
The admitted REAL result is therefore:

```text
RESEARCH_UNAVAILABLE
COMMITTEE_UNAVAILABLE
CONTRADICTION NOT_EVALUATED
CIO BLOCKED
EV UNAVAILABLE
ALLOCATION UNAVAILABLE
IHA NOT_ISSUED
BROKER MUTATION DISABLED
```

Fixture responses remain test-only. Configured providers cannot be silently
downgraded into this unavailable path; callers must supply the explicit
provider, committee, subject, horizon, policy, and semantic bindings required
by the existing operational cycle.

## Non-responsibilities

No order, TEA, IHA grant, broker mutation, frontend AI calculation, fabricated
EV, automated profit realization, public-network binding, generic orchestration
framework, or JOO-Automation dependency is introduced.
