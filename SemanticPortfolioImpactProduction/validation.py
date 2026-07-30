from ExplicitPortfolioImpact.models import (
    ExplicitPortfolioImpact,
)
from ExplicitPortfolioImpact.validation import (
    validate_explicit_portfolio_impact,
)
from SemanticPortfolioImpactProduction.models import (
    SemanticallyProducedPortfolioImpact,
)


def validate_semantically_produced_portfolio_impact(
    production: SemanticallyProducedPortfolioImpact,
) -> None:
    if type(production) is not SemanticallyProducedPortfolioImpact:
        raise TypeError(
            "production must be "
            "SemanticallyProducedPortfolioImpact"
        )
    if type(production.impact) is not ExplicitPortfolioImpact:
        raise TypeError(
            "impact must be ExplicitPortfolioImpact"
        )
    validate_explicit_portfolio_impact(production.impact)
