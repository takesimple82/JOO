# Milestone Selection Input Supply Architecture

## Status and identity

- Status: Architecture authored for independent review; first-slice
  supply freeze only
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Development infrastructure** — not an investment-domain plane
- Capability: **Milestone Selection Input Supply**
- Owner: **Selector Input Supply**
- Milestone ID: **UNRESOLVED**
- This document does **not** invent or assign `Automation-M4`,
  `Autopilot-M1`, `M55+`, `PF-M5`, `Automation-M3`, `IRO-M3`,
  `IRO-M4`, Architecture State Resolver, or any other manufactured
  successor identity
- Authorizing direction review: Architecture Review Board
  (`~/JOO-Automation/results/milestone_selection_input_supply_architecture_review/latest.md`)
  — **FINAL DECISION: SELECTOR INPUT ARCHITECTURE READY**
- Production location (later, not created by this document): the
  already-specified Autopilot host artifact
  `state/<repository_id>/milestone_selection_input.json` under
  JOO-Automation. Not a JOO investment package, not an extension of
  `joo_auto`, and not a new resolver module
- Repository boundary for this document: architecture authoring only;
  this document alone authorizes no production code, test, package
  change, schema module, configuration, run artifact, selector-input
  file, Supervisor prompt rewrite, Autopilot runtime change, or Git
  history mutation

This document freezes the **minimum contract** that lawfully supplies
the already-implemented Milestone Selection Engine Runtime Integration
with one explicit, repository-scoped selector input file.

It answers only:

> Who may author `state/<repository_id>/milestone_selection_input.json`,
> what exact first-slice bytes are lawful, and how can that authoring
> remain explicit, repository-scoped, and deterministic without becoming
> a resolver, parser, ranking engine, or successor selector?

It does **not** answer:

> What milestone should be built next, and may Autopilot now continue?

This document does **not** redesign:

- Milestone Selection Engine first-slice models or cardinality rules
- Milestone Selection Engine Runtime Integration
- Autopilot Repository Target Abstraction
- Autopilot v5 safe-fastpath
- Supervisor action vocabulary (`RUN_REVIEW` / `COMMIT` / `STOP`)
- `COMMIT READY` single-consumption
- `next_action` schema
- JOO investment-domain architecture

Implementation is **not** authorized.

Human materialization of the selector input file is **not** authorized
by this document.

PF-M5 is **not** authorized.

Automation-M3 is **not** authorized.

Architecture State Resolver remains **deferred**.

The first slice must remain **smaller than a general Architecture
State Resolver**.

---

## 1. Purpose

Runtime Integration already consumes exactly one file:

```text
state/<repository_id>/milestone_selection_input.json
```

The Milestone Selection Engine already classifies an explicit
`MilestoneSelectionInput`. The runtime adapter already loads and
type-checks that file. The adapter does not author it.

Live `JOO_AUTOMATION` currently has **no** such file. The live
result is therefore:

```text
STOP(MISSING_SELECTOR_INPUT)
stop_source=INTEGRATION
selected_identity=none
```

That result is expected and correct. Absence is not a bug in the
engine, the adapter, Repository Target, Supervisor, or Autopilot.

The unique remaining architectural gap is **lawful authoring** of the
already-specified artifact.

This architecture adds exactly one responsibility:

**Selector Input Supply owns the authoring contract of the explicit
selector input artifact.**

It does not own eligibility classification.
It does not own runtime consumption.
It does not own repository binding.
It does not observe git.
It does not invent a successor.

The architectural benefit of the first slice is not that
`JOO_AUTOMATION` starts building a successor. The benefit is that the
already-wired supply → load → classify chain can later be completed
with an explicit closed world, without inference.

---

## 2. Context

### 2.1 Independently re-verified checkpoint

This architecture is authored only after independent re-verification.
Material state matches the authorizing direction review.

**JOO** (`/Users/takesimple/Projects/JOO`)

| Check | Value |
| --- | --- |
| Path | `/Users/takesimple/Projects/JOO` |
| Branch | `feature/stage2-provider-runtime` |
| HEAD | `0851a106ff206b0fe4b6a370fc10f8908dc6cdce` |
| Exact tag at HEAD | `v7.15-stage5-milestone-selection-engine-runtime-integration-architecture` |
| HEAD subject | Add Milestone Selection Engine runtime integration architecture |
| Tracked / staged | Clean / empty |

`git describe --exact-match HEAD` without `--tags` fails because the
tag is lightweight. `git tag --points-at HEAD` and
`git describe --tags --exact-match HEAD` resolve the expected tag on
this HEAD. This is the same non-material lightweight-tag fact already
recorded by prior Stage 5 architecture documents. It is not a
checkpoint mismatch.

