# JOO Loop Core Architecture

## Status and identity

- Status: Architecture authored for independent review; freeze only
- Product: JOO
- Plane: **Domain-independent orchestration** — not an investment-domain
  plane and not a development-pipeline plane
- Identity: **JOO Loop Core**
- Owner: **JOO Loop Core**
- Scope: **DOMAIN-INDEPENDENT CONTINUOUS MISSION/TASK ORCHESTRATION**
- Milestone ID: **UNRESOLVED**
- This document does **not** invent or assign `Loop-M1`, `Automation-M4`,
  `Autopilot-M1`, `PF-M5`, `IRO-M3`, `M55+`, Architecture State Resolver,
  or any other manufactured successor identity
- Authorizing review:
  `~/JOO-Automation/results/universal_loop_orchestrator_candidate_architecture_review/latest.md`
  — **FINAL DECISION: UNIVERSAL LOOP ORCHESTRATOR ARCHITECTURE READY**
- Architecture location: `docs/orchestration/JOO_LOOP_CORE_ARCHITECTURE.md`
- Later implementation location, if separately authorized: an isolated
  JOO-Automation package. Not `joo_auto`. Not
  `milestone_selection_engine`. Not an IRO package. Not a JOO
  investment-domain package
- Repository boundary for this document: architecture authoring only;
  this document alone authorizes no production code, test, package
  scaffold, schema module, configuration, run artifact, Autopilot run,
  live KB call, Keychain mutation, runtime state, stage, commit, tag, or
  push

This document freezes the **smallest domain-independent loop core**.

It answers only:

> How does JOO persist missions and tasks, derive eligibility, queue
> human approval, authorize irreversible execution, recover after
> interruption, accept trigger ingress, and decide
> `CONTINUE_TASK` / `IDLE` / `GLOBAL_STOP` without owning any domain?

It does **not** answer:

> What should be engineered next, what should be traded, or how a
> planner / model / daemon should run the business?

This document does **not** claim a full AI Operating System.

This document does **not** build a universal multi-agent platform.

This document does **not** redesign Milestone Selection Engine,
Supervisor, Autopilot, `joo_auto`, IRO, Provider, or CIO.

Implementation is **not** authorized.

Autopilot is **not** run by this document.

Automatic trading is **not** authorized.

Automatic push is **not** authorized.

Daemon implementation is **not** authorized.

Scheduler implementation is **not** authorized.

---

## 1. Purpose

JOO already has two live operational planes:

- **Development automation** — Milestone Selection Engine, Supervisor,
  Autopilot, and `joo_auto` execute one engineering successor at a time
  and stop the process when a human gate, review gate, or successor
  ambiguity appears
- **Investment research** — IRO, Provider, and related contracts produce
  research and CIO posture. They do not execute orders and they are not
  a domain-independent loop

Those planes are valid. They are not a universal loop.

The missing owner is a **single continuation authority** that can:

1. hold many missions across many domains;
2. persist task state independently of any one process lifetime;
3. derive eligibility without inventing domain meaning;
4. continue independent work while one task waits;
5. idle safely when nothing is executable;
6. stop globally only for true global halt conditions;
7. recover after crash, terminal close, or reboot without inferring
   completion.

JOO Loop Core owns that loop. Domain meaning stays in adapters.

The first proof domain is **Engineering**.

The second proof domain is **Trading**.

Future domains such as Brand, Legal, Manufacturing, Marketing, Finance,
and others must be addable through adapters without redesigning this
core.

---

## 2. Context

### 2.1 Checkpoint at authoring

This architecture is authored against the verified JOO checkpoint:

| Check | Value |
| --- | --- |
| Repository | `/Users/takesimple/Projects/JOO` |
| Branch | `feature/stage2-provider-runtime` |
| HEAD | `da557df4eb0f7e56d7713aa7117d74c9d8a0eac1` |
| Exact tag | `v7.22-stage5-kb-openapi-runtime-credential-configuration` |
| HEAD subject | Add KB OpenAPI Runtime Credential Configuration implementation |
| Tracked working tree | Clean |
| Staged set | Empty |

Intentionally untracked OOB files exist and remain
**non-authoritative**:

- `docs/JOO_PRODUCT_ARCHITECTURE.md`
- `docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md`

This architecture must not consume, modify, stage, or treat either OOB
file as frozen loop-core law.

`docs/JOO_PRODUCT_ARCHITECTURE.md` is investment-shaped product prose.
It is not the source of loop-core identity, continuation, or state.

Automation-M3 is OOB, not accepted, and not implemented. This freeze
reuses only the **safe authorization pattern**. It does not adopt the
OOB M3 document as law and does not create a second git executor.

Roadmap Stage 6 scheduling, monitoring, and recovery remain later
product scope. This document does not implement Stage 6 and does not
silently become a daemon or scheduler.

### 2.2 Existing contracts that constrain this freeze

