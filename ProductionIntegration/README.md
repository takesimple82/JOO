# Production Integration (Block E)

This package is the thin production composition for one externally scheduled
JOO Command Center cycle. It reuses the existing DecisionJournal and the
authoritative Block A/B0/B/C/D services. It is not a controller, scheduler,
workflow engine, policy engine, or second database.

Public entrypoints:

- `run_one_joo_command_center_cycle`: real stage and journal wiring for one
  cycle. An explicit UTC clock value is required. Live broker mutation is not
  accepted or reachable.
- `recover_joo_command_center_state`: integrity-checks the existing append-only
  journal and rebuilds a projection without provider, AI, Human-authority, or
  broker calls.
- `run_mock_broker_submission_dry_run`: explicit deterministic test seam. It
  accepts `MockMutationTransport` exactly and durably records the attempt and
  consumed one-shot authority in one transaction before the mock call.

Human authority is observed, never created. InvestmentHumanApproval and
TradeExecutionAuthorization must already be exact durable journal artifacts.
IHA may authorize pre-trade preparation and a sealed LIMIT OrderIntent, but
only a separate TEA bound to that exact intent reaches the mock mutation gate.

The production runner maps Command Center stages directly onto existing
services. The Operational CIO application is invoked once and its immutable
artifacts are exposed across the A-stage labels. Capital allocation delegates
to CapitalAllocationCycle. Broker status and reconciliation are READ-only.
There is no alternate EV arithmetic, allocation logic, execution engine, or
automatic approval/authorization.

Known broker contract uncertainties remain fail-closed: unverified SSAM
account authority, undocumented process flags, unresolved positive SSQM2341
fill semantics, native KB idempotency, cancel/modify policy, and market orders.
The production default remains `LiveMutationTransportDisabled`.

Human-attention records are immutable safety evidence. Block E deliberately
does not infer that an item is resolved from a later event; without a separate
explicit, durable Human resolution contract, recovery keeps it unresolved and
fails safe. It never deletes or silently supersedes historical attention.
