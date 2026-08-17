# Autopilot Repository Target Abstraction Architecture

## Status and identity

- Status: Architecture authored for independent review; freeze only
- Product: JOO — 24/7 AI Investment Command Center
- Plane: **Development infrastructure** — not an investment-domain plane
- Capability: **Autopilot Repository Target Abstraction**
- Owner: **Autopilot Repository Target**
- Milestone ID: **UNRESOLVED**
- This document does **not** invent or assign `Automation-M4`,
  `Autopilot-M1`, `M55+`, or any other manufactured milestone number
- Authorizing review: Autopilot Repository Target Abstraction
  Architecture Review
  (`~/JOO-Automation/results/autopilot_repository_target_abstraction_architecture_review/`)
  — **FINAL DECISION: REPOSITORY TARGET ABSTRACTION ARCHITECTURE READY**
- Production location (later, not created by this document): JOO-Automation
  Autopilot machinery (`bin/` / a small Autopilot module). Not a JOO
  investment package and not an extension of `joo_auto`
- Repository boundary for this document: architecture authoring only; this
  document alone authorizes no production code, test, package scaffold,
  schema module, configuration, run artifact, Supervisor change, review
  launcher change, Autopilot runtime change, or Git history mutation

This document freezes the **minimum safe repository-target abstraction**
required so one Autopilot v5 implementation can later operate on either
`JOO` or `JOO_AUTOMATION` without weakening existing Autopilot v5 safety
invariants.

It answers only:

> How does Autopilot select, validate, and freeze exactly one allowlisted
> mutation repository for one run?

It does **not** answer:

> What milestone should be built next, or may Autopilot push?

Implementation is **not** authorized.

Milestone Selection Engine integration is **not** authorized.

PF-M5 is **not** authorized.

This document does **not** make current Autopilot repository-aware merely
by being written. Until a later implementation is separately authorized
and completed, `joo autopilot` must not be used to target
`JOO_AUTOMATION`.

---

## 1. Purpose

Autopilot v5 is a host/target loop. The host is always JOO-Automation.
The mutation target is currently hardcoded to JOO.

The purpose of this architecture is to replace that hidden JOO constant
with an explicit, fail-closed, immutable target context so that one
parameterized Autopilot engine can later execute the same proven loop
against either allowlisted repository:

```text
joo autopilot --repo JOO
joo autopilot --repo JOO_AUTOMATION
```

The abstraction must preserve every existing Autopilot v5 safety
invariant:

- dirty-tree fail-closed
- exact-path staging only
- single-consumption `COMMIT READY`
- named OOB preservation
- deletion approval
- empty index before staging
- tag collision prevention when a tag is authorized
- post-commit full Supervisor
- no `git add .` / `git add -A` / glob / directory staging
- no history rewrite / force-push

The abstraction must also remove two JOO-era defaults that become unsafe
once JOO-Automation is a legal mutation target:

- always create a tag
- always push branch and tag to `origin`

Target capability is not tag authority and is not push authority.

---

## 2. Current Problem

### 2.1 Verified checkpoint at authoring

This architecture is authored only after independent re-verification.
Material state matches the authorizing review.

**JOO-Automation** (`/Users/takesimple/JOO-Automation`)

| Check | Value |
| --- | --- |
| Path | `/Users/takesimple/JOO-Automation` |
| Branch | `main` |
| HEAD | `0c44ec4d5f7e76b692e2246b58b28e54bc7fe567` |
| Latest commit | Add Milestone Selection Engine first slice |
| Staged set | empty |
| Tracked dirty set | empty |
| Exact tag at HEAD | none |
| Remote | `origin` present; `main` is ahead 1 and unpushed |

The Milestone Selection Engine first slice is committed. Untracked host
machinery is present (`bin/`, extra `prompts/`, `state/`, `backups/`,
`tests/test_autopilot_v5_safe_fastpath.py`). That is expected operational
tree, not a dirty tracked tree. This architecture does **not** bless
those untracked files as named OOB.

**JOO** (`/Users/takesimple/Projects/JOO`)

| Check | Value |
| --- | --- |
| Path | `/Users/takesimple/Projects/JOO` |
| Branch | `feature/stage2-provider-runtime` |
| HEAD | `60a309fb534bd1118dbfbc6e68c98aec3483010a` |
| Latest commit | Add Milestone Selection Engine architecture |
| Exact tag | `v7.13-stage5-milestone-selection-engine-architecture` |
| Staged set | empty |
| Tracked dirty set | empty |

`git describe --exact-match HEAD` without `--tags` fails because the tag
is lightweight. `git tag --points-at HEAD` and Autopilot's
`exact_tag_at_head()` resolve the expected tag. This is not a material
mismatch.

Intentionally untracked JOO OOB files exist and remain
**non-authoritative**:

- `docs/JOO_PRODUCT_ARCHITECTURE.md`
- `docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md`

This architecture must not consume, modify, stage, or treat either OOB
file as target policy, successor identity, or commit authority.

### 2.2 Hardcoded JOO world

Current Autopilot v5 pretends host and target are one JOO-shaped world.

| Layer | Current binding | Defect |
| --- | --- | --- |
| `bin/joo_autopilot.py` | `REPO = HOME / "Projects" / "JOO"` | No `--repo`; implicit JOO only |
| `bin/joo_autopilot.py` | required branch `feature/stage2-provider-runtime` | Global JOO branch |
| `bin/autopilot_runtime.py` | `KNOWN_OOB_PATHS` = the two JOO files | JOO OOB leaks to any later target |
| `bin/autopilot_runtime.py` | `FROZEN_AUTHORITY_PATHS` = JOO Constitution and roadmap | JOO authority leaks to any later target |
| `bin/autopilot_runtime.py` | default branch `feature/stage2-provider-runtime` | COMMIT READY matching is JOO-shaped |
| `bin/autopilot_runtime.py` | `directive.tag` required; always `tag` then `push origin` | Tag/push are not authorization decisions |
| `bin/joo` | `joo autopilot` execs the Python file; `joo status` `cd`s to JOO | No target resolver |
| Supervisor prompt | `REPOSITORY ~/Projects/JOO`; COMMIT branch hardcoded | Supervisor infers JOO from prose |
| `scripts/run_grok.sh` | `REPOSITORY="/Users/takesimple/Projects/JOO"` then `cd` | Review launcher independently chooses JOO |
| Host state | `state/*.json`, `state/autopilot.log` | Shared, JOO-oriented, not namespaced |
| Host results | `results/<review_name>/` | Global by review name |
| Consumed ledger | `state/consumed_commit_ready.json` | Three JOO entries; no `repository_id` |
| COMMIT READY search | `results/*/*_attempt_*.md` | Global search across all reviews |

