# KB OpenAPI Runtime Credential Configuration Architecture

## Status and identity

- Status: Architecture remediations after independent review C.
  ARCHITECTURE REMEDIATION REQUIRED; first-time credential and
  host-identity configuration freeze only; ready for independent
  re-review
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Provider & Fact** (runtime ingress composition around the
  already-accepted ProviderGateway ports)
- Opaque unnumbered identity: **KB OpenAPI Runtime Credential
  Configuration**
- Owner package: **`ProviderGateway`**
- Owner surface: ProviderGateway / runtime ingress
- This document does **not** invent or assign `PF-M6`, `KB-M1`, `M55+`,
  `Automation-M4`, `Autopilot-M1`, `PF-M5`, `Credential-M1`,
  Architecture State Resolver, or any other manufactured successor
  identity
- Authorizing previous decisions:
  - `~/JOO-Automation/results/kb_openapi_live_factual_pipeline_post_commit_verification/latest.md`
    — **FINAL DECISION: POST-COMMIT CHECKPOINT VERIFIED**
  - `~/JOO-Automation/results/kb_openapi_controlled_live_pilot_authorization_review/latest.md`
    — **FINAL DECISION: CONTROLLED LIVE PILOT AUTHORIZED**
  - `~/JOO-Automation/results/kb_openapi_controlled_live_pilot_verification_review/latest.md`
    — **FINAL DECISION: CONTROLLED LIVE PILOT VERIFIED**
  - `~/JOO-Automation/results/kb_openapi_runtime_credential_configuration_architecture_review/latest.md`
    — **FINAL DECISION: C. ARCHITECTURE REMEDIATION REQUIRED**.
    Remediations R1–R8 from that review and the authorized remediations
    prompt are incorporated in this freeze text
- This document is a **JOO-scoped** operational architecture. It is **not**
  a `JOO_AUTOMATION` catalog grant, not a selector/catalog/CIA change, and
  not an Autopilot membership action
- Repository boundary for this document: architecture remediations only;
  this document alone authorizes no production code, test, package change,
  schema module, configuration file, secret file, live KB call, live
  Autopilot run, stage, commit, tag, or push

This document freezes the **smallest lawful operational slice** that
removes repeated manual credential and host-identity input from the
already-proven live KB factual path.

```text
first-time human-controlled setup
        │
        ├── hidden appKey / appSecret  →  macOS Keychain
        └── non-secret host identity   →  operator-local file
                │
                ▼
normal JOO run  (zero interactive input)
        │
        ├── retrieve Keychain items
        ├── reconstruct existing credential JSON
        ├── load / derive host identity
        ▼
existing CredentialSupplier
        │
        ▼
existing KbOpenApiLiveBrokerTransport
        │
        ├── Candidate B OAuth
        └── SSQM2952
                │
                ▼
existing KbOpenApiAdapter / ProviderGateway broker_fact envelope
```

It does **not** redesign accepted Gateway, transport, FactStore, or
Snapshot public contracts.

It does **not** persist holdings, execute orders, call market APIs, or
start Autopilot.

Implementation requires a separate authorization after independent
architecture re-review and a later Implementation Boundary Review. This
document does **not** authorize that implementation.

---

## Normative surface (must remain explicit)

### This freeze implements ONLY

| # | Responsibility |
| --- | --- |
| 1 | **One-time secure registration** of KB `appKey` / `appSecret` into macOS Keychain |
| 2 | **Runtime Keychain retrieval** that reconstructs the already-accepted credential JSON string |
| 3 | **Existing `CredentialSupplier` occupancy** so `credential_ref` and Gateway collect remain unchanged |
| 4 | **One-time non-secret host-identity configuration** for `dataHeader.ipAddr` |
| 5 | **Automatic derivation of the current locally assigned MAC of the active primary Wi-Fi interface** for `dataHeader.macAddr`, with an optional non-secret override |
| 6 | **Fail-closed missing / denied / malformed secret and host-identity behavior** |
| 7 | **Fake-backend testability** so CI never requires real Keychain items or real KB credentials |
| 8 | **Preservation** of the proven live path: Candidate B OAuth → SSQM2952 → existing Gateway envelope |

### This freeze does NOT implement

| Concern | Owner (elsewhere) |
| --- | --- |
| **`BrokerTransport` / `KbOpenApiLiveBrokerTransport` public contract** | Frozen live factual pipeline — reused, not redesigned |
| **`KbOpenApiAdapter` public collect contract** | Frozen PF-M1 broker-first slice — reused |
| **`CredentialSupplier` Protocol** | Frozen PF-M1 — occupied, not redesigned |
| **FactStore append / eligibility / retrieval** | Frozen PF-M2 / `FactStore` — not this slice |
| **Portfolio Snapshot production** | Frozen PF-M3 — unchanged |
| **Market Snapshot / MarketTransport** | Frozen PF-M4 / later live-market slice |
| **Selector / catalog / CIA / Autopilot / Supervisor** | JOO_AUTOMATION plane — not this work |
| **Architecture State Resolver** | Deferred; not a prerequisite |
| **IRO / CIO capital allocation** | Later research / capital planes |
| **Order placement / modify / cancel / autonomous trading** | Layer 15 BX-M1 + Human Approval |
| **General secrets platform / cross-platform vault** | Never this slice |
| **Public-IP discovery product / external IP website lookup** | Never this slice |
| **Holdings normalization / domestic cash / buying power / overseas / market data** | Later additive slices |

---

## 1. Repository checkpoint

Verified immediately before authoring and re-verified immediately before
this remediation. Remediation does not proceed from an unverified
checkpoint.

### JOO

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| Path | `/Users/takesimple/Projects/JOO` | `/Users/takesimple/Projects/JOO` | Match |
| Branch | `feature/stage2-provider-runtime` | `feature/stage2-provider-runtime` | Match |
| HEAD | `8c8f654dc7cb7d0e59e92e9f41ffc94e880a0cc5` | Exact | Match |
| Exact tag at HEAD | `v7.20-stage5-kb-openapi-live-factual-pipeline` | Lightweight tag at HEAD | Match |
| Subject | `Add KB OpenAPI Live Factual Pipeline implementation` | Exact | Match |
| Tracked tree | Clean | Clean | Match |
| Staged set | Empty | Empty | Match |
| Authorized mutation | this architecture file only | Exact this file | Match |

**Preserved out-of-boundary untracked files (read-only; not modified, not
staged):**

- `docs/JOO_PRODUCT_ARCHITECTURE.md`
- `docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md`

**Authorized remediation target (untracked; the only JOO file this
remediation may modify):**

- `docs/provider/KB_OPENAPI_RUNTIME_CREDENTIAL_CONFIGURATION_ARCHITECTURE.md`

### JOO-Automation

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| Path | `/Users/takesimple/JOO-Automation` | `/Users/takesimple/JOO-Automation` | Match |
| Branch | `main` | `main` | Match |
| HEAD | `4e227411080276a71e5a9af0870618b7d391772e` | Exact | Match |

JOO-Automation is **read-only evidence** for this document. It is not
the owner, not a secret store, and not a configuration plane.

---

## 2. Frozen live evidence this document consumes

This identity does **not** re-prove the live KB path. It consumes the
already-verified controlled live pilot.

### 2.1 Proven live path

```text
real appKey / appSecret
        → Candidate B OAuth
        → SSQM2952
        → KbOpenApiLiveBrokerTransport
        → KbOpenApiAdapter
        → ProviderGateway broker_fact envelope
```

### 2.2 Proven live result

| Fact | Frozen value |
| --- | --- |
| First live fact | `SSQM2952` |
| OAuth | HTTP 200, Candidate B only |
| SSQM2952 | HTTP 200 |
| `processFlag` | `A` |
| `processCode` | `0011` |
| `Record1` | list, 11 rows |
| Secret residual scan | PASS |
| Sensitive-account-metadata keys | NONE |
| Gateway `result_kind` | `success` |
| `provider_id` | `kb_open_api` |
| `source_class` | `broker_fact` |
| `status` | `success` |
| FactStore append | NO |
| Order execution | NO |
| Market API | NO |
| Autopilot | NO |

### 2.3 Proven credential encoding

The committed decoder accepts only a JSON object string whose exact keys
are `appKey` and `appSecret`, both nonblank `str`. The controlled pilot
constructed:

```text
{"appKey":"...","appSecret":"..."}
```

via `json.dumps(..., separators=(",", ":"))` and supplied that string
through the existing `CredentialSupplier`.

This identity must reconstruct **that same encoding**. It must not invent
a second credential dialect.

### 2.4 Proven host-identity values used by the pilot

The successful pilot sent:

| Field | Pilot value | Classification |
| --- | --- | --- |
| `dataHeader.ipAddr` | `58.226.25.218` | Required request field. Not SECRET. Not SENSITIVE_ACCOUNT_METADATA |
| `dataHeader.macAddr` | `02:c9:e7:ea:c3:8a` | Required request field. Current locally assigned MAC of the active primary Wi-Fi interface. Locally administered / Private Wi-Fi MAC |

That pilot MAC is the **local interface** value. It is **not** the
`networksetup -getinfo Wi-Fi` field `Wi-Fi ID`, which on the same
machine was `ac:c9:06:24:5a:ba`. Those two strings are **not
interchangeable**. See §13.4.

Operator fact consumed from the verification review: that public IP was
**not** separately registered in the KB Open API developer console, and
OAuth plus SSQM2952 still returned HTTP 200.

**What this proves**

- For that successful pilot, on that application, at that time, a
  separate console registration of the current public IP was not an
  operational prerequisite.
- `ipAddr` / `macAddr` remain required Candidate B / SSQM2952
  `dataHeader` fields.
- The MAC first octet `02` is consistent with macOS Private Wi-Fi
  Address, not a burned-in NIC.

**What this does not prove**

- KB never validates IP.
- KB never validates MAC.
- KB ignores `dataHeader.ipAddr` / `macAddr`.
- A dummy, LAN, or sample placeholder IP would be accepted.
- Source TCP IP is unchecked.
- Order TRs, other apps, or a later policy change would behave the same.

Those unproven claims must not become product machinery.

### 2.5 Pilot UX that this identity retires

The controlled live pilot intentionally used per-run manual input:

- `input()` for public IP
- `input()` for MAC
- `getpass()` for `appKey`
- `getpass()` for `appSecret`

That method remains the **proven first-pilot injection**. It is **not**
the desired everyday production UX. Production runtime must not preserve
per-run typing of those four values.

---

## 3. Existing JOO inventory this identity must reuse

Inspected accepted tracked implementation. This identity composes around
these contracts. It does not reopen them.

| Capability | Accepted state | Constraint on this identity |
| --- | --- | --- |
| `KbOpenApiLiveBrokerTransport` | Occupies `BrokerTransport` | Constructor still requires nonblank `ip_addr` and `mac_addr`. Decoder still requires exact JSON keys `appKey` / `appSecret` |
| `KbOpenApiAdapter.collect` | Public broker collect | Unchanged |
| `CredentialSupplier` | `credential_ref -> object` | Unchanged Protocol. Gateway resolver still requires nonblank `str` |
| `resolve_outbound_credential` | Supplier exception or non-`str` / blank → `AUTH_FAILURE` | Reused |
| `ExplicitBrokerAdapterBinding.credential_ref` | Opaque nonblank handle. Not the secret | Reused |
| Envelope / failure classes | Existing vocabulary | Reused. No second failure plane |
| Process-local token cache | `_access_token` / `_token_type` / `_expires_at` | Unchanged. Access token is **not** stored in Keychain |
| SECRET vocabulary | Includes `appKey`, `appSecret`, `access_token`, `token`, `hts_pwd`, `ac_pwd`, `hd_pin_no` | Unchanged |
| SENSITIVE_ACCOUNT_METADATA | Unchanged | Unchanged |
| JOO CLI / `joo configure` / `JOO start` | **Absent** | Command **semantics** are frozen here. Exact shell/CLI wiring is deferred to Implementation Boundary Review |
| `config.yaml` | Git-tracked research/script config | **Not** a host-identity or secret store |
| `PipelineRuntime` | Committee execution runtime | **Not** this owner |
| `run.sh` | Research → Knowledge → CIO script | **Not** this owner. Do not hijack |

There is **no** accepted production secrets vault, Keychain facade, host
identity file, or operator CLI for KB credentials.

---

## 4. Exact operational gap

The live factual path is proven. The remaining gap is operational UX and
secret lifetime:

```text
proven:
  CredentialSupplier(str) → decoder → OAuth → SSQM2952 → envelope

missing:
  durable secret storage that is not a file, not git, not a prompt
  automatic host-identity supply that is not typed every run
```

This freeze occupies **only** that gap.

It does **not** occupy FactStore persistence, holdings normalization,
Snapshot integration, cash, buying power, overseas, market data,
scheduler, or orders.

### 4.1 Strategic constraint

This work must not become another long infrastructure detour.

It is a **narrow operational UX/security slice** whose only purpose is:

```text
remove repeated manual credential / host-identity input
while preserving the already-proven live KB factual path
```

Rejected expansions:

- general enterprise secrets platform / general secrets manager
- cross-platform credential abstraction
- Keychain daemon or new credential server
- public-IP discovery product / network discovery service
- network watcher / IP-registration subsystem
- broad CLI framework
- new configuration platform
- new Gateway public API
- new collect dialect
- Autopilot or scheduler attachment
- FactStore / Snapshot / market integration
- automatic trading

---

## 5. Owner and opaque identity

### 5.1 Owner

| Field | Decision |
| --- | --- |
| Owner package | **`ProviderGateway`** |
| Owner surface | **runtime ingress** |
| Plane | Provider & Fact |
| Additive capability | Keychain-backed credential supply + host-identity composition for the existing live KB transport |
| Not the owner | Milestone Selection Engine, Selector Input Supply, CIA, Supervisor, Autopilot, Architecture State Resolver, CIO, Research Committee, FactStore, Snapshot producers, JOO-Automation, `PipelineRuntime`, `run.sh` |

`ProviderGateway` already owns ingress, the KB adapter, the live
transport, and credential **use**. This freeze occupies the already
accepted `CredentialSupplier` port and the already accepted transport
constructor arguments `ip_addr` / `mac_addr`. It does not move ownership
to automation, research, or capital planes.

### 5.2 Opaque unnumbered identity

**Exact identity string:**

```text
KB OpenAPI Runtime Credential Configuration
```

This identity names the operational capability, not a roadmap rank.

Rejected manufactured identities:

- `PF-M6`
- `KB-M1`
- `Credential-M1`
- `M55+`
- `Automation-M4`
- `Autopilot-M1`

### 5.3 Additive-versus-new-package ruling

| Option | Verdict |
| --- | --- |
| **Additive runtime composition inside existing `ProviderGateway`** | **Selected and frozen** |
| New package (`SecretsVault`, `KeychainGateway`, `CredentialPlatform`, `HostIdentityService`) | **Rejected** — second secrets / config plane |
| Relocate secrets into `FactStore` | **Rejected** — store becomes a vault |
| Relocate secrets into Snapshot / IRO / CIO | **Rejected** |
| Relocate secrets into JOO-Automation state / prompts / results | **Rejected** |
| Reuse git-tracked `config.yaml` | **Rejected** — machine-specific and would mix secrets or host data into git |
| Cross-platform secrets library (`keyring`, cloud KMS, etc.) | **Rejected** — extra dependency and a platform |

### 5.4 Layout intent (additive; not a scaffold)

```text
ProviderGateway/
  adapters/
    kb_open_api.py                         # frozen adapter; unchanged
    kb_openapi_live_broker_transport.py    # frozen live transport; unchanged public contract
    ports.py                               # CredentialSupplier unchanged
  auth/
    credentials.py                         # frozen public helpers; unchanged
    kb_openapi_keychain.py                 # THIS freeze: retrieve + reconstruct
    kb_openapi_host_identity.py            # THIS freeze: IP load + MAC derive/override
```

Setup command wiring is **not** created by this document. Exact setup
module path is an Implementation Boundary Review detail.

Prefer **module functions and injected callables** over public classes
and new `ports.py` Protocols. A `KeychainBackend` test seam is justified.
Named ports such as `IpAddrSupplier` are heavier than needed; a function
is enough.

This document does **not** create any of those files.

---

## 6. Required architecture questions

