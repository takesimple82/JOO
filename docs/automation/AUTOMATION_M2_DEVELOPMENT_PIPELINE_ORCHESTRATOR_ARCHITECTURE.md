# Automation-M2 Development Pipeline Orchestrator Architecture

## 1. Status and milestone

- Status: Frozen
- Product: Automation-M2 Development Pipeline Orchestrator
- Milestone: Automation-M2
- Production package: existing `joo_auto`
- Predecessor: accepted Automation-M1 review-only milestone orchestrator
- Repository boundary: automation architecture only; no implementation

This document freezes the first Automation-M2 architecture. It creates no
production code, test, configuration, manifest, prompt, run artifact, or Git
mutation. A separate implementation authorization is required.

## 2. Context

Automation-M1 is an accepted review-only orchestrator in
`/Users/takesimple/JOO-Automation/joo_auto`. It freezes a milestone manifest,
verifies an exact JOO checkpoint, materializes immutable prompt bytes, invokes
Grok review phases one at a time, captures immutable run-local artifacts,
persists state and events, and requires explicit human approval between its
fixed review phases. Its pilot established the accepted run ID, manifest hash,
attempt, prompt, artifact, approval, checkpoint, transition, and lock
conventions.

Automation-M1 deliberately does not execute Codex, parse review decisions,
author architecture or implementation, prepare Git commands, or coordinate
the full development sequence. Actual Stage 5 milestones therefore continue
to use manual handoffs between Grok review, Codex authoring, Codex
implementation, independent reviews, and human Git operations.

Inspection confirms that no equivalent full M2 pipeline exists. Current
`joo_auto` has no Codex adapter, exact `FINAL DECISION` parser, manifest schema
v2, ordered variable phase pipeline, phase-aware change-path guard, or
print-only `git_prepare`. Legacy shell wrappers remain Grok review wrappers
and are not an equivalent state-machine pipeline.

## 3. Problem statement

The development workflow has deterministic coordination work that M1 does not
own: running frozen Codex prompts, enforcing legal phase order, capturing
Codex artifacts, parsing exact review eligibility, stopping on policy or
remediation outcomes, emitting the next command, and rendering exact Git
commands without executing them.

Automating these mechanics is useful only if the system remains unable to
invent architecture, resolve product policy, approve its own work, bypass
failed reviews, or mutate Git. M2 must extend M1 without breaking existing M1
manifests, runs, commands, artifacts, or human authority.

## 4. Architectural decision

Select execution option B: extend the existing Python `joo_auto` package into
an ordered, manifest-driven development pipeline orchestrator.

M2 may:

- execute Grok reviews;
- execute Codex non-interactively with frozen human-authored prompts;
- capture immutable artifacts and hashes;
- parse exact phase-scoped decisions for eligibility;
- enforce checkpoint, index, history, and path boundaries;
- advance only through the frozen state machine and human gates;
- emit deterministic next commands; and
- prepare and print exact Git commands.

M2 must never execute `git add`, `git commit`, `git tag`, `git push`,
`git reset`, `git clean`, branch creation or switching, merge, rebase, amend,
or force operations. Human operators execute all Git mutations outside M2.

M2 does not invent domain contracts, rewrite prompts, resolve product policy,
approve its own output, infer approval from prose, repair repository state, or
bypass a failed, missing, ambiguous, policy, or remediation result.

## 5. Relationship to Automation-M1

Automation-M2 is an extension of Automation-M1 in the same `joo_auto`
package. It is not a separate automation package and not a JOO domain package.

M2 reuses and preserves M1 conventions for:

- configuration and manifest loading;
- timestamp-plus-random-suffix `run_id` generation;
- byte-exact manifest freezing and SHA-256;
- exact read-only repository inspection;
- global exclusive locking;
- prompt containment and immutable materialization;
- bounded Grok resume behavior;
- exclusive attempt artifacts;
- atomic `state.json`, append-only `events.jsonl`, and `summary.md`;
- explicit human approvals with operator and UTC timestamp;
- retry as a new attempt;
- supervised cancellation; and
- side-effect-free status and dry-run behavior.

