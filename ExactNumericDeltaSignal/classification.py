from ExactCrossContextNumericDelta.models import (
    ExactCrossContextNumericDelta,
)
from ExactCrossContextNumericDelta.validation import (
    validate_exact_cross_context_numeric_delta,
)
from ExactCrossContextNumericDeltaDirection.classification import (
    _classify_exact_cross_context_numeric_delta_direction_unchecked,
)
from ExactCrossContextNumericDeltaDirection.models import (
    ExactCrossContextNumericDeltaDirectionStatus,
)
from ExactNumericDeltaMateriality.classification import (
    _classify_exact_numeric_delta_materiality_unchecked,
)
from ExactNumericDeltaMateriality.models import (
    ExactNumericDeltaMaterialityPolicy,
    ExactNumericDeltaMaterialityStatus,
)
from ExactNumericDeltaMateriality.validation import (
    validate_exact_numeric_delta_materiality_policy,
)
from ExactNumericDeltaSignal.models import (
    ExactNumericDeltaSignalClassification,
    ExactNumericDeltaSignalStatus,
)


def classify_exact_numeric_delta_signal(
    delta: ExactCrossContextNumericDelta,
    policy: ExactNumericDeltaMaterialityPolicy,
) -> ExactNumericDeltaSignalClassification:
    validate_exact_cross_context_numeric_delta(delta)
    validate_exact_numeric_delta_materiality_policy(policy)

    direction_status = (
        _classify_exact_cross_context_numeric_delta_direction_unchecked(
            delta
        )
    )
    materiality_status = (
        _classify_exact_numeric_delta_materiality_unchecked(
            delta,
            policy,
        )
    )
    signal_status = _map_signal_status(
        direction_status,
        materiality_status,
    )
    return ExactNumericDeltaSignalClassification(
        delta=delta,
        policy=policy,
        direction_status=direction_status,
        materiality_status=materiality_status,
        signal_status=signal_status,
    )


def _map_signal_status(
    direction_status: ExactCrossContextNumericDeltaDirectionStatus,
    materiality_status: ExactNumericDeltaMaterialityStatus,
) -> ExactNumericDeltaSignalStatus:
    if (
        materiality_status
        is ExactNumericDeltaMaterialityStatus.UNIT_MISMATCH
    ):
        return ExactNumericDeltaSignalStatus.UNIT_MISMATCH

    mappings = {
        (
            ExactCrossContextNumericDeltaDirectionStatus.ZERO,
            ExactNumericDeltaMaterialityStatus.IMMATERIAL,
        ): ExactNumericDeltaSignalStatus.NO_CHANGE,
        (
            ExactCrossContextNumericDeltaDirectionStatus.POSITIVE,
            ExactNumericDeltaMaterialityStatus.IMMATERIAL,
        ): ExactNumericDeltaSignalStatus.IMMATERIAL_INCREASE,
        (
            ExactCrossContextNumericDeltaDirectionStatus.NEGATIVE,
            ExactNumericDeltaMaterialityStatus.IMMATERIAL,
        ): ExactNumericDeltaSignalStatus.IMMATERIAL_DECREASE,
        (
            ExactCrossContextNumericDeltaDirectionStatus.POSITIVE,
            ExactNumericDeltaMaterialityStatus.MATERIAL,
        ): ExactNumericDeltaSignalStatus.MATERIAL_INCREASE,
        (
            ExactCrossContextNumericDeltaDirectionStatus.NEGATIVE,
            ExactNumericDeltaMaterialityStatus.MATERIAL,
        ): ExactNumericDeltaSignalStatus.MATERIAL_DECREASE,
    }
    try:
        return mappings[
            (direction_status, materiality_status)
        ]
    except KeyError as error:
        raise RuntimeError(
            "unsupported numeric delta signal classification"
        ) from error