| # | Question | Decision |
| --- | --- | --- |
| 1 | Where are `appKey` / `appSecret` persisted? | **macOS Keychain only.** Two generic-password items. See §7 |
| 2 | What persistence options are rejected? | Plaintext `.env`, JSON/YAML secret files, git-tracked config, per-run prompts, JOO-Automation state, FactStore, Snapshot, AI context, general cross-platform secrets platforms |
| 3 | What is the first-time setup UX? | Human-controlled `joo configure kb` **semantics**. Hidden entry. Store to Keychain. Never echo. Never write secrets to project files. Exact CLI wiring deferred. See §8 |
| 4 | What is the normal-run UX? | Zero interactive input. Retrieve Keychain. Load/derive host identity. Existing collect path. See §9 |
| 5 | How does runtime load credentials? | Keychain retrieve → reconstruct exact JSON → existing `CredentialSupplier` → existing decoder. See §10 |
| 6 | What is the secret lifetime? | Keychain persistent. Credential JSON and decoded values process-local only. Access token remains the existing process-local transport cache. See §11 |
| 7 | What is the IP strategy? | **Configuration-backed non-secret `ip_addr`** filling the existing transport constructor, plus a separately replaceable loader. No external lookup. No per-run input. No network-change detector. Stale configured value is sent until `--host` or an existing live call fails. See §12 |
| 8 | What is the MAC strategy? | **Auto-derive the current locally assigned MAC of the active primary Wi-Fi interface** at composition time, with optional non-secret override. Not Wi-Fi ID. Not AP/BSSID. Not hard-coded `en0`. Not stored in Keychain. See §13 |
| 9 | Where does non-secret host identity live? | One tiny operator-local file outside git and outside the repository. See §14 |
| 10 | How does JOO talk to Keychain? | Production backend is macOS Security.framework via Python stdlib `ctypes` (`SecItemAdd` / `SecItemUpdate` / `SecItemCopyMatching` / `SecItemDelete`). Exact ctypes / CoreFoundation marshalling and OSStatus mapping is an Implementation Boundary Review freeze. See §15 |
| 11 | What fails closed? | Missing / denied / malformed secrets → `AUTH_FAILURE`. Missing host identity / underivable MAC without override → `VALIDATION_FAILURE`. No production getpass fallback. See §16 |
| 12 | Do existing public contracts change? | **No.** See §18 |
| 13 | How are secrets rotated / deleted? | `joo configure kb --replace` uses §7.5 pair-write verify / fail-closed reset. `--delete` succeeds only after both items are verified absent (§7.6). No plaintext backup. No old secret printed. See §19 |
| 14 | How is this tested without real credentials? | Fake Keychain backend + fake MAC deriver + fake host-identity file. See §20 |
| 15 | What later live follow-up is required? | Separately authorized controlled verification that Keychain retrieval still yields OAuth + SSQM2952 success. **Not authorized now.** See §21 |

---

## 7. Keychain strategy

### 7.1 Persistence authority

**Selected:** macOS Keychain.

This is the smallest macOS-native secret store. The operator machine is
macOS. A cross-platform abstraction is not required and is forbidden.

**Rejected**

| Option | Verdict |
| --- | --- |
| Plaintext `.env` | Forbidden — files and shell environment leak |
| JSON secret file | Forbidden |
| YAML secret file | Forbidden |
| Git-tracked config | Forbidden |
| Gitignored secret file inside the JOO repo | Forbidden — still a project file; easy to commit later |
| Per-run `getpass()` / `input()` during production collect | Forbidden after first-time setup |
| JOO-Automation state / prompts / results | Forbidden |
| FactStore | Forbidden |
| Snapshot | Forbidden |
| AI context / selector / catalog / CIA | Forbidden |
| Access-token Keychain item | Forbidden — token remains process-local transport cache only |
| Broker payload in Keychain | Forbidden |
| Third-party `keyring` / cloud KMS / enterprise vault | Forbidden |

### 7.2 Exact Keychain item model

**Selected: two generic-password items, not one JSON blob.**

| Item | Service | Account | Password payload |
| --- | --- | --- | --- |
| 1 | `joo.provider.kb_open_api` | `appKey` | the `appKey` value exactly as entered at setup |
| 2 | `joo.provider.kb_open_api` | `appSecret` | the `appSecret` value exactly as entered at setup |

Frozen identifiers:

```text
KEYCHAIN SERVICE:  joo.provider.kb_open_api
KEYCHAIN ACCOUNT:  appKey
KEYCHAIN ACCOUNT:  appSecret
KEYCHAIN CLASS:    generic password
KEYCHAIN:          default login keychain
```

Reasons two items is the smallest deterministic model:

1. Missing `appKey` and missing `appSecret` are independently detectable.
2. Keychain stores raw secret strings. JSON reconstruction stays in
   process memory, where the existing decoder already owns it.
3. Rotation replaces both items as a pair without inventing a blob schema.
4. A JSON blob in Keychain would mix encoding concerns into persistence.

**Rejected item models**

| Model | Verdict |
| --- | --- |
| One Keychain item whose password is the credential JSON blob | Rejected — encoding and persistence become one object |
| Service-per-secret (`joo.kb.appKey` as service) | Rejected — larger and less conventional |
| iCloud Keychain as a product requirement | Rejected — local login keychain is sufficient |
| Custom Keychain ACL product | Rejected unless Implementation Boundary Review proves it necessary for write/read without argv leakage |
| One item per `credential_ref` namespace / multi-provider vault | Rejected — general secrets platform |

### 7.3 Retrieval behavior

Runtime retrieval does **all** of the following, in this order:

1. Resolve the expected `credential_ref` (see §10.2).
2. Retrieve account `appKey` from service `joo.provider.kb_open_api`.
3. Retrieve account `appSecret` from the same service.
4. If either item is absent, unreadable, or access-denied: **stop**.
   Return through the existing supplier-failure path so Gateway emits
   `AUTH_FAILURE`. Do not retrieve further. Do not prompt.
5. If either retrieved payload is not a `str`, is empty, or is only
   surrounding whitespace: **stop** as `AUTH_FAILURE`.
6. Reconstruct the credential JSON in process memory (§10.3).
7. Return that JSON string from `CredentialSupplier`.
8. Do not log, print, persist, or interpolate either value.

Retrieved values are **not trimmed**. The existing decoder does not trim.
Setup must reject blank and surrounding-whitespace values before store so
runtime never needs to repair them.

### 7.4 Missing-secret behavior

| Condition | Runtime result |
| --- | --- |
| `appKey` item absent | `AUTH_FAILURE`, `detail=None` |
| `appSecret` item absent | `AUTH_FAILURE`, `detail=None` |
| Either item unreadable | `AUTH_FAILURE`, `detail=None` |
| Keychain access denied / user clicked Deny | `AUTH_FAILURE`, `detail=None` |
| Retrieved value empty or whitespace-only | `AUTH_FAILURE`, `detail=None` |
| Retrieved value not usable as `str` | `AUTH_FAILURE`, `detail=None` |

Do **not** fall back to `getpass()`, environment variables, files, or
sample placeholders.

### 7.5 First-time write and replacement — pair verification + fail-closed reset

First-time store and `--replace` share the same pair-write final-state
rule. Replacement remains explicit only:

```text
joo configure kb --replace
```

UX rules that remain frozen:

- Both intended `appKey` and `appSecret` values are collected as hidden
  input **before** any Keychain mutation.
- The old values are not printed.
- No plaintext backup is written.
- There is no rollback to previous plaintext values.
- There is no transactional Keychain platform.
- Host identity is unchanged unless the operator also requests host
  update (§19).
- First-time `joo configure kb` **fails closed** if either Keychain item
  already exists. It must not silently overwrite. That existence check
  happens **before** any write.

This is **pair verification + fail-closed reset only**. It is not a
two-phase Keychain protocol and not a new vault.

**Retracted claim**

This architecture **retracts** any earlier implication that runtime will
necessarily detect a mixed old/new pair by credential validation.

If `appKey` is overwritten and `appSecret` is not (or the reverse),
runtime retrieves two non-empty strings and reconstructs mixed old/new
client material. The existing decoder and Gateway path treat that as
valid credential JSON. The next collect will **not** fail closed on that
mixture. It will send the mixed pair.

Therefore configuration itself must not leave a mixed pair usable.

**Exact first-time write and replacement behavior**

1. Collect both intended new values in process memory first:
   `appKey`
   `appSecret`