Existing schema-v1 review-only manifests and existing M1 runs remain
supported. Existing M1 CLI behavior and legacy review wrappers must not be
broken. M2 may version and extend internal schemas, but must route v1 inputs
through compatibility behavior that preserves their fixed review-only
meaning. It must not reinterpret an existing completed artifact under v2
decision rules.

## 6. Responsibility and ownership

M2 owns coordination of one frozen milestone manifest through one ordered
allowlisted pipeline. Its responsibilities are phase validation, tool
invocation, immutable evidence capture, exact decision eligibility, guarded
state transitions, human-gate enforcement, next-command emission, and
print-only Git preparation.

M2 does not own the semantic content of any phase prompt or result. Every
architecture, implementation, review, remediation, and product-policy
statement remains owned by the human-authored prompt and the invoked tool or
human decision. Tool completion is evidence of execution, never approval.

Only one milestone pipeline may be active under the accepted M1 global lock.
Parallel milestone pipelines are outside the first M2 boundary.

## 7. Configuration contract

The M2 configuration has exactly these required fields:

1. `automation_root`: accepted M1 non-blank path string;
2. `joo_repository`: accepted M1 non-blank path string;
3. `review_command`: accepted M1 non-blank command string;
4. `max_grok_resume_attempts`: accepted M1 exact non-negative integer;
5. `codex_command`: non-blank string; and
6. `max_codex_attempts`: exact non-negative integer.

No additional required configuration field belongs to the first M2 boundary.
Boolean values are not accepted as integers for either attempt limit. Config
contains no credentials, prompt content, approval token, Git mutation
authority, danger-bypass flag, or product-policy default.

## 8. Manifest schema v2

A schema-v2 manifest has exactly these required top-level fields:

- `pipeline_schema_version`: exact integer `2`;
- `milestone_id`: non-blank opaque string;
- `title`: non-blank string;
- `joo_repository`: absolute path;
- `base_checkpoint`;
- `phases`: ordered non-empty list;
- `expected_change_paths`: explicit repository-relative file-path list; and
- `commit_plan` whenever `git_prepare` exists.

The accepted optional M1 descriptive metadata may remain optional for
compatibility, but it cannot change validation, transitions, authority, or
path scope.

`base_checkpoint` contains exactly:

- `branch`: non-blank exact string;
- `head`: non-blank exact commit string;
- `exact_tag`: non-blank exact tag string; and
- `require_clean_tree`: exact Boolean.

Each phase object contains exactly:

- `phase_id`;
- `prompt_source`; and
- `tool`.

The only allowed tools and exact phase/tool combinations are:

| Phase ID | Tool |
|---|---|
| `candidate_review` | `grok_review` |
| `architecture_authoring` | `codex_exec` |
| `architecture_review` | `grok_review` |
| `implementation` | `codex_exec` |
| `implementation_review` | `grok_review` |
| `commit_review` | `grok_review` |
| `git_prepare` | `git_prepare` |

The frozen legal order is the table order. A manifest may omit phases for an
ADR-only, review-only, remediation, or another separately approved milestone
shape, but the configured order must be a valid subsequence. Phase IDs must be
unique. Unknown phases, unknown tools, duplicate phase IDs, and mismatched
phase/tool pairs are rejected.

Schema-v2 validation freezes and enforces these co-presence and order rules
before run initialization:

- `architecture_authoring`, when present, requires
  `architecture_review` later in the phase list;
- `implementation`, when present, requires `implementation_review` later in
  the phase list;
- no `codex_exec` phase may be the final configured phase;
- implementation before an approved architecture review is rejected;
- commit review before all configured required prior reviews is rejected;
- `git_prepare`, when present, must be final and requires `commit_review`
  earlier in the phase list; and
- `commit_plan` is required whenever `git_prepare` is present.

A manifest violating any co-presence rule is rejected during manifest
validation before a run is initialized. Review-only manifests remain valid
when they contain no Codex phase and do not require `commit_plan` when they
contain no `git_prepare`. ADR-only manifests remain valid when authoring is
followed by architecture review and later commit review as configured. The
standard package sequence remains valid:

