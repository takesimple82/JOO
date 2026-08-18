# Milestone Selection Catalog Expansion Architecture

## Status and identity

- Status: Architecture authored for independent review; catalog-expansion
  contract freeze only
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Development infrastructure** — not an investment-domain plane
- Capability: **Milestone Selection Catalog Expansion**
- Owner: **Selector Input Supply**
- Milestone ID: **UNRESOLVED**
- This document does **not** invent or assign `Automation-M4`,
  `Autopilot-M1`, `M55+`, `PF-M5`, `Automation-M3`, `IRO-M3`,
  `IRO-M4`, Architecture State Resolver, or any other manufactured
  successor identity
- Authorizing direction review: Architecture Review Board
  (`~/JOO-Automation/results/milestone_selection_catalog_expansion_architecture_review/latest.md`)
  — **FINAL DECISION: CATALOG EXPANSION ARCHITECTURE READY**
- Production location (later, not created by this document): the
  already-specified Autopilot host artifact
  `state/<repository_id>/milestone_selection_input.json` under
  JOO-Automation. Not a JOO investment package, not an extension of
  `joo_auto`, not a second catalog JSON, and not a resolver module
- Repository boundary for this document: architecture authoring only;
  this document alone authorizes no production code, test, package
  change, schema module, configuration, run artifact, selector-input
  overwrite, Catalog Identity Authorization artifact, Supervisor
  prompt rewrite, Autopilot runtime change, or Git history mutation

This document freezes the **smallest lawful architecture** for expanding
the already-materialized empty repository-scoped selector catalog into a
later non-empty explicit closed world.

It answers only:

> How may a later authorized non-empty closed world replace the already
> authorized empty `milestone_selection_input.json` without inventing
> identities, ranking among historical names, parsing prose, creating a
> second catalog source, or standing up Architecture State Resolver?

It does **not** answer:

> What milestone should be built next, and may Autopilot now continue?

This document does **not** redesign:

- Milestone Selection Engine first-slice models or cardinality rules
- Milestone Selection Engine Runtime Integration
- Milestone Selection Input Supply empty-world first slice
- Autopilot Repository Target Abstraction
- Autopilot v5 safe-fastpath
- Supervisor action vocabulary (`RUN_REVIEW` / `COMMIT` / `STOP`)
- `COMMIT READY` single-consumption
- `next_action` schema
- JOO investment-domain architecture

Implementation is **not** authorized.

Overwrite of the live empty catalog is **not** authorized.

Catalog Identity Authorization is **defined**, not created.

No catalog identity is granted.

Architecture State Resolver remains **DEFERRED**.

---

## 1. Purpose

Runtime Integration already consumes exactly one file:

```text
state/<repository_id>/milestone_selection_input.json
```

Selector Input Supply already froze the first-slice authoring contract.
That first slice is the **empty explicit closed world**. It is already
materialized for `JOO_AUTOMATION`.

The live engine result is therefore:

```text
STOP(NO_ELIGIBLE_MILESTONE)
stop_source=ENGINE
selected_identity=none
```

That result is expected and correct. An empty closed world is not a
defect in the engine, the adapter, Repository Target, Supervisor, or
Autopilot.

The unique remaining architectural gap is **lawful expansion**: how a
later non-empty explicit closed world may replace those empty bytes.

This architecture adds exactly one responsibility to the existing
Selector Input Supply owner:

**Selector Input Supply owns the expansion / overwrite contract of the
already-specified explicit selector catalog.**

It does not own eligibility classification.
It does not own runtime consumption.
It does not own repository binding.
It does not observe git.
It does not invent a successor.
It does not grant catalog membership by existing.

The architectural benefit of this freeze is not that Autopilot starts
building a successor. The benefit is that a later membership grant can
become overwrite-safe, repository-scoped, ranking-free, and
identity-explicit without opening a second source of truth.

---

## 2. Current checkpoint

This architecture is authored only after independent re-verification.
Material state matches the authorizing direction review.

### 2.1 JOO

| Check | Value |
| --- | --- |
| Path | `/Users/takesimple/Projects/JOO` |
| Branch | `feature/stage2-provider-runtime` |
| HEAD | `8ca243cab29ca0ef7160484745a31fda66c32e5e` |
| Exact tag at HEAD | `v7.16-stage5-milestone-selection-input-supply-architecture` |
| HEAD subject | Add Milestone Selection Input Supply architecture |
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
product direction only. It is not a catalog.

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

Namespaced live selector-owned cycle after empty-world materialization:

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
| Unused namespaced `COMMIT READY` | none |
| Supervisor `next_action` | `STOP` |

Current exact input:

```json
{
  "records": [],
  "dependencies": [],
  "blocking_evidence": []
}
```

`state/JOO/milestone_selection_input.json` is absent.
`state/milestone_selection_input.json` must not exist and must not be
created.