`joo_auto` is a different product. Its frozen dual-root law
(`automation_root` ≠ `joo_repository`) is not reopened here. Autopilot v5
is the untracked Supervisor loop in `bin/`. Only Autopilot v5 may later
target JOO-Automation **as Autopilot's mutation repository**.

### 2.3 Why replacing `REPO` alone is unsafe

If only the Python `REPO` constant changed, a JOO-Automation run would
still:

- launch Supervisor and reviews against JOO
- apply JOO branch and JOO OOB rules
- read and write the JOO checkpoint and JOO consumed ledger
- match a JOO `COMMIT READY` by tag or message
- create a JOO-style tag and push `origin` even when unauthorized
- treat Autopilot's own `state/` writes as target dirt when host equals
  target

Current Autopilot v5 **cannot** operate on `~/JOO-Automation` as target.

### 2.4 Required replacement shape

```text
joo autopilot --repo <ID>
  → resolve allowlisted identity
  → validate target
  → freeze AutopilotExecutionContext
  → Supervisor / review / commit / tag / push all consume that context
```

Review launcher and host state/results must consume the same context.
Otherwise the abstraction is theater.

---

## 3. Owner

The exact owner is:

**Autopilot Repository Target**

This is a new Autopilot-owned component. It is not a numbered milestone
and not a second Autopilot implementation.

It is invoked by the Autopilot entrypoint **before** Supervisor, review,
Grok, staging, commit, tag, or push. It produces one immutable
`AutopilotExecutionContext` for the run.

### 3.1 Owns

- allowlisted repository identities
- repository target registry
- repository-specific branch policy
- repository-specific named OOB policy
- repository-specific frozen-authority policy
- protected host-prefix policy
- construction of immutable `AutopilotExecutionContext`
- target validation before Supervisor / review / git operations
- repository-scoped host state and results paths

### 3.2 Does not own

| Rejected owner or adjacent | Reason |
| --- | --- |
| Autopilot entrypoint | Parser/invoker only. Must not own the registry or validation rules. |
| Autopilot runtime | Consumer of the frozen context. Keeps COMMIT READY, exact-path staging, dirty-tree, and authorized tag/push execution. |
| Supervisor | Intra-milestone `RUN_REVIEW` / `COMMIT` / `STOP` only. Must not choose or switch repository. |
| Milestone Selection Engine | Eligibility cardinality only. Filesystem-free and Autopilot-integration-free. Not this owner. |
| `joo_auto` / Automation-M1 / M2 / M3 | Different product. Dual-root invariant stays. Not this owner. |
| `scripts/run_grok.sh` | Consumer. Must accept the frozen target. Must not remain a second hidden owner. |
| Commit authorization policy | Unused `COMMIT READY` plus explicit COMMIT directive remain Autopilot runtime / commit-review authority. |
| Push authorization policy | Explicit push decision on the unused `COMMIT READY` / COMMIT directive. Target capability ≠ push authority. |
| Investment product architecture | JOO Constitution, PF, IRO, Market, FactStore, allocation. Not a targeting concern. |

One owner per responsibility is preserved.

---

## 4. Supported Target Identities

Callers supply a **logical repository ID only**.

Initial closed allowlist:

| `repository_id` | Registered path | Required branch |
| --- | --- | --- |
| `JOO` | `~/Projects/JOO` | `feature/stage2-provider-runtime` |
| `JOO_AUTOMATION` | `~/JOO-Automation` | `main` |

These are logical identities. They are not filesystem inputs.

### 4.1 Identity invariants

- caller supplies logical repository ID only
- exact built-in `str`
- exact equality
- no trim
- no case folding
- no closest match
- no path input
- no cwd inference
- no nearest git root
- no environment-variable inference
- no fallback to `JOO`

Therefore:

- `"JOO "` ≠ `"JOO"`
- `"joo"` is unknown
- `"JOO-AUTOMATION"` is unknown
- `"JOO_automation"` is unknown

Unknown target must fail closed before Supervisor, review, Grok,
staging, commit, tag, or push.

### 4.2 Closed allowlist

- No third repository until a later architecture expands the allowlist.
- No `--repo /tmp/foo`, `--repo ~/OtherProject`, or `--repo .`.
- Paths come only from the registry.
- Registry paths are resolved from `Path.home()` at validation time.
- The live resolved path must equal the registered path.

Arbitrary path targeting: **NO**.

Cwd target inference: **NO**.

---

## 5. Non-Responsibilities

This architecture does **not** implement or own:

- Milestone Selection Engine integration
- automatic milestone sequencing
- Architecture State Resolver
- PF-M5
- IRO-M3
- IRO-M4
- Automation-M3
- `joo_auto` changes
- investment research
- portfolio decisions
- market data
- KB provider logic
- third repository support
- arbitrary paths
- cwd inference
- environment inference
- automatic push permission
- automatic tag generation
- commit authorization policy
- push authorization policy
- Supervisor decision logic
- roadmap sequencing
- blessing all current untracked Automation operational files as OOB
- committing Autopilot `bin/` itself

This document does not authorize any of the above.

---

## 6. RepositoryTarget

`RepositoryTarget` is an immutable registry record. It is **static
policy**, not a live git observation.

### 6.1 Minimum fields

| Field | Kind | Meaning |
| --- | --- | --- |
| `repository_id` | Static policy | Exact allowlisted logical ID |
| `repository_path` | Static policy | Registry-resolved absolute path |
| `required_branch` | Static policy | Exact required live branch |
| `known_oob_paths` | Static policy | Repository-specific named OOB relative paths |
| `frozen_authority_paths` | Static policy | Repository-specific frozen-authority relative paths |
| `protected_host_prefixes` | Static policy | Host write prefixes excluded from target dirt and staging when host path equals target path |