| Contract | Status | What it already owns | What it must not become |
| --- | --- | --- | --- |
| Milestone Selection Engine | Frozen and implemented | Engineering successor-identity cardinality only. `0/1/N`. `ELIGIBLE` derived, never persisted. Fail-closed `STOP` is success | A multi-task queue, ranker, 24/7 loop, or continue-other-work engine |
| MSE Runtime Integration | Frozen and implemented | One successor decision per inter-milestone cycle. Unbounded successor looping is forbidden | The universal loop |
| Supervisor | Live intra-milestone actor | `RUN_REVIEW` / `COMMIT` / `STOP` for an already selected engineering identity | Loop continuation authority |
| Autopilot v5 | Live engineering executor | Serial engineering execution, exact-path git, `COMMIT READY` single-consumption, process-bound `STOP` | Domain-independent core, daemon, or parallel-work engine |
| `joo_auto` Automation-M1/M2 | Frozen and implemented; schema v1/v2 only | One manifest, exclusive lock, human approve after every review, print-only git. Interrupted `running` is not auto-repaired | Universal loop or parallel missions |
| Automation-M3 | **OOB, not accepted, not implemented** | Candidate pattern only: distinct authorize action, bound fingerprint, single-use, re-verify at execute, remote publication forbidden | Frozen law. Do not absorb the OOB document |
| Autopilot Repository Target | Frozen and implemented | Allowlisted `JOO` vs `JOO_AUTOMATION` bind. Tag/push are not implied by target | Repository chooser for the loop core |
| IRO / IRO-M1 / IRO-M2 | Frozen investment-research plane | Portfolio-first research lifecycle. Stops at human authority. No orders | Domain-independent loop or trading execution |
| Provider / KB OpenAPI Runtime Credential Configuration | Operationally complete at this HEAD | Zero-input Keychain retrieval for live read. No scheduler, no orders, no Autopilot attachment | Loop core, daemon, or trading lane |
| `docs/JOO_PRODUCT_ROADMAP.md` v1.2 | Approved product direction | Stage 6 is later scheduling / monitoring / recovery | Current implementation authorization |

### 2.3 Proven current stop, not a defect of this freeze

Live engineering automation is process-bound and single-lane:

1. `joo_auto` waits after every review for human `approve`.
2. Autopilot `STOP` exits the process. One human or review gate occupies
   the only lane.
3. Milestone Selection Engine turns two eligible successor identities
   into `STOP(MULTIPLE_ELIGIBLE_MILESTONES)`.
4. Runtime integration allows one engineering successor decision per
   cycle and forbids unbounded looping.
5. There is no domain-independent approval queue, operator brief,
   trigger ingress, or resume-after-reboot contract.

That behavior remains lawful for engineering successor selection.

It is **not** continue-other-work.

JOO Loop Core exists so those nested authorities can stay unchanged
while independent work continues.

---

## 3. Architecture identity

| Field | Frozen value |
| --- | --- |
| Owner | JOO Loop Core |
| Identity | JOO Loop Core |
| Scope | Domain-independent continuous mission/task orchestration |
| Arrangement | **B** — new JOO Loop Core + existing Autopilot inside the Engineering Adapter |
| Continuation authority | JOO Loop Core only |
| First proof domain | Engineering |
| Second proof domain | Trading |

The core owns:

- mission state
- task state
- derived eligibility
- approval queue
- continuation
- persistence
- recovery
- trigger ingress
- execution authorization
- operator brief

The core does **not** own:

- trading logic
- engineering workflow semantics
- brand design logic
- legal logic
- KB OpenAPI
- CIO logic
- git semantics
- model-specific semantics

The core must not contain ticker symbols, portfolio logic, legal rules,
brand rules, engineering implementation details, KB OpenAPI semantics,
CIO logic, or design-system logic.

---

## 4. Arrangement and relationship to existing Autopilot

### 4.1 Arrangement B

```text
JOO Loop Core
  CONTINUE_TASK / IDLE / GLOBAL_STOP
        │
        ├── Engineering Adapter          (first proof domain)
        │     ├── Milestone Selection Engine
        │     ├── Supervisor
        │     ├── Autopilot
        │     ├── joo_auto
        │     ├── review command / review artifacts
        │     └── existing git safety
        │
        ├── Trading Adapter              (second proof domain)
        │     ├── Provider / broker_fact
        │     ├── FactStore / Snapshot later as authorized
        │     ├── IRO
        │     ├── committees
        │     └── CIO report transform
        │
        └── Future adapters
              Brand / Legal / Manufacturing / Marketing / Finance / others
```

This is **arrangement B**:

```text
New JOO Loop Core
+
Existing Autopilot inside Engineering Adapter
```

Do **not** generalize the existing Autopilot into the universal core.

Do **not** delete or rewrite Autopilot now.

Do **not** silently add a queue to Autopilot. That would create a second
continuation authority.

### 4.2 Nested authorities remain valid and scoped

| Existing owner | Relationship to JOO Loop Core |
| --- | --- |
| Milestone Selection Engine | Unchanged. Sole authority for **engineering successor-identity cardinality**. Invoked only by the Engineering Adapter. `0/1/N` remains. Multiple eligible *milestones* still stop that successor question; they do not become a global loop stop |
| Supervisor | Unchanged intra-engineering-milestone actor. Vocabulary stays `RUN_REVIEW` / `COMMIT` / `STOP`. Not a fourth action. Not loop continuation authority |
| Autopilot | Unchanged executor of engineering `RUN_REVIEW` / `COMMIT` / `STOP`. Becomes the Engineering Adapter’s mutation worker. Does not compute loop continuation. Existing git fail-safes, exact-path staging, and `COMMIT READY` remain Autopilot-owned |
| `joo_auto` | Unchanged engineering pipeline machinery consumed by the Engineering Adapter. Not the loop core |
| Human-Gated Git Executor (M3) | **Not frozen. Not implemented. Not reused as a module.** Only the safe pattern is reused: distinct execution authorization, bound fingerprint, single-use, re-verify at execute, review success ≠ execute authority, remote publication forbidden |
| IRO / Provider / CIO | Unchanged investment-research machinery consumed by the Trading Adapter. Not the loop core |

MSE `0/1/N` remains unchanged.

`MULTIPLE_ELIGIBLE_MILESTONES` remains an **Engineering successor
ambiguity**, not a global loop stop.

If the Engineering Adapter reports MSE
`STOP(MULTIPLE_ELIGIBLE_MILESTONES)`, that engineering successor task
becomes `WAITING_HUMAN` or remains ineligible. Other eligible tasks
continue.

There must not be a second Autopilot-level “keep selecting the next
milestone” loop. Frozen MSE runtime integration stays: one engineering
successor decision per inter-milestone cycle, inside the Engineering
Adapter.

Loop Core must not re-rank, replace, or repair an MSE `STOP`.

---

