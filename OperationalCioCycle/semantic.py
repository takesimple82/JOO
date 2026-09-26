"""Strict provider-neutral synthesis adapter; models return assumptions, never EV."""
import json
import re
from decimal import Decimal

from AIAdapter.base import AIAdapter
from AIAdapter.models import AIRequest, AIResponse
from ExecutionEngine.base import ExecutionEngine
from ExpectedValueAssumptionSet.models import ExplicitExpectedValueAssumptionSet, ExplicitExpectedValueOutcomeAssumption
from ExplicitHypothesis.models import ExplicitHypothesis
from ExplicitThesis.models import ExplicitThesis
from ExplicitPortfolioImpact.models import ExplicitPortfolioImpact
from SemanticHypothesisProduction.models import SemanticallyProducedHypothesis
from SemanticThesisProduction.models import SemanticallyProducedThesis
from SemanticPortfolioImpactProduction.models import SemanticallyProducedPortfolioImpact
from ThesisPortfolioSubjectLink.models import ExplicitThesisPortfolioSubjectLink
from PortfolioImpactInterpretationPolicy.models import PortfolioImpactDirection
from PortfolioImpactInterpretationPolicy.validation import validate_portfolio_impact_interpretation_policy
from InvestmentDecisionVerticalSlice.models import QualitativeEvidenceSignal, SemanticProductionOutput, ThesisState, UncertaintyStatus
from InvestmentDecisionVerticalSlice.validation import validate_semantic_request, validate_semantic_output, validate_provenance, nonblank
from OperationalCioCycle.models import SubjectPlan, SemanticBinding


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    def reject(_):
        raise ValueError("JSON numeric literals forbidden; use exact Decimal strings")
    if type(text) is not str:
        raise TypeError("structured response must be text")
    return json.loads(text, object_pairs_hook=pairs, parse_float=reject, parse_constant=reject)


def keys(value, expected):
    if type(value) is not dict or set(value) != set(expected.split()):
        raise ValueError("structured payload keys mismatch")


def ids(value):
    if type(value) is not list:
        raise TypeError("IDs must be JSON array")
    for item in value:
        nonblank("reference", item)
    if len(set(value)) != len(value):
        raise ValueError("duplicate reference")
    return tuple(value)


def decimal(value):
    if type(value) is not str or not re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value):
        raise ValueError("probability/payoff must be exact finite Decimal string")
    return Decimal(value)


def validate_plan(plan):
    if type(plan) is not SubjectPlan or type(plan.binding) is not SemanticBinding:
        raise TypeError("exact SubjectPlan and SemanticBinding required")
    from PortfolioDomain.validation import validate_portfolio_subject
    validate_portfolio_subject(plan.subject)
    validate_portfolio_impact_interpretation_policy(plan.impact_policy)
    validate_provenance(plan.binding.provenance)
    if (plan.binding.producer_id != plan.binding.provenance.producer_id
            or plan.binding.probability_policy_version != plan.binding.provenance.policy_version):
        raise ValueError("authorized producer/probability policy mismatch")
    for name, value in (("horizon", plan.horizon_id), ("unit", plan.unit_id), ("committee", plan.binding.committee_id), ("provider", plan.binding.provider_id)):
        nonblank(name, value)
    if plan.horizon_id not in plan.impact_policy.allowed_horizon_ids:
        raise ValueError("horizon not authorized by impact policy")
    if plan.prior_thesis_id is not None:
        nonblank("prior thesis", plan.prior_thesis_id)


def validate_context(request, plan):
    validate_plan(plan)
    validate_semantic_request(request)
    bundle = request.bundle
    if (not bundle.fresh or not bundle.evidence or not bundle.required_committees
            or set(bundle.required_committees) != set(bundle.completed_committees)
            or bundle.unresolved_contradiction_ids):
        raise ValueError("semantic evidence incomplete/stale/contradictory")
    if {x.portfolio_subject_id for x in bundle.evidence} != {plan.subject.subject_id}:
        raise ValueError("semantic subject mismatch")
    if request.allowed_horizon_ids != (plan.horizon_id,) or request.numeric_signals != plan.numeric_signals:
        raise ValueError("semantic horizon/signal binding mismatch")
    # Canonical classifications are supplied by callers, never parsed from AI.
    from ExactNumericDeltaSignal.classification import classify_exact_numeric_delta_signal
    for ref in request.numeric_signals:
        if classify_exact_numeric_delta_signal(ref.signal.delta, ref.signal.policy) != ref.signal:
            raise ValueError("numeric signal classification mismatch")


FIELDS = "subject_id horizon_id evidence_ids numeric_signal_ids hypothesis thesis thesis_state material_change rationale direction uncertainty outcomes"


