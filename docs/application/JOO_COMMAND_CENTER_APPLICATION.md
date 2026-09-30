# JOO Command Center application boundary

The Phase 6 application foundation is an observation surface, not a new
orchestrator. It projects existing immutable JOO artifacts into a professional
operator dashboard while preserving their source authority.

The data flow is one-way:

`FactStore + DecisionJournal -> verified read-only query -> immutable projection -> redacted JSON -> local UI`

The application shows portfolio composition, authoritative capital facts,
change state, CIO posture, Expected Value records, allocation and investment
approval state, execution safety, human attention, evidence references, and
system health. Missing or malformed authority fails closed; the UI never
derives broker facts, quantities, prices, valuations, approvals, or execution
permission.

`FIXTURE` mode is deterministic and visibly labelled as demo data.
`REAL_READ_ONLY` opens already-existing SQLite databases in read-only mode and
verifies FactStore record integrity, supersession ordering, and the
DecisionJournal hash chain before projection.

The real producer is a separate process documented in
`CommandCenterReadOnlyOperation/README.md`. Its journaled observation is the
publication boundary: incomplete FactStore-only writes cannot silently become
the application's current portfolio view.

Phase 8 adds a second separate operation documented in
`CommandCenterAiDecisionOperation/README.md`. It binds an immutable factual
evidence package to the journal-ordered active observation. The existing
`OperationalCioCycle` remains the only successful provider/committee/Exact EV
CIO path. When no authorized provider exists, the operation persists only a
truthful unavailable/blocked attempt. The API exposes that state through
`ai_pipeline`; JavaScript performs no research or investment calculation.

REAL-mode decision, EV, allocation, and approval artifacts are admitted to the
view only when their snapshot/decision chain matches the active factual
observation. A later factual observation cannot silently inherit an older CIO
or allocation result.

This slice adds no public-network deployment, authentication system, broker
mutation, approval action, TEA issuance, portfolio automation, or replacement
for durable production ownership. Those remain outside this application's
authority.
