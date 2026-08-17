# Milestone Selection Engine Architecture

## Status and identity

- Status: Architecture authored for independent review; first-slice freeze
  only
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Development infrastructure** — not an investment-domain plane
- Program name (descriptive only): Autopilot Deterministic Milestone
  Continuation
- Owner: **Milestone Selection Engine**
- Milestone ID: **UNRESOLVED**
- This document does **not** invent or assign `Automation-M4`,
  `Autopilot-M1`, `M55+`, or any other manufactured milestone number
- Production location (later, not created by this document): an isolated
  side-effect-free component in JOO-Automation; not a JOO investment
  package and not an extension of `joo_auto`
- Authorizing review: Autopilot Deterministic Milestone Continuation
  Candidate Boundary Review after `v7.12-stage5-iro-m2-implementation`
  (decision: **CANDIDATE BOUNDARY APPROVED**)
- Repository boundary for this document: architecture authoring only; this
  document alone authorizes no production code, test, package scaffold,
  schema module, configuration, run artifact, Supervisor integration,
  Autopilot continuation, or Git history mutation

This document freezes the **minimum architecture** for a deterministic
Milestone Selection Engine.

It answers only:

> Given explicit normalized milestone records, is there exactly one
> legally eligible next milestone?

It does **not** answer:

> What milestone seems strategically best?

Implementation is **not** authorized.

PF-M5 is **not** authorized.

Autopilot continuation is **not** authorized.

---

## 1. Purpose

The Milestone Selection Engine owns **inter-milestone eligibility
cardinality**.

The intra-milestone pipeline already exists:

```text
Supervisor → RUN_REVIEW / COMMIT / STOP
→ Autopilot execution
→ review → remediation if required → re-review
→ commit review → COMMIT READY
→ path-scoped git add → commit → tag → push
→ post-commit Supervisor
```

The missing responsibility is not review, implementation, commit, tag,
push, or strategic ranking. The missing responsibility is a deterministic
answer to whether the supplied explicit records determine exactly one
lawful successor.

The engine must implement behavior equivalent to:

```text
eligible_set = deterministic_filter(all_supplied_candidates)

if len(eligible_set) == 0:
    STOP(NO_ELIGIBLE_MILESTONE)

if len(eligible_set) == 1:
    CONTINUE(exact milestone identity)

if len(eligible_set) >= 2:
    STOP(MULTIPLE_ELIGIBLE_MILESTONES)
```

A sequencing system that returns `STOP` is still valuable. Fail-safe
`STOP` is preferred to speculative continuation.

---

## 2. Context

### 2.1 Checkpoint at authoring

This architecture is authored against the verified JOO checkpoint:

| Check | Value |
| --- | --- |
| Repository | `/Users/takesimple/Projects/JOO` |
| Branch | `feature/stage2-provider-runtime` |
| HEAD | `57efdb94d845cd9973ac01445602c6cc8237e924` |
| Exact tag | `v7.12-stage5-iro-m2-implementation` |
| HEAD subject | Add IRO-M2 memory comparison contradiction and bounded re-research implementation |
| Tracked working tree | Clean |
| Unused `COMMIT READY` | None; consumed for `57efdb9` / `v7.12` |

Intentionally untracked OOB files exist and remain **non-authoritative**:

- `docs/JOO_PRODUCT_ARCHITECTURE.md`
- `docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md`

This architecture must not consume, modify, stage, or treat either OOB
file as a source of successor identity, dependency, or ranking.

### 2.2 Existing contracts that constrain this freeze

| Authority | What it contributes | What it does not contribute |
| --- | --- | --- |
| `JOO_CONSTITUTION.md` | One owner per responsibility; opaque caller-supplied identity; validation-first; stop when multiple valid designs exist | A milestone registry or successor graph |
| `docs/JOO_PRODUCT_ROADMAP.md` v1.2 | Stage-level product direction; Stage 6 is later product scheduling | Named PF-M5 / IRO-M3 / Automation-M3 uniqueness |
| `DEVELOPMENT_PROTOCOL.md` | Architecture before implementation; stop on ambiguity | Successor selection |
| `AUTONOMOUS_EXECUTION_PROTOCOL.md` | Autonomous work stays inside an approved milestone | Inter-milestone choice |
| `ARCHITECTURE_PATTERNS.md` | Explicit model → validator → applicability separation | Milestone eligibility |
| Automation-M1 | Accepted review-only orchestrator for one operator-selected manifest | Successor discovery or filtering |
| Automation-M2 (`docs/automation/AUTOMATION_M2_DEVELOPMENT_PIPELINE_ORCHESTRATOR_ARCHITECTURE.md`) | Frozen pipeline for one already-chosen opaque `milestone_id`; print-only Git; exact `COMMIT READY` eligibility for human approval | Successor selection; Git mutation |
| Automation-M3 | Named residual: human-gated local Git execute; architecture remains OOB; last independent review token is `AUTOMATION-M3 ARCHITECTURE REMEDIATION REQUIRED` | Selector ownership |
| Autopilot v5 | Executes Supervisor directives; owns fail-safes, scoped commit/tag/push, and `COMMIT READY` single-consumption | Roadmap or successor authority |
| Supervisor | Intra-milestone action choice among `RUN_REVIEW`, `COMMIT`, `STOP` | Deterministic successor eligibility |