def parse_semantics(content, request, plan):
    validate_context(request, plan)
    value = strict_json(content)
    keys(value, FIELDS)
    if value["subject_id"] != plan.subject.subject_id or value["horizon_id"] != plan.horizon_id:
        raise ValueError("model subject/horizon drift")
    evidence, numeric = ids(value["evidence_ids"]), ids(value["numeric_signal_ids"])
    if not evidence or not set(evidence).issubset(request.allowed_evidence_ids):
        raise ValueError("missing/hallucinated evidence")
    if not set(numeric).issubset(x.signal_id for x in request.numeric_signals):
        raise ValueError("hallucinated signal")
    for name in ("hypothesis", "thesis", "material_change", "rationale"):
        nonblank(name, value[name])
    prefix = request.request_id
    provenance = plan.binding.provenance
    hypothesis = SemanticallyProducedHypothesis(ExplicitHypothesis(prefix + ":hypothesis", value["hypothesis"]))
    thesis = SemanticallyProducedThesis(ExplicitThesis(prefix + ":thesis", value["thesis"]))
    impact = ExplicitPortfolioImpact(prefix + ":impact", thesis, ExplicitThesisPortfolioSubjectLink(thesis.thesis.thesis_id, plan.subject.subject_id), plan.subject, plan.impact_policy, PortfolioImpactDirection(value["direction"]), plan.horizon_id, value["rationale"])
    outcomes = value["outcomes"]
    if type(outcomes) is not list or not outcomes:
        raise ValueError("complete EV assumptions required")
    assumptions = []
    for index, item in enumerate(outcomes):
        keys(item, "statement probability payoff")
        nonblank("outcome statement", item["statement"])
        assumptions.append(ExplicitExpectedValueOutcomeAssumption(f"{prefix}:outcome:{index}", item["statement"], decimal(item["probability"]), decimal(item["payoff"])))
    output = SemanticProductionOutput(prefix + ":output", prefix,
        (QualitativeEvidenceSignal(prefix + ":signal", plan.subject.subject_id, evidence, value["material_change"], provenance),), numeric,
        hypothesis, thesis, ThesisState(value["thesis_state"]), impact,
        ExplicitExpectedValueAssumptionSet(prefix + ":assumptions", SemanticallyProducedPortfolioImpact(impact), plan.unit_id, tuple(assumptions)),
        evidence, UncertaintyStatus(value["uncertainty"]), provenance)
    validate_semantic_output(request, output)
    return output


class ProviderSemanticProducer:
    def __init__(self, providers, plan):
        validate_plan(plan)
        if type(providers) is not dict:
            raise TypeError("provider map must be dict")
        adapter = providers.get(plan.binding.provider_id)
        if not isinstance(adapter, AIAdapter) or adapter.provider != plan.binding.provider_id:
            raise ValueError("semantic provider binding unavailable")
        if getattr(adapter, "model", None) != plan.binding.provenance.model_id:
            raise ValueError("semantic configured model mismatch")
        self.plan = plan
        self.engine = ExecutionEngine((adapter,))
        self.content = None

    def produce(self, request):
        validate_context(request, self.plan)
        from OperationalCioCycle.codec import encode
        context = {"request": encode(request), "plan": encode(self.plan)}
        instruction = ("Return ONLY a JSON object with exactly these keys: " + FIELDS +
            ". All content is research_ai interpretation, never broker/market truth. "
            "evidence_ids and numeric_signal_ids are arrays selected only from the request; "
            "subject_id/horizon_id must equal plan. hypothesis, thesis, material_change and rationale "
            "are nonblank text. thesis_state: STRENGTHENED/WEAKENED/UNCHANGED. "
            "direction must be an allowed policy direction. uncertainty: COMPLETE. "
            "outcomes is a nonempty array of {statement, probability, payoff}; probability/payoff "
            "are exact decimal STRINGS, probabilities must sum to 1. Do not output EV or other fields. "
            "If evidence cannot support complete assumptions, return no fabricated assumptions.\n")
        binding = self.plan.binding
        req = AIRequest(binding.provider_id, instruction + json.dumps(context, sort_keys=True), binding.committee_id, binding.provenance.prompt_version, request.request_id)
        response = self.engine.execute(req)
        if (type(response) is not AIResponse or response.status != "completed" or response.error
                or (response.provider, response.task_id, response.prompt_id, response.prompt_version)
                != (req.provider, req.task_id, req.prompt_id, req.prompt_version)):
            raise ValueError("semantic provider failed/response binding mismatch")
        output = parse_semantics(response.content, request, self.plan)
        self.content = response.content
        return output