2. Never print either value.
3. Attempt to write both Keychain items.
4. After both write attempts, retrieve both Keychain items again.
5. Compare the retrieved values in-process to the intended values.
6. Configuration success is lawful **only if**:
   - the `appKey` item exists
   - the `appSecret` item exists
   - retrieved `appKey` exactly equals intended `appKey`
   - retrieved `appSecret` exactly equals intended `appSecret`
7. If any write or verification fails after either item may have been
   mutated:
   - perform best-effort delete of **both** Keychain items
   - verify both items are absent
   - return visible configuration failure
   - instruct the operator to run first-time configuration again
     (`joo configure kb`)
   - do not leave a mixed old/new pair usable
8. No rollback to old plaintext values.
9. No backup secret file.
10. No transactional Keychain platform.

A mixed old/new pair must **never** be reported as successful
configuration.

### 7.6 Delete / reset — final-state verification

```text
joo configure kb --delete
```

Exact delete semantics:

1. Attempt deletion of the `appKey` item.
2. Attempt deletion of the `appSecret` item.
3. Already absent is lawful.
4. Retrieve/check both item identities after deletion.
5. Delete succeeds **only if both** items are confirmed absent.
6. If either item remains:
   - return visible failure
   - do not report reset success
   - do not silently ignore the surviving item

Additional frozen rules:

- Do not print secret values during deletion or verification.
- Do not delete the non-secret host-identity file unless the operator
  also requests host reset (§19).
- After a verified both-absent delete, normal runtime fail-closes with
  `AUTH_FAILURE` until the operator configures again.

---

## 8. First-time setup UX

### 8.1 Command semantics

**Target command:**

```text
joo configure kb
```

No JOO CLI, argparse entrypoint, or `joo` console script exists in the
accepted tree. This document therefore freezes **command semantics
only**. Exact shell / CLI wiring is deferred to Implementation Boundary
Review.

The semantic owner remains `ProviderGateway` / runtime ingress. Review
must not invent a second CLI platform, a JOO-Automation executor, or a
`run.sh` hijack to satisfy this identity.

Lawful later wiring options, in preference order:

1. Smallest ProviderGateway-owned setup entrypoint that implements these
   exact semantics.
2. If and only if a later accepted JOO CLI owner already exists at
   implementation time, occupy that CLI with these subcommands.

Do **not** implement the CLI in this authoring.

### 8.2 First-time workflow

`joo configure kb` is human-controlled and runs only in a real local TTY.

Exact steps:

1. If either Keychain item already exists: **stop**. Tell the operator to
   use `--replace`. Do not prompt for secrets.
2. Prompt `appKey` with hidden input. Never echo.
3. Prompt `appSecret` with hidden input. Never echo.
4. Reject blank values and values with surrounding whitespace. Do not
   store. Do not trim.
5. Write `appKey` and `appSecret` using the §7.5 pair-write rule
   (collect both in memory, write both, retrieve both, succeed only if
   both exist and both match; on any post-mutation failure delete both,
   verify both absent, fail visibly, instruct first-time configure
   again). Do not print either value.
6. Prompt visible non-secret `ip_addr` for `dataHeader.ipAddr`.
7. Reject blank, surrounding whitespace, and sample placeholders
   `127.0.0.1` and `0.0.0.0`.
8. Prompt optional visible non-secret MAC override. Empty input means
   "auto-derive at runtime" and writes **no** `mac_addr` key.
9. Write the operator-local host-identity file (§14).
10. Print only non-secret success status: Keychain items stored, host
    identity written, MAC mode `auto` or `override`. Never print secret
    values, never print Keychain passwords, never print a reconstructed
    credential JSON.

### 8.3 Setup security invariants

During setup:

- `appKey` / `appSecret` are never echoed.
- values are never written to the JOO repository, `/tmp` durable files,
  logs, git, prompts, or JOO-Automation results.
- values are never placed on a shell command line or in process argv.
- stdout / stderr of a successful setup contain no secret substrings.
- exception text contains no secret substrings.

A one-time macOS Keychain authorization dialog may appear when items are
created or first read. That is an OS permission prompt, not a JOO secret
prompt, and is lawful.

### 8.4 After setup

No per-run secret entry.

No per-run IP entry.

No per-run MAC entry.

---

## 9. Normal-run UX

### 9.1 Target

```text
JOO start
        → retrieve appKey / appSecret from Keychain automatically
        → derive / load host identity automatically
        → create existing credential JSON
        → existing ProviderGateway
        → Candidate B OAuth
        → KB factual reads
```

`JOO start` is a **target UX label**, not an existing CLI. No accepted
`JOO start` command exists. The frozen runtime property is:

```text
NORMAL RUN MANUAL SECRET INPUT: NO
NORMAL RUN MANUAL IP INPUT:     NO
NORMAL RUN MANUAL MAC INPUT:    NO
```

Composing the existing `KbOpenApiAdapter` with:

- the Keychain-backed `CredentialSupplier`
- host-identity-supplied `ip_addr` / `mac_addr`
- the existing `KbOpenApiLiveBrokerTransport`

and calling `collect()` once must require **zero human input**.

Exact process / CLI wiring of "JOO start" is deferred to Implementation
Boundary Review. This identity must not hijack `run.sh`, research
scripts, or Autopilot to create a start command.

### 9.2 What a normal run may lawfully do

- Read two Keychain items.
- Read the operator-local host-identity file.
- Derive the current locally assigned MAC of the active primary Wi-Fi
  interface if no override is configured.
- Reconstruct the credential JSON in process memory.
- Call the existing collect path.

### 9.3 What a normal run must not do

- Prompt for `appKey`, `appSecret`, IP, or MAC.
- Fall back to the pilot `getpass()` method.
- Look up a public IP on an external website.
- Append to FactStore.
- Place, modify, or cancel orders.
- Call market APIs.
- Start Autopilot.
- Print secrets or raw holdings.

---

## 10. Runtime credential flow

### 10.1 Occupancy, not redesign

```text
ExplicitBrokerCollectRequest
        │
        ▼
validate_explicit_broker_collect_request
        │
        ▼
resolve_outbound_credential(credential_ref)
        │   CredentialSupplier now backed by Keychain
        ▼
KbOpenApiLiveBrokerTransport.read(...)
        │   decode_kb_openapi_client_material
        ├── appKey     → POST /oauth2/token only
        └── appSecret  → POST /oauth2/token only
                │
                ▼
existing process-local Access Token cache
                │
                ▼
POST /api/v1/ssqm2952
                │
                ▼
existing broker_fact envelope
```

`ProviderInterface.collect`, `KbOpenApiAdapter.collect`,
`resolve_outbound_credential`, and `BrokerTransport.read(credential: str)`
remain unchanged.

### 10.2 `credential_ref` convention

`credential_ref` remains an opaque nonblank binding field. It is **not**
the secret.

This identity occupies `CredentialSupplier` with a Keychain-backed
callable constructed for **one** expected ref.

Production composition default:

```text
credential_ref = "kb_open_api"
```

This is a composition convention only. It reuses the reserved provider id
so a second identifier is not invented. It does not change
`ExplicitBrokerAdapterBinding`.

Rules:

- The supplier is constructed with the expected ref.
- If `collect` is called with a different ref: fail through the existing
  supplier-exception / `AUTH_FAILURE` path.
- Tests may inject any expected ref. They must not require the production
  default.
- The Keychain **service / account names do not include**
  `credential_ref`. There is one KB client-material pair on this machine.

### 10.3 Exact credential JSON reconstruction

After both Keychain payloads are retrieved as `str` values `app_key` and
`app_secret`, runtime reconstructs exactly:

```text
json.dumps(
    {"appKey": app_key, "appSecret": app_secret},
    ensure_ascii=False,
    separators=(",", ":"),
)
```

Frozen reconstruction invariants:

- keys are exactly `appKey` and `appSecret`
- key order in the emitted string is `appKey` then `appSecret`
- compact separators `("," , ":")`
- `ensure_ascii=False`
- no surrounding whitespace
- values are the Keychain payloads as stored; not trimmed; not coerced
- no extra keys
- no aliases (`app_key`, `client_id`, `grantType`, ...)

The existing transport decoder remains the only decoder. This identity
must not add a second parser and must not change
`decode_kb_openapi_client_material`.

### 10.4 Where reconstructed JSON may exist

