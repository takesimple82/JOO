from InvestmentDecisionVerticalSlice.models import CioActionPosture, CioDecisionRecord, ComparisonStatus, ThesisState
from InvestmentDecisionVerticalSlice.validation import nonblank, unique_ids, validate_cio_decision


def synthesize_cio_decision(*, decision_id, snapshot_id, bundle, output, transitions, impacts, ev_records, comparisons, what_changed, why_it_matters, narrative_reference_ids):
    nonblank("decision_id", decision_id); nonblank("what_changed", what_changed); nonblank("why_it_matters", why_it_matters)
    unresolved = []
    if not bundle.fresh: unresolved.append("STALE_EVIDENCE")
    if set(bundle.required_committees) != set(bundle.completed_committees): unresolved.append("MISSING_COMMITTEE")
    if bundle.unresolved_contradiction_ids: unresolved.append("UNRESOLVED_CONTRADICTION")
    if output.uncertainty_status.value != "COMPLETE": unresolved.append(output.uncertainty_status.value)
    if any(x.status in (ComparisonStatus.INCOMPARABLE, ComparisonStatus.UNRESOLVED) for x in comparisons): unresolved.append("OPPORTUNITY_NOT_COMPARABLE")
    superior = None
    if unresolved:
        posture = CioActionPosture.NO_ACTION_UNRESOLVED
    elif any(x.state is ThesisState.INVALIDATED for x in transitions):
        posture = CioActionPosture.INVALIDATE_THESIS
    else:
        for comparison in comparisons:
            if comparison.status is ComparisonStatus.RIGHT_SUPERIOR and comparison.right.role.value == "CANDIDATE":
                superior = comparison.right.opportunity_id
            if comparison.status is ComparisonStatus.LEFT_SUPERIOR and comparison.left.role.value == "CANDIDATE":
                superior = comparison.left.opportunity_id
        posture = CioActionPosture.CONSIDER_ROTATION if superior else CioActionPosture.MAINTAIN
    unique_ids("narrative_reference_ids", narrative_reference_ids)
    allowed = {x.evidence_id for x in bundle.evidence} | {output.output_id} | {x.transition_id for x in transitions} | {x.record_id for x in impacts} | {x.record_id for x in ev_records} | {x.comparison_id for x in comparisons}
    if not set(narrative_reference_ids).issubset(allowed):
        raise ValueError("CIO narrative reference not allowlisted")
    decision = CioDecisionRecord(
        decision_id, snapshot_id, bundle.bundle_id, output.output_id,
        tuple(x.transition_id for x in transitions), tuple(x.record_id for x in impacts),
        tuple(x.record_id for x in ev_records), tuple(x.comparison_id for x in comparisons),
        tuple(dict.fromkeys(x.left.horizon_id for x in comparisons)), posture,
        what_changed, why_it_matters, superior, tuple(unresolved), narrative_reference_ids, False,
    )
    validate_cio_decision(decision)
    return decision