JOO currently has **no** tracked authoritative general milestone registry
or dependency graph sufficient to produce one unique successor.

### 2.3 Long-term product direction

JOO's long-term direction remains:

- 24/7 AI Investment Command Center
- KB Open API as the primary factual data source
- Provider layer for portfolio and market factual snapshots
- AI committees for research and evidence generation
- CIO for final synthesis and portfolio allocation decision

Development automation exists only to safely accelerate construction.
The Milestone Selection Engine is development infrastructure. It must
not distort investment-product architecture, absorb PF / IRO / Market /
FactStore / allocation ownership, or treat construction sequencing as an
investment decision.

---

## 3. Owner

The exact owner is:

**Milestone Selection Engine**

This is a new component. It is not a new numbered milestone and not a
new investment domain.

The descriptive program name **Autopilot Deterministic Milestone
Continuation** is not the owner. Autopilot may later consume a
`CONTINUE` identity. Autopilot may not compute that identity.

### 3.1 Rejected owners

| Rejected owner | Reason |
| --- | --- |
| Autopilot | Executes directives and git fail-safes. Selection would turn execution authority into roadmap authority. |
| Supervisor | An LLM that currently infers successors from prose. Leaving selection there preserves the unsafe model this engine exists to replace. |
| Automation-M1 | Owns one operator-selected review-only manifest. It does not discover or filter successors. |
| Automation-M2 | Owns one frozen pipeline for one already-chosen `milestone_id`. |
| Automation-M3 | Named Git-execute residual. Architecture is OOB and not approved. Not a selector. |
| PF | Investment-domain owner. Construction sequencing is not its contract. |
| IRO | Investment-research operational owner. Not a development sequencer. |
| Market | Domain-structure / market-fact owner. Not a sequencer. |
| FactStore | Fact persistence and retrieval owner. `successor_of` is fact supersession, not milestone succession. |
| Portfolio allocation packages | Capital-decision structure. Not development sequencing. |
| Architecture State Resolver | Later factual-normalization owner. Normalization is not eligibility cardinality. |

---

## 4. Responsibility

The engine owns only:

1. input validation
2. dependency validation
3. derived eligibility classification
4. eligible-set cardinality
5. `CONTINUE` / `STOP` decision
6. selection evidence

It classifies **supplied records**. It does not inspect the repository,
parse documents, mutate state, choose a review/implementation phase, or
author policy.

---

## 5. Non-responsibilities

The engine must not:

- select, rank, score, or prefer among multiple eligible identities
- invent dependencies, deferrals, exclusive successors, or gates
- infer product priority, business value, or narrative later direction
- parse Constitution, roadmap, README, or architecture Markdown
- inspect git status, the `COMMIT READY` ledger, review files, or OOB
  paths
- consume, reuse, or detect unused `COMMIT READY` by itself
- execute `git add`, commit, tag, push, reset, clean, or branch mutation
- integrate Supervisor or Autopilot in the first implementation slice
- implement Architecture State Resolver
- author policy records or a live milestone registry product
- implement PF-M5 Market Watch, IRO-M3, IRO-M4, Broker Observation,
  MarketSnapshotProducer later gate, or Automation-M3
- own Stage 6 product scheduling
- own investment strategy, portfolio decisions, market data ingestion,
  KB Open API provider work, or committee research
- use an LLM for preference, ranking, or successor invention
- treat identifier prefix, numeric suffix, filename, document order, or
  timestamp as a selection key
- persist `ELIGIBLE` or `BLOCKED` as lifecycle state
- waive architecture review, implementation review, commit review,
  scoped commit rules, or OOB preservation
- authorize implementation by emitting `CONTINUE`

---

## 6. Authority boundaries

```text
Policy records
  Human / separately accepted architecture artifacts
        │  explicit identities, prerequisites, deferrals, future policy
        ▼
Fact records
  Architecture State Resolver (later, not this slice)
        │  factual normalization only
        ▼
Milestone Selection Engine
        │  CONTINUE(identity) or STOP(reason) + SelectionEvidence
        ▼
Supervisor
        │  intra-milestone action for that exact identity, or preserve STOP
        ▼
Autopilot
        │  execute the exact selected workflow only
        ▼
Human
           resolve genuine ambiguity through explicit records
```

Authority rules:

1. Later layers may consume earlier ones. They may not assume them.
2. Human silence is never authorization.
3. A `CONTINUE` decision identifies only the successor identity.
4. A `CONTINUE` decision does not waive any review gate.
5. A `CONTINUE` decision does not authorize OOB files.
6. A `CONTINUE` decision does not become git mutation authority.
7. `COMMIT READY` remains single-consumption and remains owned by
   Autopilot / the commit-review process.
8. Existing Autopilot safety gates remain independent.
9. Selection authority does not become implementation authority.

---

## 7. Input contract

### 7.1 Root input

The first-slice public input is one immutable `MilestoneSelectionInput`
containing exactly:

1. `records`: a finite collection of `MilestoneRecord`
2. `dependencies`: a finite collection of `MilestoneDependency`
3. `blocking_evidence`: a finite collection of `BlockingEvidence`

