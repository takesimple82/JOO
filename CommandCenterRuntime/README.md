# Command Center Runtime (Completion Block D)

`CommandCenterRuntime` is the Block D **24/7 AI CIO Command Center** operational
plane. It wakes only from evidence-bound facts, routes deterministic stages
across existing Blocks A / B0 / B / C services, preserves both Human gates
(InvestmentHumanApproval and TradeExecutionAuthorization), and never activates
live SSAM mutation.

```text
Evidence-bound WakeEvent
  -> deterministic change detection (no invented materiality %)
  -> wake routing (capital-only ≠ auto research)
  -> JOOOperationalCycle / run_command_center_cycle
       collect → persist → detect → classify
       → run ONLY required existing domain stages
       → HumanAttentionItem → OperationalCheckpoint
  -> recover_command_center (crash resume; no duplicate mutation/authority)
```

## Frozen D0 posture

| Rule | Enforcement |
| --- | --- |
| Evidence First | `seal_wake_event` rejects AI/LLM sources and AI_INVENTED fact ids |
| No Stage Skipping | `assert_no_stage_skip` + `STAGE_PREDECESSORS` |
| Both Human gates | IHA and TEA never merged / auto-approved / timeout-approved |
| Live disabled | `LiveMutationTransportDisabled` default; `enable_live_mutation` raises |
| Idempotency | `IdempotencyStore` keyed by source_event + decision_kind |
| Fail closed | missing ≠ 0/unchanged/safe; ownership unprovable → deny |
| Hosting | `run_command_center_cycle` + `recover`; no while-loop correctness |

## Explicit stages

FACT_REFRESH → PORTFOLIO_SNAPSHOT → CAPITAL_SNAPSHOT → RESEARCH →
SEMANTIC_ADMISSION → THESIS → EXPECTED_VALUE → CIO → CAPITAL_ALLOCATION →
INVESTMENT_HUMAN_GATE → PRETRADE → TRADE_HUMAN_GATE → BROKER_STATUS →
RECONCILIATION

## Journal kinds

Block D extends `JournalRecordKind` with `WAKE_EVENT`,
`OPERATIONAL_CHECKPOINT`, `HUMAN_ATTENTION_ITEM`, `PROVIDER_OPERATION_FAILURE`.
OCC codec admits `CommandCenterRuntime.models`.

## Non-responsibilities

No JOO-Automation, no Controller / Loop Core / workflow engine / second DB,
no live SSAM1801/1802/1805/1806, no AI investment reasoning inside the cycle,
no Block E / final E2E / live trading activation.

## Verification

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s CommandCenterRuntime/tests -q`
