from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from ExpectedValueAssumptionSet.validation import validate_explicit_expected_value_assumption_set
from ExpectedValueAssumptionSetApplicability.classification import classify_expected_value_assumption_set_applicability
from ExpectedValueAssumptionSetApplicability.models import ExpectedValueAssumptionSetApplicabilityStatus
from ExplicitPortfolioImpact.validation import validate_explicit_portfolio_impact
from SemanticHypothesisProduction.validation import validate_semantically_produced_hypothesis
from SemanticThesisProduction.validation import validate_semantically_produced_thesis

from InvestmentDecisionVerticalSlice.models import *


def nonblank(name, value):
    if type(value) is not str:
        raise TypeError(f"{name} must be str")
    if value.strip() == "":
        raise ValueError(f"{name} must not be blank")


def unique_ids(name, values):
    if type(values) is not tuple:
        raise TypeError(f"{name} must be tuple")
    for value in values:
        nonblank(name, value)
    if len(set(values)) != len(values):
        raise ValueError(f"{name} must be unique")


def validate_provenance(value):
    if type(value) is not SemanticProducerProvenance:
        raise TypeError("provenance must be SemanticProducerProvenance")
    for name in ("producer_id", "model_id", "policy_version", "prompt_version"):
        nonblank(name, getattr(value, name))


def validate_evidence_bundle(bundle):
    if type(bundle) is not ResearchEvidenceBundle:
        raise TypeError("bundle must be ResearchEvidenceBundle")
    nonblank("bundle_id", bundle.bundle_id)
    nonblank("iro_run_id", bundle.iro_run_id)
    nonblank("portfolio_snapshot_id", bundle.portfolio_snapshot_id)
    if type(bundle.evidence) is not tuple:
        raise TypeError("evidence must be tuple")
    ids = []
    for item in bundle.evidence:
        if type(item) is not ResearchEvidenceReference:
            raise TypeError("evidence item must be ResearchEvidenceReference")
        for name in ("evidence_id", "research_id", "committee_id", "portfolio_subject_id", "statement"):
            nonblank(name, getattr(item, name))
        if item.truth_class is not TruthClass.RESEARCH_AI:
            raise ValueError("IRO evidence truth_class must be research_ai")
        ids.append(item.evidence_id)
    if len(set(ids)) != len(ids):
        raise ValueError("evidence_id must be unique")
    unique_ids("required_committees", bundle.required_committees)
    unique_ids("completed_committees", bundle.completed_committees)
    unique_ids("unresolved_contradiction_ids", bundle.unresolved_contradiction_ids)
    if type(bundle.fresh) is not bool:
        raise TypeError("fresh must be bool")


def validate_qualitative_signal(signal, allowed_evidence_ids):
    if type(signal) is not QualitativeEvidenceSignal:
        raise TypeError("signal must be QualitativeEvidenceSignal")
    nonblank("signal_id", signal.signal_id)
    nonblank("portfolio_subject_id", signal.portfolio_subject_id)
    unique_ids("consumed_evidence_ids", signal.consumed_evidence_ids)
    if not signal.consumed_evidence_ids:
        raise ValueError("qualitative signal requires evidence")
    if not set(signal.consumed_evidence_ids).issubset(set(allowed_evidence_ids)):
        raise ValueError("hallucinated evidence reference")
    nonblank("material_change_statement", signal.material_change_statement)
    validate_provenance(signal.provenance)


def validate_semantic_request(request):
    if type(request) is not SemanticProductionRequest:
        raise TypeError("request must be SemanticProductionRequest")
    nonblank("request_id", request.request_id)
    validate_evidence_bundle(request.bundle)
    unique_ids("allowed_evidence_ids", request.allowed_evidence_ids)
    if set(request.allowed_evidence_ids) != {x.evidence_id for x in request.bundle.evidence}:
        raise ValueError("evidence allowlist must match bundle")
    if type(request.numeric_signals) is not tuple:
        raise TypeError("numeric_signals must be tuple")
    numeric_ids = []
    from ExactNumericDeltaSignal.models import ExactNumericDeltaSignalClassification
    for reference in request.numeric_signals:
        if type(reference) is not NumericSignalReference:
            raise TypeError("numeric signal reference type mismatch")
        nonblank("signal_id", reference.signal_id)
        if type(reference.signal) is not ExactNumericDeltaSignalClassification:
            raise TypeError("numeric signal must reuse ExactNumericDeltaSignalClassification")
        numeric_ids.append(reference.signal_id)
    if len(set(numeric_ids)) != len(numeric_ids):
        raise ValueError("numeric signal ids must be unique")
    unique_ids("allowed_horizon_ids", request.allowed_horizon_ids)
    if not request.allowed_horizon_ids:
        raise ValueError("allowed_horizon_ids must not be empty")


