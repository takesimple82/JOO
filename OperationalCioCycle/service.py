"""One ordinary application composition. No scheduler, allocation or execution."""
from dataclasses import replace
from datetime import datetime, timezone
from itertools import combinations

from FactStore.sqlite_storage import SQLiteAppendOnlyFactEngine
from FactStore.validation.validators import verify_stored_fact_integrity
from InvestmentResearchOrchestrator.run_coordinator import RunCoordinator
from InvestmentResearchOrchestrator.evidence_store import EvidenceStore
from InvestmentResearchOrchestrator.models.plan import ExplicitResearchCandidate
from InvestmentResearchOrchestrator.models.enums import EvidencePayloadKind
from KbPortfolioVerticalSlice.service import run_kb_portfolio_vertical_slice
from InvestmentDecisionVerticalSlice.models import (
    SemanticProductionRequest, EvAssumptionProvenance, OpportunityEvaluation,
    OpportunityRole, JournalAppend, JournalRecordKind, CioActionPosture,
)
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal
from InvestmentDecisionVerticalSlice.semantic_admission import produce_and_admit_semantics
from InvestmentDecisionVerticalSlice.thesis_state import make_thesis_transition
from InvestmentDecisionVerticalSlice.portfolio_impact import admit_portfolio_impact
from InvestmentDecisionVerticalSlice.ev_integration import calculate_admitted_ev
from InvestmentDecisionVerticalSlice.opportunity_comparison import compare_opportunities
from InvestmentDecisionVerticalSlice.cio_synthesis import synthesize_cio_decision
from OperationalCioCycle.models import CycleResult, CandidateAdmission
from OperationalCioCycle.universe import build_universe, validate_config, utc
from OperationalCioCycle.evidence import admit_first, subject_bundle
from OperationalCioCycle.semantic import ProviderSemanticProducer, parse_semantics, validate_plan, strict_json
from InvestmentDecisionVerticalSlice.validation import validate_cio_decision, nonblank
from OperationalCioCycle.codec import encode, decode


