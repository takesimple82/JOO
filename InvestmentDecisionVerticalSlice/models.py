from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

from ExactExpectedValue.models import ExactExpectedValueCalculation
from ExactNumericDeltaSignal.models import ExactNumericDeltaSignalClassification
from ExpectedValueAssumptionSet.models import ExplicitExpectedValueAssumptionSet
from ExplicitPortfolioImpact.models import ExplicitPortfolioImpact
from SemanticHypothesisProduction.models import SemanticallyProducedHypothesis
from SemanticThesisProduction.models import SemanticallyProducedThesis


class TruthClass(Enum):
    BROKER_FACT = "broker_fact"
    MARKET_FACT = "market_fact"
    RESEARCH_AI = "research_ai"
    DERIVED_DECISION = "derived_decision"


class ThesisState(Enum):
    STRENGTHENED = "STRENGTHENED"
    WEAKENED = "WEAKENED"
    UNCHANGED = "UNCHANGED"
    INVALIDATED = "INVALIDATED"
    UNRESOLVED = "UNRESOLVED"


class UncertaintyStatus(Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE_EVIDENCE = "INCOMPLETE_EVIDENCE"
    CONTRADICTORY = "CONTRADICTORY"
    UNRESOLVED = "UNRESOLVED"


class ComparisonStatus(Enum):
    LEFT_SUPERIOR = "LEFT_SUPERIOR"
    RIGHT_SUPERIOR = "RIGHT_SUPERIOR"
    EQUAL = "EQUAL"
    INCOMPARABLE = "INCOMPARABLE"
    UNRESOLVED = "UNRESOLVED"


class OpportunityRole(Enum):
    CURRENT_HOLDING = "CURRENT_HOLDING"
    CANDIDATE = "CANDIDATE"


class CioActionPosture(Enum):
    MAINTAIN = "MAINTAIN"
    RESEARCH_MORE = "RESEARCH_MORE"
    CONSIDER_ROTATION = "CONSIDER_ROTATION"
    INVALIDATE_THESIS = "INVALIDATE_THESIS"
    NO_ACTION_UNRESOLVED = "NO_ACTION_UNRESOLVED"


class JournalRecordKind(Enum):
    RESEARCH_EVIDENCE_BUNDLE = "RESEARCH_EVIDENCE_BUNDLE"
    SEMANTIC_PRODUCTION = "SEMANTIC_PRODUCTION"
    THESIS_TRANSITION = "THESIS_TRANSITION"
    PORTFOLIO_IMPACT = "PORTFOLIO_IMPACT"
    EV_ASSUMPTION_SET = "EV_ASSUMPTION_SET"
    EXACT_EV_RESULT = "EXACT_EV_RESULT"
    OPPORTUNITY_COMPARISON = "OPPORTUNITY_COMPARISON"
    CIO_DECISION = "CIO_DECISION"


@dataclass(frozen=True)
class ResearchEvidenceReference:
    evidence_id: str
    research_id: str
    committee_id: str
    portfolio_subject_id: str
    truth_class: TruthClass
    statement: str


@dataclass(frozen=True)
class ResearchEvidenceBundle:
    bundle_id: str
    iro_run_id: str
    portfolio_snapshot_id: str
    evidence: tuple[ResearchEvidenceReference, ...]
    required_committees: tuple[str, ...]
    completed_committees: tuple[str, ...]
    unresolved_contradiction_ids: tuple[str, ...]
    fresh: bool


@dataclass(frozen=True)
class SemanticProducerProvenance:
    producer_id: str
    model_id: str
    policy_version: str
    prompt_version: str


@dataclass(frozen=True)
class QualitativeEvidenceSignal:
    signal_id: str
    portfolio_subject_id: str
    consumed_evidence_ids: tuple[str, ...]
    material_change_statement: str
    provenance: SemanticProducerProvenance


@dataclass(frozen=True)
class NumericSignalReference:
    signal_id: str
    signal: ExactNumericDeltaSignalClassification


@dataclass(frozen=True)
class SemanticProductionRequest:
    request_id: str
    bundle: ResearchEvidenceBundle
    allowed_evidence_ids: tuple[str, ...]
    numeric_signals: tuple[NumericSignalReference, ...]
    allowed_horizon_ids: tuple[str, ...]


@dataclass(frozen=True)
class SemanticProductionOutput:
    output_id: str
    request_id: str
    qualitative_signals: tuple[QualitativeEvidenceSignal, ...]
    consumed_numeric_signal_ids: tuple[str, ...]
    hypothesis: SemanticallyProducedHypothesis
    thesis: SemanticallyProducedThesis
    thesis_state: ThesisState
    impact: ExplicitPortfolioImpact
    assumption_set: ExplicitExpectedValueAssumptionSet | None
    consumed_evidence_ids: tuple[str, ...]
    uncertainty_status: UncertaintyStatus
    provenance: SemanticProducerProvenance


@dataclass(frozen=True)
class ThesisTransition:
    transition_id: str
    portfolio_subject_id: str
    prior_thesis_id: str | None
    current_thesis_id: str
    state: ThesisState
    evidence_ids: tuple[str, ...]
    signal_ids: tuple[str, ...]
    semantic_output_id: str
    effective_at: datetime


@dataclass(frozen=True)
class PortfolioImpactRecord:
    record_id: str
    snapshot_id: str
    current_holding: bool
    thesis_transition_id: str
    evidence_ids: tuple[str, ...]
    signal_ids: tuple[str, ...]
    semantic_output_id: str
    uncertainty_status: UncertaintyStatus
    impact: ExplicitPortfolioImpact


@dataclass(frozen=True)
class EvAssumptionProvenance:
    record_id: str
    assumption_set: ExplicitExpectedValueAssumptionSet
    horizon_id: str
    evidence_ids: tuple[str, ...]
    thesis_transition_id: str
    impact_record_id: str
    semantic_output_id: str
    provenance: SemanticProducerProvenance
    uncertainty_status: UncertaintyStatus


@dataclass(frozen=True)
class ExactEvRecord:
    record_id: str
    source: EvAssumptionProvenance
    calculation: ExactExpectedValueCalculation


@dataclass(frozen=True)
class OpportunityEvaluation:
    opportunity_id: str
    portfolio_subject_id: str
    role: OpportunityRole
    comparison_policy_id: str
    probability_policy_version: str
    horizon_id: str
    unit_id: str
    ev_record: ExactEvRecord | None


@dataclass(frozen=True)
class OpportunityComparison:
    comparison_id: str
    left: OpportunityEvaluation
    right: OpportunityEvaluation
    status: ComparisonStatus


@dataclass(frozen=True)
class CioDecisionRecord:
    decision_id: str
    snapshot_id: str
    evidence_bundle_id: str
    semantic_output_id: str
    thesis_transition_ids: tuple[str, ...]
    impact_record_ids: tuple[str, ...]
    ev_record_ids: tuple[str, ...]
    comparison_ids: tuple[str, ...]
    horizon_ids: tuple[str, ...]
    posture: CioActionPosture
    what_changed: str
    why_it_matters: str
    superior_opportunity_id: str | None
    unresolved_reasons: tuple[str, ...]
    narrative_reference_ids: tuple[str, ...]
    executable: bool


@dataclass(frozen=True)
class JournalAppend:
    record_id: str
    kind: JournalRecordKind
    created_at: datetime
    payload: dict


@dataclass(frozen=True)
class StoredDecisionRecord:
    sequence: int
    record_id: str
    kind: JournalRecordKind
    created_at: datetime
    payload: dict
    previous_seal: str
    integrity_seal: str
