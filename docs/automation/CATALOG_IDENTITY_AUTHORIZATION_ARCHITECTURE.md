# Catalog Identity Authorization Architecture

## Status and identity

- Status: Architecture authored for independent review; first-slice
  Catalog Identity Authorization freeze only
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Development infrastructure** — not an investment-domain plane
- Capability: **Catalog Identity Authorization**
- Owner: **Selector Input Supply**
- Milestone ID: **UNRESOLVED**
- This document does **not** invent or assign `Automation-M4`,
  `Autopilot-M1`, `M55+`, `PF-M5`, `Automation-M3`, `IRO-M3`,
  `IRO-M4`, Architecture State Resolver, or any other manufactured
  successor identity
- Authorizing direction review: Architecture Review Board
  (`~/JOO-Automation/results/catalog_identity_authorization_architecture_boundary_review/latest.md`)
  — **FINAL DECISION: CATALOG IDENTITY AUTHORIZATION ARCHITECTURE READY**
- Authority vehicle: this tracked JOO document. Not a host state file,
  not a second runtime catalog, not a compiler input, and not a review
  result
- Production runtime catalog remains the already-specified Autopilot
  host artifact `state/<repository_id>/milestone_selection_input.json`
  under JOO-Automation. This document does not create, move, or
  overwrite that file
- Repository boundary for this document: architecture authoring only;
  this document alone authorizes no production code, test, package
  change, schema module, configuration, run artifact, selector-input
  overwrite, second catalog JSON, host state CIA file, catalog
  compiler, Supervisor prompt rewrite, Autopilot runtime change, or
  Git history mutation

This document freezes the **smallest lawful Catalog Identity
Authorization contract**.

It answers only:

> Which exact identities, if any, may exist as catalog members in one
> named repository namespace, and how is that membership granted,
> replaced, or revoked without ranking, inference, overwrite, or
> successor selection?

It does **not** answer:

> What milestone should be built next, and may Autopilot now continue?

This document does **not** redesign:

- Milestone Selection Engine first-slice models or cardinality rules
- Milestone Selection Engine Runtime Integration
- Milestone Selection Input Supply empty-world first slice
- Milestone Selection Catalog Expansion overwrite contract
- Autopilot Repository Target Abstraction
- Autopilot v5 safe-fastpath
- Supervisor action vocabulary (`RUN_REVIEW` / `COMMIT` / `STOP`)
- `COMMIT READY` single-consumption
- `next_action` schema
- JOO investment-domain architecture

Implementation is **not** authorized.

Overwrite of the live empty catalog is **not** authorized.

Live Autopilot is **not** authorized.

No catalog identity is granted except the first-slice **zero-identity**
set for `JOO_AUTOMATION`.

Architecture State Resolver remains **DEFERRED**.

---

## 1. Purpose

Catalog Expansion already froze that a milestone identity may enter a
repository-scoped selector catalog only after a separate Catalog
Identity Authorization grants that exact opaque identity membership
in that exact repository namespace.

That earlier freeze **defined** Catalog Identity Authorization. It did
not create it.

The unique remaining architectural gap is the **membership grant
itself**: the smallest lawful authority that can later permit
identities to exist in

```text
state/<repository_id>/milestone_selection_input.json
```

without becoming a second catalog, a compiler, a resolver, a ranking
engine, overwrite authorization, or a successor selector.

This architecture adds exactly one responsibility to the existing
Selector Input Supply owner:

**Selector Input Supply owns the Catalog Identity Authorization
contract: who may grant repository-scoped catalog membership, what
one grant contains, and how a later grant replaces the prior set.**

It does not own eligibility classification.
It does not own runtime consumption.
It does not own repository binding.
It does not observe git.
It does not overwrite the catalog.
It does not invent a successor.

The architectural benefit of the first slice is not that Autopilot
starts building a successor. The benefit is that membership authority
exists as an inspectable empty set. That empty set is successor-neutral
and is the membership analogue of the already-live empty explicit
closed world.

---

## 2. Current checkpoint

This architecture is authored only after independent re-verification.
Material state matches the authorizing boundary review.

### 2.1 JOO

| Check | Value |
| --- | --- |
| Path | `/Users/takesimple/Projects/JOO` |
| Branch | `feature/stage2-provider-runtime` |
| HEAD | `c57b4c2dd5e7fc2039cc2832a789034c45e23abb` |
| Exact tag at HEAD | `v7.17-stage5-milestone-selection-catalog-expansion-architecture` |
| HEAD subject | Add Milestone Selection Catalog Expansion architecture |
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
file as successor identity, catalog membership, ranking, or commit
authority.

Tracked `docs/JOO_PRODUCT_ROADMAP.md` remains v1.2. It is stage-level
product direction only. It is not a catalog and not a CIA.

### 2.2 JOO-Automation

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

### 2.3 Current live selector state

| Fact | Observed |
| --- | --- |
| Target | `JOO_AUTOMATION` |
| Selector input path | `state/JOO_AUTOMATION/milestone_selection_input.json` |
| Exact input | empty explicit closed world |
| Raw bytes | 69-byte UTF-8 object; LF; two-space indent; one trailing newline |
| `input_identity` | `d36a00d8a2a0b5f6d369cad89ff4744dae4e5ac6bfaa52f80e6e70f9fd5b9cfa` |
| `decision_class` | `STOP` |
| `stop_reason` | `NO_ELIGIBLE_MILESTONE` |
| `stop_source` | `ENGINE` |
| `selected_identity` | none |
| Classification ran | yes |
| Eligible identities | none |
| Authorized identities | **NONE** |
| Unused namespaced `COMMIT READY` | none |

Current exact catalog:

```json
{
  "records": [],
  "dependencies": [],
  "blocking_evidence": []
}
```

`state/JOO/milestone_selection_input.json` is **ABSENT**.
`state/milestone_selection_input.json` is **ABSENT** and must not be
created.

No Catalog Identity Authorization artifact existed before this
document.