## 5. One continuation authority

This section is load-bearing.

**JOO Loop Core is the ONE loop-level continuation authority.**

Only JOO Loop Core may decide:

```text
CONTINUE_TASK
IDLE
GLOBAL_STOP
```

Existing nested authorities remain valid but scoped:

| Question | Sole owner |
| --- | --- |
| May the loop run, idle, or globally halt? | JOO Loop Core |
| Is there exactly one lawful next engineering milestone identity? | Milestone Selection Engine |
| What intra-engineering-milestone action is legal for that identity? | Supervisor |
| How is that engineering directive executed safely? | Autopilot |
| What does a trading, research, legal, or brand task mean? | The owning domain adapter |

No nested component may continue the universal loop independently.

No duplicate continuation authority.

MSE `CONTINUE(identity)` is not `CONTINUE_TASK`.

Supervisor `RUN_REVIEW` / `COMMIT` is not `CONTINUE_TASK`.

Autopilot process continuation is not loop continuation.

A Domain Adapter may interpret domain evidence and emit candidate tasks.
It may not decide loop continuation.

---

## 6. Core responsibilities

The core freezes only these twelve responsibilities:

1. **Mission Registry** — persistent missions with opaque objectives
2. **Task Queue** — explicit tasks, dependencies, priority, attempts, and
   opaque payload
3. **Derived Eligibility Engine** — eligibility is computed, never stored
4. **CandidateTask ingress** — adapters submit candidate records; planner
   output is data only
5. **Capability / Policy dispatch** — `capability_id` plus independence
   constraints; no model engine
6. **Human Approval Queue** — durable approve / reject / expire /
   supersede; does not halt unrelated work
7. **ExecutionAuthorization** — required for `IRREVERSIBLE_EXTERNAL`
8. **Durable State Store** — file-based, restart-safe, no database
9. **CONTINUE_TASK / IDLE / GLOBAL_STOP** — the only loop-level
   continuation machine
10. **Recovery markers** — interrupted worker / review / approval /
    process; no inferred completion
11. **Trigger ingress** — accept `SCHEDULED` / `EVENT` / `CONDITION` as
    data
12. **Operator Brief** — generic machine-generated summary

Explicitly excluded from the core:

- generic planner engine
- generic re-planner engine
- multi-agent framework
- scheduler implementation
- daemon implementation
- model framework
- database platform

Planner or model output may enter only as `CandidateTask` data.

Planner output is never execution authority.

Reviewer and verifier are workers with independence constraints, not
core engines.

---

## 7. Mission contract

A Mission is the durable unit of operator intent. The core stores it. The
core does not understand it.

### 7.1 Required fields

| Field | Meaning |
| --- | --- |
| `mission_id` | Caller-supplied opaque identity |
| `domain_adapter_id` | Owning adapter. Core uses this only as a dispatch key |
| `objective_payload` | Opaque to the core |
| `state` | One of the mission states below |
| `created_at` | Immutable creation timestamp |
| `updated_at` | Last durable mutation timestamp |

Do not add trading, design, legal, engineering, or CIO-specific fields.

The mission objective must remain opaque to the core.

Mission identities are caller-supplied opaque strings. The core must not
invent domain meaning from `mission_id` text.

### 7.2 Mission states

```text
ACTIVE
PAUSED
BLOCKED
COMPLETED
```

| State | Loop effect |
| --- | --- |
| `ACTIVE` | Tasks of this mission may become derived-eligible |
| `PAUSED` | Tasks of this mission are not executable. Other missions may continue |
| `BLOCKED` | Tasks of this mission are not executable. Other missions may continue |
| `COMPLETED` | No new work is claimed for this mission. Historical tasks remain durable |

Mission-specific pause or block is **not** `GLOBAL_STOP`.

The core must not infer `COMPLETED` from domain payload. Completion is an
explicit recorded transition.

---

## 8. Task contract

A Task is the durable unit of work. The core stores it, derives
eligibility from it, and never interprets its payload.

### 8.1 Required fields

| Field | Meaning |
| --- | --- |
| `task_id` | Caller-supplied opaque identity |
| `mission_id` | Owning mission |
| `task_type` | Adapter-declared type. Opaque to core semantics |
| `opaque_payload` | Domain data. Core must never interpret it |
| `dependency_ids` | Explicit prerequisite `task_id` list |
| `priority` | Explicit caller- or adapter-supplied comparable priority |
| `state` | One persisted task state from Section 9 |
| `required_capabilities` | Capability identifiers required to execute, review, or verify |
| `review_policy` | Whether independent review is required |
| `execution_policy` | Whether start/completion is auto, human-gated, or forbidden |
| `execution_class` | `REVERSIBLE_LOCAL` or `IRREVERSIBLE_EXTERNAL` |
| `protected_resource_id` | Serialized mutation resource, if any |
| `attempt` | Integer attempt number. First attempt is `1` |
| `created_at` | Immutable creation timestamp |
| `updated_at` | Last durable mutation timestamp |
| `result_pointer` | Pointer, id, or hash to result evidence. Never raw secrets |

Do not over-model optional metadata.

Core must never interpret `opaque_payload`.

Core must never invent `priority`.

Core must never treat `task_id` lexical order as a safety tie-break.

### 8.2 CandidateTask ingress

Adapters, or a later planner plugin, submit `CandidateTask` records.

A `CandidateTask` is ingress data. It becomes a persisted `PLANNED` task
only after validation.

Planner / model output may be copied into `opaque_payload`. That copy is
data. It is not authority.

The core never runs a model as planner.

---

## 9. Task state machine

`ELIGIBLE` is **derived only**. It is never persisted.

This is the same derived-vs-persisted invariant as Milestone Selection
Engine, applied to tasks rather than successor identities.

### 9.1 Persisted states

