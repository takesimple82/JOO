from BaselineCurrentPropositionPair.models import (
    ExplicitBaselineCurrentPropositionPair,
)
from EffectiveContextObservedDate.models import (
    ExplicitEffectiveContextObservedDate,
)
from ExactCrossContextNumericDelta.models import (
    ExactCrossContextNumericDelta,
    ExactCrossContextNumericDeltaCalculation,
)
from ExactCrossContextNumericDeltaApplicability.classification import (
    classify_exact_cross_context_numeric_delta_applicability,
)
from ExactCrossContextNumericDeltaApplicability.models import (
    ExactCrossContextNumericDeltaApplicabilityStatus,
)
from ExactDecimalArithmetic.arithmetic import (
    subtract_exact_decimal,
)
from SemanticPropositionProduction.models import (
    SemanticallyProducedNumericProposition,
)


def calculate_exact_cross_context_numeric_delta(
    pair: ExplicitBaselineCurrentPropositionPair,
    baseline: SemanticallyProducedNumericProposition,
    current: SemanticallyProducedNumericProposition,
    baseline_context_date: ExplicitEffectiveContextObservedDate,
    current_context_date: ExplicitEffectiveContextObservedDate,
) -> ExactCrossContextNumericDeltaCalculation:
    applicability_status = (
        classify_exact_cross_context_numeric_delta_applicability(
            pair,
            baseline,
            current,
            baseline_context_date,
            current_context_date,
        )
    )
    if (
        applicability_status
        is not ExactCrossContextNumericDeltaApplicabilityStatus.CALCULABLE
    ):
        return ExactCrossContextNumericDeltaCalculation(
            applicability_status=applicability_status,
            delta=None,
        )

    value = subtract_exact_decimal(
        current.proposition.value,
        baseline.proposition.value,
    )
    delta = ExactCrossContextNumericDelta(
        baseline_proposition_id=pair.baseline_proposition_id,
        current_proposition_id=pair.current_proposition_id,
        unit_id=baseline.proposition.unit_id,
        value=value,
    )
    return ExactCrossContextNumericDeltaCalculation(
        applicability_status=applicability_status,
        delta=delta,
    )