### 6.2 Initial registry values

**`JOO`**

- `repository_id`: `JOO`
- `repository_path`: `~/Projects/JOO`
- `required_branch`: `feature/stage2-provider-runtime`
- `known_oob_paths`:
  - `docs/JOO_PRODUCT_ARCHITECTURE.md`
  - `docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md`
- `frozen_authority_paths`:
  - `JOO_CONSTITUTION.md`
  - `docs/JOO_PRODUCT_ROADMAP.md`
- `protected_host_prefixes`: empty
  Host writes never land in the JOO working tree.

**`JOO_AUTOMATION`**

- `repository_id`: `JOO_AUTOMATION`
- `repository_path`: `~/JOO-Automation`
- `required_branch`: `main`
- `known_oob_paths`: empty
- `frozen_authority_paths`: empty
- `protected_host_prefixes`:
  - `state/`
  - `results/`

JOO frozen-authority paths must not leak onto `JOO_AUTOMATION`.
`JOO_AUTOMATION` must not inherit JOO Constitution or JOO roadmap as
frozen authority. An empty initial frozen-authority set is lawful. It
does not waive full Supervisor verification.

### 6.3 Fields that must not appear on RepositoryTarget

Do **not** include:

- push authority
- live HEAD
- current tag
- current `COMMIT READY`
- caller-selected remote
- business priority
- dirty set / porcelain
- remote divergence
- consumed-ledger contents

Those are runtime facts or separate authorization decisions.

`remote_name` is not a registry field. If a valid commit authorization
later says push, Autopilot may use existing `origin` only.

### 6.4 Static policy versus runtime fact

| Concern | Lives on | Why |
| --- | --- | --- |
| Allowlisted ID, path, branch, OOB, frozen authority, protected prefixes | `RepositoryTarget` | Policy for any run of that ID |
| Live HEAD, exact tag, porcelain, staged set, OOB existence hashes | `baseline_observation` | Per-run fact captured after validation |
| Namespaced state/results directories | `AutopilotExecutionContext` | Derived from ID + host root for this run |
| Tag decision / push decision | unused `COMMIT READY` + COMMIT directive | Authorization, not target capability |

`repository_path` is policy. Validation compares the live resolved path
to that registered path. The target record is not updated from live git
state.

---

## 7. AutopilotExecutionContext

`AutopilotExecutionContext` is immutable for the entire Autopilot
invocation.

### 7.1 Minimum fields

| Field | Meaning |
| --- | --- |
| `target` | Immutable `RepositoryTarget` |
| `automation_root` | Always `~/JOO-Automation` (host) |
| `state_dir` | Host path namespaced by `repository_id` |
| `results_dir` | Host path namespaced by `repository_id` |
| `baseline_observation` | Captured after validation, before Supervisor |

### 7.2 Construction

Context is constructed only after the validation order in §10 succeeds.
No Supervisor, review, Grok, or git mutation may occur before the
context exists.

### 7.3 Immutability

- Target is immutable for the entire run.
- No Supervisor action may switch repository.
- No review result may switch repository.
- Switching `JOO` ↔ `JOO_AUTOMATION` requires a new Autopilot
  invocation.
- All actions in one run remain bound to this context and its baseline
  observation.

There is one Autopilot engine. There is no `JOOAutopilot` and no
`JOOAutomationAutopilot`.

---

## 8. Host vs Target

### 8.1 Frozen dual role

| Role | Path | Mutable by Autopilot? |
| --- | --- | --- |
| Automation host | `~/JOO-Automation` | writes namespaced `state/` and `results/`; may write host `prompts/` |
| Target repository | `JOO` or `JOO_AUTOMATION` | safety checks, observation, Supervisor cwd, review cwd, stage / commit / authorized tag / authorized push |

- Host is always JOO-Automation.
- Target is exactly one allowlisted identity per run.

### 8.2 Equality cases

When target = `JOO`:

- host ≠ target
- current proven shape is preserved

When target = `JOO_AUTOMATION`:

- host path == target path
- this special equality is allowed **only** because
  `JOO_AUTOMATION` is an explicit allowlisted target

This equality does **not** weaken the frozen dual-root architecture of
`joo_auto` / Automation-M2. `joo_auto` continues to require
`automation_root` ≠ `joo_repository`. This architecture concerns
Autopilot v5 only.

### 8.3 Consequence of host == target

Autopilot host writes must not destabilize target safety.

- Autopilot state writes must not create false target dirt.
- Autopilot state writes must not become stage candidates.
- Autopilot must not invalidate its own `JOO_AUTOMATION` observation by
  writing host state.
- Protected host prefixes are the mechanism. They are not named OOB.

---

## 9. CLI Contract

### 9.1 Future explicit syntax

```text
joo autopilot --repo JOO
joo autopilot --repo JOO_AUTOMATION
```

The flag is exactly `--repo`.
The value is exactly one allowlisted logical ID.

### 9.2 Missing flag

```text
joo autopilot
```

without `--repo` **fails closed**.

Do not preserve an implicit default target.
Do not infer `JOO` from legacy behavior.
Existing JOO flow is preserved only by the explicit identity
`joo autopilot --repo JOO`.

That is a one-flag compatibility tax, not a redesign of
Supervisor → review → `COMMIT READY` → exact-path commit.

### 9.3 Frozen negatives

- Current shell directory does not select the target.
- `cd ~/JOO-Automation && joo autopilot --repo JOO` still targets JOO.
- `cd ~/Projects/JOO && joo autopilot --repo JOO_AUTOMATION` still
  targets JOO-Automation.
- `cd ~/JOO-Automation && joo autopilot` is not `JOO_AUTOMATION`.
  It is a missing-flag failure.
- No nearest-git-root inference.
- No `JOO_REPO` / environment guess.
- No positional filesystem path.
- No `--repo` value other than the two allowlisted IDs.

### 9.4 Other Autopilot CLI consumers

`joo status` currently `cd`s to JOO and reads un-namespaced
`state/autopilot.log`. A later implementation may keep a read-only
status helper. It must consume the same resolver. It must not invent a
second targeting rule. Status without an explicit `--repo` must fail
closed or remain a separately documented JOO-only helper until it is
converted. It must not silently report the wrong repository.

---

## 10. Target Validation

