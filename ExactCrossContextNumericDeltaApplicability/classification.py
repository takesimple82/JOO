from typing import Optional

from BaselineCurrentPropositionPair.models import (
    ExplicitBaselineCurrentPropositionPair,
)
from BaselineCurrentPropositionPair.validation import (
    validate_explicit_baseline_current_proposition_pair,
)
from BaselineCurrentPropositionPairApplicability.classification import (
    _classify_baseline_current_proposition_pair_applicability_unchecked,
)
from BaselineCurrentPropositionPairApplicability.models import (
    BaselineCurrentPropositionPairApplicabilityStatus,
)
from CrossContextPropositionCompatibility.classification import (
    _classify_cross_context_proposition_compatibility_unchecked,
)
from CrossContextPropositionCompatibility.models import (
    CrossContextPropositionCompatibilityStatus,
)
from EffectiveContextObservedDate.models import (
    ExplicitEffectiveContextObservedDate,
)
from EffectiveContextObservedDate.validation import (
    validate_explicit_effective_context_observed_date,
)
from EffectiveContextTemporalOrdering.models import (
    _classify_effective_context_temporal_ordering_unchecked,
)
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from ExactCrossContextNumericDeltaApplicability.models import (
    ExactCrossContextNumericDeltaApplicabilityStatus,
)
from SemanticPropositionProduction.models import (
    SemanticallyProducedNumericProposition,
)
from SemanticPropositionProduction.validation import (
    validate_semantically_produced_numeric_proposition,
)


def classify_exact_cross_context_numeric_delta_applicability(
    pair: ExplicitBaselineCurrentPropositionPair,
    baseline: SemanticallyProducedNumericProposition,
    current: SemanticallyProducedNumericProposition,
    baseline_context_date: ExplicitEffectiveContextObservedDate,
    current_context_date: ExplicitEffectiveContextObservedDate,
) -> ExactCrossContextNumericDeltaApplicabilityStatus:
    validate_explicit_baseline_current_proposition_pair(pair)
    validate_semantically_produced_numeric_proposition(baseline)
    validate_semantically_produced_numeric_proposition(current)
    validate_explicit_effective_context_observed_date(
        baseline_context_date
    )
    validate_explicit_effective_context_observed_date(
        current_context_date
    )

    pair_status = (
        _classify_baseline_current_proposition_pair_applicability_unchecked(
            pair,
            baseline.proposition,
            current.proposition,
            baseline_context_date,
            current_context_date,
            _classify_effective_context_temporal_ordering_unchecked,
        )
    )
    mapped_pair_status = _map_pair_status(pair_status)
    if mapped_pair_status is not None:
        return mapped_pair_status

    compatibility_status = (
        _classify_cross_context_proposition_compatibility_unchecked(
            baseline,
            current,
        )
    )
    return _map_compatibility_status(compatibility_status)


def _map_pair_status(
    status: BaselineCurrentPropositionPairApplicabilityStatus,
) -> Optional[
    ExactCrossContextNumericDeltaApplicabilityStatus
]:
    mappings = {
        (
            BaselineCurrentPropositionPairApplicabilityStatus
            .BASELINE_PROPOSITION_ENDPOINT_MISMATCH
        ): (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .BASELINE_PROPOSITION_ENDPOINT_MISMATCH
        ),
        (
            BaselineCurrentPropositionPairApplicabilityStatus
            .CURRENT_PROPOSITION_ENDPOINT_MISMATCH
        ): (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CURRENT_PROPOSITION_ENDPOINT_MISMATCH
        ),
        (
            BaselineCurrentPropositionPairApplicabilityStatus
            .BASELINE_CONTEXT_ENDPOINT_MISMATCH
        ): (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .BASELINE_CONTEXT_ENDPOINT_MISMATCH
        ),
        (
            BaselineCurrentPropositionPairApplicabilityStatus
            .CURRENT_CONTEXT_ENDPOINT_MISMATCH
        ): (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CURRENT_CONTEXT_ENDPOINT_MISMATCH
        ),
        (
            BaselineCurrentPropositionPairApplicabilityStatus
            .CONTEXT_DATE_CONFLICT
        ): (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CONTEXT_DATE_CONFLICT
        ),
        BaselineCurrentPropositionPairApplicabilityStatus.SAME_DATE: (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .SAME_DATE
        ),
        (
            BaselineCurrentPropositionPairApplicabilityStatus
            .BASELINE_AFTER_CURRENT
        ): (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .BASELINE_AFTER_CURRENT
        ),
        BaselineCurrentPropositionPairApplicabilityStatus.APPLICABLE: (
            None
        ),
    }
    try:
        return mappings[status]
    except KeyError as error:
        raise RuntimeError(
            "unsupported baseline/current pair applicability status"
        ) from error


def _map_compatibility_status(
    status: CrossContextPropositionCompatibilityStatus,
) -> ExactCrossContextNumericDeltaApplicabilityStatus:
    mappings = {
        CrossContextPropositionCompatibilityStatus.SUBJECT_MISMATCH: (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .SUBJECT_MISMATCH
        ),
        CrossContextPropositionCompatibilityStatus.PREDICATE_MISMATCH: (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .PREDICATE_MISMATCH
        ),
        CrossContextPropositionCompatibilityStatus.UNIT_MISMATCH: (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .UNIT_MISMATCH
        ),
        CrossContextPropositionCompatibilityStatus.COMPATIBLE: (
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CALCULABLE
        ),
    }
    try:
        return mappings[status]
    except KeyError as error:
        raise RuntimeError(
            "unsupported cross-context compatibility status"
        ) from error