Intentionally untracked JOO OOB files exist and remain
**non-authoritative**:

- `docs/JOO_PRODUCT_ARCHITECTURE.md`
- `docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md`

This architecture must not consume, modify, stage, or treat either OOB
file as successor identity, selector input, ranking, or commit
authority.

**JOO-Automation** (`/Users/takesimple/JOO-Automation`)

| Check | Value |
| --- | --- |
| Path | `/Users/takesimple/JOO-Automation` |
| Branch | `main` |
| HEAD | `4e227411080276a71e5a9af0870618b7d391772e` |
| HEAD subject | Add Milestone Selection Engine runtime integration |
| Exact tag at HEAD | none |
| Tracked / staged | Clean / empty |

Untracked host machinery (`prompts/`, `state/`, `backups/`) is
expected operational tree, not a dirty tracked tree.

### 2.2 Current live selector state

Namespaced first live selector-owned cycle after runtime integration:

| Fact | Observed |
| --- | --- |
| Target | `JOO_AUTOMATION` |
| Command surface | `joo autopilot --repo JOO_AUTOMATION` |
| Branch / HEAD | `main` / `4e227411080276a71e5a9af0870618b7d391772e` |
| Selector input | **ABSENT** |
| Runtime decision | `STOP` |
| `stop_reason` | `MISSING_SELECTOR_INPUT` |
| `stop_source` | `INTEGRATION` |
| `selected_identity` | none |
| `input_identity` | none |
| Engine classification | did not run |
| Supervisor `next_action` | `STOP` |
| Unused namespaced `COMMIT READY` | none |

`state/JOO/milestone_selection_input.json` is also absent.
`state/milestone_selection_input.json` must not exist and must not be
created.

This is the expected first live selector-owned result. The remaining
gap is input supply, not selection, not consumption, and not
repository targeting.

### 2.3 Frozen predecessors that this document must not reopen

| Authority | Status | Constraint on this freeze |
| --- | --- | --- |
| Milestone Selection Engine architecture | Frozen at JOO `v7.13` | Explicit caller-supplied `MilestoneSelectionInput` only; 0 / 1 / N; no ranking, filesystem, git, Markdown, or LLM |
| Milestone Selection Engine first slice | Committed at `0c44ec4`; package `milestone_selection_engine/` | Public API unchanged |
| Repository Target Abstraction architecture | Frozen at JOO `v7.14` | Target binding precedes selection; supported IDs are `JOO` and `JOO_AUTOMATION` only |
| Repository Target implementation | Live | Not redesigned |
| Milestone Selection Engine Runtime Integration architecture | Frozen at JOO `v7.15` | Reads exact namespaced file; adapter loads and validates only; missing file is `STOP(MISSING_SELECTOR_INPUT)` |
| Runtime Integration implementation | Committed at `4e22741`; live-verified | Not redesigned |
| Autopilot v5 safe-fastpath | Live | Exact-path staging, dirty-tree fail-closed, repository-scoped `COMMIT READY`, tag/push authorization, OOB safety, `next_action` safety, no history rewrite |
| Supervisor vocabulary | `RUN_REVIEW` / `COMMIT` / `STOP` only | Consumes a decision; must not invent records |
| `COMMIT READY` | Autopilot-owned, single-consumption, repository-scoped | Unused authority blocks selector invocation; never becomes first-slice engine input |
| Architecture State Resolver | Deferred and absent | Must not be invented here |

Runtime Integration §9 already froze the **consumption** source. It
left writers as humans or later separately authorized record authors
and kept Architecture State Resolver deferred. This document freezes
only that remaining writer / supply contract.

### 2.4 What is still missing

```text
RepositoryTarget is frozen and live
Milestone Selection Engine is frozen, implemented, and isolated
Runtime Integration is frozen, implemented, and live-verified
Architecture State Resolver is absent
Explicit selector input artifact is absent
Selector Input Supply contract is the unique remaining freeze
```

This document freezes only the missing authoring contract. It does not
replace the deferred resolver.

---

## 3. Owner

The exact owner is:

**Selector Input Supply**

Milestone ID remains:

**UNRESOLVED**

This owner is responsible only for the lawful authoring contract of
the explicit selector input artifact.

### 3.1 What this owner may decide

Selector Input Supply may freeze:

- who may write the already-specified file
- which exact first-slice object is lawful
- which later record kinds remain explicit rather than inferred
- repository isolation of the write target
- the prohibition on inference, ranking, and automatic mutation

### 3.2 What this owner must not become

Selector Input Supply must **not** become:

| Rejected identity | Why |
| --- | --- |
| Milestone Selection Engine | Classifies supplied records. Must remain author-free |
| Architecture State Resolver | Later live-fact normalizer. Deferred and not this slice |
| Autopilot | Executor and safety owner. Must not invent candidates |
| Supervisor | Intra-milestone LLM actor. Must not invent records |
| Repository Target | Binds the repository. Does not author the milestone set |
| Roadmap parser | Prose is not a record source |
| Ranking engine | Cardinality remains the only selection rule |
| LLM successor selector | Discovery and preference are forbidden |

This is a development-infrastructure owner. It is not a numbered
milestone. It is not `Automation-M4`, `Autopilot-M1`, or Architecture
State Resolver.

### 3.3 Ownership that does not move

| Actor | Still owns | Must not gain |
| --- | --- | --- |
| Selector Input Supply | Lawful authoring contract of the explicit input file | Eligibility; git observation; repository choice |
| Human | First-slice writer of the exact frozen bytes, after later materialization authorization | Informal chat as autonomy |
| Milestone Selection Engine | Eligibility cardinality; `CONTINUE` / `STOP` | File authoring |
| Runtime Adapter | Load, type-check, hash raw bytes, persist decision | File authoring |
| Autopilot Repository Target | Allowlisted target bind; `AutopilotExecutionContext` | Successor identity or catalog authorship |
| Supervisor | Intra-milestone `RUN_REVIEW` / `COMMIT` / `STOP` for an already selected identity | Independent successor choice or record invention |
| Autopilot runtime | Safety gates; exact-path staging; `COMMIT READY` single-consumption; tag/push authorization | Computing, ranking, or writing selector input |
| Architecture State Resolver | Nothing yet. Deferred | Hidden selector or automatic catalog mutation |
| `COMMIT READY` / commit-review | Unused versus consumed commit authority | Successor identity or `blocking_evidence` authorship in this slice |

---

## 4. Exact runtime artifact

### 4.1 Already-frozen filename

The runtime artifact remains exactly:

```text
state/<repository_id>/milestone_selection_input.json
```

under the Autopilot host (`~/JOO-Automation`).

This document does not relocate that path. Runtime Integration already
froze it. This architecture only freezes who may write it and what
first-slice bytes are lawful.

### 4.2 Exact top-level JSON keys

The file must be a JSON object whose keys are **exactly**:

```text
records
dependencies
blocking_evidence
```

No other top-level key is lawful.

The live adapter requires those three keys and no others. Extra keys
are `INVALID_SELECTOR_INPUT`. Missing keys are
`INVALID_SELECTOR_INPUT`.

### 4.3 No envelope fields

The file is the Milestone Selection Engine payload. It is not a
runtime decision envelope.

Forbidden top-level fields include, at least:

- `repository_id`
- `generated_at`
- `catalog_version`
- `priority`
- `score`
- `rank`
- `source_document`
- `next_milestone`

Repository identity is carried by the **state namespace**, not inside
the MSE payload.

`generated_at` and `cycle_id` remain on
`MilestoneSelectionRuntimeDecision`. They must not migrate onto the
input file.

### 4.4 Collection meanings

| Key | Exact meaning | First-slice content |
| --- | --- | --- |
| `records` | Finite JSON array of `MilestoneRecord` objects | `[]` |
| `dependencies` | Finite JSON array of `MilestoneDependency` objects | `[]` |
| `blocking_evidence` | Finite JSON array of `BlockingEvidence` objects | `[]` |

Later expansion, if separately authorized, may add named objects
inside those arrays. It may not add new top-level keys.

### 4.5 Later record field contract, not first-slice content

If a later catalog-expansion authorization adds a record, that record
must deserialize onto the existing engine types. This document does
not authorize those records. It only preserves the already-frozen
shapes so a later expansion cannot invent a second schema.

A later `MilestoneRecord` object, if authorized, remains exactly:

| Field | Rule |
| --- | --- |
| `identity` | Exact opaque non-blank `str`. No trim. No case-fold |
| `completed` | Exact Boolean recorded fact |
| `deferred` | Exact Boolean recorded policy fact |
| `oob` | Exact Boolean recorded authority fact |
| `superseded` | Exact Boolean recorded replacement fact |
| `architecture_frozen` | Exact Boolean metadata. No eligibility effect |

A later `MilestoneDependency` object, if authorized, remains exactly:

| Field | Rule |
| --- | --- |
| `dependent` | Exact opaque non-blank `str` |
| `prerequisite` | Exact opaque non-blank `str` |
| `dependency_type` | Exactly `PREREQUISITE` |
| `source_identity` | Opaque non-blank evidence identity |

A later `BlockingEvidence` object, if authorized, remains the existing
closed engine kind/scope contract. This first slice authorizes **no**
blocking-evidence objects.