No other required input belongs to the first slice. The engine does not
read the filesystem to populate these collections.

Exact collection types are an implementation-authorization concern, but
must be exact accepted built-in types under the Constitution. Callers
must supply the collections they mean. The engine must not convert,
copy-to-normalize, or reconstruct them.

### 7.2 Required concepts

| Concept | Kind | Role |
| --- | --- | --- |
| `MilestoneIdentity` | Input value | Opaque caller-supplied exact string |
| `MilestoneRecord` | Input | Identity plus recorded facts only |
| `MilestoneDependency` | Input | Explicit `PREREQUISITE` edge plus source identity |
| `BlockingEvidence` | Input | Normalized fail-safe or unsatisfied-gate evidence |
| `MilestoneEligibility` | Derived | Per-identity classification after validation |
| `MilestoneSelectionDecision` | Output | Exactly `CONTINUE` or `STOP` |
| `SelectionEvidence` | Output | Immutable input identities and filter trace |
| `StopReason` | Output | Closed exact reason |

Do not create a speculative type zoo. The first slice does **not** add:

- persisted `MilestoneState`
- `MilestoneGate` as a standalone type
- `REQUIRED_SUCCESSOR`
- `OPTIONAL_SUCCESSOR`
- `BLOCKS`
- `RELATED`
- `PRIORITY`
- `WEIGHT`
- `SCORE`
- `MAYBE`
- `PREFER`
- `RECOMMEND`
- `WAIT_AND_GUESS`
- `BEST_CANDIDATE`
- `RANKED_LIST`

An unsatisfied required gate arrives only as `BlockingEvidence` against
one identity or against all continuation. A separate gate type may be
added later only if a proven invariant appears.

### 7.3 MilestoneRecord

`MilestoneRecord` is a minimal immutable record of explicit facts.

Required fields:

| Field | Meaning | Eligibility effect |
| --- | --- | --- |
| `identity` | Exact `MilestoneIdentity` | Subject of classification |
| `completed` | Exact Boolean recorded fact | `True` excludes the identity |
| `deferred` | Exact Boolean recorded policy fact | `True` excludes the identity |
| `oob` | Exact Boolean recorded authority fact | `True` excludes the identity |
| `superseded` | Exact Boolean recorded replacement fact | `True` excludes the identity |
| `architecture_frozen` | Exact Boolean metadata | **None** |

Field meanings:

- `completed` means implementation was accepted, committed, tagged, and
  the corresponding `COMMIT READY` was consumed. The engine does not
  verify that history. It classifies the supplied Boolean.
- `deferred` means an explicit policy record names the identity as a
  later direction that is not currently authorized.
- `oob` means the identity is outside the current commit/authority
  boundary.
- `superseded` means an explicit record states the identity is exhausted
  or replaced.
- `architecture_frozen` records only that an architecture freeze exists
  for the identity. Frozen is not completed. Frozen is not next. Frozen
  is not a lifecycle state.

A milestone may be architecture-frozen and not completed. IRO-M2 was
architecture-frozen at `v6.7` and implementation-completed only at
`v7.12`. Those facts must remain separable.

Do not persist `ELIGIBLE` or `BLOCKED` on the record.

---

## 8. Identity invariants

`MilestoneIdentity` is:

- exact
- stable
- opaque
- caller-supplied
- non-blank
- free of ordering semantics
- free of priority semantics

Additional invariants:

1. The engine never generates, derives, hashes, trims, case-folds, or
   infers an identity.
2. Comparison is exact equality only.
3. Duplicate identities in one input record set are rejected at
   validation.
4. Unknown identities fail closed. The engine does not invent a record.
5. Existing strings such as `PF-M5`, `IRO-M3`, and `Automation-M3` are
   legal **opaque identities only**.
6. The engine must not interpret `PF`, `IRO`, `Automation`, `M`, or any
   numeric suffix.
7. Identifier lexical order must not affect the decision.
8. No identity implies priority.

---

## 9. Recorded facts versus derived state

| Label | Treatment | Why |
| --- | --- | --- |
| `completed` | Recorded fact | Caller attests accepted completion |
| `deferred` | Recorded explicit policy fact | Named later direction, not currently authorized |
| `oob` | Recorded authority fact | Outside commit/authority boundary |
| `superseded` | Recorded explicit fact | Exhausted or replaced identity |
| `architecture_frozen` | Orthogonal metadata | Architecture accepted ≠ implementation completed ≠ next |
| `ELIGIBLE` | Derived only | Persisting it creates drift |
| `BLOCKED` | Derived only | Result of facts, prerequisites, or supplied blocking evidence |
| `GATED` | Not a state | A gate arrives as `BlockingEvidence` or a later record type |
| `REQUIRED SUCCESSOR` / `OPTIONAL SUCCESSOR` | Not states | Relationships. First slice needs only `PREREQUISITE` |

`MilestoneEligibility` is computed only after validation succeeds and
only after fail-closed graph checks in §11.3 have passed.

Derived classification may be traced in `SelectionEvidence`. It must not
be written back onto `MilestoneRecord`.

---

## 10. Dependency contract

### 10.1 Single first-slice dependency type

Exactly one dependency type is authorized:

**`PREREQUISITE`**

A `MilestoneDependency` must identify:

