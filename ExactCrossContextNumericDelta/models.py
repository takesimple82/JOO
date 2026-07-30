from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from ExactCrossContextNumericDeltaApplicability.models import (
    ExactCrossContextNumericDeltaApplicabilityStatus,
)


@dataclass(frozen=True)
class ExactCrossContextNumericDelta:
    baseline_proposition_id: str
    current_proposition_id: str
    unit_id: str
    value: Decimal


@dataclass(frozen=True)
class ExactCrossContextNumericDeltaCalculation:
    applicability_status: (
        ExactCrossContextNumericDeltaApplicabilityStatus
    )
    delta: Optional[ExactCrossContextNumericDelta]
