from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from ExpectedValueAssumptionSetApplicability.models import (
    ExpectedValueAssumptionSetApplicabilityStatus,
)
from SemanticExpectedValueAssumptionSetProduction.models import (
    SemanticallyProducedExpectedValueAssumptionSet,
)


@dataclass(frozen=True)
class ExactExpectedValue:
    source: SemanticallyProducedExpectedValueAssumptionSet
    value: Decimal


@dataclass(frozen=True)
class ExactExpectedValueCalculation:
    applicability_status: (
        ExpectedValueAssumptionSetApplicabilityStatus
    )
    expected_value: Optional[ExactExpectedValue]