1. dependent `MilestoneIdentity`
2. prerequisite `MilestoneIdentity`
3. dependency type = exactly `PREREQUISITE`
4. source / evidence identity, opaque and non-blank

Do not add `REQUIRED_SUCCESSOR`, `OPTIONAL_SUCCESSOR`, `BLOCKS`,
`RELATED`, `PRIORITY`, `WEIGHT`, or `SCORE`.

Prerequisite satisfaction is not succession. Completing a prerequisite
makes a dependent *possible*, not *next*. PF-M3 and PF-M4 completeness
does not make PF-M5 unique. Humans later chose IRO-M2 after those
prerequisites already existed.

### 10.2 No inferred edges

The engine must never infer a dependency from:

- architecture prose
- README non-responsibility lists
- roadmap narrative
- filename adjacency
- tag-number inference
- identifier prefix or suffix
- document order
- human silence

If no `MilestoneDependency` is supplied, no prerequisite exists.

### 10.3 Dependency behavior

| Condition | Behavior |
| --- | --- |
| Missing / blank identity on a dependency record | Validation failure; no decision |
| Self-dependency | Validation failure; no decision |
| Duplicate dependency (same dependent, prerequisite, and type) | Validation failure; no decision |
| Unknown dependency type | Validation failure; no decision |
| Dependent identity not in the record set | `STOP(UNKNOWN_MILESTONE)` |
| Prerequisite identity not in the record set | `STOP(MISSING_DEPENDENCY)` |
| Prerequisite `oob is True` | Dependent is not eligible. OOB cannot satisfy a prerequisite |
| Prerequisite `completed is False` | Dependent is not eligible |
| Prerequisite `completed is True` and `oob is False` | That prerequisite is satisfied |
| Cycle among `PREREQUISITE` edges | `STOP(DEPENDENCY_CYCLE)`; no partial ranking |
| Narrative-only later direction with no record | Not a dependency. Ignored because it was never supplied |

A completed OOB identity cannot lawfully satisfy a prerequisite. If a
record asserts `completed is True` and `oob is True`, that is
`AMBIGUOUS_ARCHITECTURE_STATE` (§17), not a satisfied prerequisite.

---

## 11. Validation order

Validation-first. All inputs must be validated before eligibility
classification. Invalid input must not be partially classified.

Exact exception types are an implementation-authorization concern. They
must be stable, and upstream exceptions must propagate unchanged.

### 11.1 Validation sequence

The public selector validates in this exact order and stops at the first
validation failure:

1. Root input exact type (`MilestoneSelectionInput`).
2. `records` container exact type.
3. Each element of `records` exact type (`MilestoneRecord`).
4. Each record `identity` exact type and non-blank.
5. Duplicate record identities rejected.
6. Each recorded-fact field exact Boolean type, in field order:
   `completed`, `deferred`, `oob`, `superseded`, `architecture_frozen`.
7. `dependencies` container exact type.
8. Each element of `dependencies` exact type (`MilestoneDependency`).
9. Each dependency `dependent` exact type and non-blank.
10. Each dependency `prerequisite` exact type and non-blank.
11. Each dependency type exact and equal to `PREREQUISITE`.
12. Each dependency `source_identity` exact type and non-blank.
13. Self-dependency rejected (`dependent == prerequisite`).
14. Duplicate dependency rejected (same dependent, prerequisite, type).
15. `blocking_evidence` container exact type.
16. Each element exact type (`BlockingEvidence`).
17. Each `kind` exact and inside the closed first-slice set (§13).
18. Each `scope` exact (`GLOBAL` or `IDENTITY`).
19. `target_identity` present, exact, and non-blank if and only if
    `scope is IDENTITY`; forbidden if `scope is GLOBAL`.
20. Kind/scope pairing rejected when a global-only kind is
    identity-scoped (§13.3).
21. Each blocking-evidence `source_identity` exact type and non-blank.

The engine must not trim, sort, convert, copy, or reconstruct inputs in
order to make them valid.

### 11.2 Validation failures are not StopReasons

Shape, exact-type, blank-identity, duplicate-identity, self-dependency,
duplicate-dependency, and illegal kind/scope errors are validation
failures. They produce no `MilestoneSelectionDecision`.

They are not a second ranking path.

### 11.3 Decision-time fail-closed checks

After validation succeeds, and before eligibility classification, the
engine applies these checks in this exact order. The first match produces
`STOP` and **does not** classify eligibility:

1. `UNKNOWN_MILESTONE` — a well-formed identity referenced as a
   dependency dependent or as an identity-scoped blocking-evidence
   target is not among the supplied record identities.
2. `MISSING_DEPENDENCY` — a well-formed prerequisite identity is not
   among the supplied record identities.
3. `AMBIGUOUS_ARCHITECTURE_STATE` — a supplied identity has
   contradictory recorded facts under §17.3.
4. `DEPENDENCY_CYCLE` — the directed `PREREQUISITE` graph contains a
   cycle.

If none of these apply, eligibility classification runs.

---

## 12. Eligibility rules

A supplied identity is eligible if and only if **all** of the following
are true:

1. identity is valid and present in the known record set
2. `completed is False`
3. `superseded is False`
4. `oob is False`
5. `deferred is False`
6. every explicit prerequisite identity is known
7. every explicit prerequisite is completed and not OOB
8. no applicable identity-scoped `BlockingEvidence` blocks it
9. no global `BlockingEvidence` blocks continuation

Otherwise the identity is not eligible.

There is no hidden heuristic, default ranking, highest remaining number,
filename adjacency, or “named in a document” rule.

`architecture_frozen is True` does not make an identity eligible.
`architecture_frozen is False` does not make an identity eligible.

Multiple exclusion facts may be true together. Combinations that are not
listed in §17.3 are simply not eligible. The engine does not choose a
preferred exclusion reason to invent eligibility.

---

## 13. Blocking evidence

### 13.1 Role

`BlockingEvidence` is normalized input. The selector must not inspect
git, review files, the consumed-ledger, or the working tree to discover
these conditions.

Autopilot and the review pipeline remain the owners of detection. The
selector only applies evidence the caller already normalized.

### 13.2 Closed first-slice kinds

| Kind | Existing detection owner | First-slice scope |
| --- | --- | --- |
| `UNUSED_COMMIT_READY` | Autopilot consumed-ledger | `GLOBAL` only |
| `DIRTY_WORKING_TREE` | Autopilot / checkpoint | `GLOBAL` only |
| `OOB_CONTAMINATION` | Autopilot known-OOB guards | `GLOBAL` only |
| `UNRESOLVED_REVIEW` | Review pipeline | `GLOBAL` or `IDENTITY` |
| `MISSING_ARCHITECTURE_GATE` | Architecture / review process | `GLOBAL` or `IDENTITY` |
| `CONSTITUTION_CONFLICT` | Constitution / review board | `GLOBAL` only |
| `REPLAY_DETECTED` | Autopilot loop / completed-fact | `GLOBAL` only |
| `PARTIAL_PREVIOUS_MILESTONE` | Intra-milestone pipeline | `GLOBAL` only |

Do not expand this set in the first slice.

### 13.3 Minimum representation

`BlockingEvidence` contains exactly:

| Field | Rule |
| --- | --- |
| `kind` | Exact closed kind from §13.2 |
| `scope` | Exact `GLOBAL` or `IDENTITY` |
| `target_identity` | Required iff `IDENTITY`; forbidden iff `GLOBAL` |
| `source_identity` | Opaque non-blank evidence identity |

Presence of valid blocking evidence is sufficient. The engine does not
re-verify the underlying git or review condition.

### 13.4 Application

- Identity-scoped evidence excludes only that identity (eligibility rule
  8).
- Any supplied `GLOBAL` evidence makes every identity fail eligibility
  rule 9.
- If classification otherwise would have produced exactly one eligible
  identity, global evidence still prevents `CONTINUE`.
- The resulting eligible set is then empty, so the decision is
  `STOP(NO_ELIGIBLE_MILESTONE)` with the blocking evidence recorded.

Do not invent a ninth `StopReason` for blocking evidence. Cardinality
after application is enough, and `SelectionEvidence` already names the
evidence.

---

## 14. Cardinality semantics

After validation and fail-closed graph checks, the engine computes the
eligible set by applying §12 to every supplied record.

```text
if len(eligible_set) == 0:
    STOP(NO_ELIGIBLE_MILESTONE)
if len(eligible_set) == 1:
    CONTINUE(that exact identity)
if len(eligible_set) >= 2:
    STOP(MULTIPLE_ELIGIBLE_MILESTONES)
```

No priority engine.
No ranking engine.
No scoring.
No LLM preference.
No milestone-number ordering.
No filename ordering.
No document ordering.
No timestamp ordering.
No business-value heuristic.
No narrative inference.

### 14.1 Order independence

The following must not affect the decision class, `CONTINUE` identity,
`StopReason`, eligible-set membership, or excluded-set membership:

- candidate / record input order
- dependency input order
- blocking-evidence input order
- identifier lexical order
- dictionary / map insertion order

The same normalized input must produce the same decision.

Caller order may appear in `SelectionEvidence` as an input trace. That
trace is an audit fact, not a ranking.

---

## 15. Selection evidence

`SelectionEvidence` makes the decision auditable. It contains only
deterministic facts.

Required contents:

1. supplied record identities, in caller order
2. supplied dependency edges, in caller order
3. supplied blocking evidence, in caller order
4. whether fail-closed graph checks ran, and which `StopReason` if they
   stopped classification
5. if classification ran: per-identity derived eligibility
6. if classification ran: excluded identities with exact derived
   exclusion facts
7. if classification ran: prerequisite evaluation for each dependency
   (`known`, `completed`, `oob`, `satisfied`)
8. applied blocking evidence and whether each item was global or
   identity-scoped
9. resulting eligible identity set
10. final decision class, and either the `CONTINUE` identity or the
    `StopReason`

`SelectionEvidence` must not include:

- LLM reasoning
- subjective ranking
- business-value opinions
- implicit narrative interpretation
- scores, weights, or preferred-order lists

Derived exclusion traces are evidence, not persisted lifecycle state.

---

## 16. Decision contract

`MilestoneSelectionDecision` is immutable.

Exactly two decision classes exist:

| Class | Payload |
| --- | --- |
| `CONTINUE` | Exactly one `MilestoneIdentity` plus `SelectionEvidence` |
| `STOP` | Exactly one `StopReason` plus `SelectionEvidence` |

There is no `MAYBE`, `PREFER`, `RECOMMEND`, `WAIT_AND_GUESS`,
`BEST_CANDIDATE`, or `RANKED_LIST`.

A `CONTINUE` decision:

- identifies only the successor identity
- does not waive architecture review
- does not waive implementation review
- does not waive commit review
- does not waive scoped commit rules
- does not authorize OOB files
- does not authorize implementation by itself
- does not authorize git mutation
- does not consume or refresh `COMMIT READY`

---

## 17. STOP semantics

### 17.1 Closed first-slice StopReason set

All six reasons are necessary. Each owns a distinct invariant.

| Reason | When | Why it is not another reason |
| --- | --- | --- |
| `NO_ELIGIBLE_MILESTONE` | Valid, classifiable input; zero eligible identities | Cardinality 0 after lawful classification |
| `MULTIPLE_ELIGIBLE_MILESTONES` | Valid, classifiable input; two or more eligible identities | Cardinality N; not a ranking request |
| `UNKNOWN_MILESTONE` | A dependent or identity-scoped blocking target is not in the record set | Closed-world failure for a referenced subject, not a missing prerequisite |
| `MISSING_DEPENDENCY` | A prerequisite identity is not in the record set | Graph-completeness failure on a `PREREQUISITE` edge |
| `DEPENDENCY_CYCLE` | Cycle among supplied `PREREQUISITE` edges | Well-typed graph that cannot be classified without ranking |
| `AMBIGUOUS_ARCHITECTURE_STATE` | Contradictory recorded facts for one identity (§17.3) | Classification would require choosing an interpretation |

Do not invent additional first-slice reasons.

### 17.2 Fail-closed preference

If a condition could be treated as either “exclude one identity and
continue” or “stop the whole selection,” the engine must stop unless this
document explicitly classifies the condition as a per-identity exclusion.

Unknown identities, missing prerequisites, cycles, and contradictory
facts stop the whole selection. They must not be repaired by dropping
the offending record and classifying the remainder.

### 17.3 First-slice contradictory facts

After validation, the following combination on one identity is
`AMBIGUOUS_ARCHITECTURE_STATE`:

1. `completed is True` and `oob is True`

A completed identity cannot lawfully be outside the authority boundary.
The engine does not prefer `completed` or `oob`.

A supplied `PARTIAL_PREVIOUS_MILESTONE` evidence item remains global
blocking evidence under §13. It does not create this `StopReason`. If
present and the input is otherwise classifiable, it prevents `CONTINUE`
through eligibility rule 9.

Other Boolean combinations (`completed` and `deferred`, `deferred` and
`oob`, `completed` and `superseded`, and so on) are coherent exclusions
or coherent historical facts. They do not produce this `StopReason`.

`architecture_frozen` never participates in contradiction. It has no
eligibility meaning and must not be interpreted as completion.

---

## 18. Supervisor boundary

Supervisor consumes the selection decision. Supervisor does not produce
it.

```text
Milestone Selection Engine → decision
Supervisor → consumes decision
```

If `CONTINUE`:

- Supervisor may issue only the appropriate intra-milestone action for
  **that exact identity**.
- Supervisor still chooses among `RUN_REVIEW`, `COMMIT`, and `STOP` for
  that identity's current gate.
- Supervisor may not substitute another milestone identity.

If `STOP`:

- Supervisor must preserve `STOP`.
- Supervisor may not treat engine silence, a missing decision, or an
  old decision as authorization.

Supervisor remains an LLM-owned intra-milestone actor. This architecture
does not absorb that job and does not authorize Supervisor integration
in the first implementation slice.

---

## 19. Autopilot boundary

Autopilot executes the exact selected workflow only.

Autopilot must never:

- select another successor
- override `STOP`
- rank candidates
- repair ambiguity
- infer dependencies
- reuse stale `COMMIT READY`

Minimum later enforcement invariant, **not** part of the first slice:

> Autopilot may start a successor workflow only when the current unused
> decision is `CONTINUE` with exactly one identity, and that identity
> equals the workflow’s milestone identity. Any other decision, a
> missing decision, or an identity mismatch is fail-closed STOP.

Autopilot remains the owner of:

- unused versus consumed `COMMIT READY`
- known OOB path preservation
- dirty-tree and unexpected-path fail-safes
- path-scoped add / commit / tag / push
- replay / loop bounds

The selector must not duplicate those detection responsibilities.

---

## 20. Human gate

The human is needed only when authoritative explicit records do not
determine exactly one valid successor, or when a fail-closed state
requires explicit remediation.

Frozen human-gate rules:

1. Human selection must be represented as an **explicit record** before
   autonomous continuation may resume.
2. Human silence is never authorization.
3. Informal chat, untracked prompts, or operational prose such as
   “human selected PF-M5” is not a record.
4. The engine must not treat the absence of a deferral as approval.
5. Existing fail-closed STOPs remain in force until an explicit record
   changes the supplied input.
6. Policy-record ownership stays with humans / separately accepted
   architecture artifacts. The engine never authors those records.

---

## 21. Architecture State Resolver boundary