This architecture must leave the live catalog bytes unchanged.

### 2.4 Frozen predecessors that this document must not reopen

| Authority | Status | Constraint on this freeze |
| --- | --- | --- |
| Milestone Selection Engine architecture | Frozen at JOO `v7.13` | Explicit caller-supplied `MilestoneSelectionInput` only; 0 / 1 / N; no ranking, filesystem, git, Markdown, or LLM |
| Milestone Selection Engine first slice | Committed at `0c44ec4`; package `milestone_selection_engine/` | Public API unchanged |
| Repository Target Abstraction architecture | Frozen at JOO `v7.14` | Target binding precedes selection; supported IDs are `JOO` and `JOO_AUTOMATION` only |
| Repository Target implementation | Live | Not redesigned |
| Milestone Selection Engine Runtime Integration architecture | Frozen at JOO `v7.15` | Reads exact namespaced file; adapter loads and validates only |
| Runtime Integration implementation | Committed at `4e22741`; live-verified | Not redesigned |
| Milestone Selection Input Supply architecture | Frozen at JOO `v7.16` | Empty explicit closed world; human writer; resolver deferred |
| Milestone Selection Catalog Expansion architecture | Frozen at JOO `v7.17` | Option A; CIA defined not created; overwrite fail-closed |
| Autopilot v5 safe-fastpath | Live | Exact-path staging, dirty-tree fail-closed, repository-scoped `COMMIT READY`, tag/push authorization, OOB safety, `next_action` safety, no history rewrite |
| Supervisor vocabulary | `RUN_REVIEW` / `COMMIT` / `STOP` only | Consumes a decision; must not invent records |
| `COMMIT READY` | Autopilot-owned, single-consumption, repository-scoped | Unused authority blocks selector invocation; never becomes first-slice engine input |
| Architecture State Resolver | Deferred and absent | Must not be invented here |

### 2.5 What is still missing

```text
RepositoryTarget is frozen and live
Milestone Selection Engine is frozen, implemented, and isolated
Runtime Integration is frozen, implemented, and live-verified
Empty explicit catalog is materialized for JOO_AUTOMATION
Catalog Expansion overwrite contract is frozen
Architecture State Resolver is absent
Catalog Identity Authorization contract is the unique remaining freeze
Non-empty catalog overwrite is unauthorized
```

This document freezes only the missing membership-grant contract. It
does not replace the deferred resolver, does not overwrite the
catalog, and does not name a successor.

---

## 3. Owner

The exact owner remains:

**Selector Input Supply**

Milestone ID remains:

**UNRESOLVED**

Do not create another owner.

Catalog Identity Authorization is the same owner’s next contract, not
a new component, not a numbered milestone, and not Architecture State
Resolver.

### 3.1 What this owner may decide

Selector Input Supply may freeze:

- that CIA is a human-authored repository-scoped policy grant
- that the vehicle is this tracked JOO architecture / authority
  document
- that one CIA binds exactly one `repository_id`
- that one CIA authorizes the complete finite membership set
- that the first-slice set for `JOO_AUTOMATION` is empty
- that a later accepted CIA replaces the prior set
- the prohibition on inference, ranking, ranking-by-omission,
  overwrite, live Autopilot, and implementation

### 3.2 What this owner must not become

Selector Input Supply must **not** become:

| Rejected identity | Why |
| --- | --- |
| Milestone Selection Engine | Classifies supplied records. Must remain author-free |
| Architecture State Resolver | Later live-fact normalizer. Deferred and not this slice |
| Autopilot | Executor and safety owner. Must not invent candidates |
| Supervisor | Intra-milestone LLM actor. Must not invent records |
| Repository Target | Binds the repository. Does not author the milestone set |
| Catalog Compiler | Would create a second source of truth |
| Milestone registry product | Out of scope |
| Roadmap parser | Prose is not a record source |
| Ranking engine | Cardinality remains the only selection rule |
| LLM successor selector | Discovery and preference are forbidden |
| Overwrite authorizer | Membership is not overwrite |
| Implementation authorizer | Membership is not implementation |

This is a development-infrastructure owner. It is not a numbered
milestone. It is not `Automation-M4`, `Autopilot-M1`, or Architecture
State Resolver.

### 3.3 Ownership that does not move

| Actor | Still owns | Must not gain |
| --- | --- | --- |
| Selector Input Supply | Lawful authoring, expansion, and CIA membership-grant contract | Eligibility; git observation; repository choice; ranking; overwrite; implementation |
| Human | First-slice grant author of the accepted CIA membership set | Informal chat as autonomy |
| Architecture board | Accept or reject the written grant as written | Granting by prose, comment, or preference |
| Milestone Selection Engine | Eligibility cardinality; `CONTINUE` / `STOP` | File authoring; membership grants |
| Runtime Adapter | Load, type-check, hash raw bytes, persist decision | File authoring, repair, overwrite, CIA loading |
| Autopilot Repository Target | Allowlisted target bind; `AutopilotExecutionContext` | Successor identity or catalog authorship |
| Supervisor | Intra-milestone `RUN_REVIEW` / `COMMIT` / `STOP` for an already selected identity | Independent successor choice or record invention |
| Autopilot runtime | Safety gates; exact-path staging; `COMMIT READY` single-consumption; tag/push authorization | Computing, ranking, writing selector input, or granting membership |
| Architecture State Resolver | Nothing yet. Deferred | Hidden selector or automatic catalog mutation |
| `COMMIT READY` / commit-review | Unused versus consumed commit authority | Successor identity or membership |

---

## 4. Non-responsibilities

This architecture does **not** include, authorize, or implement:

- `PF-M5` implementation
- `Automation-M3`
- `IRO-M3`
- `IRO-M4`
- Architecture State Resolver
- catalog overwrite
- catalog materialization
- live Autopilot
- automatic continuation
- roadmap parser
- Markdown parser
- LLM discovery
- ranking
- scoring
- priority
- catalog compiler
- second runtime catalog
- host state CIA file
- separate CIA JSON file
- git execution changes
- tag / push changes
- JOO investment-domain work
- third repository support
- any historical completed identity as a catalog backfill
- naming of a successor `X`
- commit
- tag
- push