`candidate_review` → `architecture_authoring` → `architecture_review` →
`implementation` → `implementation_review` → `commit_review` → `git_prepare`.

`expected_change_paths` is the complete explicit path allowlist for the run.
It may be empty for a pure review-only pipeline. Its paths do not grant Git
mutation authority.

Every `expected_change_paths` entry must be a non-blank explicit
repository-relative file path. Directory entries, paths ending in `/`, `.`,
any `..` traversal segment, absolute paths, and glob or wildcard syntax are
invalid. Forbidden wildcard syntax includes at least `*`, `?`, `[`, and `]`.
No entry is interpreted as a textual prefix. No filesystem, directory,
implicit, or recursive expansion occurs, and no symlink canonicalization is
performed. A milestone whose file set is variable or unknown is not
representable by this first M2 path contract and requires later architecture;
M2 must not infer its paths.

### Commit plan

When required, `commit_plan` contains exactly:

- `commit_message`: non-blank exact string;
- `next_tag`: non-blank exact string; and
- `git_add_paths`: non-empty explicit repository-relative file-path list.

Every `git_add_paths` entry follows the same explicit-file validation as
`expected_change_paths`. Directory entries, paths ending in `/`, `.`, any
`..` traversal segment, absolute paths, globs, and wildcard syntax including
`*`, `?`, `[`, and `]` are invalid. No directory, implicit, or recursive
expansion and no textual-prefix interpretation exists. Every entry must also
be present in `expected_change_paths`; schema-v2 load validation requires
`git_add_paths` to be an explicit subset of `expected_change_paths`. Equality
is required only at the pre-`git_prepare` repository verification point
between the observed relevant file-path set and `git_add_paths`.

## 9. Identity

Each M2 run records these explicit identities:

- operator-selected `milestone_id`;
- generated M1-convention `run_id`;
- byte-exact `manifest_sha256`;
- base checkpoint identity;
- per-phase attempt number;
- prompt SHA-256;
- result and captured-artifact SHA-256 values;
- approval records; and
- monotonically appended event sequence.

Every retry creates a new attempt identity and never overwrites an earlier
attempt. Identity fields are opaque and do not encode domain semantics beyond
operator-selected milestone labels. A hash identifies exact bytes; it does
not attest semantic correctness or approval.

## 10. Phase model

M2 coordinates only the configured phases. Review phases run Grok and require
exact decision parsing before human approval eligibility. Authoring and
implementation phases run Codex with an immutable prompt and require
repository post-guards. `git_prepare` is deterministic and invokes no model.

Codex architecture authoring may queue `architecture_review_pending`
immediately after successful guarded completion. Codex implementation may
queue `implementation_review_pending` immediately after successful guarded
completion. These direct handoffs are not approvals of Codex output; the
following independent review and its human gate own advancement eligibility.
No authoring or implementation phase may terminate a pipeline or be the final
configured phase.

Final configured phases have exact type-specific completion semantics:

- a final review phase reaches `completed` only after its exact positive
  decision and explicit human approval;
- a final `git_prepare` phase transitions automatically from
  `git_prepare_complete` to `completed` after successful print-only
  preparation; and
- no tool success implies approval of architectural or implementation
  content.

`architecture_authoring_complete` transitions only to
`architecture_review_pending`. `implementation_complete` transitions only to
`implementation_review_pending`. Codex tool success never constitutes review,
approval, or run completion. The manifest co-presence rules make each review
mandatory before run initialization.

## 11. State model

The finite global states are exactly:

- `initialized`;
- `completed`;
- `blocked`;
- `cancelled`;
- `product_policy_required`; and
- `remediation_required`.

For every configured review phase `P`, M2 generates only:

- `P_pending`;
- `P_running`;
- `P_complete`;
- `P_failed`; and
- `P_approved`.

For every configured Codex phase `P`, M2 generates only:

