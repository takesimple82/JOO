# Operational CIO — Completion Block A

This is ordinary application composition, not an orchestration framework.
One `run_operational_cio_cycle(...)` invocation executes the existing KB First
Slice, real IRO RunCoordinator and EvidenceStore, per-subject Second Slice
admission, concrete provider-neutral semantic synthesis, unchanged
ExactExpectedValue, compatible comparisons, non-executable CIO synthesis,
and one atomic append to the existing DecisionJournal.

## Public API and caller authority

`CycleConfig`, `CandidateAdmission`, `SemanticBinding`, `SubjectPlan`,
`OpportunityUniverse`, `CycleResult`, `run_operational_cio_cycle`, `replay_cycle`.
All model containers are frozen dataclasses. Subject declarations, admissions,
plans, numeric references and outputs retain ordered immutable tuples.

The caller supplies explicit subject identities/display names, horizon, unit,
impact policy, freshness duration, comparison policy, producer identity,
probability-policy version, model and committee/provider bindings. There are
no invented thresholds, probabilities, capital values or hard-coded vendors.
`SemanticBinding.provenance` must match its authorized producer/probability
policy; the selected concrete AIAdapter must expose the configured `model`.
An adapter without inspectable configured model identity is rejected.

`config.journal_id` is the existing journal's `journal_identity` (resolved
physical SQLite path), checked at append and replay. Moving/copying a journal
does not silently preserve that binding. A completed cycle ID cannot execute
again: use `replay_cycle(journal, cycle_id, journal.journal_identity)`.

`first_slice_arguments` are the existing First Slice keyword arguments:
configured KB adapter, collection/normalization identities, durable
`FactStore` backed by `SQLiteAppendOnlyFactEngine`, snapshot producer, explicit
watchlist declarations, freshness policy, initialized IRO run, prior snapshot,
ingress ID, real `RunCoordinator`, and its caller-configured committee inputs.
The composition never obtains credentials or enables a network provider on
its own. No fake producer or manual semantic output is accepted by the public
execution path. External provider clients/HTTP can be injected for tests.

## Opportunity Universe and IRO admission

Holdings derive only from the accepted snapshot. Watchlist membership alone
is not evaluation eligibility, much less investment authority. Candidates
require an explicit `CandidateAdmission(subject, admission_id, provenance)`;
AI cannot create/promote them. All declarations must exactly cover the union
of holdings, watchlist and explicit candidates. Duplicate/conflicting IDs,
empty/no-eligible universe, out-of-universe plans, and identity drift reject.

A candidate need not be watchlisted. The composition translates candidate
admissions into `ExplicitResearchCandidate` inputs for the existing IRO
planner. Optional `decision_candidates` requests research coverage of current
holdings plus those candidates; no snapshot/watchlist is modified and no
synthetic factual delta is created. `CANDIDATE_RESEARCH` needs an explicit
caller committee route. A persisted `DECISION_RESEARCH_ADMISSION` binds source,
admission ID, provenance, snapshot and holdings; replay verifies it against
the universe. Ordinary IRO callers omitting this optional input retain the
existing scan-driven scope.

IRO prompts bind the actual planned subject and immutable snapshot context
(exact holding quantity strings and watchlist membership), not a reused
committee-wide subject label. Every finding carries its frozen prompt ID/hash.
Research remains `research_ai`: provider/model output is never broker truth.

Only a completed, non-escalated IRO with a resolved current contradiction
audit can enter the decision path. Each eligible subject needs exactly one
current-wave research unit, complete required committees from independent
configured providers, exact subject/finding/provider/prompt bindings, and
nonmissing fresh timestamps. Older waves or another subject's completeness
cannot fill a gap. Failure/no-change from the First Slice never wakes CIO.

## Structured semantics and exact arithmetic