```text
PLANNED
RUNNING
WAITING_REVIEW
WAITING_VERIFICATION
WAITING_HUMAN
WAITING_EXTERNAL
COMPLETED
FAILED
BLOCKED
DEFERRED
SUPERSEDED
```

### 9.2 Legal transitions

| From | To | Trigger |
| --- | --- | --- |
| `PLANNED` | `RUNNING` | Derived eligible and worker claimed under a lawful continuation decision |
| `PLANNED` | `WAITING_HUMAN` | `HUMAN_APPROVAL_REQUIRED` before start |
| `PLANNED` | `WAITING_EXTERNAL` | External dependency wait before start |
| `PLANNED` | `BLOCKED` | Integrity failure, equal-priority resource contention, or adapter block |
| `PLANNED` | `DEFERRED` | Explicit policy deferral |
| `PLANNED` | `SUPERSEDED` | Explicit replacement by a new `task_id` |
| `RUNNING` | `WAITING_REVIEW` | Worker completed and `REVIEW_REQUIRED` |
| `RUNNING` | `WAITING_VERIFICATION` | Worker completed; verify required; review not required or already satisfied |
| `RUNNING` | `WAITING_HUMAN` | Policy requires human after work |
| `RUNNING` | `WAITING_EXTERNAL` | External wait discovered in-run |
| `RUNNING` | `COMPLETED` | `AUTO_ALLOWED` and no remaining review, verify, or authorize gate |
| `RUNNING` | `FAILED` | Non-retryable failure or retry exhausted |
| `RUNNING` | `BLOCKED` | Integrity failure or observed partial irreversible mutation |
| `WAITING_REVIEW` | `WAITING_VERIFICATION` | Independent review passed and verify remains |
| `WAITING_REVIEW` | `WAITING_HUMAN` | Review passed or review policy requires human next |
| `WAITING_REVIEW` | `COMPLETED` | Review passed and no remaining gate |
| `WAITING_REVIEW` | `FAILED` | `REVIEW_FAILED` |
| `WAITING_VERIFICATION` | `WAITING_HUMAN` | Verification passed and human gate remains |
| `WAITING_VERIFICATION` | `COMPLETED` | Verification passed and no remaining gate |
| `WAITING_VERIFICATION` | `FAILED` | `VERIFICATION_FAILED` |
| `WAITING_HUMAN` | `RUNNING` | Explicit approve and work still remains |
| `WAITING_HUMAN` | `WAITING_VERIFICATION` | Explicit approve and verify remains |
| `WAITING_HUMAN` | `COMPLETED` | Explicit approve and no remaining work or gate |
| `WAITING_HUMAN` | `FAILED` | Explicit reject or policy-terminal expiry |
| `WAITING_HUMAN` | `SUPERSEDED` | Explicit replacement by a new `task_id` |
| `WAITING_EXTERNAL` | `PLANNED` | External dependency resolved |
| `WAITING_EXTERNAL` | `FAILED` | External dependency expired or failed |
| `WAITING_EXTERNAL` | `SUPERSEDED` | Explicit replacement by a new `task_id` |
| `FAILED` | `PLANNED` | Lawful retry: same `task_id`, `attempt + 1`, evidence preserved |
| `BLOCKED` | none automatically | Explicit remediation record required |

### 9.3 Forbidden transitions and invariants

- `COMPLETED` cannot return to `RUNNING`
- new work requires a new `task_id`
- required review cannot be skipped
- required verifier cannot be skipped
- independent reviewer must not be the same invocation identity as the
  worker
- silent state mutation is forbidden
- irreversible retry requires a new `ExecutionAuthorization`
- all transitions generate durable event evidence
- successful review is not execute authority
- human approve-to-continue is not `ExecutionAuthorization`
- `ELIGIBLE` must never be written as persisted state

Verification is required when the adapter declares a `VERIFIER`
capability or otherwise records that a verifier must run. The core does
not infer verification from domain payload.

---

## 10. Eligibility

Eligibility is derived.

A task is derived-eligible only when all of the following are true:

- persisted `state == PLANNED`
- owning mission `state == ACTIVE`
- all `dependency_ids` identify tasks in `COMPLETED`
- the task is not deferred, superseded, or blocked
- the task is not waiting human or waiting external
- `execution_policy` is not `FORBIDDEN`
- required capabilities are available
- the protected mutation resource, if any, is available

`N` eligible tasks is **LAWFUL**.

This must explicitly differ from Milestone Selection Engine `0/1/N`:

| Question | MSE | JOO Loop Core |
| --- | --- | --- |
| Subject | Engineering successor identities | Generic tasks |
| `N` ready items | `STOP(MULTIPLE_ELIGIBLE_MILESTONES)` | Lawful. Select by explicit priority |
| `0` ready items | `STOP(NO_ELIGIBLE_MILESTONE)` | `IDLE`, not `GLOBAL_STOP` |
| Ambiguity owner | Engineering successor question | Resource contention or core-level loop ambiguity, each scoped as defined below |

Core may select among multiple eligible tasks using explicit
caller/adapter `priority`.

Equal priority on the same `protected_resource_id`:

- execute neither automatically
- do not lexical-sort `task_id` to break the safety tie
- hold the contended tasks
- continue unrelated work

Equal-priority resource contention is **not** core-level
`AMBIGUOUS_NEXT_ACTION`.

It is not `GLOBAL_STOP`.

Unrelated tasks may continue.

A capability is “available” only when a worker binding exists for that
`capability_id` and any required independence role can be satisfied.
Absence of a required independent reviewer makes a `REVIEW_REQUIRED`
task non-executable. That is `IDLE` or task-local block, not
`GLOBAL_STOP`.

---

## 11. Continuation decision

The continuation decision is a machine-readable object. Prose is not a
decision.

### 11.1 Decision kinds

Exactly these three kinds exist:

```text
CONTINUE_TASK
IDLE
GLOBAL_STOP
```