The two known JOO OOB documents remain non-authoritative.

---

## 5. What Catalog Identity Authorization is

Catalog Identity Authorization is:

**A HUMAN-AUTHORED, REPOSITORY-SCOPED POLICY GRANT**

It is the only lawful act that may add an opaque identity string to
the closed world that may later be written into the sole runtime
catalog.

It answers only:

> Which exact identities, if any, may exist as catalog members in this
> one repository namespace, and with which explicit attested
> Booleans?

It does **not** answer:

> What should be built next?
> May Autopilot continue?
> May the catalog be overwritten?
> May that identity be implemented?

CIA is not eligibility.
CIA is not uniqueness.
CIA is not `CONTINUE`.
CIA is not implementation authority.

### 5.1 What CIA is not

CIA is **not**:

- a runtime state file
- a review result
- a second catalog
- a compiler input
- a ranking artifact
- a selector result
- overwrite authorization
- live Autopilot authorization
- implementation authorization
- an MSE payload clone
- Architecture State Resolver
- a successor selector

### 5.2 Membership is not eligibility

An identity becomes a catalog member only by CIA for that exact
`repository_id`.

Eligibility remains the Milestone Selection Engine’s derived
classification of the supplied record fields after a later lawful
catalog write.

Membership without a later overwrite leaves the live catalog
unchanged.
Membership of many identities does not imply a ranking.
Membership of one identity does not imply `CONTINUE`.
Zero membership is lawful.

---

## 6. Authority vehicle

The vehicle is exactly one tracked JOO architecture / authority
document:

```text
docs/automation/CATALOG_IDENTITY_AUTHORIZATION_ARCHITECTURE.md
```

This document is that vehicle.

### 6.1 Chosen representation

CIA is a **policy grant**. The architecture document is the vehicle.
The thing being authorized is the membership policy.

The document contains an explicit, inspectable, machine-readable
membership block.

That block is authorization text.
It is **not** a runtime catalog.
The Runtime Adapter must **never** load this document or that block.

Humans may later copy authorized identities into the sole runtime
file only after a separate overwrite authorization.

There is **no** compiler.

### 6.2 Rejected vehicles

| Option | Why rejected |
| --- | --- |
| Separate machine-readable CIA JSON in JOO | A sibling JSON is a second catalog in all but name. Invites a compiler |
| Host state CIA file under `state/<repository_id>/` | Already rejected by Catalog Expansion §6.2. Would sit beside the sole runtime catalog |
| Review result only | Reviews live in untracked host `results/`. Prose is not membership. Not durable JOO authority |
| Runtime catalog itself as the grant | The catalog is the MSE payload. Membership authority must precede overwrite |
| Informal chat / untracked prompt | Not a machine-readable grant |

Do **not** create:

- a separate CIA JSON file
- a host state CIA file
- a second runtime catalog
- a catalog compiler

### 6.3 Adapter isolation

The Runtime Adapter continues to load only:

```text
state/<repository_id>/milestone_selection_input.json
```

It must not:

- read this architecture document
- parse Markdown
- discover CIA blocks
- compile CIA into catalog bytes
- treat a review result as membership

---

## 7. Repository binding

A CIA binds **exactly one** `repository_id`.

Allowed exact values:

```text
JOO
JOO_AUTOMATION
```

These are logical identities. They are not filesystem inputs.

### 7.1 Identity invariants

- exact built-in `str`
- exact equality
- no trim
- no case-fold
- no closest match
- no path inference
- no cwd inference
- no nearest git root
- no environment-variable inference
- no cross-repository grant

Therefore:

- `"JOO "` ≠ `"JOO"`
- `"joo"` is unknown
- `"JOO-AUTOMATION"` is unknown
- `"JOO_automation"` is unknown

Unknown `repository_id` is not a lawful CIA.

### 7.2 Isolation

A `JOO_AUTOMATION` CIA does **not** authorize `JOO`.
A `JOO` CIA does **not** authorize `JOO_AUTOMATION`.

The two namespaces are invisible to each other.

Copying a membership set from one repository into the other is a new
grant. It requires its own later CIA.

### 7.3 First-slice binding

First-slice scope is `JOO_AUTOMATION` only.

No `JOO` CIA is issued in this first slice.

The absent `JOO` catalog remains
`STOP(MISSING_SELECTOR_INPUT)` until a separate later `JOO` CIA and
a separate later `JOO` materialization exist.

Empty CIA for `JOO_AUTOMATION` is distinct from missing CIA for
`JOO`:

| Condition | Meaning |
| --- | --- |
| Empty CIA + empty catalog | Membership authority exists and grants nothing. Engine `STOP(NO_ELIGIBLE_MILESTONE)` |
| No CIA + no catalog | No membership authority. File must remain absent. Integration `STOP(MISSING_SELECTOR_INPUT)` |

---

## 8. Membership semantics

Freeze these definitions.

### 8.1 Authorized identity

An **authorized identity** is an exact opaque string explicitly
present in the current accepted CIA membership set for that
`repository_id`.

Comparison is exact equality only.
No trim.
No case-fold.
No suffix interpretation.
No numeric sequencing.

### 8.2 Unauthorized identity

An **unauthorized identity** is any identity not present in that
accepted set.

An unauthorized identity must not appear in the catalog.
Insertion of an unauthorized identity fails closed.

### 8.3 Omitted identity

An **omitted identity** is an identity not listed in the current set.

Omission of a never-authorized identity is **lawful**.

Omission of an already-authorized identity from a replacement CIA or
a replacement catalog, without explicit revocation, is
**ranking-by-omission** and is **forbidden**.

### 8.4 Revoked identity

A **revoked identity** is a previously authorized identity explicitly
removed by a later replacement CIA.

