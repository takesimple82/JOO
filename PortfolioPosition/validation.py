from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)
from PortfolioMembership.validation import (
    validate_explicit_portfolio_membership,
)
from PortfolioPosition.models import (
    ExplicitPortfolioPosition,
)


def validate_explicit_portfolio_position(
    position: ExplicitPortfolioPosition,
) -> None:
    if type(position) is not ExplicitPortfolioPosition:
        raise TypeError(
            "position must be "
            "ExplicitPortfolioPosition"
        )
    if type(position.position_id) is not str:
        raise TypeError("position_id must be str")
    if position.position_id.strip() == "":
        raise ValueError(
            "position_id must not be blank"
        )
    if (
        type(position.membership)
        is not ExplicitPortfolioMembership
    ):
        raise TypeError(
            "membership must be "
            "ExplicitPortfolioMembership"
        )
    validate_explicit_portfolio_membership(
        position.membership
    )