This `STOP` is the successful fail-safe already authorized by `v7.16`.
It is not a defect. This architecture must leave those bytes unchanged.

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
Architecture State Resolver is absent
Catalog Identity Authorization is absent
Non-empty catalog overwrite is unauthorized
Selector Input Supply expansion contract is the unique remaining freeze
```

This document freezes only the missing expansion contract. It does not
replace the deferred resolver and does not grant membership.

---

## 3. Owner

The exact owner remains:

**Selector Input Supply**

Milestone ID remains:

**UNRESOLVED**

Do not create another owner.

Catalog expansion is the same owner’s next contract, not a new
component, not a numbered milestone, and not Architecture State
Resolver.

### 3.1 What this owner may decide

Selector Input Supply may freeze:

- that the sole runtime catalog remains the already-specified file
- that expansion of a present catalog is overwrite
- that overwrite defaults to fail-closed
- that catalog membership requires a later Catalog Identity
  Authorization
- record-field, dependency, and blocking-evidence ownership for the
  first non-empty slice
- repository isolation of expansion
- the prohibition on inference, ranking, ranking-by-omission, and
  automatic mutation

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

This is a development-infrastructure owner. It is not a numbered
milestone. It is not `Automation-M4`, `Autopilot-M1`, or Architecture
State Resolver.

### 3.3 Ownership that does not move

| Actor | Still owns | Must not gain |
| --- | --- | --- |
| Selector Input Supply | Lawful authoring and later expansion contract of the explicit input file | Eligibility; git observation; repository choice; ranking; membership grants by silence |
| Human | Writer of exact authorized replacement bytes after later overwrite authorization | Informal chat as autonomy |
| Later Catalog Identity Authorization | Explicit closed-world membership grants, repository-scoped | Preference, score, “best next”, runtime catalog authority |
| Milestone Selection Engine | Eligibility cardinality; `CONTINUE` / `STOP` | File authoring |
| Runtime Adapter | Load, type-check, hash raw bytes, persist decision | File authoring, repair, overwrite |
| Autopilot Repository Target | Allowlisted target bind; `AutopilotExecutionContext` | Successor identity or catalog authorship |
| Supervisor | Intra-milestone `RUN_REVIEW` / `COMMIT` / `STOP` for an already selected identity | Independent successor choice or record invention |
| Autopilot runtime | Safety gates; exact-path staging; `COMMIT READY` single-consumption; tag/push authorization | Computing, ranking, or writing selector input |
| Architecture State Resolver | Nothing yet. Deferred | Hidden selector or automatic catalog mutation |
| `COMMIT READY` / commit-review | Unused versus consumed commit authority | Successor identity or `blocking_evidence` authorship in this slice |

---

## 4. Non-responsibilities

This architecture does **not** include, authorize, or implement:

- `PF-M5`
- `Automation-M3`
- `IRO-M3`
- `IRO-M4`
- Architecture State Resolver
- any historical completed identity as a catalog backfill
- roadmap parsing
- Markdown parsing
- README parsing
- Constitution parsing
- LLM milestone discovery
- ranking, scoring, preference, or best-candidate selection
- automatic prerequisite inference
- automatic completion inference
- automatic blocking-evidence authoring
- catalog compiler
- static duplicate catalog JSON
- milestone registry product
- authoring UI
- automatic catalog update
- unbounded successor continuation
- Repository Target redesign
- Milestone Selection Engine redesign
- Runtime Integration redesign
- Supervisor action redesign
- `COMMIT READY` redesign
- `next_action` redesign
- safe-fastpath redesign
- third repositories
- `joo_auto` milestone reuse
- overwrite of the live empty file
- creation of a Catalog Identity Authorization artifact
- naming of a successor `X`
- commit
- tag
- push
- live Autopilot

The two known JOO OOB documents remain non-authoritative.

---

## 5. Catalog authority

### 5.1 Chosen option

**Option A — DIRECT EXPLICIT RUNTIME CATALOG EXPANSION**

The sole runtime catalog remains:

```text
state/<repository_id>/milestone_selection_input.json
```

under the Autopilot host (`~/JOO-Automation`).

A later JOO architecture/review artifact may freeze membership and a
later overwrite board may freeze exact replacement bytes. Those
artifacts are **authorization**, not a second runtime source.

### 5.2 Rejected catalog authorities

| Option | Decision | Why |
| --- | --- | --- |
| B. Separate static catalog JSON later compiled into runtime input | **Rejected** | Unnecessary duplicate truth. Invites a compiler. Makes runtime input derived rather than authoritative |
| C. Architecture State Resolver first | **Rejected as a prerequisite** | Humans may attest static catalog facts. Resolver is not required before a non-empty catalog is lawful |
| D. No lawful catalog source exists | **Rejected** | A lawful source exists: explicit human / board membership grants written into the already-frozen runtime file |

Do **not** create:

- a separate static catalog JSON
- a catalog compiler
- a second source of truth
- Architecture State Resolver
- a roadmap parser
- a Markdown parser
- LLM milestone discovery
- a ranking engine

### 5.3 Authority chain

```text
Later Catalog Identity Authorization
  JOO architecture/review artifact
  explicit repository-scoped membership grant
        │
        ▼
