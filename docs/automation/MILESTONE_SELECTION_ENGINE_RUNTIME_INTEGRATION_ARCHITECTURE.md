# Milestone Selection Engine Runtime Integration Architecture

## Status and identity

- Status: Architecture authored for independent review; runtime-consumption
  freeze only
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Development infrastructure** — not an investment-domain plane
- Capability: **Milestone Selection Engine Runtime Integration**
- Owner: **Milestone Selection Engine**
- Milestone ID: **UNRESOLVED**
- This document does **not** invent or assign `Automation-M4`,
  `Autopilot-M1`, `M55+`, `PF-M5`, or any other manufactured milestone
  number
- Authorizing review: Independent Architecture Review
  (`~/JOO-Automation/results/milestone_selection_engine_runtime_integration_architecture_review/latest.md`)
  — **FINAL DECISION: ARCHITECTURE READY**
- Production location (later, not created by this document): a thin
  Autopilot-hosted consumption adapter in JOO-Automation. The existing
  `milestone_selection_engine` package remains isolated and
  side-effect-free
- Repository boundary for this document: architecture authoring only;
  this document alone authorizes no production code, test, package
  change, schema module, configuration, run artifact, Supervisor prompt
  rewrite, Autopilot runtime change, or Git history mutation

This document freezes the **minimum contract** that lets the already
implemented, side-effect-free Milestone Selection Engine be consumed by
the live repository-aware Autopilot / Supervisor loop.

It answers only:

> How does one frozen Autopilot cycle obtain an explicit selector input,
> invoke `select_next_milestone`, persist that exact decision, and
> require Supervisor to consume it fail-closed?

It does **not** answer:

> What milestone should be built next, and may Autopilot now continue
> automatically through an unbounded successor loop?

This document does **not** redesign:

- Milestone Selection Engine first-slice models or cardinality rules
- Autopilot Repository Target Abstraction
- Autopilot v5 safe-fastpath
- Supervisor action vocabulary (`RUN_REVIEW` / `COMMIT` / `STOP`)
- `COMMIT READY` single-consumption
- JOO investment-domain architecture

Implementation is **not** authorized.

PF-M5 is **not** authorized.

Automation-M3 is **not** authorized.

Architecture State Resolver remains **deferred**.

---

## 1. Purpose

The Milestone Selection Engine already owns inter-milestone eligibility
cardinality. Given explicit caller-supplied records, it returns exactly
one of:

```text
CONTINUE(exact milestone identity)
STOP(exact reason)
```

Live Autopilot can already bind one allowlisted repository and execute
the proven v5 machine. The first live command:

```text
joo autopilot --repo JOO_AUTOMATION
```

resolved `JOO_AUTOMATION`, initialized namespaced state/results, ran
Supervisor against JOO-Automation, preserved isolation, and issued
`STOP` because no unique next milestone was determined.

That `STOP` was Supervisor prose judgment. The engine was never asked.

The unique remaining architectural gap is **runtime integration**:
live Autopilot / Supervisor consumption of an unused engine decision.

This architecture adds exactly one responsibility:

**Live Autopilot/Supervisor consumption of a Milestone Selection Engine
decision.**

The architectural benefit is not that current `JOO_AUTOMATION` starts
building a successor. Without explicit records, `STOP` remains correct.
The benefit is that `STOP` / `CONTINUE` becomes Milestone Selection
Engine authority rather than Supervisor narrative inference.

---

## 2. Context

### 2.1 Independently re-verified checkpoint

This architecture is authored only after independent re-verification.
Material state matches the authorizing review.

**JOO** (`/Users/takesimple/Projects/JOO`)

| Check | Value |
| --- | --- |
| Path | `/Users/takesimple/Projects/JOO` |
| Branch | `feature/stage2-provider-runtime` |
| HEAD | `c8ec84d9a92e7ebb400928a50fbcdade10a36c1f` |
| Exact tag at HEAD | `v7.14-stage5-autopilot-repository-target-abstraction-architecture` |
| HEAD subject | Add Autopilot Repository Target Abstraction architecture |
| Tracked / staged | Clean / empty |

`git describe --exact-match HEAD` without `--tags` fails because the tag
is lightweight. `git tag --points-at HEAD` and
`git rev-parse v7.14-stage5-autopilot-repository-target-abstraction-architecture`
resolve the expected tag on this HEAD. This is the same non-material
lightweight-tag fact already recorded by the Repository Target
Abstraction architecture. It is not a checkpoint mismatch.

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
| HEAD | `64e2f693fe9da16a25446f3ff563eb0b0cf73dee` |
| HEAD subject | Add Autopilot repository target abstraction |
| Exact tag at HEAD | none |
| Tracked / staged | Clean / empty |
| Parent | `0c44ec4d5f7e76b692e2246b58b28e54bc7fe567` — Add Milestone Selection Engine first slice |

Untracked host machinery (`bin/`, extra `prompts/`, `state/`,
`backups/`) is expected operational tree, not a dirty tracked tree.

### 2.2 Frozen predecessors that this document must not reopen

| Authority | Status | Constraint on this freeze |
| --- | --- | --- |
| Milestone Selection Engine architecture | Frozen at JOO `v7.13` | Caller-supplied, side-effect-free, 0 / 1 / N only |
| Milestone Selection Engine first slice | Committed at `0c44ec4`; package `milestone_selection_engine/` | Public API unchanged |
| Repository Target Abstraction architecture | Frozen at JOO `v7.14` | Target binding precedes selection |
| Repository Target implementation | Committed at `64e2f69`; live-validated | Not redesigned |
| Autopilot v5 safe-fastpath | Live | Not redesigned |
| Supervisor vocabulary | `RUN_REVIEW` / `COMMIT` / `STOP` only | No fourth action |
| `COMMIT READY` | Autopilot-owned, single-consumption, repository-scoped | Engine must not inspect or consume it |

### 2.3 First live Autopilot evidence

Namespaced first cycle at `2026-08-17 18:07:43`:

| Fact | Observed |
| --- | --- |
| Command | `joo autopilot --repo JOO_AUTOMATION` |
| Target | `JOO_AUTOMATION` → `/Users/takesimple/JOO-Automation` |
| Branch / HEAD | `main` / `64e2f69` |
| Namespaced state | `state/JOO_AUTOMATION/` |
| Namespaced results | `results/JOO_AUTOMATION/` |
| Unused namespaced `COMMIT READY` | none |
| Namespaced consumed ledger | absent |
| `state/JOO_AUTOMATION/next_action.json` | `STOP` |
| Engine import in Autopilot runtime | none |