The concrete `ProviderSemanticProducer` uses the existing ExecutionEngine
and a caller provider map. It sends a validated SemanticProductionRequest,
explicit subject/horizon/policy and exact numeric-reference context. It checks
the returned provider/task/prompt/version identity before strict JSON parsing.
Unknown/duplicate keys, unparseable text, unsupported states, missing evidence,
hallucinated evidence/signal references, subject/horizon drift, wrong numeric
objects/classifications, float probabilities, nonfinite numbers and incomplete
assumptions reject. AI only returns signal IDs, never replacement numeric
signal objects. Probabilities/payoffs are decimal **strings**; existing
assumption applicability enforces exact sum 1 without residual filling.

Wire schema keys: `subject_id`, `horizon_id`, `evidence_ids`,
`numeric_signal_ids`, `hypothesis`, `thesis`, `thesis_state`, `material_change`,
`rationale`, `direction`, `uncertainty`, `outcomes`. Each outcome has exactly
`statement`, `probability`, `payoff`. The adapter assigns all downstream IDs
deterministically from the request. No EV field is allowed. Missing/invalidated/
unresolved assumptions fail closed; this slice never manufactures a neutral EV.

The existing hypothesis/thesis/impact/assumption admission and
`calculate_admitted_ev` invoke unchanged ExactExpectedValue. Every evaluation
inherits its subject role/eligibility, evidence, horizon/unit and policy from
the admitted graph, not model authority.

## Comparison and CIO boundary

Strict symmetric EV comparison has no incumbent bonus, turnover penalty,
transaction cost threshold or margin. Different horizon/unit/probability/
comparison policies yield diagnostic `INCOMPARABLE` records as required;
these records are never ranked or supplied to any plane's CIO synthesis.
Each compatible plane gets its own decision. A unique top candidate strictly
above the plane's holdings may produce CONSIDER_ROTATION. Equal top candidates
cannot be selected by iteration order: ambiguous superiority is unresolved.
All contributing semantic output IDs are retained in the canonical CIO record
in addition to its backward-compatible primary output ID.

Every CIO record has `executable=False`. It grants no allocation, rule override,
investment approval, order or broker execution authority. Engineering Human
Commit Gate and Investment Human Approval Gate remain separate.

## Atomic journal and replay

`OPERATIONAL_CIO_CYCLE` stores the completed dependency graph in one existing
DecisionJournal transaction: original raw/canonical sealed facts, snapshot,
IRO result/evidence/prompt bytes, candidate admission, subject/provider policies,
original admission time, structured semantic response text, derived artifacts
and decisions. No second database or mutable semantic cache is introduced.
Facts/research may remain append-only if later synthesis fails; no partial
completed CIO record is written. Freshness is checked both before AI and after
its latency, immediately before append.

The closed versioned codec permits only enumerated trusted domain model types,
exact Decimal/date/tuple/bytes representations. No pickle, data-driven import,
float/NaN or arbitrary type construction is permitted. Replay reconstructs and
validates the stored graph at its historical timestamps, reuses stored semantic
text, reruns exact arithmetic/comparisons/CIO, and requires exact equality with
stored results. It never calls AI, broker, market or IRO. Replay is historical
verification, not renewed current freshness or execution authorization.

The reused journal now acquires its write transaction **before** reading the
chain tail, preventing concurrent chain forks. Existing schema/triggers/seals
remain enforced; SQL failure rolls back the entire batch. Integrity seals
detect corruption, not a privileged attacker rewriting every byte and seal.

## Verification and non-responsibilities

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s OperationalCioCycle/tests -q`

`PYTHONDONTWRITEBYTECODE=1 python3 test_repository.py`

Integration tests replace only external KB HTTP and AI HTTP/client boundaries;
KB adapter/transport, SQLite FactStore, snapshot producer, RunCoordinator,
ResearchOrchestrator, PipelineRuntime, CommitteeRuntime, ExecutionEngine,
semantic adapter, Exact EV, CIO and DecisionJournal execute production code.
No live credentialed provider reliability, 24/7 service, allocation, weights,
risk budgets, approval, order, fill, scheduler or dashboard is claimed.
