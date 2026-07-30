# JOO Command Center Product Roadmap

Version: 1.2  
Status: Approved  
Owner: JOO Command Center

## 1. Vision

JOO is an institutional-grade AI investment operating system that transforms research into repeatable capital allocation decisions.

Its long-term goal is to connect evidence, investment theses, portfolio construction, and CIO-level decisions in one reproducible system. JOO should help human decision-makers allocate capital consistently while preserving the reasoning and evidence behind every decision.

---

## 2. Core Principles

- Evidence First
- Human-in-the-loop
- Portfolio First
- Reproducibility
- Append Only History
- Automation with Verification
- Committee First Protocol
- Human Authority

### Portfolio First

Research begins from the current portfolio, watchlist, constraints, and investment objectives. The system does not perform broad research unless it can materially affect portfolio expected value.

### Committee First Protocol

- No investment decision is based on a single AI model.
- Relevant committee responses must be collected before CIO synthesis.
- Missing committee responses must be identified as missing.
- The system must not predict, invent, or simulate committee answers.

### Human Authority

JOO may generate research, analysis, and recommendations. Only the human operator may approve material capital allocation actions, override portfolio rules, or authorize execution.

---

## 3. System Architecture

```text
Portfolio Database
        │
        ▼
Research Planner
        │
        ├──────────────► External AI
        │                (Claude / ChatGPT / Gemini / Grok / Perplexity)
        │
        ▼
Committee Layer
        │
        ▼
Research Engine
        │
        ▼
Knowledge Engine
        │
        ▼
Evidence Engine
        │
        ▼
Signal Engine
        │
        ▼
Hypothesis Engine
        │
        ▼
Contradiction Engine
        │
        ▼
Thesis Engine
        │
        ▼
Portfolio Engine
        │
        ▼
CIO Engine
        │
        ▼
Human Approval Gate
        │
        ▼
Dashboard
        │
        ▼
History Database
        │
        ▼
Learning Engine
```

### Architecture Responsibilities

- **Portfolio Database:** Stores current holdings, watchlists, portfolio constraints, risk limits, investment objectives, and portfolio priorities.
- **Research Planner:** Converts portfolio priorities into research tasks. It generates standardized research prompts for the Committee Layer based on portfolio priorities. It should prevent irrelevant research and assign tasks to the Committee Layer.

  Research priority order:

  1. Current Holdings
  2. Watchlist
  3. Major Competitors
  4. Critical Suppliers
  5. Major Customers
  6. Sector Leaders

- **External AI:** Produces independent research outputs from multiple AI systems.
- **Committee Layer:** Collects and compares actual outputs from multiple AI systems. It must not simulate missing committee responses.
- **Research Engine:** Executes, versions, logs, validates, and replays research runs.
- **Knowledge Engine:** Normalizes facts, links entities, builds timelines, and preserves provenance.
- **Evidence Engine:** Scores evidence quality, freshness, relevance, and verification status.
- **Signal Engine:** Detects material changes that may affect expected value.
- **Hypothesis Engine:** Converts signals into testable explanations and assumptions.
- **Contradiction Engine:** Identifies conflicts between sources, evidence, and hypotheses.
- **Thesis Engine:** Maintains investment theses, catalysts, risks, and invalidation conditions.
- **Portfolio Engine:** Measures thesis impact across the entire portfolio and applies constraints.
- **CIO Engine:** Produces capital allocation recommendations and rationale.
- **Human Approval Gate:** Requires explicit human approval before material portfolio actions.
- **Dashboard:** Displays current state, changes, risks, recommendations, and priorities.
- **History Database:** Preserves append-only research, decisions, approvals, overrides, and outcomes.
- **Learning Engine:** Evaluates previous decisions and improves prompts, workflows, and decision quality. It must not change portfolio rules or execute capital actions without human approval. Learn from portfolio outcomes and feed improvements back into future research, thesis evaluation, and decision processes.

---

## 4. Development Roadmap

### Stage 0 — Foundation

#### Objective

Establish a stable, documented, and reproducible engineering foundation for all future development.

#### Architecture Mapping

- Repository
- Configuration
- Schemas
- Event Logging
- Development Controls

#### Deliverables

- Documented system architecture and product roadmap
- Standard development and contribution workflow
- Append-only event history with a documented schema
- Reusable event-logging utility
- Stable repository structure and engineering conventions

#### Exit Criteria

