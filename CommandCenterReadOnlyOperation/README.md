# Secure private real read-only operation

This package is the narrow producer boundary between the existing KB
Keychain-backed READ transport and the Command Center's read-only stores. It
calls only OAuth, SSQM2952, and SSQM0004. The HTTP adapter rejects every other
path, including every SSAM mutation path.

The producer and application remain separate processes:

```text
Keychain OAuth + KB READ
  -> existing normalization and snapshot contracts
  -> append-only FactStore + DecisionJournal observation

FactStore + DecisionJournal (SQLite mode=ro/query_only)
  -> CommandCenterApplication
```

## Non-secret binding configuration

Create a private local JSON file outside the repository. It contains logical
identities and explicit verified domestic bindings, never credentials or a
brokerage account number:

```json
{
  "schema_version": 1,
  "account_selector": "kb-primary-readonly",
  "portfolio_id": "personal-portfolio",
  "freshness_max_age_seconds": 300,
  "domestic_bindings": [
    {
      "position_class": "verified-provider-class",
      "provider_symbol": "verified-provider-symbol",
      "position_id": "stable-position-id",
      "portfolio_subject_id": "stable-subject-id"
    }
  ]
}
```

Semantic-blank `crncy_cd` is accepted only when an exact configured
`position_class + provider_symbol` binding exists. Unknown domestic candidates
fail before durable publication. Foreign/USD rows remain immutable raw
evidence and explicit exclusions.

## Daily startup

Produce one observation:

```console
python3 -m CommandCenterReadOnlyOperation \
  --config /absolute/private/path/command_center_readonly.json
```

Then start the independently read-only application:

```console
python3 -m CommandCenterApplication --mode REAL_READ_ONLY \
  --fact-store ~/.joo/command_center/facts.sqlite3 \
  --journal ~/.joo/command_center/decision.sqlite3
```

The server remains bound to `127.0.0.1`. The observation journal record is the
publication boundary, so an interrupted producer cannot cause the application
to mix partially appended facts with a previous snapshot.

The producer never runs research, creates CIO/EV/allocation output, creates
IHA or TEA, changes runtime ownership, or invokes broker mutation.
