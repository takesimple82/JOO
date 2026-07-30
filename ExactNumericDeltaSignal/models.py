from dataclasses import dataclass
from enum import Enum

from ExactCrossContextNumericDelta.models import (
    ExactCrossContextNumericDelta,
)
from ExactCrossContextNumericDeltaDirection.models import (
    ExactCrossContextNumericDeltaDirectionStatus,
)
from ExactNumericDeltaMateriality.models import (
    ExactNumericDeltaMaterialityPolicy,
    ExactNumericDeltaMaterialityStatus,
)


class ExactNumericDeltaSignalStatus(Enum):
    UNIT_MISMATCH = "unit_mismatch"
    NO_CHANGE = "no_change"
    IMMATERIAL_INCREASE = "immaterial_increase"
    IMMATERIAL_DECREASE = "immaterial_decrease"
    MATERIAL_INCREASE = "material_increase"
    MATERIAL_DECREASE = "material_decrease"


@dataclass(frozen=True)
class ExactNumericDeltaSignalClassification:
    delta: ExactCrossContextNumericDelta
    policy: ExactNumericDeltaMaterialityPolicy
    direction_status: ExactCrossContextNumericDeltaDirectionStatus
    materiality_status: ExactNumericDeltaMaterialityStatus
    signal_status: ExactNumericDeltaSignalStatus