- `P_pending`;
- `P_running`;
- `P_complete`; and
- `P_failed`.

Codex phases have no approved state. Successful guarded Codex completion
transitions directly to the required downstream review pending state and
never to `completed`.

`git_prepare` uses exactly:

- `git_prepare_pending`;
- `git_prepare_running`;
- `git_prepare_complete`; and
- `git_prepare_failed`.

It has no `git_prepare_approved`, `git_prepare_auto_approved`, or
`human_git_approval_pending` state. Among non-Codex configured phases,
`git_prepare` is the only phase without an approved state because it performs
no architectural judgment and no Git mutation. Codex phases separately have
no approved state because successful guarded execution hands off to review
and is never approval.

No states are generated for omitted phases. M2 introduces no
`push_complete`, `commit_complete`, `auto_approved`, `inferred_approved`, or
generic phase-detached success state.

Commit readiness is represented only by `commit_review_complete`, the exact
parsed token `COMMIT READY`, and subsequent explicit human approval. It is not
a Git commit, tag, push, or mutation-ready assertion by a model alone.

`completed`, `blocked`, `cancelled`, `product_policy_required`, and
`remediation_required` are terminal and have no transitions.

## 12. Transition table

| From | To | Exact trigger |
|---|---|---|
| `initialized` | first configured `P_pending` | successful initialization |
| `P_pending` | `P_running` | explicit `continue` after lock and pre-guards |
| `P_running` | `P_complete` | tool success, required immutable artifacts, and post-guards |
| `P_running` | `P_failed` | adapter, tool, or artifact failure |
| `P_failed` | `P_pending` | explicit `retry`, reserving a new attempt |
| review `P_complete` | `P_approved` | eligible exact positive decision plus explicit human `approve` |
| `P_approved` | next `Q_pending` | automatic phase advancement |
| final review `P_approved` | `completed` | automatic final advancement after its human gate |
| `architecture_authoring_complete` | `architecture_review_pending` | guarded direct handoff, not approval or completion |
| `implementation_complete` | `implementation_review_pending` | guarded direct handoff, not approval or completion |
| `commit_review_complete` | `commit_review_approved` | exact `COMMIT READY` eligibility plus explicit human `approve` |
| `commit_review_approved` | `git_prepare_pending` | automatic advancement when configured |
| `git_prepare_pending` | `git_prepare_running` | explicit `continue` |
| `git_prepare_running` | `git_prepare_complete` | all preconditions, path and tag checks, artifacts, and print-only rendering succeed |
| `git_prepare_running` | `git_prepare_failed` | renderer, artifact, verification, or precondition failure |
| `git_prepare_failed` | `git_prepare_pending` | explicit `retry` creating a new immutable attempt |
| `git_prepare_complete` | `completed` | automatic transition with `git_prepare_render_complete` event |
| review post-tool path with exact policy token | `product_policy_required` | exact phase-scoped parse before approvable completion |
| review post-tool path with exact remediation token | `remediation_required` | exact phase-scoped parse before approvable completion |
| review post-tool path with exact blocking token | `blocked` | exact phase-scoped parse before approvable completion |
| non-terminal | `blocked` | drift, mutation, unexpected path, ambiguous decision, or missing required artifact |
| non-terminal | `cancelled` | explicit human `cancel` |

`COMMIT REVIEW BLOCKED` maps to `blocked`, not positive eligibility. No model
completion is equivalent to approval. A review cannot transition from
complete to approved unless its one run-local artifact has exactly one
eligible positive decision block. Later validators, tools, or phases do not
run after a terminal transition.

Successful Git command printing is not human approval and does not execute
Git. The automatic `git_prepare_complete` to `completed` transition records
only that M2 finished verifying and preparing commands. Manual Git execution
and push remain outside the run state machine. `completed` has no outgoing
transition.

An interrupted running phase may transition only through explicit cancel or
an operator-directed recovery defined by later accepted architecture. M2 does
not infer process death or rewrite state.

## 13. Human gates

Explicit human approval is mandatory:

