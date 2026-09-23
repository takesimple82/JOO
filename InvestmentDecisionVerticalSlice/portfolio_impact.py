from PortfolioImpactApplicability.classification import classify_portfolio_impact_applicability
from PortfolioImpactApplicability.models import PortfolioImpactApplicabilityStatus
from PortfolioImpactInterpretationPolicy.classification import classify_portfolio_impact_interpretation_policy_applicability
from PortfolioImpactInterpretationPolicy.models import PortfolioImpactInterpretationPolicyApplicabilityStatus
from InvestmentDecisionVerticalSlice.models import PortfolioImpactRecord


def admit_portfolio_impact(*, record_id, snapshot, transition, output):
    impact = output.impact
    if classify_portfolio_impact_applicability(impact.semantic_thesis, impact.link, impact.portfolio_subject) is not PortfolioImpactApplicabilityStatus.APPLICABLE:
        raise ValueError("portfolio impact endpoint mismatch")
    if classify_portfolio_impact_interpretation_policy_applicability(impact.policy, impact.direction, impact.horizon_id, impact.rationale) is not PortfolioImpactInterpretationPolicyApplicabilityStatus.APPLICABLE:
        raise ValueError("portfolio impact policy rejected")
    if transition.current_thesis_id != impact.semantic_thesis.thesis.thesis_id:
        raise ValueError("portfolio impact thesis mismatch")
    current = any(x.position.membership.portfolio_subject_id == impact.portfolio_subject.subject_id for x in snapshot.holding_snapshot.holding_observations)
    signals = tuple(x.signal_id for x in output.qualitative_signals) + output.consumed_numeric_signal_ids
    return PortfolioImpactRecord(record_id, snapshot.portfolio_snapshot_id, current, transition.transition_id, output.consumed_evidence_ids, signals, output.output_id, output.uncertainty_status, impact)