Supervisor, not the engine, produced that `STOP`. Runtime integration is
absent. That remains the unique architectural gap.

### 2.4 What is still missing

```text
RepositoryTarget is frozen and live
Milestone Selection Engine is frozen, implemented, and isolated
Architecture State Resolver is absent
Explicit selector input records are absent
Runtime consumption contract is absent
```

This document freezes only the missing consumption contract and the
explicit record source that the deferred resolver is not yet allowed to
replace.

---

## 3. Owner

The exact owner remains:

**Milestone Selection Engine**

Runtime integration does **not** transfer selection ownership to any
other actor.

### 3.1 Ownership that does not move

| Actor | Still owns | Must not gain |
| --- | --- | --- |
| Milestone Selection Engine | Eligibility cardinality; `CONTINUE` / `STOP`; this consumption contract | Repository choice; git execution; `COMMIT READY` |
| Autopilot Repository Target | Allowlisted target bind; `AutopilotExecutionContext` | Successor identity |
| Supervisor | Intra-milestone `RUN_REVIEW` / `COMMIT` / `STOP` for an already selected identity | Independent successor choice |
| Autopilot runtime | Safety gates; exact-path staging; `COMMIT READY` single-consumption; tag/push authorization; post-commit Supervisor | Computing or overriding selection |
| Architecture State Resolver | Nothing yet. Deferred | Must not be invented here as a hidden selector |
| `COMMIT READY` / commit-review | Unused versus consumed commit authority | Successor identity |
| Human | Explicit record authoring when cardinality is 0 or N | Informal chat as autonomy |

### 3.2 Adapter versus owner

A later implementation may host a thin **Milestone Selection Runtime
Adapter** beside Autopilot machinery. That adapter is a loader,
invoker, persister, injector, and fail-closed enforcer.

The adapter is not a second owner. It may not:

- author policy
- invent dependencies
- rank candidates
- choose a repository
- consume `COMMIT READY`
- execute git

Selection authority stays with the engine. Consumption authority stays
with this contract. Execution authority stays with Autopilot.

---

## 4. Existing Milestone Selection Engine contract

This document preserves the accepted first-slice contract exactly.

### 4.1 Public API

Models:

- `MilestoneRecord`
- `MilestoneSelectionInput`
- `MilestoneDependency`
- `BlockingEvidence`
- `BlockingEvidenceKind`
- `BlockingEvidenceScope`
- `MilestoneEligibility`
- `EligibilityExclusionFact`
- `PrerequisiteEvaluation`
- `DecisionClass`
- `StopReason`
- `SelectionEvidence`
- `MilestoneSelectionDecision`

Operations:

- `validate_milestone_selection_input`
- `select_next_milestone`

No ranking, scoring, preference, or “best candidate” API exists. None
is added here.

### 4.2 Cardinality

After validation and fail-closed graph/state checks:

| Eligible count | Decision |
| --- | --- |
| 0 | `STOP(NO_ELIGIBLE_MILESTONE)` |
| 1 | `CONTINUE(exact identity)` |
| 2+ | `STOP(MULTIPLE_ELIGIBLE_MILESTONES)` |

Closed engine `StopReason` set remains exactly:

- `NO_ELIGIBLE_MILESTONE`
- `MULTIPLE_ELIGIBLE_MILESTONES`
- `UNKNOWN_MILESTONE`
- `MISSING_DEPENDENCY`
- `DEPENDENCY_CYCLE`
- `AMBIGUOUS_ARCHITECTURE_STATE`

This document does **not** add a seventh engine `StopReason`.

### 4.3 Decision meaning

`CONTINUE` identifies only the unique eligible successor identity.

`CONTINUE` does **not** mean:

- architecture approved
- implementation approved
- commit approved
- tag approved
- push approved
- review waived
- OOB authorized
- git mutation authorized

`STOP` is a successful fail-safe result.

### 4.4 Engine isolation that remains

The engine package must remain:

- side-effect free
- filesystem free
- git free
- network free
- LLM free
- Markdown-parser free

Runtime integration must call the engine. It must not move filesystem,
git, Supervisor, or Autopilot concerns into
`milestone_selection_engine/`.

---

## 5. Integration responsibility

Exactly one new responsibility is authorized as architecture:

**Live Autopilot/Supervisor consumption of a Milestone Selection Engine
decision.**

### 5.1 Required adapter steps

When, and only when, the cycle is at a lawful inter-milestone
continuation point (§15), the adapter must:

1. obtain an explicit selector input from the frozen record source
   (§9)
2. invoke `select_next_milestone`
3. persist/attach the resulting
   `MilestoneSelectionRuntimeDecision` to the current
   repository-scoped Autopilot cycle
4. require Supervisor to consume that exact decision
5. fail closed if the decision is absent, stale, invalid, or
   mismatched
6. preserve all existing intra-milestone gates

### 5.2 Forbidden adapter behavior

The integration layer must not:

- author policy records
- invent dependencies, deferrals, exclusive successors, or gates
- rank, score, or prefer candidates
- choose `JOO` or `JOO_AUTOMATION`
- consume, refresh, or inspect `COMMIT READY` as engine input
- execute `git add`, commit, tag, push, reset, clean, or branch
  mutation
- parse Constitution, roadmap, README, or architecture Markdown
- infer records from Supervisor prose, chat, or silence
- silently recompute inside Supervisor
- waive dirty-tree, exact-path, OOB, or unused-`COMMIT READY` gates

Recomputation, when lawful, belongs only to the Autopilot
orchestration step that precedes Supervisor.

---

## 6. Non-responsibilities

This architecture does **not** implement or own:

- PF-M5 Market Watch
- Automation-M3 Human-Gated Git Executor
- Architecture State Resolver
- automatic roadmap parsing
- policy ranking or business-value scoring
- repository selection
- `COMMIT READY` ownership or consumption
- git execution
- tag / push authority
- Milestone Selection Engine redesign
- Repository Target redesign
- Autopilot v5 safe-fastpath redesign
- Supervisor action-vocabulary expansion
- third repositories
- new milestone ID assignment
- unbounded automatic successor looping
- JOO investment-domain work
- `joo_auto` M1 / M2 / M3 phase machinery

