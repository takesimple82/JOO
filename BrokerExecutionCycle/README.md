# Broker Execution Cycle (Completion Block C)

`BrokerExecutionCycle` is the Block C **human-gated LIMIT order execution**
plane. It consumes Block B `SealedApprovedAllocationArtifact` +
`InvestmentHumanApproval` and fresh pre-trade facts. It does **not** live-call
SSAM1801/1802/1805/1806 against production from default paths.

```text
SealedApprovedAllocation + IHA
  + ProposedLimitPrice (explicit; no AI; no market fallback)
  + Quote (IVU10140) + trade unit (trd_q_unt)
  + Orderable cash (SSQM0004.ordr_psbl_csh) / sellable (SSQM1801.ordr_psbl_q)
  + Instrument bridge (A005930 → 005930) + VerifiedExecutionAccountBinding
      -> PreTradeValidation (fail-closed)
      -> LIMIT OrderIntent (ordr_ccd=00 only)
      -> TradeExecutionAuthorization (TEA; one-shot; binds intent seal)
      -> Mutation Safety Gate + durable pre-send attempt
      -> Mock mutation transport ONLY by default
      -> Accept / Reject / SUBMISSION_OUTCOME_UNKNOWN
      -> SSQM2341 status/fill facts (no overclaim)
      -> Reconciliation (acceptance ≠ fill)
```

## Frozen Human Execution Policy V1

| Code | Rule |
| --- | --- |
| C0-D1 | `ordr_ccd="00"` LIMIT_ONLY; never 03/12/13/M3 |
| C0-D2 | IHA alone insufficient; chain IHA → SealedApprovedAllocation → fresh pretrade → OrderIntent → TEA → mutation |
| C0-D3 | ExactDecimal qty floor to trade unit; unit missing → FAIL CLOSED (do not assume 1); exposure ≤ 100000000 |
| C0-D4 | VerifiedExecutionAccountBinding required; no inventing `gnl_ac_no1`; mutation false until verified |
| C0-D5 | UNKNOWN → READ-only SSQM2341; auto recovery = STATE ONLY never reorder; ambiguous → Human |

## KB contracts (C0 authority)

| Action | API |
| --- | --- |
| BUY | SSAM1802 `POST /api/v1/ssam1802` |
| SELL | SSAM1801 |
| MODIFY | SSAM1805 (deferred; no auto policy) |
| CANCEL | SSAM1806 (deferred; no auto policy) |
| Status | SSQM2341 |
| Quote | IVU10140 (`trd_q_unt`, `now_prc`) |
| Cash | SSQM0004.`ordr_psbl_csh` |
| Sellability | `ordr_psbl_q` |

Acceptance: `processFlag=="A"` **and** nonzero/non-all-zero `ordr_no`.
HTTP 200 alone ≠ accept. Do not AI-parse `o_msg`.

## Journal kinds

Block C extends `JournalRecordKind` with pretrade / intent / TEA / submit /
acceptance / rejection / unknown / status / fill / reconciliation kinds.

## Non-responsibilities

No live SSAM mutation by default, no JOO-Automation, no Controller/Bridge,
no second DB, no float, no AI arithmetic, no Block A/B/B0 semantic drift.

## Verification

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s BrokerExecutionCycle/tests -q`
