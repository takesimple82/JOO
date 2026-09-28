# KB Capital Fact Authority (Block B0)

`KbCapitalFactAuthority` is the Block B0 **Capital Fact Plane**: broker-reported
cash and valuation facts only. It does **not** compute deployable capital,
Human Investment Policy (HIP), allocation sizing, investable weights, approval,
or orders.

```text
SSQM0004 (balances) + SSQM2952 capital fields
  -> immutable raw broker_fact
  -> distinct canonical capital facts
  -> immutable CapitalSnapshot
  -> optional id-only binding to PortfolioSnapshot
```

## Broker orderable cash ≠ deployable capital

`OrderableCashFact` is sourced **only** from `SSQM0004.ordr_psbl_csh`
(주문가능현금). That broker ceiling is **not** JOO deployable capital.
Deployable / investable / HIP ceilings are Block B / later policy planes.

## Frozen H3 field authority

| Fact | Broker field | Notes |
| --- | --- | --- |
| Holding quantity (reuse First Slice) | `SSQM2952.Record1[].hld_q` | Existing portfolio path |
| Position market value | `SSQM2952.Record1[].val_amt` | Never `hld_q × now_prc`; unsettled `hld_q=0` + `val_amt>0` preserved |
| Orderable cash ceiling | `SSQM0004.ordr_psbl_csh` | Broker fact only |
| Deposit / D+1 / D+2 | `tdy_tfnd_amt` / `ndy_tfnd` / `nxt2_dy_tfnd` | Kept distinct; missing ≠ 0 |
| Withdrawable cash | `do_psbl_csh` | Not allocation ceiling |
| Orderable total | `ordr_psbl_amt` | Distinct from orderable cash |
| Broker-reported account valuation | `nt_asts_val_amt` | **NOT** sizing / weights / investable authority |

## Cash-only / domestic-only

- No credit, margin, 미수, loan, 대용, `mx_*`, or leverage inflation of
  `OrderableCashFact`.
- Domestic KRW only on the capital plane. Foreign `SSQM2952` rows
  (`USD`, `외화증권`, `외화증권(M)`, other nonblank non-`KRW`) are
  excluded before domestic MV normalize and leave durable exclusion
  provenance (`EXCLUDED_NON_DOMESTIC`) — never silent drop. Malformed
  domestic lookalikes still fail closed. No FX or cross-currency
  aggregation. Free cash remains `SSQM0004` only.

## Composition

Prefer `run_kb_capital_fact_plane_with_portfolio_slice` to reuse
`run_kb_portfolio_vertical_slice` for holdings, then collect `balances`
(`SSQM0004`) on the existing ProviderGateway live transport.

Raw broker facts are appended **before** canonical normalization. If
normalization fails, the raw fact remains and the plane fails closed.

## Freshness

Caller-supplied `freshness_max_age` is required. Stale or missing freshness
policy fails closed. No default SLA.

## Replay

`replay_capital_snapshot_from_store` rebuilds consistency checks from stored
facts without KB transport or AI.

## Block C revalidation (document only)

Block C must later revalidate that capital facts remain distinct from
allocation / HIP / approval / order authority. This package intentionally
exposes `sizing_authority = NOT_SIZING_AUTHORITY` and does not invent
investable numbers.

## Non-responsibilities

No allocation, HIP, human approval, broker orders, execution, JOO-Automation,
second FactStore/DB/Controller/Bridge, or agent framework.