---

## 7. Integration position in the loop

### 7.1 Current live loop

```text
RepositoryTarget
→ freeze AutopilotExecutionContext
→ Supervisor
→ RUN_REVIEW / COMMIT / STOP
→ Autopilot
```

Supervisor currently infers whether a successor exists.

### 7.2 Frozen future loop

```text
RepositoryTarget
→ freeze AutopilotExecutionContext
→ inter-milestone gate
→ resolve explicit milestone-selection input
→ Milestone Selection Engine
→ MilestoneSelectionRuntimeDecision
→ Supervisor consumes that exact decision
→ RUN_REVIEW / COMMIT / STOP
→ Autopilot executes the directive
```

Target bind remains first. Selection occurs only inside one already
frozen `AutopilotExecutionContext`.

### 7.3 Decision consumption

If the engine or integration returns `CONTINUE(identity)`:

- Supervisor may act only for that exact identity
- Supervisor still chooses among `RUN_REVIEW`, `COMMIT`, and `STOP`
  for that identity’s current intra-milestone gate

If the engine or integration returns `STOP(reason)`:

- Supervisor must preserve `STOP`
- Supervisor may not substitute another milestone

### 7.4 Intra-milestone path is unchanged

If the cycle is not at an inter-milestone continuation point, the
selector is **not** invoked. Supervisor continues the already selected
active identity through existing gates.

---

## 8. Runtime objects

Do not invent a type zoo. First-slice runtime integration adds only
these concepts:

| Concept | Kind | Role |
| --- | --- | --- |
| `MilestoneSelectionInputArtifact` | Explicit file | Serialized existing `MilestoneSelectionInput` |
| `MilestoneSelectionHumanDecision` | Explicit file | Exclusive human authorization after ambiguity |
| `MilestoneSelectionRuntimeDecision` | Immutable envelope | Repository-scoped, single-cycle decision |
| Milestone Selection Runtime Adapter | Hosted function | Load, invoke, persist, inject, enforce |

Existing engine types are reused. They are not duplicated under new
names.

The first slice does **not** add:

- `BEST_CANDIDATE`
- `RANKED_LIST`
- `PRIORITY`
- `SCORE`
- persisted `ELIGIBLE` / `BLOCKED`
- a second `next_action` schema
- a new Supervisor action
- a new Repository Target field

---

## 9. Selector input source

### 9.1 The critical freeze

The engine requires explicit caller-supplied records. Architecture
State Resolver is absent and remains deferred. Therefore the first
runtime-integration slice must not infer input from prose, git,
roadmap, or filesystem discovery of architecture documents.

**Chosen source:** one repository-scoped explicit milestone-selection
input file.

**Rejected sources:**

| Source | Why rejected |
| --- | --- |
| Supervisor-produced normalized records | Restores LLM authorship of the candidate set |
| Roadmap / Constitution / architecture Markdown | Prose parsing is forbidden |
| Git history / tags / filenames | Engine and adapter must not inspect git to invent records |
| Architecture State Resolver | Deferred; combining resolver and selector is forbidden |
| Informal chat or untracked prompts | Not machine-readable authority |
| Silence / missing file treated as a guessed candidate set | Invents work |

### 9.2 Owner and representation

| Concern | Freeze |
| --- | --- |
| Artifact owner | Human / separately accepted architecture artifacts |
| Loader | Milestone Selection Runtime Adapter |
| Representation | JSON object that deserializes onto the existing `MilestoneSelectionInput` |
| Filename | `state/<repository_id>/milestone_selection_input.json` |
| Writers in this slice | Humans or later separately authorized record authors only |
| Forbidden writers | Autopilot, Supervisor, the adapter, the engine |

The adapter loads and type-checks. It does not author.

### 9.3 Exact payload

The file must deserialize to exactly:

1. `records`: finite collection of `MilestoneRecord`
2. `dependencies`: finite collection of `MilestoneDependency`
3. `blocking_evidence`: finite collection of `BlockingEvidence`

Field names, Boolean fields, `dependency_type = PREREQUISITE`, and
closed evidence kinds/scopes are the existing engine contract.

The adapter must not trim identities, case-fold, sort to repair
invalid input, or reconstruct missing fields.

### 9.4 Missing, empty, and invalid input

| Condition | Behavior |
| --- | --- |
| Input file absent | Integration `STOP(MISSING_SELECTOR_INPUT)`. Engine is not invoked. No records are invented. |
| Input file present and well-typed, including empty collections | Invoke `select_next_milestone`. Empty records lawfully yield `STOP(NO_ELIGIBLE_MILESTONE)`. |
| Input file present but not valid JSON or not exact engine types | Integration `STOP(INVALID_SELECTOR_INPUT)`. Engine produces no decision. |
| Engine validation raises `TypeError` or `ValueError` | Integration fail-closed `STOP(INVALID_SELECTOR_INPUT)`. Exception is not repaired. |

Absence is not an implicit empty world. An explicit empty file or
explicit empty collections are the only way to ask the engine to
classify an empty record set.

### 9.5 Blocking evidence is not auto-authored

The adapter must not populate `BlockingEvidence` from live git,
unused `COMMIT READY`, dirty-tree, or review tokens.

Those detections remain Autopilot-owned. Unused `COMMIT READY` and
unresolved intra-milestone work block selector invocation at the
inter-milestone gate (§15–§16). They are not converted into
adapter-authored engine input.

If a human or later resolver writes `blocking_evidence` into the
explicit file, the engine applies it unchanged.

---

## 10. Human decision record

### 10.1 When a human record is required

If the current unused-or-last engine decision for this
`repository_id` is `STOP(MULTIPLE_ELIGIBLE_MILESTONES)`, autonomous
continuation may resume only after an explicit machine-readable human
decision exists.

The following do **not** count:

- informal chat
- untracked prompt prose
- “human selected PF-M5” in a review narrative
- silence
- deleting one candidate from a conversation

### 10.2 Chosen representation

Filename:

```text
state/<repository_id>/milestone_selection_human_decision.json
```

Immutable concept: `MilestoneSelectionHumanDecision`.

Minimum fields:

| Field | Meaning |
| --- | --- |
| `repository_id` | Exact allowlisted ID |
| `authorized_identity` | Exact opaque milestone identity |
| `input_identity` | Exact identity of the selector input artifact this choice applies to |
| `generated_at` | Exact UTC timestamp string |
| `source_identity` | Opaque non-blank evidence identity for the human record itself |

Do not add rank, score, preferred-order, or alternative lists.

### 10.3 How the choice becomes engine input without ranking

The human decision record is **not** a ranking engine and **not** a
filter the adapter applies to eligible identities.

The human reduces cardinality by updating
`milestone_selection_input.json` using existing record fields. The
normal first-slice method is to mark non-chosen open identities
`deferred: true`. `superseded: true` or identity-scoped blocking
evidence may also be used if those are the true recorded facts.

The adapter then:

1. requires the human decision file after a `MULTIPLE` stop
2. requires `input_identity` to equal the current input artifact
3. requires `repository_id` to equal the frozen target
4. invokes the engine on the updated input
5. if the engine returns `CONTINUE(X)`, requires
   `X == authorized_identity`
6. if the engine still returns `MULTIPLE` or any other
   non-matching result, fail closed

The adapter never drops candidates itself.

### 10.4 Other stop reasons

A human decision record is required to resume only after
`MULTIPLE_ELIGIBLE_MILESTONES`.

After `NO_ELIGIBLE_MILESTONE` or another fail-closed engine reason,
the lawful resume path is an updated explicit input file. That is
record supply, not ranking. A human decision file is not required
unless the new classification itself becomes `MULTIPLE`.

---

## 11. Runtime decision artifact

### 11.1 Concept

`MilestoneSelectionRuntimeDecision` is the immutable runtime envelope
that binds one engine-or-integration decision to one repository-scoped
Autopilot cycle.

It is not `next_action.json`.
It is not `MilestoneSelectionDecision` alone.
It is not `RepositoryTarget`.

### 11.2 Minimum fields

| Field | Meaning |
| --- | --- |
| `repository_id` | Frozen target ID |
| `baseline_head` | Frozen `AutopilotExecutionContext` baseline HEAD |
| `required_branch` | Frozen target required branch |
| `decision_class` | `CONTINUE` or `STOP` |
| `selected_identity` | Exact identity if `CONTINUE`; otherwise absent |
| `stop_reason` | Exact engine or integration reason if `STOP`; otherwise absent |
| `stop_source` | `ENGINE` or `INTEGRATION` |
| `evidence` | Immutable engine `SelectionEvidence` when the engine ran; empty when integration stopped before invocation |
| `input_identity` | Exact identity of the input artifact used, or absent when input was missing |
| `generated_at` | Exact UTC timestamp string |
| `cycle_id` | Opaque exact single-cycle identity |
| `consumed` | Exact Boolean; `false` until this cycle consumes it |

Do not add ranking fields, alternative identities, or cross-repository
pointers.

`required_branch` exists only so “repository target differs” is a
deterministic staleness check. It is not branch-selection authority.

### 11.3 `input_identity`

`input_identity` is the exact SHA-256 hex digest of the raw input-file
bytes. Any byte change is a material input change. The adapter must
not canonicalize, pretty-print, or sort the file to compute identity.

If the input file is missing, `input_identity` is absent and
`stop_reason` is `MISSING_SELECTOR_INPUT`.

### 11.4 `cycle_id`

`cycle_id` is generated when the decision is produced. It is an opaque
exact `str`, unique within that repository namespace. A later
implementation may use a UUID or an Autopilot-cycle token. This
document does not freeze a generator algorithm.

One produced decision belongs to exactly one `cycle_id`.

### 11.5 Persistence

Filename:

```text
state/<repository_id>/milestone_selection_decision.json
```

One unused-or-current decision file per repository namespace. There is
no results-namespace selection authority in this slice.

`results/<repository_id>/...` must not be treated as a selector
decision. Review reports may mention the decision; they are not the
decision.

### 11.6 Lifetime

The decision must not survive a material repository state change.

Material changes include at least:

- different `repository_id`
- different baseline HEAD
- different required branch / repository target
- different selector-input bytes
- already consumed for a later cycle
- missing required selector input

A stale decision is not repaired by Supervisor. Orchestration either
produces a fresh decision or fail-closed `STOP`s.

---

## 12. State filenames and namespacing

### 12.1 Exact filenames

Under the Autopilot host (`~/JOO-Automation`):

```text
state/JOO/milestone_selection_input.json
state/JOO/milestone_selection_decision.json
state/JOO/milestone_selection_human_decision.json

state/JOO_AUTOMATION/milestone_selection_input.json
state/JOO_AUTOMATION/milestone_selection_decision.json
state/JOO_AUTOMATION/milestone_selection_human_decision.json
```

These join the already frozen namespaced files
(`next_action.json`, `supervisor_checkpoint.json`,
`consumed_commit_ready.json`, `autopilot.log`).

### 12.2 Isolation rules

- One selection decision belongs to exactly one `repository_id`
- Cross-repository reuse is forbidden
- A `JOO` decision is invisible to `JOO_AUTOMATION`
- A `JOO_AUTOMATION` decision is invisible to `JOO`
- No global shared selector decision
- No un-namespaced alias for these new files

Legacy un-namespaced `state/*.json` remains the JOO alias only for
pre-existing Autopilot files. It is **not** a selector-input or
selector-decision location.

`JOO_AUTOMATION` must never read `state/milestone_selection_*.json`.
Those paths must not be created.

### 12.3 Protected host prefixes

When target is `JOO_AUTOMATION`, these files live under protected
`state/` and must not become stage candidates or target dirt. That
Repository Target rule is unchanged.

---

## 13. Decision lifetime and single consumption

### 13.1 Produce once per inter-milestone cycle

At a lawful inter-milestone point, orchestration produces exactly one
`MilestoneSelectionRuntimeDecision` for the current `cycle_id`, with
`consumed = false`, then invokes Supervisor.

It must not reuse a previous cycle’s decision.

### 13.2 Consume once

After Supervisor writes `next_action.json`, Autopilot validates that
directive against the unused decision (§20).

On successful validation:

1. set `consumed = true` on the same decision artifact
2. execute the directive using existing Autopilot semantics