Revocation is an explicit later membership-set replacement that does
not list the prior member.

**Silence is not revocation.**

Informal chat, review prose, deleting a name from conversation, or
leaving a granted name out of later catalog bytes is not revocation.

### 8.5 Deferred / oob / superseded

`deferred`, `oob`, and `superseded` are record fields on an
**already-authorized** identity.

They reduce eligibility cardinality.
They are **not** membership states.
They are **not** ranking scores.

An identity may be authorized and deferred.
An identity may be authorized and oob.
An identity may be authorized and superseded.

Those facts exclude the identity from the eligible set. They do not
remove it from the membership set.

### 8.6 Completed

`completed` is a **human-attested Boolean** only in this first slice.

It must **not** be derived from:

- git
- HEAD
- tags
- commit history
- consumed or unused `COMMIT READY`
- runtime state
- review results

A later Architecture State Resolver may become the factual producer
of `completed` only after separate architecture approval. That
approval is not this document.

### 8.7 Zero identities

**Zero identities are lawful.**

The current live empty catalog already classifies as
`STOP(NO_ELIGIBLE_MILESTONE)`. That is the existence proof. There is
no frozen contradiction.

### 8.8 What is never a member by itself

Silence is not a member.
Historical mention is not a member.
Roadmap order is not a member.
Architecture title is not a member.
Filename is not a member.
Tag is not a member.
Review prose is not a member.
OOB sequencing is not a member.

---

## 9. Membership model

One CIA authorizes the **COMPLETE FINITE MEMBERSHIP SET** for exactly
one `repository_id`.

The set may contain:

- 0 identities
- 1 identity
- N identities

Many names do not imply a ranking.

### 9.1 Replacement, not accumulation

There is one current CIA per repository.

A later accepted CIA for the same `repository_id` **replaces** the
prior membership set.

It does **not** accumulate silently.

This full-set design makes ranking-by-omission structurally visible.
One-CIA-per-identity would let a writer grant only A and leave B
undiscussed. A complete set makes every authorized name inspectable
in one artifact.

### 9.2 Why full-set is required

If CIA authorizes `{A, B}`, both names are inspectable members.

A later writer cannot pretend B was never granted.

If A and B remain independently eligible, the engine result is
`STOP(MULTIPLE_ELIGIBLE_MILESTONES)`.

That is success.

---

## 10. Required CIA representation

The architecture document freezes a machine-readable authority block
concept with exactly these required keys:

| Field | Rule |
| --- | --- |
| `repository_id` | Exactly `JOO` or `JOO_AUTOMATION` |
| `authorized_identities` | Finite explicit list. May be `[]` |

### 10.1 Authorized-identity object

Each authorized identity, **when present**, must carry:

| Field | Rule |
| --- | --- |
| `identity` | Exact opaque non-blank string. No trim. No case-fold |
| `completed` | Exact Boolean |
| `deferred` | Exact Boolean |
| `oob` | Exact Boolean |
| `superseded` | Exact Boolean |
| `architecture_frozen` | Exact Boolean metadata. No eligibility effect |

Do **not** populate any authorized-identity object in this first
slice.

### 10.2 Optional prerequisite edges

Optional, only if present at all:

- explicit `PREREQUISITE` edges only
- both endpoints already authorized members of **this** CIA
- each edge names `dependent`, `prerequisite`,
  `dependency_type = PREREQUISITE`, and non-blank `source_identity`

The optional key, if used in a later replacement CIA, is
`prerequisite_edges`.

Absence of `prerequisite_edges` means no edges.
Silence is not an edge.

The first-slice default is no dependency edges.

### 10.3 Authority block is not an MSE payload

The CIA block authorizes membership and attested Booleans.

The runtime catalog remains the only MSE payload.

Do **not** clone the MSE envelope onto CIA:

- no top-level `records`
- no top-level `dependencies` as an MSE catalog clone
- no `blocking_evidence`

A later human overwrite, if separately authorized, may copy
authorized identities into catalog `records` and may copy authorized
`PREREQUISITE` edges into catalog `dependencies`. That copy is a
later overwrite act. It is not a compiler and is not authorized by
this document.

### 10.4 This document does not create a future non-empty grant

This document freezes the representation.

It does **not** create the actual future non-empty grant.

No later successor identity is named here as a member.

---

## 11. Forbidden CIA fields

The following fields must never appear on a CIA:

- `rank`
- `priority`
- `score`
- `best_candidate`
- `preferred`
- `next_milestone`
- `catalog_version`
- `generated_at`
- `blocking_evidence`
- runtime decision fields
- MSE payload clone (`records` / `dependencies` /
  `blocking_evidence` as a second catalog)

Also forbidden:

- inferred edges
- identities outside the named repository
- a second `repository_id`
- ranking commentary presented as membership

`generated_at` and `cycle_id` remain on
`MilestoneSelectionRuntimeDecision`. They must not migrate onto CIA.

---

## 12. Dependency contract

Only **`PREREQUISITE`** edges are lawful.

### 12.1 Rules

| Rule | Freeze |
| --- | --- |
| Allowed type | Exactly `PREREQUISITE` |
| Silence | Not an edge |
| First-slice default | no dependency edges |
| Endpoints | Both must already be authorized members of the same CIA set |
| Required edge fields | `dependent`, `prerequisite`, `dependency_type = PREREQUISITE`, non-blank `source_identity` |

Do not add `REQUIRED_SUCCESSOR`, `OPTIONAL_SUCCESSOR`, `BLOCKS`,
`RELATED`, `PRIORITY`, `WEIGHT`, or `SCORE`.

Prerequisite satisfaction makes a dependent *possible*, not *next*.

### 12.2 Forbidden inference

Do not infer dependencies from:

- milestone numbers
- roadmap order
- tag order
- filename adjacency
- historical sequence
- architecture prose
- README non-responsibility lists
- document order
- human silence

If no `prerequisite_edges` are written, no prerequisite exists.

### 12.3 Incomplete graphs