| Kind | Meaning |
| --- | --- |
| `CONTINUE_TASK` | Exactly one `task_id` is now authorized to be claimed |
| `IDLE` | No executable eligible task exists now. The system remains healthy and may resume on trigger, approval, or external event |
| `GLOBAL_STOP` | Automatic continuation is prohibited until explicit remediation or human action |

`CONTINUE_TASK` must identify one `task_id`.

`IDLE` is distinct from `GLOBAL_STOP`.

No ambiguous prose-only continuation decision is lawful.

Autopilot process-exit on `STOP` must not be copied as loop-core
`GLOBAL_STOP`.

### 11.2 Decision object

Minimum fields:

| Field | Required |
| --- | --- |
| `kind` | Always |
| `task_id` | If and only if `kind == CONTINUE_TASK` |
| `reason` | If `kind` is `IDLE` or `GLOBAL_STOP` |
| `decided_at` | Always |
| `evidence_pointer` | Always |

The latest durable decision is authority. Hidden in-memory continuation
is forbidden.

---

## 12. Global stop

### 12.1 Exact `GLOBAL_STOP` conditions

`GLOBAL_STOP` is lawful only for:

1. explicit operator global pause
2. `SAFETY_STOP`
3. loop state corruption / runtime integrity unsafe
4. core-level `AMBIGUOUS_NEXT_ACTION`
5. safety policy requiring global halt

Runtime integrity unsafe includes loop-state corruption, unexpected
mutation of loop-core files, credential-leak path, or lock corruption
that makes deterministic continuation of the loop itself unsafe.

Core-level `AMBIGUOUS_NEXT_ACTION` means the loop cannot deterministically
decide among `CONTINUE_TASK` / `IDLE` / `GLOBAL_STOP`. It does **not**
mean “two eligible tasks exist.” `N` eligible tasks are lawful.

### 12.2 Conditions that must not become `GLOBAL_STOP`

| Condition | Required decision / effect |
| --- | --- |
| No derived-eligible executable task | `IDLE` |
| Task waiting human approval | Continue other work, or `IDLE` if none remains |
| Task waiting external | Continue other work, or `IDLE` if none remains |
| Mission `PAUSED` or `BLOCKED` | That mission’s tasks are ineligible. Other missions may continue |
| MSE `MULTIPLE_ELIGIBLE_MILESTONES` | Engineering successor task waits or stays ineligible. Other tasks may continue |
| Equal-priority contention on one resource | Hold those tasks. Continue unrelated work |

Human approval wait must not cause `GLOBAL_STOP`.

No eligible task must produce `IDLE`, not `STOP`.

Mission-specific pause or block must not stop unrelated missions.

---

## 13. Continue-other-work

This is a primary invariant.

```text
Task A:
  WAITING_HUMAN
  or WAITING_EXTERNAL
  or BLOCKED
  or DEFERRED

must NOT globally stop Task B or Task C
if B or C is independently derived-eligible.
```

Dependents of A remain ineligible only.

The core must continue the highest lawful eligible independent work.

If no independent eligible work remains, the decision is `IDLE`.

Continue-other-work is how JOO Loop Core differs from current Autopilot
process-exit and from MSE `N → STOP`.

---

## 14. Human approval policy

### 14.1 Policy vocabulary

```text
AUTO_ALLOWED
REVIEW_REQUIRED
HUMAN_APPROVAL_REQUIRED
FORBIDDEN
```

Field use:

| Field | Lawful values | Meaning |
| --- | --- | --- |
| `review_policy` | `AUTO_ALLOWED` or `REVIEW_REQUIRED` | Whether an independent `REVIEWER` worker is required |
| `execution_policy` | `AUTO_ALLOWED`, `HUMAN_APPROVAL_REQUIRED`, or `FORBIDDEN` | Whether the task may start/complete autonomously, must wait for a human, or must never run |

`REVIEW_REQUIRED` and `HUMAN_APPROVAL_REQUIRED` are distinct gates. Both
may apply to one task.

`FORBIDDEN` can never enter `RUNNING`.

`REVIEW_REQUIRED` requires an independent reviewer worker. The worker
must not self-approve.

`HUMAN_APPROVAL_REQUIRED` creates a durable `ApprovalRequest` and moves
the task to `WAITING_HUMAN`.

### 14.2 ApprovalRequest

An `ApprovalRequest` must be durable.

Minimum fields:

| Field | Meaning |
| --- | --- |
| `approval_id` | Opaque identity |
| `mission_id` | Owning mission |
| `task_id` | Exact task that needs approval |
| `policy` | The policy that created the request |
| `request_reason` | Why approval is required |
| `fingerprint` | Bound request fingerprint |
| `state` | One approval state below |
| `created_at` | Immutable creation timestamp |
| `updated_at` | Last durable mutation timestamp |

Approval states:

```text
PENDING
APPROVED
REJECTED
EXPIRED
SUPERSEDED
```

Lawful actions: `approve` / `reject` / `expire` / `supersede`.

### 14.3 Approval invariants

Human approval must never be inferred from:

- review success
- model confidence
- previous approval
- plain-text statements

Approval is task-specific.

Approval is not ambient.

Approve-to-continue is **not** `ExecutionAuthorization` for irreversible
actions.

The morning approval queue is a section of the Operator Brief, not a
second authority.

---

## 15. Execution authorization

### 15.1 Execution class

```text
REVERSIBLE_LOCAL
IRREVERSIBLE_EXTERNAL
```

`IRREVERSIBLE_EXTERNAL` requires an explicit `ExecutionAuthorization`.

`REVERSIBLE_LOCAL` does not create remote or market mutation authority.

### 15.2 ExecutionAuthorization record

Minimum fields:

| Field | Meaning |
| --- | --- |
| `authorization_id` | Opaque identity |
| `task_id` | Exact task bound by this authorization |
| `attempt` | Exact attempt number bound by this authorization |
| `execution_fingerprint` | Bound plan / payload fingerprint |
| `single_use` | Must be true |
| `created_at` | Immutable issuance timestamp |
| `state` | `ISSUED`, `CONSUMED`, or `INVALIDATED` |