A consumed decision must not authorize a later cycle.

### 13.3 Failed validation

If `next_action` mismatches the decision:

- fail closed
- do not execute `RUN_REVIEW` or `COMMIT`
- do not treat the decision as reusable authorization
- mark the decision consumed or otherwise invalid for later reuse

The next Autopilot cycle, if any, must re-enter orchestration. It must
not let Supervisor invent a substitute identity.

### 13.4 Intra-milestone reuse is not decision reuse

After `CONTINUE(X)` is consumed and Supervisor issued `RUN_REVIEW` or
`COMMIT` for `X`, later intra-milestone cycles keep `X` as the active
identity through `next_action` / checkpoint `last_milestone`.

That is active-milestone continuity, not reuse of the consumed
selection envelope.

---

## 14. Staleness contract

### 14.1 A decision is stale if any of the following is true

1. `repository_id` differs from the frozen
   `AutopilotExecutionContext.target.repository_id`
2. `baseline_head` differs from the frozen baseline HEAD
3. `required_branch` differs from the frozen target required branch
   (repository target differs)
4. `input_identity` differs from the current input-file digest, or the
   input file is required and missing
5. `consumed` is `true`
6. `cycle_id` is not the current Autopilot cycle
7. a human decision is required after `MULTIPLE` and is absent,
   stale, or mismatched
8. the persisted object is missing required fields or is not the
   exact runtime envelope

### 14.2 Stale-decision behavior

```text
stale decision → STOP
```

Do not silently recompute inside Supervisor.

If the cycle is still a lawful inter-milestone point, orchestration
may produce a **new** decision before Supervisor. That is a new
`cycle_id`, not a mutation of the stale envelope.

If the cycle is intra-milestone, orchestration must not produce a
successor decision. Stale successor envelopes are ignored, and the
active identity remains the unfinished intra-milestone identity.

### 14.3 Missing decision when a decision is required

At an inter-milestone point, Supervisor must not run without a current
unused `MilestoneSelectionRuntimeDecision`.

Missing required decision → integration
`STOP(MISSING_SELECTION_DECISION)`.

---

## 15. Active milestone versus successor

### 15.1 Distinction

| Kind | Meaning | Selector? |
| --- | --- | --- |
| Active milestone | Identity already inside the intra-milestone pipeline | Must not run |
| Successor | Identity that may become next after the previous identity is closed | May run only at the inter-milestone point |

The engine runs only at an inter-milestone continuation point. It must
not select a successor while a current milestone still has an
unfinished lawful intra-milestone gate.

### 15.2 Inter-milestone continuation point

The selector may be invoked only when **all** of the following are
true:

1. `AutopilotExecutionContext` is frozen and valid
2. repository checkpoint / baseline observation is valid
3. no unused namespaced `COMMIT READY` exists for this
   `repository_id`
4. no unresolved implementation / review / remediation action exists
5. the previous milestone is complete or explicitly closed

If any condition fails, the selector is not invoked.

### 15.3 Unresolved intra-milestone work

Unresolved intra-milestone work exists when any of the following is
true:

- namespaced `next_action.action` is `RUN_REVIEW` or `COMMIT`
- last official review token in this repository namespace is an
  intra-milestone continue token, including existing
  `CONTINUE_FINALS` such as `REMEDIATION REQUIRED`
- checkpoint `last_event` is a non-terminal intra-milestone event
  and `last_milestone` is non-empty and `next_action` is not `STOP`

A `STOP` next_action after a hard-blocked intra-milestone gate does
**not** authorize successor selection unless the previous identity is
also complete or explicitly closed in the selector input.

### 15.4 Previous milestone complete or explicitly closed

The previous milestone is complete when:

- any unused `COMMIT READY` for this repository is absent, and
- that identity’s commit authority was consumed if a commit occurred,
  and
- namespaced `next_action` is absent or `STOP`

The previous milestone is explicitly closed when the current selector
input records it `completed`, `deferred`, `superseded`, or `oob`, and
the unused-`COMMIT READY` and `next_action` conditions above also
hold.

Supervisor prose labels such as
`post-repository-target-abstraction` are not engine identities. They
do not become selector input.

### 15.5 Current `JOO_AUTOMATION` application

Live namespaced state is:

- `next_action = STOP`
- unused `COMMIT READY` = none
- consumed namespaced ledger = absent
- last event = `STOP`

This is an inter-milestone point. The selector would be eligible to
run. Explicit input is absent. Lawful result is therefore integration
`STOP(MISSING_SELECTOR_INPUT)`, not `CONTINUE(PF-M5)` and not a
Supervisor-invented successor.

---

## 16. `COMMIT READY` interaction

### 16.1 Ownership unchanged

`COMMIT READY` remains Autopilot / commit-review authority.
Single-consumption remains repository-scoped.

The Milestone Selection Engine must not inspect, detect, consume, or
refresh `COMMIT READY`.

The adapter must not turn unused `COMMIT READY` into engine
`BlockingEvidence`.

### 16.2 Ordering

```text
unused COMMIT READY
  → do not invoke selector
  → do not select a successor
  → existing commit path stays authoritative
```

Unfinished / unused commit authority blocks successor selection.

### 16.3 Active-commit path

If an unused namespaced `COMMIT READY` already exists:

- Supervisor may issue only `COMMIT` for that exact unused authority,
  or `STOP`
- Supervisor may not start a successor review
- Autopilot executes the existing commit path

This is true even if a selector input file would otherwise contain
exactly one eligible successor.

### 16.4 After consumption

After `COMMIT READY` is consumed and the mandatory post-commit
Supervisor cycle runs, successor selection becomes possible only if
§15’s inter-milestone gate now holds **and** explicit input exists.

The adapter does not mark the committed identity `completed`. Updating
that recorded fact is a human / later resolver responsibility. See
§24.3 for the first-slice replay guard.

---

## 17. Supervisor contract

### 17.1 Supervisor no longer independently selects

When a selector decision is required, Supervisor must not independently
choose the next milestone.

| Engine / integration decision | Supervisor may do |
| --- | --- |
| `CONTINUE(X)` | Issue only the next lawful intra-milestone action for **X** |
| `STOP(reason)` | Issue `STOP` |

### 17.2 Supervisor must not