Later Overwrite / Materialization Authorization
  exact replacement bytes + SHA-256
        │
        ▼
HUMAN
  writes those exact bytes
        │
        ▼
Selector Input Supply
  expansion / overwrite contract
        │
        ▼
state/<repository_id>/milestone_selection_input.json
  sole runtime catalog
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
Architecture existence is never overwrite authorization.

### 5.4 Payload law preserved

The file remains the Milestone Selection Engine payload. Top-level
keys remain exactly:

```text
records
dependencies
blocking_evidence
```

No other top-level key is lawful.

Forbidden envelope fields remain forbidden, including at least:

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

Do not add `catalog_version`. Catalog history and auditability come
from:

1. the architecture / review authorization
2. the exact replacement bytes
3. the raw SHA-256 `input_identity`

not from an in-file version field.

---

## 6. Catalog Identity Authorization

### 6.1 Rule

A milestone identity may enter a repository-scoped selector catalog
**only after** a separate Catalog Identity Authorization explicitly
grants that exact opaque identity membership in that exact repository
namespace.

Catalog Identity Authorization must be:

- explicit
- machine-readable
- repository-scoped
- exact-string based
- ranking-free

It is a **membership grant**.

It is not:

- priority
- score
- preference
- best candidate
- roadmap inference
- historical sequence
- LLM recommendation
- overwrite authorization
- `CONTINUE(X)`
- implementation authority

### 6.2 Chosen representation

**Catalog Identity Authorization is a later JOO architecture/review
artifact.**

It is not a host `state/` file.
It is not a second runtime catalog JSON.
It is not an input the Runtime Adapter loads.

This is the smallest design that does not create a second runtime
catalog source. The empty-world pattern is reused:

- architecture / review freezes the grant
- a later overwrite board freezes exact bytes
- a human writes those bytes
- the adapter only loads the sole runtime file

A host-adjacent authorization file such as
`state/<repository_id>/catalog_identity_authorization.json` is
**rejected**. It would sit beside the runtime catalog and invite the
adapter or a compiler to treat it as a second source.

Exact later filename is deferred to the Catalog Identity Authorization
review. The later artifact belongs under tracked JOO
`docs/automation/` and/or the independent review that accepts it. This
document does **not** create that artifact.

### 6.3 Minimum machine-readable content

A later Catalog Identity Authorization must name, at minimum:

| Field | Rule |
| --- | --- |
| `repository_id` | Exact allowlisted ID: `JOO` or `JOO_AUTOMATION` |
| authorized identities | Finite explicit list. May be empty. Silence is not a member |
| for each identity: exact identity string | Opaque, non-blank, no trim, no case-fold |
| for each identity: `completed` | Exact Boolean |
| for each identity: `deferred` | Exact Boolean |
| for each identity: `oob` | Exact Boolean |
| for each identity: `superseded` | Exact Boolean |
| for each identity: `architecture_frozen` | Exact Boolean metadata |

Optional dependencies, if present at all:

- only explicit `PREREQUISITE` edges
- both endpoints already authorized catalog members
- each edge names `dependent`, `prerequisite`,
  `dependency_type = PREREQUISITE`, and non-blank `source_identity`

Forbidden in the grant:

- `rank`
- `priority`
- `score`
- `best_candidate`
- narrative preference
- “next milestone”
- inferred edges
- identities outside the named repository

One Catalog Identity Authorization artifact authorizes **exactly one**
`repository_id`. A `JOO_AUTOMATION` grant does not authorize a `JOO`
catalog. The reverse is also true.

### 6.4 Current membership

Currently authorized catalog identities:

**NONE**

This architecture does **not** grant membership to:

- `PF-M5`
- `Automation-M3`
- `IRO-M3`
- `IRO-M4`
- Architecture State Resolver
- any other identity

This architecture does **not** name a successor `X`.

Existing strings remain legal **opaque strings only**. They are not
catalog members until a later grant names them.

### 6.5 Lawful identity sources

Only these sources may introduce a catalog identity:

1. **A later Catalog Identity Authorization** that names the exact
   opaque string, the exact `repository_id`, and the exact Boolean
   fields for that record.
2. **The human write of those exact authorized bytes** into
   `state/<repository_id>/milestone_selection_input.json`, after a
   separate overwrite / materialization authorization.

“Separately accepted architecture artifacts” may participate **only**
as the vehicle of that explicit grant. They may not be mined for
names.

