from BaselineCurrentPropositionPair.models import (
    ExplicitBaselineCurrentPropositionPair,
)
from BaselineCurrentPropositionPair.validation import (
    validate_explicit_baseline_current_proposition_pair,
)
from BaselineCurrentPropositionPairApplicability.models import (
    BaselineCurrentPropositionPairApplicabilityStatus,
)
from EffectiveContextObservedDate.models import (
    ExplicitEffectiveContextObservedDate,
)
from EffectiveContextObservedDate.validation import (
    validate_explicit_effective_context_observed_date,
)
from EffectiveContextTemporalOrdering.classification import (
    classify_effective_context_temporal_ordering,
)
from EffectiveContextTemporalOrdering.models import (
    EffectiveContextTemporalOrderingStatus,
)
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from EvidenceProposition.validation import (
    validate_exact_observed_numeric_proposition,
)


def classify_baseline_current_proposition_pair_applicability(
    pair: ExplicitBaselineCurrentPropositionPair,
    baseline: ExactObservedNumericProposition,
    current: ExactObservedNumericProposition,
    baseline_context_date: ExplicitEffectiveContextObservedDate,
    current_context_date: ExplicitEffectiveContextObservedDate,
) -> BaselineCurrentPropositionPairApplicabilityStatus:
    validate_explicit_baseline_current_proposition_pair(pair)
    validate_exact_observed_numeric_proposition(baseline)
    validate_exact_observed_numeric_proposition(current)
    validate_explicit_effective_context_observed_date(
        baseline_context_date
    )
    validate_explicit_effective_context_observed_date(
        current_context_date
    )

    return (
        _classify_baseline_current_proposition_pair_applicability_unchecked(
            pair,
            baseline,
            current,
            baseline_context_date,
            current_context_date,
            classify_effective_context_temporal_ordering,
        )
    )


def _classify_baseline_current_proposition_pair_applicability_unchecked(
    pair: ExplicitBaselineCurrentPropositionPair,
    baseline: ExactObservedNumericProposition,
    current: ExactObservedNumericProposition,
    baseline_context_date: ExplicitEffectiveContextObservedDate,
    current_context_date: ExplicitEffectiveContextObservedDate,
    temporal_classifier,
) -> BaselineCurrentPropositionPairApplicabilityStatus:
    if pair.baseline_proposition_id != baseline.proposition_id:
        return (
            BaselineCurrentPropositionPairApplicabilityStatus
            .BASELINE_PROPOSITION_ENDPOINT_MISMATCH
        )
    if pair.current_proposition_id != current.proposition_id:
        return (
            BaselineCurrentPropositionPairApplicabilityStatus
            .CURRENT_PROPOSITION_ENDPOINT_MISMATCH
        )
    if (
        baseline.effective_context_id
        != baseline_context_date.effective_context_id
    ):
        return (
            BaselineCurrentPropositionPairApplicabilityStatus
            .BASELINE_CONTEXT_ENDPOINT_MISMATCH
        )
    if (
        current.effective_context_id
        != current_context_date.effective_context_id
    ):
        return (
            BaselineCurrentPropositionPairApplicabilityStatus
            .CURRENT_CONTEXT_ENDPOINT_MISMATCH
        )

    temporal_status = temporal_classifier(
        baseline_context_date,
        current_context_date,
    )
    if temporal_status is EffectiveContextTemporalOrderingStatus.BEFORE:
        return (
            BaselineCurrentPropositionPairApplicabilityStatus
            .APPLICABLE
        )
    if temporal_status is EffectiveContextTemporalOrderingStatus.SAME_DATE:
        return (
            BaselineCurrentPropositionPairApplicabilityStatus
            .SAME_DATE
        )
    if temporal_status is EffectiveContextTemporalOrderingStatus.AFTER:
        return (
            BaselineCurrentPropositionPairApplicabilityStatus
            .BASELINE_AFTER_CURRENT
        )
    return (
        BaselineCurrentPropositionPairApplicabilityStatus
        .CONTEXT_DATE_CONFLICT
    )