If a later grant names an edge whose endpoint is not an authorized
member of that same CIA, the grant is unlawful.

Do not invent a member to complete a graph.

If an unlawful edge were later copied into the runtime catalog, the
engine would fail closed with `UNKNOWN_MILESTONE` or
`MISSING_DEPENDENCY`. That remains correct. It is not a reason to
invent membership.

---

## 13. Ranking-by-omission protection

This is a load-bearing invariant.

```text
catalog record identities
  ==
current CIA authorized identities
```

for the same `repository_id`.

### 13.1 Consequence

If CIA authorizes A and B, the later replacement catalog must contain
both A and B exactly once.

A writer must **not** omit B to force `CONTINUE(A)`.

If A and B are both eligible after lawful field application, the
lawful result is:

```text
STOP(MULTIPLE_ELIGIBLE_MILESTONES)
```

That is success.

### 13.2 Lawful cardinality reduction

Lawful reduction may use only existing record fields:

- `completed`
- `deferred`
- `oob`
- `superseded`

or later separately authorized identity-scoped blocking evidence.

Do **not** add ranking.

### 13.3 Unlawful reduction

The following are not lawful reduction:

- omitting an already-authorized identity from the replacement
  catalog
- omitting an already-authorized identity from a replacement CIA
  without explicit revocation
- informal chat
- review prose
- deleting a name from conversation
- leaving a granted name out of the catalog bytes

The already-frozen human-decision file after
`MULTIPLE_ELIGIBLE_MILESTONES` remains available. It is not a ranking
engine. It requires the catalog bytes themselves to be updated
through the same explicit fields.

### 13.4 Omission of never-authorized names remains lawful

Omitting `PF-M5`, `Automation-M3`, `IRO-M3`, `IRO-M4`, Architecture
State Resolver, or any other never-authorized name is lawful because
those names are not members.

Historical discussion does not make omission ranking.

---

## 14. Grant authority

First-slice membership grant authority:

**HUMAN**

The human authors the written membership set in this tracked
document.

### 14.1 Architecture board

The architecture board may **accept or reject** a written grant.

It does **not** grant by prose.

Board comments, “we prefer X”, and review narrative are not
membership.

Acceptance of this first-slice document accepts the written
zero-identity set. It does not add names.

### 14.2 Actors that must never grant membership

| Actor | Why forbidden |
| --- | --- |
| Supervisor | LLM intra-milestone actor |
| Autopilot | Executor. Must not invent candidates |
| Runtime Adapter | Loader and type-checker only |
| Milestone Selection Engine | Side-effect-free classifier |
| Repository Target | Binds repository. Does not author members |
| roadmap | Prose is not a grant |
| git | Observation is not membership |
| HEAD | Observation is not membership |
| tags | Observation is not membership |
| commits | Observation is not membership |
| LLM | Discovery and preference are forbidden |
| informal chat | Not a machine-readable grant |
| untracked prompts | Not durable JOO authority |
| OOB documents | Non-authoritative |
| silence | Never authorization |

---

## 15. Historical names

Historical discussion is **not** membership.

This document does **not** pre-qualify later candidates.

| Name | Membership status |
| --- | --- |
| `PF-M5` | **NOT AUTHORIZED** |
| `Automation-M3` | **NOT AUTHORIZED** |
| `IRO-M3` | **NOT AUTHORIZED** |
| `IRO-M4` | **NOT AUTHORIZED** |
| Architecture State Resolver | **DEFERRED COMPONENT, NOT AN AUTHORIZED MILESTONE IDENTITY** |

### 15.1 Why none are members

`PF-M5` is a historically discussed opaque string. There is no
tracked PF-M5 architecture. The v7.11 uniqueness review ended
`REVIEW BLOCKED`. Roadmap v1.2 does not name it as unique successor.

`Automation-M3` is a named residual. Its architecture remains
untracked OOB. OOB is non-authoritative.

`IRO-M3` and `IRO-M4` are later-direction mentions, not CIA members.

Architecture State Resolver is a deferred **component**. It is not a
grantable milestone identity.

Milestone Selection Engine already says strings such as `PF-M5` are
legal **opaque identities only**. That is not a membership grant.

### 15.2 No candidate list

A future CIA may name any exact opaque string.

Historical discussion is neither necessary nor sufficient.

This architecture publishes **no** candidate list and does **not**
name successor `X`.

### 15.3 Explicit successor neutrality

```text
PF-M5: NOT AUTHORIZED
Automation-M3: NOT AUTHORIZED
IRO-M3: NOT AUTHORIZED
IRO-M4: NOT AUTHORIZED
Architecture State Resolver: DEFERRED COMPONENT, NOT AN AUTHORIZED
  MILESTONE IDENTITY
any unnamed successor X: NOT AUTHORIZED
```

---

## 16. Record-field ownership

Reuse the existing `MilestoneRecord` field meanings exactly.

Do **not** add fields.

Do **not** persist `ELIGIBLE`, `BLOCKED`, `RANK`, `SCORE`, or
`PRIORITY`.

| Field | Owner | Kind | Eligibility effect |
| --- | --- | --- | --- |
| `identity` | CIA membership grant | Opaque exact string | Subject of later classification only if written into the catalog |
| `completed` | human-attested Boolean | Recorded fact | `True` excludes the identity |
| `deferred` | human / policy Boolean | Explicit policy | `True` excludes the identity |
| `oob` | human / policy Boolean | Explicit authority | `True` excludes the identity |
| `superseded` | human / policy Boolean | Explicit replacement | `True` excludes the identity |
| `architecture_frozen` | human / policy metadata Boolean | Orthogonal metadata | **None** |

### 16.1 `identity`

Granted only by CIA.

The written catalog string, if a later overwrite is authorized, must
be the exact granted opaque string.

Repository-scoped membership does not travel with the string.

### 16.2 `completed`

Human-attested Boolean only in this first slice.

Must not be computed from git, HEAD, tags, commit history,
`COMMIT READY`, or runtime state.