- replace `X` with `Y`
- rank alternatives
- override selector `STOP`
- invent a candidate set
- infer roadmap priority
- treat missing, stale, or silent decisions as authorization
- choose or switch repository
- write `next_action.json` outside the bound namespace

### 17.3 Supervisor still owns

For the already-selected milestone, Supervisor still owns:

- `RUN_REVIEW`
- `COMMIT`
- `STOP`

including whether the current gate for `X` is review, commit, or a
human-only stop.

`CONTINUE(X)` is not an order to `RUN_REVIEW`. If `X` cannot lawfully
proceed, Supervisor may `STOP` for `X`. That does not authorize `Y`.

### 17.4 Machine-generated selection block

Every Supervisor invocation that requires a selection decision must
receive an explicit machine-generated block **in addition to** the
existing Autopilot target block.

The two blocks stay separate.

Minimum selection-block contents:

- `repository_id`
- `baseline_head`
- `cycle_id`
- `decision_class`
- `selected_identity` or `(none)`
- `stop_reason` or `(none)`
- `stop_source`
- `decision_path`

Supervisor must treat that block as the sole authoritative successor
identity. It may not infer identity from prose or cwd.

Exact rendering is an implementation concern. The authority split is
not.

### 17.5 Action vocabulary unchanged

No fourth action is added. `CONTINUE` is not a Supervisor action.
`CONTINUE` is a selector decision class.

---

## 18. Autopilot contract

### 18.1 Autopilot remains the executor

Autopilot consumes Supervisor directives as today:

- `STOP` → persist checkpoint and exit
- `RUN_REVIEW` → launch the named review in the frozen target
- `COMMIT` → unused `COMMIT READY` + exact-path staging + authorized
  tag/push

Existing `max_steps` loop semantics remain. This document does not add
a second outer successor loop.

### 18.2 Autopilot must not

- compute milestone selection itself
- override engine or integration `STOP`
- change the selected identity
- turn `STOP` into `RUN_REVIEW`
- reuse a stale or consumed decision
- invoke the selector during unresolved intra-milestone work
- invoke the selector while unused `COMMIT READY` exists

### 18.3 Autopilot still owns

- repository safety
- exact-path staging
- dirty-tree protection
- `COMMIT READY` single-consumption
- tag / push authorization
- post-commit Supervisor cycle
- namespaced state / results writes
- host == target protected prefixes

A `CONTINUE` identity does not weaken those gates.

### 18.4 Orchestration ownership

Autopilot hosts the adapter call:

```text
after target freeze
before Supervisor
```

Hosting is not selection. Autopilot may call `select_next_milestone`.
It may not replace its result.

---

## 19. Repository Target interaction

Repository Target remains frozen.

### 19.1 Order

```text
--repo <ID>
→ resolve / validate target
→ freeze AutopilotExecutionContext
→ then, and only then, selection
```

The engine must never choose `JOO` or `JOO_AUTOMATION`.

Asking the engine to choose a repository is already a specified
Repository Target `STOP` (wrong owner). This document keeps that
prohibition.

### 19.2 One context, one decision

One `MilestoneSelectionRuntimeDecision` belongs to exactly one
`repository_id` inside one frozen `AutopilotExecutionContext`.

Switching `JOO` ↔ `JOO_AUTOMATION` requires a new Autopilot
invocation and a new decision. Cross-repository reuse is forbidden.

### 19.3 No target-field expansion

`RepositoryTarget` gains no selector fields. Live HEAD, selector
input, and unused `COMMIT READY` do not migrate onto the static
target record.

---

## 20. `next_action` interaction

### 20.1 Two objects, two jobs

| Object | Answers |
| --- | --- |
| selector decision | What milestone identity is allowed |
| Supervisor `next_action` | What immediate intra-milestone action is allowed |

They must not be collapsed into one object.

Existing `next_action` schemas remain:

```text
{"action":"RUN_REVIEW","prompt_name":"...","reason":"...","milestone":"..."}
{"action":"COMMIT","paths":[...],"message":"...","tag":"...","branch":"...","push":"...","reason":"...","milestone":"..."}
{"action":"STOP","reason":"...","milestone":"..."}
```

### 20.2 Identity invariant

If the unused decision is `CONTINUE(X)`:

```text
next_action.milestone == X
```

Exact string equality. No trim. No case-fold.

`next_action.action` may be `RUN_REVIEW`, `COMMIT`, or `STOP`.
`STOP` here means Supervisor cannot lawfully proceed on `X`. It is
not authorization to start `Y`.

### 20.3 Selector `STOP` invariant

If the unused decision is `STOP`:

```text
next_action.action == STOP
```

The STOP `milestone` field is diagnostic only. It is not a successor
identity and must not be executed as one.

### 20.4 Mismatch

Any of the following is fail-closed before execution:

- `CONTINUE(X)` but `next_action.milestone != X`
- `CONTINUE(X)` but `next_action.action` is missing or unknown
- `STOP` but `next_action.action != STOP`
- `next_action` missing after Supervisor
- `next_action` written outside the bound namespace

Mismatch reason: `NEXT_ACTION_IDENTITY_MISMATCH`.

---

## 21. Cardinality behavior at runtime

The engine’s 0 / 1 / N rule is unchanged. Runtime consumption only
preserves it.

### 21.1 Zero eligible candidates

```text
STOP(NO_ELIGIBLE_MILESTONE)
```

or, if the input artifact is absent:

```text
STOP(MISSING_SELECTOR_INPUT)
```

Do not invent work.

### 21.2 Multiple eligible candidates

```text
STOP(MULTIPLE_ELIGIBLE_MILESTONES)
```

Do not rank. Human resume requires §10.

### 21.3 Unique eligible candidate

```text
CONTINUE(exact identity)
```

This authorizes only that successor identity. Every later gate still
applies.

### 21.4 Integration-layer stop reasons

These are **not** engine `StopReason` values. They are exact
integration fail-closed reasons persisted on
`MilestoneSelectionRuntimeDecision.stop_reason` with
`stop_source = INTEGRATION`.

Closed first-slice integration reasons:

| Reason | When |
| --- | --- |
| `MISSING_SELECTOR_INPUT` | Required input file absent |
| `INVALID_SELECTOR_INPUT` | Input is not exact engine input |
| `MISSING_SELECTION_DECISION` | Decision required and absent |
| `STALE_SELECTION_DECISION` | Persisted decision fails §14 |
| `DECISION_REPOSITORY_MISMATCH` | `repository_id` mismatch |
| `DECISION_HEAD_MISMATCH` | baseline HEAD mismatch |
| `DECISION_TARGET_MISMATCH` | required branch / target mismatch |
| `DECISION_INPUT_MISMATCH` | input digest mismatch |
| `DECISION_ALREADY_CONSUMED` | reuse of a consumed envelope |
| `NEXT_ACTION_IDENTITY_MISMATCH` | Supervisor directive disagrees |
| `UNUSED_COMMIT_READY_BLOCKS_SUCCESSOR` | Successor attempted while unused `COMMIT READY` exists |
| `UNRESOLVED_INTRA_MILESTONE_WORK` | Selector invoked during active work |
| `HUMAN_DECISION_REQUIRED` | `MULTIPLE` resume without §10 record |
| `HUMAN_DECISION_MISMATCH` | Human record / `CONTINUE` identity disagree |
| `SELECTOR_REPLAY_DETECTED` | Same identity continued after its commit was already consumed without an input update that closes it |

Do not add ranking reasons.

---

## 22. Current `JOO_AUTOMATION` expected behavior

Apply this architecture to the live checkpoint:

| Fact | Value |
| --- | --- |
| Target | `JOO_AUTOMATION` |
| HEAD | `64e2f693fe9da16a25446f3ff563eb0b0cf73dee` |
| Explicit selector input | absent |
| Human decision record | absent |
| Unused `COMMIT READY` | none |
| `next_action` | `STOP` |

Lawful outcome after integration still:

```text
STOP
```

Expected first-slice reason:

```text
MISSING_SELECTOR_INPUT
```

This architecture does **not** determine PF-M5, Automation-M3, or any
other successor. Integration alone does not make current
`JOO_AUTOMATION` continue.

The same command against `JOO` is independent. A missing `JOO` input
file is a `JOO`-scoped `MISSING_SELECTOR_INPUT`. It does not read
Automation files, and the reverse is also true.

---

## 23. Fail-closed conditions

| Condition | Action |
| --- | --- |
| Selector invoked while unused `COMMIT READY` exists | STOP; no successor |
| Selector invoked during unresolved intra-milestone work | STOP; no successor |
| Required input missing | STOP; engine not invoked |
| Invalid input | STOP; no partial classification |
| Engine validation exception | STOP; propagate, do not repair |
| Engine `STOP` | Supervisor and Autopilot preserve STOP |
| Engine `CONTINUE(X)` and Supervisor emits `Y` | STOP; do not execute |
| Engine `STOP` and Supervisor emits `RUN_REVIEW` or `COMMIT` | STOP; do not execute |
| Missing decision at inter-milestone point | STOP |
| Stale HEAD / repository / target / input | STOP |
| Consumed decision reused | STOP |
| Human silence after `MULTIPLE` | STOP |
| Informal chat treated as exclusive choice | STOP |
| Prose / roadmap parsed into records | Forbidden / STOP |
| Adapter chooses repository | STOP (wrong owner) |
| Cross-repository decision reuse | STOP |
| `CONTINUE` treated as review/commit/tag/push waiver | STOP |
| Git mutation added to the engine package | Unauthorized / STOP |

The machine must not hide, coerce, or rank its way out of any failure
mode.

---

## 24. First future implementation slice

This document authorizes **no** implementation.

If a later board authorizes implementation, the first slice may contain
only the minimum needed to consume one successor decision safely.

### 24.1 In scope if later authorized

1. `MilestoneSelectionRuntimeDecision` envelope
2. repository-scoped selector input artifact loader
3. repository-scoped human-decision artifact loader
4. selector invocation adapter hosted beside Autopilot, calling
   existing `select_next_milestone`
5. decision persistence under `state/<repository_id>/`
6. staleness and single-consumption validation
7. inter-milestone gate detection
8. unused-`COMMIT READY` successor-blocking
9. Supervisor selection-block injection
10. `next_action` identity enforcement
11. first-slice replay guard (§24.3)
12. tests in §25

Suggested later module identity, descriptive only:
`milestone_selection_runtime` beside Autopilot `bin/`. Exact module
name is deferred to implementation authorization and must remain
unnumbered.

### 24.2 Explicitly out of the first implementation slice

- Architecture State Resolver
- automatic roadmap parsing
- Milestone Selection Engine model or `StopReason` changes
- Repository Target changes
- PF-M5
- Automation-M3
- new milestone numbering
- git behavior changes
- commit / tag / push behavior changes
- Autopilot v5 safe-fastpath redesign
- Supervisor action-vocabulary changes
- unbounded automatic successor looping
- auto-updating selector input after commit
- results-namespace selection authority
- third repositories
- committing Autopilot `bin/` as a side effect of this architecture
  document

### 24.3 First-slice replay guard

The adapter does not write `completed: true` after a commit.

If:

- checkpoint `last_milestone` is exact identity `X`, and
- a namespaced `COMMIT READY` for that just-finished commit path has
  already been consumed, and
- namespaced `next_action` is `STOP`, and
- the engine would `CONTINUE(X)` because the input still leaves `X`
  eligible

then orchestration must `STOP(SELECTOR_REPLAY_DETECTED)` instead of
injecting that `CONTINUE`.

Closing `X` in the explicit input is a human / later resolver action.

### 24.4 Later hosting

- Architecture freeze: this tracked JOO document under
  `docs/automation/`
- Implementation, if later authorized: JOO-Automation Autopilot
  machinery plus unchanged `milestone_selection_engine` public API
- Do not implement inside a JOO investment-domain package
- Do not extend `joo_auto`
- Do not import JOO PF / IRO / Market / FactStore / allocation
  packages into the adapter beyond existing Autopilot isolation

### 24.5 No automatic continuation loop yet

The first implementation slice must prove that **one** successor
decision can be safely produced and consumed in one live cycle.

It must not add an unbounded “keep selecting the next milestone”
loop. Further automatic repeated continuation is a later gate if it
is needed at all.

Existing Autopilot `max_steps` cycling of intra-milestone
`RUN_REVIEW` / `COMMIT` / post-commit Supervisor remains. That is
not successor looping.

---

## 25. Required test invariants