def _derive(inputs, providers=None, stored_contents=None):
    config, first, records, now, subjects, admissions, plans, raw, normalized, prior, provider_bindings = inputs
    validate_config(config)
    for fact in (raw,) + normalized:
        verify_stored_fact_integrity(fact)
    admit_first(config, first, records, now, raw, normalized, prior)
    universe = build_universe(config, first.snapshot, subjects, admissions, now)
    scope_records = [strict_json(r.payload) for r in records if r.payload_kind is EvidencePayloadKind.DECISION_RESEARCH_ADMISSION]
    expected_scope = {"snapshot_id": config.snapshot_id,
        "holding_subject_ids": [x.position.membership.portfolio_subject_id for x in first.snapshot.holding_snapshot.holding_observations],
        "candidates": [{"subject_id": x.subject.subject_id, "admission_id": x.admission_id, "provenance": x.provenance} for x in admissions]}
    if scope_records != [expected_scope]:
        raise ValueError("IRO research admission/universe provenance mismatch")
    eligible = tuple(x for x in universe.members if x.eligible)
    if type(plans) is not tuple or len(plans) != len(eligible):
        raise ValueError("exact eligible subject plans required")
    for plan in plans:
        validate_plan(plan)
    by_subject = {x.subject.subject_id: x for x in plans}
    if len(by_subject) != len(plans) or set(by_subject) != {x.subject.subject_id for x in eligible}:
        raise ValueError("ineligible/outside/duplicate subject plan")
    if stored_contents is not None and (type(stored_contents) is not tuple or len(stored_contents) != len(eligible)):
        raise ValueError("stored semantic coverage mismatch")
    contents, artifacts, evaluations = [], [], []
    for index, member in enumerate(eligible):
        plan = by_subject[member.subject.subject_id]
        if plan.subject != member.subject:
            raise ValueError("plan subject identity drift")
        bundle = subject_bundle(config, first, records, member, provider_bindings)
        prefix = f"{config.cycle_id}:subject:{member.subject.subject_id}"
        request = SemanticProductionRequest(prefix, bundle, tuple(x.evidence_id for x in bundle.evidence), plan.numeric_signals, (plan.horizon_id,))
        if stored_contents is None:
            producer = ProviderSemanticProducer(providers, plan)
            output = produce_and_admit_semantics(producer, request)
            content = producer.content
        else:
            content = stored_contents[index]
            output = parse_semantics(content, request, plan)
        transition = make_thesis_transition(transition_id=prefix + ":transition", portfolio_subject_id=member.subject.subject_id,
            prior_thesis_id=plan.prior_thesis_id, output=output, effective_at=now)
        impact = admit_portfolio_impact(record_id=prefix + ":impact-record", snapshot=first.snapshot, transition=transition, output=output)
        source = EvAssumptionProvenance(prefix + ":ev-source", output.assumption_set, plan.horizon_id, output.consumed_evidence_ids,
            transition.transition_id, impact.record_id, output.output_id, output.provenance, output.uncertainty_status)
        ev = calculate_admitted_ev(prefix + ":ev", source)
        if ev.calculation.expected_value is None:
            raise ValueError("Exact EV unavailable")
        evaluation = OpportunityEvaluation(prefix + ":opportunity", member.subject.subject_id,
            OpportunityRole.CURRENT_HOLDING if "holding" in member.sources else OpportunityRole.CANDIDATE,
            config.comparison_policy_id, output.provenance.policy_version, plan.horizon_id, plan.unit_id, ev)
        contents.append(content)
        artifacts.append((request, output, transition, impact, ev))
        evaluations.append(evaluation)
    comparisons = tuple(compare_opportunities(f"{config.cycle_id}:comparison:{i}", a, b)
        for i, (a, b) in enumerate(combinations(evaluations, 2)))
    # Each compatibility plane gets its own decision; there is no cross-plane ranking.
    planes = {}
    for i, value in enumerate(evaluations):
        key = (value.horizon_id, value.unit_id, value.probability_policy_version, value.comparison_policy_id)
        planes.setdefault(key, []).append(i)
    decisions = []
    for index, indices in enumerate(planes.values()):
        group = [evaluations[i] for i in indices]
        items = [artifacts[i] for i in indices]
        bundle = replace(items[0][0].bundle, bundle_id=f"{config.cycle_id}:plane:{index}:bundle",
            evidence=tuple(e for a in items for e in a[0].bundle.evidence),
            required_committees=tuple(dict.fromkeys(c for a in items for c in a[0].bundle.required_committees)),
            completed_committees=tuple(dict.fromkeys(c for a in items for c in a[0].bundle.completed_committees)))
        ids = {x.opportunity_id for x in group}
        compatible = tuple(c for c in comparisons if c.left.opportunity_id in ids and c.right.opportunity_id in ids)
        decision = synthesize_cio_decision(decision_id=f"{config.cycle_id}:decision:{index}", snapshot_id=config.snapshot_id,
            bundle=bundle, output=items[0][1], transitions=tuple(a[2] for a in items), impacts=tuple(a[3] for a in items),
            ev_records=tuple(a[4] for a in items), comparisons=compatible,
            what_changed=" | ".join(a[1].qualitative_signals[0].material_change_statement for a in items),
            why_it_matters=" | ".join(a[1].impact.rationale for a in items), narrative_reference_ids=tuple(e.evidence_id for e in bundle.evidence))
        best_value = max(x.ev_record.calculation.expected_value.value for x in group)
        winners = [x for x in group if x.ev_record.calculation.expected_value.value == best_value]
        holdings = [x for x in group if x.role is OpportunityRole.CURRENT_HOLDING]
        candidates = [x for x in winners if x.role is OpportunityRole.CANDIDATE]
        # Never let the existing pair-wise synthesizer pick the last candidate.
        if len(winners) == 1 and candidates and holdings and all(best_value > x.ev_record.calculation.expected_value.value for x in holdings):
            decision = replace(decision, superior_opportunity_id=winners[0].opportunity_id, posture=CioActionPosture.CONSIDER_ROTATION)
        elif len(candidates) > 1 and holdings and all(best_value > x.ev_record.calculation.expected_value.value for x in holdings):
            decision = replace(decision, superior_opportunity_id=None, posture=CioActionPosture.NO_ACTION_UNRESOLVED,
                unresolved_reasons=("AMBIGUOUS_TOP_OPPORTUNITY",))
        else:
            decision = replace(decision, superior_opportunity_id=None, posture=CioActionPosture.MAINTAIN)
        decision = replace(decision, horizon_ids=(group[0].horizon_id,), semantic_output_ids=tuple(a[1].output_id for a in items))
        validate_cio_decision(decision)
        decisions.append(decision)
    result = CycleResult(config.cycle_id, universe, tuple(evaluations), comparisons, tuple(decisions), config.cycle_id + ":completed")
    return result, tuple(contents), tuple(artifacts)


