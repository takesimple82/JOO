# JOO Command Center Application

This package is a local, read-only application surface over JOO's existing
facts, journaled decisions, attention records, and execution safety state. It
does not own investment decisions, approvals, trade authorization, broker
submission, or durable runtime ownership.

## Modes

- `FIXTURE` is the default. It is conspicuously labelled and never represents
  live KB data.
- `REAL_READ_ONLY` requires existing FactStore and DecisionJournal SQLite
  files. Both are opened with SQLite `mode=ro`; the application cannot create,
  migrate, or append to them.

Run the deterministic demo locally:

```console
python3 -m CommandCenterApplication --mode FIXTURE
```

Run against existing verified stores:

```console
python3 -m CommandCenterApplication --mode REAL_READ_ONLY \
  --fact-store /absolute/path/facts.sqlite3 \
  --journal /absolute/path/decision.sqlite3
```

Open `http://127.0.0.1:8765`. The server binds only to loopback and exposes
GET/HEAD routes. POST, PUT, PATCH, and DELETE are rejected.

After a fresh factual observation, record the Phase 8 evidence-bound AI
availability state with the separate producer before starting this viewer:

```console
python3 -m CommandCenterAiDecisionOperation \
  --fact-store /absolute/path/facts.sqlite3 \
  --journal /absolute/path/decision.sqlite3
```

Without an authorized external research provider, the API truthfully exposes
`RESEARCH_UNAVAILABLE`, `COMMITTEE_UNAVAILABLE`, blocked CIO, unavailable EV
and allocation, and `NOT_ISSUED` IHA. It never substitutes fixture research.

## Authority boundary

- position quantity comes only from canonical `SSQM2952` position facts;
- position market value comes only from broker `val_amt` facts;
- cash comes only from `SSQM0004.ordr_psbl_csh` and remains a ceiling;
- broker account valuation is displayed as `NOT_SIZING_AUTHORITY`;
- foreign positions remain explicit exclusions;
- all decimal values remain canonical decimal strings through JSON and UI;
- execution is always shown as `LIVE_BLOCKED` / `LIVE_DISABLED` while the
  current real execution authority remains unclosed.

There are intentionally no approval, TEA, capital mutation, broker mutation,
or recovery-control endpoints.