def validate_semantic_output(request, output):
    validate_semantic_request(request)
    if type(output) is not SemanticProductionOutput:
        raise TypeError("output must be SemanticProductionOutput")
    nonblank("output_id", output.output_id)
    if output.request_id != request.request_id:
        raise ValueError("semantic request identity mismatch")
    unique_ids("consumed_evidence_ids", output.consumed_evidence_ids)
    if not set(output.consumed_evidence_ids).issubset(set(request.allowed_evidence_ids)):
        raise ValueError("hallucinated evidence reference")
    unique_ids("consumed_numeric_signal_ids", output.consumed_numeric_signal_ids)
    if not set(output.consumed_numeric_signal_ids).issubset({x.signal_id for x in request.numeric_signals}):
        raise ValueError("hallucinated numeric signal reference")
    if type(output.qualitative_signals) is not tuple:
        raise TypeError("qualitative_signals must be tuple")
    for signal in output.qualitative_signals:
        validate_qualitative_signal(signal, request.allowed_evidence_ids)
    validate_semantically_produced_hypothesis(output.hypothesis)
    validate_semantically_produced_thesis(output.thesis)
    if type(output.thesis_state) is not ThesisState:
        raise TypeError("thesis_state must be ThesisState")
    validate_explicit_portfolio_impact(output.impact)
    if output.impact.semantic_thesis != output.thesis:
        raise ValueError("portfolio impact thesis mismatch")
    subject_id = output.impact.portfolio_subject.subject_id
    evidence_by_id = {x.evidence_id: x for x in request.bundle.evidence}
    for signal in output.qualitative_signals:
        if signal.portfolio_subject_id != subject_id:
            raise ValueError("qualitative signal subject mismatch")
        if any(evidence_by_id[x].portfolio_subject_id != subject_id for x in signal.consumed_evidence_ids):
            raise ValueError("signal evidence subject mismatch")
        if not set(signal.consumed_evidence_ids).issubset(set(output.consumed_evidence_ids)):
            raise ValueError("signal evidence not consumed by output")
    if output.impact.horizon_id not in request.allowed_horizon_ids:
        raise ValueError("impact horizon not allowed")
    if type(output.uncertainty_status) is not UncertaintyStatus:
        raise TypeError("uncertainty_status must be UncertaintyStatus")
    validate_provenance(output.provenance)
    for signal in output.qualitative_signals:
        if signal.provenance != output.provenance:
            raise ValueError("signal producer provenance mismatch")
    blocked = (
        not request.bundle.fresh
        or set(request.bundle.required_committees) != set(request.bundle.completed_committees)
        or bool(request.bundle.unresolved_contradiction_ids)
        or output.uncertainty_status is not UncertaintyStatus.COMPLETE
        or output.thesis_state is ThesisState.UNRESOLVED
    )
    if request.bundle.unresolved_contradiction_ids and output.thesis_state is not ThesisState.UNRESOLVED:
        raise ValueError("contradiction requires UNRESOLVED thesis")
    if blocked and output.assumption_set is not None:
        raise ValueError("blocked semantic output must not contain EV assumptions")
    if output.assumption_set is not None:
        if output.thesis_state in (ThesisState.INVALIDATED, ThesisState.UNRESOLVED):
            raise ValueError("terminal or unresolved thesis must not have EV assumptions")
        validate_explicit_expected_value_assumption_set(output.assumption_set)
        if classify_expected_value_assumption_set_applicability(output.assumption_set) is not ExpectedValueAssumptionSetApplicabilityStatus.APPLICABLE:
            raise ValueError("probability total must equal 1")
        if output.assumption_set.impact.impact != output.impact:
            raise ValueError("assumption impact mismatch")


def validate_thesis_transition(value):
    if type(value) is not ThesisTransition:
        raise TypeError("transition must be ThesisTransition")
    for name in ("transition_id", "portfolio_subject_id", "current_thesis_id", "semantic_output_id"):
        nonblank(name, getattr(value, name))
    if value.prior_thesis_id is not None:
        nonblank("prior_thesis_id", value.prior_thesis_id)
    if type(value.state) is not ThesisState:
        raise TypeError("state must be ThesisState")
    unique_ids("evidence_ids", value.evidence_ids)
    unique_ids("signal_ids", value.signal_ids)
    if value.state is not ThesisState.UNCHANGED and not value.evidence_ids:
        raise ValueError("thesis transition requires evidence")
    if type(value.effective_at) is not datetime or value.effective_at.tzinfo is not timezone.utc:
        raise ValueError("effective_at must be UTC datetime")


def validate_ev_provenance(value):
    if type(value) is not EvAssumptionProvenance:
        raise TypeError("source must be EvAssumptionProvenance")
    for name in ("record_id", "horizon_id", "thesis_transition_id", "impact_record_id", "semantic_output_id"):
        nonblank(name, getattr(value, name))
    unique_ids("evidence_ids", value.evidence_ids)
    validate_explicit_expected_value_assumption_set(value.assumption_set)
    validate_provenance(value.provenance)
    if value.uncertainty_status is not UncertaintyStatus.COMPLETE:
        raise ValueError("EV assumptions must be complete")
    if value.assumption_set.impact.impact.horizon_id != value.horizon_id:
        raise ValueError("EV horizon mismatch")
    for outcome in value.assumption_set.outcomes:
        if type(outcome.probability) is not Decimal or type(outcome.value) is not Decimal:
            raise TypeError("probability and payoff must be Decimal")

def validate_cio_decision(value):
    if type(value) is not CioDecisionRecord:
        raise TypeError("decision must be CioDecisionRecord")
    for name in ("decision_id", "snapshot_id", "evidence_bundle_id", "semantic_output_id", "what_changed", "why_it_matters"):
        nonblank(name, getattr(value, name))
    unique_ids("thesis_transition_ids", value.thesis_transition_ids)
    unique_ids("impact_record_ids", value.impact_record_ids)
    unique_ids("ev_record_ids", value.ev_record_ids)
    unique_ids("comparison_ids", value.comparison_ids)
    unique_ids("horizon_ids", value.horizon_ids)
    unique_ids("unresolved_reasons", value.unresolved_reasons)
    unique_ids("narrative_reference_ids", value.narrative_reference_ids)
    if type(value.posture) is not CioActionPosture:
        raise TypeError("posture must be CioActionPosture")
    if value.superior_opportunity_id is not None:
        nonblank("superior_opportunity_id", value.superior_opportunity_id)
    if value.executable is not False:
        raise ValueError("CIO decision must not be executable")
    unique_ids("semantic_output_ids", value.semantic_output_ids)
    if value.semantic_output_ids and value.semantic_output_id not in value.semantic_output_ids:
        raise ValueError("primary semantic output absent from decision provenance")