Deterministic fail-closed order **before** any Supervisor, review, Grok,
or git action:

1. `--repo` present
2. exact repository ID type (`str`; exact bytes; no coercion)
3. ID allowlisted (`JOO` or `JOO_AUTOMATION` only)
4. registry path exists
5. path is a git working tree
6. resolved path equals registered path
   (no symlink escape to a third tree)
7. live branch == `required_branch`
8. index empty
9. repository-specific policy loads
   (named OOB, frozen authority, protected host prefixes)
10. state/results namespace bound to this `repository_id`
11. baseline observation captured

No Supervisor call before these pass.

Unknown ID: STOP immediately. No fallback to `JOO`. No closest match.

Namespace bind in step 10 must occur **before** any Autopilot host write
for the run, including log creation. After bind, all Autopilot host
writes for that run go only into the bound namespace.

Baseline observation in step 11 is captured after namespace bind so that
host writes cannot race the first fingerprint. When host == target,
protected prefixes are already excluded from target dirt.

---

## 11. Branch Policy

Global branch assumptions are removed.

| Target | Required branch |
| --- | --- |
| `JOO` | `feature/stage2-provider-runtime` |
| `JOO_AUTOMATION` | `main` |

Wrong branch: STOP before Supervisor, review, Grok, staging, commit,
tag, or push.

Commit preflight continues to require:

```text
directive.branch == live branch == target.required_branch
```

`directive.branch` is required. There is no default branch.

Current runtime default
`directive.get("branch", "feature/stage2-provider-runtime")` is a JOO
leak and must not survive implementation.

Current COMMIT READY matcher that special-cases the string
`feature/stage2-provider-runtime` is a JOO leak and must not survive
implementation. Matching uses the frozen target's required branch.

---

## 12. OOB Policy

Two mechanisms, not one:

1. **Exact-path staging** (frozen, primary). A `COMMIT READY` may never
   cause unrelated operational files to be staged.
2. **Repository-specific named OOB** (observation + leak detector).

### 12.1 Initial named OOB

| Target | Named OOB set |
| --- | --- |
| `JOO` | `docs/JOO_PRODUCT_ARCHITECTURE.md`; `docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md` |
| `JOO_AUTOMATION` | empty |

Do **not** bless all current untracked JOO-Automation operational files
as OOB. `bin/`, extra prompts, `backups/`, and
`tests/test_autopilot_v5_safe_fastpath.py` may later be intended commit
subjects. Their protection is exact-path staging, not a blanket OOB
blessing.

### 12.2 Inheritance

- `JOO_AUTOMATION` does not inherit JOO OOB.
- `JOO` does not inherit Automation operational files as OOB.
- Untracked files not in the exact directive remain preserved, as today.

### 12.3 Named OOB versus protected host prefixes

Named OOB is a target-policy set of specific relative files that
Autopilot observes and refuses to stage.

Protected host prefixes are host write surfaces. They are not named OOB.
They must not be classified as general OOB.

---

## 13. Protected Host Prefixes

### 13.1 When they apply

`protected_host_prefixes` are consulted only when host path equals
target path. Today that is only `JOO_AUTOMATION`.

When host ≠ target (`JOO`), host writes cannot appear in target
porcelain. The JOO prefix set is empty.

### 13.2 Required prefixes for JOO_AUTOMATION

Freeze at minimum:

- `state/`

Also freeze:

- `results/`

even though `results/` is currently gitignored.

### 13.3 Why results/ is also protected

`~/JOO-Automation/.gitignore` currently ignores `results/` and `runs/`.
Gitignore is a convenience, not a safety invariant.

Autopilot-invoked reviews write results during the run. If `.gitignore`
is later changed, if a file is force-added, or if porcelain is inspected
without ignore rules, those writes must still:

- never become automatic stage candidates
- never classify as unexpected target dirt
- never invalidate the frozen target fingerprint
- never mix with named OOB

Therefore `results/` receives explicit protected-host treatment when
host == target.

`runs/` is gitignored and is `joo_auto` write surface, not Autopilot
v5's write surface. This architecture does not bless `runs/` as Autopilot
OOB and does not add it as an Autopilot protected prefix unless a later
architecture makes Autopilot write there.

### 13.4 Rules

Protected host prefixes:

- are excluded from unexpected tracked dirt
- are excluded from `repo_fingerprint` target dirt
- are never auto-staged
- are never legal exact-path directive entries in the first
  implementation slice
- are not named OOB
- do not waive exact-path staging for any other path

### 13.5 Self-invalidation prohibition

When target = `JOO_AUTOMATION`, Autopilot must not invalidate its own
observation by writing state or results.

Required sequence:

1. bind `state/JOO_AUTOMATION/` and `results/JOO_AUTOMATION/`
2. perform all Autopilot host writes only inside those namespaces
3. capture baseline observation with protected prefixes excluded
4. subsequent namespaced host writes must not change the target
   fingerprint

Writing `state/autopilot.log` or any other un-namespaced host file
during a `JOO_AUTOMATION` run is forbidden.

---

## 14. State Namespacing

State namespacing is **required**.

### 14.1 Required conceptual layout

Under the host (`~/JOO-Automation`):

```text
state/JOO/
state/JOO_AUTOMATION/
```

Each namespace owns at minimum:

- `autopilot.log`
- `supervisor_checkpoint.json`
- `supervisor_fastpath_context.json`
- `next_action.json`
- `consumed_commit_ready.json`

Separate logs are required. A shared log is not the first-slice design.
If a later implementation adds a shared diagnostic stream, every line
must still prefix `repository_id`, and the authoritative per-target log
remains the namespaced file.

### 14.2 Legacy JOO files

Existing:

```text
state/autopilot.log
state/supervisor_checkpoint.json
state/next_action.json
state/consumed_commit_ready.json
```

belong only to `JOO`.

They must **never** be visible to `JOO_AUTOMATION`.

Current contents confirm the leak risk:

- checkpoint observation path is `/Users/takesimple/Projects/JOO`
- `next_action.json` is a JOO STOP after IRO-M2
- consumed ledger has three JOO entries and no `repository_id`

### 14.3 Compatibility semantics

This document does **not** implement migration.

Architecture-level bind:

1. Long-term layout is fully namespaced.
2. First implementation must treat current un-namespaced `state/*.json`
   and `state/autopilot.log` as the **legacy JOO alias**.
3. For target `JOO` only, resolution is:
   - preferred: `state/JOO/<file>`
   - if preferred is absent: `state/<file>`
4. For target `JOO_AUTOMATION`, un-namespaced `state/*` is invisible.
   Missing namespaced files mean empty/new Automation state, not a
   fallback to JOO files.
5. A later authorized one-time physical move may copy JOO alias files
   into `state/JOO/`. The move is JOO-only, one-way, and must not copy
   any JOO file into `state/JOO_AUTOMATION/`.
6. After a physical move, the alias may remain read-only for one
   compatibility window or be removed by a later authorized slice.
7. Never merge ledgers.
8. Never let `JOO_AUTOMATION` read, write, or consume legacy
   un-namespaced state.

### 14.4 Fastpath and checkpoint isolation

A `JOO` checkpoint, fastpath context, or `next_action` must not be
loaded for `JOO_AUTOMATION`, and the reverse.

Repository-scoped checkpoint identity must include `repository_id`.
Fingerprint comparison is never cross-repository.

---

## 15. Results Namespacing

### 15.1 Required conceptual layout

```text
results/JOO/<review_name>/
results/JOO_AUTOMATION/<review_name>/
```

Same review name in different repositories creates independent
authority.

A JOO result must never be consumable as `JOO_AUTOMATION` authority.
A `JOO_AUTOMATION` result must never be consumable as JOO authority.

### 15.2 Legacy JOO results

Existing:

```text
results/<review_name>/
```

belongs only to `JOO`.

Compatibility bind, analogous to state:

1. Preferred JOO result path: `results/JOO/<review_name>/`
2. If that directory is absent, target `JOO` may read the legacy
   `results/<review_name>/` path as JOO-only evidence.
3. `JOO_AUTOMATION` never searches or writes the un-namespaced tree.
4. New Autopilot-invoked reviews must write only into
   `results/<repository_id>/<review_name>/`.
5. A later authorized physical move may relocate legacy JOO results
   under `results/JOO/`. It must not copy them under
   `results/JOO_AUTOMATION/`.

### 15.3 Review-name identity

Review-result identity in Supervisor checkpoint and observation must
include `repository_id`.

`latest.md` is namespace-local. `results/JOO/foo/latest.md` and
`results/JOO_AUTOMATION/foo/latest.md` are two authorities.

Prompt files may remain host-global under `prompts/` in the first
implementation slice. Prompt filename is not authority identity.
Authority is the namespaced result path.

---

## 16. COMMIT READY Namespacing

### 16.1 Separate ledgers

Preferred and required architecture: **separate repository-specific
consumed ledgers**.

```text
state/JOO/consumed_commit_ready.json
state/JOO_AUTOMATION/consumed_commit_ready.json
```

Do not use a global ledger without mandatory repository qualification.
Optional `repository_id` fields on a shared list are not sufficient.

Legacy `state/consumed_commit_ready.json` is the JOO alias only.

### 16.2 Consumption identity

A valid commit authority must bind at minimum:

- `repository_id`
- authority result identity/path inside that repository's results
  namespace
- baseline HEAD
- exact path set
- commit message
- tag decision (`NONE` or exact tag string)
- push decision (`NO` or `YES`)

JOO `COMMIT READY` must never be consumable in `JOO_AUTOMATION`.
`JOO_AUTOMATION` `COMMIT READY` must never be consumable in `JOO`.

### 16.3 Discovery scope

`COMMIT READY` discovery searches only:

```text
results/<repository_id>/…
```

No global search across all repository results.

For target `JOO` during the compatibility window, discovery may also
search legacy `results/<review_name>/` **only after** the namespaced
JOO tree, and **only** for paths that are not already under another
repository namespace. `JOO_AUTOMATION` has no such alias.

Current global glob `results/*/*_attempt_*.md` is unlawful once two
targets exist.

### 16.4 Matching rules that must change

Current matcher leaks JOO assumptions:

- default branch `feature/stage2-provider-runtime`
- special-case presence of that branch string
- required `directive.tag` and `tag in text`
- consumption key = authority path **or** tag, with no repository

Frozen replacement:

- branch match uses `target.required_branch` / `directive.branch`
- tag match uses the tag **decision**
- if tag decision is `NONE`, do not require a tag string and do not
  treat the empty string as a substring match
- if tag decision is an exact string, that exact string must appear in
  the authority and must not already exist on the **target**
- consumption key is namespaced: `repository_id` + authority path +
  baseline HEAD + path set + message + tag decision + push decision
- tag string alone is never a cross-repository consumption key

---

## 17. Supervisor Context

Supervisor remains responsible only for its existing orchestration
action:

- `RUN_REVIEW`
- `COMMIT`
- `STOP`

Repository target selection is **not** Supervisor authority.

### 17.1 Machine-generated target block

Every Supervisor invocation for a run must receive an explicit
machine-generated target block. Supervisor may not infer repository
from prose or cwd.

Minimum block contents:

- `repository_id`
- `repository_path`
- `required_branch`
- known OOB paths
- protected host prefixes
- state namespace
- results namespace
- baseline HEAD
- exact tag
- tracked / staged / dirty facts from the frozen observation

Supervisor must treat that block as authoritative git identity.

### 17.2 What Supervisor must not do

- choose a repository
- switch repository mid-run
- infer JOO from the current Supervisor prompt boilerplate
- write `next_action.json` outside the bound state namespace
- emit a COMMIT branch other than `target.required_branch`
- treat a result from the other repository as unused `COMMIT READY`

### 17.3 COMMIT directive fields that change

Current COMMIT schema requires exact tag and hardcoded JOO branch.

Frozen future COMMIT authorization must carry:

- exact paths
- exact message
- exact branch (`target.required_branch`)
- exact **tag decision** (`NONE` or exact tag string)
- exact **push decision** (`NO` or `YES`)

Supervisor still does not invent those values. They remain bound to an
unused independent `COMMIT READY`.

---

## 18. Review Launcher Context

Current `scripts/run_grok.sh` hardcodes:

```text
REPOSITORY="/Users/takesimple/Projects/JOO"
RESULT_DIR="$HOME/JOO-Automation/results/$PROMPT_NAME"
cd "$REPOSITORY"
```

