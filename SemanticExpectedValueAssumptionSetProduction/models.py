from dataclasses import dataclass

from ExpectedValueAssumptionSet.models import (
    ExplicitExpectedValueAssumptionSet,
)


@dataclass(frozen=True)
class SemanticallyProducedExpectedValueAssumptionSet:
    assumption_set: ExplicitExpectedValueAssumptionSet
