from dataclasses import dataclass

from ExplicitPortfolioImpact.models import (
    ExplicitPortfolioImpact,
)


@dataclass(frozen=True)
class SemanticallyProducedPortfolioImpact:
    impact: ExplicitPortfolioImpact
