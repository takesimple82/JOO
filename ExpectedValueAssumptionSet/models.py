from dataclasses import dataclass
from decimal import Decimal

from SemanticPortfolioImpactProduction.models import (
    SemanticallyProducedPortfolioImpact,
)


@dataclass(frozen=True)
class ExplicitExpectedValueOutcomeAssumption:
    outcome_id: str
    statement: str
    probability: Decimal
    value: Decimal


@dataclass(frozen=True)
class ExplicitExpectedValueAssumptionSet:
    assumption_set_id: str
    impact: SemanticallyProducedPortfolioImpact
    unit_id: str
    outcomes: tuple[
        ExplicitExpectedValueOutcomeAssumption,
        ...,
    ]
