# Capital Allocation Cycle (Completion Block B)

`CapitalAllocationCycle` is the Block B **Human Investment Policy + deterministic
capital allocation + Investment Human Approval** plane. It consumes Block B0
`KbCapitalFactAuthority` CapitalSnapshot facts and Block A CIO outputs. It does
**not** place broker orders, SSAM fills, lots, or JOO-Automation actions.

```text
Frozen HIP V1
  + CapSnapshot orderable cash (SSQM0004.ordr_psbl_csh)
  + OpportunityUniverse eligibility
  + CIO posture / EV comparisons
  + caller-proposed NON-EXECUTABLE KRW notionals
      -> deterministic allocator
      -> fail-closed constraint engine
      -> CapitalAllocationProposal (executable=False)
      -> InvestmentHumanApproval
      -> SealedApprovedAllocationArtifact (no order payload)
```

## Frozen HIP V1

| Field | Value |
| --- | --- |
| deployable_capital_mode | `ORDERABLE_CASH_FULL` → deployable = CapSnapshot orderable cash |
| explicit_reserve_krw | `Decimal("0")` **explicit** (missing ≠ 0) |
| max_position_market_value_krw | `Decimal("100000000")` hard cap |
| capital_sourcing_mode | `ROTATION_ALLOWED` |
| on_invalidate_thesis | `BLOCK_AND_ALLOW_REDUCE_LEGS` |
| leverage_allowed | `False` |
| approval_required | `True` |
| currency | KRW domestic only |
| profit_realization_mode | `DEFER` (documented; no +50% hardcoded) |

**Never** use `nt_asts_val_amt` / broker-reported account valuation as the
deployable denominator. CapSnapshot `sizing_authority` remains
`NOT_SIZING_AUTHORITY`.

## CIO posture admission (V1)

| Posture | Allocation effect |
| --- | --- |
| MAINTAIN | preserve; no forced increase |
| CONSIDER_ROTATION | may rotate under EV superiority + policy; ≠ auto sell |
| INVALIDATE_THESIS | no buy/increase; reduce/exit allowed; approval required |
| NO_ACTION_UNRESOLVED / RESEARCH_MORE | no new capital increase |

## Actions

`INCREASE` / `MAINTAIN` / `REDUCE` / `EXIT` are derived from current vs proposed
KRW market-value notional. Share-quantity conversion that would invent
executable orders is rejected; intents remain NON-EXECUTABLE KRW notionals.

## Capital conservation

Cash-funded increases ≤ deployable after explicit reserve + eligible rotation
proceeds. Rotation proceeds are attributable per reduced subject and must not
be double-counted. Provenance is carried on `CapitalFundingProvenance`.

## RiskBudget / CapitalBucket

Structural ID compatibility only. No numeric risk model or AI allocation
arithmetic.

## Journal kinds

Block B extends `JournalRecordKind` with HIP / proposal / approval / artifact
kinds. Payloads remain sealed, append-only DecisionJournal records.

## Non-responsibilities

No Block C orders/lots/SSAM/fills, no Controller/Bridge/agent framework, no
second DB, no float, no ExactExpectedValue semantic changes, no Block A EV
comparison margin/turnover/cost changes, no JOO-Automation.

## Verification

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s CapitalAllocationCycle/tests -q`
