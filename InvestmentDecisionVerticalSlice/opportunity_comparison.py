from InvestmentDecisionVerticalSlice.models import ComparisonStatus, OpportunityComparison
from InvestmentDecisionVerticalSlice.validation import nonblank


def compare_opportunities(comparison_id, left, right):
    nonblank("comparison_id", comparison_id)
    comparable = (
        left.comparison_policy_id == right.comparison_policy_id
        and left.probability_policy_version == right.probability_policy_version
        and left.horizon_id == right.horizon_id
        and left.unit_id == right.unit_id
    )
    if not comparable:
        status = ComparisonStatus.INCOMPARABLE
    elif left.ev_record is None or right.ev_record is None:
        status = ComparisonStatus.UNRESOLVED
    else:
        lcalc, rcalc = left.ev_record.calculation, right.ev_record.calculation
        if lcalc.expected_value is None or rcalc.expected_value is None:
            status = ComparisonStatus.UNRESOLVED
        elif lcalc.expected_value.value > rcalc.expected_value.value:
            status = ComparisonStatus.LEFT_SUPERIOR
        elif lcalc.expected_value.value < rcalc.expected_value.value:
            status = ComparisonStatus.RIGHT_SUPERIOR
        else:
            status = ComparisonStatus.EQUAL
    return OpportunityComparison(comparison_id, left, right, status)


def replay_comparison(record):
    replayed = compare_opportunities(record.comparison_id, record.left, record.right)
    if replayed != record:
        raise ValueError("deterministic comparison replay mismatch")
    return replayed