A later grant may name a development-infrastructure identity or an
investment-domain identity. Neither class is privileged. Neither class
is currently granted.

### 6.6 Explicitly rejected identity sources

Do not introduce identities from:

- roadmap Markdown, including v1.2 Stage 5 / Stage 6 prose
- Constitution prose
- architecture document titles
- architecture document paths
- architecture Markdown tables or “later direction” sentences
- README files
- review prose, including “human selected PF-M5”
- untracked prompts
- informal chat
- silence
- git tags
- commits
- HEAD
- commit dates
- filenames
- document order
- version number
- milestone number
- Supervisor diagnostic labels
- `joo_auto` milestone manifests
- OOB documents, including Product Architecture and Automation-M3
- LLM discovery
- historical references to `PF-M5`, `Automation-M3`, `IRO-M3`,
  `IRO-M4`, or Architecture State Resolver

---

## 7. Identity contract

Milestone identities remain:

- explicit
- opaque
- exact
- caller-supplied
- non-blank
- free of ordering semantics
- free of priority semantics

Additional invariants that this expansion architecture must preserve,
not weaken:

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
9. No discovery from filenames, tags, commits, prompts, or Markdown.
10. Membership is repository-scoped. The same opaque string is not a
    member of another namespace unless that namespace has its own
    grant.

Catalog membership is not eligibility.
Catalog membership is not uniqueness.
Catalog membership is not `CONTINUE`.

An identity becomes a catalog member only by Catalog Identity
Authorization for that exact repository. Eligibility remains the
engine’s derived classification of the supplied record fields.

Supervisor labels such as `post-repository-target-abstraction` remain
non-identities.

---

## 8. Record-field ownership

Reuse the existing `MilestoneRecord` model exactly.

Do **not** add fields.

Do **not** persist `ELIGIBLE`, `BLOCKED`, `RANK`, `SCORE`, or
`PRIORITY`.

| Field | Kind | First non-empty slice producer | Live observation? |
| --- | --- | --- | --- |
| `identity` | Opaque policy membership | Granted only by Catalog Identity Authorization, then written by the human | No |
| `completed` | Recorded fact | Human-attested Boolean only | **Must not** be computed from git, HEAD, tag, commit, or `COMMIT READY` |
| `deferred` | Explicit policy Boolean | Human / Catalog Identity Authorization | Policy |
| `oob` | Explicit authority Boolean | Human / Catalog Identity Authorization | Policy |
| `superseded` | Explicit replacement Boolean | Human / Catalog Identity Authorization | Policy |
| `architecture_frozen` | Explicit metadata Boolean | Human / Catalog Identity Authorization | Policy metadata. **No eligibility effect** |

### 8.1 `identity`

Granted only by Catalog Identity Authorization.

The written string must be the exact granted opaque string.
Repository-scoped membership does not travel with the string.

### 8.2 `completed`

In the first non-empty slice, `completed` is a human-attested fact.

The supplier must **not** compute it from:

- git
- HEAD
- exact tag
- commit history
- consumed or unused `COMMIT READY`

A later Architecture State Resolver may become the factual producer of
`completed` only after a separate architecture approval. That approval
is not this document.

### 8.3 `deferred`, `oob`, `superseded`

These remain explicit human / policy Booleans. They are the lawful
cardinality-reduction fields. They are not ranking scores.

### 8.4 `architecture_frozen`

This remains orthogonal metadata.

`architecture_frozen is True` does not make an identity eligible.
`architecture_frozen is False` does not make an identity eligible.
Frozen is not completed. Frozen is not next. Frozen is not a
lifecycle state.

### 8.5 Derived labels stay derived

`ELIGIBLE` and `BLOCKED` remain derived engine classifications. They
must not be written onto the catalog record.

Contradictory `completed is True` and `oob is True` remains engine
`AMBIGUOUS_ARCHITECTURE_STATE`. Do not “repair” it in the file.

---

## 9. Dependency ownership

Only the existing `PREREQUISITE` dependency type is lawful.

Do not add `REQUIRED_SUCCESSOR`, `OPTIONAL_SUCCESSOR`, `BLOCKS`,
`RELATED`, `PRIORITY`, `WEIGHT`, or `SCORE`.

| Rule | Freeze |
| --- | --- |
| Who may define an edge | Human / Catalog Identity Authorization only |
| Required fields | `dependent`, `prerequisite`, `dependency_type = PREREQUISITE`, non-blank `source_identity` |
| Silence | Not an edge |
| First non-empty slice default | `dependencies = []` |
| Exception | The same later membership grant explicitly authorizes exact edges |
| Endpoints | Both must already be authorized catalog members |
| Forbidden inference | Milestone numbers, historical sequencing, filename adjacency, tag sequence, roadmap order |