- after `candidate_review_complete`;
- after `architecture_review_complete`;
- after `implementation_review_complete`;
- after `commit_review_complete`;
- before any Git mutation, which occurs outside M2;
- before push, which occurs outside M2; and
- for every product-policy decision.

Approval records contain the phase, operator identity, and UTC timestamp.
They cannot be ambient, inferred, reused across phases, or supplied by review
prose. Codex authoring and implementation do not require an extra approval
before their configured independent review, because review completion and
human approval are the decision gates.

No separate M2 approval is required after `git_prepare_complete`. The human
operator's later execution of printed Git commands is not represented as an
M2 state transition. M2 records no `commit_complete` or `push_complete` state.

## 14. Decision parser

M2 parses only the run-local captured Markdown artifact for the exact phase
attempt. Global mutable `latest.*` files and historical prose are not
authoritative.

The grammar is exact:

1. Find a line exactly `FINAL DECISION:`.
2. The next non-empty line must be exactly `- <TOKEN>`.
3. The token must be in the exact allowlist for that phase.
4. There must be exactly one `FINAL DECISION:` block.
5. Zero blocks, multiple blocks, a missing token line, or an unrecognized
   token fail closed as ambiguous.

The parser performs no substring matching, fuzzy matching, case
normalization, prose inference, Markdown-emphasis stripping, or historical
format normalization. Milestone-prefixed tokens are unsupported in the first
M2 contract.

The exact phase-scoped tokens are:

| Phase | Positive | Policy or block | Remediation |
|---|---|---|---|
| `candidate_review` | `CANDIDATE APPROVED` | `NO SAFE CANDIDATE`; `PRODUCT POLICY REQUIRED` | `CANDIDATE REMEDIATION REQUIRED` |
| `architecture_review` | `ARCHITECTURE APPROVED` | none | `ARCHITECTURE REMEDIATION REQUIRED` |
| `implementation_review` | `IMPLEMENTATION APPROVED` | none | `IMPLEMENTATION REMEDIATION REQUIRED` |
| `commit_review` | `COMMIT READY` | `COMMIT REVIEW BLOCKED` | `COMMIT REMEDIATION REQUIRED` |

Positive tokens establish only eligibility for human approval. Candidate
policy tokens lead to `product_policy_required`; remediation tokens lead to
`remediation_required`; `COMMIT REVIEW BLOCKED` leads to `blocked`.

Parsing occurs in the review phase's post-tool completion path, after required
artifact capture and guards but before the phase can become eligible for human
approval. The exact outcome rules are:

- one positive exact token enters `P_complete` with positive approval
  eligibility;
- a product-policy exact token transitions directly to
  `product_policy_required`;
- a remediation exact token transitions directly to
  `remediation_required`;
- a blocking exact token transitions directly to `blocked`; and
- a missing, zero, duplicate, conflicting, or malformed decision block
  transitions directly to `blocked`.

Non-positive review outcomes never wait in an approvable `P_complete` state.

## 15. Prompt lifecycle

M2 never generates semantic prompt content. Every configured phase has an
explicit human-authored `prompt_source` resolving to a readable regular file
strictly inside the configured prompts root. This includes the deterministic
`git_prepare` phase contract, although its bytes are not sent to a model.

Prompt materialization is byte-exact, immutable, and exclusive per attempt.
The prompt SHA-256, source path, generated run-local path, phase, and attempt
are recorded. The bytes are not rewritten, summarized, corrected,
normalized, or embedded in command audit argv.

Missing prompt sources refuse initialization or execution according to the
validated lifecycle. A prompt source changed after its frozen hash is
recorded fails closed. M2-managed review prompts must require the unprefixed
exact decision grammar and tokens in Section 14.

## 16. Grok adapter

M2 reuses accepted M1 Grok behavior:

- configured review command or the accepted direct Grok adapter;
- one immutable run-local attempt directory;
- raw stdout and stderr capture;
- Markdown and JSON result capture;
- bounded resume controlled by `max_grok_resume_attempts`;
- unique result identity and exclusive artifact creation;
- run-local copies as authority rather than mutable global `latest.*`;
- no editing of review output; and
- full pre/post repository guards.

