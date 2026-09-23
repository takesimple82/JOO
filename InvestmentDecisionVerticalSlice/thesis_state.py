from datetime import datetime
from InvestmentDecisionVerticalSlice.models import ThesisTransition
from InvestmentDecisionVerticalSlice.validation import validate_thesis_transition


def make_thesis_transition(*, transition_id, portfolio_subject_id, prior_thesis_id, output, effective_at: datetime):
    signals = tuple(x.signal_id for x in output.qualitative_signals) + output.consumed_numeric_signal_ids
    transition = ThesisTransition(
        transition_id, portfolio_subject_id, prior_thesis_id,
        output.thesis.thesis.thesis_id, output.thesis_state,
        output.consumed_evidence_ids, signals, output.output_id, effective_at,
    )
    validate_thesis_transition(transition)
    return transition
