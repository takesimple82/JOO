from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)


def validate_explicit_portfolio_observation_context(
    context: ExplicitPortfolioObservationContext,
) -> None:
    if (
        type(context)
        is not ExplicitPortfolioObservationContext
    ):
        raise TypeError(
            "context must be "
            "ExplicitPortfolioObservationContext"
        )
    if type(context.observation_context_id) is not str:
        raise TypeError(
            "observation_context_id must be str"
        )
    if context.observation_context_id.strip() == "":
        raise ValueError(
            "observation_context_id must not be blank"
        )
    if type(context.portfolio_id) is not str:
        raise TypeError("portfolio_id must be str")
    if context.portfolio_id.strip() == "":
        raise ValueError(
            "portfolio_id must not be blank"
        )