Architecture State Resolver is a **separate later component**.

It is not part of this owner. It is not part of the first implementation
slice.

### 21.1 Later factual responsibility

The resolver may later normalize facts such as:

- HEAD
- exact tag
- working-tree state
- completed milestone identity
- accepted architecture metadata
- accepted review state
- unused `COMMIT READY`
- OOB paths
- replay state

into `MilestoneRecord` and `BlockingEvidence` values.

### 21.2 Forbidden resolver behavior

The resolver must not:

- select
- rank
- invent dependencies
- infer product priority
- infer exclusive successors
- repair ambiguity
- parse architecture Markdown into a dependency graph

Combining resolver and engine now would mix git/ledger observation with
eligibility classification and violate one-owner responsibility.

Deferring the resolver does not block this architecture. The first slice
is caller-supplied and side-effect free.

---

## 22. Current v7.12 expected behavior

This engine does **not** make PF-M5 next.

At the current `v7.12` architecture state there is no tracked
authoritative general milestone registry or dependency graph sufficient
to produce one unique successor.

Therefore a lawful current application must fail closed.

Depending on the normalized supplied records, the result may be:

- `STOP(NO_ELIGIBLE_MILESTONE)`
- `STOP(MULTIPLE_ELIGIBLE_MILESTONES)`
- another exact fail-closed condition from §17

That is correct behavior.

Current facts that prevent `CONTINUE(PF-M5)` include:

- tracked roadmap v1.2 does not name PF-M5 as the unique successor
- PF-M3 / PF-M4 completeness is prerequisite possibility, not uniqueness
- the PF-M5 uniqueness review at `v7.11` ended `REVIEW BLOCKED`
- IRO-M2 completion removes IRO-M2 from leftover implementation; it does
  not make Market Watch unique
- post-commit Supervisor already issued `STOP` because remaining work is
  unranked
- untracked product-architecture sequencing is OOB and non-authoritative
- no tracked milestone registry, dependency file, or eligibility ledger
  exists

If the engine is applied to the records that actually exist today
(none), the decision is `STOP(NO_ELIGIBLE_MILESTONE)`.

If the engine is later applied to an explicit set containing currently
discussed open identities such as `PF-M5`, `IRO-M3`, `Automation-M3`,
later broker-observation, MarketSnapshotProducer later-gate, and IRO-M4,
with no exclusive-successor record, the decision is
`STOP(MULTIPLE_ELIGIBLE_MILESTONES)`.

The selector is valuable even when it returns `STOP`.

---

## 23. First implementation slice

This document authorizes **no** implementation.

If a later board authorizes implementation, the first slice may contain
only:

1. immutable models
2. validation
3. dependency validation
4. eligibility classification
5. 0 / 1 / N selection
6. `SelectionEvidence`
7. `StopReason`
8. focused unit tests
9. README stating public API and non-responsibilities

### 23.1 Required first-slice properties

The first implementation slice must be:

- side-effect free
- filesystem free
- git free
- network free
- LLM free
- Markdown-parser free
- Supervisor free
- Autopilot integration free

### 23.2 Later hosting

- Architecture freeze: this tracked JOO document under
  `docs/automation/`
- Implementation, if later authorized: JOO-Automation, as a new isolated
  component
- Do not implement inside a JOO investment-domain package
- Do not extend `joo_auto` M1 / M2 / M3 phase machinery
- Do not import JOO PF / IRO / Market / FactStore / allocation packages
- Do not invent `Automation-M4` or `Autopilot-M1` as the package
  identity
- Exact package / module names are deferred to implementation
  authorization and must remain unnumbered descriptive identities

### 23.3 Explicitly out of the first slice

- Architecture State Resolver implementation
- Supervisor integration
- Autopilot integration
- automatic continuation loop
- git status inspection
- commit review inspection
- `COMMIT READY` consumption
- `git add`, commit, tag, push
- roadmap parsing
- architecture document parsing
- LLM ranking
- business-value ranking
- PF-M5 Market Watch
- IRO-M3 / IRO-M4
- Broker Observation
- MarketSnapshotProducer later gate
- Automation-M3 Human-Gated Git Executor
- Stage 6 product scheduling
- investment strategy
- portfolio decisions
- market data ingestion
- KB Open API provider work
- committee research
- policy-record authoring UI or registry product

---

## 24. Test invariants

A later implementation must prove at least the following. These tests
are not authored by this document.

| Invariant | Expected |
| --- | --- |
| Zero candidates | `STOP(NO_ELIGIBLE_MILESTONE)` |
| One valid candidate | `CONTINUE` exact identity |
| Multiple valid candidates | `STOP(MULTIPLE_ELIGIBLE_MILESTONES)` |
| Completed candidate | excluded |
| Deferred candidate | excluded |
| OOB candidate | excluded |
| Superseded candidate | excluded |
| Missing prerequisite | blocks dependent |
| Incomplete prerequisite | blocks dependent |
| Completed prerequisite | permits dependent if all other rules pass |
| Unknown dependency | fail closed |
| Duplicate identity | rejected as validation failure |
| Self-dependency | rejected as validation failure |
| Duplicate dependency | rejected as validation failure |
| Dependency cycle | `STOP(DEPENDENCY_CYCLE)` |
| Identifier number | does not affect selection |
| Identifier prefix | does not affect selection |
| Candidate input order | does not affect selection |
| Dependency input order | does not affect selection |
| Same normalized input | same result |
| Global `BlockingEvidence` | prevents `CONTINUE` even if one candidate would otherwise be unique |
| OOB prerequisite | cannot satisfy a dependent |
| `completed and oob` on one identity | `STOP(AMBIGUOUS_ARCHITECTURE_STATE)` |
| `architecture_frozen` only | does not create eligibility or succession |
| No git / filesystem / network / LLM behavior | static and behavioral absence in the first slice |