### 16.3 `deferred`, `oob`, `superseded`

These remain explicit human / policy Booleans. They are the lawful
cardinality-reduction fields. They are not ranking scores and not
membership states.

### 16.4 `architecture_frozen`

This remains orthogonal metadata.

`architecture_frozen is True` does not make an identity eligible.
`architecture_frozen is False` does not make an identity eligible.
Frozen is not completed. Frozen is not next. Frozen is not a
lifecycle state. Frozen has no direct eligibility effect.

### 16.5 Derived labels stay derived

`ELIGIBLE` and `BLOCKED` remain derived engine classifications. They
must not be written onto CIA or onto the catalog record.

---

## 17. Architecture State Resolver

Architecture State Resolver remains **DEFERRED**.

CIA must remain **static** and **human-authored**.

### 17.1 CIA must not inspect

CIA must not inspect:

- git
- HEAD
- tags
- dirty tree
- `COMMIT READY`
- review results
- runtime state

CIA must not auto-update the catalog.

### 17.2 Resolver is not a prerequisite

Architecture State Resolver is **not** required before CIA.

Humans may explicitly attest static membership and static Booleans.

Independently already frozen:

- Catalog Expansion §5.2 Option C — resolver-first **rejected as a
  prerequisite**
- Catalog Expansion §11 — humans may attest static catalog facts
- Input Supply §12 — first supply slice must remain smaller than a
  resolver
- Runtime Integration — resolver deferred
- MSE §21 — resolver is a later factual normalizer, not eligibility
  cardinality

### 17.3 Later resolver, if separately authorized

A later Architecture State Resolver may become a factual producer
only after separate architecture approval.

That later component remains outside this owner.

The resolver must not:

- select
- rank
- invent dependencies
- infer product priority
- infer exclusive successors
- repair ambiguity
- parse architecture Markdown into a dependency graph
- grant CIA membership
- auto-mutate the catalog after commit

Combining resolver and selector is forbidden.
Combining resolver and CIA is forbidden.

### 17.4 Structural deferral

```text
Selector Input Supply authors a static CIA grant
Architecture State Resolver is absent
Autopilot keeps live detection
Milestone Selection Engine keeps cardinality
Runtime catalog remains the sole MSE payload
```

---

## 18. Catalog overwrite boundary

CIA does **NOT** authorize catalog overwrite.

### 18.1 Required sequence

```text
Catalog Identity Authorization
        │
        ▼
catalog overwrite authorization
  exact replacement bytes + SHA-256
        │
        ▼
offline selector classification proof
        │
        ▼
separately authorized live Autopilot
        │
        ▼
possible CONTINUE(X)
  only if cardinality is exactly 1
```

Every arrow is a **separate gate**.

Later layers may consume earlier ones. They may not assume them.

### 18.2 Current position

| Gate | Status |
| --- | --- |
| Catalog Expansion architecture | Frozen at `v7.17` |
| Catalog Identity Authorization | This document; first-slice zero identities |
| Catalog overwrite authorization | **NOT AUTHORIZED** |
| Exact replacement bytes + SHA-256 | Not issued; live SHA remains `d36a00d8…` |
| Offline selector classification proof | Not a new proof; current empty world already classifies |
| Live Autopilot | **NOT AUTHORIZED** |
| `CONTINUE(X)` | Not proven; `X` unnamed |

### 18.3 What this document must not do

This document must not:

- overwrite `state/JOO_AUTOMATION/milestone_selection_input.json`
- create `state/JOO/milestone_selection_input.json`
- create `state/milestone_selection_input.json`
- create another runtime file
- change the current live result

The current SHA-256 remains:

```text
d36a00d8a2a0b5f6d369cad89ff4744dae4e5ac6bfaa52f80e6e70f9fd5b9cfa
```

---

## 19. Live Autopilot boundary

CIA does **NOT** authorize live Autopilot.

CIA existence is not an Autopilot invocation.
CIA acceptance is not an Autopilot invocation.
A later non-empty CIA is not an Autopilot invocation.

Autopilot remains a later separate gate.

Autopilot continues to:

- bind the repository first
- keep unused `COMMIT READY` outside the catalog
- refuse to author selector input
- refuse to grant membership
- preserve exact-path staging, dirty-tree fail-closed, OOB safety,
  `next_action` safety, no force push, and no history rewrite

---

## 20. Implementation and downstream gates

CIA does **NOT** authorize implementation of any identity.

There is no selected milestone in this first slice.

Even a later `CONTINUE(X)` does **not** waive:

- architecture review
- implementation authorization
- implementation review
- commit review
- `COMMIT READY`
- exact-path staging
- dirty-tree protection
- OOB protection
- tag authorization
- push authorization
- `next_action` identity enforcement
- no force push
- no history rewrite

`CONTINUE(X)` identifies the successor only.

`CONTINUE(X)` is not architecture approval.
`CONTINUE(X)` is not implementation approval.
`CONTINUE(X)` is not git mutation authority.

Supervisor, after a later lawful `CONTINUE(X)`, may still issue only
`RUN_REVIEW`, `COMMIT`, or `STOP` for that exact identity. Supervisor
may not replace `X` with `Y`.

This document does not name `X`.

---

## 21. First-slice CIA

The first slice must remain successor-neutral.

### 21.1 Frozen first-slice grant

| Field | Value |
| --- | --- |
| Vehicle | this document |
| `repository_id` | `JOO_AUTOMATION` |
| Authorized identity set | **EMPTY** |
| Prerequisite edges | none |
| `JOO` CIA | **not issued** |

No identity is granted.

Therefore all of the following remain unauthorized:

- `PF-M5`
- `Automation-M3`
- `IRO-M3`
- `IRO-M4`
- Architecture State Resolver
- any unnamed successor `X`

### 21.2 Machine-readable first-slice authority block

The current first-slice CIA for `JOO_AUTOMATION` is exactly:

```json
{
  "repository_id": "JOO_AUTOMATION",
  "authorized_identities": []
}
```