Prerequisite satisfaction makes a dependent *possible*, not *next*.
Completing a prerequisite must not be treated as uniqueness.

If a later grant names an edge whose endpoint is not a catalog member,
the engine fail-closes with `UNKNOWN_MILESTONE` or
`MISSING_DEPENDENCY`. That is correct. Do not invent records to
complete a graph.

---

## 10. Blocking-evidence boundary

For the first non-empty catalog slice:

```text
blocking_evidence = []
```

must remain the default.

Do **not** convert any of the following into selector
`BlockingEvidence`:

- dirty working tree
- unused `COMMIT READY`
- review remediation
- unresolved review tokens
- OOB presence
- runtime blockers
- Supervisor narrative

Those remain Autopilot-owned live gates **outside** selector input.
Unused `COMMIT READY` continues to block selector invocation even if a
later file contains exactly one eligible identity.

Identity-scoped blocking evidence may become lawful only in a later
slice, and only when separately authorized. It is not part of the
first non-empty default.

The adapter must not author, discover, or normalize blocking evidence.

---

## 11. Architecture State Resolver deferral

Architecture State Resolver remains **DEFERRED**.

Architecture State Resolver is **NOT** required before a non-empty
catalog is lawful.

Humans may explicitly attest static catalog facts.

The first non-empty slice must not:

- inspect git
- inspect HEAD
- inspect tags
- mark `completed` automatically
- parse Markdown
- auto-update the catalog
- normalize `COMMIT READY`
- normalize dirty tree
- create blocking evidence
- select or rank milestones

### 11.1 Later resolver, if separately authorized

A later resolver may become a separately authorized factual producer
of recorded facts and blocking evidence.

That later component remains outside this owner. Combining resolver
and selector is forbidden.

The resolver must not:

- select
- rank
- invent dependencies
- infer product priority
- infer exclusive successors
- repair ambiguity
- parse architecture Markdown into a dependency graph
- auto-mutate the catalog after commit

### 11.2 Structural deferral

```text
Selector Input Supply authors / expands a static explicit object
Architecture State Resolver is absent
Autopilot keeps live detection
Milestone Selection Engine keeps cardinality
```

Deferring the resolver does not block a later non-empty catalog. It
blocks only live observation as a hidden author.

---

## 12. Repository isolation

Catalog expansion must be separately authorized per repository.

Lawful runtime paths remain only:

```text
state/JOO/milestone_selection_input.json
state/JOO_AUTOMATION/milestone_selection_input.json
```

under the Autopilot host.

### 12.1 Current live catalogs

| Namespace | Catalog state |
| --- | --- |
| `JOO_AUTOMATION` | Empty explicit closed world present |
| `JOO` | Absent |
| un-namespaced `state/milestone_selection_input.json` | Must remain absent |

Authorizing expansion of `JOO_AUTOMATION` does not create or authorize
a `JOO` catalog. The reverse is also true.

A missing `JOO` catalog remains independent
`STOP(MISSING_SELECTOR_INPUT)` until its own file is separately
authorized and materialized.

### 12.2 Isolation rules

- No cross-repository copy without separate authorization
- Copying bytes from one namespace into the other is a new write
- No un-namespaced alias
- No cwd inference
- No filesystem-path inference
- No environment inference
- `"JOO "` ≠ `"JOO"`
- `"joo"` is unknown
- `"JOO-AUTOMATION"` is unknown

The engine never chooses a repository. Selector Input Supply never
chooses a repository. Expansion happens only inside one already-bound
namespace.

Repository Target still binds the repository **before** selection.

When the target is `JOO_AUTOMATION`, these files live under protected
host `state/` and must not become stage candidates or target dirt.

---

## 13. Existing empty-world catalog

The `JOO_AUTOMATION` empty catalog already exists and is already the
authorized first-slice object from `v7.16`.

Current exact bytes remain:

```text
{
  "records": [],
  "dependencies": [],
  "blocking_evidence": []
}
```

with LF newlines, exactly two-space indentation, one space after each
colon, no BOM, no trailing spaces, and exactly one trailing newline.

Current SHA-256 remains:

```text
d36a00d8a2a0b5f6d369cad89ff4744dae4e5ac6bfaa52f80e6e70f9fd5b9cfa
```

This architecture must not rewrite those bytes.

The empty world remains lawful until a later overwrite is separately
authorized. After this document exists, the lawful live classification
remains:

```text
STOP(NO_ELIGIBLE_MILESTONE)
```

Absence of a `JOO` file remains distinct from this empty present file.
This document does not collapse that distinction.

---

## 14. Overwrite contract

Because the `JOO_AUTOMATION` empty catalog already exists, every
non-empty `JOO_AUTOMATION` catalog is a **REPLACEMENT / OVERWRITE**.

### 14.1 Default

```text
overwrite default = FAIL CLOSED
```

