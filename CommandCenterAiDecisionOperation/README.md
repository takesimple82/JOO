# Evidence-bound REAL AI CIO attempt

This package is the minimal Phase 8 operational seam from the active
`READ_ONLY_OBSERVATION` to research/CIO availability state. It does not replace
`OperationalCioCycle`: that existing composition remains the only admitted
successful path from actual committee responses through semantic admission,
ExactExpectedValue, comparison, and non-executable CIO synthesis.

The package creates an immutable broker-fact evidence package bound to the
authoritative DecisionJournal sequence, observation, PortfolioSnapshot,
CapitalSnapshot, normalized fact IDs, and raw holdings/balances identities.
Research never mutates these facts.

When no authorized external AI provider configuration exists, REAL mode
publishes the truthful state:

```text
RESEARCH_UNAVAILABLE -> COMMITTEE_UNAVAILABLE -> CIO BLOCKED
EV UNAVAILABLE -> Allocation UNAVAILABLE -> IHA NOT_ISSUED
```

No deterministic fixture or simulated committee response is accepted by this
REAL entrypoint. If configured providers are detected, the unavailable runner
fails closed and requires the explicit subject, committee, model, policy, and
semantic bindings already required by `OperationalCioCycle`.

```console
python3 -m CommandCenterAiDecisionOperation \
  --fact-store ~/.joo/command_center/facts.sqlite3 \
  --journal ~/.joo/command_center/decision.sqlite3
```

The operation has no IHA, TEA, order, or broker mutation authority.