The supplier must not add ranking, score, preference, source-document,
or next-milestone fields to any of these objects.

---

## 5. Exact first-slice payload

### 5.1 Frozen object

The first authorized first-slice object is **exactly**:

```json
{
  "records": [],
  "dependencies": [],
  "blocking_evidence": []
}
```

This is an explicit closed world.

It introduces zero milestone identities.
It introduces zero prerequisite edges.
It introduces zero blocking-evidence objects.

### 5.2 Exact first-slice bytes

Later materialization, if separately authorized, must write one exact
UTF-8 byte sequence. Formatting is material.

The only authorized first-slice file body is the following UTF-8 text
with LF newlines and exactly one trailing newline after the closing
brace:

```text
{
  "records": [],
  "dependencies": [],
  "blocking_evidence": []
}
```

Constraints on those bytes:

- encoding is UTF-8
- newlines are LF only
- indentation is exactly two spaces
- one space follows each colon
- empty collections are exactly `[]`
- no BOM
- no trailing spaces
- no additional keys, comments, or whitespace variants
- exactly one trailing newline after `}`

Any other formatting is a different `input_identity`. This
architecture does not authorize a canonicalizer to make variants
equivalent.

### 5.3 Absent file versus explicit empty file

| Condition | Lawful result | Engine invoked? |
| --- | --- | --- |
| File absent | Integration `STOP(MISSING_SELECTOR_INPUT)` | No |
| File present with the frozen empty object | Engine `STOP(NO_ELIGIBLE_MILESTONE)` | Yes |
| File present but not the exact engine payload | Integration `STOP(INVALID_SELECTOR_INPUT)` | No |

Absence is **not** an implicit empty world.

An explicit empty file is the only way to ask the engine to classify
an empty record set.

This distinction is the first-slice proof. It must not be collapsed.

### 5.4 What the empty object is not

The frozen empty object is not:

- authorization of a successor
- a unique eligible identity
- an implicit `CONTINUE`
- a ranking of remaining work
- a resolver observation
- a repair of `MISSING_SELECTOR_INPUT` by inventing records

It is a successful fail-safe upgrade from missing input to an explicit
closed world whose lawful classification is
`STOP(NO_ELIGIBLE_MILESTONE)`.

---

## 6. First-slice owner / writer

### 6.1 Writer

First-slice writer:

**HUMAN**

The human may author only the exact frozen first-slice bytes, and only
after a later implementation / materialization authorization.

This document does **not** authorize that write.

### 6.2 Forbidden writers

The following actors must not write
`milestone_selection_input.json` in this slice:

| Actor | Why forbidden |
| --- | --- |
| Autopilot | Executor. Must not invent or persist candidates |
| Supervisor | LLM actor. Must not invent records |
| Runtime Adapter | Loader and type-checker only |
| Milestone Selection Engine | Side-effect-free classifier. Filesystem-free |
| Architecture State Resolver | Absent. Deferred |
| Review pipeline | Detection owner, not catalog author |
| Informal chat / untracked prompt | Not a machine-readable record |
| Silence | Never authorization |

### 6.3 Adapter remains a loader

The already-implemented runtime adapter:

- locates `state/<repository_id>/milestone_selection_input.json`
- hashes the raw bytes
- deserializes exact engine types
- does not author, repair, pretty-print, or overwrite the file

This architecture does not change that adapter unless a later board
separately authorizes an adapter change. No such change is required
for the empty first-slice object.

---

## 7. Record ownership for later expansion

This section freezes responsibility boundaries. It does **not**
authorize expansion beyond the empty first-slice object.

| Information | Kind | First-slice treatment | Later producer, if separately authorized |
| --- | --- | --- | --- |
| Milestone identity exists in the closed world | Policy / authority | Not present. Zero identities | Explicit human / separately authorized artifact only |
| `completed` | Recorded fact | Not present | Human-attested Boolean in this slice architecture only. Later Architecture State Resolver may become the factual producer only after separate architecture approval |
| `deferred` | Explicit policy record | Not present | Explicit policy record only |
| `oob` | Explicit policy record | Not present | Explicit policy record only |
| `superseded` | Explicit policy record | Not present | Explicit policy record only |
| `architecture_frozen` | Explicit metadata record | Not present | Explicit metadata record only. Frozen is not completed and not next |
| `dependencies` | Explicit `PREREQUISITE` edges only | Empty array | Written edges only. Silence is not an edge |
| `blocking_evidence` | Normalized detection evidence | **Must remain empty** | Must not be auto-converted from git state, unused `COMMIT READY`, dirty tree, or review tokens |

### 7.1 Blocking evidence stays empty in this slice

Do not auto-convert any of the following into `BlockingEvidence`:

- git state
- unused `COMMIT READY`
- dirty working tree
- review tokens
- OOB presence
- Supervisor narrative
- unused `COMMIT READY` outside the input file

Those detections remain Autopilot-owned live gates. Unused
`COMMIT READY` continues to block selector invocation **outside** the
input file.

### 7.2 `completed` remains attestation, not git proof

If a later expansion includes `completed`, that Boolean is
human-attested under this slice architecture. The supplier must not
compute it from HEAD, exact tag, commit history, or consumed
`COMMIT READY`.

A later Architecture State Resolver may become the factual producer of
`completed` only after a separate architecture approval. That approval
is not this document.

### 7.3 No hidden default records

Omitting an identity is the lawful way to keep it out of the closed
world. The supplier must not invent a record to complete a graph, fill
a prefix sequence, or satisfy a narrative “next” claim.

---

## 8. Identity contract

Milestone identities remain:

- opaque
- exact
- non-blank strings
- free of ordering semantics
- free of priority semantics

Additional invariants that this supply architecture must preserve, not
weaken:

1. The supplier never generates, derives, hashes, trims, case-folds,
   or infers an identity.
2. Comparison is exact equality only.
3. `" PF-M5 "` is distinct from `"PF-M5"` if both ever appear.
4. Duplicate identities are rejected by the engine, not repaired by
   the supplier.
5. Unknown identities fail closed. The supplier must not invent a
   record to complete a graph.
6. No suffix interpretation.
7. No numeric sequencing.
8. No ranking semantics.
9. No discovery from filenames.
10. No discovery from tags.
11. No discovery from git commits.
12. No discovery from prompts.
13. No discovery from Markdown.

Existing strings such as `PF-M5`, `IRO-M3`, and `Automation-M3` are
legal **opaque identities only** if a later authorized catalog
explicitly includes them. This first slice must not introduce them.

Supervisor labels such as `post-repository-target-abstraction` remain
non-identities.

### 8.1 First-slice identity set

The first-slice empty input introduces **zero** milestone identities.

Do **not** insert:

- `PF-M5`
- `Automation-M3`
- `IRO-M3`
- `IRO-M4`
- Architecture State Resolver
- `Automation-M4`
- `Autopilot-M1`
- any other successor identity

An empty present file is lawful. A unique eligible unauthorized
identity is not.

---

## 9. Repository isolation

### 9.1 Exact files

The only lawful selector-input locations are:

```text
state/JOO/milestone_selection_input.json
state/JOO_AUTOMATION/milestone_selection_input.json
```

under the Autopilot host.

### 9.2 No global alias

There is no:

```text
state/milestone_selection_input.json
```

Legacy un-namespaced `state/*.json` remains the JOO alias only for
pre-existing Autopilot files. It is **not** a selector-input location
and must not be created for this artifact.

### 9.3 No cross-repository reuse

- A `JOO` input may never be reused for `JOO_AUTOMATION`.
- A `JOO_AUTOMATION` input may never be reused for `JOO`.
- The two catalogs are invisible to each other.
- Copying bytes from one namespace into the other is a new write that
  requires its own authorization.

The current live gap is
`state/JOO_AUTOMATION/milestone_selection_input.json`. A later `JOO`
file is an independent write. It must not be inferred from the
Automation file.

### 9.4 No path inference

The writer must name the logical repository ID. Forbidden inference
includes:

- current working directory
- nearest git root
- filesystem path resemblance
- environment variables
- `"JOO "` / `"joo"` / `"JOO-AUTOMATION"` spellings

`"JOO "` ≠ `"JOO"`. `"joo"` is unknown. `"JOO-AUTOMATION"` is unknown.

The engine never chooses a repository. Selector Input Supply never
chooses a repository. Supply happens only inside one already-bound
namespace.

### 9.5 Protected host prefix

When the target is `JOO_AUTOMATION`, these files live under protected
host `state/` and must not become stage candidates or target dirt.
That Repository Target rule is unchanged.

---

## 10. Explicit, not inferred

### 10.1 Allowed

- exact human-authored JSON
- explicit empty collections
- later explicitly authorized named records
- exact prerequisite rows
- exact policy flags

Every value in the file must be written as itself.

### 10.2 Forbidden

- roadmap parsing
- Constitution parsing
- architecture Markdown parsing
- README parsing
- git HEAD / tag inference
- commit history inference
- `COMMIT READY` inference
- review token inference
- Supervisor narrative inference
- LLM milestone discovery
- candidate ranking
- best-candidate selection
- automatic input repair
- missing-field reconstruction
- trim / sort / pretty-print to repair invalid input
- treating a missing file as an implicit empty world

### 10.3 Informal non-records

The following remain non-records:

- informal chat
- untracked prompts
- “human selected PF-M5” in a review narrative
- silence
- deleting one candidate from a conversation
- OOB product-architecture sequencing

---

## 11. Raw byte identity

Runtime Integration already hashes the raw input bytes with SHA-256.
That contract is reused, not redesigned.

```text
same exact bytes
  → same input_identity
  → same deserialized MilestoneSelectionInput
  → deterministic Milestone Selection Engine result
```

Invariants:

1. `input_identity` is the SHA-256 hex digest of the raw file bytes.
2. The adapter must not canonicalize, pretty-print, sort, or rewrite
   the file to compute identity.
3. Formatting changes are material byte changes.
4. A later authorized empty first-slice file has one identity: the
   digest of the frozen first-slice bytes in §5.2.
5. If the file is missing, `input_identity` is absent and
   `stop_reason` is `MISSING_SELECTOR_INPUT`.

The supplier must not introduce a second identity scheme.

---

## 12. Architecture State Resolver deferral

Architecture State Resolver remains **DEFERRED**.

This architecture does not:

- observe git
- observe HEAD
- observe tags
- mark `completed` automatically
- normalize review state
- normalize `COMMIT READY`
- normalize dirty tree
- update selector input after commits
- infer candidate identity
- infer prerequisites
- author `BlockingEvidence` from live gates
- parse accepted architecture Markdown
- combine resolver and selector

### 12.1 Later resolver, if separately authorized

A later resolver may become a separately authorized factual producer
of recorded facts and blocking evidence.

That later component remains outside this owner. Combining resolver
and selector is forbidden.

### 12.2 Structural deferral

Deferral is structural, not rhetorical:

```text
Selector Input Supply authors a static explicit object
Architecture State Resolver is absent
Autopilot keeps live detection
Milestone Selection Engine keeps cardinality
```

The first supply slice must remain smaller than a general resolver.
It is a writer contract for one explicit file, not an observer of
repository truth.

---

## 13. Autopilot boundary

Autopilot:

- binds the repository first
- checks the inter-milestone gate
- reads selector input through the runtime adapter
- does not author selector input
- does not add candidates
- does not update `completed` fields
- does not rank records
- does not convert unused `COMMIT READY` into `blocking_evidence`

### 13.1 Preserved safe-fastpath

This architecture preserves, and does not reopen:

- exact-path staging
- dirty-tree fail-closed
- repository-scoped `COMMIT READY`
- tag / push authorization
- OOB safety
- `next_action` safety
- no history rewrite
- no force-push

### 13.2 Unused `COMMIT READY` stays outside the file

Unused `COMMIT READY` continues to block selector invocation at the
already-frozen inter-milestone gate.

Do **not** put `COMMIT READY` into `blocking_evidence` in this slice.

Live safety remains a gate. It is not first-slice catalog content.

### 13.3 Replay remains an orchestration guard

The already-frozen runtime replay guard remains. The adapter does not
write `completed: true` after a commit. Closing an identity in the
explicit input remains a human / later resolver action after separate
authorization.

---

## 14. Supervisor boundary

Supervisor:

- consumes `STOP` / `CONTINUE` decisions
- does not write selector input
- does not invent records
- does not infer a successor from prose
- does not rank candidates
- must preserve engine or integration `STOP`
- may not replace `CONTINUE(X)` with `Y`

Supervisor remains an intra-milestone actor among
`RUN_REVIEW` / `COMMIT` / `STOP` for an already selected identity, or
a preserver of selector `STOP`.

This architecture adds no fourth Supervisor action and no selector
authorship.

---

## 15. Expected current outcome

### 15.1 Now

```text
input file absent
  → STOP(MISSING_SELECTOR_INPUT)
  → stop_source=INTEGRATION
  → selected_identity=none
  → engine not invoked
```

This is the correct live result for current `JOO_AUTOMATION`.

The same command against `JOO` is independent. A missing `JOO` input
is a `JOO`-scoped `MISSING_SELECTOR_INPUT`.

### 15.2 After later authorized empty first-slice materialization

If, and only if, a later board authorizes materialization of the
frozen empty object for a named repository:

```text
input file exists with empty collections
  → runtime adapter loads and validates
  → Milestone Selection Engine runs
  → STOP(NO_ELIGIBLE_MILESTONE)
```

This is the correct first-slice outcome.

It proves the full input-supply chain without authorizing a successor.

It does not start PF-M5, Automation-M3, IRO-M3, IRO-M4, or
Architecture State Resolver.

### 15.3 Independent namespaces after materialization

Materializing `JOO_AUTOMATION` does not materialize `JOO`.
Materializing `JOO` does not materialize `JOO_AUTOMATION`.