Autopilot's Python `cwd=REPO` is therefore not the real review target.
That split is a fail-closed defect this architecture must close.

### 18.1 Autopilot-invoked review

Autopilot-invoked review launcher must receive the exact frozen target
path and context.

Frozen invariants:

- the review launcher must not independently choose a repository
- Autopilot cwd and review launcher cwd must refer to the same target
- result output must go to `results/<repository_id>/<review_name>/`
- Autopilot must refuse to call a review launcher that cannot accept a
  target

All reviews in one Autopilot iteration use that same context.

### 18.2 Standalone manual review

Standalone manual `review <name>` may retain its current JOO hardcoded
default for operator habit. That behavior is outside Autopilot's
mutation contract.

This exception does **not** apply to Autopilot-invoked review.
Autopilot-invoked review must be target-explicit.

---

## 19. Cross-Repository Evidence

A review running against one mutation target may read the other
allowlisted repository as **read-only evidence** if needed.

Frozen limits:

- mutation target remains immutable
- review cannot switch commit target
- cross-repo evidence does not grant mutation authority
- cross-repo evidence is not `COMMIT READY`
- cross-repo evidence is not staging authority
- switching `JOO` ↔ `JOO_AUTOMATION` requires a new Autopilot
  invocation

Example: an Autopilot run with `--repo JOO_AUTOMATION` may read JOO
architecture documents as evidence. It may not commit to JOO.

---

## 20. Exact-Path Staging

Preserve all current safety invariants. Repository abstraction changes
only which target root paths are relative to.

Frozen:

- no `git add .`
- no `git add -A`
- no directory-wide staging
- no glob staging
- exact path set only
- index empty before staging
- staged set exactly equals directive paths
- named OOB must not appear in the index
- protected host prefixes must not appear in the index
- unexpected tracked dirt outside the exact path set remains fail
  closed
- deleted tracked files require explicit deletion approval
- no history rewrite
- no force-push
- no `git reset --hard`
- no `git clean` of preserved untracked files

Directive paths are relative to the frozen target root.
Absolute paths remain forbidden.
Parent-directory escape remains forbidden.

---

## 21. Tag Policy

Current Autopilot always requires and creates a tag. That must change.

### 21.1 Tag is an authorization decision

Commit authorization contains an exact tag decision.

The tag decision may be:

- `NONE`
- or an exact tag string

### 21.2 NONE

If the decision is `NONE`:

- no `git tag` command may execute
- Autopilot must not generate a tag automatically
- existing-tag collision checks do not apply
- consumption must not use a tag string as identity

### 21.3 Exact tag

If the decision is an exact tag string:

- that exact string is used
- Autopilot must not rewrite, prefix, or generate a substitute
- the tag must not already exist on the **target**
- existing-tag safety remains

### 21.4 No convention leak

JOO tag convention must not leak into `JOO_AUTOMATION`.

`JOO_AUTOMATION` is currently ahead of `origin/main` by the Milestone
Selection Engine first slice and has no new tag for that slice. An
always-tag Autopilot would invent an unauthorized Automation tag.
That is forbidden.

Target repository capability does not imply tag authority.

---

## 22. Push Policy

Current Autopilot always pushes branch and tag. That must change.

### 22.1 Push is an authorization decision

Push requires exact explicit authorization.

If:

```text
PUSH AUTHORIZED: NO
```

then no `git push` command may execute.

Absent push authorization is treated as `NO`.

### 22.2 Authorized push

If push is authorized (`PUSH AUTHORIZED: YES`):

- remote is exactly `origin`
- no arbitrary remote
- branch push is `origin` + `target.required_branch`
- tag push occurs only when the tag decision is an exact tag string
- `TAG: NONE` plus `PUSH AUTHORIZED: YES` pushes the branch only

### 22.3 Capability versus authority

Target repository capability does not imply push authority.

`JOO_AUTOMATION` currently has `origin` and is ahead 1. That does not
authorize Autopilot to publish the Milestone Selection Engine slice.

Current always-push in `execute_commit` must not survive as a global
default.

---

## 23. Remote Policy

- No caller-supplied remote.
- Push remote, if used, is `origin` only.
- Do not require `origin` for non-push runs.
- Missing `origin` only blocks when push is explicitly authorized.
- Missing `origin` + `PUSH AUTHORIZED: YES` → fail closed.
- Missing `origin` + `PUSH AUTHORIZED: NO` → lawful.
- No implicit remote escalation.

`RepositoryTarget` does not carry a remote field.

---

## 24. Observation / Checkpoint

### 24.1 Baseline observation

Baseline observation is captured after target validation and before
Supervisor.

Minimum contents:

- `repository_id`
- `repository_path`
- branch
- HEAD
- exact tag
- tracked dirty set
- staged set
- untracked / OOB facts
- remote divergence if needed
- authority fingerprints as applicable

All actions in one run remain bound to that observation and context.

### 24.2 Fingerprint isolation

`repo_fingerprint` remains a target-safety fingerprint.

When host == target, porcelain entries under
`protected_host_prefixes` are excluded from that fingerprint and from
unexpected tracked dirt.

Host writes may be recorded separately as host operational facts. They
do not participate in target dirt classification.

### 24.3 Checkpoint

Supervisor checkpoint, fastpath context, and `next_action` are written
only to the bound `state_dir`.

Checkpoint and observation must include `repository_id`.

A JOO fingerprint must not match a `JOO_AUTOMATION` tree, even when
host == target and protected prefixes are excluded.

### 24.4 Mandatory full events

Existing Autopilot v5 mandatory-full events remain:

- commit
- tag
- push
- tracked file mutation
- unexpected dirty path
- test failure
- remediation / conflict / blocked / STOP tokens
- milestone transition
- fingerprint mismatch

Authorized `TAG: NONE` does not create a tag event.
Authorized `PUSH AUTHORIZED: NO` does not create a push event.
A successful commit still forces a full post-commit Supervisor.

---

## 25. Loop Immutability

One parameterized engine:

```text
validate target
→ freeze AutopilotExecutionContext
→ Supervisor
→ Review
→ Commit Review
→ unused COMMIT READY
→ exact-path staging
→ commit
→ tag if authorized
→ push if authorized
→ full post-commit Supervisor
```

