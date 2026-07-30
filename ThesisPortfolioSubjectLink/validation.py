from ThesisPortfolioSubjectLink.models import (
    ExplicitThesisPortfolioSubjectLink,
)


def validate_explicit_thesis_portfolio_subject_link(
    link: ExplicitThesisPortfolioSubjectLink,
) -> None:
    if type(link) is not ExplicitThesisPortfolioSubjectLink:
        raise TypeError(
            "link must be ExplicitThesisPortfolioSubjectLink"
        )

    if type(link.thesis_id) is not str:
        raise TypeError("thesis_id must be str")
    if link.thesis_id.strip() == "":
        raise ValueError("thesis_id must not be blank")

    if type(link.portfolio_subject_id) is not str:
        raise TypeError("portfolio_subject_id must be str")
    if link.portfolio_subject_id.strip() == "":
        raise ValueError(
            "portfolio_subject_id must not be blank"
        )