No overwrite may occur merely because this architecture exists.
No overwrite may occur merely because a later membership grant exists.
No overwrite may occur because a reviewer prefers a successor.

### 14.2 Required authorities before any replacement

Before any replacement of namespaced catalog bytes, require separately:

1. Catalog Expansion architecture frozen
2. Catalog Identity Authorization for exact repository membership
3. Overwrite / Materialization Authorization
4. Exact replacement bytes
5. Exact SHA-256
6. Offline selector classification proof
7. Namespace isolation proof

This document supplies only item 1 as a candidate freeze. It supplies
none of items 2–7.

### 14.3 Writer

Writer:

**HUMAN**

Prefer:

**NO NEW RUNTIME MODULE**

A later review may authorize a tiny deterministic materializer only if
it proves that manual exact-byte overwrite is insufficient to prove
namespace isolation, overwrite refusal, or byte-identity invariants.
No such module is authorized now.

### 14.4 Adapter remains a loader

The Runtime Adapter must not:

- overwrite
- rewrite
- pretty-print
- sort
- canonicalize
- repair

The adapter continues to load, type-check, hash raw bytes, invoke the
existing engine, persist the decision, inject the selection block, and
validate `next_action` identity.

### 14.5 After a later lawful write

If a later board authorizes replacement:

- previous `input_identity`
  `d36a00d8a2a0b5f6d369cad89ff4744dae4e5ac6bfaa52f80e6e70f9fd5b9cfa`
  becomes stale
- Runtime Integration already fail-closes stale decisions
- the next inter-milestone cycle must recompute
- the consumed empty-world decision must not authorize the new cycle

Formatting remains material. Any whitespace or key-order change is a
different catalog.

---

## 15. Raw-byte input_identity

Preserve the already-frozen Runtime Integration contract:

```text
input_identity = SHA-256(raw file bytes)
```

No canonicalization.

Invariants:

1. Same exact bytes produce the same `input_identity`.
2. Any whitespace, formatting, or content change produces a different
   `input_identity`.
3. The adapter must not canonicalize, pretty-print, sort, or rewrite
   the file to compute identity.
4. Do not add `catalog_version`.
5. Catalog history / auditability comes from the architecture/review
   authorization, the exact replacement bytes, and the raw SHA-256.

The supplier must not introduce a second identity scheme.

---

## 16. Ranking-by-omission prohibition

This is a load-bearing invariant.

**Omitting an identity that has no Catalog Identity Authorization is
lawful.**

**Omitting an identity that already has a Catalog Identity
Authorization merely to force cardinality 1 is hidden ranking and
forbidden.**

If multiple separately-authorized identities remain eligible, the
lawful result is:

```text
STOP(MULTIPLE_ELIGIBLE_MILESTONES)
```

Do not rank them.

Lawful cardinality reduction remains only through existing explicit
fields:

- `deferred`
- `oob`
- `superseded`

or separately authorized identity-scoped blocking evidence in a later
slice.

The already-frozen human-decision file after
`MULTIPLE_ELIGIBLE_MILESTONES` remains available. It is not a ranking
engine. It requires the catalog bytes themselves to be updated through
those same explicit fields.

Informal chat, deleting one name from a conversation, or leaving an
already-granted eligible identity out of the replacement bytes is not
a lawful reduction.

If a later grant names A and B as independently eligible, the
replacement catalog must contain both. The engine must then
`STOP(MULTIPLE_ELIGIBLE_MILESTONES)`. That is success.

---

## 17. First non-empty catalog shape

This architecture freezes the **SHAPE** only.

It does **not** authorize the actual contents yet.

First non-empty catalog shape:

```json
{
  "records": [
    "...only separately authorized catalog identities..."
  ],
  "dependencies": [],
  "blocking_evidence": []
}
```

unless a later Catalog Identity Authorization explicitly grants
dependencies.

Each record, if later authorized, remains exactly the existing
`MilestoneRecord`:

- `identity`
- `completed`
- `deferred`
- `oob`
- `superseded`
- `architecture_frozen`

No ranking, score, priority, source-document, next-milestone, or
catalog-version fields.

The first non-empty catalog:

- may later contain zero, one, or many records
- may later contain exactly one eligible record if and only if that is
  the true authorized closed world
- must not be pre-filled with historical completed identities to
  “complete the graph”
- must not insert an identity into this architecture document as the
  selected next milestone

This document therefore populates **no** record, **no** dependency,
and **no** blocking-evidence object.

---

## 18. CONTINUE(X) proof conditions

This architecture does **not** prove `CONTINUE(X)`.

The current empty bytes must continue to classify as
`STOP(NO_ELIGIBLE_MILESTONE)`.

`CONTINUE(X)` may be proven later only when **all** of the following
are true:

1. Catalog Identity Authorization exists.
2. Exact replacement catalog bytes are authorized.
3. The runtime input is repository-scoped.
4. The engine classifies exactly one eligible identity.
5. Blocking evidence remains lawful.
6. Offline tests prove the exact `CONTINUE(X)`.
7. Overwrite authorization exists.
8. Live Autopilot is separately authorized.

`CONTINUE(X)` identifies the successor only.

`X` remains unnamed by this document. A later grant may choose a
development-infrastructure identity or an investment-domain identity.
Neither is granted now.

---

## 19. Downstream gates CONTINUE does not waive

`CONTINUE(X)` does **not** waive:

- architecture review for `X`
- implementation authorization
- implementation review
- implementation commit review
- `COMMIT READY`
- exact-path staging
- dirty-tree fail closed
- OOB protection
- tag authorization
- push authorization
- `next_action` identity enforcement
- no force push
- no history rewrite
- no arbitrary repository targeting
- repository-scoped single-consumption of `COMMIT READY`
- the requirement that `next_action` identity equal `X`

`CONTINUE(X)` is not architecture approval.
`CONTINUE(X)` is not implementation approval.
`CONTINUE(X)` is not git mutation authority.

Supervisor, after a later lawful `CONTINUE(X)`, may still issue only
`RUN_REVIEW`, `COMMIT`, or `STOP` for that exact identity. Supervisor
may not replace `X` with `Y`.

---

## 20. Test invariants

A later implementation, overwrite, or materialization must prove at
least the following. These tests are not authored by this document.

| # | Invariant | Expected |
| --- | --- | --- |
| 1 | Existing empty bytes still return `NO_ELIGIBLE_MILESTONE` | SHA `d36a00d8…` classifies as engine `STOP`; no successor invented |
| 2 | Unauthorized overwrite fails closed | File bytes unchanged |
| 3 | Unauthorized identity insertion fails closed | No identity enters the catalog without a Catalog Identity Authorization |
| 4 | Exact authorized identity membership only | Written identities equal the granted opaque strings |
| 5 | Repository mismatch fails closed | A `JOO` grant cannot write `JOO_AUTOMATION`, and the reverse |
| 6 | `JOO` catalog remains absent unless independently authorized | `JOO` stays `MISSING_SELECTOR_INPUT` |
| 7 | No un-namespaced alias | `state/milestone_selection_input.json` is not read and must not be created |
| 8 | No roadmap / Markdown / README parsing | Writer / tests do not mine prose for identities |
| 9 | No git / HEAD / tag inference | HEAD, tags, and commits do not populate records or `completed` |
| 10 | No `COMMIT READY` conversion | Unused authority stays outside `blocking_evidence` and still blocks invocation |
| 11 | No ranking fields | Payload has no `priority`, `score`, `rank`, `next_milestone`, or `catalog_version` |
| 12 | Raw-byte SHA change produces different `input_identity` | Any whitespace or content change is a new digest |
| 13 | Same exact bytes produce same `input_identity` | SHA-256 of raw bytes is stable |
| 14 | One eligible authorized identity → `CONTINUE` exact identity | No trim, no case-fold, exact string |
| 15 | Multiple eligible authorized identities → `STOP(MULTIPLE_ELIGIBLE_MILESTONES)` | No ranking |
| 16 | Zero eligible identities → `STOP(NO_ELIGIBLE_MILESTONE)` | Lawful empty or fully excluded authorized set |
| 17 | Omission of an already-authorized eligible identity to force cardinality 1 is forbidden | Hidden ranking fails closed |
| 18 | No MSE package change | Existing engine tests remain green; public API unchanged |
| 19 | No Repository Target change | Supported IDs remain `JOO` and `JOO_AUTOMATION` only |
| 20 | No Runtime Integration redesign | Adapter remains loader / hasher / invoker / enforcer |
| 21 | `CONTINUE` does not waive downstream gates | §19 remains mandatory after any later `CONTINUE(X)` |

Normal, boundary, wrong-type, empty-value, order, and exception
propagation cases required by the repository agent contract apply to
every later public writer or materializer entry point, if one is
authorized at all.

If a later grant yields `MULTIPLE`, tests must prove
`STOP(MULTIPLE_ELIGIBLE_MILESTONES)` and that informal chat cannot
resume.

---

## 21. First later authorization boundary

This document authorizes **no** implementation and **no** overwrite.

Preferred later sequence after this architecture is independently
accepted:

```text
1. Catalog Identity Authorization review
2. exact overwrite / materialization authorization
3. offline classification proof
4. live Autopilot proof
```

No new runtime module unless a later review proves manual exact-byte
overwrite is insufficient.

### 21.1 Immediately after this freeze

If this architecture is accepted, the next artifact is the Catalog
Identity Authorization review / freeze.

That later review may:

- grant zero identities, which keeps the empty world lawful
- grant one or more exact opaque identities for exactly one
  `repository_id`