Grok process failure, unusable JSON, incomplete bounded resume, missing result,
duplicate artifact identity, or failed post-inspection prevents phase
completion.

## 17. Codex adapter

The first Codex adapter must:

- invoke configured `codex_command` non-interactively with the exact frozen
  prompt;
- create a new immutable attempt directory;
- capture command argv without embedding the full prompt bytes;
- capture raw stdout, raw stderr, exit code, and a final output artifact;
- record SHA-256 for every required captured artifact;
- enforce `max_codex_attempts` and explicit retry attempts;
- never pass danger-bypass, unrestricted, Git-authority, or equivalent flags;
- verify branch, HEAD, tag set at HEAD, staged state, and changed/untracked
  paths before and after execution;
- prove that no new commit or tag was created;
- prove that nothing was staged; and
- prove that no explicit observed file path outside `expected_change_paths`
  appeared.

Codex failure, non-zero exit, missing final output, missing required capture,
or bounded-attempt exhaustion produces phase failure. Any Codex Git history,
tag, branch, or index mutation produces `blocked`. M2 captures evidence but
never cleans, reverts, resets, deletes, repairs, or completes such a mutation.

## 18. Repository and path guards

Review phases must preserve the exact expected pre-phase working-tree
boundary. Authoring and implementation phases may change only explicit
`expected_change_paths`. At every intermediate phase, the complete observed
changed and untracked path set must be a subset of that allowlist.

Repository guards derive this path set only from
`git status --porcelain=v1 --untracked-files=all`. Each porcelain record is
parsed into pathnames rather than compared as a raw status line. For an
ordinary record, the two-character status prefix and following separator are
excluded and the reported pathname is included. For a rename or copy record,
both source and destination pathnames are included. Git porcelain quoting is
decoded deterministically so pathname bytes are preserved as reported by Git.
Comparisons use normalized repository-relative path strings without resolving
symlinks or performing filesystem canonicalization. Sorting is only for
deterministic recording; set comparison determines subset or equality.

The compared values are explicit file pathnames only. Directory entries are
never valid allowlist members and are never expanded. No prefix, implicit,
recursive, filesystem, or symlink-based interpretation can authorize an
observed path. For example, `SomePackage/` is invalid and cannot authorize
`SomePackage/models.py`; the file must be listed explicitly.

No staged change is allowed after any M2-managed phase. Branch and base HEAD
must remain unchanged throughout M2 because M2 executes no commit. Tag-set
inspection must detect creation, deletion, or collision, including lightweight
tags at HEAD. A configured clean precondition is checked exactly; an approved
dirty development boundary is represented only by its expected paths and
must not weaken history or index guards.

Before `git_prepare`, observed relevant paths must equal `git_add_paths`
exactly as repository-relative file-path sets. No directory expansion or
prefix matching may be used to establish equality. Unexpected, omitted,
staged, renamed, or out-of-bound paths block the run. If Codex creates any
file not explicitly listed in `expected_change_paths`, the run blocks. M2
never repairs the repository automatically.

## 19. Git preparation

`git_prepare` is deterministic print-only behavior and invokes no Git
mutation. Its preconditions are:

1. commit review parsed exactly `COMMIT READY`;
2. commit review has explicit human approval;
3. current branch and post-development checkpoint satisfy the manifest;
4. observed relevant explicit file paths equal `git_add_paths` exactly with
   no expansion or prefix matching;
5. the index is empty;
6. `next_tag` does not exist locally; and
7. `commit_message` and `next_tag` remain byte-for-byte manifest values.

On success, M2 prints:

- one exact path-scoped `git add` command;
- one exact `git commit` command;
- one exact lightweight `git tag` command;
- one exact current-branch push command;
- one exact tag push command; and
- exact post-check commands.

Arguments must be shell-safe and deterministically rendered without broad
globs or `git add .`. The output is an operator plan, not execution or
approval. M2 does not run any printed command. After all verification,
artifact capture, and rendering succeeds, `git_prepare_running` transitions
to `git_prepare_complete`, then automatically to `completed`. No
`git_prepare_approved` state or post-print approval exists.

