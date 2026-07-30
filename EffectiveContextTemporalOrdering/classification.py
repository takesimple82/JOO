from EffectiveContextObservedDate.models import (
    ExplicitEffectiveContextObservedDate,
)
from EffectiveContextObservedDate.validation import (
    validate_explicit_effective_context_observed_date,
)
from EffectiveContextTemporalOrdering.models import (
    EffectiveContextTemporalOrderingStatus,
)


def classify_effective_context_temporal_ordering(
    left: ExplicitEffectiveContextObservedDate,
    right: ExplicitEffectiveContextObservedDate,
) -> EffectiveContextTemporalOrderingStatus:
    validate_explicit_effective_context_observed_date(left)
    validate_explicit_effective_context_observed_date(right)

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