### 15.3 Issuance and consumption rules

`ExecutionAuthorization` is created only by an explicit authorization
issuance that is distinct from review and distinct from
approve-to-continue.

Successful review does not create it.

Human approve-to-continue does not automatically create it.

Retry, payload change, or fingerprint change invalidates it.

A consumed authorization cannot be reused.

The authorization must be re-verified immediately before execute.

`COMMIT READY` remains Autopilot-owned commit-review eligibility. It is
not universal execute authority.

Do **not** adopt OOB Automation-M3 as frozen law.

Reuse only the safe pattern:

- distinct authorization
- bound fingerprint
- single-use
- re-verify at execute
- review success ≠ execute authority
- remote publication forbidden

Automatic push remains **NOT AUTHORIZED**.

Automatic trading remains **NOT AUTHORIZED**.

This architecture creates no authorized irreversible trading task and no
authorized automatic push task.

---

## 16. Failure model

### 16.1 Waiting reasons

Waiting is not failure.

```text
HUMAN_APPROVAL_REQUIRED
EXTERNAL_DEPENDENCY_WAIT
```

### 16.2 Failure / stop reasons

```text
RETRYABLE_TRANSIENT_FAILURE
NON_RETRYABLE_FAILURE
REVIEW_FAILED
VERIFICATION_FAILED
SAFETY_STOP
AMBIGUOUS_NEXT_ACTION
RESOURCE_UNAVAILABLE
PROCESS_INTERRUPTED
```

`FAILED` is a task state, not a reason.

Every failure or wait must record an exact reason. Prose-only failure is
forbidden.

### 16.3 Retry

Every retry requires:

- an explicit retry class
- `max_attempts`
- preserved evidence from prior attempts
- a new `attempt` number
- no duplicate irreversible execution
- a new `ExecutionAuthorization` if `execution_class` is
  `IRREVERSIBLE_EXTERNAL`

No infinite retry loop.

Backoff, if any, is owned by trigger or adapter. The core does not
implement a scheduler.

`PROCESS_INTERRUPTED` may retry only when the work is reversible and
policy allows.

Observed irreversible mutation must not retry.

---

## 17. Persistence

Freeze file-based persistence.

No database.

Root:

```text
state/LOOP_CORE/
```

Exact layout:

```text
state/LOOP_CORE/missions/<mission_id>/mission.json
state/LOOP_CORE/missions/<mission_id>/tasks/<task_id>.json
state/LOOP_CORE/missions/<mission_id>/events.jsonl
state/LOOP_CORE/approvals/<approval_id>.json
state/LOOP_CORE/authorizations/<authorization_id>.json
state/LOOP_CORE/recovery.json
state/LOOP_CORE/briefs/<window_id>.md
```

Atomic JSON replacement.

Append-only `events.jsonl`.

No hidden in-memory-only authority.

State must survive:

- terminal close
- process crash
- reboot
- overnight execution

Do not mix with selector state namespaces:

- `state/JOO/`
- `state/JOO_AUTOMATION/`

The loop-core store must not share files, locks, or recovery markers
with Milestone Selection Engine or Autopilot namespaced state.

This document does **not** create `state/LOOP_CORE/`. Persistence is a
later implementation concern and is not authorized here.

Must preserve at minimum:

- missions
- tasks
- dependencies
- task state
- result pointers
- approval queue
- execution authorizations
- attempts
- timestamps
- recovery marker
- last deterministic continuation decision

Mission and task identities are caller-supplied opaque strings.
Operational attempt numbers may be generated.

State stores pointers, ids, and hashes. It must not store raw secrets,
raw Keychain values, or raw holdings.

---

## 18. Recovery

On startup the core must:

1. inspect the recovery marker;
2. inspect persisted `RUNNING` tasks;
3. never infer work completion.

| Interruption | Resume |
| --- | --- |
| Process crash, terminal close, or reboot | Restore last persisted states. Do not invent progress |
| Interrupted reversible `RUNNING` with no mutation evidence | `PROCESS_INTERRUPTED` → retry only if policy allows; otherwise `FAILED` |
| Interrupted irreversible after observed mutation | `BLOCKED` or `SAFETY_STOP`. No retry. No auto-repair |
| Interrupted irreversible before mutation | Fail without consuming authorization |
| Interrupted review | Restore `WAITING_REVIEW`. Do not re-execute the worker |
| Interrupted verification | Restore `WAITING_VERIFICATION` |
| Interrupted human approval | Restore `WAITING_HUMAN`. The `ApprovalRequest` remains |
| Interrupted Autopilot / git path | Engineering Adapter defers to existing Autopilot / `joo_auto` fail-closed rules |

Loop Core must not `git clean`, `git reset`, or force.

No inferred repair.

Evidence of each attempt is immutable.

Engineering git state remains owned by existing Autopilot / `joo_auto`
fail-closed rules.

---

## 19. Concurrency

Conservative first policy:

- one mutation lane per `protected_resource_id`
- first implementation slice may serialize **all** work
- later independent read/research concurrency may be added only when
  those tasks cannot conflict
- repository mutation remains existing Engineering Adapter lock-owned
- trading execution lane exists conceptually but contains **no
  authorized execution tasks**
- no simultaneous conflicting mutations

24/7 does not mean uncontrolled parallelism.

Loop Core must not bypass Autopilot / `joo_auto` locks.

Unrelated tasks on different protected resources may be selected in
later slices. They must not be claimed as concurrent mutations in the
first slice if that slice serializes all work.

---

## 20. Trigger ingress

Freeze only the trigger event contract.

Trigger is ingress data. It is not a scheduler product and not a kernel
implementation.

### 20.1 Classes