- set explicit Booleans for each granted identity
- optionally grant explicit `PREREQUISITE` edges whose endpoints are
  already members

That later review may **not**:

- overwrite the live file as a side effect
- parse roadmap or Markdown to discover names
- rank candidates
- name this document as membership
- waive overwrite authorization
- run live Autopilot

### 21.2 Explicitly out of the next slices unless separately authorized

- MSE package change
- Runtime Adapter change
- Repository Target change
- Supervisor prompt rewrite
- safe-fastpath change
- Architecture State Resolver
- live Autopilot as a side effect of authoring
- materializing `JOO` because `JOO_AUTOMATION` already has a file

### 21.3 Later hosting

- Architecture freeze: this tracked JOO document under
  `docs/automation/`
- Later Catalog Identity Authorization: a later tracked JOO
  architecture/review artifact; exact path deferred
- Later materialization, if authorized: Autopilot host
  `~/JOO-Automation/state/<repository_id>/milestone_selection_input.json`
- Do not implement inside a JOO investment-domain package
- Do not extend `joo_auto`
- Do not import JOO PF / IRO / Market / FactStore / allocation
  packages
- Do not invent `Automation-M4` or `Autopilot-M1` as the package
  identity

---

## 22. Explicit forbidden work

The following work is forbidden by this architecture and is not
authorized by the existence of this document:

- inserting `PF-M5`, `Automation-M3`, `IRO-M3`, `IRO-M4`, Architecture
  State Resolver, or any other identity into the catalog
- naming a successor `X`
- overwriting
  `state/JOO_AUTOMATION/milestone_selection_input.json`
- creating `state/JOO/milestone_selection_input.json`
- creating `state/milestone_selection_input.json`
- creating a Catalog Identity Authorization artifact now
- creating a second catalog JSON
- creating a catalog compiler
- implementing Architecture State Resolver
- parsing roadmap, Constitution, architecture Markdown, or README
- inferring identities from git, HEAD, tags, commits, filenames,
  version numbers, or milestone numbers
- converting dirty tree, unused `COMMIT READY`, review tokens, OOB, or
  Supervisor narrative into `blocking_evidence`
- adding ranking, score, priority, or `catalog_version` fields
- omitting an already-authorized eligible identity to force
  `CONTINUE`
- changing the Milestone Selection Engine package
- changing Repository Target
- redesigning Runtime Integration
- redesigning Supervisor actions, `COMMIT READY`, `next_action`, or
  safe-fastpath
- targeting a third repository
- reusing `joo_auto` milestone manifests
- commit, tag, or push
- live Autopilot

---

## 23. Authoring-time authority state

| Question | Answer |
| --- | --- |
| Architecture document authored | Yes |
| Independent architecture review | Required next |
| Implementation authorized | **NO** |
| Catalog Identity Authorization created | **NO** — concept frozen only |
| Currently authorized catalog identities | **NONE** |
| Human overwrite of the live file authorized | **NO** — later board only |
| Selector input bytes changed by this document | **NO** |
| `PF-M5` authorized | **NO** |
| `Automation-M3` authorized | **NO** |
| `IRO-M3` / `IRO-M4` authorized | **NO** |
| Architecture State Resolver | **DEFERRED** |
| Resolver required before a non-empty catalog | **NO** |
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
| Catalog authority | Sole runtime file; Option A |
| First-slice live payload | Empty explicit closed world |
| Current live result | `STOP(NO_ELIGIBLE_MILESTONE)` |
| Expected result until later grant + overwrite | `STOP(NO_ELIGIBLE_MILESTONE)` |
| Next action | Independent Architecture Review |

Until a later Catalog Identity Authorization and overwrite are
separately authorized and completed, live Autopilot must continue to
treat the current empty `JOO_AUTOMATION` catalog as
`STOP(NO_ELIGIBLE_MILESTONE)`. That remains the correct live outcome.

---

## 24. Final readiness statement

This document freezes the smallest lawful catalog-expansion contract:

- owner remains Selector Input Supply
- sole runtime catalog remains
  `state/<repository_id>/milestone_selection_input.json`
- Catalog Identity Authorization is a later JOO architecture/review
  membership grant, not a second runtime source
- currently authorized identities are none
- overwrite defaults to fail-closed
- Architecture State Resolver stays deferred and is not a
  prerequisite
- ranking-by-omission is forbidden
- first non-empty shape is frozen; contents are not
- `CONTINUE(X)` is not proven and waives no downstream gate

This document is ready for Independent Architecture Review.

It is not ready for Catalog Identity Authorization issuance.
It is not ready for overwrite.
It is not ready for implementation.
It is not ready for live Autopilot.

The current live selector state remains the correct fail-safe:

```text
STOP(NO_ELIGIBLE_MILESTONE)
```