The other namespace remains `MISSING_SELECTOR_INPUT` until its own
file exists.

---

## 16. First implementation / materialization slice

This document authorizes **no** implementation and **no**
materialization.

### 16.1 Minimal later slice

Later, if separately authorized, the first slice must be minimal.

It may:

- create a tiny deterministic writer / materializer **or**
- authorize exact manual materialization of the frozen empty object
- validate the exact repository namespace
- refuse overwrite unless separately authorized
- validate produced bytes against the exact MSE input contract
- test `JOO` / `JOO_AUTOMATION` isolation

### 16.2 Prefer no new runtime module

Architecture review of any later implementation request must decide
whether code is actually necessary.

**Prefer no new runtime module** if exact manual materialization of
the frozen empty object is sufficient.

A writer / materializer is justified only if a later board finds
manual materialization insufficient to prove namespace isolation,
overwrite refusal, or byte-identity invariants.

If a writer is authorized, it must be a tiny deterministic
materializer of the frozen bytes. It must not become a registry,
resolver, parser, or sequencer.

### 16.3 Explicitly out of the first implementation slice

- a general milestone registry
- Architecture State Resolver
- document parsing
- automatic milestone sequencing
- automatic input mutation after commit
- automatic blocking-evidence authoring
- dual-source catalog compiler
- authoring UI
- MSE package change
- runtime adapter change unless separately authorized
- Autopilot safe-fastpath change
- Supervisor prompt rewrite
- live Autopilot execution as a side effect of authoring

### 16.4 Later hosting

- Architecture freeze: this tracked JOO document under
  `docs/automation/`
- Materialization, if later authorized: Autopilot host
  `~/JOO-Automation/state/<repository_id>/milestone_selection_input.json`
- Do not implement inside a JOO investment-domain package
- Do not extend `joo_auto`
- Do not import JOO PF / IRO / Market / FactStore / allocation
  packages
- Do not invent `Automation-M4` or `Autopilot-M1` as the package
  identity

---

## 17. Required future test invariants

A later implementation or materialization must prove at least the
following. These tests are not authored by this document.

| Invariant | Expected |
| --- | --- |
| Missing file ≠ empty file | Absent → `MISSING_SELECTOR_INPUT`; explicit empty → engine runs |
| Explicit empty input deserializes lawfully | Frozen object becomes `MilestoneSelectionInput` with empty collections |
| Explicit empty input → `NO_ELIGIBLE_MILESTONE` | Engine `STOP`; no successor invented |
| `JOO` / `JOO_AUTOMATION` isolation | No cross-namespace read or reuse |
| No un-namespaced alias | `state/milestone_selection_input.json` is not read and must not be created |
| No identity invention | First-slice file contains zero identities |
| No roadmap parsing | Supplier / writer does not read `docs/JOO_PRODUCT_ROADMAP.md` |
| No Markdown parsing | Constitution, architecture, and README prose are not record sources |
| No git inference | HEAD, tags, and commit history do not populate records |
| No `COMMIT READY` conversion | Unused `COMMIT READY` is not written into `blocking_evidence` |
| No ranking fields | Payload has no `priority`, `score`, `rank`, or `next_milestone` |
| No LLM | No Supervisor or chat extraction of identities |
| Raw-byte hash changes when bytes change | Formatting or content change yields a new `input_identity` |
| Same bytes produce same `input_identity` | SHA-256 of the frozen first-slice bytes is stable |
| MSE package unchanged | Existing engine tests remain green; public API unchanged |
| Runtime adapter unchanged unless separately authorized | Existing runtime-integration tests remain green |

Normal, boundary, wrong-type, empty-value, order, and exception
propagation cases required by the repository agent contract apply to
every later public writer or materializer entry point, if one is
authorized at all.

Overwrite of an existing namespaced file is fail-closed unless a later
board separately authorizes replacement.

---

## 18. Authority chain

```text
Human
  writes exact accepted bytes after later authorization
        │
        ▼
Selector Input Supply
  contract for lawful payload and placement
  first-slice content = empty collections
        │
        ▼
state/<repository_id>/milestone_selection_input.json
        │
        ▼
Milestone Selection Runtime Adapter
  load / type-check / hash raw bytes only
        │
        ▼
Milestone Selection Engine
  CONTINUE or STOP
        │
        ▼
Supervisor / Autopilot
  consume; do not author
```

Later layers may consume earlier ones. They may not assume them.
Human silence is never authorization.

This document occupies only the Selector Input Supply box. It does
not occupy the engine, adapter, Supervisor, Autopilot, or a later
resolver.

---

## 19. Non-responsibilities

This architecture does **not** include, authorize, or implement:

