from EffectiveContextObservedDate.models import (
    ExplicitEffectiveContextObservedDate,
)
from EffectiveContextObservedDate.validation import (
    validate_explicit_effective_context_observed_date,
)
from EffectiveContextTemporalOrdering.models import (
    EffectiveContextTemporalOrderingStatus,
    _classify_effective_context_temporal_ordering_unchecked,
)


def classify_effective_context_temporal_ordering(
    left: ExplicitEffectiveContextObservedDate,
    right: ExplicitEffectiveContextObservedDate,
) -> EffectiveContextTemporalOrderingStatus:
    validate_explicit_effective_context_observed_date(left)
    validate_explicit_effective_context_observed_date(right)

    return _classify_effective_context_temporal_ordering_unchecked(
        left,
        right,
    )