Loop rules:

- context is immutable for the run
- target cannot change after freeze
- every review in the run uses the same target and the same results
  namespace
- every git command uses the frozen target root
- Supervisor `next_action` is read and written only in the bound
  `state_dir`
- a review result cannot retarget the run
- a `COMMIT READY` from the other repository cannot enter the loop
- leaving the loop and targeting the other repository requires a new
  process invocation with a new `--repo`

---

## 26. Fail-Closed Conditions

| Condition | Action |
| --- | --- |
| Missing `--repo` | STOP before Supervisor |
| Non-`str` or non-exact repository ID | STOP before Supervisor |
| Unknown / whitespace / case-variant ID | STOP before Supervisor |
| Arbitrary path / cwd / env inference attempted | STOP |
| Registry path missing or not a git working tree | STOP |
| Resolved path ≠ registered path | STOP |
| Wrong branch | STOP before review / stage / commit |
| Index not empty at validation | STOP |
| Repository-specific policy cannot load | STOP |
| Namespace cannot be bound to `repository_id` | STOP |
| Target switch mid-run | STOP |
| Review launcher cannot honor frozen target | STOP before review |
| JOO `COMMIT READY` used on `JOO_AUTOMATION` (or reverse) | STOP |
| Namespaced checkpoint / `next_action` / ledger leak | STOP |
| Same review name used as cross-repo authority | STOP |
| Unexpected tracked dirt outside exact paths | STOP |
| Named OOB staged | STOP |
| Host `state/` or `results/` staged | STOP |
| Directory-wide / glob / unsafe staging | STOP |
| `TAG: NONE` but a tag is created, or a tag is auto-generated | STOP |
| Exact tag already exists on the target | STOP |
| `PUSH AUTHORIZED: NO` but any push runs | STOP |
| Push to a remote other than `origin` | STOP |
| Push authorized but `origin` missing | STOP |
| Host == target and Autopilot operational files staged without exact later authority | STOP |
| Milestone Selection Engine asked to choose a repository | STOP (wrong owner) |
| Implicit fallback to `JOO` | STOP |

The engine must not hide, coerce, or default its way out of any failure
mode.

---

## 27. Backward Compatibility

### 27.1 One engine

The proven JOO Autopilot v5 loop remains one parameterized machine.

Do not duplicate execution code into `JOOAutopilot` and
`JOOAutomationAutopilot`.

Do not implement this inside `joo_auto`.
Do not import JOO investment-domain packages.

### 27.2 `--repo JOO` must preserve

For `joo autopilot --repo JOO`, existing safety guarantees continue:

- JOO OOB preservation
- dirty-tree fail closed
- exact staging
- single-consumption `COMMIT READY`
- deletion approval
- tag collision prevention when a tag is authorized
- post-commit Supervisor
- empty-index contract
- no `git add .` / `git add -A`
- no history rewrite / force-push
- Milestone Selection Engine remains unintegrated
- `joo_auto` dual-root and Automation-M3 non-approval remain untouched

Compatibility tax: operators type `--repo JOO`. That is an explicit
legacy **identity**, not a cwd default.

### 27.3 Current runtime until implementation

Until implementation is separately authorized and completed:

- current Autopilot remains JOO-hardcoded
- `joo autopilot` must not be used to target `JOO_AUTOMATION`
- this document does not change that runtime
- Milestone Selection Engine runtime integration remains deferred

### 27.4 `joo_auto` dual-root

Automation-M1 / M2 dual-root (`automation_root` ≠ `joo_repository`)
remains frozen. Autopilot's allowlisted host == target case for
`JOO_AUTOMATION` is not a `joo_auto` license.

---

## 28. First Implementation Slice

This document authorizes **no** implementation.

If a later board authorizes implementation, the first slice may contain
only:

1. `RepositoryTarget` model and registry for exactly `JOO` and
   `JOO_AUTOMATION`
2. `AutopilotExecutionContext`
3. CLI `--repo` parsing; missing / unknown ID fail closed
4. target validation in the §10 order
5. context propagation through safety checks, observation, Supervisor,
   review launcher, staging, commit, tag, and push
6. repository-specific branch, named OOB, and frozen-authority policy
7. host == target protected `state/` and `results/` prefixes
8. state / results / consumed-ledger namespacing, with current JOO files
   bound only to `JOO`
9. Supervisor machine-generated target block
10. review launcher accepts explicit target and writes namespaced
    results
11. repository-scoped `COMMIT READY` discovery and consumption
12. `TAG: NONE` support
13. `PUSH AUTHORIZED: NO` support
14. tests listed in §29

### 28.1 Later hosting

- Architecture freeze: this tracked JOO document under
  `docs/automation/`
- Implementation, if later authorized: JOO-Automation Autopilot
  machinery
- Do not implement inside a JOO investment-domain package
- Do not extend `joo_auto` M1 / M2 / M3 phase machinery
- Do not invent `Automation-M4` or `Autopilot-M1` as the package
  identity
- Exact module names are deferred to implementation authorization and
  must remain unnumbered descriptive identities

### 28.2 Explicitly out of the first slice

- Milestone Selection Engine integration
- automatic next-milestone continuation
- Architecture State Resolver
- PF-M5
- IRO-M3 / IRO-M4
- Automation-M3
- `joo_auto` changes
- third repositories
- cwd inference
- environment inference
- arbitrary paths
- automatic push permission
- automatic tag generation
- committing Autopilot `bin/` itself
- physical state/results migration, unless separately authorized as a
  JOO-only bind
- prompt-directory namespacing, unless a later proven collision
  requires it

---

## 29. Required Tests

A later implementation must prove at least the following. These tests
are not authored by this document.