def run_operational_cio_cycle(*, config, first_slice_arguments, subjects, admissions, plans, providers, journal, clock=lambda: datetime.now(timezone.utc)):
    validate_config(config)
    if type(journal) is not DecisionJournal or type(first_slice_arguments) is not dict:
        raise TypeError("DecisionJournal and explicit First Slice arguments required")
    if journal.journal_identity != config.journal_id:
        raise ValueError("physical journal identity mismatch")
    prior_records = journal.list_records()
    if any(x.record_id == config.cycle_id + ":completed" for x in prior_records):
        raise ValueError("cycle already completed; use replay without external calls")
    arguments = dict(first_slice_arguments)
    if type(admissions) is not tuple or type(subjects) is not tuple or type(plans) is not tuple:
        raise TypeError("immutable tuple cycle inputs required")
    declared = {x.subject_id: x for x in subjects}
    if len(declared) != len(subjects):
        raise ValueError("duplicate subject identity")
    candidate_ids, admission_ids = set(), set()
    for candidate in admissions:
        if type(candidate) is not CandidateAdmission or declared.get(candidate.subject.subject_id) != candidate.subject:
            raise ValueError("explicit candidate identity required")
        nonblank("admission ID", candidate.admission_id)
        nonblank("admission provenance", candidate.provenance)
        if candidate.subject.subject_id in candidate_ids or candidate.admission_id in admission_ids:
            raise ValueError("duplicate candidate admission")
        candidate_ids.add(candidate.subject.subject_id)
        admission_ids.add(candidate.admission_id)
    run_arguments = dict(arguments["iro_run_arguments"])
    if "decision_candidates" in run_arguments:
        raise ValueError("candidate authority belongs to cycle admissions only")
    run_arguments["decision_candidates"] = tuple(ExplicitResearchCandidate(x.subject.subject_id, x.admission_id, x.provenance) for x in admissions)
    arguments["iro_run_arguments"] = run_arguments
    coordinator = arguments.get("coordinator")
    if type(coordinator) is not RunCoordinator or type(coordinator._store) is not EvidenceStore:
        raise TypeError("real IRO RunCoordinator/EvidenceStore required")
    store = arguments["fact_store"]
    if type(store._engine) is not SQLiteAppendOnlyFactEngine:
        raise ValueError("durable FactStore required")
    if arguments["policy"].freshness_max_age != config.freshness_max_age:
        raise ValueError("First Slice/cycle freshness policy mismatch")
    if arguments["snapshot_identity"].portfolio_snapshot_id != config.snapshot_id or arguments["run"].run_id != config.iro_run_id:
        raise ValueError("First Slice/cycle identity mismatch")
    if coordinator._store.list_for_run(config.iro_run_id):
        raise ValueError("IRO run identity already used")
    first = run_kb_portfolio_vertical_slice(**arguments)
    if first.ingress is None:
        raise ValueError("first slice failed/no-change; no CIO wake")
    raw = store.get_by_fact_id(first.ingress.raw_fact_id)
    normalized = tuple(store.get_by_fact_id(x) for x in first.ingress.normalized_fact_ids)
    records = coordinator._store.list_for_run(config.iro_run_id)
    now = clock()
    utc(now)
    inputs = (config, first, records, now, subjects, admissions, plans, raw, normalized, arguments["prior_snapshot"], dict(arguments["iro_run_arguments"]["provider_by_committee"]))
    result, contents, artifacts = _derive(inputs, providers)
    # Provider latency must not turn a fresh admission into a stale decision.
    finished = clock()
    utc(finished)
    if finished < now or finished - first.ingress.collected_at > config.freshness_max_age:
        raise ValueError("snapshot expired during semantic production")
    payload = {"version": 1, "inputs": encode(inputs), "contents": encode(contents), "artifacts": encode(artifacts), "result": encode(result), "finished_at": encode(finished)}
    journal.append_batch((JournalAppend(result.journal_record_id, JournalRecordKind.OPERATIONAL_CIO_CYCLE, finished, payload),))
    return result


def replay_cycle(journal, cycle_id, journal_id):
    if type(journal) is not DecisionJournal:
        raise TypeError("DecisionJournal required")
    if journal.journal_identity != journal_id:
        raise ValueError("physical journal identity mismatch")
    records = [r for r in journal.list_records() if r.record_id == cycle_id + ":completed"]
    if len(records) != 1 or records[0].kind is not JournalRecordKind.OPERATIONAL_CIO_CYCLE:
        raise ValueError("completed cycle missing")
    record = records[0]
    payload = record.payload
    if set(payload) != {"version", "inputs", "contents", "artifacts", "result", "finished_at"} or type(payload["version"]) is not int or payload["version"] != 1:
        raise ValueError("cycle journal schema mismatch")
    inputs, contents = decode(payload["inputs"]), decode(payload["contents"])
    if type(inputs) is not tuple or len(inputs) != 11 or inputs[0].cycle_id != cycle_id or inputs[0].journal_id != journal_id:
        raise ValueError("cycle/journal identity mismatch")
    finished = decode(payload["finished_at"])
    utc(finished)
    if finished != record.created_at or finished < inputs[3] or finished - inputs[1].ingress.collected_at > inputs[0].freshness_max_age:
        raise ValueError("cycle persistence freshness mismatch")
    result, _, artifacts = _derive(inputs, stored_contents=contents)
    if encode(result) != payload["result"] or encode(artifacts) != payload["artifacts"]:
        raise ValueError("deterministic cycle replay mismatch")
    return result