This block is authorization text inside this architecture document.

It is **not** a runtime file.
It is **not** loaded by the Runtime Adapter.
It does **not** overwrite the catalog.
It does **not** create another runtime file.
It does **not** change the current live result.

Independent Architecture Review may accept or reject this written
grant as written. Acceptance accepts the empty set. Acceptance does
not add names, overwrite the catalog, authorize live Autopilot, or
authorize implementation.

### 21.3 Correspondence with the live catalog

The live `JOO_AUTOMATION` catalog is the empty explicit closed world.

The first-slice CIA authorized-identity set is empty.

Therefore:

```text
catalog record identities
  ==
current CIA authorized identities
  ==
empty
```

The expected current selector result remains:

```text
STOP(NO_ELIGIBLE_MILESTONE)
```

Current authorized identities:

**NONE**

### 21.4 What the empty grant is not

The zero-identity CIA is not:

- authorization of a successor
- a unique eligible identity
- an implicit `CONTINUE`
- a ranking of remaining work
- a resolver observation
- overwrite authorization
- a repair that invents records

It is a successful fail-safe membership authority whose lawful
catalog correspondence is the already-live empty world.

---

## 22. Future replacement CIA

A later board may separately authorize a **replacement** CIA
membership set for the same `repository_id`.

### 22.1 What a later board may authorize

That later board may authorize:

- zero identities
- one identity
- multiple identities

If multiple identities remain eligible after lawful field
application:

```text
STOP(MULTIPLE_ELIGIBLE_MILESTONES)
```

That is success.

Do **not** add ranking to collapse N to 1.

### 22.2 Replacement vehicle

A later replacement CIA is a later independently accepted tracked
JOO architecture / authority document that contains a replacement
machine-readable block for exactly one `repository_id`.

It is not a host JSON file.
It is not a second runtime catalog.
It is not this document’s first-slice block silently edited into a
non-empty grant.

This first-slice document must not be used as a vehicle for sneaking
in a named successor.

### 22.3 Replacement semantics

The later accepted block **replaces** the prior set.

It does not accumulate.

If it drops a previously authorized identity, that drop is
revocation only when the replacement CIA states the new complete
set without that identity. Reviewers must treat that omission as
explicit replacement, not as silence.

If it keeps a previously authorized identity, the replacement catalog
must still contain that identity.

### 22.4 Successor remains unnamed here

This architecture does **not** name successor `X`.

A later grant may choose a development-infrastructure identity or an
investment-domain identity. Neither class is privileged. Neither
class is granted now.

---

## 23. Test invariants

A later CIA replacement, overwrite, or materialization must prove at
least the following. These tests are not authored by this document.

| # | Invariant | Expected |
| --- | --- | --- |
| 1 | CIA binds exactly one `repository_id` | One grant names exactly `JOO` or `JOO_AUTOMATION` |
| 2 | `JOO` CIA cannot authorize `JOO_AUTOMATION` | Cross-repository grant fails closed |
| 3 | `JOO_AUTOMATION` CIA cannot authorize `JOO` | Cross-repository grant fails closed |
| 4 | Zero identities are lawful | Empty CIA + empty catalog → `STOP(NO_ELIGIBLE_MILESTONE)` |
| 5 | One exact identity membership is deterministic | Exact granted string only; no trim; no case-fold |
| 6 | Multiple memberships are deterministic | Two eligible authorized identities → `STOP(MULTIPLE_ELIGIBLE_MILESTONES)` |
| 7 | Unauthorized identity insertion fails closed | Catalog unchanged; identity rejected |
| 8 | Catalog identity set must equal CIA authorized set | Exact set equality for that `repository_id` |
| 9 | Ranking-by-omission is forbidden | Omitting an already-authorized identity to force `CONTINUE` fails closed |
| 10 | No roadmap inference | Roadmap prose is not a record source |
| 11 | No architecture Markdown inference | Architecture titles, tables, and later-direction sentences are not members |
| 12 | No git / HEAD / tag inference | HEAD, tags, and commits do not populate membership or `completed` |
| 13 | No LLM discovery | Supervisor / chat cannot grant |
| 14 | No un-namespaced alias | `state/milestone_selection_input.json` remains absent |
| 15 | CIA does not overwrite runtime catalog | Live SHA remains unchanged until a later overwrite board |
| 16 | CIA does not authorize live Autopilot | Autopilot remains a later separate gate |
| 17 | CIA does not authorize implementation | No identity may be implemented from CIA alone |
| 18 | CIA does not waive downstream gates | `CONTINUE(X)`, if ever proven, still requires architecture, implementation, review, `COMMIT READY`, staging, tag, and push gates |
| 19 | No second catalog | Adapter still loads only the namespaced runtime file |
| 20 | No compiler | CIA is not compiled into catalog bytes |
| 21 | No resolver implementation | Architecture State Resolver remains deferred and absent |
| 22 | No MSE redesign | Existing engine tests remain green; public API unchanged |
| 23 | No Repository Target redesign | Supported IDs remain `JOO` and `JOO_AUTOMATION` only |
| 24 | No Runtime Integration redesign | Adapter remains loader / hasher / invoker / enforcer |

Normal, boundary, wrong-type, empty-value, order, and exception
propagation cases required by the repository agent contract apply to
every later public writer or materializer entry point, if one is
authorized at all.

If a later grant yields `MULTIPLE`, tests must prove
`STOP(MULTIPLE_ELIGIBLE_MILESTONES)` and that informal chat cannot
resume.

---

## 24. Frozen invariants

1. Owner is Selector Input Supply.
2. Milestone ID remains `UNRESOLVED`.
3. CIA is a human-authored repository-scoped policy grant.
4. The vehicle is this tracked JOO architecture / authority document.
5. CIA is not a runtime state file, review result, second catalog,
   compiler input, ranking artifact, selector result, overwrite
   authorization, live Autopilot authorization, or implementation
   authorization.