- Architecture, roadmap, and development workflow are documented.
- Event history can be written and validated as JSON Lines.
- Core engineering conventions are consistently applied.
- The repository is ready for feature development without foundational ambiguity.

### Stage 1 — Research Layer

#### Objective

Create a repeatable research process that converts external information and AI analysis into structured research artifacts.

#### Architecture Mapping

- Portfolio Database input
- Research Planner
- External AI
- Committee Layer
- Research Engine

#### Deliverables

- Multi-AI Research that collects outputs from multiple AI systems
- Prompt Library for standardized, reusable research instructions
- Research Versioning for inputs, prompts, configurations, and outputs
- Research Replay for reproducing prior research executions
- Research Logging for successful and failed executions
- Source attribution and collection timestamps
- Research quality and completeness checks

#### Exit Criteria

- The same inputs and configuration produce reproducible research artifacts.
- Multiple AI research outputs are collected before research enters the CIO process.
- Versioned research can be replayed from its recorded inputs and prompts.
- Every research output is linked to its sources and execution context.
- Failed and successful executions are observable.
- Human reviewers can verify research before downstream use.

### Stage 2 — Knowledge Layer

#### Objective

Transform research artifacts into structured, queryable, and durable investment knowledge.

#### Architecture Mapping

- Knowledge Engine
- Evidence Engine
- Fact Normalization
- Entity Linking
- Timeline
- Provenance

#### Deliverables

- Fact Normalization into consistent, structured records
- Entity Linking across research sources and knowledge records
- Timeline construction for material events and changes
- Knowledge Versioning with append-only updates
- Entity and relationship models
- Structured fact and claim extraction
- Evidence provenance and confidence metadata
- Knowledge retrieval interfaces

#### Exit Criteria

- Research can be converted into normalized knowledge records.
- Facts are linked to consistent entities and placed in a queryable timeline.
- Every material claim is traceable to supporting evidence.
- Knowledge changes preserve historical state.
- Relevant knowledge can be reliably retrieved by entity and topic.

#### Current Repository Boundary

The accepted repository implementation through
`v2.7-stage3-evidence-supersession-applicability-m1` completes the current
Foundation input and Evidence contract scope:

- `ResearchFinding`-based Foundation input contracts
- Evidence validation, provenance, assessment, and aggregation
- The structural `ExactObservedNumericProposition` substrate
- Exact numeric comparison and contradiction-candidate classification
- Explicit proposition supersession and supersession applicability

This boundary does not complete semantic Knowledge production.
`ResearchFinding.statement` is an interpreted research statement, not an
immutable source document or structured semantic evidence record. The
repository has no callable producer that converts it into an
`ExactObservedNumericProposition`; that proposition remains a downstream
structural substrate.

The repository does not infer numeric or date occurrences from free-form
research text. It does not treat `event_date` or `publication_date` as an
`observed_on` value. Semantic Knowledge production must be supplied by an
accepted external or future upstream producer. No extraction runtime, LLM
inference contract, heuristic NLP parser, or closed extraction grammar is
owned by this repository boundary.

The following Knowledge responsibilities remain unimplemented:

- Immutable source snapshots and numeric/date occurrence extraction
- Numeric-value-to-observed-date semantic linkage
- Canonical entity governance and predicate specifications
- Effective-context semantic production and temporal ordering
- Baseline selection and durable Knowledge retrieval

Signal, Hypothesis, and Thesis remain unimplemented. Signal implementation
must not begin until accepted upstream contracts provide semantically produced
numeric propositions, explicit observed-date context, compatible context
ordering, and deterministic baseline/current inputs. The existing opaque
`effective_context_id` supports identity equality only and must not be treated
as chronological or self-ordering.

### Stage 3 — Investment Intelligence

#### Objective

Convert structured knowledge into testable investment theses while detecting conflicting evidence and assumptions.

#### Architecture Mapping

- Signal Engine
- Hypothesis Engine
- Contradiction Engine
- Thesis Engine

#### Deliverables

- Evidence scoring and ranking
- Contradiction detection and resolution workflow
- Thesis creation and lifecycle management
- Assumption, catalyst, and risk tracking
- Thesis-to-portfolio impact analysis

#### Exit Criteria

- Each thesis is supported by explicit evidence and assumptions.
- Contradictory evidence is surfaced rather than discarded.
- Thesis changes are versioned and explainable.
- Risks, catalysts, and invalidation conditions are measurable.

### Stage 4 — Investment Intelligence Structural Chain

#### Objective