## 20. Failure and recovery

Failure behavior is fail-closed:

- missing prompt refuses start or phase execution;
- missing result or required capture makes the phase failed;
- duplicate immutable artifacts make the phase failed;
- stale global results are ignored;
- checkpoint or tag drift blocks the run;
- dirty or unexpected paths block the run;
- any non-explicit, directory, absolute, traversal, glob, wildcard, duplicate,
  or otherwise invalid manifest path refuses schema-v2 load or initialization;
- staged changes block the run;
- Grok or Codex process failure makes the phase failed;
- ambiguous or missing required decision blocks the run;
- exact remediation decisions terminate in `remediation_required`;
- exact product-policy decisions terminate in `product_policy_required`;
- a Git-preparation renderer, artifact, verification, precondition, path, or
  tag-collision failure transitions `git_prepare_running` to
  `git_prepare_failed`;
- interrupted running phases require explicit cancel or operator-directed
  recovery; and
- retry creates a new immutable attempt without overwriting prior evidence,
  including `git_prepare_failed` to `git_prepare_pending`.

M2 never edits artifacts, invents a replacement prompt, restores a checkpoint,
removes unexpected paths, resets an index, changes branches, or repairs JOO
state.

## 21. Auditability

Each run stores immutable or durability-protected evidence for:

- frozen manifest bytes and SHA-256;
- exact base checkpoint;
- every pre- and post-phase checkpoint;
- generated prompt path and SHA-256;
- phase tool and command argv, without full prompt bytes;
- stdout and stderr paths;
- exit codes;
- every captured artifact path and SHA-256;
- parsed decision token or exact parse-failure reason;
- every state transition in `events.jsonl`;
- every approval with phase, operator, and UTC timestamp;
- Git-preparation output and its verification snapshot; and
- `summary.md` with the exact next legal operator command.

The automatic `git_prepare_complete` to `completed` transition appends an
event containing:

- source state `git_prepare_complete`;
- destination state `completed`;
- UTC timestamp;
- Git-preparation attempt identity;
- command-render artifact path and SHA-256;
- verification snapshot path and SHA-256; and
- reason code exactly `git_prepare_render_complete`.

This event records command-preparation completion only and must not claim that
Git was executed.

Run-local artifacts are authoritative and append-only per attempt. Mutable
global result aliases are provenance only. Audit records must not store secret
material from Grok or Codex configuration.

## 22. Dependency allowlist

The M2 production dependency allowlist is:

- Python 3 standard library; and
- list-argv subprocess execution of configured Git, Grok/review, and Codex
  commands.

No third-party Python dependency and no JOO domain import is required. Git
subprocesses are read-only inspection calls only. No Git mutation subprocess
is permitted, even if a human has approved commit readiness.

## 23. Explicit non-responsibilities

M2 does not:

- invent domains, models, fields, invariants, architecture, or prompts;
- select a candidate after `NO SAFE CANDIDATE`;
- resolve product policy;
- edit Grok or Codex output;
- infer, synthesize, or auto-grant approval;
- bypass human gates or failed, missing, ambiguous, or remediation reviews;
- execute any Git index, history, branch, tag, merge, rebase, or push mutation;
- stage broad paths or emit wildcard staging plans;
- modify files outside `expected_change_paths`;
- clean, revert, delete, or repair unexpected changes;
- run parallel milestone pipelines;
- weaken M1 review-only safety or CLI compatibility;
- implement JOO investment automation or Stage 6 runtime; or
- provide general workflow, cloud, service, or product-policy orchestration.

## 24. Compatibility requirements

M2 must preserve:

- existing Automation-M1 schema-v1 review-only manifests;
- existing run directory identities and immutable artifact meaning;
- M1 state and event readability;
- M1 CLI verbs and their established behavior;
- explicit human approvals and terminal-state immutability;
- prompt containment, exact bytes, SHA-256, and exclusive creation;
- Grok resume limits and run-local canonical results;
- read-only status and side-effect-free dry-run behavior;
- global lock exclusivity and no automatic force unlock;
- legacy `review` and `run_grok.sh` workflows; and
- the prohibition on Git writes.