6. One CIA binds exactly one `repository_id`.
7. Allowed IDs are exactly `JOO` and `JOO_AUTOMATION`.
8. No trim, case-fold, path inference, cwd inference, or
   cross-repository grant.
9. First-slice CIA binds `JOO_AUTOMATION` only.
10. First-slice authorized identity set is empty.
11. No `JOO` CIA is issued in this first slice.
12. Zero identities are lawful.
13. One CIA authorizes the complete finite membership set.
14. A later accepted CIA replaces the prior set; it does not
    accumulate.
15. Authorized / unauthorized / omitted / revoked meanings are as
    frozen in §8.
16. Silence is not revocation and not membership.
17. `deferred` / `oob` / `superseded` are not membership states.
18. `completed` is human-attested in this first slice.
19. Required CIA keys are `repository_id` and
    `authorized_identities`.
20. Authorized-identity objects, when present, carry `identity`,
    `completed`, `deferred`, `oob`, `superseded`, and
    `architecture_frozen`.
21. Optional edges are explicit `PREREQUISITE` only.
22. First-slice default is no dependency edges.
23. Forbidden CIA fields include rank, priority, score,
    best_candidate, preferred, next_milestone, catalog_version,
    generated_at, blocking_evidence, runtime decision fields, and
    MSE payload clone.
24. Catalog record identities must equal current CIA authorized
    identities for the same `repository_id`.
25. Ranking-by-omission is forbidden.
26. Multiple eligible authorized identities yield
    `STOP(MULTIPLE_ELIGIBLE_MILESTONES)`.
27. First-slice grant authority is HUMAN.
28. The architecture board accepts or rejects; it does not grant by
    prose.
29. Supervisor, Autopilot, adapter, engine, Repository Target,
    roadmap, git, HEAD, tags, commits, LLM, informal chat, untracked
    prompts, OOB documents, and silence must never grant membership.
30. `PF-M5`, `Automation-M3`, `IRO-M3`, and `IRO-M4` are not
    authorized.
31. Architecture State Resolver is a deferred component, not an
    authorized milestone identity.
32. CIA is static and human-authored.
33. CIA does not inspect git, HEAD, tags, dirty tree,
    `COMMIT READY`, review results, or runtime state.
34. CIA does not auto-update the catalog.
35. CIA does not authorize catalog overwrite.
36. CIA does not authorize live Autopilot.
37. CIA does not authorize implementation.
38. CIA does not waive downstream gates.
39. No second catalog, compiler, host CIA file, or resolver
    implementation is authorized.
40. No MSE, Repository Target, or Runtime Integration redesign is
    authorized.
41. Current live result remains `STOP(NO_ELIGIBLE_MILESTONE)`.
42. Current authorized identities remain NONE.
43. This document does not authorize commit, tag, or push.
44. Development automation must not distort JOO's
    investment-product architecture.

---

## 25. Authoring-time authority state

| Question | Answer |
| --- | --- |
| Architecture document authored | Yes |
| Independent architecture review | Required next |
| Implementation authorized | **NO** |
| Catalog Identity Authorization vehicle created | **YES** — this document |
| First-slice CIA membership set | **ZERO AUTHORIZED IDENTITIES** for `JOO_AUTOMATION` |
| Currently authorized catalog identities | **NONE** |
| `JOO` CIA issued | **NO** |
| Human overwrite of the live file authorized | **NO** |
| Selector input bytes changed by this document | **NO** |
| Host state CIA file created | **NO** |
| Separate CIA JSON created | **NO** |
| Second runtime catalog created | **NO** |
| Catalog compiler created | **NO** |
| `PF-M5` authorized | **NO** |
| `Automation-M3` authorized | **NO** |
| `IRO-M3` / `IRO-M4` authorized | **NO** |
| Architecture State Resolver | **DEFERRED** |
| Resolver required before CIA | **NO** |
| Milestone Selection Engine redesign | **NO** |
| Runtime Integration redesign | **NO** |
| Repository Target redesign | **NO** |
| Supervisor / safe-fastpath / `COMMIT READY` / `next_action` redesign | **NO** |
| Roadmap parsing | **NO** |
| LLM discovery | **NO** |
| Unique successor authorized | **NO** |
| `CONTINUE(X)` proven | **NO** |
| Automatic continuation loop | **NO** |
| Commit / tag / push authorized | **NO** |
| Live Autopilot authorized | **NO** |
| Milestone ID | **UNRESOLVED** |
| Owner | **Selector Input Supply** |
| Target repository | `JOO_AUTOMATION` |
| First-slice live payload | Empty explicit closed world |
| Current live result | `STOP(NO_ELIGIBLE_MILESTONE)` |
| Expected result until later replacement CIA + overwrite | `STOP(NO_ELIGIBLE_MILESTONE)` |
| Next action | Independent Architecture Review |

Until a later replacement CIA and overwrite are separately authorized
and completed, live Autopilot must continue to treat the current
empty `JOO_AUTOMATION` catalog as
`STOP(NO_ELIGIBLE_MILESTONE)`. That remains the correct live outcome.

---

## 26. Final readiness statement

This document freezes the smallest lawful Catalog Identity
Authorization contract:

- owner remains Selector Input Supply
- CIA is a human-authored repository-scoped policy grant
- the vehicle is this tracked JOO architecture / authority document
- one CIA binds exactly one `repository_id`
- one CIA authorizes the complete finite membership set
- the first-slice `JOO_AUTOMATION` set is empty
- no `JOO` CIA is issued
- ranking-by-omission is forbidden
- Architecture State Resolver stays deferred
- overwrite, live Autopilot, and implementation remain unauthorized
- `CONTINUE(X)` is not proven and waives no downstream gate

This document is ready for Independent Architecture Review.

It is not ready for a non-empty membership grant.
It is not ready for overwrite.
It is not ready for implementation.
It is not ready for live Autopilot.

The current live selector state remains the correct fail-safe:

```text
STOP(NO_ELIGIBLE_MILESTONE)
```