- PF-M5
- Automation-M3
- IRO-M3
- IRO-M4
- Architecture State Resolver
- roadmap parsing
- Markdown parsing
- LLM discovery
- candidate ranking
- business-value scoring
- automatic completion inference
- automatic prerequisite inference
- automatic blocking-evidence authoring
- automatic selector-input mutation
- automatic post-commit updates
- unbounded successor loop
- Repository Target redesign
- Runtime Integration redesign
- Milestone Selection Engine redesign
- Supervisor redesign
- safe-fastpath redesign
- `COMMIT READY` redesign
- `next_action` redesign
- JOO investment-domain implementation
- a general milestone registry
- a catalog compiler
- an authoring UI
- creation of `milestone_selection_input.json` by this document

The two known JOO OOB documents remain non-authoritative.

---

## 20. Frozen invariants

1. Owner is Selector Input Supply.
2. Milestone ID remains `UNRESOLVED`.
3. This owner authors the contract of the explicit input file only.
4. This owner is not the engine, adapter, Autopilot, Supervisor,
   Repository Target, resolver, parser, or ranking engine.
5. The runtime path remains
   `state/<repository_id>/milestone_selection_input.json`.
6. Top-level JSON keys are exactly `records`, `dependencies`, and
   `blocking_evidence`.
7. No envelope fields belong in the input file.
8. Repository identity lives in the namespace, not in the payload.
9. The first authorized object is the empty explicit closed world.
10. Absent file ≠ explicit empty file.
11. Absent file is `STOP(MISSING_SELECTOR_INPUT)`.
12. Explicit empty file is engine `STOP(NO_ELIGIBLE_MILESTONE)`.
13. First-slice writer is HUMAN after later authorization.
14. Autopilot, Supervisor, adapter, engine, and resolver must not
    write the file in this slice.
15. First-slice `blocking_evidence` remains empty.
16. Identities remain opaque, exact, and non-inferred.
17. The first-slice empty input introduces zero identities.
18. `PF-M5`, `Automation-M3`, `IRO-M3`, `IRO-M4`, and Architecture
    State Resolver are not inserted.
19. `JOO` and `JOO_AUTOMATION` inputs are isolated.
20. There is no un-namespaced alias.
21. No cwd or path inference.
22. Supply is explicit, never inferred from prose, git, or chat.
23. Same exact bytes yield the same `input_identity`.
24. JSON is not canonicalized before hashing.
25. Architecture State Resolver remains deferred.
26. Resolver and selector must not be combined.
27. Autopilot binds the repository and does not author input.
28. Unused `COMMIT READY` blocks selector invocation outside the file.
29. Supervisor consumes decisions and does not invent records.
30. Current live result remains `STOP(MISSING_SELECTOR_INPUT)`.
31. Later empty materialization remains `STOP(NO_ELIGIBLE_MILESTONE)`.
32. Prefer no new runtime module if manual materialization suffices.
33. No general registry, resolver, parser, or sequencer is authorized.
34. Existing MSE, Runtime Integration, Repository Target, Supervisor,
    and safe-fastpath contracts remain unchanged.
35. This document does not authorize implementation, materialization,
    commit, tag, or push.
36. Development automation must not distort JOO's investment-product
    architecture.

---

## 21. Authorization freeze

| Question | Answer |
| --- | --- |
| Architecture document authored | Yes |
| Independent architecture review | Required next |
| Implementation authorized | **NO** |
| Human materialization of the file authorized | **NO** — later board only |
| Selector input file created by this document | **NO** |
| PF-M5 authorized | **NO** |
| Automation-M3 authorized | **NO** |
| IRO-M3 / IRO-M4 authorized | **NO** |
| Architecture State Resolver | **DEFERRED** |
| Milestone Selection Engine redesign | **NO** |
| Runtime Integration redesign | **NO** |
| Repository Target redesign | **NO** |
| Supervisor / safe-fastpath / `COMMIT READY` / `next_action` redesign | **NO** |
| Roadmap parsing | **NO** |
| LLM discovery | **NO** |
| Unique successor authorized | **NO** |
| Automatic continuation loop | **NO** |
| Commit / tag / push authorized | **NO** |
| Live Autopilot authorized | **NO** |
| Milestone ID | **UNRESOLVED** |
| Owner | **Selector Input Supply** |
| First-slice payload | Empty explicit closed world |
| Current live result | `STOP(MISSING_SELECTOR_INPUT)` |
| Expected result after empty input materialization | `STOP(NO_ELIGIBLE_MILESTONE)` |
| Next action | Independent Architecture Review |

Until a later materialization is separately authorized and completed,
live Autopilot must continue to treat missing selector input as
`STOP(MISSING_SELECTOR_INPUT)`. That remains the correct live
outcome.