Process memory of the JOO runtime only.

It may pass through:

1. Keychain-backed `CredentialSupplier` return value
2. `resolve_outbound_credential` / `apply_outbound_credential`
3. `BrokerTransport.read(..., credential=...)`
4. `decode_kb_openapi_client_material`

Then it must drop out of use. Decoded `appKey` / `appSecret` are used
only to build the Candidate B token request body.

### 10.5 Where reconstructed JSON must never exist

- logs
- stdout / stderr
- exception messages
- review artifacts / results
- prompts
- FactStore
- Snapshots
- AI / IRO / CIO
- selector / catalog / CIA
- the operator-local host-identity file
- git
- environment variables
- argv

---

## 11. Secret lifetime

| Material | Lifetime | Store |
| --- | --- | --- |
| `appKey` | Durable until replace/delete | macOS Keychain item `appKey` |
| `appSecret` | Durable until replace/delete | macOS Keychain item `appSecret` |
| reconstructed credential JSON | process-local only | memory |
| decoded `appKey` / `appSecret` | process-local only | memory |
| Access Token / `token_type` / `expires_at` | existing transport instance cache only | memory |
| broker payload / SSQM2952 body | existing collect envelope only | not Keychain; this slice does not persist it |

No secrets in:

- logs
- stdout
- exceptions
- results
- prompts
- FactStore
- snapshots
- AI
- selector / catalog / CIA
- host-identity file
- `config.yaml`
- JOO-Automation state

Do **not** store the access token in Keychain.

Do **not** store the broker payload in Keychain.

---

## 12. IP strategy

### 12.1 Decision

**Selected: configuration-backed non-secret `ip_addr` plus a separately
replaceable runtime loader.**

That value is passed to the existing constructor:

```text
KbOpenApiLiveBrokerTransport(..., ip_addr=<loaded>, mac_addr=<derived or override>, ...)
```

This occupies the already-required `dataHeader.ipAddr` field. It does
**not** create a public-IP discovery product.

### 12.2 Option review

| Option | Verdict |
| --- | --- |
| A. Derive from local interface / network context without external dependency | **Rejected as the default.** The proven live value was a public IP (`58.226.25.218`). Local-interface derivation typically yields RFC1918 / link-local / ULA and would invent a meaning for `ipAddr` that the pilot did not prove |
| **B. Persist a non-secret configured IP** | **Selected default source** |
| C. External public IP lookup | **Rejected** — extra network dependency; forbidden in the pilot; not justified by current evidence |
| D. Manual entry every run | **Rejected** as standing production UX |

### 12.3 Why configuration-backed, not discovery

The semantic meaning of KB `dataHeader.ipAddr` is **not proven**.

The pilot proved only that sending `58.226.25.218` worked for that call
without a separate console registration. That is not enough to build:

- an external public-IP website client
- a local-interface discovery product
- a "must register current public IP" JOO gate

The smallest lawful design is:

1. persist the non-secret value the operator wants sent as `ipAddr`
2. load it automatically on every normal run
3. keep the loader separately replaceable if later live evidence proves
   a different source

### 12.4 Separately replaceable loader

Runtime obtains `ip_addr` through a small injectable function owned by
this identity. Prefer a function over a named public port. A named
`IpAddrSupplier` Protocol is heavier than needed and is not required.

The production function reads the operator-local host-identity file
(§14).

Tests inject a fake function.

A later evidence-based replacement of the production supplier does **not**
require changing `KbOpenApiLiveBrokerTransport`, `CredentialSupplier`, or
Gateway collect.

That later replacement is **not** authorized by this document. In
particular, this document does **not** authorize:

- HTTP/HTTPS lookup to any IP-echo website
- STUN / third-party geo-IP
- guessing `127.0.0.1`, `0.0.0.0`, or the pilot IP

### 12.5 IP validation at configure and at load

`ip_addr` must be a nonblank `str` with no surrounding whitespace.

Configure and load reject:

- missing file / missing `ip_addr` key
- non-`str`
- empty or whitespace-only
- surrounding whitespace
- sample placeholders `127.0.0.1` and `0.0.0.0`

Do not invent a full IPv4/IPv6 product validator. The existing transport
already requires a nonblank `str`. This identity only prevents blank,
whitespace-padded, and known-placeholder values from being stored or
loaded.

Missing or invalid IP at normal run is `VALIDATION_FAILURE`. No prompt.

### 12.6 Public / NAT IP detectability — JOO does not detect it

JOO does **not** attempt to detect public / NAT IP changes.

Local interfaces generally cannot determine the externally visible
NAT / public IP. They typically yield RFC1918 / link-local / ULA.

JOO does **not** introduce an external IP-discovery service.

Configured `ip_addr` continues to be sent until:

a) the operator changes it using the host configuration workflow
   (`joo configure kb --host` or first-time configure), or
b) an existing live KB call fails

A live failure (`AUTH_FAILURE` / `PROVIDER_ERROR` / `TRANSPORT_FAILURE`
from the existing collect path) may trigger operator reconfiguration.

JOO must **not** silently invent or replace `ip_addr`.

The successful prior pilot does **not** prove a stale `ip_addr` will
always be accepted.

The successful prior pilot does **not** prove KB never validates IP.

Rejected:

- network watcher
- IP-registration subsystem
- automatic replacement of configured `ip_addr`

---

## 13. MAC strategy

### 13.1 Decision

**Selected: automatic derivation of the current locally assigned MAC of
the active primary Wi-Fi interface, with optional non-secret override.**

| Option | Verdict |
| --- | --- |
| A. Derive the current locally assigned MAC of the active primary Wi-Fi interface automatically | Selected as the **default** |
| B. Persist configured MAC only | Rejected as the only source — Private Wi-Fi Address is expected to change |
| **C. Auto-derive with optional configured override** | **Selected** |
| D. Manual entry every run | **Rejected** |

Do **not** store MAC in Keychain.

### 13.2 Why auto-derive is compatible with frozen evidence

The successful pilot MAC `02:c9:e7:ea:c3:8a` is the **local interface**
value and is locally administered. It is not the `networksetup` "Wi-Fi
ID" `ac:c9:06:24:5a:ba`. macOS Private Wi-Fi Address / interface changes
are expected. A stale configured MAC is a worse default than the current
local-interface address.

Override exists for two lawful cases only:

1. derivation fails (no Wi-Fi interface, permission, or unreadable
   address)
2. a later live call is rejected and the operator needs a specific
   `macAddr`

### 13.3 When derivation runs

Derive **once per process**, when composing
`KbOpenApiLiveBrokerTransport`.

Do **not** change the transport to re-query MAC on every HTTP request.
Do **not** make the transport a host-identity product.

If a non-secret `mac_addr` override is present in the host-identity file,
do **not** call the deriver.

### 13.4 Derivation constraints

The KB `macAddr` value must be:

```text
the CURRENT LOCALLY ASSIGNED MAC ADDRESS
of the ACTIVE PRIMARY WI-FI INTERFACE
```

That is the address the local interface itself reports (`ifconfig` /
`getifaddrs` for that interface). It is **not** interchangeable with
other MAC-like strings on the same machine.

**Pilot evidence — these two values are not interchangeable**

| Source | Value seen during the verified pilot | Lawful for `macAddr`? |
| --- | --- | --- |
| Local interface (`ifconfig` / interface MAC) | `02:c9:e7:ea:c3:8a` | **Yes — this is the proven live value** |
| `networksetup -getinfo Wi-Fi` field `Wi-Fi ID` | `ac:c9:06:24:5a:ba` | **No** |

Implementation Boundary Review must freeze active / primary Wi-Fi
interface **discovery**. This architecture freezes the source and the
rejections:

- use the **local interface MAC**
- a locally administered / Private Wi-Fi MAC is lawful
- do **not** reject a locally administered address merely because the
  first octet indicates it
- **DO NOT** use `networksetup` "Wi-Fi ID"
- **DO NOT** use AP BSSID
- **DO NOT** use router / AP hardware identity
- **DO NOT** hard-code `en0` as the only valid device name
- no automatic Ethernet / Bluetooth / Thunderbolt fallback
- optional configured `mac_addr` override remains the **only** fallback
- MAC remains outside Keychain
- no external network call
- injectable deriver so tests never touch real interfaces
- output format is the proven live format: lowercase colon-separated
  hex `xx:xx:xx:xx:xx:xx`. Official sample hyphenated form is not the
  proven live encoding and is not required

