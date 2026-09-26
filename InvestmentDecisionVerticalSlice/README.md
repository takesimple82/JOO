# Investment Decision Vertical Slice

This package is the narrow operational seam from admitted IRO research to a
non-executable JOO CIO analytical decision. It reuses the accepted Hypothesis,
Thesis, Portfolio Impact, Expected Value assumption, and ExactExpectedValue
contracts rather than redefining them.

Truth classes remain disjoint: `broker_fact`, `market_fact`, `research_ai`,
and `derived_decision`. Qualitative signals contain no numeric factual value,
probability, payoff, or materiality score. Numeric signals reuse
`ExactNumericDeltaSignalClassification` through an explicit reference.

Semantic outputs are admitted only against exact evidence, numeric-signal,
subject, horizon, committee-completeness, contradiction, producer, model,
prompt, and policy bindings. Probabilities and payoffs are research-derived
assumptions expressed as exact Decimal values; existing ExactExpectedValue is
the sole arithmetic authority.

Comparisons are symmetric, strict, and limited to exact matching horizon,
unit, probability policy, and comparison policy. No cross-horizon ranking,
incumbent bonus, margin, transaction cost, or turnover policy exists.

CIO postures are `MAINTAIN`, `RESEARCH_MORE`, `CONSIDER_ROTATION`,
`INVALIDATE_THESIS`, and `NO_ACTION_UNRESOLVED`. Every decision has
`executable=False`; it is not allocation, approval, order intent, or broker
authority.

`DecisionJournal` provides local SQLite WAL/FULL, canonical JSON, chained
integrity seals, immutable triggers, exact schema verification, transactional
batch append, restart validation, and deterministic replay inputs. Replay
does not call an AI model.

This package owns no allocation quantity, position sizing, capital/risk
amount, rebalance, approval, order, execution, scheduler, UI, generic
orchestration framework, or JOO-Automation dependency.
# Operational CIO reuse

`OperationalCioCycle` is the production caller of the existing evidence,
semantic, impact, EV, comparison and CIO contracts. `CioDecisionRecord` keeps
the legacy primary `semantic_output_id` and adds optional ordered
`semantic_output_ids` for a multi-subject decision. When provided, this set must
include the primary output. Operational decisions always populate the complete
set and remain non-executable.

The existing journal admits `OPERATIONAL_CIO_CYCLE` as one atomic dependency
graph record. It exposes its resolved physical `journal_identity` for cycle
binding, and locks before reading the append chain tail to prevent concurrent
forks. No second database or relaxed schema/trigger/integrity contract is added.
