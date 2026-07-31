from PortfolioMembership.models import (
    ExplicitPortfolioMembership,
)


def validate_explicit_portfolio_membership(
    membership: ExplicitPortfolioMembership,
) -> None:
    if type(membership) is not ExplicitPortfolioMembership:
        raise TypeError(
            "membership must be "
            "ExplicitPortfolioMembership"
        )
    if type(membership.portfolio_id) is not str:
        raise TypeError("portfolio_id must be str")
    if membership.portfolio_id.strip() == "":
        raise ValueError(
            "portfolio_id must not be blank"
        )
    if type(membership.portfolio_subject_id) is not str:
        raise TypeError(
            "portfolio_subject_id must be str"
        )
    if membership.portfolio_subject_id.strip() == "":
        raise ValueError(
            "portfolio_subject_id must not be blank"
        )