Schema-v1 compatibility does not retroactively parse historical decisions or
require old reports to match the M2 grammar. M2-managed schema-v2 prompts and
runs use the new exact parser. Existing review-only runs remain auditable
under their original accepted semantics.

## 25. First implementation boundary

The first M2 implementation is limited to:

1. manifest schema v2;
2. compatibility handling for M1 schema;
3. ordered phase, Codex/review co-presence, and explicit-file path validation;
4. extended state and transition model;
5. Codex adapter;
6. exact `FINAL DECISION` parser;
7. human approval eligibility checks;
8. phase-aware path and checkpoint guards;
9. print-only `git_prepare` renderer;
10. deterministic next-command emission;
11. persistent audit updates;
12. focused and regression tests; and
13. README updates.

Implementation remains inside the existing Automation workspace and
`joo_auto` package. Exact implementation files, class names, function names,
state schema version, CLI additions, and test file allocation must be frozen
by the later implementation authorization without weakening this contract.

The first implementation explicitly defers Git mutation, push, semantic
prompt generation, ChatGPT API integration, parallel runs, force unlock, and
autonomous product-policy resolution.

## 26. Acceptance criteria

The Automation-M2 architecture is acceptable only when:

1. M2 remains an extension of `joo_auto` and preserves M1 review-only support;
2. schema v2 validates the exact phase, tool, checkpoint, expected-path, and
   conditional commit-plan contracts;
3. only legal phase subsequences and phase/tool combinations are accepted,
   every Codex phase has its required later review, no Codex phase is final,
   and `git_prepare` requires an earlier commit review;
4. state and transitions distinguish execution, completion, eligibility,
   human approval, terminal policy, remediation, blocked, and cancelled
   outcomes;
5. exact run-local decision parsing is fail-closed and phase-scoped;
6. Codex execution is frozen-prompt, bounded-attempt, fully captured, and
   guarded against history, tag, branch, index, and unexpected-path mutation;
7. review and Codex completion never imply approval;
8. every required human gate is enforced;
9. review phases alone own approved states, Codex completion hands off only to
   its mandatory review without auto-approval or run completion, and
   final-phase semantics are deterministic;
10. Git preparation has exactly pending, running, complete, and failed states,
    retries immutably, and automatically transitions from successful
    print-only completion to terminal `completed` without a second approval;
11. `expected_change_paths` and `git_add_paths` accept only explicit
    repository-relative file paths, use no directory expansion or prefix
    matching, and enforce intermediate subset and pre-prepare equality by set
    operations;
12. Git preparation is exact, path-scoped, verified, and print-only;
13. M2 executes no Git mutation and owns no architecture invention;
14. immutable audit evidence, including the exact
    `git_prepare_render_complete` transition event, and deterministic next
    commands are retained;
15. dependencies remain standard-library plus configured subprocesses;
16. tests prove M1 compatibility, parser exactness, transitions, retries,
    path guards, Codex capture, no auto-approval, and static absence of Git
    writes; and
17. no JOO domain contract or Stage 6 responsibility changes.

## 27. Deferred work

The following remain outside the first Automation-M2 implementation:

- execution of `git add`, commit, tag, or push under any approval token;
- automatic or human-gated push execution;
- automatic semantic prompt generation or rewriting;
- ChatGPT API or other hosted workflow integration;
- parallel milestone pipelines;
- automatic lock breaking or force unlock;
- automatic checkpoint repair or repository cleanup;
- autonomous product-policy resolution;
- fuzzy or legacy decision normalization;
- milestone-prefixed decision-token support;
- general-purpose test execution unless separately frozen; and
- JOO Stage 5 or Stage 6 investment/runtime automation.

Each deferred responsibility requires separate architecture and explicit
authorization. None is implied by M2 completion.
