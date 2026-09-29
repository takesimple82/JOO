# Broker Execution Cycle (Completion Block C)

`BrokerExecutionCycle` is the Block C **human-gated LIMIT order execution**
plane. It consumes Block B `SealedApprovedAllocationArtifact` +
`InvestmentHumanApproval` and fresh pre-trade facts. It does **not** live-call
SSAM1801/1802/1805/1806 against production from default paths.
Every mock mutation also requires a caller-owned durable pre-send appender;
without it the mutation gate fails before transport invocation.
The final mutation gate recomputes the account, OrderIntent, TEA, and SSAM
translation bindings, requires the explicit execution-account allowlist, and
accepts the exact local `MockMutationTransport` type only. A caller cannot
raise the frozen 100,000,000 KRW absolute exposure cap through the validation
override seam; an override may only make the cap stricter.

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

## Phase 2 pre-live authority closure (A–G)

Evidence sources: official KB Excel (`all_kbstock_excel-20260812-101425.xlsx`) +
sample ZIP (`all_kbstock_sample (1).zip`). Never invent missing broker semantics.
`LiveMutationTransportDisabled` remains true — no real SSAM submit/cancel/modify.

| ID | Authority | Closure |
| --- | --- | --- |
| A | SSAM account-field | `gnl_ac_no1` SAMPLE_OBSERVED (Excel INPUT omits); OrderIntent/TEA exact bind; Excel required INPUT enforced; unknown FAIL CLOSED |
| B | SSQM2341 fill | Excel qty `ordr_q`/`tl_ccls_q`/`nccls_q` only when processFlag=A + matched Record1; HTTP alone ≠ fill; undocumented enums raw/UNKNOWN |
| C | KB native idempotency | NONE_DOCUMENTED; JOO uses TEA one-shot + durable pre-send |
| D | Cancel/modify | SSAM1805/1806 + Excel `crct_clsf` 1/2; draft only; `DEFERRED_NO_AUTO_POLICY` |
| E | HumanAttention / UNKNOWN | `QUERY_RECOVER_THEN_HUMAN_IF_AMBIGUOUS`; never auto-resubmit |
| F | Credential / allowlist | no secret logging; allowlisted `gnl_ac_no1` only; mismatch FAIL CLOSED |
| G | Shadow dry-run | intent→binding→qty→SSAM body→live-disabled boundary→shadow ack/recon; `real_mutation_submitted=False` |

See `authority_evidence.py`, `account_allowlist.py`, `kb_idempotency.py`,
`shadow_dry_run.py`, and `tests/test_phase2_authority_closure.py`.

## Verification

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s BrokerExecutionCycle/tests -q`

## Phase 4 gates (live still disabled)

- JIT TEA: `tea_freshness.assert_jit_fresh_facts_permit_exact_execution` required at mutation gate; fresh SSQM0004.`ordr_psbl_csh` under ORDERABLE_CASH_FULL; exact intent only; fail closed.
- Open LIMIT: `open_limit_monitor` → HumanAttention only; `DEFERRED_NO_AUTO_POLICY` preserved.
- `gnl_ac_no1`: AUTHORITY_NOT_CLOSED / LIVE_BLOCKER (Excel omit; sample conflict).
- `LiveMutationTransportDisabled` remains default; mock/shadow only.