Normal, boundary, wrong-type, empty-value, order, and exception-propagation
cases required by the repository agent contract apply to every public
entry point.

---

## 25. Failure modes

| Failure | Required behavior |
| --- | --- |
| Wrong input / record / dependency / evidence type | Validation failure; no decision |
| Blank identity | Validation failure; no decision |
| Duplicate identity | Validation failure; no decision |
| Self-dependency | Validation failure; no decision |
| Duplicate dependency | Validation failure; no decision |
| Unknown kind or illegal scope pairing | Validation failure; no decision |
| Unknown referenced subject identity | `STOP(UNKNOWN_MILESTONE)` |
| Unknown prerequisite identity | `STOP(MISSING_DEPENDENCY)` |
| Dependency cycle | `STOP(DEPENDENCY_CYCLE)` |
| Contradictory recorded facts | `STOP(AMBIGUOUS_ARCHITECTURE_STATE)` |
| Zero eligible identities | `STOP(NO_ELIGIBLE_MILESTONE)` |
| Two or more eligible identities | `STOP(MULTIPLE_ELIGIBLE_MILESTONES)` |
| Global blocking evidence | No `CONTINUE`; cardinality 0 |
| Narrative / Markdown / filename / tag inference | Forbidden; must not occur |
| Missing decision consumed by Supervisor or Autopilot | Later consumers must fail closed |
| Stale `COMMIT READY` | Remains Autopilot fail-closed; selector must not repair it |
| Implementation attempted from this document alone | Unauthorized |

The engine must not hide, coerce, or rank its way out of any failure
mode.

---

## 26. Frozen invariants

1. Fail-safe `STOP` is preferred to speculative continuation.
2. No decision may be produced from narrative inference.
3. No milestone identity implies priority.
4. No LLM decides what to build next.
5. No selection decision authorizes implementation by itself.
6. A `CONTINUE` decision identifies only the successor identity.
7. `CONTINUE` does not waive architecture review.
8. `CONTINUE` does not waive implementation review.
9. `CONTINUE` does not waive commit review.
10. `CONTINUE` does not waive scoped commit rules.
11. `CONTINUE` does not authorize OOB files.
12. `COMMIT READY` remains single-consumption.
13. Existing Autopilot safety gates remain independent.
14. Selection authority does not become git mutation authority.
15. One owner per responsibility: the owner is Milestone Selection
    Engine.
16. Autopilot, Supervisor, Automation-M1, Automation-M2, Automation-M3,
    PF, IRO, Market, FactStore, allocation packages, and Architecture
    State Resolver do not own this responsibility.
17. Identities are exact, opaque, caller-supplied, and non-blank.
18. Duplicate identities are rejected.
19. Unknown identities fail closed.
20. `ELIGIBLE` and `BLOCKED` are derived, never persisted lifecycle
    state.
21. `architecture_frozen` is metadata, not a lifecycle state and not an
    eligibility rule.
22. The only first-slice dependency type is `PREREQUISITE`.
23. Dependencies are never inferred from prose, filenames, tags, or
    silence.
24. OOB cannot satisfy a prerequisite.
25. Self-dependency and duplicate dependency are validation failures.
26. A dependency cycle is `STOP(DEPENDENCY_CYCLE)`.
27. Candidate, dependency, and map order cannot change the decision.
28. Same normalized input produces the same result.
29. Validation precedes all eligibility classification.
30. Invalid input is not partially classified.
31. Cardinality 0 / 1 / N is the only selection rule.
32. There is no ranking, scoring, or preference engine.
33. The closed `StopReason` set is exactly the six values in §17.1.
34. At `v7.12`, lawful live application fails closed and does not emit
    `CONTINUE(PF-M5)`.
35. Milestone ID remains `UNRESOLVED`.
36. This document does not authorize implementation, PF-M5, Autopilot
    continuation, commit, tag, or push.
37. The two known OOB documents remain non-authoritative and outside
    this architecture's commit boundary.
38. Development automation must not distort JOO's investment-product
    architecture.

---

## 27. Authorization freeze

| Question | Answer |
| --- | --- |
| Architecture document authored | Yes |
| Independent architecture review | Required next |
| Implementation authorized | **NO** |
| PF-M5 authorized | **NO** |
| Autopilot continuation authorized | **NO** |
| Automation-M3 authorized | **NO** |
| Architecture State Resolver authorized | **NO** |
| Supervisor integration authorized | **NO** |
| Commit / tag / push authorized | **NO** |
| Human decision required now | **NO** |
| Milestone ID | **UNRESOLVED** |
| Owner | **Milestone Selection Engine** |
