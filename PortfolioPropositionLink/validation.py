from PortfolioPropositionLink.models import (
    ExplicitPropositionPortfolioSubjectLink,
)


def validate_explicit_proposition_portfolio_subject_link(
    link: ExplicitPropositionPortfolioSubjectLink,
) -> None:
    if type(link) is not ExplicitPropositionPortfolioSubjectLink:
        raise TypeError(
            "link must be ExplicitPropositionPortfolioSubjectLink"
        )

    if type(link.proposition_id) is not str:
        raise TypeError("proposition_id must be str")
    if link.proposition_id.strip() == "":
        raise ValueError("proposition_id must not be blank")

    if type(link.portfolio_subject_id) is not str:
        raise TypeError("portfolio_subject_id must be str")
    if link.portfolio_subject_id.strip() == "":
        raise ValueError(
            "portfolio_subject_id must not be blank"
        )
