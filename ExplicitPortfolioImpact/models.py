from dataclasses import dataclass

from PortfolioDomain.models import PortfolioSubject
from PortfolioImpactInterpretationPolicy.models import (
    PortfolioImpactDirection,
    PortfolioImpactInterpretationPolicy,
)
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)
from ThesisPortfolioSubjectLink.models import (
    ExplicitThesisPortfolioSubjectLink,
)


@dataclass(frozen=True)
class ExplicitPortfolioImpact:
    impact_id: str
    semantic_thesis: SemanticallyProducedThesis
    link: ExplicitThesisPortfolioSubjectLink
    portfolio_subject: PortfolioSubject
    policy: PortfolioImpactInterpretationPolicy
    direction: PortfolioImpactDirection
    horizon_id: str
    rationale: str
