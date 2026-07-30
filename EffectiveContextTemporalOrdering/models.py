from enum import Enum


class EffectiveContextTemporalOrderingStatus(Enum):
    CONTEXT_DATE_CONFLICT = "context_date_conflict"
    BEFORE = "before"
    SAME_DATE = "same_date"
    AFTER = "after"


def _classify_effective_context_temporal_ordering_unchecked(
    left,
    right,
) -> EffectiveContextTemporalOrderingStatus:
    if (
        left.effective_context_id
        == right.effective_context_id
        and left.observed_on != right.observed_on
    ):
        return (
            EffectiveContextTemporalOrderingStatus
            .CONTEXT_DATE_CONFLICT
        )
    if left.observed_on < right.observed_on:
        return EffectiveContextTemporalOrderingStatus.BEFORE
    if left.observed_on == right.observed_on:
        return EffectiveContextTemporalOrderingStatus.SAME_DATE
    return EffectiveContextTemporalOrderingStatus.AFTER