If automatic derivation fails and no override exists:

```text
VALIDATION_FAILURE
fail closed
```

### 13.5 Failure behavior

| Condition | Result |
| --- | --- |
| Override present and valid | use override; no derivation |
| Override absent; derivation succeeds | use derived MAC |
| Override absent; derivation fails | `VALIDATION_FAILURE`; fail closed |
| Override present but blank / whitespace / wrong type | `VALIDATION_FAILURE`; do not derive as a silent repair |

Sample placeholder `00:00:00:00:00:00` is rejected at configure and at
load.

---

## 14. Host identity configuration location

### 14.1 Decision

Non-secret host identity lives **outside Keychain** and **outside git**.

**Selected location:**

```text
~/.joo/kb_openapi_host_identity.json
```

This is one tiny operator-local file. It is **not** a configuration
platform, plugin registry, or multi-app settings system.

`~/.joo/` may exist solely to hold this file for this identity. Later
work must not treat that directory as an invitation to dump unrelated
state.

### 14.2 Option review

| Option | Verdict |
| --- | --- |
| Existing git-tracked `config.yaml` | **Rejected** — machine-specific host data must not enter git |
| New config file inside the JOO repository | **Rejected** |
| Deterministic OS-derived value for both IP and MAC | **Rejected** for IP (unproven). Selected for MAC default only |
| Keychain items for IP / MAC | **Rejected** — they are not secrets |
| JOO-Automation state | **Rejected** |
| Environment variables as the standing store | **Rejected** — per-shell and easy to leak into process listings |
| **Tiny operator-local file outside git** | **Selected** |

### 14.3 File contract

UTF-8 JSON object. Exact allowed keys:

| Key | Required | Meaning |
| --- | --- | --- |
| `ip_addr` | **yes** | non-secret value copied into transport `ip_addr` |
| `mac_addr` | no | non-secret override; omit for auto-derive |

Lawful examples of shape, not live values:

```text
{"ip_addr":"<configured>"}
```

```text
{"ip_addr":"<configured>","mac_addr":"<override>"}
```

Rules:

- extra keys are `VALIDATION_FAILURE`
- SECRET names (`appKey`, `appSecret`, `access_token`, `token`,
  `hts_pwd`, `ac_pwd`, `hd_pin_no`, and the rest of
  `SECRET_FIELD_NAMES`) as keys or as an invitation to store those
  values are `VALIDATION_FAILURE`
- the file must never contain reconstructed credential JSON
- missing file at normal run is `VALIDATION_FAILURE`
- Implementation Boundary Review should freeze restrictive directory /
  file permissions (`0700` / `0600` or equivalent) if the OS allows

### 14.4 What this file is not

- not a secrets vault
- not a KB payload store
- not a FactStore
- not a Snapshot
- not Autopilot state
- not git-tracked
- not inside `/Users/takesimple/Projects/JOO`

---

## 15. macOS Keychain interaction boundary

### 15.1 One production method, one test method

| Role | Method |
| --- | --- |
| Persistence authority | macOS Keychain generic-password items in §7.2 |
| Production backend | macOS Security.framework via Python stdlib `ctypes`, occupying a small `KeychainBackend` test seam |
| Test backend | in-memory fake `KeychainBackend` |
| Forbidden | `keyring`, PyObjC as a new dependency, `security add-generic-password -w <secret>`, any cloud vault, a general Keychain SDK, a runtime fallback between `security` CLI and Security.framework |

### 15.2 Production backend — Security.framework via ctypes

**Frozen production Keychain backend for the first implementation
slice:**

```text
macOS Security.framework via Python stdlib ctypes
```

Required Security.framework operations:

- `SecItemAdd`
- `SecItemUpdate`
- `SecItemCopyMatching`
- `SecItemDelete`

Rationale:

- secret stays in process memory
- no secret in argv
- no shell history
- no PyObjC requirement
- no third-party `keyring`
- no general Keychain SDK / platform

**Explicitly rejected for secret WRITE:**

```text
security add-generic-password -w <secret>
```

That form places secret material in argv. It is forbidden.

`security … -w` as the last option (TTY prompt) cannot satisfy the
"validate blank / surrounding whitespace in Python, then store" rule,
because JOO must see the value before write.

This document does **not** implement the ctypes backend.

Implementation Boundary Review must freeze exact ctypes /
CoreFoundation marshalling and OSStatus mapping.

Do **not** create a runtime fallback between the `security` CLI and
Security.framework.

Do **not** invent a general Keychain SDK.

Tests keep the in-memory fake.

### 15.3 Exact logical operations

| Operation | Meaning |
| --- | --- |
| add | first-time create of both items; fail closed before write if either already exists; then §7.5 pair-write + verify |
| update / replace | overwrite both items under the same §7.5 pair-write + verify / fail-closed reset |
| retrieve | `SecItemCopyMatching` both items; return raw password payloads as `str` |
| delete | §7.6: attempt both deletes; already-absent lawful; success only after both confirmed absent |

### 15.4 Hard leak rules

- no shell interpolation of secrets
- no secret in argv
- no secret in command history
- no secret on stdout / stderr of JOO
- no secret in exceptions, logs, or test failure messages
- production retrieve uses `SecItemCopyMatching`, not
  `find-generic-password -w`
- `security add-generic-password -w <secret>` is forbidden
- child `stderr`, if any later IBR-frozen diagnostic exists, must be
  treated as potentially sensitive and must not be forwarded to JOO logs

### 15.5 ProviderGateway import boundary

Accepted `ProviderGateway` production imports are currently limited to
`__future__`, `abc`, `dataclasses`, `datetime`, `json`, `typing`, and
`ProviderGateway`.

This identity will require a **narrow additive stdlib allowlist** for the
new modules only. Implementation Boundary Review must freeze the exact
names. Expected candidates, not yet authorized:

- `ctypes` for the Security.framework Keychain backend
- `os` / `pathlib` for `~/.joo/...`
- `getpass` **only** in the setup entrypoint, never on the collect path
- `subprocess` only if IBR later freezes it for **non-secret** host /
  interface discovery, never for secret write

Forbidden additions: `requests`, `httpx`, `keyring`, `AIAdapter`,
`FactStore`, `socket` used as a public-IP client.

The runtime collect path must not import `getpass` and must not be able
to prompt.

---

## 16. Error behavior

Reuse the existing failure classes. No second plane.

| Condition | Class | Interactive fallback |
| --- | --- | --- |
| Missing Keychain `appKey` item | `AUTH_FAILURE` | **None** |
| Missing Keychain `appSecret` item | `AUTH_FAILURE` | **None** |
| Keychain access denied | `AUTH_FAILURE` | **None** |
| Unreadable Keychain item | `AUTH_FAILURE` | **None** |
| Malformed retrieved value (empty, whitespace-only, non-str) | `AUTH_FAILURE` | **None** |
| Unexpected `credential_ref` | `AUTH_FAILURE` | **None** |
| Reconstructed JSON rejected by existing decoder | `AUTH_FAILURE` | **None** |
| Missing host-identity file | `VALIDATION_FAILURE` | **None** |
| Missing / invalid `ip_addr` | `VALIDATION_FAILURE` | **None** |
| MAC derivation failure and no valid override | `VALIDATION_FAILURE` | **None** |
| Invalid MAC override | `VALIDATION_FAILURE` | **None** |
| Host-identity file contains extra keys or SECRET names | `VALIDATION_FAILURE` | **None** |

`detail` remains `None` on these failures. Secrets must not be
interpolated into diagnostics.

Existing transport / OAuth / SSQM2952 mappings are unchanged.

Configure-time errors are operator-facing and non-secret (already
configured; blank input; Keychain write failed; pair-write verification
failed; delete did not leave both items absent). They are not Gateway
envelopes.

### 16.1 Host-identity failure emission

Host-identity validation belongs to **runtime composition before
constructing** `KbOpenApiLiveBrokerTransport`.

- missing / malformed `ip_addr`: `VALIDATION_FAILURE`
- MAC derivation failure with no override: `VALIDATION_FAILURE`

Do **not** redesign the `KbOpenApiLiveBrokerTransport` constructor.

Do **not** change ProviderGateway public APIs merely to carry these
failures.