| Invariant | Expected |
| --- | --- |
| `JOO` ID resolves exact path | `~/Projects/JOO` |
| `JOO_AUTOMATION` ID resolves exact path | `~/JOO-Automation` |
| missing `--repo` | fail closed before Supervisor |
| unknown ID | fail closed before Supervisor |
| arbitrary path | rejected |
| cwd does not affect target | same ID always same registry path |
| case / whitespace variation | rejected |
| wrong branch | fail closed before Supervisor / review / Grok / git mutation |
| target immutable for run | no mid-run switch |
| JOO authority cannot be consumed in Automation | fail closed |
| Automation authority cannot be consumed in JOO | fail closed |
| state namespace isolation | JOO state invisible to Automation and reverse |
| results namespace isolation | JOO result invisible to Automation and reverse |
| same review name does not mix authority | two independent authorities |
| JOO OOB policy remains | the two named JOO files preserved and unstageable |
| Automation does not inherit JOO OOB | empty Automation named OOB set |
| host state prefix never staged | `state/` rejected as stage candidate |
| host results prefix never staged | `results/` rejected as stage candidate when host == target |
| exact-path staging preserved | no `.` / `-A` / glob / directory |
| `TAG: NONE` | no `git tag` command |
| `PUSH AUTHORIZED: NO` | no `git push` command |
| push YES uses `origin` only | no arbitrary remote |
| missing `origin` + push NO | lawful |
| missing `origin` + push YES | fail closed |
| existing JOO safe-fastpath tests | still pass under `--repo JOO` |
| Automation target flow does not mutate JOO | JOO HEAD / index / worktree unchanged |
| review launcher uses exact target | no silent JOO `cd` |
| Supervisor receives exact target block | no prose / cwd inference |
| no target switch mid-run | fail closed |
| no arbitrary remote | fail closed |
| host state write does not invalidate Automation observation | fingerprint excludes protected prefixes |
| Autopilot does not write un-namespaced `state/` on Automation runs | namespace bind precedes host writes |

Normal, boundary, wrong-type, empty-value, order, and exception
propagation cases required by the repository agent contract apply to
every public entry point.

---

## 30. Frozen Invariants

1. Owner is Autopilot Repository Target.
2. Milestone ID remains `UNRESOLVED`.
3. Exactly two initial logical targets exist: `JOO` and
   `JOO_AUTOMATION`.
4. Callers supply logical repository ID only.
5. Identity comparison is exact built-in `str` equality.
6. No trim, case folding, closest match, path input, cwd inference,
   nearest git root, environment inference, or fallback to `JOO`.
7. Arbitrary path targeting is forbidden.
8. `joo autopilot` without `--repo` fails closed.
9. `RepositoryTarget` is immutable static policy.
10. `AutopilotExecutionContext` is immutable for the run.
11. Host is always `~/JOO-Automation`.
12. Host == target is lawful only for allowlisted `JOO_AUTOMATION`.
13. That equality does not weaken `joo_auto` dual-root.
14. One Autopilot engine; no per-repository Autopilot fork.
15. Target validation precedes Supervisor, review, Grok, and git
    mutation.
16. Wrong branch fails closed before those actions.
17. JOO required branch is `feature/stage2-provider-runtime`.
18. `JOO_AUTOMATION` required branch is `main`.
19. Named OOB is repository-specific.
20. `JOO_AUTOMATION` initial named OOB set is empty.
21. Current untracked Automation operational files are not named OOB.
22. Exact-path staging remains the primary protection.
23. `state/` is a protected host prefix when host == target.
24. `results/` is a protected host prefix when host == target, even if
    gitignored.
25. Protected host prefixes are not general OOB.
26. State namespacing is required:
    `state/JOO/` and `state/JOO_AUTOMATION/`.
27. Results namespacing is required:
    `results/JOO/<review_name>/` and
    `results/JOO_AUTOMATION/<review_name>/`.
28. Legacy un-namespaced `state/*` and `results/<name>/` belong only to
    `JOO`.
29. `JOO_AUTOMATION` must never see those legacy files.
30. Consumed ledgers are repository-specific.
31. `COMMIT READY` discovery searches only the target's results
    namespace.
32. JOO `COMMIT READY` is never consumable in `JOO_AUTOMATION`.
33. `JOO_AUTOMATION` `COMMIT READY` is never consumable in `JOO`.
34. Supervisor receives a machine-generated target block and may not
    infer repository from prose or cwd.
35. Supervisor remains `RUN_REVIEW` / `COMMIT` / `STOP` only.
36. Repository target selection is not Supervisor authority.
37. Autopilot-invoked review launcher must receive the frozen target.
38. Autopilot cwd and review launcher cwd refer to the same target.
39. Cross-repo evidence is read-only and grants no mutation authority.
40. Tag decision is `NONE` or an exact tag string.
41. `NONE` performs no `git tag` and generates no tag.
42. JOO tag convention does not leak into `JOO_AUTOMATION`.
43. Push requires explicit authorization.
44. `PUSH AUTHORIZED: NO` performs no `git push`.
45. Authorized push uses `origin` only.
46. Missing `origin` blocks only when push is authorized.
47. Target capability ≠ tag authority ≠ push authority.
48. No caller-supplied remote.
49. All run actions remain bound to the baseline observation / context.
50. Autopilot must not invalidate a `JOO_AUTOMATION` observation by
    writing its own state.
51. Existing JOO v5 safety guarantees continue for `--repo JOO`.
52. This document does not authorize implementation.
53. This document does not authorize Milestone Selection Engine
    integration.
54. This document does not authorize PF-M5.
55. This document does not authorize commit, tag, or push.
56. Until implementation is completed, `joo autopilot` must not be used
    to target `JOO_AUTOMATION`.
57. The two known JOO OOB documents remain non-authoritative and
    outside this architecture's commit boundary.
58. Development automation must not distort JOO's investment-product
    architecture.

---

## 31. Authorization freeze

| Question | Answer |
| --- | --- |
| Architecture document authored | Yes |
| Independent architecture review | Required next |
| Implementation authorized | **NO** |
| Milestone Selection Engine integration | **NO** |
| PF-M5 authorized | **NO** |
| Automation-M3 authorized | **NO** |
| Architecture State Resolver authorized | **NO** |
| Arbitrary path targeting | **NO** |
| Cwd target inference | **NO** |
| State namespacing | **REQUIRED** |
| Commit / tag / push authorized | **NO** |
| Human decision required now | **NO** |
| Milestone ID | **UNRESOLVED** |
| Owner | **Autopilot Repository Target** |
| Next action | Independent Architecture Review |

Until a later implementation is separately authorized and completed,
current Autopilot remains JOO-hardcoded and must not be used to target
`JOO_AUTOMATION`.