```text
SCHEDULED
EVENT
CONDITION
```

### 20.2 Required fields

| Field | Meaning |
| --- | --- |
| `trigger_id` | Opaque identity |
| `trigger_class` | `SCHEDULED`, `EVENT`, or `CONDITION` |
| `source_adapter_id` | Adapter that emitted the trigger |
| `occurred_at` | When the source says the trigger occurred |
| `opaque_payload` | Domain data. Core must never interpret it |

No cron.

No launchd.

No market hours.

No daemon.

No scheduler implementation.

An external runtime may later feed trigger events. First slices, if
later authorized, remain operator- or process-invoked.

Core knows trigger presence and task timing only as recorded data.
Market semantics belong to the Trading Adapter.

---

## 21. Worker abstraction

Freeze the minimal worker invocation contract.

Core semantics use:

| Field | Meaning |
| --- | --- |
| `capability_id` | What kind of worker is required |
| `input_contract_id` | Declared input contract |
| `output_contract_id` | Declared output contract |
| `timeout` | Invocation bound |
| `independence_role` | Role used for independence checks |

`independence_role` values:

```text
WORKER
REVIEWER
VERIFIER
TOOL
```

Do not store GPT, Claude, Grok, Gemini, or any other model name in
Mission or Task semantics.

Model/tool binding is runtime or adapter configuration behind
`capability_id`.

Reviewer independence:

```text
if review_policy == REVIEW_REQUIRED:
    reviewer invocation identity != worker invocation identity
```

Cost or priority class, if present, is optional adapter metadata. It is
not a ranking engine.

This is not a multi-agent framework.

---

## 22. Domain adapter

Freeze the minimal domain adapter data boundary.

At minimum:

| Field | Meaning |
| --- | --- |
| `domain_id` | Adapter identity |
| `mission_type` | Adapter-declared mission class |
| `task_type` | Adapter-declared task class |
| `opaque_payload` | Domain data |
| `required_capabilities` | Capabilities the core must dispatch |
| `review_policy` | Review gate |
| `execution_policy` | Execution / human gate |
| `execution_class` | Reversible vs irreversible |
| `protected_resource_id` | Mutation lane, if any |
| `trigger_policy` | Adapter-owned trigger interpretation |

Adapter owns:

- domain interpretation
- candidate emission
- domain evidence interpretation
- domain result interpretation
- domain report transformation

Core must not parse domain payload.

Brand, Legal, Manufacturing, Marketing, Finance, and other future
domains must be addable by new adapters without redesigning this core.

This document does **not** implement any adapter.

---

## 23. Engineering Adapter

First proof domain.

Freeze role only. Do not implement the adapter yet.

The Engineering Adapter consumes existing:

- Milestone Selection Engine
- Supervisor
- Autopilot
- `joo_auto`
- review artifacts
- git safety
- tests
- architecture / implementation / commit review pipeline

It does not replace them.

Engineering flow may include:

```text
architecture
→ review
→ implementation boundary
→ implementation
→ implementation review
→ commit review
→ gated commit/tag
→ post-commit verification
→ next candidate
```

MSE is asked only at a true inter-milestone point.

Autopilot remains the sole engineering git executor.

If one engineering task enters `WAITING_HUMAN`, other unrelated core
tasks continue.

No auto-push.

Do not invent a second git executor.

MSE `0/1/N` remains unchanged and remains an engineering successor
authority only.

---

## 24. Trading Adapter

Second proof domain.

Freeze role only. Do not implement the adapter yet.

The Trading Adapter consumes domain machinery:

- Provider
- `broker_fact`
- FactStore / Snapshot later as authorized
- IRO
- committees
- CIO

It owns market schedule semantics and trading trigger policy.

It may transform Operator Brief into Morning CIO.

No order execution.

No automatic trading.

Core knows trigger and task timing only.

Trading Adapter owns market semantics.

The conceptual trading execution lane contains no authorized execution
tasks.

---

## 25. Operator Brief

Freeze a generic Operator Brief.

At minimum:

| Field | Meaning |
| --- | --- |
| `window_start` | Brief window start |
| `window_end` | Brief window end |
| `active_missions` | Missions in `ACTIVE` |
| `completed_tasks` | Tasks completed in the window |
| `failed_tasks` | Tasks failed in the window |
| `waiting_human` | Current human-approval queue |
| `waiting_external` | Current external waits |
| `blocked_tasks` | Current blocked tasks |
| `deferred_tasks` | Current deferred tasks |
| `important_evidence_pointer_changes` | Pointer / id / hash changes only |
| `system_health` | `RUNNING`, `IDLE`, or `GLOBAL_STOP` |
| `next_planned_actions` | Highest lawful next actions, if any |

`system_health` values:

```text
RUNNING
IDLE
GLOBAL_STOP
```

No raw secrets.

No raw holdings.

No domain-specific mandatory fields.

Engineering Adapter may render:

```text
Overnight Engineering Report
```

Trading Adapter may render:

```text
Morning CIO Report
```

Core emits only the generic brief. Adapter renders are transforms, not
second continuation authorities.

---

## 26. Morning / 24/7 target

Eventual target, recorded so later runtime work has a lawful freeze to
implement against:

- no terminal babysitting
- persistent operation
- long idle without busy-loop
- trigger-driven resume
- safe pause
- recovery after reboot or crash
- operator report

Explicitly freeze:

```text
DAEMON:
NOT IN THIS ARCHITECTURE IMPLEMENTATION SLICE

SCHEDULER:
NOT IN THIS ARCHITECTURE IMPLEMENTATION SLICE
```

24/7 runtime supervision is later.

This architecture must make `IDLE` sleep-capable in contract. It must
not implement a daemon.

Roadmap Stage 6 remains later product scope.

---

## 27. Engineering showcase target

Record the first future autonomy proof. Do not implement it now.

One human Mission submission.

Then, without manual copy/paste:

```text
candidate
→ architecture
→ review
→ implementation boundary
→ implementation
→ independent review
→ verification
→ approval queue if required
→ continue unrelated work
→ commit/tag only if authorized
→ post-commit verification
→ next candidate
→ Operator Brief
```

Manual nano, prompt copy/paste, and review-command repetition must
eventually reach zero for the standard path.

This is a future proof target, not an implementation authorization.

No auto-push.

---

## 28. Trading showcase target

Record the second future autonomy proof. Do not implement it now.

```text
US-session triggers
→ evidence / research tasks
→ verification
→ Korea pre-open transformation
→ before 08:00 KST Morning CIO
```

No automatic order execution.

Core knows trigger and task timing only.

Trading Adapter owns market semantics.

---

## 29. Autonomy metrics

Freeze observability requirements, not an optimization engine.

Track at minimum:

| Metric | Meaning |
| --- | --- |
| `human_touches_per_completed_mission` | Human actions required to complete one mission |
| `mission_completion_rate` | Completed missions over submitted missions |
| `recovery_success_rate` | Lawful recoveries over recovery attempts |
| `approval_wait_count` | Tasks currently or historically waiting human |
| `blocked_task_count` | Tasks currently or historically blocked |
| `invalid_autonomous_mutation_count` | Mutations that occurred without lawful authority |
| `resume_success_count` | Lawful resumes after idle, crash, or reboot |
| `duplicate_irreversible_execution_count` | Repeated irreversible executes of the same bound work |
| `operator_brief_deadline_success` | Briefs produced inside the required window |

Critical safety targets:

```text
invalid_autonomous_mutation_count = 0
duplicate_irreversible_execution_count = 0
```

Manual copy/paste should trend toward `0`.

These metrics do not authorize a ranking engine, a planner, or automatic
remediation.

---

## 30. Security

Core must never:

- persist raw credentials
- print secrets
- copy Keychain values into loop state
- infer authority from model output
- bypass execution policy
- auto-trade
- auto-push
- blindly retry irreversible operations

Use existing Keychain / credential contracts where a domain needs them.

State stores pointers, ids, and hashes only where possible.

Human silence is never authorization.

Model confidence is never authorization.

A Trading Adapter’s existence is never trading authority.

An Engineering Adapter’s existence is never push authority.

---

## 31. Non-responsibilities

Explicitly exclude:

- scheduler implementation
- daemon implementation
- generic LLM platform
- planner AI framework
- multi-agent framework
- database platform
- market strategy
- portfolio allocation
- order execution
- legal reasoning
- brand reasoning
- design generation
- git executor replacement
- Milestone Selection replacement
- Supervisor replacement
- Autopilot replacement
- KB OpenAPI ownership
- CIO decision ownership
- Architecture State Resolver
- any manufactured numbered milestone
- adoption of OOB product architecture as law
- adoption of OOB Automation-M3 as law

IRO remains the investment-research operational plane.

Development Automation remains the engineering-build plane.

Neither is the loop core.

---

## 32. Implementation slicing

Freeze future order only.

Do not authorize any slice in this document.

| Slice | Contents |
| --- | --- |
| A | Core models, validation, state store, derived eligibility, `CONTINUE_TASK` / `IDLE` / `GLOBAL_STOP` |
| B | Approval queue and continue-other-work |
| C | Recovery markers, retry policy, and `ExecutionAuthorization` |
| D | Engineering Adapter |
| E | Operator Brief |
| F | Trigger ingress |
| G | Trading Adapter research/report only |

Do not start at Trading.

Do not build a daemon, planner engine, or multi-agent framework in any
of these slices.

Do not implement any adapter in this document.

A later implementation authorization is required before Slice A may
begin.

---

## 33. Invariants

The following are load-bearing and must survive independent review
unchanged in meaning:

1. JOO Loop Core is the one loop-level continuation authority.
2. Decision kinds are exactly `CONTINUE_TASK`, `IDLE`, and
   `GLOBAL_STOP`.
3. `IDLE` is distinct from `GLOBAL_STOP`.
4. Continue-other-work is required: a waiting, blocked, or deferred task
   must not stop independently eligible work.
5. `ELIGIBLE` is derived only.
6. `N` eligible tasks is lawful.
7. MSE `0/1/N` is unchanged and remains engineering successor
   cardinality only.
8. Autopilot remains inside the Engineering Adapter.
9. Supervisor remains intra-engineering `RUN_REVIEW` / `COMMIT` /
   `STOP`.
10. Core never interprets `opaque_payload`.
11. Required review and required verifier cannot be skipped.
12. Reviewer invocation identity must differ from worker invocation
    identity when `REVIEW_REQUIRED`.
13. Review success is not execute authority.
14. Approve-to-continue is not `ExecutionAuthorization`.
15. Irreversible retry requires a new `ExecutionAuthorization`.
16. Automatic trading is not authorized.
17. Automatic push is not authorized.
18. Persistence is the file store under `state/LOOP_CORE/`.
19. No database, daemon, or scheduler is authorized by this document.
20. Future domains attach through adapters without redesigning the core.

---

## 34. Architecture status

```text
JOO LOOP CORE ARCHITECTURE:
READY FOR INDEPENDENT REVIEW

IMPLEMENTATION:
NOT AUTHORIZED

AUTOPILOT:
NOT RUN

AUTOMATIC TRADING:
NOT AUTHORIZED

AUTOMATIC PUSH:
NOT AUTHORIZED

DAEMON:
NOT AUTHORIZED

SCHEDULER:
NOT AUTHORIZED
```

Next action: Independent Architecture Review.

Do not implement.

Do not run Autopilot.

Do not call live KB.

Do not mutate Keychain.

Do not create runtime state.

Do not invent a numbered milestone.

Do not reopen MSE `0/1/N`.

Do not treat OOB product architecture or OOB Automation-M3 as frozen
law.