The existing constructor already raises `ValueError` on blank `ip_addr`
/ `mac_addr`. Composition must validate first so those constructor
raises are not the product failure surface.

Exact composition-level result representation may be frozen later by
Implementation Boundary Review.

---

## 17. Security

### 17.1 Vocabularies — unchanged

**SECRET** — must never persist outside Keychain, and must never enter
AI, logs, envelopes, FactStore, or Snapshots:

- `appKey`
- `appSecret`
- `access_token`
- `token`
- `hts_pwd`
- `ac_pwd`
- `hd_pin_no`

plus the already-accepted names `password`, `api_key`, `apikey`,
`secret`, `authorization`, `refresh_token`, `credential`, `credentials`.

**SENSITIVE_ACCOUNT_METADATA** — unchanged:

- `ac_no`
- `gnl_ac_no`
- `gnl_ac_no1`
- `ac_nm`
- `rnmcno`
- `rsdnt_rno`
- `rprst_cs_no`
- `emp_no`

This identity does not persist account metadata.

### 17.2 Persistence rules

1. `appKey` and `appSecret` persist only as the two frozen Keychain
   items.
2. Access tokens do **not** persist in Keychain.
3. Broker payloads do **not** persist in Keychain.
4. Host identity is non-secret and lives only in the operator-local file.
5. No secret files are created in the JOO repository or `/tmp` as a
   standing store.
6. Existing residual secret scans remain in force on the collect path.
7. Test fixtures use only obviously fake material
   (`test-app-key`, `test-app-secret`, `test-access-token`).
8. This document contains no real credentials.

---

## 18. Existing contracts unchanged

Do **not** redesign:

- `BrokerTransport`
- `KbOpenApiLiveBrokerTransport` public constructor / `read` / `probe`
- `decode_kb_openapi_client_material`
- `KbOpenApiAdapter`
- `ExplicitBrokerAdapterBinding`
- `ExplicitBrokerParameterProfile`
- `ExplicitBrokerCollectRequest`
- `CredentialSupplier` public Protocol
- `resolve_outbound_credential` / `apply_outbound_credential`
- ProviderGateway envelope
- FactStore
- Snapshot
- IRO
- CIO

Prefer adapter / runtime composition around existing ports.

Allowed later implementation, after independent review and a separate
implementation authorization:

- new additive modules that implement `CredentialSupplier`
- new additive host-identity loader / MAC deriver
- setup entrypoint implementing §8 / §19 semantics
- additive tests and a narrow stdlib import allowlist
- README documentation of the new composition

Not allowed:

- changing collect signatures
- changing credential JSON keys
- changing Candidate B OAuth
- adding order or market paths
- adding FactStore append to this identity

---

## 19. Rotation and delete UX

Frozen semantics. Exact CLI wiring deferred with §8.

| Command semantic | Effect |
| --- | --- |
| `joo configure kb` | First-time store of both secrets + host identity. Fails if Keychain items already exist. Applies §7.5 pair-write verify / fail-closed reset |
| `joo configure kb --replace` | Hidden re-entry of both secrets. Apply §7.5 pair-write: verify both retrieved values match intended values. On any failure after mutation, best-effort delete both, verify both absent, fail visibly, instruct first-time configure. No plaintext backup. No old secret printed. No rollback to old values. Host identity unchanged |
| `joo configure kb --delete` | Apply §7.6: attempt delete of both items; already-absent is lawful; succeed only after both item identities are confirmed absent. Remaining item is visible failure, not success. No secret printed. Host identity unchanged |
| `joo configure kb --host` | Re-prompt non-secret IP and optional MAC override only. Does not read or write Keychain secrets |
| `joo configure kb --host --reset` | Delete the operator-local host-identity file only. Next run fail-closes on missing host identity until `--host` or full configure |

`--replace` plus `--host` in one invocation is lawful and updates both
planes without printing secrets.

There is no "print current secret" command.

There is no "export to file" command.

---

## 20. Test invariants

Future tests must prove the following **without real credentials, without
the real login Keychain, and without live KB**.

| # | Invariant |
| --- | --- |
| 1 | Fake Keychain backend can store and retrieve two items |
| 2 | Successful credential load reconstructs exact compact JSON `{"appKey":"...","appSecret":"..."}` |
| 3 | Missing `appKey` item → `AUTH_FAILURE` |
| 4 | Missing `appSecret` item → `AUTH_FAILURE` |
| 5 | Access denied / unreadable item → `AUTH_FAILURE` |
| 6 | Malformed retrieved values → `AUTH_FAILURE` |
| 7 | Unexpected `credential_ref` → `AUTH_FAILURE` |
| 8 | No secret appears in argv, stdout, stderr, logs, or exception text |
| 9 | Existing ProviderGateway public collect API is unchanged |
| 10 | Existing `CredentialSupplier` Protocol is unchanged |
| 11 | Existing decoder still accepts only `appKey` / `appSecret` |
| 12 | MAC auto-derivation is used when override is absent |
| 13 | MAC override is used and the deriver is not called |
| 14 | Missing MAC (derivation failure, no override) fail-closes `VALIDATION_FAILURE` |
| 15 | Configured `ip_addr` is passed to the existing transport constructor |
| 16 | Missing / invalid IP fail-closes `VALIDATION_FAILURE` |
| 17 | No external public-IP network lookup occurs |
| 18 | No secret files are written under the JOO repository |
| 19 | No FactStore / Snapshot / AI secret path exists |
| 20 | Normal runtime composition requires zero interactive input |
| 21 | First-time configure refuses to overwrite existing Keychain items |
| 22 | `--replace` applies §7.5 pair-write verify; mixed old/new is never reported as successful configuration; no old or new secrets emitted |
| 23 | `--delete` succeeds only after both items are verified absent; already-absent is lawful; a surviving item is failure |
| 24 | Host-identity extra keys / SECRET names fail closed |
| 25 | Sample placeholder IP / MAC values are rejected |
| 26 | Access token is not written to the fake Keychain |
| 27 | CI does not require macOS Keychain authorization or network access to `developer.kbsec.com` |
| 28 | Partial first-time `appKey` / `appSecret` write is not successful configuration |
| 29 | Partial replace is not successful configuration |
| 30 | Partial delete is not successful reset |
| 31 | Post-write pair verification: both items exist and retrieved values exactly equal intended values |
| 32 | Post-delete both-absent verification: delete succeeds only when both item identities are confirmed absent |
| 33 | Failed pair mutation triggers best-effort deletion of both items, then verifies both absent |
| 34 | A mixed old/new pair is never reported as successful configuration |
| 35 | No secret in argv |
| 36 | No secret in stdout / stderr |
| 37 | No secret in exception text |
| 38 | MAC deriver uses the local-interface MAC of the active primary Wi-Fi interface |
| 39 | Locally administered / Private Wi-Fi MAC is accepted |
| 40 | `networksetup` "Wi-Fi ID" is rejected as a MAC source |
| 41 | AP / BSSID is rejected as a MAC source |
| 42 | Hard-coded `en0` is not the only interface-discovery strategy |
| 43 | Configured MAC override is used and the deriver is not called |
| 44 | Derivation failure without override fails closed as `VALIDATION_FAILURE` |
| 45 | Normal runtime remains zero-interactive-input |
| 46 | Existing ProviderGateway public API remains unchanged |

A caller-sequence test may compose:

```text
fake Keychain supplier + fake host identity + fake HTTP transport
        → KbOpenApiAdapter.collect
        → existing success / AUTH_FAILURE / VALIDATION_FAILURE
```

That test does not authorize live KB and does not append FactStore.

---

## 21. Controlled follow-up pilot

A later controlled live verification should prove:

- no manual `appKey` / `appSecret` entry on the collect run
- Keychain runtime retrieval works
- Candidate B OAuth still succeeds
- SSQM2952 still succeeds
- no secret output
- no new persistence of secrets or holdings
- no order path

That follow-up is a **separate authorization**.

This document does **not** authorize:

- running that pilot
- any live KB call
- any real `appKey` / `appSecret` being pasted into chat, prompts, or
  results
- Autopilot
- FactStore append
- implementation of this identity

---

## 22. Non-responsibilities

This identity / slice must **not**:

1. Persist holdings to FactStore.
2. Normalize `Record1` into Snapshot-compatible facts.
3. Integrate Portfolio Snapshot or Market Snapshot.
4. Call domestic cash TRs (`SSQM0004` / `SWQN2302`).
5. Call buying-power TRs (`SSQM1802`).
6. Call overseas holdings TRs.
7. Call market data TRs or occupy `MarketTransport`.
8. Add a scheduler or 24/7 automation.
9. Execute orders (`SSAM*` or any write TR).
10. Perform automatic trading.
11. Mutate Autopilot.
12. Build a general enterprise secrets platform / general secrets
    manager / Keychain daemon / new credential server.
13. Build a cross-platform credential abstraction.
14. Implement Architecture State Resolver.
15. Change selector / catalog / CIA.
16. Store access tokens in Keychain.
17. Store broker payloads in Keychain.
18. Create plaintext secret files.
19. Look up public IP through an external website, detect public / NAT
    IP changes, run a network watcher, or invent an IP-registration
    subsystem.
20. Require per-run typing of IP, MAC, `appKey`, or `appSecret`.
21. Hijack `run.sh`, research scripts, or JOO-Automation as the secret
    store or start command.
22. Redesign `BrokerTransport`, `KbOpenApiAdapter`,
    `CredentialSupplier`, Gateway envelope, FactStore, Snapshot, IRO, or
    CIO.
23. Invent a numbered milestone for this work.
24. Use `networksetup` "Wi-Fi ID", AP / BSSID, or router / AP hardware
    identity as `macAddr`.
25. Hard-code `en0` as the only valid Wi-Fi device name.
26. Write secrets with `security add-generic-password -w <secret>`.
27. Create a runtime fallback between the `security` CLI and
    Security.framework.
28. Build a broad CLI framework.

---

## 23. Implementation boundary

### 23.1 This document does not authorize implementation

**DO NOT IMPLEMENT THIS NOW.**

**IMPLEMENTATION: NOT AUTHORIZED**

**LIVE KB: NOT AUTHORIZED**

If this architecture is independently re-reviewed and accepted, a later
Implementation Boundary Review must freeze, before any production code:

1. exact setup entrypoint wiring for the frozen command semantics
2. exact ctypes / CoreFoundation marshalling and OSStatus mapping for
   the frozen Security.framework production backend (`SecItemAdd`,
   `SecItemUpdate`, `SecItemCopyMatching`, `SecItemDelete`). No
   `security -w <secret>` write path. No runtime fallback to the
   `security` CLI
3. exact active / primary Wi-Fi interface discovery and local-interface
   MAC query. Not hard-coded `en0` as the only name. Not
   `networksetup` "Wi-Fi ID". Not AP / BSSID
4. exact additive stdlib import allowlist
5. exact new module paths under `ProviderGateway`
6. exact production `credential_ref` construction site
7. test module names for the fake backends
8. exact composition-level `VALIDATION_FAILURE` representation for
   host-identity failures before transport construction

Until that review, no runtime Python may be modified.

Preferred later implementation remains a **narrow operational slice**:

1. small Keychain module / functions
2. small host-identity loader
3. narrow configure entrypoint semantics
4. runtime composition into existing ProviderGateway contracts

That later implementation must continue to reject a broad CLI framework,
a general secrets manager, a network discovery service, a configuration
platform, a scheduler, a cross-platform credential abstraction, a
Keychain daemon, a new credential server, automatic trading, market
integration, FactStore integration, and Snapshot integration.

### 23.2 Later implementation allowlist (not authorized now)

| Path | Later authorized mutation |
| --- | --- |
| `ProviderGateway/auth/kb_openapi_keychain.py` | **New file.** Keychain backend + JSON reconstruction + `CredentialSupplier` occupancy |
| `ProviderGateway/auth/kb_openapi_host_identity.py` | **New file.** IP load + MAC derive/override |
| setup entrypoint path frozen by IBR | **New file only after IBR.** Implements §8 / §19 semantics |
| `ProviderGateway/tests/*` | Additive fake-backend tests |
| `ProviderGateway/README.md` | Document Keychain / host-identity composition; do not rewrite frozen collect contracts |
| `ProviderGateway/tests/test_boundary.py` | Narrow additive stdlib allowlist only, if IBR requires it |

### 23.3 Must remain unchanged

- `ProviderInterface.collect` signature and request union
- `KbOpenApiAdapter` public collect / health behavior
- `KbOpenApiLiveBrokerTransport` public `read` / `probe` / decoder
- `CredentialSupplier` Protocol
- `ExplicitProviderPayloadEnvelope` fields
- `ExplicitBrokerCollectRequest` / binding types
- Candidate B OAuth serialization
- SSQM2952 request contract
- FactStore append / retrieval semantics
- `PortfolioSnapshotProducer` / `MarketSnapshotProducer`
- IRO-M1 / IRO-M2
- Automation / CIA / selector documents and runtime
- Out-of-boundary untracked documents listed in §1
- Git history, tags, remotes

---

## 24. Strategic product position

JOO remains an operational investment command center. This identity sits
**beside** the already-proven factual path, not above it:

```text
one-time configure
        │
        ├── Keychain (appKey, appSecret)
        └── ~/.joo/kb_openapi_host_identity.json
                │
                ▼
normal run composition
                │
                ▼
KB Securities Open API
        │  raw verified facts (already proven: SSQM2952)
        ▼
existing ProviderGateway broker_fact envelope
        │
        ▼
later additive normalization / FactStore / Snapshot / CIO
        (OUT OF THIS SLICE)
```

KB factual truth remains below AI interpretation.

AI must never receive `appKey`, `appSecret`, or access tokens.

Unknown / failed credential or host-identity reads remain explicit
fail-closed states. They must not degrade into empty holdings or a
prompt loop.

---

## 25. Document authority

- This document is the canonical architecture for the unnumbered
  identity **KB OpenAPI Runtime Credential Configuration**.
- It is subordinate to the Constitution and to accepted PF-M1, PF-M2,
  PF-M3, PF-M4, the KB OpenAPI Live Factual Pipeline, IRO-M1, and
  IRO-M2 contracts in those contracts' scopes.
- It consumes the post-commit verification and the controlled live
  pilot authorization / verification as sequencing and evidence
  authority only.
- It does not authorize implementation, live KB calls, live Autopilot,
  stage, commit, tag, or push.
- Next required action is **Independent Architecture Re-Review**.

```text
OWNER:                          ProviderGateway
IDENTITY:                       KB OpenAPI Runtime Credential Configuration
KEYCHAIN STRATEGY:              two generic-password items
                                service=joo.provider.kb_open_api
                                accounts=appKey, appSecret
KEYCHAIN BACKEND:               Security.framework via ctypes
                                IMPLEMENTATION NOT AUTHORIZED
PAIR REPLACE:                   verify both values;
                                on any failure delete both and verify absent
DELETE:                         success only when both items verified absent
FIRST-TIME SETUP UX:            joo configure kb  (semantics; CLI wiring deferred)
NORMAL-RUN UX:                  zero interactive input
NORMAL-RUN SECRET ENTRY:        NO
IP STRATEGY:                    configuration-backed non-secret ip_addr
                                + separately replaceable loader
                                no external lookup
                                no per-run input
                                no network-change detector
                                stale value sent until --host or live-call failure
MAC STRATEGY:                   current locally assigned
                                active-primary-Wi-Fi interface MAC
                                + optional non-secret override
                                not stored in Keychain
                                not Wi-Fi ID
                                not AP/BSSID
                                not hard-coded en0
RUNTIME CREDENTIAL FLOW:        Keychain → compact JSON → existing
                                CredentialSupplier → existing decoder
SECRET LIFETIME:                Keychain persistent;
                                JSON / decoded values / token process-local
FAIL-CLOSED CONDITIONS:         missing/denied/malformed secrets → AUTH_FAILURE
                                missing host identity / MAC → VALIDATION_FAILURE
                                host-identity validation at composition
                                before transport construction
                                no production prompt fallback
EXISTING CONTRACTS UNCHANGED:   yes
IMPLEMENTATION BOUNDARY:        NOT AUTHORIZED
TEST INVARIANTS:                fake backends; no real credentials; no live KB
                                + pair-write / pair-delete / MAC-source
                                invariants in §20
CONTROLLED FOLLOW-UP PILOT:     later; NOT AUTHORIZED NOW
NON-RESPONSIBILITIES:           §22
```