A later implementation must prove at least the following. These tests
are not authored by this document.

| Invariant | Expected |
| --- | --- |
| Selector not invoked while unused `COMMIT READY` exists | no engine call; no successor |
| Selector not invoked during unresolved intra-milestone work | no engine call |
| Selector invoked at a valid inter-milestone point when input exists | engine called once |
| Missing input at inter-milestone point | `STOP(MISSING_SELECTOR_INPUT)` |
| `CONTINUE` identity injected into Supervisor | selection block carries exact identity |
| Supervisor cannot substitute another identity | mismatch fail-closed |
| Engine `STOP` preserved | Autopilot executes STOP |
| Missing decision fails closed | no Supervisor-invented successor |
| Stale HEAD fails closed | `DECISION_HEAD_MISMATCH` / stale |
| Wrong `repository_id` fails closed | `DECISION_REPOSITORY_MISMATCH` |
| Decision single-cycle / single-consumption | consumed envelope cannot authorize a later cycle |
| `next_action` identity mismatch fails closed | no execution |
| Zero candidate | `STOP(NO_ELIGIBLE_MILESTONE)` |
| Multiple candidate | `STOP(MULTIPLE_ELIGIBLE_MILESTONES)` |
| Unique candidate | `CONTINUE(exact identity)` |
| Human choice requires explicit record | chat / silence insufficient |
| Human record without matching `CONTINUE` | `HUMAN_DECISION_MISMATCH` |
| No prose parsing | adapter does not read roadmap / architecture Markdown into records |
| No roadmap ranking | no score / priority API |
| No Repository Target selection | engine / adapter never choose `JOO` vs `JOO_AUTOMATION` |
| No git operations added to MSE package | package remains filesystem/git free |
| `JOO` / `JOO_AUTOMATION` decision isolation | no cross-namespace read or reuse |
| Existing Repository Target tests remain green | no RTA regression |
| Existing MSE tests remain green | no engine-contract regression |
| Existing Autopilot safe-fastpath tests remain green | no v5 safety regression |
| `CONTINUE` does not waive later gates | unused `COMMIT READY`, dirty-tree, exact-path still bind |
| Replay after consumed commit of `X` | `SELECTOR_REPLAY_DETECTED` |

Normal, boundary, wrong-type, empty-value, order, and exception
propagation cases required by the repository agent contract apply to
every public adapter entry point.

---

## 26. Authority boundaries

```text
Human / accepted artifacts
  explicit milestone_selection_input.json
  optional milestone_selection_human_decision.json
        │
        ▼
Autopilot Repository Target
  freeze AutopilotExecutionContext
        │
        ▼
Inter-milestone gate
  unused COMMIT READY? unresolved intra-milestone work?
        │
        ▼
Milestone Selection Runtime Adapter
  load explicit input → select_next_milestone
        │
        ▼
MilestoneSelectionRuntimeDecision
        │
        ▼
Supervisor
  intra-milestone RUN_REVIEW / COMMIT / STOP for that exact identity
  or preserve STOP
        │
        ▼
Autopilot
  execute the exact directive; keep safety gates
```

Later layers may consume earlier ones. They may not assume them.
Human silence is never authorization.

---

## 27. Frozen invariants

1. Owner is Milestone Selection Engine.
2. Milestone ID remains `UNRESOLVED`.
3. Runtime integration does not transfer selection ownership to
   Supervisor, Autopilot, Repository Target, Architecture State
   Resolver, `COMMIT READY`, or a human chat session.
4. The existing engine public API is unchanged.
5. Cardinality 0 / 1 / N remains the only selection rule.
6. There is no ranking, scoring, or preference engine.
7. Selector input is an explicit repository-scoped file, not prose.
8. Missing input is `STOP(MISSING_SELECTOR_INPUT)` and invents no
   records.
9. Architecture State Resolver remains deferred.
10. `MilestoneSelectionRuntimeDecision` is repository-scoped and
    single-consumption.
11. A decision must not survive a material repository or input change.
12. Stale or consumed decisions fail closed.
13. Recomputation belongs to orchestration, never Supervisor.
14. Supervisor may not replace `CONTINUE(X)` with `Y`.
15. Supervisor must preserve engine or integration `STOP`.
16. Autopilot may not compute or override selection.
17. `next_action` and the selector decision remain distinct objects.
18. `CONTINUE(X)` requires `next_action.milestone == X`.
19. Selector `STOP` requires `next_action.action == STOP`.
20. Unused `COMMIT READY` blocks successor selection.
21. The engine never inspects or consumes `COMMIT READY`.
22. The selector runs only at an inter-milestone continuation point.
23. Unresolved intra-milestone work blocks successor selection.
24. Repository Target remains first and frozen.
25. The engine never chooses `JOO` or `JOO_AUTOMATION`.
26. Cross-repository decision reuse is forbidden.
27. Human exclusive choice after `MULTIPLE` requires an explicit
    machine-readable record.
28. Informal chat, untracked prompts, and silence are not records.
29. `CONTINUE` waives no later gate.
30. Existing Autopilot safety gates remain independent.
31. No automatic unbounded successor loop is authorized.
32. Current `JOO_AUTOMATION` without explicit records remains `STOP`.
33. Integration alone does not start PF-M5 or Automation-M3.
34. The two known JOO OOB documents remain non-authoritative.
35. This document does not authorize implementation, commit, tag, or
    push.
36. Development automation must not distort JOO's investment-product
    architecture.

---

## 28. Authorization freeze

| Question | Answer |
| --- | --- |
| Architecture document authored | Yes |
| Independent architecture review | Required next |
| Implementation authorized | **NO** |
| PF-M5 authorized | **NO** |
| Automation-M3 authorized | **NO** |
| Architecture State Resolver | **DEFERRED** |
| Milestone Selection Engine redesign | **NO** |
| Repository Target redesign | **NO** |
| Automatic continuation loop | **NO** |
| Commit / tag / push authorized | **NO** |
| Human decision required now | **NO** — current lawful result is still STOP |
| Milestone ID | **UNRESOLVED** |
| Owner | **Milestone Selection Engine** |
| Next action | Independent Architecture Review |

Until a later implementation is separately authorized and completed,
live Autopilot must not claim engine-owned successor selection.
Current `JOO_AUTOMATION` `STOP` remains the correct live outcome.