Establish a validation-first structural chain from accepted Evidence through
Signal, Hypothesis, and Thesis to a canonical Portfolio Subject.

#### Architecture Mapping

- Evidence Engine
- Signal Engine
- Hypothesis Engine
- Thesis Engine
- Portfolio Subject boundary

#### Deliverables

- Exact cross-context numeric change and Signal contracts
- Explicit and semantically produced Hypothesis contracts
- Signal-to-Hypothesis linkage
- Explicit and semantically produced Thesis contracts
- Hypothesis-to-Thesis linkage
- Thesis-to-Portfolio-Subject structural linkage

#### Exit Criteria

- The accepted structural chain is continuous from Evidence to a canonical
  Portfolio Subject.
- Structural identity, semantic production attestation, linkage, and numeric
  evaluation responsibilities remain separate.
- Portfolio Impact interpretation is not inferred from numeric direction,
  Thesis text, or identifiers.

#### Completion Status

Completed at `v3.21-stage4-thesis-portfolio-subject-link-m1`. Portfolio Impact,
Expected Value, portfolio operational context, recommendation, allocation,
constraints, human decisions, overrides, and audit boundaries are planned
Stage 5 responsibilities.

### Stage 5 — Semantic Investment Interpretation and Decision

#### Objective

Translate the accepted structural investment-intelligence chain into explicit,
portfolio-aware semantic interpretations and reviewable capital decision
contracts.

#### Architecture Mapping

- Portfolio Impact
- Expected Value
- Portfolio Context
- Recommendation and Allocation Proposal
- Constraint Evaluation
- Explainability
- Human Decision and Override
- Audit Domain

#### Planned Deliverables

- Portfolio Impact applicability, interpretation policy, and semantic
  production
- Expected Value assumptions and exact result contracts
- Canonical portfolio identity, membership, positions, holding snapshots, and
  watchlist entries
- Portfolio snapshots, capital buckets, and risk budgets
- Recommendations, allocation proposals, and constraint evaluations
- Explainability, human approval, override, and audit domain boundaries

#### Status

Planned. Stage 5 implementation is not complete. Runtime execution, workflow,
monitoring, persistence enforcement, and automation remain Stage 6 scope.

### Stage 6 — Automation Platform

#### Objective

Operate the complete investment workflow as a reliable, observable, and verified automation platform.

#### Architecture Mapping

- History Database
- Learning Engine
- Scheduling
- Monitoring
- Recovery
- Quality Measurement

#### Deliverables

- Scheduled and event-driven workflows
- Integrated monitoring, alerting, and recovery
- Decision and portfolio dashboard
- End-to-end history database
- Automated verification and operational controls
- Learning Engine that learns from previous decisions
- Prompt improvements based on observed outcomes
- Workflow improvements based on execution history
- Decision quality measurement

#### Exit Criteria

- Qualified workflows run automatically with verification gates.
- Failures are recorded, surfaced, and recoverable.
- The dashboard provides current state and complete decision history.
- Reliability and automation targets are continuously measured.
- Human operators retain visibility and control over material decisions.

---

## 5. Non-Goals

- Fully autonomous trading
- Market prediction as the primary objective
- Replacing human investment judgment
- Using unverified information as fact
- Allowing one AI model to control the decision process
- Modifying portfolio rules without explicit human approval

---

## 6. Product Philosophy

JOO is not designed to predict markets.

JOO is designed to improve decision quality.

Every component should increase evidence quality, reduce uncertainty, and improve capital allocation over time.

---

## 7. Success Metrics

- **Research reproducibility:** At least 95% of research runs can be reproduced from recorded inputs, prompts, configuration, and source references.
- **Decision traceability:** 100% of material portfolio recommendations link to their supporting theses, evidence, assumptions, and approvals.
- **Portfolio consistency:** 100% of proposed allocations pass documented portfolio constraints before approval.
- **Automation coverage:** At least 90% of qualified recurring workflow steps execute automatically with verification gates.
- **System reliability:** At least 99.5% successful scheduled workflow execution, excluding documented external service outages.

---

## 8. Guiding Rule

All future development tasks must align with this roadmap. New stages require updating this document before implementation.

- Every task must map to one current stage and one documented deliverable.
- Review findings must be resolved before approval and commit.
- Approved stages may not be changed casually.
- Material architecture changes require a roadmap version update.
- New features that do not align with the roadmap must be placed in a backlog.
- No implementation may begin before the relevant stage plan and exit criteria are defined.
